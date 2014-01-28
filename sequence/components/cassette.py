#!/usr/bin/env python
""" Cassette Component
"""
from pyelixys.sequence.components.component import Component

class Cassette(Component):
    """ Cassette """
    def __init__(self, dbcomp):
        super(Cassette, self).__init__(dbcomp)
