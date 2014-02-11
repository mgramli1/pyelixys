import json
from validate import Validator
from validate import VdtTypeError

comp_vtor = Validator()

def component_params(params):
    """
    Checks if component parameters
    are validate.
    Passed in argument is of type
    dictionary.
    """
    # Check integers
    valid_keys = [
            "component_id",
            "sequence_id",
            "previous_component_id",
            "next_component_id"]
    for k,v in params.iteritems():
        if k in valid_keys:
            comp_vtor.check("integer(min=1)", v)

    # Check strings
    valid_keys = [
            "type",
            "note",
            "details"]
    for k,v in params.iteritems():
        if k == 'type' and k in valid_keys:
            comp_vtor.check("string(min=1, max=20)", v)
        elif k == 'note' and k in valid_keys:
            comp_vtor.check("string(min=0, max=64)", v)
        elif k == 'details' and k in valid_keys:
            comp_vtor.check("string(min=1, max=2048)", v)
            # Check all the objects in the details dict
            details_params = json.loads(v)
            # First check ids
            detail_valid_keys = [
                    "sequenceid",
                    "id",
                    "reactor"]
            for k1,v1 in details_params.iteritems():
                if k1 in detail_valid_keys:
                    comp_vtor.check("integer(min=1)",v1)
            # Check strings
            detail_valid_keys = [
                "note",
                "componenttype",
                "type",
                ]
            for k1,v1 in details_params.iteritems():
                if k1 in detail_valid_keys:
                    comp_vtor.check("string",v1)

            # Check list of integers
            for reagent_id in details_params['reagentids']:
                comp_vtor.check("integer(min=1)", reagent_id)
            # Check boolean(s)
            comp_vtor.check("boolean", details_params["validationerror"])
    return params

comp_vtor.functions['check_component'] = component_params

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

