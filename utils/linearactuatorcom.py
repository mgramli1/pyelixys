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

"""

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
    return CRC


