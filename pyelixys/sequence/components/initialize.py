#!/usr/bin/env python
""" Initialize Component
"""
import time
from component import Component
# import the component threading module
from componentthread import ComponentThread

class Initialize(Component):
    """ Initialize"""
    def __init__(self, dbcomp):
        super(Initialize, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.validation_error = dbcomp.details['validationerror']

        # Set a thread
        self.thread = InitializeThread(self)

    def run(self):
        '''
        Executes the 'INITIALIZE'
        run thread and the Initialize
        object is passed into the
        InitializeThread.
        '''
        self.thread.start()

class InitializeThread(ComponentThread):
    '''
    Main Initialize Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self, init):
        super(InitializeThread, self).__init__()
        self.init = init

    def run(self):
        '''
        Begins the run process of the
        Init() unit operation.
        Runs as a thread
        '''
        self._is_complete.clear()

        self.init.component_status = "Starting the Initialize run()"

        self.init.component_status = "Initializing valves"

        self.init.component_status = "Closing the gas transfer valve"
        self.init.system.reagent_robot.gas_transfer.stop_transfer()

        # For each reactor:
        for reactor in self.init.system.reactors:
            self.init.component_status = "\tSetting reactor %d down" \
                    % (reactor.conf['id'] + 1)
            reactor.lower()
            time.sleep(2)

        for reactor in self.init.system.reactors:
            for stopcock in reactor.stopcocks:
                time.sleep(1)
                self.init.component_status = "Setting reactor %d " \
                        "stopcock %d to CCW1" \
                       % (reactor.conf['id'] + 1, stopcock.id_)
                stopcock.turn_counter_clockwise()

                time.sleep(1)
                self.init.component_status = "Setting reactor %d " \
                        "stopcock %d to CCW2" \
                        % (reactor.conf['id'] + 1, stopcock.id_)
                stopcock.turn_counter_clockwise()

                time.sleep(1)
                self.init.component_status = "Setting reactor %d " \
                        "stopcock %d to CW" \
                         % (reactor.conf['id'] + 1, stopcock.id_)
                stopcock.turn_clockwise()


        for reactor in self.init.system.reactors:
            self.init.component_status = "Turning reactor %d " \
                    "F18 Valve off" % (reactor.conf['id'] + 1)
            reactor.f18.turn_off()



        self.init.component_status = "Setting coolling system off"
        # self.init.system.coolant_pump.on = False

        self.init.component_status = "Setting vacuum system off"
        # self.init.system.vacuum.on = False

        for reactor in self.init.system.reactors:
            self.init.component_status = "Setting reactor %d " \
                    "heater off" \
                    % (reactor.conf['id'] + 1)
            # TODO turn off heater
            self.init.component_status = "Setting reactor %d " \
                    "mixter off" \
                    % (reactor.conf['id'] + 1)
            reactor.mixer.set_duty_cycle(0)

        self.init.component_status = "Setting pressure regulator 1 to 5 psi"
        self.init.system.pressure_regulators[0].set_pressure(5)

        self.init.component_status = "Setting pressure regulator 2 to 60 psi"
        self.init.system.pressure_regulators[1].set_pressure(60)

        self.init.component_status = "Setting gripper up"
        self.init.system.reagent_robot.gripper.lift()

        self.init.component_status = "Opening gripper arm"
        self.init.system.reagent_robot.gripper.open()

        self.init.component_status = "Setting gas transfer up"
        self.init.system.reagent_robot.gas_transfer.lift()

        for reactor in self.init.system.reactors:
            self.init.component_status = "Setting reactor %d down" \
                    % (reactor.conf['id'] + 1)
            reactor.lower()
            time.sleep(2)
            # TODO Confirm or does lower() confirm reactor is down?

        # TODO Home reactors and reagent robots, dont confirm?
        self.init.component_status = "Homing reagent robot"
        # self.init.syste.reagent_robot.home()

        for reactor in self.init.system.reactors:
            self.init.component_status = "Homing reactor %d" \
                    % (reactor.conf['id'] + 1)
            # TODO Home reactor, dont confirm?

        for reactor in self.init.system.reactors:
            self.init.component_status = "Homing reactor %d" \
                    % (reactor.conf['id'] + 1)
            # TODO Home reactor, but confirm?

        # TODO Raise robots to install position
        for reactor in self.init.system.reactors:
            self.init.component_status = "Moving reactor %d " \
                    "to the install position" \
                    % (reactor.conf['id'] + 1)
            # TODO Move reactor install, but confirm?

        self.init.component_status = "Sucessfully finished " \
                "running Initialize operation"
        self._is_complete.set()

if __name__ == '__main__':
    a = {"note": "", "sequenceid": 4, "validationerror": False,
            "componenttype": "INITIALIZE", "type": "component",
            "id": 26}

    class db(object):
        details = a

    i = Initialize(db)
    from IPython import embed
    embed()
