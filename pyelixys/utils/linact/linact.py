#/usr/bin/env python

import os
import time

import ctypes
from ctypes import cdll

from functools import wraps

import serial
from serial import SerialException
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-p", "--port", type=str,
                        help="com port to use to"
                        "send and receive command")

args = parser.parse_args()



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

    def get_rx_length(self):
        return linactlib.LinActBuf_rxlen(self.obj)

    def get_expected_rx_length(self):
        return linactlib.LinActBuf_expected_rxlen(self.obj)

    def get_data_length(self):
        return linactlib.LinActBuf_rxdatalen(self.obj)

    def push_rx(self,c):
        if c >= 0 and c < 256:
            linactlib.LinActBuf_pushRx(self.obj, c)

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

    def rxdata(self):
        f = linactlib.LinActBuf_rxbuf
        datatype = ctypes.c_char * self.get_rx_length()
        dataptr = f(self.obj)
        return datatype.from_address(dataptr).raw

    def payload(self):
        f = linactlib.LinActBuf_payload
        datatype = ctypes.c_char * self.get_data_length()
        dataptr = f(self.obj)
        return datatype.from_address(dataptr).raw

    def __str__(self):
        return str(self.data(), self.rxdata())

    def __repr__(self):
        tx,rx = self.data(), self.rxdata()
        return "TX:%s\r\nRX:%s" %  (tx.encode('hex').upper(), rx.encode('hex').upper())


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

    def startQuery(self):
        buf = linactlib.LinAct_axisStartQuery(self.obj, self.devid)
        buf = LinearActuatorBuffer(buf)
        return buf

    def pauseQuery(self):
        buf = linactlib.LinAct_axisPauseQuery(self.obj, self.devid)
        buf = LinearActuatorBuffer(buf)
        return buf

    def brakeReleaseQuery(self):
        buf = linactlib.LinAct_axisBrakeReleaseQuery(self.obj, self.devid)
        buf = LinearActuatorBuffer(buf)
        return buf

    def homeQuery(self):
        buf = linactlib.LinAct_axisHomeQuery(self.obj, self.devid)
        buf = LinearActuatorBuffer(buf)
        return buf

    def turnOnQuery(self):
        buf = linactlib.LinAct_axisTurnOnQuery(self.obj, self.devid)
        buf = LinearActuatorBuffer(buf)
        return buf

    def resetQuery(self):
        buf = linactlib.LinAct_axisResetQuery(self.obj, self.devid)
        buf = LinearActuatorBuffer(buf)
        return buf

    def posQuery(self):
        buf = linactlib.LinAct_axisPosGetQuery(self.obj, self.devid)
        buf = LinearActuatorBuffer(buf)
        return buf

    def setPosQuery(self, pos):
        pos = int(pos * 100.0)
        buf = linactlib.LinAct_axisPosSetQuery(self.obj, self.devid, pos)
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

    def gatewayStartQuery(self):
        buf = linactlib.LinAct_gatewayStartQuery(self.obj)
        buf = LinearActuatorBuffer(buf)
        return buf

    def pushRx(self, c):
        if c >= 0 and c < 256:
            linactlib.LinAct_pushRx(c);

    def loadRxMsg(self, s):
        for c in s:
            self.buf.push_rx(ord(c))

    def check_crc_error(self):
        f = linactlib.LinAct_checkcrc
        val = f(self.obj)
        return val

    def check_crc(self):
        if self.check_crc_error() > 0:
            return True
        else:
            return False


    def getBuf(self):
        buf = linactlib.LinAct_getBuffer(self.obj)
        return LinearActuatorBuffer(buf)

    buf = property(getBuf)

    def getPos(self):
        self.posQuery()
        f = linactlib.LinAct_getPosition
        f.restype = ctypes.c_float
        return f(self.obj)


class LinearActuatorCom(LinearActuator):
    """ Linear Actuator Communicator """
    def __init__(self, devid, port, baudrate=230400, timeout=1.0):
        """ <Constructor> """
        self.com = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        super(LinearActuatorCom, self).__init__(devid)

    def send(self):
        buf = self.getBuf()
        self.com.write(buf.data())

    def receive(self):
        buf = self.getBuf()
        resplen = buf.get_expected_rx_length()
        resp = self.com.read(resplen)
        self.loadRxMsg(resp)
        if self.check_crc():
            print "Received valid response"
            return True
        else:
            print "Received invalid response"
            return False
        print buf

    def startGateway(self):
        self.gatewayStartQuery()
        self.send()
        self.receive()


    def home(self):
        self.homeQuery()
        self.send()
        self.receive()

    def start(self):
        self.startQuery()
        self.send()
        self.receive()

    def pause(self):
        self.pauseQuery()
        self.send()
        self.receive()

    def brakeRelease(self):
        self.brakeReleaseQuery()
        self.send()
        self.receive()

    def reset(self):
        self.resetQuery()
        self.send()
        self.receive()
        pass

    def move(self, posmm):
        self.setPosQuery(posmm)
        self.send()
        self.receive()

    def getPos(self):
        self.posQuery()
        self.send()
        self.receive()
        f = linactlib.LinAct_getPosition
        f.restype = ctypes.c_float
        return f(self.obj)

    def getStatus(self):
        pass





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

    #pgzR 168
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
    print "GWSTART:%s" % repr(la.gatewayStartQuery())
    print "GWSTATUS:%s" % repr(la.gatewayStatusQuery())
    print "START:%s" % repr(la.startQuery())
    print "STATUS:%s" % repr(la.statusQuery())
    print "HOME:%s" % repr(la.homeQuery())
    print "RESET:%s" % repr(la.resetQuery())
    print "BRAKERELEASE:%s" % repr(la.brakeReleaseQuery())
    print "QUERYPOS:%s" % repr(la.posQuery())
    print "QUERYSETPOS:%s" % repr(la.setPosQuery(100))


    print "GWSTATUS:%s" % repr(la.statusQuery())
    example_status_msg = "\x3f\x03\x02\x40\x11\x60\x4d"

    la.loadRxMsg(example_status_msg)

    if la.check_crc():
        print "CRC OK: ERR %d" % la.check_crc_error()
    else:
        print "CRC FAIL: ERR %d" % la.check_crc_error()

    la.buf.reset();
    la.posQuery();
    example_status_msg = "\x3f\x03\x04\x38\xa5\x00\x00\x38\xb1"
    la.loadRxMsg(example_status_msg)

    print "Pos %0.2f" % la.getPos()

    la.buf.reset();
    la.posQuery();
    example_status_msg = "\x3f\x03\x04\x38\xa5\x00\x00\x38\xb3"
    la.loadRxMsg(example_status_msg)

    print "Pos %0.2f" % la.getPos()

    la.buf.reset();
    la.posQuery();
    example_status_msg = "\x3f\x03\x04\x38\xa5\x80\x00\x59\x73"
    la.loadRxMsg(example_status_msg)

    print "Pos %0.2f" % la.getPos()

    if args.port:
        try:
            linact = LinearActuatorCom(0, args.port)
        except SerialException as e:
            print "Could not open com port: %s" % str(e)


    embed()
