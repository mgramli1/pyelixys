#!/usr/bin/env python
""" Add Component
"""
from component import Component
# import the component threading module
from componentthread import ComponentThread

class Add(Component):
    """ Add """
    def __init__(self, dbcomp):

        super(Add, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.reagent_id = dbcomp.details['reagent']
        self.reactor = dbcomp.details['reactor']
        self.delivery_time = dbcomp.details['deliverytime']
        self.delivery_position = dbcomp.details['deliveryposition']
        self.delivery_pressure = dbcomp.details['deliverypressure']
        self.validation_error = dbcomp.details['validationerror']
        self.note = dbcomp.details['note']
        
        # Set a thread
        self.thread = AddThread()
        
    def run(self):
        '''
        Executes the 'ADD' run thread
        and the Add object is passed
        into the AddThread
        '''
        self.thread.run(self)

class AddThread(ComponentThread):
    '''
    Main Add Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self):
        super(AddThread, self).__init__()

    def run(self, add):
        '''
        Begins the run process of the
        Add unit operation.
        Function takes an Add class object
        which shall contain the details of
        the unit op's execution.
        '''
        add.log.debug("Starting the Add run()")
        
        add.log.debug("Setting Pressure Regulator 1 to " + 
                str(add.delivery_pressure))
        # Set Pressure Regulator 1 to 'delivery_pressure'

        add.log.debug("Setting Reactor " +
                str(add.reactor) +
                " to the ADD position")
        # Set Reactor Position to the ADD position

        add.log.debug("Setting gripper down")
        # Set the Gripper down
        add.system.reagent_robot.gripper.lower()
        
        add.log.debug("Closing gripper arm")
        # Set the Gripper to closed
        add.system.reagent_robot.gripper.close()

        add.log.debug("Setting gripper up")
        # Set the Gripper up
        add.system.reagent_robot.gripper.lift()

        add.log.debug("Setting gripper to " +
                str(delivery_pressure))
        # Set the gripper to the 'delivery_position'
        
        add.log.debug("Setting gas transfer down")
        # Set the Gas Trasnfer down
        add.system.gas_transfer.lower()

        add.log.debug("Turning on gas transfer")
        # Turn on gas transfer
        
        add.log.debug("Setting gripper down")
        # Set the gripper down
        add.system.reagent_robot.lower()
