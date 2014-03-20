#!/usr/bin/env python
""" Mix Component
"""
import time
from component import Component
# import the component threading module
from componentthread import ComponentThread

class Mix(Component):
    """ Mix 
    
    The mix operation controls the mixer motor, in which the user sets a duty cycle (0 to 100) 
    a duration of time to mix at.
    
    """
    def __init__(self, dbcomp):
        super(Mix, self).__init__(dbcomp)
        details = dbcomp.details
        self.component_id = details['componentid']
        self.sequence_id = details['sequenceid']
        self.mix_time = details['time']
        self.reactor = self.system.reactors[details['reactor']]
        self.stir_speed = details['stirspeed']
        self.note = details['note']
        # Set a thread

    def run(self):
        '''
        Executes the 'Mix'
        run thread and the Mix
        object is passed into the
        MixThread.
        '''
        self.component_status = "Starting the Mix run()"

        self.component_status = "Mixing"

        self.component_status = "Setting reactor %d to stir speed %f" \
                % (self.reactor.id_, self.stir_speed)
        self.reactor.mixer.set_duty_cycle(self.stir_speed)
        time.sleep(2)

        self.component_status = "Mixing reagent, waiting for completion"
        starttimer = time.time()
        while (starttimer + self.mix_time > time.time()):
            time.sleep(0.1)

        self.component_status = "Setting reactor %d to stir motor off" \
                % (self.reactor.id_)
        
        self.reactor.mixer.set_duty_cycle(0)
        time.sleep(2)


        self.component_status = "Sucessfully finished " \
                "running Mix operation"
        
        

class MixThread(ComponentThread):
    '''
    Main Mix Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self, mix):
        '''
        Constructs a new thread
        and expects a Mix object
        to be passed in.
        '''
        super(MixThread, self).__init__()
        self.mix = mix

    def run(self):
        '''
        Begins the run process of the
        Mix unit operation.
        Runs as a thread
        '''
        self._is_complete.clear()

        self.mix.run()
        
        self._is_complete.set()
        

if __name__ == '__main__':
    details = {}
    details["time"] = 10,
    details["componenttype"] = "MIX"
    details["reactor"] = 0 
    details["stirspeed"] = 100.0 
    details["sequenceid"] = 14
    details["note"] = "",
    details["type"] = "component" 
    details["componentid"] = 112
            
    class db(object):
        details = details

    m = Mix(db)
    from IPython import embed
    embed()


