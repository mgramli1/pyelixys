# UCLA EE202A - LPC1768 Programmer for Python
# November 27, 2010

#issues baudrate too slow --> missed messages

import sys
import time
from time import sleep
import serial
import getopt
import binascii
import struct

def hostPrint(msg):
    now = time.localtime(time.time())
    print time.strftime("%Y-%m-%d %H:%M:%S ", now) + msg

def hostFault(msg):
    hostPrint(msg)
    sys.exit(2)

### CLASS START ###
class flashlpc:
    RESET_STRING = "{~NESL~}"
    
    def __init__(self, port, crystalfreq,reset=False):
        #--- Initialize serial device
        self.sd = serial.Serial(port, baudrate=57600, timeout=1)
        
        #--- Eliminate any lingering data in input stream
        self.sd.flushInput()
        #--- Reset Chip ---#
        
        if reset:
            self.lpcReset()
        
        #--- Start sync sequence
        self.lpcSyncScript(crystalfreq)
        
        #--- Display device info
        self.lpcShowDevID()
        self.lpcShowBootloaderVer()
        self.lpcShowSerialNumber()
        
        #--- Unlock device for programming
        self.sd.write("U 23130\n")  #see page625 lpc1768 specs for details
        ret = self.sd.readline()
        if not ret:
            hostFault("ERROR: Unable to unlock device for programming. Timed out: %s" % ret)
        elif int(ret) != 0:
            hostFault("ERROR: Unable to unlock device for programming: %d" % int(ret))
        
        #--- CONSTANTS ---
        #LPC17xx series has uneven sector sizes. Below 64kb = sector size of 4, > 64kb is size of 32
        self.lpc1768_sectors = (4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,
                                32,32,32,32,32,32,32,32,32,32,32,32,32,32)
        self.lpc1768_prog_addr_base = 0x10002000    #arbitrary, just choose something in Local RAM for temporary storage
        self.lpc1768_mem_block_size = 4096
        #-----------------
    def lpcReset(self):
        hostPrint("Attempting RESET...")
        self.sd.write(self.RESET_STRING)
        time.sleep(.250)
        self.sd.flushInput()
    
    def lpcAutoReset(self):
        hostPrint("Auto RESET...")
        self.sd.write("G 0 T\r\n")
        self.sd.flushInput()
        
    def lpcSyncScript(self, crystalfreq):
        #--- Write "?" to start sync
        self.sd.write("?")
        ret = self.sd.readline()
        if ret != "Synchronized\r\n":
            hostFault("ERROR: Unable to sync. Sync message not detected")
        elif not ret:
            hostFault("ERROR: Unable to sync. Timed out at \'?\'")
        
        #--- Reply sync message
        self.sd.write("Synchronized\n") ### DEBUG: SHOULD BE "Synchronized\r\n"?
        ret = self.sd.readline()
        if ret != "Synchronized\n":
            hostFault("ERROR: Unable to sync. Sync message not detected")
        
        #--- Check for "OK\r\n"
        ret = self.sd.readline()
        if ret != "OK\r\n":
            hostFault("ERROR: Unable to sync. OK message not detected")
        
        #--- Set crystal frequency
        self.sd.write("%d\r\n" % crystalfreq)
        ret = self.sd.readline()
        if ret != ("%d\rOK\r\n" % crystalfreq):
            hostFault("ERROR: Unable to sync. Frequency OK message not detected")
        
        #--- Echo off
        self.sd.write("A 0\n")
        ret = self.sd.readline()
        ret = self.sd.readline()    
        return
        
    def lpcShowDevID(self):
        self.sd.write("J\n")
        ret = self.sd.readline()
        if ret != "0\r\n":
            hostFault("ERROR: Unable to read device ID")
        ret = self.sd.readline()
        hostPrint("Device ID = " + hex(int(ret)))
        return
        
    def lpcShowBootloaderVer(self):
        self.sd.write("K\n")
        ret = self.sd.readline()
        if ret != "0\r\n":
            hostFault("ERROR: Unable to read bootloader version")
        ret = str(int(self.sd.readline())) + "." + str(int(self.sd.readline()))
        hostPrint("Bootloader Ver = " + ret[::-1])
        return
        
    def lpcShowSerialNumber(self):
        self.sd.write("N\n")
        ret = self.sd.readline()
        if ret != "0\r\n":
            hostFault("ERROR: Unable to read serial number")
        ret = str(int(self.sd.readline())) + " " + str(int(self.sd.readline())) + " " + str(int(self.sd.readline())) + " " + str(int(self.sd.readline()))
        hostPrint("Serial Number = " + ret)
        return

    def lpcWriteDataToRam(self, addr_base, data):
        data_size = len(data)
        uuline_size = 45
        uublock_size = 900  #45 byte length x 20 lines
        
        cur_addr = addr_base
        for i in range(0, data_size, uublock_size):
            cur_block_size = uublock_size
            if (data_size - i) <= uublock_size:
                cur_block_size = data_size - i
            
            #--- Process individual blocks
            data_block = data[i : i + cur_block_size]
            data_block_size = len(data_block)
            
            #--- Set LPC1768 to receive block
            self.sd.write("W %d %d\n" % (cur_addr, data_block_size))
            ret = self.sd.readline()
            if not ret:
                hostFault("ERROR: Unable to write data to RAM. Timed out: %s" % ret)
            elif int(ret) != 0:
                hostFault("ERROR: Unable to write data to RAM: %d" % int(ret))      
            
            #--- Write uuencoded lines (20 lines of 45 bytes) for each block
            for j in range(0, data_block_size, uuline_size):
                cur_line_size = uuline_size
                if (data_block_size - j) <= uuline_size:
                    cur_line_size = data_block_size - j
                
                #uu.encode(img_file)
                uudata = binascii.b2a_uu(data_block[j:j+cur_line_size])
                self.sd.write(uudata)
            
            #--- Calculate and send string checksum
            datasum = 0
            for ch in data_block:
                datasum = datasum + ord(ch)
            self.sd.write("%d\n" % datasum)
            ret = self.sd.readline()
            #print "\'" + str(datasum) + "\'"
            if not ret:
                hostFault("Error in checksum for RAM write. Timed out: %s" % ret)
            if ret != "OK\r\n":
                hostFault("Error in checksum for RAM write: %s" % ret)

            #--- Move to next block
            cur_addr = cur_addr + cur_block_size
        return
    
    
    def lpcInsertImgChecksum(self, img):
        ### SEE: http://code.google.com/p/micropendousx/source/browse/trunk/MicropendousX/Vector_Checksum_Calculator.c
        checksum_vec = 7    #checksum_vector for lpc1768 is 7, according to OpenOCD flash source code
        vectable = struct.unpack("8i", img[0:32])   #little endian UTF-8 encoding

        #--- Sum up values over first 8 interrupt vectors
        checksum = 0
        for i in range(0, len(vectable)):
            if i != checksum_vec:
                checksum = checksum + vectable[i]
        
        #--- 2's complement operation for obtaining "0 - checksum"
        checksum = (2**32) - checksum % (2**32)

        #--- Repack image and add checksum vectors to beginning 32 bytes
        newimg = ''
        for i in range(0,8):
            if i == checksum_vec:
                newimg += struct.pack("<I", checksum)
            else:
                newimg += struct.pack("<I", vectable[i])

        #--- Append original image after checksum vectors
        newimg += img[32:]

        return newimg
    
    def lpcGetSector(self, addr):
        #--- Translates a base address to corresponding sector in flash mem
        sectors = self.lpc1768_sectors
        n_sectors = len(sectors)
        addr_base = 0
        
        for sect in range(0, n_sectors):
            if addr_base <= addr and addr < (addr_base + 1024 * sectors[sect]):
                return sect
            addr_base = addr_base + 1024 * sectors[sect]
        
        #--- If corresponding sector not found, return -1
        return -1
    
    
    def lpcEraseProgramSectors(self):
        sector_s = 0
        sector_e = len(self.lpc1768_sectors) - 1
        
        hostPrint("Erasing sectors %d to %d (max sectors %d)" % (sector_s, sector_e, len(self.lpc1768_sectors)))
        
        #--- Prepare sectors for modification
        self.sd.write("P %d %d\n" % (sector_s, sector_e))
        ret = self.sd.readline()
        if not ret:
            hostFault("ERROR: Unable to prepare sectors for programming. Timed out: %s" % ret)
        elif int(ret) != 0:
            hostFault("ERROR: Unable to prepare sectors for programming: %d" % int(ret))
        
        #--- Erase sectors
        self.sd.write("E %d %d\n" % (sector_s, sector_e))
        ret = self.sd.readline()
        if not ret:
            hostFault("ERROR: Unable to erase sectors. Timed out: %s" % ret)
        elif int(ret) != 0:
            hostFault("ERROR: Unable to erase sectors: %d" % int(ret))
        
        return
    
    
    def lpcProgramImageScript(self, img):
        hostPrint("Programming image...")
        
        #--- Defaults
        mem_base_addr = self.lpc1768_prog_addr_base
        mem_block_size = self.lpc1768_mem_block_size
        
        #--- Insert checksum into image
        ### call: insert img checksum ()
        img = self.lpcInsertImgChecksum(img)
        ### OUTPUT "inserted checksum ____" into image
        hostPrint("Inserted checksum for bootloader validation into image.")
        
        #--- Pad image with '0xFF' characters to a valid multiple of blocksize
        img_size = len(img)
        if (img_size % mem_block_size) != 0:
            pad_size = mem_block_size - (img_size % mem_block_size)
            pad_data = ''
            for i in range(0, pad_size):
                pad_data = pad_data + '\xff'
            img = img + pad_data
            img_size = img_size + pad_size
            ### OUTPUT "padding image with ___ bytes"
            hostPrint("Image size is irregular. Need to pad image by %d bytes" % pad_size)
        else:
            hostPrint("Image size is a valid multiple of block size. No padding needed")
        
        #--- Erase old program
        ### call: erase program sectors ()
        self.lpcEraseProgramSectors()
        
        #--- Write each block of entire image
        for i in range(0, img_size, mem_block_size):
            #- Calculate size of current block to write
            cur_block_size = mem_block_size
            if (img_size - i) <= mem_block_size:
                cur_block_size = img_size - i
            
            #- Copy current block to memory
            flash_addr_s = i
            flash_addr_e = flash_addr_s + cur_block_size
            
            hostPrint("Copying %d bytes to address 0x%x (current image block = %d ~ %d)" % (cur_block_size, mem_base_addr, flash_addr_s, flash_addr_e))
            self.lpcWriteDataToRam(mem_base_addr, img[flash_addr_s:flash_addr_e])
            
            #- Prepare flash sectors
            sector_s = self.lpcGetSector(flash_addr_s)
            sector_e = self.lpcGetSector(flash_addr_e)
            
            #print "P %d %d\n" % (sector_s, sector_e)   # DEBUG ###
            self.sd.write("P %d %d\n" % (sector_s, sector_e))
            ret = self.sd.readline()
            if not ret:
                hostFault("ERROR: Unable to prepare sectors for programming. Timed out: %s" % ret)
            elif int(ret) != 0:
                hostFault("ERROR: Unable to prepare sectors for programming: %d" % int(ret))
            
            #- Copy data from lpc1768 RAM to flash
            #print "C %d %d %d\n" % (flash_addr_s, mem_base_addr, cur_block_size)   # DEBUG ###
            self.sd.write("C %d %d %d\n" % (flash_addr_s, mem_base_addr, cur_block_size))
            ret = self.sd.readline()
            if not ret:
                hostFault("ERROR: Unable to program data from RAM to FLASH. Timed out: %s" % ret)
            elif int(ret) != 0:
                hostFault("ERROR: Unable to program data from RAM to FLASH: %d" % int(ret))
        
        hostPrint("Programming complete. Binary image successfully written and validated in flash memory")

### CLASS END ###

#def unescape(msg):
#   msg = msg.replace('\r','\\r')
#   msg = msg.replace('\n','\\n')
#   return msg

#def lpcAssert(retVal, expectedVal):
#   if (retVal != expectedVal):
#       hostPrint("[ERROR] Expected \'" + unescape(expectedVal) + "\'; got \'" + unescape(retVal) + "\'")
#       return -1
#   else:
#       hostPrint("[OK] Got \'" + unescape(expectedVal) + "\'")
#       return 0

def usage():
    print >>sys.stderr, "Usage: flashlpc.py [--erase] <DEVICE> filename.bin\nExample:\n\tflashlpc.py --erase COM3\tOnly erases the program on device\n\tflashlpc.py COM3 main.bin\tPrograms main.bin onto device\n"

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["help", "erase", "reset","auto-reset"])
    except getopt.error, msg:
        usage()
        sys.exit(2)
    
    erase = 0
    reset = False
    autoReset = False
    
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-e", "--erase"):
            erase = 1
        elif o in ("-r", "--reset"):
            reset = True
        elif o in ("-a", "--auto-reset"):
            autoReset = True
        else:
            hostFault("Invalid parameter(s)")

    if len(args) < 2 and erase != 1:
        usage()
        sys.exit(2)
    
    dev = args[0]
    crystalfreq = 12000
    
    cmd = flashlpc(dev, crystalfreq, reset)
    
    if erase == 1:
        cmd.lpcEraseProgramSectors()
    else:
        file = args[1]
        img = open(file, "rb").read()
        cmd.lpcProgramImageScript(img)
    
    hostPrint("Exiting. Reset the LPC1768 board")
    if autoReset:
        cmd.lpcAutoReset()
    
if __name__ == "__main__":
    main()
