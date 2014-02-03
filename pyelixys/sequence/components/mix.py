#!/usr/bin/env python
""" Mix Component
"""
from component import Component
# import the component threading module
from componentthread import ComponentThread

class Mix(Component):
    """ Mix """
    def __init__(self, dbcomp):
        super(Mix, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.mix_time = dbcomp.details['mixtime']
        self.reactor = dbcomp.details['reactor']
        self.validation_error = dbcomp.details['validationerror']
        self.stir_speed = dbcomp.details['stirspeed']
        self.note = dbcomp.details['note']
        # Set a thread
        self.thread = MixThread()

class MixThread(ComponentThread):
    '''
    Main Mix Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self):
        super(MixThread, self).__init__()
