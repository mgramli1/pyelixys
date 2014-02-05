#!/usr/bin/env python
""" Evaporate Component
"""
from component import Component
# import the component threading module
from componentthread import ComponentThread
import time

class Evaporate(Component):
    """ Evaporate """
    def __init__(self, dbcomp):
        super(Evaporate, self).__init__(dbcomp)
        
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.final_temperature = dbcomp.details['finaltemperature']
        self.stop_temperature = dbcomp.details['stopattemperature']
        self.evaporation_temperature = dbcomp.details['evaporationtemperature']
        self.evaporation_pressure = dbcomp.details['evaporationpressure']
        self.duration = dbcomp.details['duration']
        self.reactor = dbcomp.details['reactor']
        self.validation_error = dbcomp.details['validationerror']
        self.stir_speed = dbcomp.details['stirspeed']
        self.note = dbcomp.details['note']
        # Additional attributes to be used during run()
        self.start_time = None

        # Set a thread
        self.thread = EvaporateThread()

    def run(self):
        '''
        Executes the 'EVAPORATE'
        run thread and the Evaporate
        object is passed into the
        EvaporateThread.
        '''
        self.thread.run(self)

class EvaporateThread(ComponentThread):
    '''
    Main Evaporate Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self):
        super(EvaporateThread, self).__init__()

    def run(self, evaporate):
        '''
        Begins the run process of the
        Evaporate unit operation.
        Function takes an Evaporate class object
        which shall contain the details of
        the unit op's execution.
        '''
        evaporate.component_status = "Starting the Evaporate run()"
        evaporate.component_status= ("Setting pressure regulator 1 to " 
                + str(evaporate.evaporationpressure))
        # Set pressure regualtor 1 to 'evaporate.evaporationpressure'
        # Note: Divide pressure by 3? This is down in the old codebase

        evaporate.component_status = ("Setting reactor "
                + str(evaporate.reactor)
                + " to the Evaporate position")
        # Set the Evaporate position to 'evaporate.reactor'

        evaporate.component_status = ("Setting reactor "
                + str(evaporate.reactor)
                + " stir speed to "
                + str(evaporate.stir_speed))
        # Set the Evaporate stir speed to 'evaporate.stir_speed'
        #evaporate.system.reactors[evaporate.reactor].mixer.stir_speed = \
        #evaporate.stir_speed

        # Make sure gripper is up
        evaporate.component_status = "Checking if gripper is up"
        if not evaporate.system.reagent_robot.gripper.is_up:
            evaporate.component_status = "Gripper is not up, setting up"
            evaporate.system.reagent_robot.gripper.lift()
        # Make sure gas transfer is up
        evaporate.component_status = "Checking if gas transfer is up"
        if not evaporate.system.reagent_robot.gas_transfer.is_up:
            evaporate.component_status = "Gas transfer is not up, setting up"
            evaporate.system.reagent_robot.gas_transfer.lift()
        
        evaporate.component_status = "Checking to confirm reagent robot is on"
        # Make sure the reagent robot is enabled
        #if not evaporate.system.reagent_robot.enabled:
        #   evaporate.system.reagent_robot.enable()
        evaporate.component_status = "Moving the robot to the evaporate position" 
        # Move the robot to the evaporate position
        
        # Lower the gas transfer
        evaporate.component_status = "Lowering gas transfer" 
        evaporate.system.reagent_robot.gas_transfer.lower()

        evaporate.component_status = "Setting gas transfer valve on" 
        # Turn on gas transfer valve
        
        evaporate.component_status = "Setting the vacuum system on"
        # Set vacuum system on
        
        # Set reactor's temp to 'evaporate.evaporation_temperature'
        evaporate.component_status = ("Setting reactor "
                + str(evaporate.reactor)
                + "'s temperature controllers to "
                + str(evaporate.evaporation_temperature))
        evaporate.system.reactor[evaporate.reactor].(
                temperature_controller).set_setpoint(
                        evaporate.evaporation_temperature)
          
        evaporate.component_status = "Turning on the Heating system"
        # Set reactor's heater on
        evaporate.system.reactors[evaporate.reactor].(
                temperature_controller).turn_on()


        evaporate.component_status = "Checking if operation will stop at a temperature"
        if int(evaporate.stop_temperature) > 0:
            evaporate.component_status = "Setting stir speed off"
            # set reactor's stir speed to 0/off
            #evaporate.system.reactors[evaporate.reactor].mixer.stir_speed = \
            #evaporate.stir_speed

        evaporate.component_status = "Starting the evaporation"
        # Set starting time
        evaporate.start_time = time.time()
        
        evaporate.component_status = "Setting pressure regulator 1 to the pressure "
                + str(evaporate.evaporation_pressure)
                + " for the duration of "
                + str(evaporate.duration) + " seconds"
        # Set Pressure Regulator 1 to 'evaporate.evaporation_pressure'
        # and set pressure ramp time to 'evaporate.duration'/2
        # Ramp pressure over the first half of the evaporation,
        # then finish the 2nd half of the evaporation

        evaporate.component_status = "Waiting for evaporation procedure to complete"
        # Wait - while(no timer override, no abort, and starttime+duration>time.time() )
        
        evaporate.component_status = "Finished Evaporation, cooling down"
        
        evaporate.component_status = (
                "Turning off reactor "
                + str(evaporate.reactor)
                + "'s Heater off")
        # Set the reactor's Heater off
        evaporate.system.reactors[evaporate.reactor].(
                temperature_controller).turn_off()
        evaporate.component_status = "Turning cooling system on"
        # Set the cooling system on
        #evaporate.system.coolant_pump.on=True

        if int(evaporate.stop_temperature) == 0:
            
            # Set stir speed to 0/off

        # Move reactor down

        # Set gas transfer valve off

        # Set vacuum system off

        # Set gas transfer valve off again

        # Move gas transfer up

        # Home reagent robot

        # Complete
