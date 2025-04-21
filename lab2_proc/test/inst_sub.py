#=========================================================================
# sub
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
    csrr x1, mngr2proc < 5
    csrr x2, mngr2proc < 4
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sub x3, x1, x2
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 1
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

#-------------------------------------------------------------------------
# another test case
#------------------------------------------------------------------------
def dep_test():
  return """
      csrr x1, mngr2proc < 5
      csrr x2, mngr2proc < 4
      sub x1, x1, x2
      sub x3, x1, x2
      csrw proc2mngr, x3 > -3
    """

#------------------------------------------------------------------------
# gen_dest_dep_test
#------------------------------------------------------------------------

def gen_dest_dep_test():
  return [
    gen_rr_dest_dep_test (5, "sub", 8, 4, 4),
    gen_rr_dest_dep_test (4, "sub", 9, 2, 7),
    gen_rr_dest_dep_test (3, "sub", 4, 1, 3),
    gen_rr_dest_dep_test (2, "sub", 3, 2, 1),
    gen_rr_dest_dep_test (1, "sub", 6, 1, 5),
    gen_rr_dest_dep_test (0, "sub", 7, 7, 0),
  ]

#-----------------------------------------------------------------------
# gen_src0_dep_test
#-----------------------------------------------------------------------

def gen_src0_dep_test():
    return [
      gen_rr_src0_dep_test (5, "sub", 8, 1, 7),
      gen_rr_src0_dep_test (4, "sub", 9, 1, 8),
      gen_rr_src0_dep_test (3, "sub", 4, 1, 3),
      gen_rr_src0_dep_test (2, "sub", 3, 1, 2),
      gen_rr_src0_dep_test (1, "sub", 6, 1, 5),
      gen_rr_src0_dep_test (0, "sub", 7, 1, 6),
    ]

#----------------------------------------------------------------------
# gen_src1_dep_test
#----------------------------------------------------------------------

def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test (5, "sub", -8, -1, -7),
    gen_rr_src1_dep_test (4, "sub", -9, -1, -8),
    gen_rr_src1_dep_test (3, "sub", -4, -1, -3),
    gen_rr_src1_dep_test (2, "sub", -3, -1, -2),
    gen_rr_src1_dep_test (1, "sub", -6, -1, -5),
    gen_rr_src1_dep_test (0, "sub", -7, -1, -6),        
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_test
#-------------------------------------------------------------------------

def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "sub", -12, 2, -14 ),
    gen_rr_srcs_dep_test( 4, "sub", -13, 3, -16 ),
    gen_rr_srcs_dep_test( 3, "sub", -14, 4, -18 ),
    gen_rr_srcs_dep_test( 2, "sub", -15, 5, -20 ),
    gen_rr_srcs_dep_test( 1, "sub", -16, 6, -22 ),
    gen_rr_srcs_dep_test( 0, "sub", -17, 7, -24 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "sub", 25, 1, 24 ),
    gen_rr_src1_eq_dest_test( "sub", 26, 1, 25 ),
    gen_rr_src0_eq_src1_test( "sub", 27, 0 ),
    gen_rr_srcs_eq_dest_test( "sub", 28, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_rr_value_test( "sub", 0x80000000, 0x00000000,  0x80000000 ),
    gen_rr_value_test( "sub", 0x00000000, 0xffffffff,  0x00000001 ),
    gen_rr_value_test( "sub", 0x00000003, 0x00000007,  0xfffffffc ),

    gen_rr_value_test( "sub", 0x7fffffff, 0x00007fff, 0x7fff8000 ),
    gen_rr_value_test( "sub", 0x00007fff, 0x7fffffff, 0x80008000 ),
    gen_rr_value_test( "sub", 0x80000000, 0xffff8000, 0x80008000 ),
  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in range(100):
    src0 = b32( random.randint(0,0xffffffff) )
    src1 = b32( random.randint(0,0xffffffff) )
    dest = src0 - src1
    asm_code.append( gen_rr_value_test( "sub", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code

