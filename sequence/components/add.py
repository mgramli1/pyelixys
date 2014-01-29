#!/usr/bin/env python
""" Add Component
"""
from pyelixys.sequence.components.component import Component
# import the component threading module
from componentthread import ComponentThread

class Add(Component):
    """ Add """
    def __init__(self, dbcomp):

        super(Add, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.reagent_id = dbcomp.details['reagent']
        self.reactor = dbcomp.details['reactor']
        self.delivery_time = dbcomp.details['deliverytime']
        self.delivery_position = dbcomp.details['deliveryposition']
        self.delivery_pressure = dbcomp.details['deliverypressure']
        self.validation_error = dbcomp.details['validationerror']
        self.note = dbcomp.details['note']
        
        # Set a thread
        self.thread = AddThread()

class AddThread(ComponentThread):
    '''
    Main Add Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self):
        super(AddThread, self).__init__()
