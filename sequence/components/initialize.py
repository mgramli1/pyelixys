#!/usr/bin/env python
""" Initialize Component
"""
from pyelixys.sequence.components.component import Component

class Initialize(Component):
    """ Initialize"""
    def __init__(self, dbcomp):
        super(Initialize, self).__init__(dbcomp)
