#!/usr/bin/env python
""" Add Component
"""
from pyelixys.sequence.components.component import Component

class Add(Component):
    """ Add """
    def __init__(self, dbcomp):

        super(Add, self).__init__(dbcomp)
