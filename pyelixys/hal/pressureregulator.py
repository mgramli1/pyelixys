#!/usr/bin/env python
""" The pressure regulators in elixys allow
the pneumatic driving pressure and the gas transfer
pressure to be set. They access the controlbox
actuation board, which has 2 10V, 12-bit DACs
and 2 12-bit ADCs.  The DAC output voltages,
are used to set the pressures, while the ADCs
are used to read the pressures.  The information
from the ADCs can be used to determine if right
pressure it obtained for continuing.
"""
import time
from datetime import datetime
from datetime import timedelta

import math

from threading import Thread
import numpy as np

from pyelixys.logs import hallog as log
from pyelixys.hal.systemobject import SystemObject
from pyelixys.elixysexceptions import ElixysPneumaticError, \
                                      ElixysGasTransferError

class PressureRegulator(SystemObject):
    """ The PressureRegulator can be used to
    set the pressure for the pneumatic pressure line
    and the gas transfer lines. Elixys has two pressure
    regulators located in the ControlBox outside the cell.
    Setting of the pressures is done using the controlbox
    actuatution board, which unlike the synthesizer board
    uses a virtual serial port over USB for driving values.
    """

    def __init__(self, devid, synthesizer):
        """ (Construct) """
        self.id_ = devid

        super(PressureRegulator, self).__init__(synthesizer)
        self.allowable_pressure_diff = (
                self.conf['allowable_pressure_diff'])
        self.allowable_delay = timedelta(
                0, self.conf['allowable_delay'])
        self.setpoint = 0

    def _get_conf(self):
        """ Return the config this pressure regulator """
        self.press_conf = self.sysconf['PressureRegulators']

        return self.press_conf['PressureRegulator%d' % self.id_]

    def set_setpoint(self, value):
        """ Set the pressure regulator,
        setpoint is generally in psi, but really
        depends on the hw configuration """


        value = value * self.conf['PSICONV']
        log.debug("Set pressure regulator %d to %f", self.id_, value)
        self.synth.cbox.set_dac(self.id_, value)

        log.debug("Checking for pressure to equal setpoint")
        # Loop until the pressure reaches the setpoint
        begintime = datetime.now()
        while (self.allowable_delay > datetime.now() - begintime):
            if (self.is_at_pressure):
                log.debug("Sucessfully set pressure: %s", self.get_setpoint())
                return

        log.debug("Unable to set pressure to %s", self.get_setpoint())
        raise ElixysPressureError("Could not set pressure"\
                                "for regulator %d", self.id_)


    def get_setpoint(self):
        """ Get the pressure regulator
        setpoint, i.e. the pressure it is suppose to get to
        """
        value = self.synth.cbox.get_dacs()[self.id_]
        value = value / self.conf['PSICONV']
        log.debug("Current setpoint on regulator %d = %f",
                self.id_, value)
        return value

    setpoint = property(get_setpoint, set_setpoint,
            doc="Get or set the pressure setpoint")

    def set_pressure(self, value, duration=5.0, timestep=0.5):
        '''
        Set the pressure regulator pressure by
        setting the setpoint and confirming the
        actual pressure reaches the setpoint.
        '''
        # Slowly increment the pressure to
        # simulate the increase of pressure
        # until we reach it or timeout
        self.setpoint = 0.0
        current_pressure = self.pressure
        num_steps = duration / timestep
        press_diff = value - current_pressure
        increment_value = press_diff/num_steps
        # Always use floats else is truncates
        pressures = np.arange(current_pressure,
                value,
                increment_value)
        for press in pressures:
            self.set_setpoint(press)
            time.sleep(timestep)

        self.set_setpoint(value)


    def get_pressure(self):
        """ Return the actual pressure in PSI,
        or something else depending on hwconf.ini
        """
        value = self.synth.cbox.get_adcs()[self.id_]
        value = value / self.conf['PSICONV']
        log.debug("Current pressure on regulator %d = %f",
                self.id_, value)
        return value

    pressure = property(get_pressure, set_pressure)

    def get_at_pressure(self):
        diff = math.fabs(self.pressure - self.setpoint)
        return diff <= self.allowable_pressure_diff

    is_at_pressure = property(get_at_pressure)

    #: Pressure regualtor config
    conf = property(_get_conf)
