#!/usr/bin/env python
import sys
from pyelixys.hal.hwconf import config

class ElixysObject(object):
    """Parent object for all elixys systems
    All objects can therefore access the system
    config and status
    """
    sysconf = config

