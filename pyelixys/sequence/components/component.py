#!/usr/bin/env python
""" Component Base Class
"""

#TODO from pyelixys.logs import seqlog as log
# import the HAL
#TODO from pyelixys.hal.system import system

class Component(object):
    """ Base Component Class """
    system = None
    log = None
    #system = system
    #log = log

    def __init__(self, dbcomp):
        self.dbcomp = dbcomp
        
    def run(self):
        """ Run this component thread!
        If we have one?"""
        pass
