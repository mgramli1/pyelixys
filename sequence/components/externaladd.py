#!/usr/bin/env python
""" External Add Component
"""
from pyelixys.sequence.components.component import Component

class ExternalAdd(Component):
    """ External Add """
    def __init__(self, dbcomp):
        super(ExternalAdd, self).__init__(dbcomp)
