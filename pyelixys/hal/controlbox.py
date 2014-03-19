#!/usr/bin/env python
""" The ControlBoxSystem communicates with the
ControlBox Actuation board hardware over a virtual serial
port.  The COM port setting are imported from the
hwconf.  It allows the system to drive 2 SSR, 2 10V DACs,
and read 2 ADCs.
"""
import os
import time
import math
import re
import serial
from serial import SerialException
from pyelixys.hal.elixysobject import ElixysObject
from pyelixys.logs import hallog as log
from pyelixys.elixysexceptions import ElixysComportError, \
                                      ElixysCBoxError, \
                                      ElixysPneumaticError


class ControlBoxSystem(ElixysObject):
    """ The ControlBoxStatus gives access to the features of
    the control box board, these include two solid state relays,
    normally one of which would be used to control the cooling system
    pump, two 10V DACs for setting the setpoints on the  and 2 ADCs
    for reading the current pressure from the pressure regulators.
    Additonally it is possible to set the LED Ring.
    """
    def __init__(self):
        super(ControlBoxSystem, self).__init__()
        self.conf = self.sysconf['ControlBox']
        if os.name == 'nt':
            self._port = self.conf['win_port']
        elif os.name == 'posix':
            self._port = self.conf['posix_port']
        else:
            raise ElixysComportError("Could not "
                    "determine platform for port")
        self._baud = self.conf['baud']

        if self.sysconf['Simulator']['controlbox']:
            log.debug("Loading the control box simulator")
            from pyelixys.hal.tests.testcontrolbox import CBoxSim
            self.serial = CBoxSim()
            return

        try:
            self.serial = serial.Serial(port=self._port,
                                    baudrate=self._baud,
                                    timeout=0.2)
	    if os.name == 'posix':
		self.serial.close()
		self.serial.baudrate = 115200
                self.serial.baudrate = self._baud
		self.serial.open()
		self.serial.baudrate = 115200
		self.serial.baudrate = self._baud
        except SerialException:
            log.error("Failed to open comport %s", self._port)
            raise ElixysComportError("Serial COM port not available at %s."
                                    "Ensure CBox Board is connected and "
                                    "user has permission to"
                                    "access device" % self._port)

        self._leds = 0

    def get_adcs(self):
        """ Query the CBox board for the ADC values
        convert them to integers, then multiple by the
        conversion factors in the hwconf.
        """
        self.clear_in_serial_buffer()
        tmpstr = "/ADC/run\n"
        self.write(tmpstr)
        resp = self.read()
        log.debug("Get ADCS: %s" , resp)
        regex = re.compile("(?:[ADC])+ "
                       "(?P<adc0>[0-9A-Fa-f]*), "
                       "(?P<adc1>[0-9A-Fa-f]*)")
        mtch = regex.match(resp)
        adcval0 = (int(mtch.group('adc0'), 16) - self.conf['ADCOFFSET0']) * \
			self.conf['ADCCONST0']
        adcval1 = (int(mtch.group('adc1'), 16) - self.conf['ADCOFFSET1']) * \
			self.conf['ADCCONST1']
        log.debug("ADC0 = %s", adcval0)
        return adcval0, adcval1

    def get_adc0(self):
        """ Return ADC0 value """
        return self.get_adcs()[0]

    def get_adc1(self):
        """ Return ADC1 Value """
        return self.get_adcs()[1]

    adc0 = property(get_adc0)
    adc1 = property(get_adc1)


    def get_dacs(self):
        """ Query the CBox board for the current DAC values
        convert them to integers, then multiple by the
        conversion factors in the hwconf.
        """
        self.clear_in_serial_buffer()
        tmpstr = "/DAC/run\n"
        self.write(tmpstr)
        resp = self.read()
        regex = re.compile("(?:[DAC])+ "
                       "(?P<dac0>[0-9A-Fa-f]*), "
                       "(?P<dac1>[0-9A-Fa-f]*)")
        mtch = regex.match(resp)
        dacval0 = int(mtch.group('dac0'), 16) * self.conf['DACCONST0']
        dacval1 = int(mtch.group('dac1'), 16) * self.conf['DACCONST1']
        return dacval0, dacval1

    def get_dac0(self):
        """ Get DAC0 value """
        return self.get_dacs()[0]

    def get_dac1(self):
        """ Get DAC1 value """
        return self.get_dacs()[1]

    def set_dac(self, devid, value):
        """ Set the DAC0 output"""
        tmpstr = "/DAC/run %d %x\n"
        if devid == 0:
            val = value / self.conf['DACCONST0']
        elif devid == 1:
            val = value / self.conf['DACCONST1']
        else:
            raise ElixysCBoxError("Unexpected DAC device id")

        val = int(math.ceil(val))
        dacmax = self.conf['DACMAX']
        if val > dacmax:
            log.warn("Attempt to set DAC %d to "
                    "%d, setting to MAX %d", devid, val, dacmax)
            val = dacmax

        dacmin = self.conf['DACMIN']
        if val < dacmin:
            log.warn("Attempt to set DAC %d to "
                    "%d, setting to MIN %d", devid, val, dacmin)

        tmpstr = tmpstr % (devid, val)
        log.debug("Set DAC: sent %s", tmpstr)
        self.write(tmpstr)
        self.read()

    def set_dac0(self, value):
        """ Set DAC0 value """
        self.set_dac(0, value)

    def set_dac1(self, value):
        """ Set DAC1 value """
        self.set_dac(1, value)

    dac0 = property(get_dac0, set_dac0)
    """ Return or set value of DAC0 """
    dac1 = property(get_dac1, set_dac1)
    """ Return or set value of DAC1 """

    def get_ssr(self):
        """ Return the state of the solid state relays """
        self.clear_in_serial_buffer()
        tmpstr = "/SSR/run\n"
        self.write(tmpstr)
        resp = self.read()
        regex = re.compile("(?:[SSR])+ "
                       "(?P<ssr0>[0-9A-Fa-f]*), "
                       "(?P<ssr1>[0-9A-Fa-f]*)")

        print "READ:" + resp
        mtch = regex.match(resp)
        ssr0 = bool(int(mtch.group('ssr0')))
        ssr1 = bool(int(mtch.group('ssr1')))
        return ssr0, ssr1


    def get_ssr0(self):
        """ Return SSR state 0 """
        return self.get_ssr()[0]

    def get_ssr1(self):
        """ Return SSR state 1 """
        return self.get_ssr()[1]

    def set_ssr(self, devid, value):
        """ Set SSR state """
        tmpstr = "/SSR/run %d %d\n"

        if value is True:
            value = 1
        elif value is False:
            value = 0
        else:
            log.warn("Invalid SSR %d set value=%s", devid, value)
            return

        tmpstr = tmpstr % (devid, value)
        print tmpstr
        self.write(tmpstr)
        self.read()

    def set_ssr0(self, value):
        """ Set SSR state 0 """
        self.set_ssr(0, value)

    def set_ssr1(self, value):
        """ Set SSR state 1 """
        self.set_ssr(1, value)

    ssr0 = property(get_ssr0, set_ssr0)
    """ Return or set the value of the SSR 0 """
    ssr1 = property(get_ssr1, set_ssr1)
    """ Return or set the value of the SSR 1 """

    def set_leds(self, value):
        """ Set the LED Ring """
        tmpstr = "/LEDS/run %X\n"
        if not value < 2**24 and value > 0:
            log.warn("Invalid LEDs value=%d", value)
            return

        self.write(tmpstr % value)
        self.read()
        self._leds = value

    def get_leds(self):
        """ Return LED state """
        return self._leds

    leds = property(get_leds, set_leds)
    """ Return or set the value of the LEDs on the
    Controlbox board """

    def reconnect(self):
        """ Attempt to reconnect the elixys control box """

        time.sleep(0.5)

        try:
            self.serial.close()
        except SerialException:
            raise ElixysComportError("Could not close CBox connection")

        try:
            self.serial.open()
        except SerialException:
            raise ElixysComportError("Could not reopen CBox connection")

        try:
            self.serial.flushInput()
        except SerialException:
            raise ElixysComportError("Failed to flush CBox input buffer")

    def clear_in_serial_buffer(self):
        """ Check the serial buffer and make sure it is clear """
        try:
            if self.serial.inWaiting():
                resp = self.serial.readall()
                log.warn("Unknown/unparsed serial response: %s", resp)
        except SerialException:
            self.reconnect()

    def write(self, msg, retry=2):
        """ This will replace the serial write.
        This should make sure the comport is open
        and available.  It NOT retry to open!
        If we can't open raise exception.
        """
        for idx in range(retry):
            try:
                self.serial.write(msg)
                return
            except SerialException:
                log.error("CBox Com error, retry %d", idx)
                self.reconnect()

        raise ElixysComportError("Failed to write to CBox, %d retries" % retry)

    def read(self, retry=2):
        """ This will replace the serial read.
        Make sure comport is avialable. If so
        read! Else try to open.  If can't open
        raise exception.
        """
        for idx in range(retry):
            try:
                resp = self.serial.readline()
                return resp
            except SerialException:
                log.error("CBox Com error, retry %d", idx)
                self.reconnect()

        raise ElixysComportError("Failed to read from CBox, %d retries" % retry)


cbox = ControlBoxSystem()

if __name__ == '__main__':

    from IPython import embed
    embed()
