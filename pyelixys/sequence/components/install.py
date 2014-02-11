#!/usr/bin/env python
""" Install Component
"""
from component import Component
# import the component threading module
from componentthread import ComponentThread

class Install(Component):
    """ Install """
    def __init__(self, dbcomp):
        super(Install, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.message = dbcomp.details['message']
        self.reactor = dbcomp.details['reactor']
        self.validationerror = dbcomp.details['validationerror']
        self.note = dbcomp.details['note']
        # Set a thread
        self.thread = InstallThread(self)

    def run(self):
        '''
        Executes the 'Install'
        run thread and the Install
        object is passed into the
        InstallThread.
        '''
        self.thread.start()


class InstallThread(ComponentThread):
    '''
    Main Install Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self, install):
        '''
        Constructs a new thread and
        expects a Install object to be
        passed in.
        '''
        super(InstallThread, self).__init__()
        self.ins = install

    def run(self):
        '''
        Begins the run process of the
        Install unit operation.
        Runs as a thread
        '''
        self._is_complete.clear()

        self.ins.component_status = "Starting the Install run()"

        self.ins.component_status = "Moving reactor"

        # TODO Move reactor to INSTALL
        # Check if we already at the correct position
        # if: reactor position is in the Install position
        #   Check that the reactor is either up or down
        #   If all true, then we are in position
        # Else, we need to setup for the Install op
        # else:
        #   needs_pressure_restore = False
        #   if: reactor position is in either one of the INSTALL positions
        #       if: reactor is up
        #           self.ins.system.pressure_regulators[1].set_pressure(30)
        #           needs_pressure_restore = True
        #
        #   self.ins.system.reactors[self.ins.reactor].lower() - Move Reactor down
        #   Enable reactor robot
        #
        #   if needs_pressure_restore:
        #       self.ins.system.pressure_regulators[1].set_pressure(60)
        #
        #   Move reactor to the Install position
        #   self.ins.system.reactors[self.ins.system.reactors].lift()
        #   #Moves reactor up/raise reactor
        #   Disable the reactor robot

        if self.ins.message:
            self.ins.component_status = "Waiting for user input"
            # TODO Wait for user input

        self.ins.component_status = "Sucessfully finished " \
                "running Install operation"
        self._is_complete.set()

if __name__ == '__main__':
    a = {"componenttype": "INSTALL",
            "sequenceid": 14, "reactor": 1,
            "validationerror": True,
            "messagevalidation": "type=string; required=true",
            "note": "",
            "reactorvalidation": "type=enum-number; values=1,2,3; required=true",
            "message": "", "type": "component", "id": 107}



    class db(object):
        details = a

    ins = Install(db)
    from IPython import embed
    embed()

