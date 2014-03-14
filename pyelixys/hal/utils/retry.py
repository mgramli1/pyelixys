#!/usr/bin/env python
""" Utility decorators for elixys system """
from pyelixys.elixysexceptions import ElixysHALError
from functools import wraps, update_wrapper
from decorator import decorator



def retry_routine(retry_count=3):
    @decorator
    def retry(f, *args, **kwargs):
        for i in range(retry_count):
            try:
                return f(*args, **kwargs)
            except ElixysHALError as e:
                exp = e
        raise exp
    return retry
