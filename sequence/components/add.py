#!/usr/bin/env python
""" Add Component
"""
from pyelixys.sequence.components.component import Component

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
        
