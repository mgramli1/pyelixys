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
        super(PressureRegulator, self).__init__(synthesizer)

        self.id_ = devid

    def _get_conf(self):
        self.press_conf = self.sysconf['PressureRegulators']
        return self.press_conf['PressureRegulator%d' % self.id_]

    conf = property(_get_conf)
