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
        self.component_id = dbcomp.details['componentid']
        self.sequence_id = dbcomp.details['sequenceid']
        self.comment = dbcomp.details['comment']
        self.broadcast_flag = dbcomp.details['broadcastflag']
        self.note = dbcomp.details['note']

    def run(self):
        """ Wait for user input.
        TODO user input is not implemented
        You would use an Event here
        """
        self.comment.component_status = self.comment
        # TODO Wait for user input

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
        self.comment.run()
        self._is_complete.set()

if __name__ == "__main__":
    details = {}
    details['componentid'] = 0
    details['sequenceid'] = 0
    details['comment'] = "This is comment"
    details['broadcastflag'] = 0
    details['note'] = "This a note about this comment"

    class db:
        details = details

    cm = Comment(db)

    from IPython import embed
    embed()

