#!/usr/bin/env python
""" Utility decorators for elixys system """
from pyelixys.elixysexceptions import ElixysHALError
from functools import wraps

def retry_routine(retry_count=3):
    """ Decorate fxn and retry """
    def wrapper(fxn):
        @wraps(fxn)
        def wrapped_f(*args, **kwargs):
            for i in range(retry_count):
                try:
                    return fxn(*args, **kwargs)
                except ElixysHALError as e:
                    exp = e
            raise exp
        return wrapped_f
    return wrapper


