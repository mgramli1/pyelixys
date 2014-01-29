#!/usr/bin/env python
""" Install Component
"""
from pyelixys.sequence.components.component import Component

class Install(Component):
    """ Install """
    def __init__(self, dbcomp):
        super(Install, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.message = dbcomp.details['message']
        self.reactor = dbcomp.details['reactor']
        self.validationerror = dbcomp.details['validationerror']
        self.note = dbcomp.details['note']

