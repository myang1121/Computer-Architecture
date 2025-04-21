#=========================================================================
# CacheFL_test.py
#=========================================================================

import pytest

from random import seed, randint

from pymtl3 import *
from pymtl3.stdlib.mem        import MemMsgType
from pymtl3.stdlib.test_utils import mk_test_case_table

from lab3_mem.test.harness import req, resp, run_test
from lab3_mem.CacheFL      import CacheFL

seed(0xa4e28cc2)

#-------------------------------------------------------------------------
# cmp_wo_test_field
#-------------------------------------------------------------------------
# The test field in the cache response is used to indicate if the
# corresponding memory access resulted in a hit or a miss. However, the
# FL model always sets the test field to zero since it does not track
# hits/misses. So we need to do something special to ignore the test
# field when using the FL model. To do this, we can pass in a specialized
# comparison function to the StreamSinkFL.

def cmp_wo_test_field( msg, ref ):

  if msg.type_ != ref.type_:
    return False

  if msg.len != ref.len:
    return False

  if msg.opaque != msg.opaque:
    return False

  if ref.data != msg.data:
    return False

  # do not check the test field

  return True

#-------------------------------------------------------------------------
# Data
#-------------------------------------------------------------------------
# These functions are used to specify the address/data to preload into
# the main memory before running a test.

# 64B of sequential data

def data_64B():
  return [
    # addr      data
    0x00001000, 0x000c0ffe,
    0x00001004, 0x10101010,
    0x00001008, 0x20202020,
    0x0000100c, 0x30303030,
    0x00001010, 0x40404040,
    0x00001014, 0x50505050,
    0x00001018, 0x60606060,
    0x0000101c, 0x70707070,
    0x00001020, 0x80808080,
    0x00001024, 0x90909090,
    0x00001028, 0xa0a0a0a0,
    0x0000102c, 0xb0b0b0b0,
    0x00001030, 0xc0c0c0c0,
    0x00001034, 0xd0d0d0d0,
    0x00001038, 0xe0e0e0e0,
    0x0000103c, 0xf0f0f0f0,
  ]

# 512B of sequential data

def data_512B():
  data = []
  for i in range(128):
    data.extend([0x00001000+i*4,0xabcd1000+i*4])
  return data

# 1024B of random data

def data_random():
  seed(0xdeadbeef)
  data = []
  for i in range(256):
    data.extend([0x00001000+i*4,randint(0,0xffffffff)])
  return data

#----------------------------------------------------------------------
# Test Cases for Write Init
#----------------------------------------------------------------------

# Just make sure a single write init goes through the memory system.

def write_init_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x1000, 0, 0xdeadbeef ), resp( 'in', 0x0, 0,   0,  0    ),
  ]

# Write init a word multiple times, also tests opaque bits

def write_init_multi_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x1000, 0, 0xdeadbeef ), resp( 'in', 0x0, 0,   0,  0    ),
    req( 'in', 0x1, 0x1000, 0, 0xdeadbeef ), resp( 'in', 0x1, 0,   0,  0    ),
    req( 'in', 0x2, 0x1000, 0, 0xdeadbeef ), resp( 'in', 0x2, 0,   0,  0    ),
    req( 'in', 0x3, 0x1000, 0, 0xdeadbeef ), resp( 'in', 0x3, 0,   0,  0    ),
  ]

# Use write inits for each word in a cache line

def write_init_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x1000, 0, 0x01010101 ), resp( 'in', 0x0, 0,   0,  0    ),
    req( 'in', 0x1, 0x1004, 0, 0x02020202 ), resp( 'in', 0x1, 0,   0,  0    ),
    req( 'in', 0x2, 0x1008, 0, 0x03030303 ), resp( 'in', 0x2, 0,   0,  0    ),
    req( 'in', 0x3, 0x100c, 0, 0x04040404 ), resp( 'in', 0x3, 0,   0,  0    ),
  ]

# Write init one word in each cacheline in half the cache. For the direct
# mapped cache, this will write the first half of all the sets. For the
# set associative cache, this will write all of the sets in the first
# way.

def write_init_multi_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x0000, 0, 0x00000000 ), resp( 'in', 0x0, 0,   0,  0    ),
    req( 'in', 0x1, 0x1010, 0, 0x01010101 ), resp( 'in', 0x1, 0,   0,  0    ),
    req( 'in', 0x2, 0x2020, 0, 0x02020202 ), resp( 'in', 0x2, 0,   0,  0    ),
    req( 'in', 0x3, 0x3030, 0, 0x03030303 ), resp( 'in', 0x3, 0,   0,  0    ),
    req( 'in', 0x4, 0x4040, 0, 0x04040404 ), resp( 'in', 0x4, 0,   0,  0    ),
    req( 'in', 0x5, 0x5050, 0, 0x05050505 ), resp( 'in', 0x5, 0,   0,  0    ),
    req( 'in', 0x6, 0x6060, 0, 0x06060606 ), resp( 'in', 0x6, 0,   0,  0    ),
    req( 'in', 0x7, 0x7070, 0, 0x07070707 ), resp( 'in', 0x7, 0,   0,  0    ),
  ]

#----------------------------------------------------------------------
# Test Cases for Read Hits
#----------------------------------------------------------------------

# Single read hit

def read_hit_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x1000, 0, 0xdeadbeef ), resp( 'in', 0x0, 0,   0,  0          ),
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0xdeadbeef ),
  ]

# Read same word multiple times, also tests opaque bits

def read_hit_multi_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x1000, 0, 0xdeadbeef ), resp( 'in', 0x0, 0,   0,  0    ),

    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0xdeadbeef ),
    req( 'rd', 0x1, 0x1000, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0xdeadbeef ),
    req( 'rd', 0x2, 0x1000, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0xdeadbeef ),
    req( 'rd', 0x3, 0x1000, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0xdeadbeef ),
  ]

# Read every word in cache line

def read_hit_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x1000, 0, 0x01010101 ), resp( 'in', 0x0, 0,   0,  0    ),
    req( 'in', 0x1, 0x1004, 0, 0x02020202 ), resp( 'in', 0x1, 0,   0,  0    ),
    req( 'in', 0x2, 0x1008, 0, 0x03030303 ), resp( 'in', 0x2, 0,   0,  0    ),
    req( 'in', 0x3, 0x100c, 0, 0x04040404 ), resp( 'in', 0x3, 0,   0,  0    ),

    req( 'rd', 0x4, 0x1000, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x01010101 ),
    req( 'rd', 0x5, 0x1004, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x02020202 ),
    req( 'rd', 0x6, 0x1008, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x03030303 ),
    req( 'rd', 0x7, 0x100c, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x04040404 ),
  ]

# Read one word from each cacheline

def read_hit_multi_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x0000, 0, 0x00000000 ), resp( 'in', 0x0, 0,   0,  0          ),
    req( 'in', 0x1, 0x1010, 0, 0x01010101 ), resp( 'in', 0x1, 0,   0,  0          ),
    req( 'in', 0x2, 0x2020, 0, 0x02020202 ), resp( 'in', 0x2, 0,   0,  0          ),
    req( 'in', 0x3, 0x3030, 0, 0x03030303 ), resp( 'in', 0x3, 0,   0,  0          ),
    req( 'in', 0x4, 0x4040, 0, 0x04040404 ), resp( 'in', 0x4, 0,   0,  0          ),
    req( 'in', 0x5, 0x5050, 0, 0x05050505 ), resp( 'in', 0x5, 0,   0,  0          ),
    req( 'in', 0x6, 0x6060, 0, 0x06060606 ), resp( 'in', 0x6, 0,   0,  0          ),
    req( 'in', 0x7, 0x7070, 0, 0x07070707 ), resp( 'in', 0x7, 0,   0,  0          ),

    req( 'rd', 0x0, 0x0000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0x00000000 ),
    req( 'rd', 0x1, 0x1010, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0x01010101 ),
    req( 'rd', 0x2, 0x2020, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0x02020202 ),
    req( 'rd', 0x3, 0x3030, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x03030303 ),
    req( 'rd', 0x4, 0x4040, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x04040404 ),
    req( 'rd', 0x5, 0x5050, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x05050505 ),
    req( 'rd', 0x6, 0x6060, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x06060606 ),
    req( 'rd', 0x7, 0x7070, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x07070707 ),
  ]

#----------------------------------------------------------------------
# Test Cases for Write Hits
#----------------------------------------------------------------------

# Single write hit to one word

def write_hit_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x1000, 0, 0xdeadbeef ), resp( 'in', 0x0, 0,   0,  0          ),
    req( 'wr', 0x0, 0x1000, 0, 0xcafecafe ), resp( 'wr', 0x0, 1,   0,  0          ),
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0xcafecafe ),
  ]

# Write/read word multiple times, also tests opaque bits

def write_hit_multi_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x1000, 0, 0xdeadbeef ), resp( 'in', 0x0, 0,   0,  0          ),

    req( 'wr', 0x1, 0x1000, 0, 0x01010101 ), resp( 'wr', 0x1, 1,   0,  0          ),
    req( 'rd', 0x2, 0x1000, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0x01010101 ),
    req( 'wr', 0x3, 0x1000, 0, 0x02020202 ), resp( 'wr', 0x3, 1,   0,  0          ),
    req( 'rd', 0x4, 0x1000, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x02020202 ),
    req( 'wr', 0x5, 0x1000, 0, 0x03030303 ), resp( 'wr', 0x5, 1,   0,  0          ),
    req( 'rd', 0x6, 0x1000, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x03030303 ),
    req( 'wr', 0x7, 0x1000, 0, 0x04040404 ), resp( 'wr', 0x7, 1,   0,  0          ),
    req( 'rd', 0x8, 0x1000, 0, 0          ), resp( 'rd', 0x8, 1,   0,  0x04040404 ),
  ]

# Write/read every word in cache line

def write_hit_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x1000, 0, 0x01010101 ), resp( 'in', 0x0, 0,   0,  0          ),
    req( 'in', 0x0, 0x1004, 0, 0x02020202 ), resp( 'in', 0x0, 0,   0,  0          ),
    req( 'in', 0x0, 0x1008, 0, 0x03030303 ), resp( 'in', 0x0, 0,   0,  0          ),
    req( 'in', 0x0, 0x100c, 0, 0x04040404 ), resp( 'in', 0x0, 0,   0,  0          ),

    req( 'wr', 0x1, 0x1000, 0, 0x01010101 ), resp( 'wr', 0x1, 1,   0,  0          ),
    req( 'wr', 0x3, 0x1004, 0, 0x02020202 ), resp( 'wr', 0x3, 1,   0,  0          ),
    req( 'wr', 0x5, 0x1008, 0, 0x03030303 ), resp( 'wr', 0x5, 1,   0,  0          ),
    req( 'wr', 0x7, 0x100c, 0, 0x04040404 ), resp( 'wr', 0x7, 1,   0,  0          ),

    req( 'rd', 0x2, 0x1000, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0x01010101 ),
    req( 'rd', 0x4, 0x1004, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x02020202 ),
    req( 'rd', 0x6, 0x1008, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x03030303 ),
    req( 'rd', 0x8, 0x100c, 0, 0          ), resp( 'rd', 0x8, 1,   0,  0x04040404 ),
  ]

# Write/read one word from each cacheline

def write_hit_multi_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'in', 0x0, 0x0000, 0, 0x00000000 ), resp( 'in', 0x0, 0,   0,  0          ),
    req( 'in', 0x1, 0x1010, 0, 0x01010101 ), resp( 'in', 0x1, 0,   0,  0          ),
    req( 'in', 0x2, 0x2020, 0, 0x02020202 ), resp( 'in', 0x2, 0,   0,  0          ),
    req( 'in', 0x3, 0x3030, 0, 0x03030303 ), resp( 'in', 0x3, 0,   0,  0          ),
    req( 'in', 0x4, 0x4040, 0, 0x04040404 ), resp( 'in', 0x4, 0,   0,  0          ),
    req( 'in', 0x5, 0x5050, 0, 0x05050505 ), resp( 'in', 0x5, 0,   0,  0          ),
    req( 'in', 0x6, 0x6060, 0, 0x06060606 ), resp( 'in', 0x6, 0,   0,  0          ),
    req( 'in', 0x7, 0x7070, 0, 0x07070707 ), resp( 'in', 0x7, 0,   0,  0          ),

    req( 'wr', 0x0, 0x0000, 0, 0x10101010 ), resp( 'wr', 0x0, 1,   0,  0          ),
    req( 'wr', 0x1, 0x1010, 0, 0x11111111 ), resp( 'wr', 0x1, 1,   0,  0          ),
    req( 'wr', 0x2, 0x2020, 0, 0x12121212 ), resp( 'wr', 0x2, 1,   0,  0          ),
    req( 'wr', 0x3, 0x3030, 0, 0x13131313 ), resp( 'wr', 0x3, 1,   0,  0          ),
    req( 'wr', 0x4, 0x4040, 0, 0x14141414 ), resp( 'wr', 0x4, 1,   0,  0          ),
    req( 'wr', 0x5, 0x5050, 0, 0x15151515 ), resp( 'wr', 0x5, 1,   0,  0          ),
    req( 'wr', 0x6, 0x6060, 0, 0x16161616 ), resp( 'wr', 0x6, 1,   0,  0          ),
    req( 'wr', 0x7, 0x7070, 0, 0x17171717 ), resp( 'wr', 0x7, 1,   0,  0          ),

    req( 'rd', 0x0, 0x0000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0x10101010 ),
    req( 'rd', 0x1, 0x1010, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0x11111111 ),
    req( 'rd', 0x2, 0x2020, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0x12121212 ),
    req( 'rd', 0x3, 0x3030, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x13131313 ),
    req( 'rd', 0x4, 0x4040, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x14141414 ),
    req( 'rd', 0x5, 0x5050, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x15151515 ),
    req( 'rd', 0x6, 0x6060, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x16161616 ),
    req( 'rd', 0x7, 0x7070, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x17171717 ),
  ]

#----------------------------------------------------------------------
# Test Cases for Refill on Read Miss
#----------------------------------------------------------------------

# Single read miss (uses data_64B)

def read_miss_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 0,   0,  0x000c0ffe ),
  ]

# Read same word multiple times, also tests opaque bits (uses data_64B)

def read_miss_multi_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 0,   0,  0x000c0ffe ),
    req( 'rd', 0x1, 0x1000, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0x000c0ffe ),
    req( 'rd', 0x2, 0x1000, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0x000c0ffe ),
    req( 'rd', 0x3, 0x1000, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x000c0ffe ),
  ]

# Read every word in cache line (uses data_64B)

def read_miss_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'rd', 0x1, 0x1000, 0, 0          ), resp( 'rd', 0x1, 0,   0,  0x000c0ffe ),
    req( 'rd', 0x2, 0x1004, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0x10101010 ),
    req( 'rd', 0x3, 0x1008, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x20202020 ),
    req( 'rd', 0x4, 0x100c, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x30303030 ),
  ]

# Read miss for each cacheline, then read hit for each cacheline (uses data_512B)

def read_miss_multi_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 0,   0,  0xabcd1000 ),
    req( 'rd', 0x1, 0x1010, 0, 0          ), resp( 'rd', 0x1, 0,   0,  0xabcd1010 ),
    req( 'rd', 0x2, 0x1020, 0, 0          ), resp( 'rd', 0x2, 0,   0,  0xabcd1020 ),
    req( 'rd', 0x3, 0x1030, 0, 0          ), resp( 'rd', 0x3, 0,   0,  0xabcd1030 ),
    req( 'rd', 0x4, 0x1040, 0, 0          ), resp( 'rd', 0x4, 0,   0,  0xabcd1040 ),
    req( 'rd', 0x5, 0x1050, 0, 0          ), resp( 'rd', 0x5, 0,   0,  0xabcd1050 ),
    req( 'rd', 0x6, 0x1060, 0, 0          ), resp( 'rd', 0x6, 0,   0,  0xabcd1060 ),
    req( 'rd', 0x7, 0x1070, 0, 0          ), resp( 'rd', 0x7, 0,   0,  0xabcd1070 ),
    req( 'rd', 0x8, 0x1080, 0, 0          ), resp( 'rd', 0x8, 0,   0,  0xabcd1080 ),
    req( 'rd', 0x9, 0x1090, 0, 0          ), resp( 'rd', 0x9, 0,   0,  0xabcd1090 ),
    req( 'rd', 0xa, 0x10a0, 0, 0          ), resp( 'rd', 0xa, 0,   0,  0xabcd10a0 ),
    req( 'rd', 0xb, 0x10b0, 0, 0          ), resp( 'rd', 0xb, 0,   0,  0xabcd10b0 ),
    req( 'rd', 0xc, 0x10c0, 0, 0          ), resp( 'rd', 0xc, 0,   0,  0xabcd10c0 ),
    req( 'rd', 0xd, 0x10d0, 0, 0          ), resp( 'rd', 0xd, 0,   0,  0xabcd10d0 ),
    req( 'rd', 0xe, 0x10e0, 0, 0          ), resp( 'rd', 0xe, 0,   0,  0xabcd10e0 ),
    req( 'rd', 0xf, 0x10f0, 0, 0          ), resp( 'rd', 0xf, 0,   0,  0xabcd10f0 ),

    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0xabcd1000 ),
    req( 'rd', 0x1, 0x1010, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0xabcd1010 ),
    req( 'rd', 0x2, 0x1020, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0xabcd1020 ),
    req( 'rd', 0x3, 0x1030, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0xabcd1030 ),
    req( 'rd', 0x4, 0x1040, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0xabcd1040 ),
    req( 'rd', 0x5, 0x1050, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0xabcd1050 ),
    req( 'rd', 0x6, 0x1060, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0xabcd1060 ),
    req( 'rd', 0x7, 0x1070, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0xabcd1070 ),
    req( 'rd', 0x8, 0x1080, 0, 0          ), resp( 'rd', 0x8, 1,   0,  0xabcd1080 ),
    req( 'rd', 0x9, 0x1090, 0, 0          ), resp( 'rd', 0x9, 1,   0,  0xabcd1090 ),
    req( 'rd', 0xa, 0x10a0, 0, 0          ), resp( 'rd', 0xa, 1,   0,  0xabcd10a0 ),
    req( 'rd', 0xb, 0x10b0, 0, 0          ), resp( 'rd', 0xb, 1,   0,  0xabcd10b0 ),
    req( 'rd', 0xc, 0x10c0, 0, 0          ), resp( 'rd', 0xc, 1,   0,  0xabcd10c0 ),
    req( 'rd', 0xd, 0x10d0, 0, 0          ), resp( 'rd', 0xd, 1,   0,  0xabcd10d0 ),
    req( 'rd', 0xe, 0x10e0, 0, 0          ), resp( 'rd', 0xe, 1,   0,  0xabcd10e0 ),
    req( 'rd', 0xf, 0x10f0, 0, 0          ), resp( 'rd', 0xf, 1,   0,  0xabcd10f0 ),

    req( 'rd', 0x0, 0x1004, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0xabcd1004 ),
    req( 'rd', 0x1, 0x1014, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0xabcd1014 ),
    req( 'rd', 0x2, 0x1024, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0xabcd1024 ),
    req( 'rd', 0x3, 0x1034, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0xabcd1034 ),
    req( 'rd', 0x4, 0x1044, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0xabcd1044 ),
    req( 'rd', 0x5, 0x1054, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0xabcd1054 ),
    req( 'rd', 0x6, 0x1064, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0xabcd1064 ),
    req( 'rd', 0x7, 0x1074, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0xabcd1074 ),
    req( 'rd', 0x8, 0x1084, 0, 0          ), resp( 'rd', 0x8, 1,   0,  0xabcd1084 ),
    req( 'rd', 0x9, 0x1094, 0, 0          ), resp( 'rd', 0x9, 1,   0,  0xabcd1094 ),
    req( 'rd', 0xa, 0x10a4, 0, 0          ), resp( 'rd', 0xa, 1,   0,  0xabcd10a4 ),
    req( 'rd', 0xb, 0x10b4, 0, 0          ), resp( 'rd', 0xb, 1,   0,  0xabcd10b4 ),
    req( 'rd', 0xc, 0x10c4, 0, 0          ), resp( 'rd', 0xc, 1,   0,  0xabcd10c4 ),
    req( 'rd', 0xd, 0x10d4, 0, 0          ), resp( 'rd', 0xd, 1,   0,  0xabcd10d4 ),
    req( 'rd', 0xe, 0x10e4, 0, 0          ), resp( 'rd', 0xe, 1,   0,  0xabcd10e4 ),
    req( 'rd', 0xf, 0x10f4, 0, 0          ), resp( 'rd', 0xf, 1,   0,  0xabcd10f4 ),
  ]

#----------------------------------------------------------------------
# Test Cases for Refill on Write Miss
#----------------------------------------------------------------------

# Single write miss to one word (uses data_64B)

def write_miss_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'wr', 0x0, 0x1000, 0, 0xcafecafe ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0xcafecafe ),
  ]

# Write/read word multiple times, also tests opaque bits (uses data_64B)

def write_miss_multi_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'wr', 0x1, 0x1000, 0, 0x01010101 ), resp( 'wr', 0x1, 0,   0,  0          ),
    req( 'rd', 0x2, 0x1000, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0x01010101 ),
    req( 'wr', 0x3, 0x1000, 0, 0x02020202 ), resp( 'wr', 0x3, 1,   0,  0          ),
    req( 'rd', 0x4, 0x1000, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x02020202 ),
    req( 'wr', 0x5, 0x1000, 0, 0x03030303 ), resp( 'wr', 0x5, 1,   0,  0          ),
    req( 'rd', 0x6, 0x1000, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x03030303 ),
    req( 'wr', 0x7, 0x1000, 0, 0x04040404 ), resp( 'wr', 0x7, 1,   0,  0          ),
    req( 'rd', 0x8, 0x1000, 0, 0          ), resp( 'rd', 0x8, 1,   0,  0x04040404 ),
  ]

# Write/read every word in cache line (uses data_64B)

def write_miss_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'wr', 0x1, 0x1000, 0, 0x01010101 ), resp( 'wr', 0x1, 0,   0,  0          ),
    req( 'wr', 0x2, 0x1004, 0, 0x02020202 ), resp( 'wr', 0x2, 1,   0,  0          ),
    req( 'wr', 0x3, 0x1008, 0, 0x03030303 ), resp( 'wr', 0x3, 1,   0,  0          ),
    req( 'wr', 0x4, 0x100c, 0, 0x04040404 ), resp( 'wr', 0x4, 1,   0,  0          ),

    req( 'rd', 0x5, 0x1000, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x01010101 ),
    req( 'rd', 0x6, 0x1004, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x02020202 ),
    req( 'rd', 0x7, 0x1008, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x03030303 ),
    req( 'rd', 0x8, 0x100c, 0, 0          ), resp( 'rd', 0x8, 1,   0,  0x04040404 ),
  ]

# Write/read one word from each cacheline (uses data_512B)

def write_miss_multi_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'wr', 0x0, 0x1000, 0, 0x10101010 ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'wr', 0x1, 0x1010, 0, 0x11111111 ), resp( 'wr', 0x1, 0,   0,  0          ),
    req( 'wr', 0x2, 0x1020, 0, 0x12121212 ), resp( 'wr', 0x2, 0,   0,  0          ),
    req( 'wr', 0x3, 0x1030, 0, 0x13131313 ), resp( 'wr', 0x3, 0,   0,  0          ),
    req( 'wr', 0x4, 0x1040, 0, 0x14141414 ), resp( 'wr', 0x4, 0,   0,  0          ),
    req( 'wr', 0x5, 0x1050, 0, 0x15151515 ), resp( 'wr', 0x5, 0,   0,  0          ),
    req( 'wr', 0x6, 0x1060, 0, 0x16161616 ), resp( 'wr', 0x6, 0,   0,  0          ),
    req( 'wr', 0x7, 0x1070, 0, 0x17171717 ), resp( 'wr', 0x7, 0,   0,  0          ),
    req( 'wr', 0x8, 0x1080, 0, 0x18181818 ), resp( 'wr', 0x8, 0,   0,  0          ),
    req( 'wr', 0x9, 0x1090, 0, 0x19191919 ), resp( 'wr', 0x9, 0,   0,  0          ),
    req( 'wr', 0xa, 0x10a0, 0, 0x1a1a1a1a ), resp( 'wr', 0xa, 0,   0,  0          ),
    req( 'wr', 0xb, 0x10b0, 0, 0x1b1b1b1b ), resp( 'wr', 0xb, 0,   0,  0          ),
    req( 'wr', 0xc, 0x10c0, 0, 0x1c1c1c1c ), resp( 'wr', 0xc, 0,   0,  0          ),
    req( 'wr', 0xd, 0x10d0, 0, 0x1d1d1d1d ), resp( 'wr', 0xd, 0,   0,  0          ),
    req( 'wr', 0xe, 0x10e0, 0, 0x1e1e1e1e ), resp( 'wr', 0xe, 0,   0,  0          ),
    req( 'wr', 0xf, 0x10f0, 0, 0x1f1f1f1f ), resp( 'wr', 0xf, 0,   0,  0          ),

    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0x10101010 ),
    req( 'rd', 0x1, 0x1010, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0x11111111 ),
    req( 'rd', 0x2, 0x1020, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0x12121212 ),
    req( 'rd', 0x3, 0x1030, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x13131313 ),
    req( 'rd', 0x4, 0x1040, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x14141414 ),
    req( 'rd', 0x5, 0x1050, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x15151515 ),
    req( 'rd', 0x6, 0x1060, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x16161616 ),
    req( 'rd', 0x7, 0x1070, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x17171717 ),
    req( 'rd', 0x8, 0x1080, 0, 0          ), resp( 'rd', 0x8, 1,   0,  0x18181818 ),
    req( 'rd', 0x9, 0x1090, 0, 0          ), resp( 'rd', 0x9, 1,   0,  0x19191919 ),
    req( 'rd', 0xa, 0x10a0, 0, 0          ), resp( 'rd', 0xa, 1,   0,  0x1a1a1a1a ),
    req( 'rd', 0xb, 0x10b0, 0, 0          ), resp( 'rd', 0xb, 1,   0,  0x1b1b1b1b ),
    req( 'rd', 0xc, 0x10c0, 0, 0          ), resp( 'rd', 0xc, 1,   0,  0x1c1c1c1c ),
    req( 'rd', 0xd, 0x10d0, 0, 0          ), resp( 'rd', 0xd, 1,   0,  0x1d1d1d1d ),
    req( 'rd', 0xe, 0x10e0, 0, 0          ), resp( 'rd', 0xe, 1,   0,  0x1e1e1e1e ),
    req( 'rd', 0xf, 0x10f0, 0, 0          ), resp( 'rd', 0xf, 1,   0,  0x1f1f1f1f ),
  ]

#----------------------------------------------------------------------
# Test Cases for Evict
#----------------------------------------------------------------------

# Write miss to two cachelines, and then a read to a third cacheline.
# This read to the third cacheline is guaranteed to cause an eviction on
# both the direct mapped and set associative caches. (uses data_512B)

def evict_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'wr', 0x0, 0x1000, 0, 0xcafecafe ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0xcafecafe ),
    req( 'wr', 0x0, 0x1080, 0, 0x000c0ffe ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'rd', 0x0, 0x1080, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0x000c0ffe ),
    req( 'rd', 0x0, 0x1100, 0, 0          ), resp( 'rd', 0x0, 0,   0,  0xabcd1100 ), # conflicts
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 0,   0,  0xcafecafe ),
  ]

# Write word and evict multiple times. Test is carefully crafted to
# ensure it applies to both direct mapped and set associative caches.
# (uses data_512B)

def evict_multi_word():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'wr', 0x0, 0x1000, 0, 0x01010101 ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'rd', 0x1, 0x1000, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0x01010101 ),
    req( 'wr', 0x2, 0x1080, 0, 0x11111111 ), resp( 'wr', 0x2, 0,   0,  0          ),
    req( 'rd', 0x3, 0x1080, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x11111111 ),
    req( 'rd', 0x4, 0x1100, 0, 0          ), resp( 'rd', 0x4, 0,   0,  0xabcd1100 ), # conflicts
    req( 'rd', 0x5, 0x1080, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x11111111 ), # make sure way1 is still LRU

    req( 'wr', 0x6, 0x1000, 0, 0x02020202 ), resp( 'wr', 0x6, 0,   0,  0          ),
    req( 'rd', 0x7, 0x1000, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x02020202 ),
    req( 'wr', 0x8, 0x1080, 0, 0x12121212 ), resp( 'wr', 0x8, 1,   0,  0          ),
    req( 'rd', 0x9, 0x1080, 0, 0          ), resp( 'rd', 0x9, 1,   0,  0x12121212 ),
    req( 'rd', 0xa, 0x1100, 0, 0          ), resp( 'rd', 0xa, 0,   0,  0xabcd1100 ), # conflicts
    req( 'rd', 0xb, 0x1080, 0, 0          ), resp( 'rd', 0xb, 1,   0,  0x12121212 ), # make sure way1 is still LRU

    req( 'wr', 0xc, 0x1000, 0, 0x03030303 ), resp( 'wr', 0xc, 0,   0,  0          ),
    req( 'rd', 0xd, 0x1000, 0, 0          ), resp( 'rd', 0xd, 1,   0,  0x03030303 ),
    req( 'wr', 0xe, 0x1080, 0, 0x13131313 ), resp( 'wr', 0xe, 1,   0,  0          ),
    req( 'rd', 0xf, 0x1080, 0, 0          ), resp( 'rd', 0xf, 1,   0,  0x13131313 ),
    req( 'rd', 0x0, 0x1100, 0, 0          ), resp( 'rd', 0x0, 0,   0,  0xabcd1100 ), # conflicts
    req( 'rd', 0x1, 0x1080, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0x13131313 ), # make sure way1 is still LRU

    req( 'wr', 0x2, 0x1000, 0, 0x04040404 ), resp( 'wr', 0x2, 0,   0,  0          ),
    req( 'rd', 0x3, 0x1000, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x04040404 ),
    req( 'wr', 0x4, 0x1080, 0, 0x14141414 ), resp( 'wr', 0x4, 1,   0,  0          ),
    req( 'rd', 0x5, 0x1080, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x14141414 ),
    req( 'rd', 0x6, 0x1100, 0, 0          ), resp( 'rd', 0x6, 0,   0,  0xabcd1100 ), # conflicts
    req( 'rd', 0x7, 0x1080, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x14141414 ), # make sure way1 is still LRU

    req( 'rd', 0x8, 0x1000, 0, 0          ), resp( 'rd', 0x8, 0,   0,  0x04040404 ),
  ]

# Write every word on two cachelines, and then a read to a third
# cacheline. This read to the third cacheline is guaranteed to cause an
# eviction on both the direct mapped and set associative caches. (uses
# data_512B)

def evict_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'wr', 0x0, 0x1000, 0, 0x01010101 ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'wr', 0x1, 0x1004, 0, 0x02020202 ), resp( 'wr', 0x1, 1,   0,  0          ),
    req( 'wr', 0x2, 0x1008, 0, 0x03030303 ), resp( 'wr', 0x2, 1,   0,  0          ),
    req( 'wr', 0x3, 0x100c, 0, 0x04040404 ), resp( 'wr', 0x3, 1,   0,  0          ),

    req( 'wr', 0x4, 0x1080, 0, 0x11111111 ), resp( 'wr', 0x4, 0,   0,  0          ),
    req( 'wr', 0x5, 0x1084, 0, 0x12121212 ), resp( 'wr', 0x5, 1,   0,  0          ),
    req( 'wr', 0x6, 0x1088, 0, 0x13131313 ), resp( 'wr', 0x6, 1,   0,  0          ),
    req( 'wr', 0x7, 0x108c, 0, 0x14141414 ), resp( 'wr', 0x7, 1,   0,  0          ),

    req( 'rd', 0x8, 0x1100, 0, 0          ), resp( 'rd', 0x8, 0,   0,  0xabcd1100 ), # conflicts

    req( 'rd', 0x9, 0x1000, 0, 0          ), resp( 'rd', 0x9, 0,   0,  0x01010101 ),
    req( 'rd', 0xa, 0x1004, 0, 0          ), resp( 'rd', 0xa, 1,   0,  0x02020202 ),
    req( 'rd', 0xb, 0x1008, 0, 0          ), resp( 'rd', 0xb, 1,   0,  0x03030303 ),
    req( 'rd', 0xc, 0x100c, 0, 0          ), resp( 'rd', 0xc, 1,   0,  0x04040404 ),
  ]

# Write one word from each cacheline, then evict (uses data_512B)

def evict_multi_cacheline():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'wr', 0x0, 0x1000, 0, 0x10101010 ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'wr', 0x1, 0x1010, 0, 0x11111111 ), resp( 'wr', 0x1, 0,   0,  0          ),
    req( 'wr', 0x2, 0x1020, 0, 0x12121212 ), resp( 'wr', 0x2, 0,   0,  0          ),
    req( 'wr', 0x3, 0x1030, 0, 0x13131313 ), resp( 'wr', 0x3, 0,   0,  0          ),
    req( 'wr', 0x4, 0x1040, 0, 0x14141414 ), resp( 'wr', 0x4, 0,   0,  0          ),
    req( 'wr', 0x5, 0x1050, 0, 0x15151515 ), resp( 'wr', 0x5, 0,   0,  0          ),
    req( 'wr', 0x6, 0x1060, 0, 0x16161616 ), resp( 'wr', 0x6, 0,   0,  0          ),
    req( 'wr', 0x7, 0x1070, 0, 0x17171717 ), resp( 'wr', 0x7, 0,   0,  0          ),
    req( 'wr', 0x8, 0x1080, 0, 0x18181818 ), resp( 'wr', 0x8, 0,   0,  0          ),
    req( 'wr', 0x9, 0x1090, 0, 0x19191919 ), resp( 'wr', 0x9, 0,   0,  0          ),
    req( 'wr', 0xa, 0x10a0, 0, 0x1a1a1a1a ), resp( 'wr', 0xa, 0,   0,  0          ),
    req( 'wr', 0xb, 0x10b0, 0, 0x1b1b1b1b ), resp( 'wr', 0xb, 0,   0,  0          ),
    req( 'wr', 0xc, 0x10c0, 0, 0x1c1c1c1c ), resp( 'wr', 0xc, 0,   0,  0          ),
    req( 'wr', 0xd, 0x10d0, 0, 0x1d1d1d1d ), resp( 'wr', 0xd, 0,   0,  0          ),
    req( 'wr', 0xe, 0x10e0, 0, 0x1e1e1e1e ), resp( 'wr', 0xe, 0,   0,  0          ),
    req( 'wr', 0xf, 0x10f0, 0, 0x1f1f1f1f ), resp( 'wr', 0xf, 0,   0,  0          ),

    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0x10101010 ),
    req( 'rd', 0x1, 0x1010, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0x11111111 ),
    req( 'rd', 0x2, 0x1020, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0x12121212 ),
    req( 'rd', 0x3, 0x1030, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x13131313 ),
    req( 'rd', 0x4, 0x1040, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0x14141414 ),
    req( 'rd', 0x5, 0x1050, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x15151515 ),
    req( 'rd', 0x6, 0x1060, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x16161616 ),
    req( 'rd', 0x7, 0x1070, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x17171717 ),
    req( 'rd', 0x8, 0x1080, 0, 0          ), resp( 'rd', 0x8, 1,   0,  0x18181818 ),
    req( 'rd', 0x9, 0x1090, 0, 0          ), resp( 'rd', 0x9, 1,   0,  0x19191919 ),
    req( 'rd', 0xa, 0x10a0, 0, 0          ), resp( 'rd', 0xa, 1,   0,  0x1a1a1a1a ),
    req( 'rd', 0xb, 0x10b0, 0, 0          ), resp( 'rd', 0xb, 1,   0,  0x1b1b1b1b ),
    req( 'rd', 0xc, 0x10c0, 0, 0          ), resp( 'rd', 0xc, 1,   0,  0x1c1c1c1c ),
    req( 'rd', 0xd, 0x10d0, 0, 0          ), resp( 'rd', 0xd, 1,   0,  0x1d1d1d1d ),
    req( 'rd', 0xe, 0x10e0, 0, 0          ), resp( 'rd', 0xe, 1,   0,  0x1e1e1e1e ),
    req( 'rd', 0xf, 0x10f0, 0, 0          ), resp( 'rd', 0xf, 1,   0,  0x1f1f1f1f ),

    req( 'rd', 0x0, 0x1100, 0, 0          ), resp( 'rd', 0x0, 0,   0,  0xabcd1100 ), # conflicts
    req( 'rd', 0x1, 0x1110, 0, 0          ), resp( 'rd', 0x1, 0,   0,  0xabcd1110 ), # conflicts
    req( 'rd', 0x2, 0x1120, 0, 0          ), resp( 'rd', 0x2, 0,   0,  0xabcd1120 ), # conflicts
    req( 'rd', 0x3, 0x1130, 0, 0          ), resp( 'rd', 0x3, 0,   0,  0xabcd1130 ), # conflicts
    req( 'rd', 0x4, 0x1140, 0, 0          ), resp( 'rd', 0x4, 0,   0,  0xabcd1140 ), # conflicts
    req( 'rd', 0x5, 0x1150, 0, 0          ), resp( 'rd', 0x5, 0,   0,  0xabcd1150 ), # conflicts
    req( 'rd', 0x6, 0x1160, 0, 0          ), resp( 'rd', 0x6, 0,   0,  0xabcd1160 ), # conflicts
    req( 'rd', 0x7, 0x1170, 0, 0          ), resp( 'rd', 0x7, 0,   0,  0xabcd1170 ), # conflicts
    req( 'rd', 0x8, 0x1180, 0, 0          ), resp( 'rd', 0x8, 0,   0,  0xabcd1180 ), # conflicts
    req( 'rd', 0x9, 0x1190, 0, 0          ), resp( 'rd', 0x9, 0,   0,  0xabcd1190 ), # conflicts
    req( 'rd', 0xa, 0x11a0, 0, 0          ), resp( 'rd', 0xa, 0,   0,  0xabcd11a0 ), # conflicts
    req( 'rd', 0xb, 0x11b0, 0, 0          ), resp( 'rd', 0xb, 0,   0,  0xabcd11b0 ), # conflicts
    req( 'rd', 0xc, 0x11c0, 0, 0          ), resp( 'rd', 0xc, 0,   0,  0xabcd11c0 ), # conflicts
    req( 'rd', 0xd, 0x11d0, 0, 0          ), resp( 'rd', 0xd, 0,   0,  0xabcd11d0 ), # conflicts
    req( 'rd', 0xe, 0x11e0, 0, 0          ), resp( 'rd', 0xe, 0,   0,  0xabcd11e0 ), # conflicts
    req( 'rd', 0xf, 0x11f0, 0, 0          ), resp( 'rd', 0xf, 0,   0,  0xabcd11f0 ), # conflicts

    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 0,   0,  0x10101010 ),
    req( 'rd', 0x1, 0x1010, 0, 0          ), resp( 'rd', 0x1, 0,   0,  0x11111111 ),
    req( 'rd', 0x2, 0x1020, 0, 0          ), resp( 'rd', 0x2, 0,   0,  0x12121212 ),
    req( 'rd', 0x3, 0x1030, 0, 0          ), resp( 'rd', 0x3, 0,   0,  0x13131313 ),
    req( 'rd', 0x4, 0x1040, 0, 0          ), resp( 'rd', 0x4, 0,   0,  0x14141414 ),
    req( 'rd', 0x5, 0x1050, 0, 0          ), resp( 'rd', 0x5, 0,   0,  0x15151515 ),
    req( 'rd', 0x6, 0x1060, 0, 0          ), resp( 'rd', 0x6, 0,   0,  0x16161616 ),
    req( 'rd', 0x7, 0x1070, 0, 0          ), resp( 'rd', 0x7, 0,   0,  0x17171717 ),
    req( 'rd', 0x8, 0x1080, 0, 0          ), resp( 'rd', 0x8, 0,   0,  0x18181818 ),
    req( 'rd', 0x9, 0x1090, 0, 0          ), resp( 'rd', 0x9, 0,   0,  0x19191919 ),
    req( 'rd', 0xa, 0x10a0, 0, 0          ), resp( 'rd', 0xa, 0,   0,  0x1a1a1a1a ),
    req( 'rd', 0xb, 0x10b0, 0, 0          ), resp( 'rd', 0xb, 0,   0,  0x1b1b1b1b ),
    req( 'rd', 0xc, 0x10c0, 0, 0          ), resp( 'rd', 0xc, 0,   0,  0x1c1c1c1c ),
    req( 'rd', 0xd, 0x10d0, 0, 0          ), resp( 'rd', 0xd, 0,   0,  0x1d1d1d1d ),
    req( 'rd', 0xe, 0x10e0, 0, 0          ), resp( 'rd', 0xe, 0,   0,  0x1e1e1e1e ),
    req( 'rd', 0xf, 0x10f0, 0, 0          ), resp( 'rd', 0xf, 0,   0,  0x1f1f1f1f ),
  ]

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# LAB TASK: Add more directed test cases
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

#-------------------------------------------------------------------------
# Conflict Miss for Base and Alt Test Case
#------------------------------------------------------------------------
def conflict_miss_both():
  return [
  # type opq addr len data type opq test len data
    req( 'wr', 0x4, 0x3000, 0, 0x0000feed ), resp( 'wr', 0x4, 0, 0, 0 ),
    req( 'wr', 0x0, 0x1000, 0, 0xcafecafe ), resp( 'wr', 0x0, 0, 0, 0 ),
    req( 'rd', 0x1, 0x1000, 0, 0 ),          resp( 'rd', 0x1, 1, 0, 0xcafecafe ),
    req( 'wr', 0x2, 0x2000, 0, 0x000c0ffe ), resp( 'wr', 0x2, 0, 0, 0 ),
    req( 'rd', 0x3, 0x2000, 0, 0 ),          resp( 'rd', 0x3, 1, 0, 0x000c0ffe ),
    req( 'rd', 0x4, 0x3000, 0, 0x0000feed ), resp( 'rd', 0x4, 0, 0, 0x0000feed ),
  ]

#-------------------------------------------------------------------------
# Reading/Writing to all four words in a Cache Line Test Case
#-------------------------------------------------------------------------
def read_write_full_line():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'wr', 0x0, 0x1000, 0, 0xcafecafe ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'wr', 0x0, 0x1004, 0, 0x000c0ffe ), resp( 'wr', 0x0, 1,   0,  0          ),
    req( 'wr', 0x0, 0x1008, 0, 0xdead0000 ), resp( 'wr', 0x0, 1,   0,  0          ),
    req( 'wr', 0x0, 0x100c, 0, 0x0000beef ), resp( 'wr', 0x0, 1,   0,  0          ),
    
    req( 'rd', 0x0, 0x1000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0xcafecafe ),
    req( 'rd', 0x0, 0x1004, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0x000c0ffe ),
    req( 'rd', 0x0, 0x1008, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0xdead0000 ),
    req( 'rd', 0x0, 0x100c, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0x0000beef ), 
  ]

#-------------------------------------------------------------------------
# Writing to every line of the cache Test Case
#-------------------------------------------------------------------------
def write_every_line():
  return [
    # type opq addr len data type opq test len data
    req( 'wr', 0x0, 0x0000, 0, 0x00000000 ), resp( 'wr', 0x0, 0, 0, 0 ),
    req( 'wr', 0x1, 0x1010, 0, 0x01010101 ), resp( 'wr', 0x1, 0, 0, 0 ),
    req( 'wr', 0x2, 0x2020, 0, 0x02020202 ), resp( 'wr', 0x2, 0, 0, 0 ),
    req( 'wr', 0x3, 0x3030, 0, 0x03030303 ), resp( 'wr', 0x3, 0, 0, 0 ),
    req( 'wr', 0x4, 0x4040, 0, 0x04040404 ), resp( 'wr', 0x4, 0, 0, 0 ),
    req( 'wr', 0x5, 0x5050, 0, 0x05050505 ), resp( 'wr', 0x5, 0, 0, 0 ),
    req( 'wr', 0x6, 0x6060, 0, 0x06060606 ), resp( 'wr', 0x6, 0, 0, 0 ),
    req( 'wr', 0x7, 0x7070, 0, 0x07070707 ), resp( 'wr', 0x7, 0, 0, 0 ),
    req( 'wr', 0x8, 0x8080, 0, 0x08080808 ), resp( 'wr', 0x8, 0, 0, 0 ),
    req( 'wr', 0x9, 0x9090, 0, 0x09090909 ), resp( 'wr', 0x9, 0, 0, 0 ),
    req( 'wr', 0xa, 0xa0a0, 0, 0x0a0a0a0a ), resp( 'wr', 0xa, 0, 0, 0 ),
    req( 'wr', 0xb, 0xb0b0, 0, 0x0b0b0b0b ), resp( 'wr', 0xb, 0, 0, 0 ),
    req( 'wr', 0xc, 0xc0c0, 0, 0x0c0c0c0c ), resp( 'wr', 0xc, 0, 0, 0 ),
    req( 'wr', 0xd, 0xd0d0, 0, 0x0d0d0d0d ), resp( 'wr', 0xd, 0, 0, 0 ),
    req( 'wr', 0xe, 0xe0e0, 0, 0x0e0e0e0e ), resp( 'wr', 0xe, 0, 0, 0 ),
    req( 'wr', 0xf, 0xf0f0, 0, 0x0f0f0f0f ), resp( 'wr', 0xf, 0, 0, 0 ),
    
    req( 'rd', 0x0, 0x0000, 0, 0x00000000 ), resp( 'rd', 0x0, 1, 0, 0x00000000 ),
    req( 'rd', 0x1, 0x1010, 0, 0x01010101 ), resp( 'rd', 0x1, 1, 0, 0x01010101 ),
    req( 'rd', 0x2, 0x2020, 0, 0x02020202 ), resp( 'rd', 0x2, 1, 0, 0x02020202 ),
    req( 'rd', 0x3, 0x3030, 0, 0x03030303 ), resp( 'rd', 0x3, 1, 0, 0x03030303 ),
    req( 'rd', 0x4, 0x4040, 0, 0x04040404 ), resp( 'rd', 0x4, 1, 0, 0x04040404 ),
    req( 'rd', 0x5, 0x5050, 0, 0x05050505 ), resp( 'rd', 0x5, 1, 0, 0x05050505 ),
    req( 'rd', 0x6, 0x6060, 0, 0x06060606 ), resp( 'rd', 0x6, 1, 0, 0x06060606 ),
    req( 'rd', 0x7, 0x7070, 0, 0x07070707 ), resp( 'rd', 0x7, 1, 0, 0x07070707 ),
    req( 'rd', 0x8, 0x8080, 0, 0x08080808 ), resp( 'rd', 0x8, 1, 0, 0x08080808 ),
    req( 'rd', 0x9, 0x9090, 0, 0x09090909 ), resp( 'rd', 0x9, 1, 0, 0x09090909 ),
    req( 'rd', 0xa, 0xa0a0, 0, 0x0a0a0a0a ), resp( 'rd', 0xa, 1, 0, 0x0a0a0a0a ),
    req( 'rd', 0xb, 0xb0b0, 0, 0x0b0b0b0b ), resp( 'rd', 0xb, 1, 0, 0x0b0b0b0b ),
    req( 'rd', 0xc, 0xc0c0, 0, 0x0c0c0c0c ), resp( 'rd', 0xc, 1, 0, 0x0c0c0c0c ),
    req( 'rd', 0xd, 0xd0d0, 0, 0x0d0d0d0d ), resp( 'rd', 0xd, 1, 0, 0x0d0d0d0d ),
    req( 'rd', 0xe, 0xe0e0, 0, 0x0e0e0e0e ), resp( 'rd', 0xe, 1, 0, 0x0e0e0e0e ),
    req( 'rd', 0xf, 0xf0f0, 0, 0x0f0f0f0f ), resp( 'rd', 0xf, 1, 0, 0x0f0f0f0f ),
  ]

#-------------------------------------------------------------------------
# Capacity Miss Test Case
#-------------------------------------------------------------------------
def capacity_miss():
  return [
    # type opq addr len data type opq test len data
    req( 'wr', 0x0, 0x0000, 0, 0x00000000 ), resp( 'wr', 0x0, 0, 0, 0 ),
    req( 'wr', 0x1, 0x1010, 0, 0x01010101 ), resp( 'wr', 0x1, 0, 0, 0 ),    
    req( 'wr', 0x2, 0x2020, 0, 0x02020202 ), resp( 'wr', 0x2, 0, 0, 0 ),
    req( 'wr', 0x3, 0x3030, 0, 0x03030303 ), resp( 'wr', 0x3, 0, 0, 0 ),
    req( 'wr', 0x4, 0x4040, 0, 0x04040404 ), resp( 'wr', 0x4, 0, 0, 0 ),
    req( 'wr', 0x5, 0x5050, 0, 0x05050505 ), resp( 'wr', 0x5, 0, 0, 0 ),
    req( 'wr', 0x6, 0x6060, 0, 0x06060606 ), resp( 'wr', 0x6, 0, 0, 0 ),
    req( 'wr', 0x7, 0x7070, 0, 0x07070707 ), resp( 'wr', 0x7, 0, 0, 0 ),
    req( 'wr', 0x8, 0x8080, 0, 0x08080808 ), resp( 'wr', 0x8, 0, 0, 0 ),
    req( 'wr', 0x9, 0x9090, 0, 0x09090909 ), resp( 'wr', 0x9, 0, 0, 0 ),
    req( 'wr', 0xa, 0xa0a0, 0, 0x0a0a0a0a ), resp( 'wr', 0xa, 0, 0, 0 ),
    req( 'wr', 0xb, 0xb0b0, 0, 0x0b0b0b0b ), resp( 'wr', 0xb, 0, 0, 0 ),
    req( 'wr', 0xc, 0xc0c0, 0, 0x0c0c0c0c ), resp( 'wr', 0xc, 0, 0, 0 ),
    req( 'wr', 0xd, 0xd0d0, 0, 0x0d0d0d0d ), resp( 'wr', 0xd, 0, 0, 0 ),
    req( 'wr', 0xe, 0xe0e0, 0, 0x0e0e0e0e ), resp( 'wr', 0xe, 0, 0, 0 ),
    req( 'wr', 0xf, 0xf0f0, 0, 0x0f0f0f0f ), resp( 'wr', 0xf, 0, 0, 0 ),

    req( 'wr', 0x0, 0x1100, 0, 0x10101010 ), resp( 'wr', 0x0, 0, 0, 0 ),
    req( 'wr', 0x1, 0x1110, 0, 0x11111111 ), resp( 'wr', 0x1, 0, 0, 0 ),
    req( 'wr', 0x2, 0x1120, 0, 0x12121212 ), resp( 'wr', 0x2, 0, 0, 0 ),
    req( 'wr', 0x3, 0x1130, 0, 0x13131313 ), resp( 'wr', 0x3, 0, 0, 0 ),
    req( 'wr', 0x4, 0x1140, 0, 0x14141414 ), resp( 'wr', 0x4, 0, 0, 0 ),
    req( 'wr', 0x5, 0x1150, 0, 0x15151515 ), resp( 'wr', 0x5, 0, 0, 0 ),
    req( 'wr', 0x6, 0x1160, 0, 0x16161616 ), resp( 'wr', 0x6, 0, 0, 0 ),
    req( 'wr', 0x7, 0x1170, 0, 0x17171717 ), resp( 'wr', 0x7, 0, 0, 0 ),
    req( 'wr', 0x8, 0x1180, 0, 0x18181818 ), resp( 'wr', 0x8, 0, 0, 0 ),
    req( 'wr', 0x9, 0x1190, 0, 0x19191919 ), resp( 'wr', 0x9, 0, 0, 0 ),
    req( 'wr', 0xa, 0x11a0, 0, 0x1a1a1a1a ), resp( 'wr', 0xa, 0, 0, 0 ),
    req( 'wr', 0xb, 0x11b0, 0, 0x1b1b1b1b ), resp( 'wr', 0xb, 0, 0, 0 ),
    req( 'wr', 0xc, 0x11c0, 0, 0x1c1c1c1c ), resp( 'wr', 0xc, 0, 0, 0 ),
    req( 'wr', 0xd, 0x11d0, 0, 0x1d1d1d1d ), resp( 'wr', 0xd, 0, 0, 0 ),
    req( 'wr', 0xe, 0x11e0, 0, 0x1e1e1e1e ), resp( 'wr', 0xe, 0, 0, 0 ),
    req( 'wr', 0xf, 0x11f0, 0, 0x1f1f1f1f ), resp( 'wr', 0xf, 0, 0, 0 ),
    
    req( 'rd', 0x0, 0x0000, 0, 0 ), resp( 'rd', 0x0, 0, 0, 0x00000000),
    req( 'rd', 0x1, 0x1010, 0, 0 ), resp( 'rd', 0x1, 0, 0, 0x01010101),
    req( 'rd', 0x2, 0x2020, 0, 0 ), resp( 'rd', 0x2, 0, 0, 0x02020202),
    req( 'rd', 0x3, 0x3030, 0, 0 ), resp( 'rd', 0x3, 0, 0, 0x03030303),
    req( 'rd', 0x4, 0x4040, 0, 0 ), resp( 'rd', 0x4, 0, 0, 0x04040404),
    req( 'rd', 0x5, 0x5050, 0, 0 ), resp( 'rd', 0x5, 0, 0, 0x05050505),
    req( 'rd', 0x6, 0x6060, 0, 0 ), resp( 'rd', 0x6, 0, 0, 0x06060606),
    req( 'rd', 0x7, 0x7070, 0, 0 ), resp( 'rd', 0x7, 0, 0, 0x07070707),
    req( 'rd', 0x8, 0x8080, 0, 0 ), resp( 'rd', 0x8, 0, 0, 0x08080808),
    req( 'rd', 0x9, 0x9090, 0, 0 ), resp( 'rd', 0x9, 0, 0, 0x09090909),
    req( 'rd', 0xa, 0xa0a0, 0, 0 ), resp( 'rd', 0xa, 0, 0, 0x0a0a0a0a),
    req( 'rd', 0xb, 0xb0b0, 0, 0 ), resp( 'rd', 0xb, 0, 0, 0x0b0b0b0b),
    req( 'rd', 0xc, 0xc0c0, 0, 0 ), resp( 'rd', 0xc, 0, 0, 0x0c0c0c0c),
    req( 'rd', 0xd, 0xd0d0, 0, 0 ), resp( 'rd', 0xd, 0, 0, 0x0d0d0d0d),
    req( 'rd', 0xe, 0xe0e0, 0, 0 ), resp( 'rd', 0xe, 0, 0, 0x0e0e0e0e),
    req( 'rd', 0xf, 0xf0f0, 0, 0 ), resp( 'rd', 0xf, 0, 0, 0x0f0f0f0f),
    
  ]

#-------------------------------------------------------------------------
# Generic tests
#-------------------------------------------------------------------------

test_case_table_generic = mk_test_case_table([
  (                                    "msg_func                    mem_data_func stall lat src sink"),

  [ "write_init_word",                  write_init_word,            None,         0.0,  0,  0,  0    ],
  [ "write_init_multi_word",            write_init_multi_word,      None,         0.0,  0,  0,  0    ],
  [ "write_init_cacheline",             write_init_cacheline,       None,         0.0,  0,  0,  0    ],
  [ "write_init_multi_cacheline",       write_init_multi_cacheline, None,         0.0,  0,  0,  0    ],
  [ "write_init_multi_word_sink_delay", write_init_multi_word,      None,         0.0,  0,  0,  10   ],
  [ "write_init_multi_word_src_delay",  write_init_multi_word,      None,         0.0,  0,  10, 0    ],

  [ "read_hit_word",                    read_hit_word,              None,         0.0,  0,  0,  0    ],
  [ "read_hit_multi_word",              read_hit_multi_word,        None,         0.0,  0,  0,  0    ],
  [ "read_hit_cacheline",               read_hit_cacheline,         None,         0.0,  0,  0,  0    ],
  [ "read_hit_multi_cacheline",         read_hit_multi_cacheline,   None,         0.0,  0,  0,  0    ],
  [ "read_hit_multi_word_sink_delay",   read_hit_multi_word,        None,         0.0,  0,  0,  10   ],
  [ "read_hit_multi_word_src_delay",    read_hit_multi_word,        None,         0.0,  0,  10, 0    ],

  [ "write_hit_word",                   write_hit_word,             None,         0.0,  0,  0,  0    ],
  [ "write_hit_multi_word",             write_hit_multi_word,       None,         0.0,  0,  0,  0    ],
  [ "write_hit_cacheline",              write_hit_cacheline,        None,         0.0,  0,  0,  0    ],
  [ "write_hit_multi_cacheline",        write_hit_multi_cacheline,  None,         0.0,  0,  0,  0    ],
  [ "write_hit_multi_word_sink_delay",  write_hit_multi_word,       None,         0.0,  0,  0,  10   ],
  [ "write_hit_multi_word_src_delay",   write_hit_multi_word,       None,         0.0,  0,  10, 0    ],

  [ "read_miss_word",                   read_miss_word,             data_64B,     0.0,  0,  0,  0    ],
  [ "read_miss_multi_word",             read_miss_multi_word,       data_64B,     0.0,  0,  0,  0    ],
  [ "read_miss_cacheline",              read_miss_cacheline,        data_64B,     0.0,  0,  0,  0    ],
  [ "read_miss_multi_cacheline",        read_miss_multi_cacheline,  data_512B,    0.0,  0,  0,  0    ],
  [ "read_miss_multi_word_sink_delay",  read_miss_multi_word,       data_64B,     0.9,  3,  0,  10   ],
  [ "read_miss_multi_word_src_delay",   read_miss_multi_word,       data_64B,     0.9,  3,  10, 0    ],

  [ "write_miss_word",                  write_miss_word,            data_64B,     0.0,  0,  0,  0    ],
  [ "write_miss_multi_word",            write_miss_multi_word,      data_64B,     0.0,  0,  0,  0    ],
  [ "write_miss_cacheline",             write_miss_cacheline,       data_64B,     0.0,  0,  0,  0    ],
  [ "write_miss_multi_cacheline",       write_miss_multi_cacheline, data_512B,    0.0,  0,  0,  0    ],
  [ "write_miss_multi_word_sink_delay", write_miss_multi_word,      data_64B,     0.9,  3,  0,  10   ],
  [ "write_miss_multi_word_src_delay",  write_miss_multi_word,      data_64B,     0.9,  3,  10, 0    ],

  [ "evict_word",                       evict_word,                 data_512B,    0.0,  0,  0,  0    ],
  [ "evict_multi_word",                 evict_multi_word,           data_512B,    0.0,  0,  0,  0    ],
  [ "evict_cacheline",                  evict_cacheline,            data_512B,    0.0,  0,  0,  0    ],
  [ "evict_multi_cacheline",            evict_multi_cacheline,      data_512B,    0.0,  0,  0,  0    ],
  [ "evict_multi_word_sink_delay",      evict_multi_word,           data_512B,    0.9,  3,  0,  10   ],
  [ "evict_multi_word_src_delay",       evict_multi_word,           data_512B,    0.9,  3,  10, 0    ],

  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # LAB TASK: Add more entries to test case table
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  [ "conflict_miss_both",               conflict_miss_both,         None,         0.0,  0,  0,  0     ],
  [ "conflict_miss_both_sink_delay",    conflict_miss_both,         None,         0.9,  3,  0,  3     ],
  [ "conflict_miss_both_src_delay",     conflict_miss_both,         None,         0.9,  3,  9,  0     ],
  [ "read_write_full_line",             read_write_full_line,       None,         0.0,  0,  0,  0     ],
  [ "write_every_line",                 write_every_line,           None,         0.0,  0,  0,  0     ],
  [ "capacity_miss",                    capacity_miss,              None,         0.0,  0,  0,  0     ],
])

@pytest.mark.parametrize( **test_case_table_generic )
def test_generic( test_params, cmdline_opts ):
  run_test( CacheFL(), test_params, cmdline_opts, cmp_wo_test_field )

#-------------------------------------------------------------------------
# Test Case with Random Addresses and Data
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
# cmp_wo_test_field
#-------------------------------------------------------------------------
# The test field in the cache response is used to indicate if the
# corresponding memory access resulted in a hit or a miss. However, the
# FL model always sets the test field to zero since it does not track
# hits/misses. So we need to do something special to ignore the test
# field when using the FL model. To do this, we can pass in a specialized
# comparison function to the StreamSinkFL.

def cmp_wo_test_field( msg, ref ):

  # check type, len, and opaque fields

  if msg.type_ != ref.type_:
    return False

  if msg.len != ref.len:
    return False

  if msg.opaque != msg.opaque:
    return False

  # only check data on a read

  if (ref.type_ == MemMsgType.READ):
    if ref.data != msg.data:
      return False

  # do not check the test field

  return True

#-------------------------------------------------------------------------
# Data initialization function
#-------------------------------------------------------------------------
# Function that can be used to initialize 512 bytes (128 words) of data.
# The function returns a list in this format:
#
#  [ addr0, data0, addr1, data1, addr2, data2, ... ]
#
# This list can be processed such that addr0 is initialized with data0,
# addr1 is initialized with data1, and so on.
#
# We choose data which is a direct function of the address. So the data
# stored at addr0 will be the concatentation of 0xabcd in the top 16 bits
# and the bottom 16 bits of the address. So the data at address
# 0x00001024 will be 0xabcd1024. This makes it easy to always know what
# the correct data is for any given address, but also makes sure all of
# the data is unique.

def data_1KB():
  data = []
  for i in range(256):
    data.extend([0x00001000+i*4,0xabcd1000+i*4])
  return data

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# LAB TASK: Add random test cases
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

#-------------------------------------------------------------------------
# Test Case for Random Reads
#-------------------------------------------------------------------------
def random_read_msgs():

  # Create list of 100 random request messages with the corresponding
  # correct response message.

  msgs = []
  for i in range(100):

    # Choose a random index to read

    idx = randint(0,256)

    # Create address and data. Notice how we turn the random index into
    # an actual address. We multiply the index by four and then add it to
    # the base address which is 0x00001000. We can figure out the correct
    # data from the address.

    addr = 0x00001000+idx*4
    data = 0xabcd1000+idx*4

    # Create a request/response pair.

    msgs.extend([
      req( 'rd', i, addr, 0, 0 ), resp( 'rd', i, 0, 0, data ),
    ])

  return msgs

#---------------------------------------------------------------------------
# Test Case for Random Writes
#---------------------------------------------------------------------------
def random_write_msgs():

  # Create list of 100 random request messages with the corresponding
  # correct response message.
  
  msgs = []
  mem = data_1KB()
  for i in range(100):

    # Choose a random index to read

    idx = randint(0,256)

    # Create address and data. Notice how we turn the random index into
    # an actual address. We multiply the index by four and then add it to
    # the base address which is 0x00001000. We can figure out the correct
    # data from the address.

    addr = 0x00001000+idx*4
    data = 0xabcd1000+idx*4
    new_data = randint(0,256) + 0xabcd1000

    # Create a request/response pair.

    msgs.extend([
      req( 'wr', i, addr, 0, new_data ), resp( 'wr', i, 0, 0, new_data ),
      req( 'rd', i, addr, 0, 0 ), resp( 'rd', i, 0, 0, new_data ),
    ])

  return msgs

#---------------------------------------------------------------------------
# Test Case for Random Reads and Writes
#---------------------------------------------------------------------------
def random_rw_msgs():

  # Create list of 100 random request messages with the corresponding
  # correct response message.

  msgs = []
  mem = data_1KB()
  
  for i in range(100):

    # Choose a random index to read

    idx = randint(0,256)

    # Choose read or write
    is_read = randint(0,1)

    # Create address and data. Notice how we turn the random index into
    # an actual address. We multiply the index by four and then add it to
    # the base address which is 0x00001000. We can figure out the correct
    # data from the address.

    addr = 0x00001000+idx*4
    data = 0xabcd1000+idx*4
    new_data = randint(0,256) + 0xabcd1000

    # Create a request/response pair.

    if is_read:
      msgs.extend([
        req( 'rd', i, addr, 0, 0 ), resp( 'rd', i, 0, 0, mem[idx*2 + 1] ),
      ])
    else:
       msgs.extend([
         req( 'wr', i, addr, 0, new_data), resp( 'wr', i, 0, 0, new_data),
       ]) 
       mem[2*idx + 1] = new_data

  return msgs

#---------------------------------------------------------------------------
# Test Case for Random Mixed Request
#---------------------------------------------------------------------------
def random_simple_read_msgs():

  # Create list of 100 random request messages with the corresponding
  # correct response message.
  msgs = []
  mem = data_1KB()

  for i in range(100):
    # Choose a random index to read
    idx = randint(0,256)
    # Choose read or write
    # Create address and data. Notice how we turn the random index into
    # an actual address. We multiply the index by four and then add it to
    # the base address which is 0x00001000. We can figure out the correct
    # data from the address.
  
    addr = 0x00001000+idx*4
    data = 0xabcd1000 + idx*4

    # Create a request/response pair.
    msgs.extend([
      req( 'rd', i, addr, 0, 0 ), resp( 'rd', i, 0, 0, mem[idx*2 + 1] ),
    ])
  return msgs

#---------------------------------------------------------------------------
# Test Case for Random Mixed Read Write Request
#---------------------------------------------------------------------------
def random_simple_rw_msgs():
  # Create list of 100 random request messages with the corresponding
  # correct response message.
  msgs = []
  mem = data_1KB()
  for i in range(100):
    # Choose a random index to read
    idx = randint(0,256)

    # Choose read or write
    is_read = randint(0,1)
    # Create address and data. Notice how we turn the random index into
    # an actual address. We multiply the index by four and then add it to
    # the base address which is 0x00001000. We can figure out the correct
    # data from the address.
    addr = 0x00001000+idx*4
    data = 0xabcd1000 + idx*4

    new_data = randint(0,256) + 0xabcd1000
    # Create a request/response pair.
    if is_read:
      msgs.extend([
        req( 'rd', i, addr, 0, 0 ), resp( 'rd', i, 0, 0, mem[idx*2 + 1] ),
      ])
    else:
      msgs.extend([
        req( 'wr', i, addr, 0, new_data), resp( 'wr', i, 0, 0, new_data),
      ])
      mem[2*idx + 1] = new_data
  return msgs

#---------------------------------------------------------------------------
# Test Case for Random Full Request
#---------------------------------------------------------------------------
def random_full_msgs():
  # Create list of 200 random request messages with the corresponding
  # correct response message.
  msgs = []
  mem = data_1KB()

  for i in range(200):
    # Choose a random index to read
    idx = randint(0,256)
    
    # Choose read or write
    is_read = randint(0,1)
    
    # Create address and data. Notice how we turn the random index into
    # an actual address. We multiply the index by four and then add it to
    # the base address which is 0x00001000. We can figure out the correct
    # data from the address.
    addr = 0x00001000+idx*4
    data = 0xabcd1000 + idx*4
    new_data = randint(0,256) + 0xabcd1000
   
    # Create a request/response pair.
    if is_read:
      msgs.extend([
        req( 'rd', i, addr, 0, 0 ), resp( 'rd', i, 0, 0, mem[idx*2 + 1] ),
      ])
    else:
      msgs.extend([
        req( 'wr', i, addr, 0, new_data), resp( 'wr', i, 0, 0, new_data),
      ])
      mem[2*idx + 1] = new_data
  return msgs

#---------------------------------------------------------------------------
# Test Case for Unit Stride
#---------------------------------------------------------------------------
def random_unit_stride_msgs():
  # Create list of 200 random request messages with the corresponding
  # correct response message.
  msgs = []
  mem = data_1KB()
  
  for i in range(200):
    # Choose a random index to read
    idx = i % 256
    # Choose read or write
    is_read = randint(0,1)
    # Create address and data. Notice how we turn the random index into
    # an actual address. We multiply the index by four and then add it to
    # the base address which is 0x00001000. We can figure out the correct
    # data from the address.
    addr = 0x00001000+idx*4
    data = 0xabcd1000 + idx*4
    new_data = randint(0,256) + 0xabcd1000

    # Create a request/response pair.
    if is_read:
      msgs.extend([
        req( 'rd', i, addr, 0, 0 ), resp( 'rd', i, 0, 0, mem[idx*2 + 1] ),
      ])
    else:
      msgs.extend([
        req( 'wr', i, addr, 0, new_data), resp( 'wr', i, 0, 0, new_data),
      ])
      mem[2*idx + 1] = new_data
  return msgs

#---------------------------------------------------------------------------
# Test Case for Random Stride
#---------------------------------------------------------------------------
def random_stride_msgs():
  # Create list of 100 random request messages with the corresponding
  # correct response message.
  msgs = []
  mem = data_1KB()
  stride = 4

  for i in range(100):
    # Choose a random index to read
    idx = (i * stride) % 256
     
    # Choose read or write
    is_read = randint(0,1)
     
    # Create address and data. Notice how we turn the random index into
    # an actual address. We multiply the index by four and then add it to
    # the base address which is 0x00001000. We can figure out the correct
    # data from the address.
    addr = 0x00001000+idx*4
    data = 0xabcd1000 + idx*4
    new_data = randint(0,256) + 0xabcd1000
    
    # Create a request/response pair.
    if is_read:
       msgs.extend([
         req( 'rd', i, addr, 0, 0 ), resp( 'rd', i, 0, 0, mem[idx*2 + 1] ),
       ])
    else:
       msgs.extend([
          req( 'wr', i, addr, 0, new_data), resp( 'wr', i, 0, 0, new_data),
       ])
       mem[2*idx + 1] = new_data
  return msgs

#---------------------------------------------------------------------------
# Test Case for Random Mixed Locality
#---------------------------------------------------------------------------
def random_mixed_locality_msgs():
  # Create list of 100 random request messages with the corresponding
  # correct response message.
  msgs = []
  mem = data_1KB()
  shared_indices = [randint(0,256) for _ in range(4)]
  
  for idx in shared_indices:
    mem[idx*2 + 1] = randint(0,256) + 0xabcd1000
    for i in range(100):
      # Choose a random index to read
      idx = i % 256
      # Choose read or write
      is_read = randint(0,1)

      # Create address and data. Notice how we turn the random index into
      # an actual address. We multiply the index by four and then add it to
      # the base address which is 0x00001000. We can figure out the correct
      # data from the address.
      addr = 0x00001000+idx*4
      data = 0xabcd1000 + idx*4
      new_data = randint(0,256) + 0xabcd1000

      # Create a request/response pair.
      if is_read:
        msgs.extend([
          req( 'rd', i, addr, 0, 0 ), resp( 'rd', i, 0, 0, mem[idx*2 + 1] ),
        ])
      else:
        msgs.extend([
          req( 'wr', i, addr, 0, new_data), resp( 'wr', i, 0, 0, new_data),
        ])
        mem[2*idx + 1] = new_data
  return msgs

test_case_table_random = mk_test_case_table([
  (                        "msg_func                     mem_data_func stall lat src sink"),

  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # LAB TASK: Add more entries to test case table
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  [ "random_read",           random_read_msgs,           data_1KB,     0.0,  0,  0,  0    ],
  [ "random_read_delays",    random_read_msgs,           data_1KB,     0.9,  3,  10, 10   ],
  [ "random_write",          random_write_msgs,          data_1KB,     0.0,  0,  0,  0    ],
  [ "random_write_delays",   random_write_msgs,          data_1KB,     0.9,  3,  10, 10   ],
  [ "random_rv",             random_rw_msgs,             data_1KB,     0.0,  0,  0,  0    ],
  [ "random_simple",         random_simple_read_msgs,    data_1KB,     0.0,  0,  0,  0    ],
  [ "random_smple_rv",       random_simple_rw_msgs,      data_1KB,     0.0,  0,  0,  0    ],
  [ "random_full_msg",       random_full_msgs,           data_1KB,     0.0,  0,  0,  0    ],
  [ "random_unit_stride",    random_unit_stride_msgs,    data_1KB,     0.0,  0,  0,  0    ],
  [ "random_stride",         random_stride_msgs,         data_1KB,     0.0,  0,  0,  0    ],
  [ "random_mixed_locality", random_mixed_locality_msgs, data_1KB,     0.0,  0,  0,  0    ],
])

@pytest.mark.parametrize( **test_case_table_random )
def test_random( test_params, cmdline_opts ):
  run_test( CacheFL(), test_params, cmdline_opts, cmp_wo_test_field )

#-------------------------------------------------------------------------
# Test Cases for Direct Mapped
#-------------------------------------------------------------------------

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# LAB TASK: Add directed test cases explicitly for direct mapped cache
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#-------------------------------------------------------------------------
# Read Hit Clean For Direct Mapped Test Case
#-------------------------------------------------------------------------
def read_hit_clean():
  return [
    # type opq addr len data type opq test len data
    req( 'in', 0x0, 0x0000, 0, 0xdeadbeef ), resp( 'in', 0x0, 0, 0, 0 ),
    req( 'rd', 0x1, 0x0000, 0, 0 ), resp( 'rd', 0x1, 1, 0, 0xdeadbeef ),
  ]

#-------------------------------------------------------------------------
# Write Hit Clean For Direct Mapped Test Case
#-------------------------------------------------------------------------
def write_hit_clean():
  return [
    # type opq addr len data type opq test len data
    req( 'in', 0x0, 0x0000, 0, 0xdeadbeef ), resp( 'in', 0x0, 0, 0, 0 ),
    req( 'wr', 0x1, 0x0000, 0, 0xcafecafe ), resp( 'wr', 0x1, 1, 0, 0 ),
    req( 'rd', 0x2, 0x0000, 0, 0 ), resp( 'rd', 0x2, 1, 0, 0xcafecafe ),
  ]

#-------------------------------------------------------------------------
# Conflict Miss For Direct Mapped Test Case
#-------------------------------------------------------------------------
def conflict_miss_dmap():
  return [
    # type opq addr len data type opq test len data
    req( 'wr', 0x0, 0x4000, 0, 0xcafecafe ), resp( 'wr', 0x0, 0, 0, 0 ),
    req( 'rd', 0x0, 0x4000, 0, 0 ), resp( 'rd', 0x0, 1, 0, 0xcafecafe ),
    req( 'wr', 0x0, 0x2000, 0, 0x000c0ffe ), resp( 'wr', 0x0, 0, 0, 0 ),
    req( 'rd', 0x0, 0x2000, 0, 0 ), resp( 'rd', 0x0, 1, 0, 0x000c0ffe ),
    req( 'rd', 0x0, 0x4000, 0, 0 ), resp( 'rd', 0x0, 0, 0, 0xcafecafe ), # conflict
  ]

test_case_table_dmap = mk_test_case_table([
  (                                   "msg_func                         mem_data_func stall lat src sink"),

  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # LAB TASK: Add more entries to test case table
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
   [ "conflict_miss_dmap",            conflict_miss_dmap,                data_64B,     0.0,  0,  0,  0    ],
   [ "conflict_miss_dmap_sink_delay", conflict_miss_dmap,                data_64B,     0.9,  5,  0,  9    ],
   [ "conflict_miss_dmap_src_delay",  conflict_miss_dmap,                data_64B,     0.9,  6,  3,  0    ],
   [ "read_hit_clean",                read_hit_clean,                    None,         0.0,  0,  0,  0    ],
   [ "read_hit_clean_sink_delay",     read_hit_clean,                    None,         0.9,  5,  0,  7    ],
   [ "read_hit_clean_src_delay",      read_hit_clean,                    None,         0.9,  5,  2,  0    ],
   [ "write_hit_clean",               write_hit_clean,                   None,         0.0,  0,  0,  0    ],
   [ "write_hit_clean_sink_delay",    write_hit_clean,                   None,         0.6,  0,  0,  2    ],
   [ "write_hit_clean_sink_delay",    write_hit_clean,                   None,         0.3,  0,  9,  0    ],

])

@pytest.mark.parametrize( **test_case_table_dmap )
def test_dmap( test_params, cmdline_opts ):
  run_test( CacheFL(), test_params, cmdline_opts, cmp_wo_test_field )

#-------------------------------------------------------------------------
# Test Cases for Set Associative
#-------------------------------------------------------------------------

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# LAB TASK: Add directed test cases explicitly for set associative cache
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

#-------------------------------------------------------------------------
# Conflict Miss For Direct Map But Not for Set Associative
#-------------------------------------------------------------------------
def conflict_miss_fake():
  return [
    #    type  opq  addr   len data                type  opq  test len data
    req( 'wr', 0x0, 0x4000, 0, 0xcafecafe ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'rd', 0x0, 0x4000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0xcafecafe ),
    req( 'wr', 0x0, 0x2000, 0, 0x000c0ffe ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'rd', 0x0, 0x2000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0x000c0ffe ),
    req( 'rd', 0x0, 0x4000, 0, 0          ), resp( 'rd', 0x0, 1,   0,  0xcafecafe ), # dmap conflict not sa conflict
  ]

test_case_table_sassoc = mk_test_case_table([
  (                                   "msg_func              mem_data_func    stall lat src sink"),

  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # LAB TASK: Add more entries to test case table
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
   [ "conflict_miss_fake",            conflict_miss_fake,   data_64B,         0.0,  0,  0,  0    ],
   [ "conflict_miss_fake_sink_delay", conflict_miss_fake,   data_64B,         0.9,  4,  0,  8    ],
   [ "conflict_miss_fake_src_delay",  conflict_miss_fake,   data_64B,         0.9,  4,  6,  0    ],
])

@pytest.mark.parametrize( **test_case_table_sassoc )
def test_sassoc( test_params, cmdline_opts ):
  run_test( CacheFL(), test_params, cmdline_opts, cmp_wo_test_field )

#-------------------------------------------------------------------------
# Banked cache test
#-------------------------------------------------------------------------
# This test case is to test if the bank offset is implemented correctly.
# The idea behind this test case is to differentiate between a cache with
# no bank bits and a design has one/two bank bits by looking at cache
# request hit/miss status.

# We first design a test case for 2-way set-associative cache. The last
# request should hit only if students implement the correct index bit to
# be [6:9]. If they implement the index bit to be [4:7] or [5:8], the
# last request is a miss, which is wrong. See below for explanation. This
# test case also works for the baseline direct-mapped cache.

# Direct-mapped
#
#   no bank(should fail):
#      idx
#   00 0000 0000
#   01 0000 0000
#   10 0000 0000
#   00 0000 0000
#   idx: 0, 0, 0 so the third one with tag 10 will evict the first one
#   with tag 00, and thus the fourth read will miss instead of hit.
#
#   4-bank(correct):
#    idx  bk
#   00 00 00 0000
#   01 00 00 0000
#   10 00 00 0000
#   00 00 00 0000
#   idx: 0, 4, 8 so the third one with tag 10 won't evict anything, and
#   thus the fourth read will hit.

# 2-way set-associative
#
#   no bank(should fail):
#        idx
#   00 0 000 0000
#   01 0 000 0000
#   10 0 000 0000
#   00 0 000 0000
#   idx: 0, 0, 0 so the third one with tag 10 will evict the first one
#   with tag 00, and thus the fourth read will miss instead of hit.
#
#   4-bank(correct):
#     idx  bk
#   0 0 00 00 0000
#   0 1 00 00 0000
#   1 0 00 00 0000
#   idx: 0, 4, 0 so the third one with tag 10 won't evict anything, and
#   thus the fourth read will hit.

def bank_test():
  return [
    #    type  opq  addr       len data                type  opq  test len data
    req( 'rd', 0x0, 0x00000000, 0, 0 ), resp( 'rd', 0x0, 0,   0,  0xdeadbeef ),
    req( 'rd', 0x1, 0x00000100, 0, 0 ), resp( 'rd', 0x1, 0,   0,  0x00c0ffee ),
    req( 'rd', 0x2, 0x00000200, 0, 0 ), resp( 'rd', 0x2, 0,   0,  0xffffffff ),
    req( 'rd', 0x3, 0x00000000, 0, 0 ), resp( 'rd', 0x3, 1,   0,  0xdeadbeef ),
  ]

def bank_test_data():
  return [
    # addr      data (in int)
    0x00000000, 0xdeadbeef,
    0x00000100, 0x00c0ffee,
    0x00000200, 0xffffffff,
  ]

test_case_table_bank = mk_test_case_table([
  (             "msg_func   mem_data_func   stall lat src sink"),
  [ "bank_test", bank_test, bank_test_data, 0.0,  0,  0,  0    ],
])

@pytest.mark.parametrize( **test_case_table_bank )
def test_bank( test_params, cmdline_opts ):
  run_test( CacheFL(), test_params, cmdline_opts, cmp_wo_test_field )
