'''
Populates the SQLite database with
a user and a sequence with three components.
'''
import json
from pyelixys.logs import dblog as log
from pyelixys.web.database.model import session
from pyelixys.web.database.model import Role
from pyelixys.web.database.model import User
from pyelixys.web.database.model import Sequence
from pyelixys.web.database.model import Component
from pyelixys.web.database.model import Reagent
from pyelixys.web.database.model import metadata


# Import hashing library for pw hash
import hashlib

def create_role():
    # Create admin role
    role = Role('Administrator', 255)
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

def create_user(role):
    # Let's create a default user
    # Encrypt the password using md5 and reutrn as hex
    new_user = User()
    new_user.Username = 'devel'
    new_user.Password = hashlib.md5('devel').hexdigest()
    new_user.FirstName = 'Sofiebio'
    new_user.LastName = 'Developer'
    new_user.Email = 'developer@sofiebio.com'
    new_user.role = role
    new_user.ClientState = json.dumps(
            get_default_user_client_state())
    session.add(new_user)
    session.commit()

    return new_user

def create_sequence(user):
    # Create a new sequence for the user
    new_seq = Sequence()
    new_seq.Name = 'Sequence 1'
    new_seq.Component = 'Test Sequence'
    new_seq.Type = 'Saved'
    new_seq.user = user
    session.add(new_seq)
    session.commit()
    user.selected_sequence = new_seq
    session.commit()
    return new_seq

def create_cassette_components(sequence):
    # Create a new set of component cassettes
    cass_list = []
    for cass_count in range(1,4):
        new_comp = Component()
        new_comp.sequence = sequence
        new_comp.Type = 'CASSETTE'
        new_comp.Note = ''
        # Leave details empty, update later
        new_comp.Details = ''
        session.add(new_comp)
        session.commit()
        cass_list.append(new_comp)
    return cass_list

def create_reagents(cassettes):
    # Let's create some empty reagents
    # For each of the 3 cassettes, create
    # 12 reagents
    for cassette in cassettes:
        for reg_count in range(1,13):
            reagent = Reagent()
            reagent.Position = reg_count
            reagent.component = cassette
            session.add(reagent)
            session.commit()

def update_sequence_details(sequence):
    # Update the first component id and
    # component count of the sequence's fields
    # Query for the first component matched
    comp = session.query(Component).filter_by(
            SequenceID = sequence.SequenceID).first()
    sequence.first_component = comp
    sequence.Valid = True
    session.commit()

def update_component_details(cassettes):
    # Update the details field of each new
    # cassette component
    # Keep a reactor count
    reactor_count = 1

    previous_cassette = None
    for cassette in cassettes:
        cassette.Details = json.dumps(
                get_default_component_state(
                cassette,
                reactor_count))
        session.commit()
        reactor_count += 1
        if not previous_cassette is None:
            cassette.previous_component = previous_cassette
            session.commit()
            previous_cassette.next_component = cassette
            session.commit()


        previous_cassette = cassette


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
    log.debug("Created Database")
    role = create_role()
    log.debug("Created Role")
    user = create_user(role)
    log.debug("Created User")
    sequence = create_sequence(user)
    log.debug("Created Seqence")
    cassettes = create_cassette_components(sequence)
    log.debug("Created Cassettes")
    create_reagents(cassettes)
    log.debug("Created Reagents")
    update_sequence_details(sequence)
    log.debug("Updated sequence details")
    update_component_details(cassettes)
    log.debug("Updated component details")
    user = session.query(User).first()
    from IPython import embed
    embed()
