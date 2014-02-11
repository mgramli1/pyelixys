#!/usr/bin/env python
""" Mix Component
"""
import time
from component import Component
# import the component threading module
from componentthread import ComponentThread

class Mix(Component):
    """ Mix """
    def __init__(self, dbcomp):
        super(Mix, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.mix_time = dbcomp.details['mixtime']
        self.reactor = dbcomp.details['reactor']
        self.validation_error = dbcomp.details['validationerror']
        self.stir_speed = dbcomp.details['stirspeed']
        self.note = dbcomp.details['note']
        # Set a thread
        self.thread = MixThread(self)

    def run(self):
        '''
        Executes the 'Mix'
        run thread and the Mix
        object is passed into the
        MixThread.
        '''
        self.thread.start()


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

        self.mix.component_status = "Starting the Mix run()"

        self.mix.component_status = "Mixing"

        self.mix.component_status = "Setting reactor %s to stir speed %s" \
                % (self.mix.reactor, self.mix.stir_speed)
        self.mix.system.reactors[self.mix.reactor].mixer.set_duty_cycle(
                self.mix.stir_speed)
        time.sleep(2)


        self.mix.component_status = "Mixing reagent, waiting for completion"
        starttimer = time.time()
        while (starttimer + self.mix.mix_time > time.time()):
            pass

        self.mix.component_status = "Setting reactor %s to stir motor off" \
                % (self.mix.reactor)
        self.mix.system.reactors[self.mix.reactor].mixer.set_duty_cycle(0)
        time.sleep(2)


        self.mix.component_status = "Sucessfully finished " \
                "running Mix operation"
        self._is_complete.set()

if __name__ == '__main__':
    a = {"mixtimevalidation": "type=number; min=0; max=7200; required=true",
            "mixtime": 0, "componenttype": "MIX",
            "reactor": 0, "validationerror": True,
            "stirspeed": 500, "sequenceid": 14, "note": "",
            "reactorvalidation": "type=enum-number; values=1,2,3; required=true",
            "type": "component", "id": 112,
            "stirspeedvalidation": "type=number; min=0; max=5000; required=true"}
    class db(object):
        details = a

    m = Mix(db)
    from IPython import embed
    embed()


