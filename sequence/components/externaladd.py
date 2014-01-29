#!/usr/bin/env python
""" External Add Component
"""
from pyelixys.sequence.components.component import Component

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

