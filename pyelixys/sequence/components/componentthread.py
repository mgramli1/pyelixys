# Import threading capabilities
from threading import Thread
from threading import Event

class ComponentThread(Thread):
    ''' All components have threads that allow them
    to run in the background.  All
    of these threads inherit from this class
    '''
    # Thread list to maintain the
    # number of threads created.
    component_threads = []
    def __init__(self):
        super(ComponentThread, self).__init__()
        # Creation of a new thread, add to list
        self.component_threads.append(self)
        self._is_complete = Event()

    def is_running(self):
        ''' Determine if we are running '''
        if not self._is_complete.isSet():
            return True

        self.join()
        return False

    def run(self):
        ''' Run the Component
        and let the developer know when it is
        complete.
        '''
        # Clear event
        self._is_complete.clear()
        # Set event
        self._is_complete.set()

        return



