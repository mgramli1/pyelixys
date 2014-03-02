#!/usr/bin/env python
""" External Add Component
"""
from component import Component
# import the component threading module
from componentthread import ComponentThread

class ExternalAdd(Component):
    """ External Add """
    def __init__(self, dbcomp):
        super(ExternalAdd, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']

        self.reagent_name = dbcomp.details['reagentname']
        self.reactor = dbcomp.details['reactor']
        self.message = dbcomp.details['message']
        self.validation_error = dbcomp.details['validationerror']
        self.note = dbcomp.details['note']
        # Set a thread
        self.thread = ExternalAddThread(self)

    def run(self):
        '''
        Start the externaladd thread
        '''
        self.thread.start()

class ExternalAddThread(ComponentThread):
    '''
    Main External Add Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self, external_add):
        '''
        Constructs and expects an
        ExternalAdd object
        '''
        super(ExternalAddThread, self).__init__()
        self.ext_add = external_add

    def run(self):
        '''
        Begins the run process of the
        ExternalAdd() unit operation.
        Runs as a thread
        '''
        self._is_complete.clear()

        self.ext_add.component_status = "Starting ExternalAdd run()"

        # Move Reactor
        self.ext_add.component_status = "Moving Reactor"
        # Move to the ADD position

        # TODO Move reactor to ADD
        # Check if we already at the correct position
        # if: reactor position is in the ADD position
        #   Check that the reactor is either up or down
        #   If all true, then we are in position
        # Else, we need to setup for the ExternalAdd op
        # else:
        #   needs_pressure_restore = False
        #   if: reactor position is in either one of the REACT positions
        #       if: reactor is up
        #           self.ext_add.system.pressure_regulators[1].set_pressure(30)
        #           needs_pressure_restore = True
        #
        #   self.ext_add.system.reactors[self.ext_add.reactor].lower() - Move Reactor down
        #   Enable reactor robot
        #
        #   if needs_pressure_restore:
        #       self.ext_add.system.pressure_regulators[1].set_pressure(60)
        #
        #   Move reactor to the ExternalAdd position
        #   self.ex_add.system.reactors[self.ex_add.system.reactors].lift()
        #   #Moves reactor up/raise reactor
        #   Disable the reactor robot

        self.ext_add.component_status = "Waiting for user input"
        # TODO Wait until we obtain user input


        self.ext_add.component_status = "Sucessfully finished " \
                "running the ExternalAdd operation"
        self._is_complete.set()



if __name__ == '__main__':
    a = {"componenttype": "EXTERNALADD", "sequenceid": 14,
            "reactor": 0, "validationerror": True,
            "reagentname": "",
            "reagentnamevalidation": "type=string; required=true",
            "note": "",
            "reactorvalidation": "type=enum-number; values=1,2,3; required=true",
            "message": "Externally add  to reactor 0.", "type": "component", "id": 114}


    class db(object):
        details = a
    ex = ExternalAdd(db)
    from IPython import embed
    embed()

