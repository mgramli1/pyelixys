#!/usr/bin/env python
""" Move Component
"""
from pyelixys.sequence.components.component import Component

class Move(Component):
    """ Move """
    def __init__(self, dbcomp):
        super(Move, self).__init__(dbcomp)
