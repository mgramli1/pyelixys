#!/usr/bin/env python
""" React Component
"""
from component import Component
# import the component threading module
from componentthread import ComponentThread

class React(Component):
    """ React 
    
    Thre react0 sequence:
    
    I. Moves the reactor to React0 Position on the cassette
    II. Starts the stir motor
    III. Turns on the heater collets of the reactor if it is a heated reaction
    IV. Stops the stir motor after a duration of time
    V. Turns on the cooling system until the reaction has reached its final temperature
    VI. Cools for an extra 120s if a cooling delay is desired.
    
    """
    def __init__(self, dbcomp):
        super(React, self).__init__(dbcomp)

        self.component_id = dbcomp.details['componentid']
        self.sequence_id = dbcomp.details['sequenceid']
        self.reactor = dbcomp.details['reactor']
        self.stir_speed = dbcomp.details['stirspeed']
        self.duration = dbcomp.details['duration']
        self.reaction_temperature = dbcomp.details['reactiontemperature']
        self.note = dbcomp.details['note']
        self.cool_duration = details['coolduration']
        self.cooling_delay - details['coolingdelay']
        # Set a thread
        self.thread = React0Thread()
        
    def start(self):
        self.join()
        self.thread = AddThread(self)
        self.thread.start()
        return self.thread
        
    def run(self):
        '''
        Begins the run process of the
        React unit operation.
        '''
        
        self.component_status = "Moving Reactor %d to React0" % (self.reactor.id_)        
        self.reactor.move_react0()
        self.component_status = "Setting Reaction Temperature to &f" % (self.reactiontemperature.id_)        
        self.reactor.temperature_controller.setpoint = self.reaction_temperature
        self.reactor.temperature_controller.on = True
        self.component_status = "Setting reactor %d to stir speed %f" % (self.reactor.id_, self.stirspeed.id_) 
        stopped_mixer = False
        while (time.time() - self.start_time < self.duration):
            if self.reactor.temperature_controller.temperature >= self.reaction_temperature:
                if stopped_mixer is False:
                    stopped_mixer = True
                    self.reactor.mixer.duty_cycle = 50.0
            time.sleep(0.1)
        self.reactor.mixer.duty_cycle = 0.0
        self.component_status = "Setting reactor %d stir motor off" \
                % (self.reactor.id_)
        self.reactor.temperature_controller.on = False
        
        self.reactor.mixer.set_duty_cycle(0)
        time.sleep(2)
        self.component_status = "Turning on the coolant pump"

        self.system.coolant_pump.on = True
        
        self.start_time = time.time()
        while(self.final_temperature < self.reactor.temperature_controller.temperature):
            if time.time() - self.start_time > self.cool_duration:
                break
            time.sleep(0.1)

        self.system.coolant_pump.on = False
        self.component_status = "Returning reactor %d to install" % self.reactor.id_
        
        

class ReactThread(ComponentThread):
    '''
    Main React Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self):
        super(ReactThread, self).__init__()
        self.react0 = react0_component
        
    def run(self):

        self._is_complete.clear()

        self.react0.run()

        self._is_complete.set()
        '''
        Executes the 'React0' run thread
        and the Add object is passed
        into the AddThread
        '''        
if __name__ == '__main__':


    details = {}

    details['reactor'] = 0
    details['sequenceid'] = 0
    details['componentid'] = 0
    details['stirpeed'] = 50
    details['duration'] = 10 
    details['reactiontemperature'] = 55
    details['coolduration'] = 120
    details['coolingdelay'] = True
    details['note'] = ""

    class dbcomp(object):
        details = details

    a = Add(dbcomp)
    from IPython import embed
    embed()

        
