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

"""
import struct

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
print 'Gateway status query: %s' % gwstatus.encode('hex')

# Page 155
axis0pos = "\x3f\x03\xf7\x08\x00\x02"
axis0pos = calc_crc(axis0pos)
print 'Query Axis 0 pos: %s' % axis0pos.encode('hex')

# Page 158
axis1alarm = "\x3f\x03\xf7\x12\x00\x01"
axis1alarm = calc_crc(axis1alarm)

print 'Query Axis 1 alarm: %s' % axis1alarm.encode("hex")

# Page
resetcmd = "\x3f\x06\xf6\x0b\x00\x08"
resetcmd = calc_crc(resetcmd)

print 'Reset command: %s' % resetcmd.encode("hex")


# Page 184
axis1dir = '\x3f\x10\xf6\x0c\x00\x08\x10\x3a\x98\x00' \
            '\x00\x00\x0a\x00\x00\x00\x32\x00\x1e\x00' \
            '\x00\x00\x11'

axis1dir = calc_crc(axis1dir)


print "Axis 1 Direct mode: %s" % axis1dir.encode("hex")


# Page 166
homeretcmd = "\x3f\x06\xf6\x0b\x00\x12"
homeretcmd = calc_crc(homeretcmd)

print "Home return command: %s" % homeretcmd.encode("hex")

# Page 167
startcmd = "\x3f\x06\xf6\x0b\x00\x11"
startcmd = calc_crc(startcmd)

print "Start command: %s" % startcmd.encode("hex")


pausecmd = "\x3f\x06\xf6\x0b\x00\x14"
pausecmd = calc_crc(pausecmd)

print "Pause command: %s" % pausecmd.encode("hex")


