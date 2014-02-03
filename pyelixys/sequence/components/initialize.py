#!/usr/bin/env python
""" Initialize Component
"""
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
        self.thread = InitializeThread()

class InitializeThread(ComponentThread):
    '''
    Main Initialize Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self):
        super(InitializeThread, self).__init__()
    
    def run(self, init):
        '''
        Begins the run process of the
        Init() unit operation.
        Function takes an Initialize class
        object.
        '''
        init.log.debug("Starting the Initialize run()")
        
        init.log.debug("Setting the gas transfer valve closed")
        # Set gas transfer valve OFF

        # For each reactor:
        for reactor in init.system.reactors:
            init.log.debug("Setting reactor "
                    + str(reactor) + " down")
            # Move reactor Down
            init.log.debug("Setting reactor "
                    + str(reactor)
                    + " stopcock to counterclockwise")
            # Set reactor stopcock to CCW 
            init.log.debug("Setting reactor "
                    + str(reactor)
                    + " stopcock to counterclockwise")
            # Set reactor stopcock to CCW
            init.log.debug("Setting reactor "
                    + str(reactor)
                    + " stopcock to clockwise")
            # Set stopcock to CW

        init.log.debug("Setting F18 Load Value closed")
        # Set the F18 Load Valve OFF
                
        init.log.debug("Setting cooling system off")
        # Set cooing system off
        init.log.debug("Setting vacuum system off")
        # Set vacuum system off

        # Set Heaters and stir motors off
        for reactor in init.system.reactors:
            init.log.debug("Setting reactor "
                    + str(reactor) 
                    + " heater off")
            # Set reactor's heater off
            init.log.debug("Setting reactor "
                    + str(reactor) 
                    + " stir motors off")
            # Set reactor's stir motor speed to zero/off

        init.log.debug("Setting pressure regulator 1 to 5? ")
        # Set pressure regulator 1
        init.log.debug("Setting pressure regulator 2 to 60?")
        # Set pressure regulator 2
        
        init.log.debug("Setting reagent robot gripper up")
        # Set reagent robot gripper up
        init.log.debug("Setting reagent robot gripper open")
        # Set reagent robot gripper open
        init.log.debug("Setting reagent robot gas transfer up")
        # Set reagent robot gas transfer up

        # Move reactors to down position & confirm down
        init.log.debug("Setting each reactor down")
        for reactor in init.system.reactors:
            init.log.debug("Setting reactor "
                    + str(reactor)
                    + " down")
        # Home all reactors, don't confirm
        init.log.debug("Homing all reactors")
        for reactor in init.system.reactors:
            init.log.debug("Homing reactor "
                    + str(reactor))
            # Move reactor to Home position

        # Home all reactors again, confirm they are Homed
        for reactor in init.system.reactor:
            init.log.debug("Homing reactor "
                    + str(reactor)
                    + " and confirming reactor is Homed ")
            # Move reactor to Home position & confirm

        # Move reactors to install position
        for reactor in init.system.reactor:
            init.log.debug("Moving reactor "
                    + str(reactor)
                    + " to the Install position")
            # Move reactor to Install position

        init.log.debug("Finished running Initialize")
