#!/usr/bin/env python
""" Evaporate Component
"""
from pyelixys.sequence.components.component import Component
# import the component threading module
from componentthread import ComponentThread

class Evaporate(Component):
    """ Evaporate """
    def __init__(self, dbcomp):
        super(Evaporate, self).__init__(dbcomp)
        
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.final_temperature = dbcomp.details['finaltemperature']
        self.stop_temperature = dbcomp.details['stopattemperature']
        self.evaporation_temperature = dbcomp.details['evaporationtemperature']
        self.evaporation_pressure = dbcomp.details['evaporationpressure']
        self.duration = dbcomp.details['duration']
        self.reactor = dbcomp.details['reactor']
        self.validation_error = dbcomp.details['validationerror']
        self.stir_speed = dbcomp.details['stirspeed']
        self.note = dbcomp.details['note']
        # Set a thread
        self.thread = EvaporateThread()

class EvaporateThread(ComponentThread):
    '''
    Main Evaporate Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self):
        super(EvaporateThread, self).__init__()
