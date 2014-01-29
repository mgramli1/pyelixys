'''
Populates the SQLite database with
a user and a sequence with three components.
'''
from pyelixys.web.database.model import session
from pyelixys.web.database.model import Roles
from pyelixys.web.database.model import User
from pyelixys.web.database.model import Sequence
from pyelixys.web.database.model import Component
from pyelixys.web.database.model import Reagents

# Import hashing library for pw hash
import hashlib

def create_role():
    # Create admin role
    role = Roles('Administrator', 255)
    session.add(role)
    session.commit()
    return role

def get_default_client_state():
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


def create_user(role_id):
    # Let's create a default user
    # Encrypt the password using md5 and reutrn as hex
    new_user = User(
            'devel',
            hashlib.md5('devel').hexdigest(),
            'Sofiebio',
            'Developer',
            role_id,
            'developer@sofiebio.com',
            None,
            0,
            get_default_client_state())            
    # save & commit the session
    session.add(new_user)
    session.commit()
    return new_user

def create_sequence(user_id):
    # Create a new sequence for the user
    new_seq = Sequence(
            'Sequence 1',
            'Test Sequence',
            'Saved',
            '',
            user_id,
            0,
            0,
            1,
            0)
    # save & commit the session
    session.add(new_seq)
    session.commit()
    return new_seq

def create_cassette_components(sequence):
    # Create a new set of component cassettes
    cassette_list = []
    for cass_count in range(1,3):
        new_comp = Component()
        new_comp.SequenceID = sequence.SequenceID
        new_comp.PreviousComponentID = 0
        new_comp.NextComponentID = 0
        new_comp.Type = 'CASSETTE'
        new_comp.Note = ''
        # Leave details empty, update later
        new_comp.Details = ''
        session.add(new_comp)
        session.commit()
        # Save to list to return
        cassette_list.append(new_comp)
    return cassette_list

def create_regents(sequence):
    # Let's create some empty reagents
    # For each of the 3 cassettes, create
    # 12 reagents
    for cass_count in range(1,3):
        for reg_count in range(1,12):
            reagent = Reagent()
            reagent.SequenceID


if __name__ == '__main__':
    role = create_role()
    user = create_user(role.RoleID)
    sequence = create_sequence(user.UserID)
    cassettes = create_cassette_components(sequence)
    create_reagents(sequence)
