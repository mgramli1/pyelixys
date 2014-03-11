#!/usr/env python
""" The reactor model is the highest level
abstraction of the reactor.  Everything should only
access each reactor throuh this interface.
The sub systems: pneumatic actuators, linear actuators,
mixer motors, temperature controller, thermocouples, and
stopcocks, can all be accessed through this device as well.
"""
import time
from pyelixys.logs import hallog as log
from pyelixys.elixysexceptions import ElixysPneumaticError
from pyelixys.hal.systemobject import SystemObject
from pyelixys.hal.pneumaticactuator import \
        PneumaticActuator
from pyelixys.hal.pressureregulator import \
        PressureRegulator
from pyelixys.hal.linearaxis import LinearAxis
from pyelixys.hal.stopcock import Stopcock
from pyelixys.hal.tempctrl import TempCtrl
from pyelixys.hal.mixer import Mixer
from pyelixys.hal.f18 import F18
from datetime import timedelta
from datetime import datetime

class Reactor(PneumaticActuator):
    """ The Elixys System has three reactors,
    each reactor is composed of 3 stopcocks,
    a temperature controller, a linear actuator
    and a pnuematic actuator. These sub-features
    can be controller via this object.
    """
    def __init__(self, devid, synthesizer):
        # First set device id so config is valid
        self.id_ = devid

        # Initialize the pneumaticactuator and
        #  and systemobject
        super(Reactor, self).__init__(synthesizer)

        # Initialize the stopcocks
        self._stopcock_ids = self.conf['stopcock_ids']
        self.stopcocks = [Stopcock(id_, synthesizer)
                            for id_ in self._stopcock_ids]

        # Gain access to the F18 valve
        self.f18 = F18(synthesizer)

        # Initialize the temp controller
        self._temp_ctrl_ids = self.conf['tempctrl_ids']
        self.temperature_controller = \
                TempCtrl(self._temp_ctrl_ids, synthesizer)

        # Intialize Mixer
        self._mixer_id = self.conf['mixer_id']
        self.mixer = Mixer(self._mixer_id, synthesizer)

        self._actuator_id = self.conf['actuator_id']
        self.actuator = LinearAxis(self._actuator_id,
                                    synthesizer)


    def _get_conf(self):
        """ Get the reactor config for reactor with this id"""
        return self.sysconf['Reactors']['Reactor%d' % self.id_]

    conf = property(_get_conf)

    def turn_f18_transfer_on(self):
        """ Turn on F18 valve """
        self.f18.turn_on()


    def turn_f18_transfer_off(self):
        """ Turn off f18 valve """
        self.f18.turn_off()


    def get_coordinate(self, name):
        """ Read a coordinate from the config """
        return self.conf['Positions'].get(name, None)

    def brake_release(self):
        """ Release the brake """
        self.actuator.brake_release()

    def home(self):
        """ Home the reactor """
        self.actuator.reset()
        self.actuator.turn_on()
        self.actuator.home()

    def move(self, posname):
        """ Move to named position """
        self.prepare_move()
        coord = self.get_coordinate(posname)
        if not coord is None:
            self.actuator.move_and_wait(coord)
        self.brake_release()

    def move_install(self):
        """ Move to the install position """
        self.move('install')
    
    def move_transfer(self):
        """ Move to the transfer position """
        self.move('transfer')

    def move_add(self):
        """ Move to add position """
        self.move('add')

    def move_react(self, reactpos):
        """ Move to react pos """
        self.move('react%d' % reactpos)

    def move_react0(self):
        """ Move to react 0 position """
        self.move_react(0)

    def move_react1(self):
        """ Move to react 1 position """
        self.move_react(1)

    def move_evaporate(self):
        """ Move to evaporate """
        self.move('evaporate')

    def get_position(self):
        return self.actuator.actuator.position

    position = property(get_position)

    def prepare_cassette(self):
        self.lower()
        self.stopcocks[0].turn_clockwise()
        self.stopcocks[1].turn_counter_clockwise()
        self.stopcocks[2].turn_counter_clockwise()


    def prepare_move(self):
        self.prepare_air()
        self.lower()
        if not self.is_down:
            raise ElixysPneumaticError

