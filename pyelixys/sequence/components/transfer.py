#!/usr/bin/env python
""" Transfer Component
"""

import time
from component import Component
# import the component threading module
from componentthread import ComponentThread

class Transfer(Component):
    """ Transfer 
    
    The transfer unit operation executes as follows:
    
    I. The source reactor moves to the transfer position
    II. The target reactor moves to the add position
    III. Pressure Regulator 1 is set to the target pressure
    IV. Gas Transfer Starts
    V. Gas Transfer occurs for a set amount of time
    VI. Source Reactor moves to install
    VII. Target Reactor moves to install
    
    """
    def __init__(self, dbcomp):
        super(Transfer, self).__init__(dbcomp)
        self.component_id = dbcomp.details['componentid']
        self.sequence_id = dbcomp.details['sequenceid']
        self.mode = dbcomp.details['mode']
        self.pressure = dbcomp.details['pressure']
        self.delivery_position = dbcomp.details['deliveryposition']
        self.duration = dbcomp.details['duration']
        self.source_reactor = self.system.reactors[details['sourcereactor']]
        self.target_reactor = self.system.reactors[details['targetreactor']]
        self.note = dbcomp.details['note']
        # Set a thread
        
    def start(self):
        self.join()
        self.thread = TransferThread(self)        
        self.thread.start()
        return self.thread        

    def run(self):
        '''
        Begins the run process of the
        Transfer unit operation.
        '''
        self.system.pressure_regulators[0].setpoint = 0.0
        self.component_status = "Moving Reactor %d to Transfer" % self.source_reactor.id_
        self.source_reactor.move_transfer()
        self.source_reactor.lift()
        self.component_status = "Moving Reactor %d to Add" % self.target_reactor.id_
        self.target_reactor.move_add()
        self.target_reactor.lift()
        self.component_status = "Moving Reagent Robot to Transfer of Reactor %d" % self.source_reactor.id_
        self.system.reagent_robot.prepare_transfer(self.source_reactor.id_)
        self.component_status = "Setting Pressure Regulator to %f" % self.pressure
        self.system.pressure_regulators[0].set_pressure(self.pressure) 
        self.component_status = "Starting Gas Transfer"
        self.system.reagent_robot.gas_transfer.start_transfer()
        starttime = time.time()
        while (starttime + self.duration > time.time()):
            time.sleep(0.1)
        self.system.reagent_robot.gas_transfer.stop_transfer()
        self.component_status = "Transfer Complete"
        self.system.reagent_robot.move_install(0)
        self.source_reactor.move_install()
        self.target_reactor.move_install()
        

class TransferThread(ComponentThread):
    '''
    Main Transfer Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self, transfer_component):
        super(TransferThread, self).__init__()
        self.transfer = transfer_component
    
    def run(self):
        
        self._is_complete.clear()
        
        self.transfer.run()
        
        self._is_complete.set()
        

if __name__ == '__main__':
    

    details = {}

    details['componentid'] = 0
    details['sequenceid'] = 0
    details['sourcereactor'] = 0
    details['targetreactor'] = 1
    details['duration'] = 5.0
    details['deliveryposition'] = 0
    details['pressure'] = 3.0
    details['mode'] = None
    details['note'] = "Transferring from Reactor 1 to Reactor 2"



    class dbcomp(object):
        details = details

    t = Transfer(dbcomp)
    from IPython import embed
    embed()


