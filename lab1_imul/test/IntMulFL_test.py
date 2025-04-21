#=========================================================================
# IntMulFL_test
#=========================================================================

import pytest

from random import randint

from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.stream import StreamSourceFL, StreamSinkFL

from lab1_imul.IntMulFL import IntMulFL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, imul ):

    # Instantiate models

    s.src  = StreamSourceFL( Bits64 )
    s.sink = StreamSinkFL( Bits32 )
    s.imul = imul

    # Connect

    s.src.ostream  //= s.imul.istream
    s.imul.ostream //= s.sink.istream

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.src.line_trace() + " > " + s.imul.line_trace() + " > " + s.sink.line_trace()

#-------------------------------------------------------------------------
# mk_imsg/mk_omsg
#-------------------------------------------------------------------------

# Make input message, truncate ints to ensure they fit in 32 bits.

def mk_imsg( a, b ):
  return concat( Bits32( a, trunc_int=True ), Bits32( b, trunc_int=True ) )

# Make output message, truncate ints to ensure they fit in 32 bits.

def mk_omsg( a ):
  return Bits32( a, trunc_int=True )

#----------------------------------------------------------------------
# Test Case: small positive * positive
#----------------------------------------------------------------------

small_pos_pos_msgs = [
  mk_imsg(  2,  3 ), mk_omsg(   6 ),
  mk_imsg(  4,  5 ), mk_omsg(  20 ),
  mk_imsg(  3,  4 ), mk_omsg(  12 ),
  mk_imsg( 10, 13 ), mk_omsg( 130 ),
  mk_imsg(  8,  7 ), mk_omsg(  56 ),
]

# ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define additional lists of input/output messages to create
# additional directed and random test cases.
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

#=========================================================================
# Directed Tests
#=========================================================================

mult_by_zero_msgs = [
  mk_imsg(  43, 0 ), mk_omsg( 0 ),
  mk_imsg( -3, 0 ),  mk_omsg( 0 ),
  mk_imsg(  0, 0 ),  mk_omsg( 0 ),
]

mult_by_one_msgs = [
  mk_imsg(  65, 1 ), mk_omsg( 65),
  mk_imsg( -7, 1 ),  mk_omsg( -7),
  mk_imsg(  1, 1 ),  mk_omsg( 1 ),
]

mult_by_neg_one_msgs = [
  mk_imsg( 76, -1 ), mk_omsg( -76),
  mk_imsg( -43, -1), mk_omsg(   43),
  mk_imsg(-1, 35),   mk_omsg(  -35),
]

small_neg_pos_msgs = [
  mk_imsg( -5, 3 ), mk_omsg( -15),
  mk_imsg( -7, 2 ), mk_omsg( -14),
]

small_pos_neg_msgs = [
  mk_imsg( -2, 2 ), mk_omsg(-4), 
  mk_imsg( -6, 3 ), mk_omsg(-18),
  mk_imsg( -5, 5 ), mk_omsg(-25),
]

small_neg_neg_msgs = [
  mk_imsg( -6, -4 ), mk_omsg(24),
  mk_imsg( -7, -3 ), mk_omsg(21),
  mk_imsg( -8, -9 ), mk_omsg(72),
]

large_pos_pos_msgs = [
  mk_imsg(1612, 1639), mk_omsg( 2642068 ),
  mk_imsg(3405, 4070), mk_omsg( 13858350 ),
  mk_imsg(9405, 16070), mk_omsg( 151138350 ),
]

large_pos_neg_msgs = [
  mk_imsg(46340, -40001), mk_omsg(-1853646340),
  mk_imsg(567430, -30689), mk_omsg(-17413859270),
  mk_imsg(33333, -33333), mk_omsg(-1111088889),
]

large_neg_pos_msgs = [
  mk_imsg(-904050, 2206), mk_omsg(-1994334300),
  mk_imsg(-23054, 12568), mk_omsg(-289742672),
  mk_imsg(-53686, 40000), mk_omsg(-2147440000),
]

large_neg_neg_msgs = [
  mk_imsg(-46000, -46000), mk_omsg(2116000000),
  mk_imsg(-32767, -55431), mk_omsg(1816307577),
  mk_imsg(-5321, -47891),  mk_omsg(254828011), 
]

low_bit_masked_msgs = [
  mk_imsg(-1,  1024),  mk_omsg(-1024),
  mk_imsg(6789, 16),   mk_omsg(108624),
  mk_imsg(31, 8),      mk_omsg(248),

]

mid_bit_masked_msgs = [
  mk_imsg(15, 9),       mk_omsg(135),
  mk_imsg(-1, 899),     mk_omsg(-899),
  mk_imsg(5, 385),      mk_omsg(1925),
]

sparse_zeros_msgs = [
  mk_imsg(2048, 1024),  mk_omsg(2097152),
  mk_imsg(1024, 8),     mk_omsg(8192),
  mk_imsg(4097, 2049),  mk_omsg(8394753),
]

dense_ones_msgs = [
  mk_imsg(2045, 16381), mk_omsg(33499145),
  mk_imsg(55, 59),      mk_omsg(3245),
  mk_imsg(24575, 47),   mk_omsg(1155025),
]

#=========================================================================
# Random Tests
#=========================================================================

# Random Mult with Zero, One, and Negative one
random_cases = []
for i in range(3):
    a = randint(0, 0xffffffff)
    b = randint(-1, 1)
    c = a*b
    random_cases.append( (mk_imsg(a, b), mk_omsg(c)) )

rand_zero_one_neg_msgs = []
for operands, result in random_cases:
    rand_zero_one_neg_msgs.extend( [operands, result])

# Random Mult with Two Small Positive
random_cases = []
for i in range(3):
    a = randint(0, 0xf)
    b = randint(0, 0xf)
    c = a*b
    random_cases.append( (mk_imsg(a, b), mk_omsg(c)) )

rand_small_pos_msgs = []
for operands, result in random_cases:
    rand_small_pos_msgs.extend( [operands, result])

# Random Mult with Small Positive and Negative
random_cases = []
for i in range(3):
    a = randint(0, 0xf)
    b = (randint(0, 0xf) * -1)
    c = a*b
    random_cases.append( (mk_imsg(a, b), mk_omsg(c)) )

rand_small_pos_neg_msgs = []
for operands, result in random_cases:
    rand_small_pos_neg_msgs.extend( [operands, result])

# Random Mult with Small Negative and Positive
random_cases = []
for i in range(3):
    a = (randint(0, 0xf) * -1)
    b = randint(0, 0xf)
    c = a*b
    random_cases.append( (mk_imsg(a, b), mk_omsg(c)) )

rand_small_neg_pos_msgs = []
for operands, result in random_cases:
    rand_small_neg_pos_msgs.extend( [operands, result])

# Random Mult with Small Negative and Negative
random_cases = []
for i in range(3):
    a = (randint(0, 0xf) * -1)
    b = (randint(0, 0xf) * -1)
    c = a*b
    random_cases.append( (mk_imsg(a, b), mk_omsg(c)) )

rand_small_neg_msgs = []
for operands, result in random_cases:
    rand_small_neg_msgs.extend( [operands, result])

# Random Mult with Two Large Positive
random_cases = []
for i in range(3):
    a = randint(0, 0x7fffffff)
    b = randint(0, 0x7fffffff)
    c = a*b
    random_cases.append( (mk_imsg(a, b), mk_omsg(c)) )

rand_large_pos_msgs = []
for operands, result in random_cases:
    rand_large_pos_msgs.extend( [operands, result])

# Random Mult with Large Positive and Negative
random_cases = []
for i in range(3):
    a = randint(0, 0x7fffffff)
    b = (randint(1, 0x7fffffff) * -1)
    c = a*b
    random_cases.append( (mk_imsg(a, b), mk_omsg(c)) )

rand_large_pos_neg_msgs = []
for operands, result in random_cases:
    rand_large_pos_neg_msgs.extend( [operands, result])

# Random Mult with Large Negative and Positive
random_cases = []
for i in range(3):
    a = (randint(1, 0x7fffffff) * -1)
    b = randint(0, 0x7fffffff)
    c = a*b
    random_cases.append( (mk_imsg(a, b), mk_omsg(c)) )

rand_large_neg_pos_msgs = []
for operands, result in random_cases:
    rand_large_neg_pos_msgs.extend( [operands, result])

# Random Mult with Large Negative and Negative
random_cases = []
for i in range(3):
    a = (randint(1, 0x7fffffff) * -1)
    b = (randint(0, 0x7fffffff) * -1)
    c = a*b
    random_cases.append( (mk_imsg(a, b), mk_omsg(c)) )

rand_large_neg_msgs = []
for operands, result in random_cases:
    rand_large_neg_msgs.extend( [operands, result])

# Random Low Bits Masked Off
random_cases = []
for i in range(3):
    shamt1 = randint(2, 31)
    shamt2 = randint(2, 31)
    a = randint(0, 0xffffffff)
    a = a << shamt1
    b = randint(0, 0xffffffff)
    b = b << shamt2
    c = a*b
    random_cases.append( (mk_imsg(a, b), mk_omsg(c)) )

rand_low_bit_mask_msgs = []
for operands, result in random_cases:
    rand_low_bit_mask_msgs.extend( [operands, result])

# Random High Bits Masked Off
random_cases = []
for i in range(3):
    shamt1 = randint(2, 31)
    shamt2 = randint(2, 31)
    a = randint(0, 0xffffffff)
    a = a >> shamt1
    b = randint(0, 0xffffffff)
    b = b >> shamt2
    c = a*b
    random_cases.append( (mk_imsg(a, b), mk_omsg(c)) )

rand_high_bit_mask_msgs = []
for operands, result in random_cases:
    rand_high_bit_mask_msgs.extend( [operands, result])

# Random Low and High Bits Masked Off
random_cases = []
for i in range(3):
    shamt1 = randint(2, 12)
    shamt2 = randint(2, 12)
    shamt3 = randint(2, 12)
    shamt4 = randint(2, 12)
    a = randint(0, 0xffffffff)
    a = a << shamt1
    a = a >> shamt2
    b = randint(0, 0xffffffff)
    b = b << shamt3
    b = b >> shamt4
    c = a*b
    random_cases.append( (mk_imsg(a, b), mk_omsg(c)) )

rand_low_high_mask_msgs = []
for operands, result in random_cases:
    rand_low_high_mask_msgs.extend( [operands, result])

# Random Sparse Numbers with Many Zeros
random_cases = []
for i in range(3):
    shamt1 = randint(0, 31)
    shamt2 = randint(0, 31)
    a = 1 << shamt1
    b = 1 << shamt2
    c = a*b
    random_cases.append( (mk_imsg(a, b), mk_omsg(c)) )

rand_sparse_zeros_msgs = []
for operands, result in random_cases:
    rand_sparse_zeros_msgs.extend( [operands, result])

# Random Dense Numbers with Many Ones
random_cases = []
for i in range(3):
    shamt1 = randint(0, 12)
    shamt2 = randint(0, 12)
    a = 0xffffffff << shamt1
    b = 0xffffffff << shamt2
    c = a*b
    random_cases.append( (mk_imsg(a, b), mk_omsg(c)) )

rand_dense_ones_msgs = []
for operands, result in random_cases:
    rand_dense_ones_msgs.extend( [operands, result])

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                      "msgs                   src_delay sink_delay"),
  [ "small_pos_pos",     small_pos_pos_msgs,     1,        2          ],

  ## ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to leverage the additional lists
  # of request/response messages defined above, but also to test
  # different source/sink random delays.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  [  "mult_by_zero",        mult_by_zero_msgs,        0,        0          ],
  [  "mult_by_one",         mult_by_one_msgs,         0,        0          ],
  [  "mult_by_neg_one",     mult_by_neg_one_msgs,     0,        0          ],
  [  "small_neg_pos",       small_neg_pos_msgs,       0,        0          ],
  [  "small_pos_neg",       small_pos_neg_msgs,       0,        0          ],
  [  "small_neg_neg",       small_neg_neg_msgs,       0,        0          ],
  [  "large_pos_pos",       large_pos_pos_msgs,       0,        0          ],
  [  "large_pos_neg",       large_pos_neg_msgs,       0,        0          ],
  [  "large_neg_pos",       large_neg_pos_msgs,       0,        0          ],
  [  "large_neg_neg",       large_neg_neg_msgs,       0,        0          ],
  [  "low_bit_masked",      low_bit_masked_msgs,      0,        0          ],
  [  "mid_bit_masked",      mid_bit_masked_msgs,      0,        0          ],
  [  "sparse_zeros",        sparse_zeros_msgs,        0,        0          ],
  [  "dense_ones",          dense_ones_msgs,          0,        0          ],
  [  "rand_zero_one_neg",   rand_zero_one_neg_msgs,   1,        2          ],
  [  "rand_small_pos",      rand_small_pos_msgs,      0,        0          ],
  [  "rand_small_pos_neg",  rand_small_pos_neg_msgs,  3,        3          ],
  [  "rand_small_neg_pos",  rand_small_neg_pos_msgs,  0,        0          ],
  [  "rand_small_neg",      rand_small_neg_msgs,      2,        4          ],
  [  "rand_large_pos",      rand_large_pos_msgs,      0,        0          ],
  [  "rand_large_pos_neg",  rand_large_pos_neg_msgs,  3,        5          ],
  [  "rand_large_neg_pos",  rand_large_neg_pos_msgs,  0,        0          ],
  [  "rand_large_neg",      rand_large_neg_msgs,      5,        1          ],
  [  "rand_low_bit_mask",   rand_low_bit_mask_msgs,   0,        0          ],
  [  "rand_high_bit_mask",  rand_high_bit_mask_msgs,  3,        4          ],
  [  "rand_low_high_mask",  rand_low_high_mask_msgs,  0,        0          ],
  [  "rand_sparse_zeros",   rand_sparse_zeros_msgs,   7,        6          ],
  [  "rand_dense_ones",     rand_dense_ones_msgs,     0,        0          ],
])
#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, cmdline_opts ):

  th = TestHarness( IntMulFL() )

  th.set_param("top.src.construct",
    msgs=test_params.msgs[::2],
    initial_delay=test_params.src_delay+3,
    interval_delay=test_params.src_delay )

  th.set_param("top.sink.construct",
    msgs=test_params.msgs[1::2],
    initial_delay=test_params.sink_delay+3,
    interval_delay=test_params.sink_delay )

  run_sim( th, cmdline_opts, duts=['imul'] )

