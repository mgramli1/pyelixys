#/usr/bin/env python
""" The script can be loaded and acts like
the controlbox actuation board.
This simulator has a serial port like interface.
The controlbox board accepts commands
according to the
"""

import sys
from StringIO import StringIO
from pyelixys.logs import hwsimlog as log
from pyelixys.hal.tests.testelixyshw import e as hwsim
from pyelixys.hal.hwconf import config
from pyelixys.hal.elixysobject import ElixysObject

class CBoxSim(ElixysObject):
    """ This Serial object acts like a serial port,
    with the Controlbox on the other end.  It allows the
    user to set the dual DACs and read the Dual ADCs.
    It also allows the user to control the coolant pump
    via the SSRs """

    def __init__(self, *args, **kwargs):
        log.debug("Creating a controlbox simulator")
        self.conf = self.sysconf['ControlBox']
        self.hwsim = hwsim
        self.out_buffer = StringIO("CBOX")

        self.dacval0 = 0
        self.dacval1 = 0
        self.adcval0 = 0
        self.adcval1 = 0
        self.ssrval0 = 0
        self.ssrval1 = 0

        self.cbs = dict()
        self.cbs['DAC'] = self.cb_dac
        self.cbs['ADC'] = self.cb_adc
        self.cbs['SSR'] = self.cb_ssr

    def cb_dac(self, param):
        """ Callback for the DAC """
        #log.debug("DAC CB %s", param)
        if param is None:
            self.out_buffer = StringIO("DAC %X, %X\n"
                    % (self.dacval0, self.dacval1))
            return
        dacid = int(param[0].replace(',',''))
        dacval = int(param[1], 16)
        #log.debug("DAC id=%s", dacid)
        if dacid == 0:

            self.dacval0 = dacval
            #log.debug("Dacval0=%s",self.dacval0)

            self.adcval0 = (dacval * self.conf['DACCONST0']
                    / self.conf['ADCCONST0']
                    + self.conf['ADCOFFSET0'])

        elif dacid == 1:

            self.dacval1 = dacval
            #log.debug("Dacval1=%s", self.dacval1)
            self.adcval1 = (dacval * self.conf['DACCONST1']
                    / self.conf['ADCCONST1']
                    + self.conf['ADCOFFSET1'])

        else:
            log.error("Unknown dac id")


    def cb_adc(self, param):
        #""" Callback for the ADC """
        #log.debug("ADC CB %s", param)
        if param is None:
            self.out_buffer = StringIO("ADC %X, %X\n"
                    % (self.adcval0, self.adcval1))


    def cb_ssr(self, param):
        #""" Callback for  the SSR """
        #log.debug("SSR CB %s", param)
        if param is None:
            self.out_buffer = StringIO("SSR %d, %d\n"
                    % (self.ssrval0, self.ssrval1))
            return
        #log.debug("SSR:param=%s", param)

        devid = int(param[0])
        state = int(param[1].strip())

        if not state in (0,1):
            log.error("Invalid SSR state to CBoxSim")
            return

        if devid == 0:
            self.ssrval0 = state
        elif devid == 1:
            self.ssrval1 = state
        else:
            log.error("Invalid SSR ID to CBoxSim")


    def write(self, msg):
        """ Write message to the control box simulator """
        log.debug("CBOXSIM Command: %s" % msg)
        params = msg.split('/')
        cmd = params[1]
        param = params[2]

        param = param.split(" ")

        if len(param) == 3:
            param0 = param[1]
            param1 = param[2]
            params = (param0, param1)
        elif len(param) == 2:
            params = param[1]
        else:
            params = None

        self.cbs[cmd](params)

    def read(self):
        """ Read message from control box simulator """
        return self.out_buffer.readline()

    def close(self):
        """ Close the control box simulator """
        log.debug("Close the control box simulator")

    def open(self):
        """ Open the control box simulator """
        log.debug("Open the controlbox simulator")

    def flushInput(self):
        """ Flush in input buffer """
        log.debug("Flush the controlbox simulator input buffer")

    def inWaiting(self):
        """ Check to see if buffer has characters """
        return self.out_buffer.len - self.out_buffer.pos

    def readall(self):
        """ Read all from the CBOX read buffer """
        msg = self.out_buffer.read()
        self.out_buffer.truncate(0)
        return msg


    def readline(self):
        """ Read line from CBOX read buffer """
        return self.out_buffer.readline()

