#!/usr/bin/env python
""" Elute F18 Component
"""
from pyelixys.sequence.components.component import Component

class EluteF18(Component):
    """ Elute F18 """
    def __init__(self, dbcomp):
        super(EluteF18, self).__init__(dbcomp)
