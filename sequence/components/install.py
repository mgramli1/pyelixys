#!/usr/bin/env python
""" Install Component
"""
from pyelixys.sequence.components.component import Component

class Install(Component):
    """ Install """
    def __init__(self, dbcomp):
        super(Install, self).__init__(dbcomp)
