#!/usr/bin/env python
""" Cassette Component
"""
from component import Component
# import the component threading module
from componentthread import ComponentThread

class Cassette(Component):
    """ Cassette Component
    here we store the
    details for the reagents installed in the
    cassette
    TODO: Store the reagent from the dbcomp.details!
    """
    def __init__(self, dbcomp):
        super(Cassette, self).__init__(dbcomp)
        # Set a thread
        self.thread = CassetteThread(self)
        self.details = dbcomp.details

    def run(self):
        """ Do nothing """

        # TODO We *might* want to wait for user input here? Or not
        return

class CassetteThread(ComponentThread):
    '''
    Main Add Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self, cassete):
        super(CassetteThread, self).__init__()
        self.cass = cassete

    def run(self):
        self._is_complete.clear()
        self.cass.run()
        self._is_complete.set()


if __name__ == '__main__':

    details = {}

    class db:
        details=details

    cass = Cassette(db)

    from IPython import embed
    embed()
