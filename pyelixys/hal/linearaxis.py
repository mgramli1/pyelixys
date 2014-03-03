#!/usr/bin/env python
""" A linear axis controls the position of the IAI
linear actuators conncected to the Robonet controller.
The current elixys system has 5 of these axis.
Eache reactor, and each axis of the
X-Y reagent delivery robot.
"""
import time
from datetime import timedelta
from datetime import datetime

from pyelixys.logs import hallog as log
from pyelixys.hal.systemobject import SystemObject
from pyelixys.elixysexceptions import ElixysLinactError

class LinearAxis(SystemObject):
    """ The LinearAxis class has an API,
    that allows the actuator position to be set.
    It provide axis to the current position and status.
    """

    def __init__(self, devid, synthesizer):
        super(LinearActuator, self).__init__(synthesizer)
        self.id_ = devid

    def _get_conf(self):
        """ Return the Linear Actuator configuraton """
        return self.sysconf['LinearAxis']['LinearAxis%d' % self.id_]

    conf = property(_get_conf)

    def gwstart(self):
        pass

    def home(self):
        pass

    def pause(self):
        pass

    def turn_on(self):
        pass

    def pause(self):
        pass

    def brake_release(self):
        pass

    def reset(self):
        pass

    def setPosition(self, posmm):
        pass

    def move(self, posmm):
        pass

