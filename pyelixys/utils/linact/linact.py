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

    def __init__(self, obj = None):
        if obj is None:
            self.obj = linactlib.LinActBuf_new()
        else:
            self.obj = obj

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



    def readRegsister(self, reg, count):
        self.reset()
        f = linactlib.LinActBuf_readRegsister

        f.argtypes=[ctypes.c_void_p,
                    ctypes.c_ushort,
                    ctypes.c_ushort]

        f(self.obj, reg, count)


    def writeRegister(self, reg, value):
        self.reset()
        f = linactlib.LinActBuf_writeRegister
        f.argtypes=[ctypes.c_void_p,
                    ctypes.c_ushort,
                    ctypes.c_ushort]

        f(self.obj, reg, value)

    def writeMultiRegister(self, reg, data):
        self.reset()

        datalen = len(data)
        reglen = datalen / 2
        f = linactlib.LinActBuf_writeMultiRegister
        f.argtypes = [ctypes.c_void_p,
                      ctypes.c_ushort,
                      ctypes.c_ushort,
                      ctypes.c_char_p,
                      ctypes.c_char]

        f(self.obj, reg, reglen, data, chr(len(data)))


    def data(self):
        f = linactlib.LinActBuf_buf
        datatype = ctypes.c_char * self.get_length()
        dataptr = f(self.obj)
        return datatype.from_address(dataptr).raw


    def __str__(self):
        return self.data()

    def __repr__(self):
        return str(self).encode('hex').upper()


class LinearActuator(object):

    def __init__(self, devid):
        self.devid = devid
        self.obj = linactlib.LinAct_new()


    def readAddr(self):
        f = linactlib.LinAct_axisReadAddr
        f.restype = ctypes.c_ushort
        return hex(f(self.obj, self.devid))

    def writeAddr(self):
        f = linactlib.LinAct_axisWriteAddr
        f.restype = ctypes.c_ushort
        return hex(f(self.obj, self.devid))

    def start(self):
        buf = linactlib.LinAct_axisStartQuery(self.obj, self.devid)
        buf = LinearActuatorBuffer(buf)
        return buf

    def pause(self):
        buf = linactlib.LinAct_axisPauseQuery(self.obj, self.devid)
        buf = LinearActuatorBuffer(buf)
        return buf

    def brakeRelease(self):
        buf = linactlib.LinAct_axisBrakeReleaseQuery(self.obj, self.devid)
        buf = LinearActuatorBuffer(buf)
        return buf

    def home(self):
        buf = linactlib.LinAct_axisHomeQuery(self.obj, self.devid)
        buf = LinearActuatorBuffer(buf)
        return buf

    def reset(self):
        buf = linactlib.LinAct_axisResetQuery(self.obj, self.devid)
        buf = LinearActuatorBuffer(buf)
        return buf

    def posQuery(self):
        buf = linactlib.LinAct_axisPosGetQuery(self.obj, self.devid)
        buf = LinearActuatorBuffer(buf)
        return buf

    def statusQuery(self):
        buf = linactlib.LinAct_axisStatusQuery(self.obj, self.devid)
        buf = LinearActuatorBuffer(buf)
        return buf

    def gatewayStatusQuery(self):
        buf = linactlib.LinAct_gatewayStatusQueury(self.obj)
        buf = LinearActuatorBuffer(buf)
        return buf

    def gatewayStart(self):
        buf = linactlib.LinAct_gatewayStartQuery(self.obj)
        buf = LinearActuatorBuffer(buf)
        return buf


if __name__=='__main__':
    lab = LinearActuatorBuffer()
    from IPython import embed

    # page 160
    axis0statusreg = 0xF70B

    lab.readRegsister(axis0statusreg, 1)

    print "Page 160: Axis 0 Status Query %s" % lab.as_str()

    # page 163
    gwcntrlreg = 0xF600
    newdata = 0x8000

    lab.writeRegister(gwcntrlreg, newdata)

    print "Page 163: GW Ctrl Write  bit 15 %s" % lab.as_str()

    #pg 158
    axis1alarmreg = 0xF712
    lab.readRegsister(axis1alarmreg, 1)

    print "Page 158: Monitor Axis 1 Alarm %s" % lab.as_str()

    #pg 166
    axis0ctrlreg = 0xF60B
    lab.writeRegister(axis0ctrlreg, 0x0012)

    print "Page 166: Send Home Return Command %s" % lab.as_str()

    #pg 167
    lab.writeRegister(axis0ctrlreg, 0x0011)
    print "Page 167: Send Start Command %s" % lab.as_str()

    #pg 168
    lab.writeRegister(axis0ctrlreg, 0x0014)
    print "Page 168: Send Pause Command %s" % lab.as_str()

    #pg 169
    lab.writeRegister(axis0ctrlreg, 0x0008)
    print "Page 169: Send Reset Command %s" % lab.as_str()

    #pg 177
    lab.writeRegister(axis0ctrlreg, 0x8000)
    print "Page 177: Send Brake Release %s" % lab.as_str()

    #pg 185
    axis0posreg = 0xF60C
    lab.writeMultiRegister(axis0posreg, "\x03\xe8\x00\x00")

    print "Page 185: Send Pos 10.00mm Axis 0 %s" % lab.as_str()

    la = LinearActuator(0)
    print "GWSTART:%s" % repr(la.gatewayStart())
    print "GWSTATUS:%s" % repr(la.gatewayStatusQuery())
    print "START:%s" % repr(la.start())
    print "STATUS:%s" % repr(la.statusQuery())
    print "HOME:%s" % repr(la.home())
    print "RESET:%s" % repr(la.reset())
    print "BRAKERELEASE:%s" % repr(la.brakeRelease())
    print "QUERYPOS:%s" % repr(la.posQuery())


    embed()
