#!/usr/bin/env python
""" Comment Component
"""
from pyelixys.sequence.components.component import Component

class Comment(Component):
    """ Comment """
    def __init__(self, dbcomp):
        super(Comment, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.comment = dbcomp.details['comment']
        self.broadcast_flag = dbcomp.details['broadcastflag']
        self.validation_error = dbcomp.details['validationerror']
        self.note = dbcomp.details['note']
