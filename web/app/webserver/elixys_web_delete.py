'''
This python file handles all DELETE requests from
a client.

Class imports:
-all flask components needed
-basicauth which allows user/pw vertification
-get current client state to obtain the client state
from the DB
-the database and sequence manager variables from
'web_service.py'
-the GET /state handler from 'elixys_web_get.py'

The variable "current_app" is used to log all events.
'''
# import flask components
from flask import Blueprint
from flask import current_app 
from flask import request
# import basic user auth
from app.userauth.basicauth import requires_auth

# import the db and sequence manager from elixysweb.py
# import utility that obtains the client state
from web_service import getCurrentClientState
from web_service import db, sequence_manager

# import the function that handles '/Elixys/state'
# from the GET handler
from elixys_web_get import Elixys_Get_State

# establish blueprint variable
elixys_delete = Blueprint('elixys_delete', __name__,
        template_folder='templates')

# Delete Class
class Elixys_Delete_Component:
    '''
    Elixys Delete Component class handles a DELETE
    request from the client. Class contains one
    method that requires authentication (a valid
    username and password on the database).
    '''
    @elixys_delete.route('/Elixys/sequence/<s_id>/component/<c_id>',
            methods=['DELETE'])
    @requires_auth
    def delete_index(s_id, c_id):
        '''
        Function handles a DELETE request from a web request
        in the form of:
        DELETE /Elixys/sequence/<sequenceid>/component/<componentid>
        Function expects two parameters, both integers, that are passed
        in from the web request.
        Function will delete the given sequence's component by it's id
        on the database. Function shall also update the client state
        by moving to the previous component on the "Edit Sequence"
        screen on the client.
        Function shall return the output of GET /Elixys/state.
        (See elixys_web_get.py)
        '''
        auth = request.authorization
        username = str(auth.username)
        client_state = getCurrentClientState(username)
        
        current_app.logger.debug("Handling request: " + str(request))
        
        # Make sure we can edit this sequence
        sequence_metadata = db.GetSequenceMetadata(username, int(s_id))
        if sequence_metadata["sequencetype"] != "Saved":
            raise Exception("Cannot edit sequence")

        # Is the user currently viewing this component?
        if ((client_state["sequenceid"] == int(s_id))
                and (client_state["componentid"] == int(c_id))):
            # Yes, so move the user to the previous component in the sequence
            previous_component = db.get_previous_component(int(c_id))
            if previous_component == None:
                raise Exception("Failed to find previous component")

            # Update the client state
            client_state["componentid"] = previous_component["id"]
            db.update_user_client_state(username, client_state)

        # Delete the sequence component
        sequence_manager.DeleteComponent(username, int(s_id), int(c_id))

        # Return the state
        current_app.logger.debug("Calling GET /state")
        get_state = Elixys_Get_State()
        return get_state.state_index()
