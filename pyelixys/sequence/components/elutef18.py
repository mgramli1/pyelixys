#!/usr/bin/env python
""" Elute F18 Component
"""
import time
from component import Component
# import the component threading module
from componentthread import ComponentThread

class EluteF18(Component):
    """ Elute F18 
    
    I. Pressure Regulator 1 is set to the elute pressure
    II. The target reactor moves to the Add position
    III. The target reactor lifts
    IV. The reagent robot grabs the reagent from the cassette
    V. The casette stopcocks are set to elute
    VI. The reagent robot adds the reagent
    VII. The reagent is returned
    
    """
    def __init__(self, dbcomp):
        super(EluteF18, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.elute_time = dbcomp.details['elutetime']
        self.reagent_pos = dbcomp.details['reagentpos']
        self.reactor = self.system.reactors[dbcomp.details['reactor']]
        self.elute_pressure = dbcomp.details['elutepressure']
        self.note = dbcomp.details['note']
        # Set a thread
        self.thread = EluteF18Thread(self)

    def run(self):
        '''
        Executes the 'EluteF18'
        '''

        self.system.pressure_regulators[0].setpoint = 0.0
        self.component_status = "Setting Pressure Regulator 1"

        self.system.pressure_regulators[0].set_pressure(
                self.elute_pressure)

        time.sleep(1.0)

        self.component_status = "Moving Reactor %s " \
                "to the ADD position" % self.reactor
        self.reactor.move_add()

        self.component_status = "Lift Reactor %s" % self.reactor
        self.reactor.lift()

        self.component_status = "Grab reagent %d" % self.reagent_pos
        self.system.reagent_robot.grab_reagent(self.reactor.id_, self.reagent_pos)

        self.component_status = "Set stopcocks on %s for elute" % self.reactor
        self.reactor.set_stopcocks_for_elute()

        self.component_status = "Drop Reagent in %s Elute Position" % self.reactor
        self.system.reagent_robot.drop_elute(self.reactor.id_)

        self.component_status = "Setting gas transfer on"
        self.system.reagent_robot.gas_transfer.start_transfer()


        self.component_status = "Elute waiting for completion"
        starttime = time.time()
        while (starttime + self.elute_time > time.time()):
            time.sleep(0.1)

        self.system.reagent_robot.gas_transfer.stop_transfer()


        self.component_status = "Returning reagent vial %d" % self.reagent_pos
        self.system.reagent_robot.return_reagent(self.reactor.id_, self.reagent_pos)


class EluteF18Thread(ComponentThread):
    '''
    Main Elute F18 Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self, elute):
        super(EluteF18Thread, self).__init__()
        self.elute = elute

    def run(self):
        '''
        Begins the run process of the
        Elute() unit operation.
        Runs as a thread
        '''
        self._is_complete.clear()
        self.elute.run()
        self._is_complete.set()


if __name__ == '__main__':

    details = {}
    details['reactor'] = 0
    details['sequenceid'] = 0
    details['reagentpos'] = 5
    details['id'] = 0
    details['elutetime'] = 2.0
    details['elutepressure'] = 3.0
    details['note'] = "Elute from reactor 0 position 5 to add"


    class db(object):
        details = details

    el = EluteF18(db)
    from IPython import embed
    embed()


