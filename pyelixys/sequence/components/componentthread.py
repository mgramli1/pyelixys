# Import threading capabilities
from threading import Thread
from threading import Event

class ComponentThread(Thread):
    '''
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
        '''
        '''
        if not self._is_complete.isSet():
            return True

        self.join()
        return False

    def run(self):
        '''
        '''
        # Clear event
        self._is_complete.clear()
        # Set event
        self._is_complete.set()

        return



