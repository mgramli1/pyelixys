# Import access to the Sequence ORM model
# and db session object

from pyelixys.web.database.model import Sequence
from pyelixys.web.database.model import loadSession
from pyelixys.sequence import comp_lookup as component_lookup

class SequenceManager(object):
    '''
    '''
    def __init__(self, sequence_id, username=None):
        '''
        '''
        self.load_sequence(sequence_id, username)

    def load_sequence(self, sequence_id, username=None):
        # Load a new session and open the sequence object
        session = loadSession()
        self.sequence = session.query(Sequence).filter_by(
                SequenceID = int(sequence_id)).first()
        self.username = str(username)
        
        self.process_components()

    def process_components(self):
        self.components = []
        # For each component, append to the components
        # list the component as an class object of the
        # component's type.
        for dbcomp in self.sequence.components:
            self.components.append(
                    component_lookup[
                        dbcomp.details[
                            'componenttype']](dbcomp))

    def pause_sequence(self):
        '''
        '''
        # If the sequence is running, check
        # if the sequence is not paused
        pass

    def abort_sequence(self):
        '''
        '''
        pass

    def continue_sequence(self):
        '''
        '''
        # Make sure the sequence is
        # running and is paused
        pass

if __name__ == '__main__':
    sm = SequenceManager(1)
    from IPython import embed
    embed()
