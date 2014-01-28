#!/usr/bin/env python
""" Trap F18 Component
"""
from pyelixys.sequence.components.component import Component

class TrapF18(Component):
    """ Trap F18 """
    def __init__(self, dbcomp):
        super(TrapF18, self).__init__(dbcomp)
