#!/usr/env python
""" The system model is the highest level
of abstraction of the system.  Everything should only
access the hardware through this object.
The sub system classes such as the gripper,
gas transfer, stopcocks, reactors and reagent robots,
are also locate in this module
"""
import time
import time
from pyelixys.logs import hallog as log
from pyelixys.hal.systemobject import SystemObject
from pyelixys.hal.gripper import Gripper
from pyelixys.hal.gastransfer import GasTransfer
from pyelixys.hal.linearaxis import LinearAxis


class ReagentRobot(SystemObject):
    """ The Elixys Reagent Robot allows the user to
    select reagents using the gripper and gas transfer.
    An X-Y table allows the selection of positions.
    """
    def __init__(self, synthesizer):
        super(ReagentRobot, self).__init__(synthesizer)

        # Create the Gas Transfer
        self.gas_transfer = GasTransfer(synthesizer)

        # Create Gripper
        self.gripper = Gripper(synthesizer)

        self._xactuator_id = \
                self.conf['xaxis_actuator_id']
        self._yactuator_id = \
                self.conf['yaxis_actuator_id']

        self.xactuator = LinearAxis(self._xactuator_id,
                                    synthesizer)
        self.yactuator = LinearAxis(self._yactuator_id,
                                    synthesizer)

    def _get_conf(self):
        return self.sysconf['ReagentRobot']

    conf = property(_get_conf)
