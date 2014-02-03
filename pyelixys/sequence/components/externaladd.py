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
        self.thread = ExternalAddThread()

class ExternalAddThread(ComponentThread):
    '''
    Main External Add Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self):
        super(ExternalAddThread, self).__init__()
