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
        self.component_id = details['componentid']
        self.sequence_id = details['sequenceid']
        self.final_temperature = details['finaltemperature']
        self.evaporation_temperature = details['evaporationtemperature']
        self.evaporation_pressure = details['evaporationpressure']
        self.duration = details['duration']
        self.reactor = self.system.reactors[details['reactor']]
        self.stir_speed = details['stirspeed']
        self.note = details['note']
        self.cool_duration = details['coolduration']
        # Additional attributes to be used during run()
        self.start_time = 0

        # Set a thread
        self.thread = EvaporateThread(self)

    def run(self):
        '''
        Executes the 'EVAPORATE'
        run thread and the Evaporate
        object is passed into the
        EvaporateThread.
        '''
        self.component_status = "Starting the Evaporate run()"
        
        self.system.pressure_regulators[0].setpoint = 0.0
        time.sleep(0.1)
        
        self.component_status = "Setting pressure regulator 1 to %f" % \
                (self.evaporation_pressure    )
        
        self.system.pressure_regulators[0].set_pressure(
                self.evaporation_pressure)
                
        self.component_status = "Moving reactor %d to evaportation " \
                        "position" % self.reactor.id_
        
        self.reactor.move_evaporate()
        self.reactor.lift()
        
        self.component_status = "Setting reactor %d stir speed to %f" % (self.reactor.id_, self.stir_speed)
        
        self.reactor.mixer.duty_cycle = self.stir_speed
        #TODO Pull in RPM conversion from system config
        
        self.component_status = "Moving reagent robot to evaportation" \
                        "position on reactor %d" % self.reactor.id_
        self.system.reagent_robot.move_evaporate(self.reactor.id_)
        self.system.reagent_robot.gas_transfer.lower()
        
        self.component_status = "Starting gas transfer"
        self.system.reagent_robot.gas_transfer.start_transfer()
        
        
        self.component_status = "Setting the vacuum system on"
        # Set vacuum system on
        #TODO Turn on vacuum
        
        self.component_status = "Setting reactor %d " \
                    "temperature controller to %f" \
                    % (self.reactor.id_, self.evaporation_temperature)
        self.reactor.temperature_controller.setpoint = self.evaporation_temperature
        self.reactor.temperature_controller.on = True
        
        self.component_status = "Starting the evaporation"
        
        self.start_time = time.time()

        self.component_status = "Waiting for evaporation procedure to complete"
        
        stopped_mixer = False
        while (time.time() - self.start_time < self.duration):
            if self.reactor.temperature_controller.temperature >= self.evaporation_temperature:
                if stopped_mixer is False:
                    stopped_mixer = True
                    self.reactor.mixer.duty_cycle = 0.0
            time.sleep(0.1)
        
        self.reactor.mixer.duty_cycle = 0.0
        self.component_status = "Cooling after evaporation"
        self.reactor.temperature_controller.on = False
        
        #TODO turn off vacuum
        
        self.component_status = "Cooling after evaporation"

        self.system.reagent_robot.gas_transfer.stop_transfer()
        
        self.system.reagent_robot.gas_transfer.lift()
        
        self.system.reagent_robot.move_install(0)
        
        self.component_status = "Turing on the coolant pump"

        self.system.coolant_pump.on = True
        
        self.start_time = time.time()
        while(self.final_temperature < self.reactor.temperature_controller.temperature):
            if time.time() - self.start_time > self.cool_duration:
                break
            time.sleep(0.1)

        self.system.coolant_pump.on = False
        self.component_status = "Returning reactor %d to install" % self.reactor.id_
        self.reactor.move_install()
        


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
        
        self.evaporate.run()

        self._is_complete.set()

if __name__ == '__main__':
    details = {}
    
    details['duration'] = 15
    details['evaporationpressure'] = 10
    details['evaporationtemperature'] = 55
    details['finaltemperature'] = 50.0
    details['reactor'] = 0
    details['stirspeed'] = 50.0
    details['coolduration'] = 5.0
    details['sequenceid'] = 14
    details['componentid'] = 0
    details['note'] = '' 
                     
    class db(object):
        details = details

    e = Evaporate(db)
    from IPython import embed
    embed()
