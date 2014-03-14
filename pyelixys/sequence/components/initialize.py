#!/usr/bin/env python
""" Initialize Component
"""
import time
from component import Component
# import the component threading module
from componentthread import ComponentThread

class Initialize(Component):
    """ Initialize"""
    def __init__(self, dbcomp):
        super(Initialize, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']

        # Set a thread
        self.thread = InitializeThread(self)

    def run(self):
        '''
        Executes the 'INITIALIZE'
        run thread and the Initialize
        object is passed into the
        InitializeThread.
        '''
        self.system.initialize()

class InitializeThread(ComponentThread):
    '''
    Main Initialize Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self, init):
        super(InitializeThread, self).__init__()
        self.init = init

    def run(self):
        '''
        Begins the run process of the
        Init() unit operation.
        Runs as a thread
        '''
        self._is_complete.clear()
        self.init.run()
        self._is_complete.set()

if __name__ == '__main__':
    details = {}
    details["note"] = ""
    details["sequenceid"] = 0
    details['id'] = 1

    class db(object):
        details = details

    i = Initialize(db)
    from IPython import embed
    embed()
