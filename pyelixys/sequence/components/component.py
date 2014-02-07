#!/usr/bin/env python
""" Component Base Class
"""

# import the HAL
from pyelixys.logs import seqlog as log
from pyelixys.hal.elixyssys import system

class Component(object):
    """ Base Component Class
        The component_status attribute is
        a string that shall represent the
        status of the component during a run()
        execution. The attribute shall be a
        property and set log messages with
        the same string.
    """
    system = system
    log = log

    def __init__(self, dbcomp):
        self.dbcomp = dbcomp
        self.status = ""

    def run(self):
        """ Run this component thread!
        If we have one?"""
        pass

    def get_component_status(self):
        '''Returns the status of the component'''
        return self.status

    def set_component_status(
            self,
            new_component_status):
        '''
        Takes in a new component status
        and an optional level for the
        logger. When the status is updated/set,
        the logger should log the status as well.
        '''
        log.debug(str(new_component_status))
        self.status = new_component_status

    component_status = property(
            get_component_status,
            set_component_status)

