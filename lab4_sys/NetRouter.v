//========================================================================
// Network Router
//========================================================================

`ifndef LAB4_SYS_NET_ROUTER_V
`define LAB4_SYS_NET_ROUTER_V

`include "vc/net-msgs.v"
`include "vc/trace.v"
`include "vc/queues.v"

`include "lab4_sys/NetRouterRouteUnit.v"
`include "lab4_sys/NetRouterSwitchUnit.v"

module lab4_sys_NetRouter
#(
  parameter p_msg_nbits = 44
)
(
  input  logic                   clk,
  input  logic                   reset,

  // Router id (which router is this in the network?)

  input  logic     [1:0]         router_id,

  // Input streams

  input  logic [p_msg_nbits-1:0] istream_msg [3],
  input  logic                   istream_val [3],
  output logic                   istream_rdy [3],

  // Output streams

  output logic [p_msg_nbits-1:0] ostream_msg [3],
  output logic                   ostream_val [3],
  input  logic                   ostream_rdy [3]
);

  //''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // Implement router with input queues, route units, and switch units
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  //----------------------------------------------------------------------
  // Input Queues
  //----------------------------------------------------------------------

  // Input queue 0

  logic [2:0] inq0_num_free_entries;

  logic [p_msg_nbits-1:0] inq0_deq_msg;
  logic                   inq0_deq_val;
  logic                   inq0_deq_rdy;

  vc_Queue#(`VC_QUEUE_NORMAL,p_msg_nbits,4) inq0
  (
    .clk     (clk),
    .reset   (reset),
    .num_free_entries(inq0_num_free_entries),

    .enq_msg (istream_msg[0]),
    .enq_val (istream_val[0]),
    .enq_rdy (istream_rdy[0]),

    .deq_msg (inq0_deq_msg),
    .deq_val (inq0_deq_val),
    .deq_rdy (inq0_deq_rdy)
  );

  // Input queue 1

  logic [2:0] inq1_num_free_entries;

  logic [p_msg_nbits-1:0] inq1_deq_msg;
  logic                   inq1_deq_val;
  logic                   inq1_deq_rdy;

  vc_Queue#(`VC_QUEUE_NORMAL,p_msg_nbits,4) inq1
  (
    .clk     (clk),
    .reset   (reset),
    .num_free_entries(inq1_num_free_entries),

    .enq_msg (istream_msg[1]),
    .enq_val (istream_val[1]),
    .enq_rdy (istream_rdy[1]),

    .deq_msg (inq1_deq_msg),
    .deq_val (inq1_deq_val),
    .deq_rdy (inq1_deq_rdy)
  );

  // Input queue 2

  logic [2:0] inq2_num_free_entries;

  logic [p_msg_nbits-1:0] inq2_deq_msg;
  logic                   inq2_deq_val;
  logic                   inq2_deq_rdy;

  vc_Queue#(`VC_QUEUE_NORMAL,p_msg_nbits,4) inq2
  (
    .clk     (clk),
    .reset   (reset),
    .num_free_entries(inq2_num_free_entries),

    .enq_msg (istream_msg[2]),
    .enq_val (istream_val[2]),
    .enq_rdy (istream_rdy[2]),

    .deq_msg (inq2_deq_msg),
    .deq_val (inq2_deq_val),
    .deq_rdy (inq2_deq_rdy)
  );

  //----------------------------------------------------------------------
  // Route Units
  //----------------------------------------------------------------------

  // Route unit 0

  logic [p_msg_nbits-1:0] runit0_ostream_msg [3];
  logic                   runit0_ostream_val [3];
  logic                   runit0_ostream_rdy [3];

  lab4_sys_NetRouterRouteUnit#(p_msg_nbits) runit0
  (
    .clk          (clk),
    .reset        (reset),
    .router_id    (router_id),

    .istream_msg  (inq0_deq_msg),
    .istream_val  (inq0_deq_val),
    .istream_rdy  (inq0_deq_rdy),

    .ostream_msg  (runit0_ostream_msg),
    .ostream_val  (runit0_ostream_val),
    .ostream_rdy  (runit0_ostream_rdy)
  );

  // Route unit 1

  logic [p_msg_nbits-1:0] runit1_ostream_msg [3];
  logic                   runit1_ostream_val [3];
  logic                   runit1_ostream_rdy [3];

  lab4_sys_NetRouterRouteUnit#(p_msg_nbits) runit1
  (
    .clk          (clk),
    .reset        (reset),
    .router_id    (router_id),

    .istream_msg  (inq1_deq_msg),
    .istream_val  (inq1_deq_val),
    .istream_rdy  (inq1_deq_rdy),

    .ostream_msg  (runit1_ostream_msg),
    .ostream_val  (runit1_ostream_val),
    .ostream_rdy  (runit1_ostream_rdy)
  );

  // Route unit 2

  logic [p_msg_nbits-1:0] runit2_ostream_msg [3];
  logic                   runit2_ostream_val [3];
  logic                   runit2_ostream_rdy [3];

  lab4_sys_NetRouterRouteUnit#(p_msg_nbits) runit2
  (
    .clk          (clk),
    .reset        (reset),
    .router_id    (router_id),

    .istream_msg  (inq2_deq_msg),
    .istream_val  (inq2_deq_val),
    .istream_rdy  (inq2_deq_rdy),

    .ostream_msg  (runit2_ostream_msg),
    .ostream_val  (runit2_ostream_val),
    .ostream_rdy  (runit2_ostream_rdy)
  );

  //----------------------------------------------------------------------
  // Switch units
  //----------------------------------------------------------------------

  // Switch unit 0

  lab4_sys_NetRouterSwitchUnit#(p_msg_nbits) sunit0
  (
    .clk          (clk),
    .reset        (reset),

    .istream_msg  ('{ runit0_ostream_msg[0], runit1_ostream_msg[0], runit2_ostream_msg[0] }),
    .istream_val  ('{ runit0_ostream_val[0], runit1_ostream_val[0], runit2_ostream_val[0] }),
    .istream_rdy  ('{ runit0_ostream_rdy[0], runit1_ostream_rdy[0], runit2_ostream_rdy[0] }),

    .ostream_msg  (ostream_msg[0]),
    .ostream_val  (ostream_val[0]),
    .ostream_rdy  (ostream_rdy[0])
  );

  // Switch unit 1

  lab4_sys_NetRouterSwitchUnit#(p_msg_nbits) sunit1
  (
    .clk          (clk),
    .reset        (reset),

    .istream_msg  ('{ runit0_ostream_msg[1], runit1_ostream_msg[1], runit2_ostream_msg[1] }),
    .istream_val  ('{ runit0_ostream_val[1], runit1_ostream_val[1], runit2_ostream_val[1] }),
    .istream_rdy  ('{ runit0_ostream_rdy[1], runit1_ostream_rdy[1], runit2_ostream_rdy[1] }),

    .ostream_msg  (ostream_msg[1]),
    .ostream_val  (ostream_val[1]),
    .ostream_rdy  (ostream_rdy[1])
  );

  // Switch unit 2

  lab4_sys_NetRouterSwitchUnit#(p_msg_nbits) sunit2
  (
    .clk          (clk),
    .reset        (reset),

    .istream_msg  ('{ runit0_ostream_msg[2], runit1_ostream_msg[2], runit2_ostream_msg[2] }),
    .istream_val  ('{ runit0_ostream_val[2], runit1_ostream_val[2], runit2_ostream_val[2] }),
    .istream_rdy  ('{ runit0_ostream_rdy[2], runit1_ostream_rdy[2], runit2_ostream_rdy[2] }),

    .ostream_msg  (ostream_msg[2]),
    .ostream_val  (ostream_val[2]),
    .ostream_rdy  (ostream_rdy[2])
  );

  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  vc_NetMsgTrace#(p_msg_nbits) ostream0_trace
  (
    .clk   (clk),
    .reset (reset),
    .msg   (ostream_msg[0]),
    .val   (ostream_val[0]),
    .rdy   (ostream_rdy[0])
  );

  vc_NetMsgTrace#(p_msg_nbits) ostream1_trace
  (
    .clk   (clk),
    .reset (reset),
    .msg   (ostream_msg[1]),
    .val   (ostream_val[1]),
    .rdy   (ostream_rdy[1])
  );

  vc_NetMsgTrace#(p_msg_nbits) ostream2_trace
  (
    .clk   (clk),
    .reset (reset),
    .msg   (ostream_msg[2]),
    .val   (ostream_val[2]),
    .rdy   (ostream_rdy[2])
  );

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin

    // Line tracing for input queues

    case ( inq0_num_free_entries )
      4: vc_trace.append_str( trace_str, " " );
      3: vc_trace.append_str( trace_str, "." );
      2: vc_trace.append_str( trace_str, ":" );
      1: vc_trace.append_str( trace_str, "*" );
      0: vc_trace.append_str( trace_str, "#" );
    endcase

    case ( inq1_num_free_entries )
      4: vc_trace.append_str( trace_str, " " );
      3: vc_trace.append_str( trace_str, "." );
      2: vc_trace.append_str( trace_str, ":" );
      1: vc_trace.append_str( trace_str, "*" );
      0: vc_trace.append_str( trace_str, "#" );
    endcase

    case ( inq2_num_free_entries )
      4: vc_trace.append_str( trace_str, " " );
      3: vc_trace.append_str( trace_str, "." );
      2: vc_trace.append_str( trace_str, ":" );
      1: vc_trace.append_str( trace_str, "*" );
      0: vc_trace.append_str( trace_str, "#" );
    endcase

    vc_trace.append_str( trace_str, "|" );

    // Line tracing for switch units

    sunit0.line_trace( trace_str );
    sunit1.line_trace( trace_str );
    sunit2.line_trace( trace_str );

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* NET_ROUTER_V */
