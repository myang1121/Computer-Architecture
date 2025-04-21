#=========================================================================
# sw
#=========================================================================

import random

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)

from pymtl3 import *
from lab2_proc.test.inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 0x00002000
    csrr x2, mngr2proc < 0xdeadbeef
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sw   x2, 0(x1)
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    lw   x3, 0(x1)
    csrw proc2mngr, x3 > 0xdeadbeef

    .data
    .word 0x01020304
  """

# ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define additional directed and random test cases.
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

def dep_test():
    return """
      csrr x1, mngr2proc < 0x00002000
      csrr x2, mngr2proc < 0xdeadbeef
      nop
      nop
      nop
      nop
      nop
      nop
      nop
      nop
      sw   x2, 0(x1)
      lw   x3, 0(x1)
      csrw proc2mngr, x3 > 0xdeadbeef

      .data
      .word 0x01020304
    """
#-----------------------------------------------------------------------
# Another dependency test
#-----------------------------------------------------------------------
def dep_test_2():
    return """
      csrr x1, mngr2proc < 0x00002000
      csrr x2, mngr2proc < 0xdeadbeef
      lw   x4, 0(x1)
      sw   x4, 0(x1)
      sw   x2, 0(x1)
      lw   x3, 0(x1)
      csrw proc2mngr, x3 > 0xdeadbeef

      .data
      .word 0x01020304
    """

#------------------------------------------------------------------------
# gen_st_dest_dep_test
#------------------------------------------------------------------------

def gen_dest_dep_test():
  return [
    gen_st_dest_dep_test(5, "sw", 0x2000, 3, 3),
    gen_st_dest_dep_test(4, "sw", 0x2004, 4, 4),
    gen_st_dest_dep_test(3, "sw", 0x2008, 5, 5),
    gen_st_dest_dep_test(2, "sw", 0x200c, 6, 6),
    gen_st_dest_dep_test(1, "sw", 0x2010, 7, 7),
    gen_st_dest_dep_test(0, "sw", 0x2013, 8, 8),

    gen_word_data([
      0x00010203,
      0x04050607,
      0x08090a0b,
      0x0c0d0e0f,
      0x10111213,
      0x14151617,
    ])

  ]

#-------------------------------------------------------------------------
# gen_addr_test
#-------------------------------------------------------------------------

def gen_addr_test():
    return[
      
      # Test positive offset
      
      gen_st_value_test( "sw", 0,  0x00002000, 5,  5  ),
      gen_st_value_test( "sw", 4,  0x00002000, 6,  6  ),
      gen_st_value_test( "sw", 8,  0x00002000, 7,  7  ),
      gen_st_value_test( "sw", 12, 0x00002000, 8,  8  ),
      gen_st_value_test( "sw", 16, 0x00002000, 9,  9  ),
      gen_st_value_test( "sw", 20, 0x00002000, 10, 10 ),

      # Test negative offsets

      gen_st_value_test( "sw", -20, 0x00002014, 5, 5   ),
      gen_st_value_test( "sw", -16, 0x00002014, 6, 6   ),
      gen_st_value_test( "sw", -12, 0x00002014, 7, 7   ),
      gen_st_value_test( "sw",  -8, 0x00002014, 8, 8   ),
      gen_st_value_test( "sw",  -4, 0x00002014, 9, 9   ),
      gen_st_value_test( "sw",   0, 0x00002014, 10, 10 ),
      
      gen_word_data([
        0xdeadbeef,
        0x00010203,
        0x04050607,
        0x08090a0b,
        0x0c0d0e0f,
        0xcafecafe,
      ])

    ]
#------------------------------------------------------------------------
# gen_random_test
#------------------------------------------------------------------------

def gen_random_test():

  # Generate some random data

  data = []
  for i in range(128):
    data.append( random.randint(0,0xffffffff) )

  asm_code = []
  for i in range(100):

    a = random.randint(0,127)
    b = random.randint(0,127)
    src = random.randint(0,0xffffffff)

    base   = 0x2000 + (4*b)
    offset = 4*(a - b)
    result = 5


    asm_code.append( gen_st_value_test( "sw", offset, base, src, result ) )

  # Add the data to the end of the assembly code

  asm_code.append( gen_word_data( data ) )
  return asm_code
