#!/usr/bin/python

import argparse
import mmap
import re
import struct

# http://rosettacode.org/wiki/Bitwise_IO#Python
class BitWriter:
    def __init__(self, f):
        self.accumulator = 0
        self.bcount = 0
        self.out = f
 
    def __del__(self):
        try:
            self.flush()
        except ValueError:  # I/O operation on closed file
            pass
 
    def writebit(self, bit):
        if self.bcount == 8 :
            self.flush()
        if bit > 0:
            self.accumulator |= (1 << (7-self.bcount))
        self.bcount += 1
 
    def writebits(self, bits, n):
        while n > 0:
            self.writebit( bits & (1 << (n-1)) )
            n -= 1
 
    def flush(self):
        self.out.write(chr(self.accumulator))
        self.accumulator = 0
        self.bcount = 0
 
 
class BitReader:
    def __init__(self):
        self.accumulator = 0
        self.bcount = 0

    def readbit(self):
        if self.bcount == 0 :
            self.read(1)
        rv = ( self.accumulator & ( 1 << (self.bcount-1) ) ) >> (self.bcount-1)
        self.bcount -= 1
        return rv

    def readbits(self, n):
        v = 0
        while n > 0:
            v = (v << 1) | self.readbit()
            n -= 1
        return v
 

class MmapBitReader(BitReader):
    def __init__(self, fname, addr):
        BitReader.__init__(self)

        self.f = open(fname, "rw+b")

        page_addr = addr / MAP_SIZE
        off_addr = addr % MAP_SIZE

        print "page: %d, offset %d" % (page_addr, off_addr)
        self.mm = mmap.mmap(f.fileno(), MAP_SIZE, mmap.MAP_SHARED, access=mmap.ACCESS_WRITE, offset=page_addr * MAP_SIZE)
        self.mm.seek(off_addr)
    
    def close(self):
        self.f.close()
        del(self.f)
        self.mm.close()
        del(self.mm)

    def read(self, len): 
        a = self.input.read(1)
        if ( len(a) > 0 ):
            self.accumulator = ord(a)
        self.bcount = 8
    
class I2cBitReader(BitReader):
    def __init__(self, busno, dev_addr):
        BitReader.__init__(self)

        try:
            import smbus
        except: 
            print "need to install smbus-cffi"

        try:
            bus = smbus.SMBus(busno)
        except IOError, e:
            print "probably no right on i2c (root?)"
            raise e
        self.bus = bus
        self.dev_addr = dev_addr
        self.offset = 0

    def read(self, len): 
        self.accumulator = self.bus.read_byte_data(self.dev_addr, self.offset)
        self.offset += 1
        self.bcount = 8
 
parser = argparse.ArgumentParser(description='This is a demo script by nixCraft.')
parser.add_argument('addr', help='address to use')
parser.add_argument('-r', '--read',help='read')
args = parser.parse_args()
#print args

MAP_SIZE = mmap.PAGESIZE
addr = int(args.addr, 16)

if not isinstance(addr, int):
	raise Error('rr')

def chunks(l):
    """Yield successive n-sized chunks from l."""
    while True:
        m = re.match('^(\d*)(\D+)', l)
        if m is None:
            break;
        yield [ int(m.group(1)), m.group(2) ]
        l = m.string[m.end():]

read_format = list(chunks(args.read))

def dump(bitstream, read_format, reg_size):
    offset = 0
 
    for fmt in read_format:
        if fmt[0] == 0:
            continue
        if offset % reg_size == 0:
		print 'REG #0x%x' % (offset/8)
        if fmt[1] == 'b':
            l = bitstream.readbits(fmt[0])
            ffmt = "{0:0=%db}" % (fmt[0])
            fmted = ffmt.format(l) 
        elif fmt[1] == 'o':
            l = bitstream.readbits(fmt[0])
            nb_letter = (fmt[0]+2)/3 
            fmted = "%%0%do" % (nb_letter) % (l)
        elif fmt[1] == 'd':
            l = bitstream.readbits(fmt[0])
            fmted = "%d" % (l)
        elif fmt[1] == 'x':
            l = bitstream.readbits(fmt[0])
            nb_letter = (fmt[0]+3)/4 
            fmted = "%%0%dx" % (nb_letter) % (l)
        elif fmt[1] == '_':
            fmted = None
        else:
            fmted = None
            print "unhandled format ", fmt 
        offseted = reg_size - (offset % reg_size) - fmt[0]
        if fmted is not None:
            print "%02d %s" % (offseted, fmted)
        else:
            print "%02d" % (offseted)
        offset += fmt[0]
         

if addr > 0:
    bts = BitReader.open_mmap("/dev/mem", addr)
    dump(bts, read_format, 32)
else:
    import sys
    bts = I2cBitReader(2, 0x58)
    dump(bts, read_format, 8)
bts.close()

