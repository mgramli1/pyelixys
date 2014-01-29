#!/usr/bin/env python
""" Prompt Component
"""
from pyelixys.sequence.components.component import Component
# import the component threading module
from componentthread import ComponentThread

class Prompt(Component):
    """ Prompt """
    def __init__(self, dbcomp):
        super(Prompt, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.message = dbcomp.details['message']
        self.validationerror = dbcomp.details['validationerror']
        self.note = dbcomp.details['note']
        # Set a thread
        self.thread = PromptThread()

class PromptThread(ComponentThread):
    '''
    Main Prompt Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self):
        super(PromptThread, self).__init__()
