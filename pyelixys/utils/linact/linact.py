#/usr/bin/env python

import os
import time

import ctypes
from ctypes import cdll

if not os.name == 'nt':
    print "Windows support only at the moment"
    sys.exit(1)

linactlib = cdll.LoadLibrary("./build/linact.dll")

class LinearActuatorBuffer(object):
    """ Interface to in C++ library """

    def __init__(self):
        self.obj = linactlib.LinActBuf_new()

    def push(self, c):
        if c >= 0 and c < 256:
            linactlib.LinActBuf_push(self.obj, c)

    def reset(self):
        linactlib.LinActBuf_reset(self.obj)

    def get_length(self):
        return linactlib.LinActBuf_len(self.obj)

    def calc_crc(self):
        linactlib.LinActBuf_calc_crc(self.obj)

    def as_str(self):
        f = linactlib.LinActBuf_as_str
        length = self.get_length() * 2
        f.restype = ctypes.c_char_p
        return f(self.obj)

if __name__=='__main__':
    la = LinearActuatorBuffer()
    from IPython import embed
    embed()
