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
        self.reagent_id = details['reagent']
        self.reactor = details['reactor']
        self.delivery_time = details['deliverytime']
        self.delivery_position = details['deliveryposition']
        self.delivery_pressure = details['deliverypressure']
        self.validation_error = bool(details['validationerror'])
        self.note = str(details['note'])

        # Set a thread
        self.thread = AddThread(self)


    def run(self):
        '''
        Executes the 'ADD' run thread
        and the Add object is passed
        into the AddThread
        '''
        self.thread.start()

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
        '''
        Begins the run process of the
        Add unit operation.
        Function takes an Add class object
        which shall contain the details of
        the unit op's execution.
        '''
        self._is_complete.clear()

        self.add.component_status = "Starting the Add run()"

        self.add.component_status = "Setting Pressure Regulator 1 to %f" % \
                (self.add.delivery_pressure)
        self.add.system.pressure_regulators[0].set_pressure(
                self.add.delivery_pressure)

        self.add.component_status = "Setting Reactor %d " \
                "to the ADD position" % self.add.reactor
        # TODO Move reactor to ADD
        # Check if we already at the correct position
        # if: reactor position is in the ADD position
        #   Check that the reactor is either up or down
        #   If all true, then we are in position
        # Else, we need to setup for the Add op
        # else:
        #   needs_pressure_restore = False
        #   if: reactor position is in either one of the REACT positions
        #       if: reactor is up
        #           self.add.system.pressure_regulators[1].set_pressure(30)
        #           needs_pressure_restore = True
        #
        #   self.add.system.reactors[self.add.reactor].lower() - Move Reactor down
        #   Enable reactor robot
        #
        #   if needs_pressure_restore:
        #       self.add.system.pressure_regulators[1].set_pressure(60)
        #
        #   Move reactor to the ADD position
        #   self.add.system.reactors[self.add.reactors].lift() - Move reactor up/raise reactor
        #   Disable the reactor robot

        self.add.component_status = "Setting Gripper open"
        self.add.system.reagent_robot.gripper.open()

        self.add.component_status = "Setting gripper up"
        self.add.system.reagent_robot.gripper.lift()

        self.add.component_status = "Setting gas transfer up"
        self.add.system.reagent_robot.gas_transfer.lift()

        #TODO Check if reagent robot are enabled & enable them if not

        self.add.component_status = ""

        self.add.component_status = "Picking up vial"

        self.add.component_status = "Setting gripper down"
        self.add.system.reagent_robot.gripper.lower()

        self.add.log.component_status =  "Closing gripper arm"
        self.add.system.reagent_robot.gripper.close()

        self.add.log.component_status = "Setting gripper up"
        self.add.system.reagent_robot.gripper.lift()

        # TODO Check that the gripper has the vial

        # TODO Move reactor to Delivery Position with
        # self.add.delivery_position (1 or 2)

        self.add.component_status = "Setting gas transfer down"
        self.add.system.reagent_robot.gas_transfer.lower()

        self.add.component_status = "Setting gas transfer on"
        self.add.system.reagent_robot.gas_transfer.start_transfer()

        self.add.component_status = "Setting gripper down"
        self.add.system.reagent_robot.gripper.lower()

        self.add.component_status = "Delivering reagent, waiting for completion"
        starttime = time.time()
        while (starttime + self.add.delivery_time > time.time()):
            pass

        self.add.component_status = "Returning vial"

        self.add.component_status = "Setting gripper up"
        self.add.system.reagent_robot.gripper.lift()

        self.add.component_status = "Setting gas transfer off"
        self.add.system.reagent_robot.gas_transfer.stop_transfer()

        self.add.component_status = "Setting gas transfer up"
        self.add.system.reagent_robot.gas_transfer.lift()

        self.add.component_status = "Moving reactor %d to Reagent Position" \
                % self.add.reactor
        # TODO Move to reagent position

        self.add.component_status = "Setting gripper down"
        self.add.system.reagent_robot.gripper.lower()

        self.add.component_status = "Opening gripper arm"
        self.add.system.reagent_robot.gripper.open()

        self.add.component_status = "Setting gripper up"
        self.add.system.reagent_robot.gripper.lift()

        self.add.component_status = "Homing reagent robot"
        # TODO Move reagent_robot to HOME

        self.add.component_status = "Successfully finished Add Operation"

        self._is_complete.set()

if __name__ == '__main__':
    a = {"componenttype": "ADD",
            "sequenceid": 4, "deliverytimevalidation": "type=number; min=0; max=90", "reactor": 1,
            "deliverypressurevalidation": "type=number; min=0; max=15", "deliverytime": 15, "deliveryposition": 1,
            "reagentvalidation": "type=enum-reagent; values=109,110,112; required=true",
            "deliverypositionvalidation": "type=enum-number; values=1,2; required=true",
            "note": "reagent%201", "reagent": 109, "deliverypressure": 3,
            "reactorvalidation": "type=enum-number; values=1,2,3; required=true",
            "validationerror": False, "type": "component", "id": 19}


    class db(object):
        details = a

    a = Add(db)
    from IPython import embed
    embed()


