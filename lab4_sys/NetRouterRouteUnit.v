//========================================================================
// Network Router Route Unit
//========================================================================

`ifndef LAB4_SYS_NET_ROUTER_ROUTE_UNIT_V
`define LAB4_SYS_NET_ROUTER_ROUTE_UNIT_V

`include "vc/net-msgs.v"
`include "vc/trace.v"

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

module lab4_sys_NetRouterRouteUnit
#(
  parameter p_msg_nbits = 44
)
(
  input  logic                   clk,
  input  logic                   reset,

  // Router id (which router is this in the network?)

  input  logic [1:0]             router_id,

  // Input stream

  input  logic [p_msg_nbits-1:0] istream_msg,
  input  logic                   istream_val,
  output logic                   istream_rdy,

  // Output streams

  output logic [p_msg_nbits-1:0] ostream_msg [3],
  output logic                   ostream_val [3],
  input  logic                   ostream_rdy [3]
);

  net_msg_hdr_t istream_msg_hdr;
  assign istream_msg_hdr = istream_msg[`VC_NET_MSGS_HDR(p_msg_nbits)];

  //''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // Implement route unit logic
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  assign ostream_msg[0] = istream_msg;
  assign ostream_msg[1] = istream_msg;
  assign ostream_msg[2] = istream_msg;

  always_comb begin

    istream_rdy  = 0;
    ostream_val[0] = 0;
    ostream_val[1] = 0;
    ostream_val[2] = 0;

    if (istream_val) begin
      if (router_id == istream_msg_hdr.dest) begin
        istream_rdy = ostream_rdy[0];
        ostream_val[0] = 1;
      end
      else begin
        istream_rdy = ostream_rdy[1];
        ostream_val[1] = 1;
      end
    end
  end


  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin

    if ( istream_val && istream_rdy ) begin
      $sformat( str, "%d", istream_msg_hdr.dest );
      vc_trace.append_str( trace_str, str );
    end
    else
      vc_trace.append_str( trace_str, " " );

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* NET_ROUTER_ROUTE_UNIT_V */
