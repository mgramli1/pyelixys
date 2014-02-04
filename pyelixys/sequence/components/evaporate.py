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
        evaporate.log.debug("Starting the Evaporate run()")
        evaporate.component_status = "Starting the Evaporate run()"
        evaporate.log.debug("Setting pressure regulator 1 to " 
                + str(evaporate.evaporationpressure))
        # Set pressure regualtor 1 to 'evaporate.evaporationpressure'
        # Note: Divide pressure by 3?

        evaporate.log.debug("Setting reactor "
                + str(evaporate.reactor)
                + " to the Evaporate position")
        evaporate.component_status = ("Setting reactor "
                + str(evaporate.reactor)
                + " to the Evaporate position")
        # Set the Evaporate position to 'evaporate.reactor'

        evaporate.log.debug("Setting reactor "
                + str(evaporate.reactor)
                + " stir speed to "
                + str(evaporate.stir_speed))
        evaporate.component_status = ("Setting reactor "
                + str(evaporate.reactor)
                + " stir speed to "
                + str(evaporate.stir_speed))
        # Set the Evaporate stir speed to 'evaporate.stir_speed'

        # Make sure gripper is up
        evaporate.log.debug("Checking if gripper is up")
        evaporate.component_status = "Checking if gripper is up"
        if not evaporate.system.reagent_robot.gripper.is_up:
            evaporate.log.debug("Gripper is not up, setting up")
            evaporate.component_status = "Gripper is not up, setting up"
            evaporate.system.reagent_robot.gripper.lift()
        # Make sure gas transfer is up
        evaporate.log.debug("Check if gas transfer is up")
        evaporate.component_status = "Checking if gas transfer is up"
        if not evaporate.system.reagent_robot.gas_transfer.is_up:
            evaporate.log.debug("Gas Transfer is not up, setting up")
            evaporate.component_status = "Gas transfer is not up, setting up"
            evaporate.system.reagent_robot.gas_transfer.lift()
        
        evaporate.log.debug("Checking to confirm reagent robot is on")
        evaporate.component_status
        # Make sure the reagent robot is enabled
        evaporate.log.debug("Moving the robot to the evaporate position")
        # Move the robot to the evaporate position
        
        # Lower the gas transfer
        evaporate.log.debug("Lowering gas transfer")
        evaporate.system.reagent_robot.gas_transfer.lower()

        evaporate.log.debug("Setting gas transfer valve on")
        # Turn on gas transfer valve

        # Set vacuum system on
        
        # Set reactor's temp to 'evaporate.evaporation_temperature'
        evaporate.log.debug("Setting reactor "
                + str(evaporate.reactor)
                + "'s temperature controllers to "
                + str(evaporate.evaporation_temperature))
        evaporate.system.reactor[evaporate.reactor].temperature_controller.set_setpoint(
                evaporate.evaporation_temperature)
          

        evaporate.log.debug("Turning on the Heating system")
        # Set reactor's heater on

        evaporate.log.debug("Checking of operation will stop at a temperature")
        if int(evaporate.stop_temperature) > 0:
            evaporate.log.debug("Setting stir speed off")
            # set reactor's stir speed to 0/off
       
        # Set starting time
        evaporate.start_time = time.time()
       
        evaporate.log.debug("Setting pressure regulator 1 to the pressure "
                + str(evaporate.evaporation_pressure)
                + " for the duration of "
                + str(evaporate.duration) + " seconds")
        # Set Pressure Regulator 1 to 'evaporate.evaporation_pressure'
        # and wait the time for 'evaporate.duration'
       

