#!/usr/bin/env python
""" Evaporate Component
"""
import time
from component import Component
# import the component threading module
from componentthread import ComponentThread

class Evaporate(Component):
    """ Evaporate """
    def __init__(self, dbcomp):
        super(Evaporate, self).__init__(dbcomp)
        details = dbcomp.details
        self.component_id = int(details['id'])
        self.sequence_id = int(details['sequenceid'])
        self.final_temperature = int(details['finaltemperature'])
        self.stop_temperature = int(details['stopattemperature'])
        self.evaporation_temperature = int(details['evaporationtemperature'])
        self.evaporation_pressure = int(details['evaporationpressure'])
        self.duration = int(details['duration'])
        self.reactor = int(details['reactor'])
        self.validation_error = bool(details['validationerror'])
        self.stir_speed = int(details['stirspeed'])
        self.note = str(details['note'])
        # Additional attributes to be used during run()
        self.start_time = None

        # Set a thread
        self.thread = EvaporateThread(self)

    def run(self):
        '''
        Executes the 'EVAPORATE'
        run thread and the Evaporate
        object is passed into the
        EvaporateThread.
        '''
        self.thread.start()

class EvaporateThread(ComponentThread):
    '''
    Main Evaporate Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self, evap):
        super(EvaporateThread, self).__init__()
        self.evaporate = evap

    def run(self):
        '''
        Begins the run process of the
        Evaporate unit operation.
        Function takes an Evaporate class object
        which shall contain the details of
        the unit op's execution.
        '''
        self._is_complete.clear()

        self.evaporate.component_status = "Starting the Evaporate run()"
        print type(self.evaporate.evaporation_pressure)
        self.evaporate.component_status= "Setting pressure regulator 1 to %f" % \
                (self.evaporate.evaporation_pressure/3)
        self.evaporate.system.pressure_regulators[0].set_pressure(
                self.evaporate.evaporation_pressure/3)
        # Set pressure regualtor 1 to 'evaporate.evaporationpressure'
        # Note: Divide pressure by 3, this is done in the old codebase

        self.evaporate.component_status = "Setting reactor %d to the " \
                "Evaporate position." \
                % self.evaporate.reactor
        # Set the Evaporate position to 'self.evaporate.reactor'

        self.evaporate.component_status = "Setting reactor %d " \
                "stir speed to %f" \
                % (self.evaporate.reactor, self.evaporate.stir_speed)
        self.evaporate.system.reactors[self.evaporate.reactor].mixer.set_duty_cycle = \
                self.evaporate.stir_speed
        # Set the Evaporate stir speed to 'self.evaporate.stir_speed'
        # Set as a percentage

        # Make sure gripper is up
        self.evaporate.component_status = "Checking if gripper is up"
        if not self.evaporate.system.reagent_robot.gripper.is_up:
            self.evaporate.component_status = "Gripper is not up, setting up"
            self.evaporate.system.reagent_robot.gripper.lift()
        # Make sure gas transfer is up
        self.evaporate.component_status = "Checking if gas transfer is up"
        if not self.evaporate.system.reagent_robot.gas_transfer.is_up:
            self.evaporate.component_status = "Gas transfer is not up, setting up"
            self.evaporate.system.reagent_robot.gas_transfer.lift()

        self.evaporate.component_status = "Checking to confirm reagent robot is on"
        # Make sure the reagent robot is enabled
        #if not self.evaporate.system.reagent_robot.enabled:
        #   self.evaporate.system.reagent_robot.enable()
        self.evaporate.component_status = "Moving the robot to the self.evaporate.position"
        # Move the robot to the self.evaporate.position

        # Lower the gas transfer
        self.evaporate.component_status = "Lowering gas transfer"
        self.evaporate.system.reagent_robot.gas_transfer.lower()

        self.evaporate.component_status = "Setting gas transfer valve on"
        self.evaporate.system.reagent_robot.gas_transfer.start_transfer()
        # Turn on gas transfer valve

        self.evaporate.component_status = "Setting the vacuum system on"
        # Set vacuum system on

        # Set reactor's temp to 'self.evaporate.evaporation_temperature'
        self.evaporate.component_status = "Setting reactor %d " \
                "temperature controller to %f" \
                % (self.evaporate.reactor, self.evaporate.evaporation_temperature)
        self.evaporate.system.reactors[self.evaporate.reactor]. \
                temperature_controller.set_setpoint(
                        self.evaporate.evaporation_temperature)

        self.evaporate.component_status = "Turning on the Heating system"
        # Set reactor's heater on
        self.evaporate.system.reactors[self.evaporate.reactor]. \
                temperature_controller.turn_on()

        self.evaporate.component_status = "Checking if operation " \
                "will stop at a temperature"
        if int(self.evaporate.stop_temperature) > 0:
            self.evaporate.component_status = "Setting stir speed off"
            self.evaporate.system.reactors[self.evaporate.reactor].mixer.set_duty_cycle = 0
            # set reactor's stir speed to 0/off

        self.evaporate.component_status = "Starting the evaporation"
        # Set starting time
        self.evaporate.start_time = time.time()

        self.evaporate.component_status = "Setting pressure regulator 1" \
                                     " to the pressure %f for the" \
                                     " duration of %f" % \
                                     (self.evaporate.evaporation_pressure,
                                             self.evaporate.duration)
        #TODO
        # Set Pressure Regulator 1 to 'self.evaporate.evaporation_pressure'
        # and set pressure ramp time to 'self.evaporate.duration'/2
        # Ramp pressure over the first half of the evaporation,
        # then finish the 2nd half of the evaporation
        self.evaporate.system.pressure_regulators[self.evaporate.reactor].set_pressure(
                self.evaporate.evaporation_pressure,
                float(self.evaporate.duration/2))

        self.evaporate.component_status = "Waiting for evaporation procedure to complete"
        while (self.evaporate.start_time + self.evaporate.duration > time.time()):
            pass

        # Begin cool down phase
        self.evaporate.component_status = "Finished Evaporation, cooling down"

        self.evaporate.component_status = "Turning off reactor %d Heater Off" \
                % self.evaporate.reactor
        self.evaporate.system.reactors[self.evaporate.reactor].\
                    temperature_controller.turn_off()

        self.evaporate.component_status = "Turning cooling system on"
        # Set the cooling system on
        #self.evaporate.system.coolant_pump.on=True

        if int(self.evaporate.stop_temperature) == 0:
            self.evaporate.component_status = "Turning off reactor %d " \
                    "mixer's stir speed to 0" % self.evaporate.reactor
            self.evaporate.system.reactors[self.evaporate.reactor].mixer.set_duty_cycle = 0

        self.evaporate.component_status = "Setting reactor %d to the down position" \
                % self.evaporate.reactor
        self.evaporate.system.reactors[self.evaporate.reactor].lower()

        self.evaporate.component_status = "Setting gas transfer valve off"
        self.evaporate.system.reagent_robot.gas_transfer.stop_transfer()

        # Set vacuum system off
        self.evaporate.component_status = "Setting vacuum system off"
        # TODO Turn off vacuum system

        # Set gas transfer valve off again
        self.evaporate.component_status = "Setting gas transfer valve off"
        self.evaporate.system.reagent_robot.gas_transfer.stop_transfer()

        # Move gas transfer up
        self.evaporate.component_status = "Lifting gas transfer up"
        self.evaporate.system.reagent_robot.gas_transfer.lift()

        # Home reagent robot
        self.evaporate.component_status = "Homing reagent robot"
        # TODO Move reagent robot to 'Home'

        # Complete
        self.evaporate.component_status = "Successfully finished Evaporation Operation"

        self._is_complete.set()

if __name__ == '__main__':
    a = {'componenttype': 'EVAPORATE',
     'duration': 15,
     'durationvalidation': 'type=number; min=0; max=7200; required=true',
     'evaporationpressure': 10,
     'evaporationpressurevalidation': 'type=number; mn=0; max=25',
     'evaporationtemperature': 55,
     'evaporationtemperaturevalidation': 'type=number; min=20; max=200; required=true',
     'finaltemperature': 50,
     'finaltemperaturevalidation': 'type=number; min=20; max=200; required=true',
     'id': 103,
     'note': '',
     'reactor': 1,
     'reactorvalidation': 'type=enum-number; values=1,2,3; required=true',
     'sequenceid': 14,
     'stirspeed': 50,
     'stirspeedvalidation': 'type=number; min=0; max=5000; required=true',
     'stopattemperature': 60,
     'stopattemperaturevalidation': 'type=enum-number; values=0,1; required=true',
     'type': 'component',
     'validationerror': True}

    class db(object):
        details = a

    e = Evaporate(db)
    from IPython import embed
    embed()
