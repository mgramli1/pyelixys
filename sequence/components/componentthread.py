# Import threading capabilities
from threading import Thread

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

