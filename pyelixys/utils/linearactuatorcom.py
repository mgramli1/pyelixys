#!/usr/bin/env python
""" This file can be used to communicate
with the IAI linear actuators over an RS485
communication bus.

The documentation for the ROBONet controller
is in DOC ROBONET(ME0208-13A-A).pdf

Discussion of the serial protocol begins
on page 141 section 3.9.2

Link with C code for crc calculation:
http://www.nongnu.org/avr-libc/user-manual/group__util__crc.html

Link with CRC explanation:
http://www.barrgroup.com/Embedded-Systems/How-To/CRC-Calculation-C-Code

Further details in:
Jack Crenshaw's "Implementing CRCs"
article in the January 1992
issue of Embedded Systems Programming

Page 70 - 71
The address map

Servo On
Home Ctrl
Send Position
Send Start Command

PC software edit the parameter


"""
import struct
import serial
import time

## Packet Description

# Header T1-T2-T3-T4 (silent interval)
    # 3.5 characters or more
# Address 8-bit \x3F (3FH)
# Function 8-bit
    # Read holding register \x03
    # Preset single register \x06
    # Preset multiple resgister \x10
# Data N x 8-bit
    # variable length and may be ommitted
# Error check 16-bit CRC
# Trailer T1-T2-T3-T4 (silent interval)
    # 3.5 characters or more

def crc_update(crc, a):
    """ For a character calculate crc """

    crc ^= ord(a)
    for i in range(8):
        if crc & 1:
            crc = (crc >> 1) ^ 0xA001
        else:
            crc = crc >> 1
    return crc

def calc_crc(values):
    CRC = 0xFFFF
    for value in values:
        CRC = crc_update(CRC, value)
    crcbytes = struct.pack('BB',
            CRC & 0xFF,
            (CRC & 0xFF00) >> 8)
    return values + crcbytes

# Page 152
gwstatus = "\x3f\x03\xf7\x00\x00\x02"
gwstatus = calc_crc(gwstatus)
print 'Gateway status query: %s' % gwstatus.encode('hex').upper()

# Page 155
axis0pos = "\x3f\x03\xf7\x08\x00\x02"
axis0pos = calc_crc(axis0pos)
print 'Query Axis 0 pos: %s' % axis0pos.encode('hex').upper()

# Page 158
axis1alarm = "\x3f\x03\xf7\x12\x00\x01"
axis1alarm = calc_crc(axis1alarm)

print 'Query Axis 1 alarm: %s' % axis1alarm.encode("hex").upper()

# Page
resetcmd0 = "\x3f\x06\xf6\x0b\x00\x08"
resetcmd0 = calc_crc(resetcmd0)

print 'Reset command axis 0: %s' % resetcmd0.encode("hex").upper()

resetcmd1 = "\x3f\x06\xf6\x0f\x00\x08"
resetcmd1 = calc_crc(resetcmd1)

print 'Reset command axis 1: %s' % resetcmd1.encode("hex").upper()


# Page 184
axis1dir = '\x3f\x10\xf6\x0c\x00\x08\x10\x3a\x98\x00' \
            '\x00\x00\x0a\x00\x00\x00\x32\x00\x1e\x00' \
            '\x00\x00\x11'

axis1dir = calc_crc(axis1dir)


print "Axis 1 Direct mode: %s" % axis1dir.encode("hex").upper()


# Page 166
homeretcmd0 = "\x3f\x06\xf6\x0b\x00\x12"
homeretcmd0 = calc_crc(homeretcmd0)

print "Home return command: %s" % homeretcmd0.encode("hex").upper()

# Page 167
startcmd0 = "\x3f\x06\xf6\x0b\x00\x11"
startcmd0 = calc_crc(startcmd0)

print "Start command: %s" % startcmd0.encode("hex").upper()


# Page 168
pausecmd = "\x3f\x06\xf6\x0b\x00\x14"
pausecmd = calc_crc(pausecmd)

print "Pause command: %s" % pausecmd.encode("hex").upper()

# Page 184
axis0dir = '\x3f\x10\xf6\x08\x00\x08\x10\x3a\x98\x00' \
            '\x00\x00\x0a\x00\x00\x00\x32\x00\x1e\x00' \
            '\x00\x00\x11'

axis0dir = calc_crc(axis0dir)


print "Axis 0 Direct mode: %s" % axis0dir.encode("hex").upper()

# page 165
axis0son = '\x3f\x06\xf6\x0b\x00\x10'
axis0son = calc_crc(axis0son)
print "Axis 0 Servo on: %s" % axis0son.encode("hex").upper()

# Page 158
axis2alarm = "\x3f\x03\xf7\x13\x00\x01"
axis2alarm = calc_crc(axis2alarm)
print 'Query Axis 2 alarm: %s' % axis2alarm.encode("hex").upper()


# Always turn on
alwayson = "\x3f\x06\xf6\x00\x80\x00"
alwayson = calc_crc(alwayson)
print "Always run this: %s" % alwayson.encode("hex").upper()

# Brake release
axis0brake = '\x3f\x06\xf6\x0b\x80\x00'
axis0brake = calc_crc(axis0brake)
print "Axis 0 brake: %s" % axis0brake.encode('hex').upper()


def move0(posmm):
    pos = [0,0,0,0]
    axis0setpos = "\x3f\x10\xf6\x0c\x00\x02\x04"
    pos[1] = posmm & 0xFF
    pos[0] = (posmm & 0xFF00) >> 8
    pos[3] = (posmm & 0xFF0000) >> 16
    pos[2] = (posmm & 0xFF000000) >> 24

    for p in pos:
        axis0setpos += chr(p)

    axis0setpos = calc_crc(axis0setpos)
    return axis0setpos



class IAI(object):
    def __init__(self):
        self.s = serial.Serial("COM5",
                                baudrate=230400,
                                timeout=0.5)
    def turnon(self):
        self.s.write(alwayson)
        time.sleep(0.1)
        v = self.s.readline().encode('hex').upper()
        print v

    def start0(self):
        self.s.write(startcmd0)
        time.sleep(0.1)
        v = self.s.readline().encode('hex').upper()
        print v

    def home0(self):
        self.s.write(homeretcmd0)
        time.sleep(0.1)
        v = self.s.readline().encode('hex').upper()
        print v

    def reset0(self):
        self.s.write(resetcmd0)
        time.sleep(0.1)
        v = self.s.readline().encode('hex').upper()
        print v

    def move0(self, posmm):
        pos = [0,0,0,0]
        axis0setpos = "\x3f\x10\xf6\x0c\x00\x02\x04"
        pos[1] = posmm & 0xFF
        pos[0] = (posmm & 0xFF00) >> 8
        pos[3] = (posmm & 0xFF0000) >> 16
        pos[2] = (posmm & 0xFF000000) >> 24

        for p in pos:
            axis0setpos += chr(p)

        axis0setpos = calc_crc(axis0setpos)

        self.s.write(axis0setpos)
        time.sleep(0.1)
        v = self.s.readline().encode('hex').upper()
        print v


