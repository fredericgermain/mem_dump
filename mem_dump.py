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
    def __init__(self, f):
        self.input = f
        self.accumulator = 0
        self.bcount = 0
        self.read = 0
 
    def readbit(self):
        if self.bcount == 0 :
            a = self.input.read(1)
            if ( len(a) > 0 ):
                self.accumulator = ord(a)
            self.bcount = 8
            self.read = len(a)
        rv = ( self.accumulator & ( 1 << (self.bcount-1) ) ) >> (self.bcount-1)
        self.bcount -= 1
        return rv
 
    def readbits(self, n):
        v = 0
        while n > 0:
            v = (v << 1) | self.readbit()
            n -= 1
        return v
 
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

with open("/dev/mem", "rw+b") as f:
    exit
    page_addr = addr / MAP_SIZE
    off_addr = addr % MAP_SIZE

    print "page: %d, offset %d" % (page_addr, off_addr)
    mm = mmap.mmap(f.fileno(), MAP_SIZE, mmap.MAP_SHARED, access=mmap.ACCESS_WRITE, offset=page_addr * MAP_SIZE)
    mm.seek(off_addr)

    bitstream = BitReader(mm)
    offset = 0
 
    for fmt in read_format:
        if fmt[0] == 0:
            continue
        if offset % 32 == 0:
		print 'REG #0x%x' % (offset/8)
        if fmt[1] == 'b':
            l = bitstream.readbits(fmt[0])
            fmted = "{0:b}".format(l)
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
        offseted = 31 - (offset % 32) - fmt[0] + 1
        if fmted is not None:
            print "%02d %s" % (offseted, fmted)
        else:
            print "%02d" % (offseted)
        offset += fmt[0]
         

    mm.close()
