#!/usr/env python
""" The system model is the highest level
of abstraction of the system.  Everything should only
access the hardware through this object.
The sub system classes such as the gripper,
gas transfer, stopcocks, reactors and reagent robots,
are also locate in this module
"""
import os
import time
from pyelixys.logs import hallog as log
from pyelixys.hal.hal import SynthesizerHAL
from pyelixys.hal.systemobject import SystemObject

from pyelixys.hal.f18 import F18
from pyelixys.hal.reactor import Reactor
from pyelixys.hal.reagentrobot import ReagentRobot
from pyelixys.hal.pressureregulator import PressureRegulator
from pyelixys.hal.coolantpump import CoolantPump


class System(SystemObject):
    """ The system object is an abstraction of the
    elixys hardware and organizes the method calls
    and status information so that a user can directly
    access the hardware according to the physical
    mechanisms on the synthesize, i.e. Reactors,
    Gas Transfer, Gripper, Reagent Delivery, and etc.
    """
    def __init__(self):
        """ Construct the System Object """

        # Initialize the hw api
        synthesizer = SynthesizerHAL()

        # Should we start the simulator?
        # Call the constructor
        super(System, self).__init__(synthesizer)

        # Read Reactor configs and create reactors
        reactors_conf = self.sysconf['Reactors']
        self.reactors = []
        for reactor_section in reactors_conf.sections:
            reactor_id = reactors_conf[reactor_section]['id']
            self.reactors.append(Reactor(reactor_id, synthesizer))

        # Create a reagent delivery robot
        self.reagent_robot = ReagentRobot(synthesizer)

        # Give top level system object access to F18 valve
        self.f18 = F18(synthesizer)

        pressreg_config = self.sysconf['PressureRegulators']
        self.pressure_regulators = []
        for pressreg_sec in pressreg_config.sections:
            pressreg_id = pressreg_config[pressreg_sec]['id']
            self.pressure_regulators.append(
                    PressureRegulator(pressreg_id, synthesizer))

        self.coolant_pump = CoolantPump(synthesizer)

        if self.sysconf['Simulator']['synthesizer']:
            log.info("Starting the HW Simulator")
            self.start_simulator()

    def start_simulator(self):
        """ Run the simulator """

        from pyelixys.hal.tests.testelixyshw import \
                start_simulator_thread
        # If not windows wait you websocketserver to start
        #  before starting the simulator
        if not os.name == 'nt':
            time.sleep(2.0)
        self.simulator, self.simthread = \
                start_simulator_thread()


    def initialize(self):
        """ Initialize the robot """
        self.reagent_robot.home()
        for r in self.reactors:
            r.initialize()

        for r in self.reactors:
            r.move_install()
            r.lift_no_check()

        self.reagent_robot.move_install(0)

    def install_cassette(self, reactorid):
        """ Initialize the robot and then move to an install position """
        self.initialize()
        self.reagent_robot.move_install(reactorid)

if __name__ == '__main__':
    s = System()
    from IPython import embed
    embed()
