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

from threading import Thread

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

    def _get_conf(self):
        """ Return the config this pressure regulator """
        self.press_conf = self.sysconf['PressureRegulators']
        self.allowable_pressure_diff = (
                self.press_conf
                ['PressureRegulator' + str(self.id_)]
                ['allowable_pressure'])
        self.allowable_delay = timedelta(
                0,
                self.press_conf
                ['PressureRegulator' + str(self.id_)]
                ['allowable_delay'])

        return self.press_conf['PressureRegulator%d' % self.id_]
    
    def set_setpoint(self, value):
        """ Set the pressure regulator,
        setpoint is generally in psi, but really
        depends on the hw configuration """
        
        
        value = value * self.conf['PSICONV']
        log.debug("Set pressure regulator %d to %f", self.id_, value)
        self.synth.cbox.set_dac(self.id_, value) 
        return

        log.debug("Checking for pressure to equal setpoint")
        # Loop until the pressure reaches the setpoint
        begintime = datetime.now()
        is_pressure_reached = False
        while (self.allowable_delay > datetime.now() - begintime
                and not is_pressure_reached):
            if (self.allowable_pressure_diff <= self.get_pressure()
                    and self.get_pressure() <= self.get_pressure()):
                is_pressure_reached = True
        if is_pressure_reached:
            log.debug("Sucessfully set pressure: %s", self.get_setpoint())
        else:
            log.debug("Unable to set pressure to %s", self.get_setpoint())


    def get_setpoint(self):
        """ Get the pressure regulator
        setpoint, i.e. the pressure it is suppose to get to
        """
        value = self.synth.cbox.get_dacs()[self.id_]
        value = value / self.conf['PSICONV']
        log.debug("Current setpoint on regulator %d = %f",
                self.id_, value)
        return value

    setpoint = property(get_setpoint, set_setpoint)
    
    def set_pressure(self, value):
        '''
        Set the pressure regulator pressure by
        setting the setpoint and confirming the
        actual pressure reaches the setpoint.
        '''
        # Slowly increment the pressure to
        # simulate the increase of pressure
        # until we reach it or timeout
        increment_value = value/10
        begintime = datetime.now()
        is_pressure_reached = False
        while (self.allowable_delay > datetime.now() - begintime
                and not is_pressure_reached):
            self.set_setpoint(increment_value)
            if (self.allowable_pressure_diff <= self.get_pressure()
                    and self.get_pressure() <= self.get_pressure()):
                is_pressure_reached = True
        
        
        if is_pressure_reached:
            log.debug("Sucessfully set pressure: %s", self.get_setpoint())
        else:
            log.debug("Unable to set pressure to %s", self.get_setpoint())

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

    #: Pressure regualtor config
    conf = property(_get_conf)
