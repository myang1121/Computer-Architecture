#=========================================================================
# Net_test
#=========================================================================

import pytest

from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.stream import StreamSourceFL, StreamSinkFL

from lab4_sys.NetMsg import mk_net_msg
from lab4_sys.Net import Net

import random

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)


#-------------------------------------------------------------------------
# Message Types
#-------------------------------------------------------------------------

NetMsgType = mk_net_msg( 32 )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s ):

    # Instantiate models

    s.srcs  = [ StreamSourceFL( NetMsgType ) for _ in range(4) ]
    s.net   = Net( p_msg_nbits=44 )
    s.sinks = [ StreamSinkFL( NetMsgType, ordered=False ) for _ in range(4) ]

    # Connect

    for i in range(4):
      s.srcs[i].ostream //= s.net.istream[i]
      s.net.ostream[i]  //= s.sinks[i].istream

  def done( s ):
    for i in range(4):
      if not s.srcs[i].done() or not s.sinks[i].done():
        return False
    return True

  def line_trace( s ):
    srcs_str  = "|".join([ src.line_trace()  for src  in s.srcs  ])
    sinks_str = "|".join([ sink.line_trace() for sink in s.sinks ])
    return f"{srcs_str} > ({s.net.line_trace()}) > {sinks_str}"

#-------------------------------------------------------------------------
# test
#-------------------------------------------------------------------------

def test_basic( cmdline_opts ):

  th = TestHarness()

  msgs = [
    #           src  dest opaq  payload
    NetMsgType( 0,   0,   0x10, 0x10101010 ),
    NetMsgType( 0,   1,   0x20, 0x20202020 ),
    NetMsgType( 0,   2,   0x30, 0x30303030 ),
    NetMsgType( 0,   3,   0x40, 0x40404040 ),
  ]

  th.set_param("top.srcs[0].construct",  msgs=[ m for m in msgs if m.src  == 0 ] )
  th.set_param("top.srcs[1].construct",  msgs=[ m for m in msgs if m.src  == 1 ] )
  th.set_param("top.srcs[2].construct",  msgs=[ m for m in msgs if m.src  == 2 ] )
  th.set_param("top.srcs[3].construct",  msgs=[ m for m in msgs if m.src  == 3 ] )
  th.set_param("top.sinks[0].construct", msgs=[ m for m in msgs if m.dest == 0 ] )
  th.set_param("top.sinks[1].construct", msgs=[ m for m in msgs if m.dest == 1 ] )
  th.set_param("top.sinks[2].construct", msgs=[ m for m in msgs if m.dest == 2 ] )
  th.set_param("top.sinks[3].construct", msgs=[ m for m in msgs if m.dest == 3 ] )

  th.elaborate()

  run_sim( th, cmdline_opts, duts=['net'] )

#-------------------------------------------------------------------------
# Test Cases: Very Simple
#-------------------------------------------------------------------------

one = [
  #           src  dest opaq  payload
  NetMsgType( 0,   0,   0x10, 0x10101010 ),
]

rotate0 = [
  #           src  dest opaq  payload
  NetMsgType( 0,   0,   0x10, 0x10101010 ),
  NetMsgType( 1,   1,   0x11, 0x11111111 ),
  NetMsgType( 2,   2,   0x12, 0x12121212 ),
  NetMsgType( 3,   3,   0x13, 0x13131313 ),
]

rotate1 = [
  #           src  dest opaq  payload
  NetMsgType( 0,   3,   0x13, 0x13131313 ),
  NetMsgType( 1,   0,   0x10, 0x10101010 ),
  NetMsgType( 2,   1,   0x11, 0x11111111 ),
  NetMsgType( 3,   2,   0x12, 0x12121212 ),
]

rotate2 = [
  #           src  dest opaq  payload
  NetMsgType( 0,   2,   0x12, 0x12121212 ),
  NetMsgType( 1,   3,   0x13, 0x13131313 ),
  NetMsgType( 2,   0,   0x10, 0x10101010 ),
  NetMsgType( 3,   1,   0x11, 0x11111111 ),
]

rotate3 = [
  #           src  dest opaq  payload
  NetMsgType( 0,   1,   0x11, 0x11111111 ),
  NetMsgType( 1,   2,   0x12, 0x12121212 ),
  NetMsgType( 2,   3,   0x13, 0x13131313 ),
  NetMsgType( 3,   0,   0x10, 0x10101010 ),
]

all_to_dest0 = [
  #           src  dest opaq  payload
  NetMsgType( 0,   0,   0x10, 0x10101010 ),
  NetMsgType( 1,   0,   0x11, 0x11111111 ),
  NetMsgType( 2,   0,   0x12, 0x12121212 ),
  NetMsgType( 3,   0,   0x13, 0x13131313 ),
]

all_to_dest1 = [
  #           src  dest opaq  payload
  NetMsgType( 0,   1,   0x10, 0x10101010 ),
  NetMsgType( 1,   1,   0x11, 0x11111111 ),
  NetMsgType( 2,   1,   0x12, 0x12121212 ),
  NetMsgType( 3,   1,   0x13, 0x13131313 ),
]

all_to_dest2 = [
  #           src  dest opaq  payload
  NetMsgType( 0,   2,   0x10, 0x10101010 ),
  NetMsgType( 1,   2,   0x11, 0x11111111 ),
  NetMsgType( 2,   2,   0x12, 0x12121212 ),
  NetMsgType( 3,   2,   0x13, 0x13131313 ),
]

all_to_dest3 = [
  #           src  dest opaq  payload
  NetMsgType( 0,   3,   0x10, 0x10101010 ),
  NetMsgType( 1,   3,   0x11, 0x11111111 ),
  NetMsgType( 2,   3,   0x12, 0x12121212 ),
  NetMsgType( 3,   3,   0x13, 0x13131313 ),
]

#---------------------------------------------------------
# Additional Directed Tests
#---------------------------------------------------------
stream_to_dest0 = []
for i in range(16):
  msg = NetMsgType( src=0, dest=0, opaque=i, payload=i )
  stream_to_dest0.append( msg )

stream_to_dest1 = []
for i in range(16):
  msg = NetMsgType( src=0, dest=1, opaque=i, payload=i )
  stream_to_dest1.append( msg )

stream_to_dest2 = []
for i in range(16):
  msg = NetMsgType( src=0, dest=2, opaque=i, payload=i )
  stream_to_dest2.append( msg )

stream_to_all = []
for i in range(16):
  m0 = NetMsgType( src=0, dest=0, opaque=0x00+i, payload=0x0000+i )
  m1 = NetMsgType( src=0, dest=1, opaque=0x40+i, payload=0x1000+i )
  m2 = NetMsgType( src=0, dest=2, opaque=0x80+i, payload=0x2000+i )
  stream_to_all.extend([m0, m1, m2])

#-------------------------------------------------------------------------
# Random Test Cases
#-------------------------------------------------------------------------
random_test = []
for i in range(16):
  random_src = random.randint(0,3)
  random_dest = random.randint(0,3)
  m0 = NetMsgType( src=random_src, dest=random_dest, opaque=0x00+i, payload=0x0000+i )
  random_src = random.randint(0,3)
  random_dest = random.randint(0,3)
  m1 = NetMsgType( src=random_src, dest=random_dest, opaque=0x40+i, payload=0x1000+i )
  random_src = random.randint(0,3)
  random_dest = random.randint(0,3)
  m2 = NetMsgType( src=random_src, dest=random_dest, opaque=0x80+i, payload=0x2000+i )
  random_test.extend([m0, m1, m2])


#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                                  "msgs    src_delay sink_delay delay_mode"),
  [ "one",                            one,                 0,  0,  'fixed'  ],
  [ "rotate0",                        rotate0,             0,  0,  'fixed'  ],
  [ "rotate1",                        rotate1,             0,  0,  'fixed'  ],
  [ "rotate2",                        rotate2,             0,  0,  'fixed'  ],
  [ "rotate3",                        rotate3,             0,  0,  'fixed'  ],
  [ "all_to_dest0",                   all_to_dest0,        0,  0,  'fixed'  ],
  [ "all_to_dest1",                   all_to_dest1,        0,  0,  'fixed'  ],
  [ "all_to_dest2",                   all_to_dest2,        0,  0,  'fixed'  ],
  [ "all_to_dest3",                   all_to_dest3,        0,  0,  'fixed'  ],
  [ "stream_to_dest0",                stream_to_dest0,     0,  0,  'fixed'  ],
  [ "stream_to_dest0_src_delay",      stream_to_dest0,     5,  0,  'fixed'  ],
  [ "stream_to_dest1",                stream_to_dest1,     0,  0,  'fixed'  ],
  [ "stream_to_dest1_sink_delay",     stream_to_dest1,     0,  3,  'fixed'  ],
  [ "stream_to_dest2",                stream_to_dest2,     0,  0,  'fixed'  ],
  [ "stream_to_dest2_delays",         stream_to_dest2,     9,  1,  'fixed'  ],
  [ "stream_to_all",                  stream_to_all,       0,  0,  'fixed'  ],
  [ "stream_to_all_delays",           stream_to_all,       2,  7,  'fixed'  ],
  [ "random",                         random_test,         0,  0,  'fixed'  ],

  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

])

#-------------------------------------------------------------------------
# test
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, cmdline_opts ):

  th = TestHarness()

  th.set_param("top.srcs[0].construct",
    msgs                = [ m for m in test_params.msgs if m.src == 0 ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.src_delay,
    interval_delay      = test_params.src_delay )

  th.set_param("top.srcs[1].construct",
    msgs                = [ m for m in test_params.msgs if m.src == 1 ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.src_delay,
    interval_delay      = test_params.src_delay )

  th.set_param("top.srcs[2].construct",
    msgs                = [ m for m in test_params.msgs if m.src == 2 ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.src_delay,
    interval_delay      = test_params.src_delay )

  th.set_param("top.srcs[3].construct",
    msgs                = [ m for m in test_params.msgs if m.src == 3 ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.src_delay,
    interval_delay      = test_params.src_delay )

  th.set_param("top.sinks[0].construct",
    msgs                = [ m for m in test_params.msgs if m.dest == 0 ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.set_param("top.sinks[1].construct",
    msgs                = [ m for m in test_params.msgs if m.dest == 1 ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.set_param("top.sinks[2].construct",
    msgs                = [ m for m in test_params.msgs if m.dest == 2 ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.set_param("top.sinks[3].construct",
    msgs                = [ m for m in test_params.msgs if m.dest == 3 ],
    interval_delay_mode = test_params.delay_mode,
    initial_delay       = test_params.sink_delay,
    interval_delay      = test_params.sink_delay )

  th.elaborate()

  run_sim( th, cmdline_opts, duts=['net'] )
