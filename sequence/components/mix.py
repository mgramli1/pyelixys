#!/usr/bin/env python
""" Mix Component
"""
from pyelixys.sequence.components.component import Component

class Mix(Component):
    """ Mix """
    def __init__(self, dbcomp):
        super(Mix, self).__init__(dbcomp)
