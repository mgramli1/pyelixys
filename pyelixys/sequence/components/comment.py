#!/usr/bin/env python
""" Comment Component
"""
from component import Component
# import the component threading module
from componentthread import ComponentThread

class Comment(Component):
    """ Comment """
    def __init__(self, dbcomp):
        super(Comment, self).__init__(dbcomp)
        self.component_id = dbcomp.details['id']
        self.sequence_id = dbcomp.details['sequenceid']
        self.comment = dbcomp.details['comment']
        self.broadcast_flag = dbcomp.details['broadcastflag']
        self.validation_error = dbcomp.details['validationerror']
        self.note = dbcomp.details['note']

        # Set a thread
        self.thread = CommentThread(self)

    def run(self):
        self.thread.start()

class CommentThread(ComponentThread):
    '''
    Main Comment Thread point
    Inherits from ComponentThread which
    inherits from Thread.
    '''
    def __init__(self, comment):
        super(CommentThread, self).__init__()
        self.comment = comment

    def run(self):
        '''
        Begins the run process of the
        Comment unit operation as a
        thread.
        '''

        self._is_complete.clear()
        self.comment.component_status = "Starting the Comment run()"

        # Comment message would be broadcasted via SMS(Twilio) & Email here

        self.comment.component_status = "Sucessfully finished running Initialize operation"
        self._is_complete.set()


