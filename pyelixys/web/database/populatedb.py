'''
Populates the SQLite database with
a user and a sequence with three components.
'''
import json
from pyelixys.web.database.model import session
from pyelixys.web.database.model import Roles
from pyelixys.web.database.model import User
from pyelixys.web.database.model import Sequence
from pyelixys.web.database.model import Component
from pyelixys.web.database.model import Reagents
from pyelixys.web.database.model import metadata


# Import hashing library for pw hash
import hashlib

def create_role():
    # Create admin role
    role = Roles('Administrator', 255)
    session.add(role)
    session.commit()
    return role

def get_default_user_client_state():
    """ Silly work around for current webserver """
    #TODO Remove client default state server dependency
    return ({"sequenceid": 0,
            "runhistorysort": {"column": "date&time", "type": "sort", "mode": "down"},
            "lastselectscreen": "SAVED",
            "selectsequencesort": {"column": "name", "type": "sort", "mode": "down"},
            "prompt": {
                "show": False, "screen": "", "text2": "", "text1": "",
                "edit2default": "", "buttons": [], "title": "",
                "edit1validation": "", "edit1": False, "edit2": False,
                "edit1default": "", "edit2validation": "",
                "type": "promptstate"},
            "screen": "HOME",
            "type": "clientstate",
            "componentid": 0})

def get_default_component_state(cassette, reactor_count):
    ''' Silly work around for the current webserver '''
    #TODO Remove Component state/details dependency
    # Create a dictionary and append to it the
    # details needed
    details_dict = {}
    details_dict['note'] = cassette.Note
    details_dict['sequenceid'] = cassette.SequenceID
    details_dict['reactor'] = reactor_count
    details_dict['validationerror'] = False
    details_dict['componenttype'] = cassette.Type
    details_dict['type'] = 'component'
    details_dict['id'] = cassette.ComponentID
    # For all the cassette's reagents, append their ids
    details_dict['reagent'] = []
    for reagent in cassette.reagents:
        details_dict['reagent'].append(reagent.ReagentID)
    return details_dict

def create_user(role_id):
    # Let's create a default user
    # Encrypt the password using md5 and reutrn as hex
    new_user = User()
    new_user.Username = 'devel'
    new_user.Password = hashlib.md5('devel').hexdigest()
    new_user.FirstName = 'Sofiebio'
    new_user.LastName = 'Developer'
    new_user.Email = 'developer@sofiebio.com'
    new_user.RoleID = role_id
    new_user.ClientState = json.dumps(
            get_default_user_client_state())
    session.add(new_user)
    session.commit()

    return new_user

def create_sequence(user_id):
    # Create a new sequence for the user
    new_seq = Sequence()
    new_seq.Name = 'Sequence 1'
    new_seq.Component = 'Test Sequence'
    new_seq.Type = 'Saved'
    new_seq.UserID = user_id
    session.add(new_seq)
    session.commit()
    return new_seq

def create_cassette_components(sequence_id):
    # Create a new set of component cassettes
    cass_list = []
    for cass_count in range(1,4):
        new_comp = Component()
        new_comp.SequenceID = sequence_id
        new_comp.Type = 'CASSETTE'
        new_comp.Note = ''
        # Leave details empty, update later
        new_comp.Details = ''
        session.add(new_comp)
        session.commit()
        cass_list.append(new_comp)
    return cass_list

def create_reagents(sequence_id, cassettes):
    # Let's create some empty reagents
    # For each of the 3 cassettes, create
    # 12 reagents
    for cassette in cassettes:
        for reg_count in range(1,13):
            reagent = Reagents()
            reagent.SequenceID = sequence_id
            reagent.Position = reg_count
            reagent.component = cassette
            reagent.ComponentID = cassette.ComponentID
            session.add(reagent)
            session.commit()

def update_sequence_details(sequence):
    # Update the first component id and
    # component count of the sequence's fields
    # Query for the first component matched
    component_id = session.query(Component).filter_by(
            SequenceID = sequence.SequenceID).first().ComponentID
    sequence.FirstComponentID = component_id
    sequence.ComponentCount = 3
    sequence.Valid = 1
    session.commit()

def update_component_details(cassettes):
    # Update the details field of each new
    # cassette component
    # Keep a reactor count
    reactor_count = 1
    for cassette in cassettes:
        cassette.Details = json.dumps(
                get_default_component_state(
                cassette,
                reactor_count))
        session.commit()
        reactor_count += 1

if __name__ == '__main__':
    '''
    Running this file as a script
    shall execute the following which
    will create a new role and user.
    The script shall also create a
    default sequence with three cassettes
    that contain no reagents.
    '''
    metadata.create_all(checkfirst=True)
    role = create_role()
    user = create_user(role.RoleID)
    sequence = create_sequence(user.UserID)
    cassettes = create_cassette_components(sequence.SequenceID)
    create_reagents(sequence.SequenceID, cassettes)
    update_sequence_details(sequence)
    update_component_details(cassettes)
    from IPython import embed
    embed()
