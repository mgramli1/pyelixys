'''
This python file handles all POST
web requests from the client.
'''

# import basic components
import time
import json
# import flask components
from flask import Blueprint
from flask import current_app 
from flask import request
# import basic user auth
from pyelixys.web.app.userauth.basicauth import requires_auth

# import access to coreserver proxy
# and DB objects.
# import the coreserver, db and sequence manager
# from elixysweb.py
from web_service import getCurrentClientState
from web_service import core_server
from web_service import db, sequence_manager

# import exception handler
import sys
sys.path.append('/opt/elixys/core')
import Exceptions
# import initial run state obj for serverstate
from CoreServer import InitialRunState
# import elixys GET handler
from elixys_web_get import Elixys_Get_State

elixys_post = Blueprint('elixys_post', __name__,
        template_folder='templates')
# Helper Functions

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
    current_app.logger.debug("Returned server state: " + \
            str(server_state))
    return server_state

# Directs the user to the appropriate
# select screen (also used by ExceptionHandler.py)
def direct_to_last_select_screen(client_state):
    '''
    Function shall check the client state's
    last select screen and set the screen to
    the Select Sequence page.
    If client state doesn't have a
    '''
    if client_state["lastselectscreen"] == "SAVED":
        client_state["screen"] = "SELECT_SAVEDSEQUENCES"
        return client_state
    elif client_state["lastselectscreen"] == "HISTORY":
        client_state["screen"] = "SELECT_RUNHISTORY"
        return client_state
    else:
        raise Exception("Invalid last select screen value")

# Save the client state and return
def save_client_state_and_return(client_state, username):
    '''
    Function expects a client state and a string username.
    Function shall update the client state before calling
    GET /State from Elixys_Get_State().
    Function shall return the output of state_index() called
    from Elixys_Get_State.
    '''
    db.update_user_client_state(username, client_state)
    # Call GET /STATE and return
    get_state = Elixys_Get_State()
    return get_state.state_index()

# Exception Handler Helper Functions
def handle_sequence_not_found(client_state, username, sequence_id):
    """Handles the error when the server fails to find a sequence"""
    current_app.logger.debug("Failed to find sequence %s " % str(sequence_id))
            
    # Was it the sequence that the user is currently on?
    if client_state["sequenceid"] == sequence_id:
        # Yes, so return the user to the last Select Sequence screen
        client_state = direct_to_last_select_screen(client_state)
        db.update_user_client_state(username, client_state)
        current_app.logger.error("Redirecting user to select sequences page")

    # Return the state
    return Elixys_Get_State.state_index()

def handle_component_not_found(client_state, username, component_id):
    """Handles the error when the server fails to find a component"""
    current_app.logger.debug("Failed to find component " + str(component_id) + \
            ". Trying to resolve issue...")

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
            return handle_sequence_not_found(client_state, 
                    username, sequence_id)

    # Return the state
    elixys_get_state = Elixys_Get_State()
    return elixys_get_state.state_index()

def handle_reagent_not_found(client_state, username, reagent_id):
    """Handles the error when the server fails to find a reagent"""
    current_app.logger.debug("Failed to find reagent " + str(reagent_id))

    # This error should only occur if the user has
    # the sequence they are currently viewing delete out from
    # under them.  Redirect them to the last Select Sequence screen
    client_state = direct_to_last_select_screen(client_state)
    db.update_user_client_state(username, client_state)
    current_app.logger.warn("Redirecting user to select sequences page")

    # Return the state
    get_state = Elixys_Get_State()
    return get_state.state_index()

def handle_invalid_sequence(username, sequence_id):
    """Handles the error when the use attempts to run an invalid sequence"""
    current_app.logger.error("Cannot run invalid sequence (" + \
            str(sequence_id) + "\nUser: " + str(username))
    return {"type":"error", "description":"Invalid sequence"}

def handle_general_exception(username, error):
    """Handles all other exceptions"""
    # Log the actual error and send the client a generic error
    if db != None:
        current_app.logger.error(str(error) + "\nUser: " + \
                str(username))
    else:
        print str(error)
    return {"type":"error", "description":"An internal server error occurred"}

# Show the Run Sequence prompt
def show_run_sequence_prompt(client_state, username, sequence_id):
    '''
    Function expects a client state, a string username and an int
    sequence id to be passed in as parameters.
    Function calls the save client state and return function prior to
    returning the output of the funciton.
    '''
    # Load the sequence
    sequence = sequence_manager.GetSequence(username, sequence_id, False)
    # Fill in the state
    client_state["prompt"]["screen"] = "PROMPT_RUNSEQUENCE"
    client_state["prompt"]["show"] = True
    client_state["prompt"]["title"] = "RUN SEQUENCE"
    client_state["prompt"]["text1"] = \
            "Would you like to run the sequence \"" + \
            str(sequence["metadata"]["name"]) + "\"?"
    client_state["prompt"]["edit1"] = False
    client_state["prompt"]["text2"] = ""
    client_state["prompt"]["edit2"] = False
    client_state["prompt"]["buttons"] = [{"type":"button",
        "text":"YES",
        "id":"YES"},
        {"type":"button",
        "text":"NO",
        "id":"NO"}]
    client_state["sequenceid"] = sequence_id
    return save_client_state_and_return(client_state, username)

# Handle sequence POST requests
def handle_post_base_sequence(client_state,
        username, action_type, action_target_id):
    '''
    Function expects a client state, a string username, a string
    action type, and a string action_target_id.
    Function shall return True if action type and
    action_target_id are valid or function shall return
    False.
    '''
    # Check which option the user selected
    if action_type == "BUTTONCLICK":
        if action_target_id == "SEQUENCER":
            # Switch states to the last Select Sequence screen
            direct_to_last_select_screen(client_state)
            return True
        elif action_target_id == "PREVIOUS":
            # Move to the previous component
            previous_component = db.get_previous_component(
                    client_state["componentid"])
            if previous_component != None:
                client_state["componentid"] = previous_component["id"]
            return True
        elif action_target_id == "NEXT":
            # Move to the next component
            next_component = db.get_next_component( 
                    client_state["componentid"])
            if next_component != None:
                client_state["componentid"] = next_component["id"]
            return True
        else:
            # Check if the target ID corresponds to 
            # one of our sequence components
            try:
                # Cast the action target ID to an integer 
                # and fetch the corresponding component
                action_target_id = int(action_target_id)
                component = db.get_component(action_target_id)

                # Make sure the sequence IDs match
                if component["sequenceid"] != client_state["sequenceid"]:
                    return False

                # Move to the component
                client_state["componentid"] = component["id"]
                return True
            except ValueError:
                # Action target ID is not an integer
                pass
            except Exception("Component Not Found Exception"):
                # Interger does not correspond to a component ID
                pass

    # Tell the caller we didn't handle it
    return False

# Show the Run Sequence From Component prompt
def show_run_sequence_from_component_prompt(client_state,
        username, sequence_id, component_id):
    '''
    Function expects a client state, a string username, an integer
    sequence id, and an integer component_id to be passed in as 
    parameters.
    Function calls the save client and return function and returns
    the output of the function.
    '''
    # Load the sequence and find the component
    sequence = sequence_manager.GetSequence(username, sequence_id, False)
    component = None
    index = 1
    for seq_component in sequence["components"]:
        if seq_component["id"] == component_id:
            component = seq_component
            break
        index += 1
    if component == None:
        raise Exception("Component " + str(component_id) + 
                " not found in sequence " + str(sequence_id))

    # Adjust the component index for the cassettes
    index -= db.get_configuration()["reactors"]

    # Fill in the state
    client_state["prompt"]["screen"] = "PROMPT_RUNSEQUENCEFROMCOMPONENT"
    client_state["prompt"]["show"] = True
    client_state["prompt"]["title"] = "RUN SEQUENCE"
    client_state["prompt"]["text1"] = \
            "Would you like to run the sequence \"" + \
            str(sequence["metadata"]["name"]) + \
            "\" starting with unit operation number " + str(index) + \
            " (" + component["componenttype"] + ")?"
    client_state["prompt"]["edit1"] = False
    client_state["prompt"]["text2"] = ""
    client_state["prompt"]["edit2"] = False
    client_state["prompt"]["buttons"] = [{"type":"button",
        "text":"YES",
        "id":"YES"},
        {"type":"button",
        "text":"NO",
        "id":"NO"}]
    client_state["sequenceid"] = sequence_id
    return save_client_state_and_return(
           client_state, username)

# Handle POST /sequence/[sequenceid]
def handle_post_sequence():
    '''
    There currently isn't any way in the UI to edit the sequence metadata
    '''
    raise Exception("Implement post sequence")

# Handle POST /sequence/[sequenceid]/component/[componentid]
def handle_post_component(s_id, c_id, unit, client_state, username, body):
    '''
    Function expects integers sequence id, component id, and insertion id.
    Function also expects a client state and a string for the body sent
    with the POST request.
    Function calls save client and return then returns the output of the
    function called.
    '''
    # Extract sequence and component IDs
    current_app.logger.debug("Handle post component.")
    
    sequence_id = int(s_id)
    component_id = int(c_id)
    insertion_id = unit
    
    # Make sure we can edit this sequence
    sequence_metadata = db.get_sequence_metadata(sequence_id)
    if sequence_metadata["sequencetype"] != "Saved":
        raise Exception("Cannot edit sequence")

    # Parse the component JSON if present
    component = None
    if len(body) != 0:
        component = json.loads(body)

    # Are we working with an existing component?
    if component_id != 0:
        # Yes, so update the existing component
        sequence_manager.UpdateComponent(
                username, int(sequence_id),
                int(component_id), 
                int(insertion_id),
                component)
    else:
        # No, so add a new component
        component_id = sequence_manager.AddComponent(
                username, int(sequence_id),
                int(insertion_id),
                component)

        # Update the client to show the new component
        client_state["componentid"] = component_id

    # Return the new state
    return save_client_state_and_return(
            client_state, username)

# Handle POST /sequence/[sequenceid]/reagent/[reagentid]
def handle_post_reagent(s_id, r_id, client_state, username, body):
    '''
    Function expects integers sequence id and reagent id.
    Function also expects a client state, a string username, and
    a string for the body sent with the POST request.
    Function calls save client and return then returns the output of the
    function called.
    '''
    # Extract sequence and reagent IDs
    sequence_id = int(s_id)
    reagent_id = int(r_id)

    # Make sure we can edit this sequence
    sequence_metadata = db.get_sequence_metadata(sequence_id)
    if sequence_metadata["sequencetype"] != "Saved":
        raise Exception("Cannot edit sequence")

    # Save the reagent
    reagent = json.loads(body)
    db.update_reagent(
            reagent_id, 
            reagent["name"],
            reagent["description"])

    # Flag the sequence validation as dirty
    db.update_sequence_dirty_flag(sequence_id, True)

    # Return the new state
    return save_client_state_and_return(client_state, db, username)

# POST Classes
class Elixys_Post_Component:
    '''
    Class shall represent the POST Elixys/sequence/<sequence_id>/component/<component_id>
    web requests
    '''
    @elixys_post.route('/Elixys/sequence/<s_id>/component/<c_id>/<unit>',
            methods=['POST'])
    @elixys_post.route('/Elixys/sequence/<s_id>/component/<c_id>',
            methods=['POST'])
    @requires_auth
    def component_post_index(s_id, c_id, unit=None):
        '''
        This function handles all POST for components from the
        client.
        Function expects an integer sequence_id, an integer component_id,
        and an optional parameter, insertion id.
        Function shall return the output of save client and return.
        Based on the body sent with the POST request, this function
        shall use sequence_manager to update the component passed in.
        '''
        
        auth = request.authorization
        username = str(auth.username)
        server_state = get_server_state(username)
        client_state = getCurrentClientState(username)
        # Get POST object
        body = request.data
        
        insertion_id = None
        if unit != None:
            insertion_id = int(unit)

        current_app.logger.debug('POST /sequence/s_id/component/c_id' +
                "\nRequest: " + str(request) + \
                "\nBody recieved: " + str(body) + \
                "\nInsertion ID: " + str(insertion_id))
        sequence_metdata = db.get_sequence_metadata(int(s_id))
        if sequence_metdata['sequencetype'] != 'Saved':
            raise Exception("Cannot edit sequence!")
        component = None
        
        if len(body) != 0:
            component = json.loads(body)
        if int(c_id) != 0:
            current_app.logger.debug("Updating component")
            # Check if insertion_id is none
            if insertion_id != None:
                sequence_manager.UpdateComponent(
                        username, int(s_id), int(c_id),
                        int(insertion_id), component)
            else:
                sequence_manager.UpdateComponent(
                        username, int(s_id), int(c_id),
                        None, component)

        else:
            # Check if insertion_id is None
            if insertion_id != None:
                c_id = sequence_manager.AddComponent(
                        username, int(s_id),
                        int(insertion_id), component)
                current_app.logger.debug("Adding component: " + \
                        str(c_id))
                client_state["componentid"] = c_id
            else :
                c_id = sequence_manager.AddComponent(
                        username, int(s_id),
                        None, component)
                current_app.logger.debug("Adding component: " + \
                        str(c_id))
                client_state["componentid"] = c_id

        return save_client_state_and_return(
                client_state, username)

class Elixys_Post_Reagent:
    '''
    Class shall represent the POST Elixys/sequence/<sequence_id>/reagent/<reagent_id>
    web requests
    '''
    @elixys_post.route('/Elixys/sequence/<s_id>/reagent/<r_id>',
            methods=['POST'])
    @requires_auth
    def reagent_post_index(s_id, r_id):
        '''
        Function shall handle all POST .../reagent/<reagent_id>
        web requests.
        Function expects integers sequence id and reagent id to
        be passed in as parameters.
        Function returns the output of save client state and
        return.
        The function obtains the data of the body sent with
        the POST request and updates the reagent on the database
        before calling save client state and return.
        '''
        # Get objects
        
        auth = request.authorization
        username = str(auth.username)
        server_state = get_server_state(username)
        client_state = getCurrentClientState(username)
        # Get POST object
        body = request.data
        current_app.logger.debug("Body sent: " + str(body))

        # Make sure we can edit this sequence
        sequence_metadata = db.get_sequence_metadata(int(s_id))
        if sequence_metadata["sequencetype"] != "Saved":
            raise Exception("Cannot edit sequence")

        # Save the reagent
        reagent = json.loads(body)
        db.update_reagent( 
                int(r_id),
                reagent["name"],
                reagent["description"])

        # Flag the sequence validation as dirty
        db.update_sequence_dirty_flag(int(s_id), True)

        # Return the new state
        return save_client_state_and_return(
                client_state, username)

class Elixys_Post_Home:
    '''
    Class shall represent the POST /Elixys/HOME web request.
    '''
    @elixys_post.route('/Elixys/HOME', methods=['POST'])
    @requires_auth
    def home_post_index():
        '''
        Function shall handle POST /HOME requests from the client.
        Function expects no parameters to be passed in.
        Function shall return the output of save client
        and return function.
        Function checks the body sent with the POST request
        and obtains the action type and target, then handles
        what should be updated on the client state variable
        before returning via save client state and return.
        '''
        # Get objects
        
        auth = request.authorization
        username = str(auth.username)
        server_state = get_server_state(username)
        client_state = getCurrentClientState(username)
        # Get POST object
        # body = ... obtain POST object sent
        body = request.data
        current_app.logger.debug("POST REQUEST:" + str(request) + \
                 "\nBody Sent: " + str(request.data) + \
                 "\nClient State: " + str(client_state) + \
                 "\nServer State: " + str(server_state))

        # Make sure we are on the home page
        if client_state["screen"] != "HOME":
            raise Exceptions.StateMisalignmentException()

        # Parse the JSON string in the body
        JSON_body = json.loads(body)

        # Check which option the user selected
        action_type = str(JSON_body["action"]["type"])
        action_target_id = str(JSON_body["action"]["targetid"])
        if action_type == "BUTTONCLICK":
            if action_target_id == "SEQUENCER":
                # Switch states to the last Select Sequence screen
                client_state = direct_to_last_select_screen(client_state)
                return save_client_state_and_return(
                        client_state, username)
            elif action_target_id == "VIEWRUN":
                # Switch to Run Sequence
                client_state["screen"] = "RUN"
                client_state["sequenceid"] = (
                        server_state["runstate"]["sequenceid"])
                client_state["componentid"] = (
                        server_state["runstate"]["componentid"])
                return save_client_state_and_return(
                        client_state, username)
        raise Exceptions.StateMisalignmentException()

class Elixys_Post_Select:
    '''
    Class shall represent the POST /Elixys/SELECT web request.
    '''
    @elixys_post.route('/Elixys/SELECT', methods=['POST'])
    @requires_auth
    def select_post_index():
        '''
        Function shall handle POST /SELECT requests from the client.
        Function expects no parameters to be passed in.
        Function checks what the action type and target from the
        body sent with the POST web request.
        Function returns either the output of the save client state 
        and return function or returns the output of the prompt handler
        for a sequence run.
        '''
        # Get objects
        
        auth = request.authorization
        username = str(auth.username)
        server_state = get_server_state(username)
        client_state = getCurrentClientState(username)
        # Get POST object
        # body = ... obtain POST object sent
        body = request.data
        current_app.logger.debug("POST REQUEST:" + str(request) + \
                "\nBody Sent: " + \
                str(request.data))

        # Make sure we are on Select Sequence
        if not client_state["screen"].startswith("SELECT"):
            raise Exceptions.StateMisalignmentException()

        # Parse the JSON string in the body
        body_JSON = json.loads(body)

        # Check which option the user selected
        action_type = str(body_JSON["action"]["type"])
        action_target_id = str(body_JSON["action"]["targetid"])
        sequence_id = body_JSON["sequenceid"]
        if action_type == "BUTTONCLICK":
            if action_target_id == "SEQUENCER":
                # Switch states to Home
                client_state["screen"] = "HOME"
                return save_client_state_and_return(
                    client_state, username)
            elif action_target_id == "VIEWSEQUENCE":
                # Switch states to View Sequence
                client_state["screen"] = "VIEW"
                client_state["sequenceid"] = sequence_id
                client_state["componentid"] = 0
                return save_client_state_and_return(
                    client_state, username)
            elif action_target_id == "EDITSEQUENCE":
                # Switch states to Edit Sequence
                client_state["screen"] = "EDIT"
                client_state["sequenceid"] = sequence_id
                client_state["componentid"] = 0
                return save_client_state_and_return(
                    client_state, username)
            elif action_target_id == "RUNSEQUENCE":
                # Show the Run Sequence prompt
                return show_run_sequence_prompt(
                        client_state, username, sequence_id)
            elif action_target_id == "NEWSEQUENCE":
                # Show the Create Sequence prompt
                client_state["prompt"]["screen"] = "PROMPT_CREATESEQUENCE"
                client_state["prompt"]["show"] = True
                client_state["prompt"]["title"] = "NEW SEQUENCE"
                client_state["prompt"]["text1"] = "SEQUENCE NAME"
                client_state["prompt"]["edit1"] = True
                client_state["prompt"]["edit1default"] = ""
                client_state["prompt"]["edit1validation"] = \
                        "type=string; required=true"
                client_state["prompt"]["text2"] = "SEQUENCE DESCRIPTION"
                client_state["prompt"]["edit2"] = True
                client_state["prompt"]["edit2validation"] = \
                        "type=string; required=false"
                client_state["prompt"]["edit2default"] = ""
                client_state["prompt"]["buttons"] = [{"type":"button",
                    "text":"OK",
                    "id":"OK"},
                    {"type":"button",
                    "text":"CANCEL",
                    "id":"CANCEL"}]
                return save_client_state_and_return(
                        client_state, username)
            elif action_target_id == "COPYSEQUENCE":
                # Show the Copy Sequence prompt
                sequence = sequence_manager.GetSequence(
                        username, sequence_id, False)
                client_state["prompt"]["screen"] = "PROMPT_COPYSEQUENCE"
                client_state["prompt"]["show"] = True
                client_state["prompt"]["title"] = "COPY SEQUENCE"
                client_state["prompt"]["text1"] = "SEQUENCE NAME"
                client_state["prompt"]["edit1"] = True
                client_state["prompt"]["edit1default"] = \
                        sequence["metadata"]["name"] + " Copy"
                client_state["prompt"]["edit1validation"] = \
                        "type=string; required=true"
                client_state["prompt"]["text2"] = "SEQUENCE DESCRIPTION"
                client_state["prompt"]["edit2"] = True
                client_state["prompt"]["edit2default"] = \
                        sequence["metadata"]["comment"]
                client_state["prompt"]["edit2validation"] = \
                        "type=string; required=false"
                client_state["prompt"]["buttons"] = [{"type":"button",
                    "text":"OK",
                    "id":"OK"},
                    {"type":"button",
                    "text":"CANCEL",
                    "id":"CANCEL"}]
                client_state["sequenceid"] = sequence_id
                return save_client_state_and_return(
                        client_state, username)
            elif action_target_id == "DELETESEQUENCE":
                # Show the Delete Sequence prompt
                sequence = sequence_manager.GetSequence(
                        username, sequence_id, False)
                client_state["prompt"]["screen"] = "PROMPT_DELETESEQUENCE"
                client_state["prompt"]["show"] = True
                client_state["prompt"]["title"] = "DELETE SEQUENCE"
                client_state["prompt"]["text1"] = \
                        "Are you sure that you want to " + \
                        "delete the sequence \"" + \
                        sequence["metadata"]["name"] + "\"?"
                client_state["prompt"]["edit1"] = False
                client_state["prompt"]["text2"] = ""
                client_state["prompt"]["edit2"] = False
                client_state["prompt"]["buttons"] = [{"type":"button",
                    "text":"YES",
                    "id":"YES"},
                    {"type":"button",
                    "text":"NO",
                    "id":"NO"}]
                client_state["sequenceid"] = sequence_id
                return save_client_state_and_return(
                        client_state, username)
        elif action_type == "TABCLICK":
            if action_target_id == "SAVEDSEQUENCES":
                # Switch states to the Saved Sequences tab
                client_state["screen"] = "SELECT_SAVEDSEQUENCES"
                client_state["lastselectscreen"] = "SAVED"
                client_state["sequenceid"] = sequence_id
                return save_client_state_and_return(
                        client_state, username)
            elif action_target_id == "RUNHISTORY":
                # Switch states to the Run History tab
                client_state["screen"] = "SELECT_RUNHISTORY"
                client_state["lastselectscreen"] = "HISTORY"
                client_state["sequenceid"] = sequence_id
                return save_client_state_and_return(
                        client_state, username)
        elif action_type == "HEADERCLICK":
            if client_state["screen"] == "SELECT_SAVEDSEQUENCES":
            # Change the select sequences sort order
                if action_target_id == "name":
                    if client_state["selectsequencesort"]["column"] == "name":
                        if client_state["selectsequencesort"]["mode"] == "down":
                            client_state["selectsequencesort"]["mode"] = "up"
                        else:
                            client_state["selectsequencesort"]["mode"] = "down"
                    else:
                        client_state["selectsequencesort"]["column"] = "name"
                        client_state["selectsequencesort"]["mode"] = "down"
                    return save_client_state_and_return(
                            client_state, username)
                elif action_target_id == "comment":
                    if client_state["selectsequencesort"]["column"] == "comment":
                        if client_state["selectsequencesort"]["mode"] == "down":
                            client_state["selectsequencesort"]["mode"] = "up"
                        else:
                            client_state["selectsequencesort"]["mode"] = "down"
                    else:
                        client_state["selectsequencesort"]["column"] = "comment"
                        client_state["selectsequencesort"]["mode"] = "down"
                    return save_client_state_and_return(
                            client_state, username)
                elif client_state["screen"] == "SELECT_RUNHISTORY":
                    # Change the run history sort order
                    if action_target_id == "name":
                        if client_state["runhistorysort"]["column"] == "name":
                            if client_state["runhistorysort"]["mode"] == "down":
                                client_state["runhistorysort"]["mode"] = "up"
                            else:
                                client_state["runhistorysort"]["mode"] = "down"
                        else:
                            client_state["runhistorysort"]["column"] = "name"
                            client_state["runhistorysort"]["mode"] = "down"
                        return save_client_state_and_return(
                                client_state, username)
                    elif action_target_id == "comment":
                        if client_state["runhistorysort"]["column"] == "comment":
                            if client_state["runhistorysort"]["mode"] == "down":
                                client_state["runhistorysort"]["mode"] = "up"
                            else:
                                client_state["runhistorysort"]["mode"] = "down"
                        else:
                            client_state["runhistorysort"]["column"] = "comment"
                            client_state["runhistorysort"]["mode"] = "down"
                        return save_client_state_and_return(
                                client_state, username)
                    elif action_target_id == "creator":
                        if client_state["runhistorysort"]["column"] == "creator":
                            if client_state["runhistorysort"]["mode"] == "down":
                                client_state["runhistorysort"]["mode"] = "up"
                            else:
                                client_state["runhistorysort"]["mode"] = "down"
                        else:
                            client_state["runhistorysort"]["column"] = "creator"
                            client_state["runhistorysort"]["mode"] = "down"
                        return save_client_state_and_return(
                                client_state, username)
                    elif action_target_id == "date&time":
                        if client_state["runhistorysort"]["column"] == "date&time":
                            if client_state["runhistorysort"]["mode"] == "down":
                                client_state["runhistorysort"]["mode"] = "up"
                            else:
                                client_state["runhistorysort"]["mode"] = "down"
                        else:
                            client_state["runhistorysort"]["column"] = "date&time"
                            client_state["runhistorysort"]["mode"] = "down"
                        return save_client_state_and_return(
                                client_state, username)
        # Unhandled use case
        raise Exceptions.StateMisalignmentException() 

class Elixys_Post_View:
    '''
    Class shall represent the POST /Elixys/VIEW web request.
    '''
    @elixys_post.route('/Elixys/VIEW', methods=['POST'])
    @requires_auth
    def view_post_index():
        '''
        Function shall handle POST /VIEW requests from the client.
        Function expects no parameters to be passed in.
        Function shall obtain the action type and target from the
        body sent with the POST web request. The function shall
        determine whether to call the save client state and return
        function, to call the show run sequence prompt function, or
        to call the show run from component prompt funciton.
        Function shall return the output of one of the functions
        based on the body sent.
        '''
        # Get objects
        
        auth = request.authorization
        username = str(auth.username)
        server_state = get_server_state(username)
        client_state = getCurrentClientState(username)
        # Get POST object
        # body = ... obtain POST object sent
        body = request.data
        current_app.logger.debug("POST REQUEST:" + str(request) + \
                "\nBody Sent: " + \
                str(request.data))

        # Make sure we are on View Sequence
        if client_state["screen"] != "VIEW":
            raise Exceptions.StateMisalignmentException()

        # Parse the JSON string in the body and extract the action type and target
        body_JSON = json.loads(body)
        action_type = str(body_JSON["action"]["type"])
        action_target_id = str(body_JSON["action"]["targetid"])

        # Call the base sequence POST handler first
        if handle_post_base_sequence(client_state, username,
                action_type, action_target_id):
            return save_client_state_and_return(
                    client_state, username)

        # Handle View Sequence specific requests
        if action_type == "BUTTONCLICK":
            if action_target_id == "EDITSEQUENCE":
                # Switch states to Edit Sequence
                client_state["screen"] = "EDIT"
                return save_client_state_and_return(
                        client_state, username)
            elif action_target_id == "RUNSEQUENCE":
                # Show the Run Sequence prompt
                return show_run_sequence_prompt(client_state, 
                        username, client_state["sequenceid"])
            elif action_target_id == "RUNSEQUENCEHERE":
                # Show the Run Sequence From Component prompt
                return show_run_sequence_from_component_prompt(
                        client_state, username,
                        client_state["sequenceid"],
                        client_state["componentid"])
        # Unhandled use case
        raise Exceptions.StateMisalignmentException()

class Elixys_Post_Edit:
    '''
    Class shall represent the POST /Elixys/EDIT web request.
    '''
    @elixys_post.route('/Elixys/EDIT', methods=['POST'])
    @requires_auth
    def edit_post_index(): 
        '''
        Function shall handle POST /VIEW requests from the client.
        Function expects no parameters to be passed in.
        Function returns the output of the save_client_state_and_return
        or prompt functions based on what the action type or target sent
        from the body of the POST web request.
        '''
        # Get objects
        
        auth = request.authorization
        username = str(auth.username)
        server_state = get_server_state(username)
        client_state = getCurrentClientState(username)
        # Get POST object
        # body = ... obtain POST object sent
        body = request.data
        current_app.logger.debug("POST REQUEST:" + str(request) + \
                "\nBody Sent: " + \
                str(request.data))

        # Make sure we are on Edit Sequence
        if client_state["screen"] != "EDIT":
            Exceptions.StateMisalignmentException()

        # Parse the JSON string in the body and extract the action type and target
        JSON_body = json.loads(body)
        action_type = str(JSON_body["action"]["type"])
        action_target_id = str(JSON_body["action"]["targetid"])

        # Call the base sequence POST handler first
        if handle_post_base_sequence(
                client_state, username,
                action_type, action_target_id):
            return save_client_state_and_return(
                    client_state, username)
        # Handle Edit Sequence specific requests
        if action_type == "BUTTONCLICK":
            if action_target_id == "VIEWSEQUENCE":
                # Switch states to View Sequence
                client_state["screen"] = "VIEW"
                return save_client_state_and_return(
                        client_state, username)
            elif action_target_id == "RUNSEQUENCE":
                # Show the Run Sequence prompt
                return show_run_sequence_prompt(
                        client_state, username,
                        client_state["sequenceid"])
            elif action_target_id == "RUNSEQUENCEHERE":
                # Show the Run Sequence From Component prompt
                return show_run_sequence_from_component_prompt(
                        client_state, username,
                        client_state["sequenceid"],
                        client_state["componentid"])

        # Unhandled use case
        raise Exceptions.StateMisalignmentException()

class Elixys_Post_Run:
    '''
    Class shall represent the POST /Elixys/RUN web request.
    '''
    @elixys_post.route('/Elixys/RUN', methods=['POST'])
    @requires_auth
    def run_post_index():
        '''
        Function shall handle POST /VIEW requests from the client.
        Function expects no parameters to be passed in.
        Function shall return the output of the save client
        and return function.
        '''
        # Get objects
        
        auth = request.authorization
        username = str(auth.username)
        server_state = get_server_state(username)
        client_state = getCurrentClientState(username)
        # Get POST object
        # body = ... obtain POST object sent
        body = request.data
        current_app.logger.debug("POST REQUEST:" + str(request) + \
                "\nBody Sent: " + \
                str(request.data))
        
        # Make sure we are on Run Sequence
        if client_state["screen"] != "RUN":
            current_app.logger.error("State Misalignment Exception")
            raise Exceptions.StateMisalignmentException()

        # Parse the JSON string in the body and extract the action type and target
        JSON_body = json.loads(body)
        action_type = str(JSON_body["action"]["type"])
        action_target_id = str(JSON_body["action"]["targetid"])
        current_app.logger.debug("Action Type: " + str(action_type) + \
                "\nAction Target: " + str(action_target_id))
        # Check which button the user clicked
        if action_type == "BUTTONCLICK":
            if action_target_id == "ABORTRUN":
                # Show the abort confirmation prompt
                # Using the CoreServer's show abort prompt
                core_server.ShowAbortSequencePrompt(username, True)
                return save_client_state_and_return(
                        client_state, username)
            elif action_target_id == "SEQUENCER":
                # Switch states to Home
                client_state["screen"] = "HOME"
                return save_client_state_and_return(
                        client_state, username)
            elif action_target_id == "TIMEROVERRIDE":
                # Override the timer
                core_server.OverrideTimer(username)
                return save_client_state_and_return(
                        client_state, username)
            elif action_target_id == "TIMERCONTINUE":
                # Stop the timer
                core_server.StopTimer(username)
                return save_client_state_and_return(
                        client_state, username)
            elif action_target_id == "USERINPUT":
                # Deliver user input
                current_app.logger.debug("USERINPUT")
                try:
                    core_server.DeliverUserInput(username)
                except Exception as ex:
                    raise Exception(str(ex))
                current_app.logger.debug(
                        "Delivered User Input, " + 
                        "save_client_state & return...")
                return save_client_state_and_return(
                        client_state, username)
            elif action_target_id == "PAUSERUN":
                # Pause the run
                core_server.PauseSequence(username)
                return save_client_state_and_return(
                        client_state, username)
            elif action_target_id == "CONTINUERUN":
                # Continue the run
                core_server.ContinueSequence(username)
                return save_client_state_and_return(
                        client_state, username)
        # Unhandled use case
        current_app.logger.error("State Misalignment Exception")
        raise Exceptions.StateMisalignmentException() 

class Elixys_Post_Prompt:
    '''
    Class shall represent the POST /Elixys/PROMPT.
    '''
    @elixys_post.route('/Elixys/PROMPT', methods=['POST'])
    @requires_auth
    def prompt_post_index():
        '''
        Function shall handle POST /VIEW requests from the client.
        Function expects no parameters to be passed in.
        Function returns the output of the save client and
        return function.
        '''
        # Get objects
        
        auth = request.authorization
        username = str(auth.username)
        server_state = get_server_state(username)
        client_state = getCurrentClientState(username)
        # Get POST object
        # body = ... obtain POST object sent
        body = request.data
        current_app.logger.debug("POST REQUEST:" + str(request) + \
                "\nBody Sent: " + str(request.data) + \
                "\nclientstate: " +  str(client_state) + \
                "\nserverstate: " + str(server_state))

        if (not client_state["prompt"]["show"]
                or not client_state["prompt"]["screen"].startswith("PROMPT")):
            current_app.logger.error("Client[prompt][show] is False, raising " + 
                    "State Misalignment Exception")
            raise Exceptions.StateMisalignmentException() 

        # Parse the JSON string in the body
        JSON_body = json.loads(body)

        # Extract the post parameters
        action_type = str(JSON_body["action"]["type"])
        action_target_id = str(JSON_body["action"]["targetid"])
        edit1 = str(JSON_body["edit1"])
        edit2 = str(JSON_body["edit2"])

        # The only recognized action from a prompt is a button click
        if action_type != "BUTTONCLICK":
            raise Exceptions.StateMisalignmentException() 
        # Interpret the response in context of the client state
        if client_state["prompt"]["screen"] == "PROMPT_CREATESEQUENCE":
            if action_target_id == "OK":
                # Sequence name is required
                if edit1 == "":
                    raise Exception("Sequence name is required")

                # Create the new sequence
                configuration = db.get_configuration()
                sequence_id = db.create_sequence(
                        edit1, username, edit2,
                        "Saved", configuration["reactors"],
                        configuration["reagentsperreactor"])

                # Hide the prompt and move the client to the editing the new sequence
                client_state["prompt"]["show"] = False
                client_state["screen"] = "EDIT"
                client_state["sequenceid"] = sequence_id
                current_app.logger.debug("Created a new sequence, calling" +
                        "save_client...from POST /PROMPT" + \
                        "\nSequence id returned : " + str(sequence_id) + \
                        "\nClient State: " + str(client_state))
                return save_client_state_and_return(
                        client_state, username)
            if action_target_id == "CANCEL":
                # Hide the prompt
                client_state["prompt"]["show"] = False
                return save_client_state_and_return(
                        client_state, username)
        elif client_state["prompt"]["screen"] == "PROMPT_COPYSEQUENCE":
            if action_target_id == "OK":
                # Sequence name is required
                if edit1 == "":
                    raise Exception("Sequence name is required")
                
                # create a copy of the sequence in the database
                new_sequence_id = sequence_manager.CopySequence(
                        username,
                        int(client_state["sequenceid"]),
                        str(edit1),
                        str(edit2))

                # Hide the prompt and move the client to the saved sequences screen
                client_state["prompt"]["show"] = False
                client_state["screen"] = "SELECT_SAVEDSEQUENCES"
                client_state["lastselectscreen"] = "SAVED"
                return save_client_state_and_return(
                        client_state, username)
            if action_target_id == "CANCEL":
                # Hide the prompt
                client_state["prompt"]["show"] = False
                return save_client_state_and_return(
                        client_state, username)
        elif client_state["prompt"]["screen"] == "PROMPT_DELETESEQUENCE":
            if action_target_id == "YES":
                # Delete the sequence from the database
                db.delete_sequence(client_state["sequenceid"])

                # Hide the prompt
                client_state["prompt"]["show"] = False
                return save_client_state_and_return(
                        client_state, username)
            if action_target_id == "NO":
                # Hide the prompt
                client_state["prompt"]["show"] = False
                return save_client_state_and_return(
                        client_state, username)
        elif client_state["prompt"]["screen"] == "PROMPT_RUNSEQUENCE":
            if action_target_id == "YES":
                # Fetch the sequence from the database and make sure it is valid
                sequence = sequence_manager.GetSequence(
                        username, client_state["sequenceid"])
                if not sequence["metadata"]["valid"]:
                    raise Exceptions.InvalidSequenceException(
                            str(client_state['sequenceid']))
                # Run the sequence
                core_server.RunSequence(username, client_state["sequenceid"])

                # Hide the prompt and switch states to Run Sequence
                client_state["prompt"]["show"] = False
                client_state["screen"] = "RUN"
                
                current_app.logger.debug("From POST /PROMPT, calling save client")

                return save_client_state_and_return(
                        client_state, username)
            if action_target_id == "NO":
                # Hide the prompt
                client_state["prompt"]["show"] = False
                return save_client_state_and_return(
                        client_state, username)
        elif client_state["prompt"]["screen"] == "PROMPT_RUNSEQUENCEFROMCOMPONENT":
            if action_target_id == "YES":
                # Fetch the sequence from the database and make sure it is valid
                sequence = sequence_manager.GetSequence(
                        username,
                        int(client_state["sequenceid"]))
                if not sequence["metadata"]["valid"]:
                    raise Exceptions.InvalidSequenceException(client_state['sequenceid'])
                
                # Run the sequence from the component
                core_server.RunSequenceFromComponent(username,
                        client_state["sequenceid"],
                        client_state["componentid"])

                # Hide the prompt and switch states to Run Sequence
                client_state["prompt"]["show"] = False
                client_state["screen"] = "RUN"
                return save_client_state_and_return(
                        client_state, username)
            if action_target_id == "NO":
                # Hide the prompt
                client_state["prompt"]["show"] = False
                return save_client_state_and_return(
                        client_state, username)
        elif client_state["prompt"]["screen"] == "PROMPT_UNITOPERATION":
            # Currently unused
            return save_client_state_and_return(
                        client_state, username)
        elif client_state["prompt"]["screen"] == "PROMPT_SOFTERROR":
            # Pass the user's decision to the core server
            core_server.SetSoftErrorDecision(username, action_target_id)
        elif client_state["prompt"]["screen"] == "PROMPT_ABORTRUN":
            if action_target_id == "YES":
                # Abort the run and return to the home page
                core_server.AbortSequence(username)
                client_state["prompt"]["show"] = False
                client_state["screen"] = "HOME"
                return save_client_state_and_return(
                        client_state, username)
            if action_target_id == "NO":
                # Hide the prompt
                core_server.ShowAbortSequencePrompt(username, False)
                return save_client_state_and_return(
                        client_state, username)
        # Unhandled use case
        raise Exceptions.StateMisalignmentException() 
