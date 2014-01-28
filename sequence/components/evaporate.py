#!/usr/bin/env python
""" Evaporate Component
"""
from pyelixys.sequence.components.component import Component

class Evaporate(Component):
    """ Evaporate """
    def __init__(self, dbcomp):
        super(Evaporate, self).__init__(dbcomp)
