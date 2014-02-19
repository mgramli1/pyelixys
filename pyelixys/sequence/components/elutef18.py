#!/usr/bin/env python
""" Elute F18 Component
"""
import time
from component import Component
# import the component threading module
from componentthread import ComponentThread

class EluteF18(Component):
    """ Elute F18 """
    def __init__(self, dbcomp):
        super(EluteF18, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.elute_time = dbcomp.details['elutetime']
        self.reactor = dbcomp.details['reactor']
        self.validation_error = dbcomp.details['validationerror']
        self.note = dbcomp.details['note']
        self.reagent = dbcomp.details['reagent']
        self.elute_pressure = dbcomp.details['elutepressure']
        # Set a thread
        self.thread = EluteF18Thread(self)

    def run(self):
        '''
        Executes the 'EluteF18'
        run thread and the EluteF18
        object is passed into the
        EluteF18Thread.
        '''
        self.thread.start()

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

        self.elute.component_status = "Starting the EluteF18 run()"

        self.elute.component_status = "Adjusting pressure"

        self.elute.component_status = "Setting Pressure Regulator 1 to 0"
        self.elute.system.pressure_regulators[0].set_pressure(
                self.elute.elute_pressure)
        time.sleep(2)

        # TODO Move reactor to ELUTEF18
        # Check if we already at the correct position
        # if: reactor position is in the EluteF18 position
        #   Check that the reactor is either up or down
        #   If all true, then we are in position
        # Else, we need to setup for the EluteF18 op
        # else:
        #   needs_pressure_restore = False
        #   if: reactor position is in either one of the REACT positions
        #       if: reactor is up
        #           self.elute.system.pressure_regulators[1].set_pressure(30)
        #           needs_pressure_restore = True
        #
        #   self.elute.system.reactors[self.elute.reactor].lower() - Move Reactor down
        #   Enable reactor robot
        #
        #   if needs_pressure_restore:
        #       self.add.system.pressure_regulators[1].set_pressure(60)
        #
        #   Move reactor to the EluteF18 position
        #   self.elute.system.reactors[self.elute.system.reactors].lift()
        #   #Moves reactor up/raise reactor
        #   Disable the reactor robot

        self.elute.component_status = "Picking up vial"

        for stopcock in self.elute.system.reactors[self.elute.reactor].stopcocks:
            self.elute.component_status = "Setting reactor %d " \
                    "stopcock %d to CW" % \
                    (self.elute.system.reactors[self.elute.reactor].conf['id'] + 1,
                            stopcock.id_)
            stopcock.turn_clockwise()
            self.elute.component_status = "Setting reactor %d " \
                        "stopcock %d to CW once again" \
                       % (self.elute.system.reactors[self.elute.reactor]. \
                       conf['id'] + 1,
                               stopcock.id_)
            stopcock.turn_clockwise()

        if not self.elute.system.reagent_robot.gripper.is_open:
            self.elute.component_status = "Opening gripper arm"
            self.elute.system.reagent_robot.gripper.open()
        else:
            self.elute.component_status = "Checked gripper arm, " \
                    "gripper was already open"

        if not self.elute.system.reagent_robot.gripper.is_up:
            self.elute.component_status = "Setting gripper up"
            self.elute.system.reagent_robot.gripper.lift()
        else:
            self.elute.component_status = "Checked gripper up, " \
                    "gripper was already up"

        if not self.elute.system.reagent_robot.gas_transfer.is_up:
            self.elute.component_status = "Setting gas transfer up"
            self.elute.system.reagent_robot.gas_transfer.lift()
        else:
            self.elute.component_status = "Checked if gas transfer " \
                    "was up, gas transfer was already up"

        # TODO Check if reagent robot is enabled?
        # TODO Move reagent robot to reagent position
        # Pick up the vial
        has_vial = False
        try_count = 0
        while not has_vial:
            try_count += 1
            self.elute.component_status = "Setting gripper down"
            self.elute.system.reagent_robot.gripper.lower()

            self.elute.component_status = "Closing gripper arm"
            self.elute.system.reagent_robot.gripper.close()

            self.elute.component_status = "Setting gripper up"
            self.elute.system.reagent_robot.gripper.lift()

            if self.elute.system.reagent_robot.gripper.is_closed:
                self.elute.component_status = "Successfully picked " \
                        "up the reagent vial"
                has_vial = True
            elif try_count <= 3:
                self.elute.component_status = "Failed to pick up " \
                        "reagent vial, attempt %d" \
                        % try_count
                self.elute.component_status = "Opening gripper arm"
                self.elute.system.reagent_robot.gripper.open()
            else:
                self.elute.component_status = "Failed to pick up " \
                        "reagent vial after 3 attempts, " \
                        "raising error"
                self._is_complete.set()
                return

        # TODO Move reagent robot to Elute position on self.elute.reactor

        self.elute.component_status = "Setting gas transfer down"
        self.elute.system.reagent_robot.gripper.lower()

        self.elute.component_status = "Setting gas transfer valve on"
        self.elute.system.reagent_robot.gas_transfer.start_transfer()

        self.elute.component_status = "Setting gripper down"
        self.elute.system.reagent_robot.gripper.lower()


        self.elute.component_status = "Eluting"

        self.elute.component_status = "Setting pressure regualtor 1 " \
                "to elute at %f psi with a ramptime of 5 seconds" \
                % self.elute.elute_pressure
        # Setting the P.R. 1 with a ramptime of 5 (from old codebase)
        self.elute.system.pressure_regulators[0].set_pressure(
                self.elute.elute_pressure, 5)

        self.elute.component_status = "Eluting reagent, waiting for completion"
        starttimer = time.time()
        while (starttimer + self.elute.elute_time > time.time()):
            pass
        print "time leftover: %s" % \
                (time.time() - starttimer + self.elute.elute_time)
        time.sleep(3)

        self.elute.component_status = "Returning vial"

        # Check if gripper is closed and down
        if (not self.elute.system.reagent_robot.gripper.is_closed
                or not self.elute.system.reagent_robot.gripper.is_down):
            self.component_status = "Gripper is either not closed or " \
                    "not down, raising error"
            self._is_complete.set()
            return

        # Remove the vial
        has_vial_up = False
        try_count = 0
        while not has_vial_up:
            try_count += 1
            self.elute.component_status = "Setting gripper up"
            self.elute.system.reagent_robot.gripper.lift()

            if self.elute.system.reagent_robot.gripper.is_closed:
                self.elute.component_status = "Successfully picked " \
                        "up the reagent vial"
                has_vial_up = True
            elif try_count <= 10:
                self.elute.component_status = "Failed to remove " \
                        "reagent vial, attempt %s " \
                        % try_count

                self.elute.component_status = "Opening gripper arm"
                self.elute.system.reagent_robot.gripper.open()

                self.elute.component_status = "Setting gripper down"
                self.elute.system.reagent_robot.gripper.lower()

                self.elute.component_status = "Closing gripper arm"
                self.elute.system.reagent_robot.gripper.close()
            else:
                self.elute.component_status = "Failed to remove " \
                        "reagent vial after 10 attempts, " \
                        "raising error"
                self._is_complete.set()
                return

        self.elute.component_status = "Setting gas transfer valve off"
        self.elute.system.reagent_robot.gas_transfer.stop_transfer()

        self.elute.component_status = "Setting gas transfer up"
        self.elute.system.reagent_robot.gas_transfer.lift()


        self.elute.component_status = "Moving reagent back to reagent position"
        # TODO Move reagent robot back to the reagent position in self.elute.reactor


        self.elute.component_status = "Setting gripper down "
        self.elute.system.reagent_robot.gripper.lower()

        self.elute.component_status = "Opening gripper arm"
        self.elute.system.reagent_robot.gripper.open()

        self.elute.component_status = "Setting gripper up"
        self.elute.system.reagent_robot.gripper.lift()

        self.elute.component_status = "Homing reagent robot"
        # TODO Home reagent robot

        self.elute.component_status = "Sucessfully finished " \
                "running EluteF18 operation"
        self._is_complete.set()

if __name__ == '__main__':
    a = {"componenttype": "ELUTEF18", "sequenceid": 14,
            "elutetime": 10, "reactor": 1,
            "validationerror": True,
            "reagentvalidation": "type=enum-reagent; values=; required=true",
            "elutetimevalidation": "type=number; min=0; max=7200; required=true",
            "note": "", "reagent": {},
            "elutepressurevalidation": "type=number; min=0; max=25",
            "reactorvalidation": "type=enum-number; values=1,2,3; required=true",
            "elutepressure": 5, "type": "component", "id": 110}
    class db(object):
        details = a

    el = EluteF18(db)
    from IPython import embed
    embed()


