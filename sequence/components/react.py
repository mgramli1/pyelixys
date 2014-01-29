#!/usr/bin/env python
""" React Component
"""
from pyelixys.sequence.components.component import Component
# import the component threading module
from componentthread import ComponentThread

class React(Component):
    """ React """
    def __init__(self, dbcomp):
        super(React, self).__init__(dbcomp)

        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.reactor = dbcomp.details['reactor']
        self.position = dbcomp.details['position']
        self.cooling_delay = dbcomp.details['coolingdelay']
        self.stir_speed = dbcomp.details['stirspeed']
        self.duration = dbcomp.details['duration']
        self.reaction_temperature = dbcomp.details['reactiontemperature']
        self.final_temperature = dbcomp.details['finaltemperature']
        self.stop_at_temperature = dbcomp.details['stopattemperature']
        self.validation_error = dbcomp.details['validationerror']
        self.note = dbcomp.details['note']
        # Set a thread
        self.thread = ReactThread()

class ReactThread(ComponentThread):
    '''
    Main React Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self):
        super(ReactThread, self).__init__()
