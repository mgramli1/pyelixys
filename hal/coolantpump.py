#!/usr/bin/env python
""" Coolant Pump is controlled by a
solid state relay on the control box.
The CoolantPump give access to this SSR
and allows it to be turned on and off.
"""
import time

from pyelixys.logs import hallog as log
from pyelixys.hal.systemobject import SystemObject


class CoolantPump(SystemObject):
    """ The CoolantPump is used to
    turn the coolant pump off and on
    """

    def __init__(self, synthesizer):
        """ (Constructor) """
        super(CoolantPump, self).__init__(synthesizer)

        self.id_ = self.conf['id']

    def _get_conf(self):
        """ Return the Coolant pump config """
        return self.sysconf['CoolantPump']

    conf = property(_get_conf)

    def turn_on_off(self, value):
        """ Set the state of the SSR """
        log.debug("Set coolant pump on = %s", value)
        self.synth.cbox.set_ssr(self.id_, value)

    def get_on_off(self):
        """ Get the state of the pump ssr """
        value = self.synth.cbox.get_ssr()[self.id_]
        log.debug("Coolant pump is on = %s", value)
        return value

    on = property(get_on_off,turn_on_off)

