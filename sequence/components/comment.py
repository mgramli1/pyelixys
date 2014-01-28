#!/usr/bin/env python
""" Comment Component
"""
from pyelixys.sequence.components.component import Component

class Comment(Component):
    """ Comment """
    def __init__(self, dbcomp):
        super(Comment, self).__init__(dbcomp)
