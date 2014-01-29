#!/usr/bin/env python
""" Install Component
"""
from pyelixys.sequence.components.component import Component
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
        self.thread = InstallThread()

class InstallThread(ComponentThread):
    '''
    Main Install Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self):
        super(InstallThread, self).__init__()
