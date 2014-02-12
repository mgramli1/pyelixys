import json
from validate import Validator
from validate import VdtTypeError

comp_vtor = Validator()

def check_cassette_details(details):
    '''
    Validates the "details"
    of the cassette component.
    '''
    # First check ids
    detail_valid_keys = [
            "sequenceid",
            "id",
            "reactor"]
    for k1,v1 in details.iteritems():
        if k1 in detail_valid_keys:
            comp_vtor.check("integer(min=1)",v1)
    # Check strings
    detail_valid_keys = [
        "note",
        "componenttype",
        "type",
        ]
    for k1,v1 in details.iteritems():
        if k1 in detail_valid_keys:
            comp_vtor.check("string",v1)

    # Check list of integers
    for reagent_id in details['reagentids']:
        comp_vtor.check("integer(min=1)", reagent_id)
    # Check boolean(s)
    comp_vtor.check("boolean", details["validationerror"])

    return details

def check_add_details(details):
    '''
    Validates the "details"
    of the add component.
    '''
    # First check ids/integers
    detail_valid_keys = [
            "sequenceid",
            "reactor",
            "deliverytime",
            "deliveryposition",
            "reagent",
            "deliverypressure",
            "id"]
    for k1,v1 in details.iteritems():
        if k1 in detail_valid_keys:
            comp_vtor.check("integer(min=0)",v1)

    # Check strings
    detail_valid_keys = [
            "componenttype",
            "deliverytimevalidation",
            "reagentvalidation",
            "deliverypositionvalidation",
            "note",
            "reactorvalidation",
            "type"]
    for k1,v1 in details.iteritems():
        if k1 in detail_valid_keys:
            comp_vtor.check("string(min=0)",v1)

    # Check boolean
    comp_vtor.check("boolean", details['validationerror'])

    return details

def check_details(details):
    '''
    Function shall check what
    type of component the details
    are for and route to the correct
    check function
    '''
    # Convert from string to dictionary
    details = json.loads(details)
    if details['componenttype'] == 'CASSETTE':
        check_cassette_details(details)
    elif details['componenttype'] == 'ADD':
        check_add_details(details)
    return details

def component_check(params):
    """
    Checks if component parameters
    are validate.
    Function expects a dictionary type
    object that shall represent each
    key of the component's fields
    """
    valid_int_keys = [
            "component_id",
            "sequence_id",
            "previous_component_id",
            "next_component_id"]
    valid_str_keys = [
            "type",
            "note",
            "details"]

    for k,v in params.iteritems():
        # Check integer cases
        if k in valid_int_keys:
            comp_vtor.check("integer(min=0)",v)

        # Check string cases
        elif k in valid_str_keys:
            if k == 'type':
            comp_vtor.check("string(min=1, max=20)", v)
            elif k == 'note':
            comp_vtor.check("string(min=0, max=64)", v)
        # Check details dict
        elif k == 'details':
            comp_vtor.check("string(min=1, max=2048)", v)
            # Check all the objects in the details dict
            check_details(v)
                else:
            # Else, we recieved an invalid key
            # Flag an error?
            print "%s,%s" % (k,v)

    return params

def check_user_clientstate(clientstate):
    '''
    Checks the clientstate fields for
    a user's "clientstate" field.
    '''
    valid_int_clientstate_keys = [
            'sequenceid',
            'componentid']
    valid_str_clientstate_keys = [
            'lastselectscreen',
            'screen',
            'type']
    valid_dict_clientsate_keys = [
            'runhistorysort',
            'selectsequencesort',
            'prompt']
    for key, value in clientstate.iteritems():
        # Check integer case
        if key in valid_int_clientstate_keys:
            comp_vtor.check("integer(min=1)", value)

        # Check string case
        elif key in valid_str_clientstate_keys:
            comp_vtor.check("string(min=0, max=40)", value)

        # Check dict case
        elif key in valid_dict_clientsate_keys:
            # TODO Check the dictionary
            pass
        else:
            # We found an unknown, flag error?
            print "%s,%s" % (key, value)

def check_user(params):
    '''
    Function shall check
    if the values for the user
    are valid.
    '''
    # Check valid strings
    valid_keys = [
            'username',
            'password',
            'firstname',
            'lastname',
            'email',
            'phone']
    valid_int_keys = [
            'role_id',
            'message_level'
            ]

    for key, value in params.iteritems():
        # Check valid strings
        if key in valid_keys:
            comp_vtor.check("string(min=0, max=40)", value)

        # Check valid integers
        elif key in  valid_int_keys:
            comp_vtor.check("integer(min=1)", value)

        # Check clientstate dict
        elif key == "clientstate":
            clientstate = json.dumps(params['clientstate'])
            check_user_clientstate(clientstate)

        # Else, we have an unknown key, flag it?
        else:
            print "%s,%s" % (key, value)

# TODO remove this (for testing)
#"runhistorysort": {"column": "date&time", "type": "sort", "mode": "down"},
#"lastselectscreen": "SAVED",
#"selectsequencesort": {"column": "name", "type": "sort", "mode": "down"},
#"prompt": {"show": false, "screen": "", "text2": "", "text1": "", "edit2default": "", "buttons": [], "title": "", "edit1validation": "", "edit1": false, "edit2": false, "edit1default": "", "edit2validation": "", "type": "promptstate"},
#"screen": "HOME", "type": "clientstate", "componentid": 0}


comp_vtor.functions['check_component'] = component_check
comp_vtor.functions['check_user'] = user_check

### For Testing as a Script ###
if __name__ == "__main__":
    component_data = { 'component_id':'1',
            'sequence_id':'1',
            'previous_component_id':'1',
            'next_component_id':'3',
            'type':'CASSETTE',
            'note':'',
            'details': '{"note": "",\
                    "sequenceid": 1, "reactor": 1, "validationerror": false,\
                    "componenttype": "CASSETTE",\
                    "reagentids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],\
                    "type": "component", "id": 1}'}

    v = comp_vtor.check('check_component', component_data)
