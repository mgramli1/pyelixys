#!/usr/bin/env python
""" Transfer Component
"""
from pyelixys.sequence.components.component import Component

class Transfer(Component):
    """ Transfer """
    def __init__(self, dbcomp):
        super(Transfer, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.mode = dbcomp.details['mode']
        self.pressure = dbcomp.details['pressure']
        self.duration = dbcomp.details['duration']
        self.soure_reactor = dbcomp.details['sourcereactor']
        self.target_reactor = dbcomp.details['targetreactor']
        self.validation_error = dbcomp.details['validationerror']
        self.note = dbcomp.details['note']

