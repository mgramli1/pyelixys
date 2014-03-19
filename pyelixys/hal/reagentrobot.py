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
        """ Construct a reagent robot """
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
        """ Prepare the reagent robot to move
        by setting the pressure for the pneumatic's regualtor
        and lifting both the gas transfer tool and the
        gripper tool """
        self.pressure_regulators[1].setpoint = self.conf['min_pneumatic_pressure']

        self.gripper.lift()
        self.gas_transfer.lift()

        if not self.gas_transfer.is_up:
            raise ElixysGasTransferError

        if not self.gripper.is_up:
            raise ElixysGripperError

    def home(self):
        """ Home the reagent robot """
        self.prepare_move()
        self.xactuator.gwstart()
        self.xactuator.reset()
        self.yactuator.reset()
        self.xactuator.home()
        self.yactuator.home()


    def move_reagent_position(self, reactorid, reagentid):
        """ Move to the specified reagent position """
        pos = self.get_reagent_position(reactorid, reagentid)
        self.move_coord(*pos)

    def move_elute(self, reactorid):
        """ Move to the specified elute position """
        pos = self.conf['Positions']['Reactor%d' % reactorid]['elute']
        self.move_coord(*pos)

    def move_evaporate(self, reactorid):
        """ Move to the specified evaporate
        position """
        pos = self.conf['Positions']['Reactor%d' % reactorid]['evaporate']
        self.move_coord(*pos)

    def move_add(self, reactorid, addpos):
        """ Move to the specified add position on
        the reactor given by the reactor id """
        pos = self.conf['Positions']['Reactor%d' % reactorid]['add%d' % addpos]
        self.move_coord(*pos)

    def move_add0(self,reactorid):
        """ Move to the specified add0 position on
        the reactor given by the reactor id """
        self.move_add(reactorid, 0)

    def move_add1(self,reactorid):
        """ Move to the specified add1 position on
        the reactor given by the reactor id """
        self.move_add(reactorid, 1)

    def move_transfer(self, reactorid):
        """ Move to the transfer position on the
        specified reactor """
        pos = self.conf['Positions']['Reactor%d' % reactorid]['transfer']
        self.move_coord(*pos)

    def move_install(self, reactorid):
        """ Move to the install postion on the
        specified reator"""
        pos = self.conf['Positions']['Reactor%d' % reactorid]['install']
        self.move_coord(*pos)

    def brake_release(self):
        """ Release the reagent robot brakes
        on both actuators """
        self.xactuator.brake_release()
        self.yactuator.brake_release()

    def get_position(self):
        """ Get the x,y coordinates of the reagent
        robot in millimeters """
        return self.xactuator.actuator.position, \
                self.yactuator.actuator.position

    position = property(get_position,
            doc="Return the current x,y postion of the"
            " reagent robot in millimeters")

    def grab_reagent(self, reactorid, reagentid):
        """ Pick up a specified reagent """
        self.move_reagent_position(reactorid, reagentid)
        self.gripper.open()
        self.gripper.lower()
        self.gripper.close()
        time.sleep(0.5)
        self.gripper.lift()

    def return_reagent(self, reactorid, reagentid):
        """ Return the reagent to its the
        specified reagent position """
        self.gripper.lift()
        self.gas_transfer.lift()
        self.move_reagent_position(reactorid, reagentid)
        self.gripper.lower()
        self.gripper.open()
        self.gripper.lift()

    def drop_add(self, reactorid, addid):
        """ Drop the reagent in to the specified add postion """
        self.gripper.close()
        self.move_add(reactorid, addid)
        self.gripper.lower()
        self.gas_transfer.lower()

    def drop_add0(self, reactorid):
        """ Drop the reagent into add position 2 """
        self.drop_add(reactorid, 0)

    def drop_add1(self, reactorid):
        """ Drop the reagent into add position 1 """
        self.drop_add(reactorid, 1)

    def prepare_add_reagent(self,reactorid, reagentid, addid):
        """ Prepare to add the reagent by grabbing the
        specified reagent and dropping it at the correct
        position """
        self.gas_transfer.stop_transfer()
        self.grab_reagent(reactorid, reagentid)
        self.drop_add(reagentid, addid)

    def drop_elute(self, reactorid):
        """ Drop the vial in the elute position,
        for a given reactor id """
        self.gripper.close()
        self.move_elute(reactorid)
        self.gripper.lower()
        self.gas_transfer.lower()

    def prepare_transfer(self, reactorid):
        """ Prepare to transfer by moving to
        transfer and lowering the gas_transfer tool"""
        self.move_transfer(reactorid)
        self.gas_transfer.lower()


