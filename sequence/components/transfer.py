#!/usr/bin/env python
""" Transfer Component
"""
from pyelixys.sequence.components.component import Component

class Transfer(Component):
    """ Transfer """
    def __init__(self, dbcomp):
        super(Transfer, self).__init__(dbcomp)
