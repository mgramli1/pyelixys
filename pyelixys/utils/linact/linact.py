#/usr/bin/env python

import os
import time

import ctypes
from ctypes import cdll

if not os.name == 'nt':
    print "Windows support only at the moment"
    sys.exit(1)

linactlib = cdll.LoadLibrary("./build/linact.dll")
