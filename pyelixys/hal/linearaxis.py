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
    ISGWSTARTSET = False

    def __init__(self, devid, synthesizer):
        super(LinearAxis, self).__init__(synthesizer)
        self.id_ = devid
        self.actuator = synthesizer.linear_axis[self.id_]

        if not self.ISGWSTARTSET:
            self.gwstart()
            self.ISGWSTARTSET = True

        self.reset()
        self.home()

    def gwstart(self):
        self.actuator.gateway_start()

    def start(self):
        self.actuator.start()

    def home(self):
        self.actuator.turn_on()
        self.actuator.home()

    def pause(self):
        self.actuator.pause()

    def turn_on(self):
        self.actuator.turn_on()

    def brake_release(self):
        self.actuator.brake_release()

    def reset(self):
        self.actuator.reset()

    def set_position(self, posmm):
        self.actuator.set_position(posmm)

    def move(self, posmm):
        self.turn_on()
        self.set_position(posmm)
        self.start()

