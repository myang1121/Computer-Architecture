//========================================================================
// Integer Multiplier Fixed-Latency Implementation
//========================================================================

`ifndef LAB1_IMUL_INT_MUL_BASE_V
`define LAB1_IMUL_INT_MUL_BASE_V

`include "vc/muxes.v"
`include "vc/regs.v"
`include "vc/arithmetic.v"
`include "vc/trace.v"

// ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// Define datapath and control unit here.
// '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

//=======================================================================
// Integer Multiplier Datapath
// ======================================================================
module lab1_imul_IntMulDpath
(
  input  logic        clk, 
  input  logic        reset,

  // Data signals
  input  logic [63:0] istream_msg,
  output logic [31:0] ostream_msg,

  // Control signals
  input  logic        a_mux_sel,       // Sel for mux in front of A reg  
  input  logic        b_mux_sel,       // Sel for mux in front of B reg
  input  logic        result_mux_sel,  // Sel for mux for result reg
  input  logic        add_mux_sel,     // Sel for adder mux
  input  logic        result_en,       // Enable for result register

  // Status signal
  output logic        b_lsb            //Least significant bit of B  
);
 
  // Split out the a and b operands
  logic [31:0]         istream_msg_a;
  assign istream_msg_a = istream_msg[63:32];

  logic [31:0]         istream_msg_b;
  assign istream_msg_b = istream_msg[31:0];

  // A Mux
  logic [31:0] a_mux_out;
  logic [31:0] left_shift_out;

  vc_Mux2#(32) a_mux
  (
  .sel   (a_mux_sel),
  .in0   (left_shift_out),
  .in1   (istream_msg_a),
  .out   (a_mux_out)
  );

  // A register
  logic [31:0] a_reg_out;

  vc_EnReg#(32) a_reg
  (
    .clk   (clk),
    .reset (reset),
    .en    (1'b1),
    .d     (a_mux_out),
    .q     (a_reg_out)
  );

  // B Mux
  logic [31:0] b_mux_out;
  logic [31:0] right_shift_out;

  vc_Mux2#(32) b_mux
  (
    .sel    (b_mux_sel),
    .in0    (right_shift_out),
    .in1    (istream_msg_b),
    .out    (b_mux_out)
  );

  // B register
  logic [31:0] b_reg_out;

  vc_EnReg#(32) b_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (1'b1),
    .d      (b_mux_out),
    .q      (b_reg_out)
  );

  // Result Mux
  logic [31:0] result_mux_out;
  logic [31:0] adder_mux_out;

  vc_Mux2#(32) result_mux
  (
    .sel    (result_mux_sel),
    .in0    (adder_mux_out),
    .in1    (1'b0),
    .out    (result_mux_out)
  );

  // Result register
  logic [31:0] result_reg_out;

  vc_EnReg#(32) result_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (result_en),
    .d      (result_mux_out),
    .q      (result_reg_out)
  );

  // Left logical shifter
  vc_LeftLogicalShifter#(32,1) left_shifter
  (
    .in    (a_reg_out),
    .shamt (1'b1),
    .out   (left_shift_out)
  );

  // Right logical shifter
  vc_RightLogicalShifter#(32,1) right_shifter
  (
    .in    (b_reg_out),
    .shamt (1'b1),
    .out   (right_shift_out)
  );

  // Adder
  logic [31:0] adder_out;

  vc_SimpleAdder#(32) adder
  (
    .in0    (a_reg_out),
    .in1    (result_reg_out),
    .out    (adder_out)
  );

  // Adder Mux
  vc_Mux2#(32) adder_mux
  (
    .sel    (add_mux_sel),
    .in0    (adder_out),
    .in1    (result_reg_out),
    .out    (adder_mux_out)
  );
 
  // Connect to output ports
  assign ostream_msg = result_reg_out;
  assign b_lsb = b_reg_out[0];

endmodule

//======================================================================
// Integer Multiplier Control
// =====================================================================

module lab1_imul_IntMulUnitCtrl
(
  input  logic        clk,
  input  logic        reset,

  // Dataflow signals
  input  logic        istream_val,
  output logic        istream_rdy,
  output logic        ostream_val,
  input  logic        ostream_rdy,

  // Control signals
  output logic        a_mux_sel,
  output logic        b_mux_sel,
  output logic        result_mux_sel,
  output logic        add_mux_sel,
  output logic        result_en,  

  // Data signal
  input  logic        b_lsb
);  
  //---------------------------------------------------------------------
  // State Definitions
  //---------------------------------------------------------------------
 
  localparam STATE_IDLE = 2'd0;
  localparam STATE_CALC = 2'd1;
  localparam STATE_DONE = 2'd2;

  //---------------------------------------------------------------------
  // State
  // --------------------------------------------------------------------
  logic [1:0] state_reg;
  logic [1:0] state_next;
  logic [5:0] counter;

  always_ff @( posedge clk ) begin
    if ( reset ) begin
      state_reg <= STATE_IDLE;
      counter   <= 6'b0;
    end
    else begin
      state_reg <= state_next;
      if (counter < 6'b100000) begin
        counter <= counter + 6'b1;
      end
      if (state_reg == STATE_IDLE) begin
        counter <= 6'b0;
      end
    end
  end

  //---------------------------------------------------------------------
  // State Transitions
  //---------------------------------------------------------------------
  logic req_done;
  logic resp_done;
  logic is_calc_done;

  assign req_done        = istream_val && istream_rdy;
  assign resp_done       = ostream_val && ostream_rdy;
  assign is_calc_done    = (counter == 6'b100000);
 
  always_comb begin
    state_next = state_reg;

    case( state_reg)
      STATE_IDLE: if (req_done)     state_next = STATE_CALC;
      STATE_CALC: if (is_calc_done) state_next = STATE_DONE;
      STATE_DONE: if (resp_done)    state_next = STATE_IDLE;
      default:    state_next = 'x;
    endcase
  end
 
  //---------------------------------------------------------------------
  // State Outputs
  //---------------------------------------------------------------------
 localparam a_x = 1'dx;
 localparam b_x = 1'dx;
 localparam r_x = 1'dx;
 localparam add_x = 1'dx;

  function void cs
  (
    input logic    cs_istream_rdy,
    input logic    cs_ostream_val,
    input logic    cs_a_mux_sel,
    input logic    cs_b_mux_sel,
    input logic    cs_result_mux_sel,
    input logic    cs_add_mux_sel,
    input logic    cs_result_en
  );
  begin
    istream_rdy    = cs_istream_rdy;
    ostream_val    = cs_ostream_val;
    a_mux_sel      = cs_a_mux_sel;
    b_mux_sel      = cs_b_mux_sel;
    result_mux_sel = cs_result_mux_sel;
    add_mux_sel    = cs_add_mux_sel;
    result_en      = cs_result_en;
  end
  endfunction

  // Labels for Mealy transitions
  logic do_add_shift;
  logic do_shift;

  assign do_add_shift = (counter < 6'b100000) && (b_lsb == 1'b1);
  assign do_shift     = (counter < 6'b100000) && (b_lsb == 1'b0);

  // Set outputs using a control signal table
  always_comb begin 
    cs (0, 0, a_x, b_x, r_x, add_x, 0);

    case (state_reg)
      // Key for Control Signal Table:
      // i_rdy = istream_rdy, o_val = ostream_val, a_sl = a_mux_sel, b_sl = b_mux_sel,
      // r_sl = result_mux_sel, add_sl = add_mux_sel, r_en = result_en
      //
      //                                i_rdy  o_val a_sl  b_sl r_sl  add_sl r_en
      STATE_IDLE:                    cs(  1,   0,    1,    1,   1,    1,     1 );
      STATE_CALC: if (do_add_shift)  cs(  0,   0,    0,    0,   0,    0,     1 );
             else if (do_shift)      cs(  0,   0,    0,    0,   1,    1,     0 );
      STATE_DONE:                    cs(  0,   1,    a_x,  b_x, r_x,  add_x, 0 );
      default                        cs(  'x,  'x,   a_x,  b_x, r_x,  add_x, 'x);
    endcase
  end
endmodule

//========================================================================
// Integer Multiplier Fixed-Latency Implementation
//========================================================================

module lab1_imul_IntMulBase
(
  input  logic        clk,
  input  logic        reset,

  input  logic        istream_val,
  output logic        istream_rdy,
  input  logic [63:0] istream_msg,

  output logic        ostream_val,
  input  logic        ostream_rdy,
  output logic [31:0] ostream_msg
);

  // ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // Instantiate datapath and control models here and then connect them
  // together.
  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  
  //----------------------------------------------------------------------
  // Connect Control Unit and Datapath
  // ---------------------------------------------------------------------

  //Control Signals
  logic        b_mux_sel;
  logic        a_mux_sel;
  logic        result_mux_sel;
  logic        result_en;
  logic        add_mux_sel;
  
  //Data signals
  logic        b_lsb;
  
  //Control unit
  lab1_imul_IntMulUnitCtrl ctrl
  (
    .*
  );

  //Datapath
  lab1_imul_IntMulDpath dpath
  (
   .*
  );

  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin

    $sformat( str, "%x", istream_msg );
    vc_trace.append_val_rdy_str( trace_str, istream_val, istream_rdy, str );

    vc_trace.append_str( trace_str, "(" );

    // ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''
    // Add additional line tracing using the helper tasks for
    // internal state including the current FSM state.
    // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
    $sformat( str, "%x", dpath.a_reg_out);
    vc_trace.append_str(trace_str, str);
    vc_trace.append_str(trace_str,  " ");

    $sformat( str, "%x", dpath.b_reg_out);
    vc_trace.append_str(trace_str, str);
    vc_trace.append_str(trace_str, " ");

    $sformat (str, "%x", dpath.result_reg_out);
    vc_trace.append_str(trace_str, str);
    vc_trace.append_str(trace_str, " ");

    $sformat (str, "%x", dpath.adder_out);
    vc_trace.append_str(trace_str, str);
    vc_trace.append_str(trace_str, " ");
    
    $sformat (str, "%x", dpath.b_lsb);
    vc_trace.append_str(trace_str, str);
    vc_trace.append_str(trace_str, " "); 

    $sformat (str, "%x", ctrl.counter);
    vc_trace.append_str(trace_str, str);
    vc_trace.append_str(trace_str, " ");

    case (ctrl.state_reg)
      ctrl.STATE_IDLE:
        vc_trace.append_str( trace_str, "I " );
      ctrl.STATE_CALC:
      begin 
        if (ctrl.do_add_shift)
	  vc_trace.append_str(trace_str, "Cas");
        else if (ctrl.do_shift)
	  vc_trace.append_str(trace_str, "Cs");
        else
          vc_trace.append_str(trace_str, "C ");
      end
      
      ctrl.STATE_DONE:
        vc_trace.append_str(trace_str, "D ");
      
      default:
        vc_trace.append_str(trace_str, "? ");

    endcase

    vc_trace.append_str( trace_str, ")" );

    $sformat( str, "%x", ostream_msg );
    vc_trace.append_val_rdy_str( trace_str, ostream_val, ostream_rdy, str );

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* LAB1_IMUL_INT_MUL_BASE_V */
