#!/usr/bin/env python
""" Trap F18 Component
"""
from pyelixys.sequence.components.component import Component

class TrapF18(Component):
    """ Trap F18 """
    def __init__(self, dbcomp):
        super(TrapF18, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.validation_error = dbcomp.details['validationerror']
        self.cyclotron_flag = dbcomp.details['cyclotronflag']
        self.reactor = dbcomp.details['reactor']
        self.trap_pressure = dbcomp.details['trappressure']
        self.trap_time = dbcomp.details['traptime']
        self.note = dbcomp.details['note']
