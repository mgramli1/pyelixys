#!/usr/bin/env python
""" Move Component
"""
from component import Component
# import the component threading module
from componentthread import ComponentThread

class Move(Component):
    """ Move """
    def __init__(self, dbcomp):
        super(Move, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.reactor = dbcomp.details['reactor']
        self.position = dbcomp.details['position']
        self.validation_error = dbcomp.details['validationerror']
        self.note = dbcomp.details['note']
        # Set a thread
        self.thread = MoveThread(self)

    def run(self):
        '''
        Executes the 'MOVE' run thread
        and the Move object is passed
        into the MoveThread
        '''
        self.thread.start()

class MoveThread(ComponentThread):
    '''
    Main Move Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self, move_component):
        super(MoveThread, self).__init__()
        self.move = move_component

    def run(self):
        '''
        Begins the run process of the
        Move unit operation.
        Function takes an Move class object
        which shall contain the details of
        the unit op's execution.
        '''
        self._is_complete.clear()

        self.move.component_status = "Starting the Move run()"

        ### Move reactor into the react position ###
        self.move.component_status = "Moving"
        #self.move.system.reactors[(self.move.reactor)].\
                #setPosition(self.move.position)
        # TODO Move reactor into the correct position

        self.move.component_status = "Successfully finished Move Operation"
        self._is_complete.set()


######## To Test ########
if __name__ == '__main__':
    a = {"componenttype": "MOVE", "sequenceid": 14, "reactor": 2,
            "validationerror": True,
            "positionvalidation":"type=enum-string; values=Install,Transfer,React1,"\
                    "Add,React2,Evaporate; required=true",
            "note": "",
            "reactorvalidation": "type=enum-number; values=1,2,3; required=true",
            "position": "1", "type": "component", "id": 113}
    class db(object):
        details = a

    a = Move(db)
    from IPython import embed
    embed()


