#!/usr/bin/env python
""" Move Component
"""
from pyelixys.sequence.components.component import Component
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
        self.thread = MoveThread()

class MoveThread(ComponentThread):
    '''
    Main Move Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self):
        super(MoveThread, self).__init__()
