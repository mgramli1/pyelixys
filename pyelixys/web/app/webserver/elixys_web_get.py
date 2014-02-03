'''
This python file contains several classes that
handle all GET web requests from a client.

'''
# import basic components
import time
import copy
# import flask components
from flask import Blueprint
from flask import render_template
from flask import jsonify
from flask import current_app 
from flask import request
import sys
# import flask class struct implmentation
# import basic user auth
from pyelixys.web.app.userauth.basicauth import requires_auth

# import access to coreserver proxy
# and DB objects.
# import the coreserver, db and sequence manager
# from elixysweb.py
from web_service import getCurrentClientState
from web_service import core_server
from web_service import db, sequence_manager
# import initial run state obj for serverstate
from web_service import InitialRunState
# import exception handler
from web_service import Exceptions

elixys_web_get = Blueprint('elixys_web_get', __name__,
        template_folder = 'templates')
elixys_web_get_sequence = Blueprint('elixys_web_get_sequence', __name__,
        template_folder='templates')

# globals

# Helper functions

# Directs the user to the appropriate
# select screen (also used by ExceptionHandler.py)
def direct_to_last_select_screen(client_state):
    '''
    Function shall change the client state's screen
    based on the previous screen the user was on.
    Function updates the screen in client state and
    returns the new client state
    '''
    if client_state["lastselectscreen"] == "SAVED":
        client_state["screen"] = "SELECT_SAVEDSEQUENCES"
        return client_state
    elif client_state["lastselectscreen"] == "HISTORY":
        client_state["screen"] = "SELECT_RUNHISTORY"
        return client_state
    else:
        raise Exception("Invalid last select screen value")

# Exception Handler Helper Functions
def handle_sequence_not_found(client_state, username, sequence_id):
    """
    Handles the error when the server fails to find a sequence.
    Function expects a client state object, a username, and the
    sequence id that raises the exception.
    Function shall return the state from GET /Elixys/state.
    """
    client_state = getCurrentClientState(username)

    current_app.logger.debug("Failed to find sequence: " + str(sequence_id) + \
            "Client state: " + str(client_state))
 
    # Was it the sequence that the user is currently on?
    if client_state["sequenceid"] == int(sequence_id):
        # Yes, so return the user to the last Select Sequence screen
        client_state = direct_to_last_select_screen(client_state)
        db.update_user_client_state(username, client_state)
        current_app.logger.error("Redirecting user to select sequences page")

    # Return the state
    elixys_get_state = Elixys_Get_State()
    return elixys_get_state.state_index()

def handle_component_not_found(client_state, username, component_id):
    """
    Handles the error when the server fails to find a component
    Function expects a client state, username and component id that
    generate the exception.
    Function return the state from GET /Elixys/state.
    """
    current_app.logger.debug("Failed to find component " + str(component_id))

    # Was it the component that the user is currently on?
    if client_state["componentid"] == component_id:
        # Yes
        sequence_id = 0
        try:
            # Get the sequence
            sequence_id = client_state["sequenceid"]
            sequence = db.get_sequence(sequence_id)

            # Move the client to the first unit operation
            client_state["componentid"] = sequence["components"][0]["id"]
            db.update_user_client_state(username, client_state)
            current_app.logger.warn("Redirecting user to the " + \
                    "first component of sequence " + str(sequence_id))
        except Exceptions.SequenceNotFoundException as ex:
            # Sequence not found
            current_app.logger.error("Sequence Not Found Exception" + str(ex))
            return handle_sequence_not_found(
                    client_state,
                    username,
                    sequence_id)

    # Return the state
    elixys_get_state = Elixys_Get_State()
    return elixys_get_state.state_index()

def handle_reagent_not_found(client_state, username, reagent_id):
    """
    Handles the error when the server fails to find a reagent.
    Function expects a client state, username and reagent id.
    Function shall redirect user to previous screen on client.
    Function returns the state from GET /Elixys/state.
    """
    current_app.logger.debug("Failed to find reagent " + str(reagent_id))

    # This error should only occur if the user has
    # the sequence they are currently viewing delete out from
    # under them.  Redirect them to the last Select Sequence screen
    client_state = direct_to_last_select_screen(client_state)
    db.update_user_client_state(username, client_state)
    current_app.logger.warn("Redirecting user to last screen.")

    # Return the state
    get_state = Elixys_Get_State()
    return get_state.state_index()

def handle_invalid_sequence(username, sequence_id):
    """Handles the error when the use attempts to run an invalid sequence"""
    current_app.logger.error("Cannot run invalid sequence (" + 
            str(sequence_id) + "\nUser:" + str(username))
    return {"type":"error", "description":"Invalid sequence"}

def handle_general_exception(username, error):
    """Handles all other exceptions"""
    #  the actual error and send the client a generic error
    if db != None:
        current_app.logger.error("User: " + str(username) + \
                str(error))
    else:
        print str(error)
    return {"type":"error", "description":"An internal server error occurred"}

# State Helper Functions
def get_server_state(username):
    '''
    Function either initializes or obtains the current
    server state.
    Function expects a username as a string.
    Function returns either the updated server state or
    a new server state if the server state queried returned
    None. If server state is None, create a new server state.
    '''
    # Initializes and/or returns the cached server state
    
    server_state = core_server.GetServerState(username)
    if server_state == None:
        current_app.logger.debug("Core Server has yet to setup server state" +
                "\nSetting up new instance of server state")
        server_state = {"type":"serverstate"}
        server_state["timestamp"] = time.time()
        server_state["runstate"] = InitialRunState()
        server_state["runstate"]["status"] = "Offline"
        server_state["runstate"]["username"] = ""
    #current_app.logger.debug("Returned server state: " + \
    #        str(server_state)) 
    return server_state

def lower_if_possible(string_x):
    '''
    Function expects a string that will
    be lowered if possible. If not, returns
    a the string unlowered.
    '''
    try:
        return string_x.lower()
    except AttributeError:
        return string_x

# Handle GET /runstate request
def handle_get_state_home(username):
    '''
    Handles GET /runstate request
    Function expects a string username.
    Function returns the buttons for the
    HOME screen.

    '''
    # 
    
    server_state = get_server_state(str(username))
    # Check if someone running the system
    system_running = (server_state["runstate"]["username"] != "")

    # Return the button array
    return {"buttons":[{"type":"button",
        "id":"SEQUENCER",
        "enabled":True},
        {"type":"button",
        "id":"MYACCOUNT",
        "enabled":False},
        {"type":"button",
        "id":"MANAGEUSERS",
        "enabled":False},
        {"type":"button",
        "id":"VIEWLOGS",
        "enabled":False},
        {"type":"button",
        "id":"VIEWRUN",
        "enabled":system_running},
        {"type":"button",
        "id":"LOGOUT",
        "enabled":True}]}

# Handle GET /state for Select Saved Sequence
def handle_get_state_select_savedsequences(client_state, username):
    '''
    Handles GET /state for Select Saved Sequence
    Function expects a client state and a string username.
    Function returns the select saved sequences screen (the
    screen that lists all sequences.)
    '''
    # Check if the system is running
    
    server_state = get_server_state(username)
    system_available = (server_state["runstate"]["status"] == "Idle")

    # Determine the sorting modes
    sort_descending = True
    sort_key = ""
    name_sort_mode = "none"
    if client_state["selectsequencesort"]["column"] == "name":
        sort_key = "name"
        name_sort_mode = client_state["selectsequencesort"]["mode"]
        if name_sort_mode == "down":
            sort_descending = False
    comment_sort_mode = "none"
    if client_state["selectsequencesort"]["column"] == "comment":
        sort_key = "comment"
        comment_sort_mode = client_state["selectsequencesort"]["mode"]
        if comment_sort_mode == "down":
            sort_descending = False

    # Format the buttons, tabs and columns
    return_state = {"buttons":[{"type":"button",
        "id":"SEQUENCER",
        "enabled":True,
        "selectionrequired":False},
        {"type":"button",
        "id":"NEWSEQUENCE",
        "enabled":True,
        "selectionrequired":False},
        {"type":"button",
        "id":"COPYSEQUENCE",
        "enabled":True,
        "selectionrequired":True},
        {"type":"button",
        "id":"VIEWSEQUENCE",
        "enabled":True,
        "selectionrequired":True},
        {"type":"button",
        "id":"EDITSEQUENCE",
        "enabled":True,
        "selectionrequired":True},
        {"type":"button",
        "id":"RUNSEQUENCE",
        "enabled":system_available,
        "selectionrequired":True},
        {"type":"button",
        "id":"DELETESEQUENCE",
        "enabled":True,
        "selectionrequired":True}],
        "tabs":[{"type":"tab",
        "text":"SEQUENCE LIST",
        "id":"SAVEDSEQUENCES"},
        {"type":"tab",
        "text":"RUN HISTORY",
        "id":"RUNHISTORY"}],
        "tabid":"SAVEDSEQUENCES",
        "columns":[{"type":"column",
        "data":"name",
        "display":"NAME",
        "percentwidth":35,
        "sortable":True,
        "sortmode":name_sort_mode},
        {"type":"column",
        "data":"comment",
        "display":"COMMENT",
        "percentwidth":65,
        "sortable":True,
        "sortmode":comment_sort_mode}]}
    # Append the saved sequence list
    saved_sequences = db.get_all_sequences("Saved")
    saved_sequences.sort(key=lambda sequence: map(
        lower_if_possible, 
        sequence[sort_key]),
        reverse=sort_descending)
    return_state.update({"sequences":saved_sequences})
    return return_state

# Handle GET /state for Select Sequence (Run history tab)
def handle_get_state_select_runhistory(client_state, username):
    '''
    Handles GET /state for Select Sequence (Run history tab)
    Function expects a client state and a string username.
    Function returns the Run Hitory tab portion of the sequences
    screen. Function handles the toggles of the buttons for what order
    sequences shall be listed in.
    '''
    
    server_state = get_server_state(username)
    system_available = (server_state["runstate"]["status"] == "Idle")

    # Determine the sorting modes
    sort_descending = True
    sort_key1 = ""
    sort_key2 = ""
    name_sort_mode = "none"
    if client_state["runhistorysort"]["column"] == "name":
        sort_key1 = "name"
        name_sort_mode = client_state["runhistorysort"]["mode"]
        if name_sort_mode == "down":
            sort_descending = False
    comment_sort_mode = "none"
    if client_state["runhistorysort"]["column"] == "comment":
        sort_key1 = "comment"
        comment_sort_mode = client_state["runhistorysort"]["mode"]
        if comment_sort_mode == "down":
            sort_descending = False
    creator_sort_mode = "none"
    if client_state["runhistorysort"]["column"] == "creator":
        sort_key1 = "creator"
        creator_sort_mode = client_state["runhistorysort"]["mode"]
        if creator_sort_mode == "down":
            sort_descending = False
    date_time_sort_mode = "none"
    if client_state["runhistorysort"]["column"] == "date&time":
        sort_key1 = "date"
        sort_key2 = "time"
        date_time_sort_mode = client_state["runhistorysort"]["mode"]
        if date_time_sort_mode == "down":
            sort_descending = False

    # Format the buttons, tabs and columns
    return_state = {"buttons":[{"type":"button",
        "id":"SEQUENCER",
        "enabled":True},
        {"type":"button",
        "id":"COPYSEQUENCE",
        "enabled":True,
        "selectionrequired":True},
        {"type":"button",
        "id":"VIEWSEQUENCE",
        "enabled":True,
        "selectionrequired":True},
        {"type":"button",
        "id":"RUNSEQUENCE",
        "enabled":system_available,
        "selectionrequired":True},
        {"type":"button",
        "id":"VIEWRUNLOGS",
        "enabled":False,
        "selectionrequired":True},
        {"type":"button",
        "id":"VIEWBATCHRECORD",
        "enabled":False,
        "selectionrequired":True}],
        "tabs":[{"type":"tab",
        "text":"SEQUENCE LIST",
        "id":"SAVEDSEQUENCES"},
        {"type":"tab",
        "text":"RUN HISTORY",
        "id":"RUNHISTORY"}],
        "tabid":"RUNHISTORY",
        "columns":[{"type":"column",
        "data":"name",
        "display":"NAME",
        "percentwidth":20,
        "sortable":True,
        "sortmode":name_sort_mode},
        {"type":"column",
        "data":"comment",
        "display":"COMMENT",
        "percentwidth":40,
        "sortable":True,
        "sortmode":comment_sort_mode},
        {"type":"column",
        "data":"creator",
        "display":"USER",
        "percentwidth":15,
        "sortable":True,
        "sortmode":creator_sort_mode},
        {"type":"column",
        "data":"date&time",
        "display":"DATE",
        "percentwidth":25,
        "sortable":True,
        "sortmode":date_time_sort_mode}]}

    # Append the run history list
    run_history_sequences = db.get_all_sequences("History")
    if sort_key2 == "":
        run_history_sequences.sort(key=lambda sequence: map(
            lower_if_possible,
            sequence[sort_key1]),
            reverse=sort_descending)
    else:
        run_history_sequences.sort(key=lambda sequence: (map(
            lower_if_possible, 
            sequence[sort_key1]), 
            map(lower_if_possible, sequence[sort_key2])), 
            reverse=sort_descending)
    return_state.update({"sequences":run_history_sequences})
    return return_state

# Handle GET /state for View Sequence
def handle_get_state_view(client_state, username):
    '''
    Handles GET /state for View Sequence
    Function expects a client state and a string username.
    Function returns the "View Sequence" screen.
    '''
    
    server_state = get_server_state(username)
    # Do we have a component ID?
    if client_state["componentid"] == 0:
        # No, the component ID is missing.
        # Get the sequence and the ID of the first component
        sequence = sequence_manager.GetSequence(
                username,
                client_state["sequenceid"],
                False)
        client_state["componentid"] = sequence["components"][0]["id"]
        # Save client state
        db.update_user_client_state(username, client_state)        
        
    # Allow editing if this is a saved sequence
    sequence_metadata = db.get_sequence_metadata(
            client_state["sequenceid"])
    edit_allowed = (sequence_metadata["sequencetype"] == "Saved")

    # Allow running if the system is not in use
    run_allowed = (server_state["runstate"]["status"] == "Idle")

    # Allow running from here if this is not a cassette
    run_here_allowed = False
    if run_allowed:
        component = sequence_manager.GetComponent(username, 
                client_state["componentid"],
                client_state["sequenceid"])
        run_here_allowed = (component["componenttype"] != "CASSETTE")

    # Return the state
    return {"buttons":[{"type":"button",
        "id":"SEQUENCER",
        "enabled":True},
        {"type":"button",
        "id":"EDITSEQUENCE",
        "enabled":edit_allowed},
        {"type":"button",
        "id":"RUNSEQUENCE",
        "enabled":run_allowed},
        {"type":"button",
        "id":"RUNSEQUENCEHERE",
        "enabled":run_here_allowed}],
        "sequenceid":client_state["sequenceid"],
        "componentid":client_state["componentid"]}

# Handle GET /state for Edit Sequence
def handle_get_state_edit(client_state, username):
    '''
    Handles GET /state for Edit Sequence
    Function shall expect a client state and a string username.
    Function shall return the "Edit Sequence" screen.
    '''
    
    server_state = get_server_state(username)
    current_app.logger.debug("GET /STATE - edit" +
            "\nclient state: " + str(client_state) + \
            "\nclient state[comp id]: " + str(client_state["componentid"]) + \
            "\nRun State: " + str(server_state["runstate"]))
    
    # Do we have a component ID?
    if client_state["componentid"] == 0:
        # No, the component ID is missing.
        # Get the sequence and the ID of the first component
        sequence = sequence_manager.GetSequence(
                username, 
                client_state["sequenceid"], 
                False)
        client_state["componentid"] = sequence["components"][0]["id"]
        # Save client state
        db.update_user_client_state(username, client_state)

    # Allow running if the system is not in use
    run_allowed = (server_state["runstate"]["status"] == "Idle")

    # Allow running from here if this is not a cassette
    run_here_allowed = False
    if run_allowed:
        component = sequence_manager.GetComponent(
                username,
                client_state["componentid"],
                client_state["sequenceid"])
        run_here_allowed = (component["componenttype"] != "CASSETTE")

 
    # Return the state
    return {"buttons":[{"type":"button",
        "id":"SEQUENCER",
        "enabled":True},
        {"type":"button",
        "id":"VIEWSEQUENCE",
        "enabled":True},
        {"type":"button",
        "id":"RUNSEQUENCE",
        "enabled":run_allowed},
        {"type":"button",
        "id":"RUNSEQUENCEHERE",
        "enabled":run_here_allowed}],
        "sequenceid":client_state["sequenceid"],
        "componentid":client_state["componentid"]}

# Handle GET /state for Run Sequence
def handle_get_state_run(client_state, username):
    '''
    Handles GET /state for Run Sequtate: " + str(server_state))
    '''
    
    server_state = get_server_state(username)
    current_app.logger.debug("In GET /STATE - RUN" + 
            "\nClientstate: " + str(client_state) + \
            "\nServerstate: " + str(server_state))
    
    server_state = get_server_state(username)

    # Sync the client state with the run state
    if ((client_state["sequenceid"] != server_state["runstate"]["sequenceid"]) or 
            (client_state["componentid"] != server_state["runstate"]["componentid"]) or 
            (client_state["prompt"]["show"] != server_state["runstate"]["prompt"]["show"]) or 
            ((client_state["prompt"].has_key("screen")) and 
                (server_state["runstate"]["prompt"].has_key("screen")) and 
                (client_state["prompt"]["screen"] != server_state["runstate"]["prompt"]["screen"]))):
        # Log issue
        current_app.logger.debug("Syncing the client with run state" +
                   "\nClient State:\n" + str(client_state) + 
                   "\nRun State:\n" + str(server_state["runstate"]))
        # Update the sequence and component IDs
        client_state["sequenceid"] = server_state["runstate"]["sequenceid"]
        client_state["componentid"] = server_state["runstate"]["componentid"]
        # Update the prompt
        client_state["prompt"] = copy.copy(server_state["runstate"]["prompt"])
        # Update the client state
        db.update_user_client_state(username, client_state)

    # Determine if we are the user running the system
    if str(username) == server_state["runstate"]["username"]:
        # Enable or disable buttons
        sequencer_enabled = False
        pause_enabled = False   #not server_state["runstate"]["runcomplete"]
        abort_enabled = not server_state["runstate"]["runcomplete"]
    else:
        # Enable or disable buttons
        sequencer_enabled = True
        pause_enabled = False
        abort_enabled = False

    # Return the state
    return {"buttons":[{"type":"button",
        "id":"SEQUENCER",
        "enabled":sequencer_enabled},
        {"type":"button",
        "id":"PAUSERUN",
        "enabled":pause_enabled},
        {"type":"button",
        "id":"ABORTRUN",
        "enabled":abort_enabled},
        {"type":"button",
        "id":"LOGOUT",
        "enabled":True}],
        "sequenceid":client_state["sequenceid"],
        "componentid":client_state["componentid"]}

# GET Classes
class Elixys_Get_Main:
    '''
    This class handles the "Main" page for
    the web browser. If the user has yet to
    be authenticated, they will be prior to
    visiting the Homepage.
    Class represents the GET / web requests.
    '''
    @elixys_web_get.route('/')
    @requires_auth
    def main_index():
        '''
        Function requires authentication.
        Upon valid authentication, function shall
        render a HTML page stored in the 'templates'
        folder.
        '''
        current_app.logger.debug(str(request))
        return render_template('main_elixys.html')

class Elixys_Get_State:
    '''
    This class represents the GET /Elixys/state web requests.
    '''
    @elixys_web_get.route('/state', methods=['GET'])
    @elixys_web_get.route('/Elixys/state', methods=['GET'])
    @requires_auth
    def state_index(self=None):
        '''
        This function requires authentication prior to executing.
        Function takes in no parameters.
        Function shall direct the client based on the client's
        current screen.
        Function returns the state to the client as a JSON object.
        '''
        
        auth = request.authorization
        user = db.get_user(str(auth.username))
        server_state = get_server_state(str(auth.username))
        client_state = getCurrentClientState(str(auth.username))
        current_app.logger.debug(str(request) + "\nClientstate: " + \
                str(client_state) + "\nServerstate: " + str(server_state))
        # Is the remote user the one that is currently running the system?
        if str(auth.username) == server_state["runstate"]["username"]:
            # Yes, so make sure the user is on the run screen
            if client_state["screen"] != "RUN":
                # Update the client state
                client_state["screen"] = "RUN"
                db.update_user_client_state( 
                        str(auth.username),
                        client_state)

        return_state = {"type":"state",
                "user":user,
                "serverstate":server_state,
                "clientstate":client_state,
                "timestamp":time.time()}
        # Check which screen is active
        choice = str(client_state["screen"])
        
        current_app.logger.debug("Request for state" +  
                "\nREQUEST: " + str(request) + \
                "\nClient state: " + str(client_state) + \
                "\nServer state: " + str(server_state))

        #current_app.logger.debug("Client State: "+ str(client_state) + \
        #        "\nChoice from client_state[screen]: " +str(choice))

        if choice == "HOME":
            return_state.update(handle_get_state_home(auth.username))
        elif choice == "SELECT_SAVEDSEQUENCES":
            return_state.update(handle_get_state_select_savedsequences(
                client_state, auth.username))
        elif choice == "SELECT_RUNHISTORY":
            return_state.update(handle_get_state_select_runhistory(
                client_state, auth.username))
        elif choice == "VIEW":
            return_state.update(handle_get_state_view(
                client_state, auth.username))
        elif choice == "EDIT":
            return_state.update(handle_get_state_edit(
                client_state, auth.username))
        elif choice == "RUN":
            return_state.update(handle_get_state_run(
                client_state, auth.username))
        else:
            current_app.logger.debug("Unknown screen: %s" % str(choice))
            raise Exception("Unknown screen: %s" % str(choice))
        #current_app.logger.debug("Return state: " + str(return_state)) 
        return jsonify(return_state)

class Elixys_Get_Component:
    '''
    This class represents the
    GET Elixys/component/<component_id>
       '''
    @elixys_web_get.route(
            '/sequence/<sequence_id>/component/<component_id>', 
            methods=['GET'])
    @elixys_web_get.route(
            '/Elixys/sequence/<sequence_id>/component/<component_id>', 
            methods=['GET'])
    @requires_auth
    def component_index(sequence_id, component_id):
        '''
        Function handles GET request for
        /Elixys/sequence/<sequenceid>/component/<componentid>.
        Function expects a sequence id and a component id to be
        passed in through the web request.
        Function shall either return a component as a JSON object
        or try to handle an exception.
        If the sequence id from the component found on the database 
        is the same as thesequence id passed in, the function returns. 
        If the sequence ids do not match, function calls a helper method
        to try to find the matching component.
        '''
        auth = request.authorization
        username = str(auth.username)
        client_state = getCurrentClientState(username)
        server_state = get_server_state(str(username)) 
        current_app.logger.debug("In /sequence/s_id/component/c_id" + 
                "\nRequest for %s" % str(request) + \
                "\nClient state: " + str(client_state) + \
                "\nServer state: " + str(server_state))
       
        # Handle GET /sequence/[sequenceid]/component/[componentid]
        # Get the component and verify the sequence ID
        try :
            component = sequence_manager.GetComponent(
                    username,
                    int(component_id),
                    int(sequence_id))
        except Exceptions.ComponentNotFoundException:
            return handle_component_not_found(
                    client_state,
                    username,
                    int(component_id))

        current_app.logger.debug(
                "\nSequence id: " + str(component['sequenceid']) + \
                "\nPassed in sequence id: " + str(sequence_id) + \
                "\nPassed in compo id : " + str(component_id) + \
                "\nComponent JSON: " + str(component))
        if int(component["sequenceid"]) == int(sequence_id):
            return jsonify(component)
        else:
            return handle_component_not_found(
                    client_state,
                    username,
                    int(component_id))

class Elixys_Get_Configuration:
    '''
    This classs represents the
    GET Elixys/configuration web request.
    '''
    @elixys_web_get.route('/config', methods=['GET'])
    @elixys_web_get.route('/configuration', methods=['GET'])
    @elixys_web_get.route('/Elixys/config', methods=['GET'])
    @elixys_web_get.route('/Elixys/configuration', methods=['GET'])
    @requires_auth
    def config_index():
        '''
        Function shall expect no parameters.
        Function shall return a config object as a JSON object.
        Function shall query the database and obtain the config
        object from the db.
        '''
        # Handle GET /configuration
        current_app.logger.debug(str(request))

        auth = request.authorization
        user = db.get_user(auth.username)

        config = {"type":"configuration"}
        config.update(db.get_configuration())
        config.update(
                {"supportedoperations": 
                    db.get_supported_operations()})
        current_app.logger.debug(str(config))
        return jsonify(config)

class Elixys_Get_Reagent:
    '''
    This class represents the
    GET Elixys/sequence/<sequence_id>/reagent/<reagent_id>
    web request.
    '''
    @elixys_web_get.route(
            '/Elixys/sequence/<sequence_id>/reagent/<reagent_ids>')
    @elixys_web_get.route(
            '/sequence/<sequence_id>/reagent/<reagent_ids>')
    @requires_auth
    def reagent_index(sequence_id, reagent_ids):
        '''
        Function expects a sequence id and a reagent id(s) that
        is passed in from the web request.
        Function returns a reagent(s) object as a JSON object.
        This function takes all reagent ids passed in
        (seperated by a dot -in the form of .../reagent/1.2.5.6).
        For each reagent id, this funcion shall obtain the reagent
        information and return all the information as a whole.
        '''
        current_app.logger.debug(str(request))
        auth = request.authorization
        user = db.get_user(auth.username)
        # Split each reagent id based on a '.'
        reagent_ids = str(reagent_ids).split(".")
        
        # Create and return the reagent array
        reagents = {}
        reagents["type"] = "reagents"
        reagents["reagents"] = []
        for reagent_id in reagent_ids:
            reagents["reagents"].append(
                    sequence_manager.GetReagent(user, int(reagent_id)))
        return jsonify(reagents)

class Elixys_Get_Sequence:
    # Note that this routes for 'elixys_web_get_sequence'.
    # This is because the route above ('/Elixys/sequence/...')
    # has the same format as this route so we use two routes.
    '''
    This class represents the GET Elixys/sequence/<sequence_id>.
    '''
    @elixys_web_get_sequence.route(
            '/sequence/<sequence_id>',
            methods=['GET'])
    @elixys_web_get_sequence.route(
            '/Elixys/sequence/<sequence_id>',
            methods=['GET'])
    @requires_auth
    def sequence_index(sequence_id):
        '''
        Funciton shall take in a sequence id as a 
        parameter.
        Function shall return the sequence object
        as a jSON object.
        Function shall try to obtain the sequence based
        on the id or try to handle the unknown sequence id.
        All components shall be added to the return object
        as a part of a sequence's components.
        '''
        
        current_app.logger.debug(str(request))
        auth = request.authorization
        username = str(auth.username)
        server_state = get_server_state(str(username))
        client_state = getCurrentClientState(str(username))
        current_app.logger.debug(str(request) + \
                "\nClient state: " + str(client_state) + \
                "\nServer state: " + str(server_state))
        sequence = None
        # Load the sequence
        try :
            sequence = sequence_manager.GetSequence(
                    username,
                    int(sequence_id),
                    False)
        except Exceptions.SequenceNotFoundException:
            return handle_sequence_not_found(
                    client_state,
                    username,
                    int(sequence_id))
            
        #current_app.logger.debug("In /sequence function, client state: " + \
        #        str(client_state) + \
        #        "\nSequence found: " + str(sequence))
     
        # Copy a subset of the sequence data
        new_components = []
        for old_comp in sequence["components"]:
            new_comp = {"type":"sequencecomponent",
                    "note":old_comp["note"],
                    "id":old_comp["id"],
                    "componenttype":old_comp["componenttype"],
                    "validationerror":False}
            if old_comp.has_key("validationerror"):
                new_comp["validationerror"] = old_comp["validationerror"]
            new_components.append(new_comp)
        sequence["components"] = new_components

        sequence.update({"type": "sequence"})
        # Return cleaned sequence
        current_app.logger.debug("In /sequence function, new sequence: " + \
                str(sequence))
        return jsonify(sequence)

class Elixys_Get_Runstate:
    '''
    This class represents the GET Elixys/runstate web request.
    '''
    # Functions for GET /RUNSTATE
    # Handle GET /runstate request
    def handle_get_state_home():
        '''
        Function expects no parameters to be passed in.
        Function returns the Home (sequences) page.
        '''
        # Check if someone running the system
        system_running = (server_state["runstate"]["username"] != "")

        # Return the button array
        return {"buttons":[{"type":"button",
            "id":"SEQUENCER",
            "enabled":True},
            {"type":"button",
            "id":"MYACCOUNT",
            "enabled":False},
            {"type":"button",
            "id":"MANAGEUSERS",
            "enabled":False},
            {"type":"button",
            "id":"VIEWLOGS",
            "enabled":False},
            {"type":"button",
            "id":"VIEWRUN",
            "enabled":system_running},
            {"type":"button",
            "id":"LOGOUT",
            "enabled":True}]}

    # Handle GET /state for Run Sequence
    def handle_get_state_run(client_state, username):
        '''
        Function shall return the state for a Run Sequence state.
        Function expects a client state and a string username to be passed in.
        Function shall return the state for the Run Sequence state
        as a JSON object.
        '''
        # Sync the client state with the run state
        if ((client_state["sequenceid"] != server_state["runstate"]["sequenceid"]) or 
                (client_state["componentid"] != server_state["runstate"]["componentid"]) or 
                (client_state["prompt"]["show"] != server_state["runstate"]["prompt"]["show"]) or 
                ((client_state["prompt"].has_key("screen")) and 
                    (server_state["runstate"]["prompt"].has_key("screen")) and 
                    (client_state["prompt"]["screen"] != server_state["runstate"]["prompt"]["screen"]))):
            # Update the sequence and component IDs
            client_state["sequenceid"] = server_state["runstate"]["sequenceid"]
            client_state["componentid"] = server_state["runstate"]["componentid"]

            # Update the prompt
            client_state["prompt"] = copy.copy(
                    server_state["runstate"]["prompt"])
            # Update the client state
            db.update_user_client_state(username, client_state)

                
        # Determine if we are the user running the system
        if username == server_state["runstate"]["username"]:
            # Enable or disable buttons
            sequencer_enabled = False
            pause_enabled = False   #not server_state["runstate"]["runcomplete"]
            abort_enabled = not server_state["runstate"]["runcomplete"]
        else:
            # Enable or disable buttons
            sequencer_enabled = True
            pause_enabled = False
            abort_enabled = False

        # Return the state
        return {"buttons":[{"type":"button",
            "id":"SEQUENCER",
            "enabled":sequencer_enabled},
            {"type":"button",
            "id":"PAUSERUN",
            "enabled":pause_enabled},
            {"type":"button",
            "id":"ABORTRUN",
            "enabled":abort_enabled},
            {"type":"button",
            "id":"LOGOUT",
            "enabled":True}],
            "sequenceid":client_state["sequenceid"],
            "componentid":client_state["componentid"]}
    
    @elixys_web_get.route('/runstate')
    @elixys_web_get.route('/Elixys/runstate')
    @requires_auth
    def runstate_index():
        '''
        Function shall handle GET ../runstate.
        Function expects no paramaters to be passed in.
        Function shall return the state as a JSON object.
        This state will contain components from the client
        state and the server state.
        '''
        
        # Handle GET /runstate request
        # Get the user information and server state
        current_app.logger.debug(str(request))

        auth = request.authorization
        user = db.get_user(str(auth.username))
        server_state = core_server.GetServerState(user)
        client_state = getCurrentClientState(auth.username)

        # Start the state object
        return_state = {"type":"state",
            "user":user,
            "serverstate":server_state,
            "clientstate":copy.deepcopy(client_state),
            "timestamp":time.time()}

        # Complete with either the run or home states
        if server_state["runstate"]["running"]:
            return_state.update(handle_get_state_run(
                client_state, str(auth.username)))
            return_state["clientstate"]["screen"] = "RUN"
        else:
            return_state.update(handle_get_state_run(
                client_state, str(auth.username)))
            return_state["clientstate"]["screen"] = "HOME"
            return_state["clientstate"]["prompt"]["show"] = False

        # Return the state
        return jsonify(return_state)
