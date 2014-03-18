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
        self.reactor = self.reactors[dbcomp.details['reactor']]
        self.note = dbcomp.details['note']
        # Set a thread
        self.thread = InstallThread(self)

    def run(self):
        '''
        Executes the 'Install'
        '''
        self.component_status = "Starting the Install run()"
        self.system.initialize()
        self.component_status = "Move to install for reactor %d" % self.reactor.id_
        self.system.reagent_robot.move_install(self.reactor.id_)
        self.component_status = "Release the reagent robot brake"
        self.system.reagent_robot.brake_release()

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
        self.ins.run()
        self._is_complete.set()

if __name__ == '__main__':
    details = {"sequenceid": 14,
            "reactor": 2,
            "note": "",
            "message": "",
            "id": 107}



    class db(object):
        details = details

    ins = Install(db)
    from IPython import embed
    embed()

