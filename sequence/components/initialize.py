#!/usr/bin/env python
""" Initialize Component
"""
from pyelixys.sequence.components.component import Component

class Initialize(Component):
    """ Initialize"""
    def __init__(self, dbcomp):
        super(Initialize, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.validation_error = dbcomp.details['validationerror']
