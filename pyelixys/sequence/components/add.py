#!/usr/bin/env python
""" Add Component
"""
import time
from component import Component
# import the component threading module
from componentthread import ComponentThread

class Add(Component):
    """ Add """
    def __init__(self, dbcomp):

        super(Add, self).__init__(dbcomp)
        details = dbcomp.details
        self.component_id = details['id']
        self.sequence_id = details['sequenceid']
        self.reagent_pos = details['reagentpos']
        self.reactor = self.system.reactors[details['reactor']]
        self.delivery_time = details['deliverytime']
        self.delivery_position = details['deliveryposition']
        self.delivery_pressure = details['deliverypressure']
        self.note = details['note']

    def start(self):
        self.join()
        self.thread = AddThread(self)
        self.thread.start()
        return self.thread


    def run(self):
        '''
        Begins the run process of the
        Add unit operation.
        '''
        self.system.pressure_regulators[0].setpoint = 0.0
        self.component_status = "Setting Pressure Regulator 1 to %f" % \
                (self.delivery_pressure)
        self.system.pressure_regulators[0].set_pressure(
                self.delivery_pressure)

        self.component_status = "Moving Reactor %s " \
                "to the ADD position" % self.reactor
        self.reactor.move_add()

        self.component_status = "Lift Reactor %s" % self.reactor 
        self.reactor.lift()


        self.component_status = "Grab reagent %d" % self.reagent_pos
        self.system.reagent_robot.grab_reagent(self.reactor.id_, self.reagent_pos)

        self.component_status = "Prepare to add reagent %d on " \
                "reactor %s to position %d" % (self.reagent_pos,
                                               self.reactor,
                                               self.delivery_position)

        self.system.reagent_robot.drop_add(self.reactor.id_, self.delivery_position)

        self.component_status = "Setting gas transfer on"
        self.system.reagent_robot.gas_transfer.start_transfer()

        self.component_status = "Delivering reagent, waiting for completion"

        starttime = time.time()
        while (starttime + self.delivery_time > time.time()):
            time.sleep(0.1)

        self.system.reagent_robot.gas_transfer.stop_transfer()

        self.component_status = "Returning reagent vial %d" % self.reagent_pos

        self.system.reagent_robot.return_reagent(self.reactor.id_, self.reagent_pos)


class AddThread(ComponentThread):
    '''
    Main Add Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self, add_component):
        super(AddThread, self).__init__()
        self.add = add_component

    def run(self):
        
        self._is_complete.clear()

        self.add.run()
        
        self._is_complete.set()
        '''
        Executes the 'ADD' run thread
        and the Add object is passed
        into the AddThread
        '''


if __name__ == '__main__':
    

    details = {}

    details['reactor'] = 0
    details['sequenceid'] = 0
    details['reagentpos'] = 5
    details['id'] = 0
    details['deliverytime'] = 5.0
    details['deliveryposition'] = 0.0
    details['deliverypressure'] = 3.0
    details['note'] = "Add from reactor 0 position 3 to add 0"



    class dbcomp(object):
        details = details

    a = Add(dbcomp)
    from IPython import embed
    embed()


