#!/usr/bin/env python
""" Prompt Component
"""
from component import Component
# import the component threading module
from componentthread import ComponentThread

class Prompt(Component):
    """ Prompt """
    def __init__(self, dbcomp):
        super(Prompt, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.message = dbcomp.details['message']
        self.validationerror = dbcomp.details['validationerror']
        self.note = dbcomp.details['note']
        # Set a thread
        self.thread = PromptThread(self)

    def run:
        '''
        Executes the 'PROMPT' run thread
        and the Prompt object is passed
        into the PromptThread
        '''
        self.thread.start()

class PromptThread(ComponentThread):
    '''
    Main Prompt Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self, prompt_component):
        '''
        Expects a Prompt object to be
        passed in. Contructs a new PromptThread
        '''
        super(PromptThread, self).__init__()
        self.prompt = prompt_component

    def run(self):
        '''
        Begins the run process of the
        Prompt unit operation.
        Function takes an Prompt class object
        which shall contain the details of
        the unit op's execution.
        '''
        self._is_complete.clear()

        self.prompt.component_status = "Starting the Prompt run()"

        self.prompt.component_status = "Waiting for user input"
        # TODO wait for user input

        self.prompt.component_status = "Successfully finished Prompt operation"
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

    a = Prompt(db)
    from IPython import embed
    embed()


