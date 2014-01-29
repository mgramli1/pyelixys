#!/usr/bin/env python
""" Mix Component
"""
from pyelixys.sequence.components.component import Component

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

