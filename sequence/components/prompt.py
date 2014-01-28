#!/usr/bin/env python
""" Prompt Component
"""
from pyelixys.sequence.components.component import Component

class Prompt(Component):
    """ Prompt """
    def __init__(self, dbcomp):
        super(Prompt, self).__init__(dbcomp)
