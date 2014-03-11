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
from pyelixys.hal.pressureregulator import PressureRegulator
from pyelixys.elixysexceptions import ElixysReagentRobotError,\
                                      ElixysGripperError,\
                                      ElixysGasTransferError


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

        pressreg_config = self.sysconf['PressureRegulators']
        self.pressure_regulators = []
        for pressreg_sec in pressreg_config.sections:
            pressreg_id = pressreg_config[pressreg_sec]['id']
            self.pressure_regulators.append(
                    PressureRegulator(pressreg_id, synthesizer))


    
    def _get_conf(self):
        return self.sysconf['ReagentRobot']

    conf = property(_get_conf)


    def get_reagent_position(self, reactorid, reagentid):
        """ Look up reagent position in config file """
        return self.conf['Positions']["Reactor%d" % reactorid]["reagent%d" % reagentid]

    def move_coord(self, x, y):
        """ Move to x, y coordinates """

        log.debug("Move Reagent Robot to %d, %d", x, y)
        self.prepare_move()
        self.xactuator.move(x)
        self.yactuator.move(y)
        self.yactuator.wait()
        self.xactuator.wait()

    def prepare_move(self):
        self.pressure_regulators[1].setpoint = self.conf['min_pneumatic_pressure']

        self.gripper.lift()
        self.gas_transfer.lift()

        if not self.gas_transfer.is_up:
            raise ElixysGasTransferError

        if not self.gripper.is_up:
            raise ElixysGripperError

    def home(self):
        self.prepare_move()

        self.xactuator.gwstart()
        self.xactuator.reset()
        self.yactuator.reset()
        self.xactuator.home()
        self.yactuator.home()


    def move_reagent_position(self, reactorid, reagentid):
        pos = self.get_reagent_position(reactorid, reagentid)
        self.move_coord(*pos)

    def move_elute(self, reactorid):
        pos = self.conf['Positions']['Reactor%d' % reactorid]['elute']
        self.move_coord(*pos)

    def move_evaporate(self, reactorid):
        pos = self.conf['Positions']['Reactor%d' % reactorid]['evaporate']
        self.move_coord(*pos)

    def move_add(self, reactorid, addpos):
        pos = self.conf['Positions']['Reactor%d' % reactorid]['add%d' % addpos]
        self.move_coord(*pos)

    def move_add0(self,reactorid):
        self.move_add(reactorid, 0)

    def move_add1(self,reactorid):
        self.move_add(reactorid, 1)

    def move_transfer(self, reactorid):
        pos = self.conf['Positions']['Reactor%d' % reactorid]['transfer']
        self.move_coord(*pos)

    def move_install(self, reactorid):
        pos = self.conf['Positions']['Reactor%d' % reactorid]['install']
        self.move_coord(*pos)

    def brake_release(self):
        self.xactuator.brake_release()
        self.yactuator.brake_release()

    def get_position(self):
        return self.xactuator.actuator.position, \
                self.yactuator.actuator.position

    position = property(get_position)

    def grab_reagent(self, reactorid, reagentid):
        self.move_reagent_position(reactorid, reagentid)
        self.gripper.open()
        self.gripper.lower()
        self.gripper.close()
        time.sleep(0.5)
        self.gripper.lift()

    def return_reagent(self, reactorid, reagentid):
        self.gripper.lift()
        self.gas_transfer.lift()
        self.move_reagent_position(reactorid, reagentid)
        self.gripper.lower()
        self.gripper.open()
        self.gripper.lift()

    def drop_add(self, reactorid, addid):
        self.gripper.close()
        self.move_add(reactorid, addid)
        self.gripper.lower()
        self.gas_transfer.lower()

    def prepare_add_reagent(self,reactorid, reagentid, addid):
        self.gas_transfer.stop_transfer()
        self.grab_reagent(reactorid, reagentid)
        self.drop_add(reagentid, addid)

    
