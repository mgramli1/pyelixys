#!/usr/bin/env python
""" Elute F18 Component
"""
from pyelixys.sequence.components.component import Component
# import the component threading module
from componentthread import ComponentThread

class EluteF18(Component):
    """ Elute F18 """
    def __init__(self, dbcomp):
        super(EluteF18, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.elute_time = dbcomp.details['elutetime']
        self.reactor = dbcomp.details['reactor']
        self.validation_error = dbcomp.details['validationerror']
        self.note = dbcomp.details['note']
        self.reagent = dbcomp.details['reagent']
        self.elute_pressure = dbcomp.details['elutepressure']
        # Set a thread
        self.thread = EluteF18Thread()

class EluteF18Thread(ComponentThread):
    '''
    Main Elute F18 Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self):
        super(EluteF18Thread, self).__init__()
