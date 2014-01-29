#!/usr/bin/env python
""" Cassette Component
"""
from pyelixys.sequence.components.component import Component
# import the component threading module
from componentthread import ComponentThread

class Cassette(Component):
    """ Cassette """
    def __init__(self, dbcomp):
        super(Cassette, self).__init__(dbcomp)
        # Set a thread
        self.thread = CassetteThread()

class CassetteThread(ComponentThread):
    '''
    Main Add Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self):
        super(CassetteThread, self).__init__()
