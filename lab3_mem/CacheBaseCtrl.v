//=========================================================================
// Base Blocking Cache Control
//=========================================================================

`ifndef LAB3_MEM_CACHE_BASE_CTRL_V
`define LAB3_MEM_CACHE_BASE_CTRL_V

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Include necessary files
//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
`include "vc/regfiles.v"
`include "vc/mem-msgs.v"

module lab3_mem_CacheBaseCtrl
#(
  parameter p_num_banks = 1
)
(
  input  logic        clk,
  input  logic        reset,

  // Processor <-> Cache Interface

  input  logic        proc2cache_reqstream_val,
  output logic        proc2cache_reqstream_rdy,

  output logic        proc2cache_respstream_val,
  input  logic        proc2cache_respstream_rdy,

  // Cache <-> Memory Interface

  output logic        cache2mem_reqstream_val,
  input  logic        cache2mem_reqstream_rdy,

  input  logic        cache2mem_respstream_val,
  output logic        cache2mem_respstream_rdy,

  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Define additional ports
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  
  // control signals (ctrl->dpath)

  output logic        cachereq_reg_en,
  output logic        tag_array_wen,
  output logic        tag_array_ren,
  output logic        data_array_wen,
  output logic        data_array_ren,
  output logic        read_data_zero_mux_sel,
  output logic        read_data_reg_en,
  output logic [1:0]  hit,
  output logic        evict_addr_reg_en,//new
  output logic        memreq_addr_mux_sel,//new
  output logic [2:0]  memreq_type,//new
  output logic        memresp_en,//new
  output logic        write_data_mux_sel,//new
  output logic        wben_mux_sel,//new

  // status signals (dpath->ctrl)

  input  logic  [2:0] cachereq_type,
  input  logic [31:0] cachereq_addr,
  input  logic        tag_match
);

  //----------------------------------------------------------------------
  // State Definitions
  //----------------------------------------------------------------------

  localparam STATE_IDLE              = 5'd0;
  localparam STATE_TAG_CHECK         = 5'd1;
  localparam STATE_INIT_DATA_ACCESS  = 5'd2;
  localparam STATE_READ_DATA_ACCESS  = 5'd3;
  localparam STATE_WRITE_DATA_ACCESS = 5'd4;
  localparam STATE_REFILL_REQUEST    = 5'd5;
  localparam STATE_REFILL_WAIT       = 5'd6;
  localparam STATE_REFILL_UPDATE     = 5'd7;
  localparam STATE_EVICT_PREPARE     = 5'd8;
  localparam STATE_EVICT_REQUEST     = 5'd9;
  localparam STATE_EVICT_WAIT        = 5'd10;
  localparam STATE_WAIT              = 5'd11;

  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Impement control unit
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  //----------------------------------------------------------------------
  // State
  //----------------------------------------------------------------------  
  always @( posedge clk ) begin
    if ( reset ) begin
      state_reg <= STATE_IDLE;
    end
    else begin
      state_reg <= state_next;
    end
  end

  //---------------------------------------------------------------------
  // State Transitions
  //---------------------------------------------------------------------
  
  logic is_read;
  logic is_write;
  logic is_init;

  assign is_read  = cachereq_type == `VC_MEM_REQ_MSG_TYPE_READ;
  assign is_write = cachereq_type == `VC_MEM_REQ_MSG_TYPE_WRITE;
  assign is_init  = cachereq_type == `VC_MEM_REQ_MSG_TYPE_WRITE_INIT;
  assign memreq_type = (state_reg == STATE_EVICT_REQUEST)? `VC_MEM_REQ_MSG_TYPE_WRITE : `VC_MEM_REQ_MSG_TYPE_READ;
  assign tag_match_en = (state_reg == STATE_TAG_CHECK)? 1'b1 : 1'b0;

  logic [4:0] state_reg;
  logic [4:0] state_next;

  always @(*) begin

    state_next = state_reg;
    case ( state_reg )

      STATE_IDLE:
        if ( proc2cache_reqstream_val )
          state_next = STATE_TAG_CHECK;

      STATE_TAG_CHECK:
        if (is_init)
          state_next = STATE_INIT_DATA_ACCESS;
        else if (is_read && tag_match_valid)
	  state_next = STATE_READ_DATA_ACCESS;
        else if (is_write && tag_match_valid)
	  state_next = STATE_WRITE_DATA_ACCESS;
  	else if (!tag_match_valid && !is_dirty)
	  state_next = STATE_REFILL_REQUEST;
  	else if (!tag_match_valid && is_dirty)
	  state_next = STATE_EVICT_PREPARE;

      STATE_INIT_DATA_ACCESS:
        state_next = STATE_WAIT;
      
      STATE_READ_DATA_ACCESS:
        state_next = STATE_WAIT;
      
      STATE_WRITE_DATA_ACCESS:
	state_next = STATE_WAIT;
      
      STATE_REFILL_REQUEST:
        if (cache2mem_reqstream_rdy)
	  state_next = STATE_REFILL_WAIT;
      
      STATE_REFILL_WAIT:
        if (cache2mem_respstream_val)
	  state_next = STATE_REFILL_UPDATE;
      
      STATE_REFILL_UPDATE:
        if (is_read)
	  state_next = STATE_READ_DATA_ACCESS;
        else if (is_write)
          state_next = STATE_WRITE_DATA_ACCESS;

      STATE_EVICT_PREPARE:
        state_next = STATE_EVICT_REQUEST;

      STATE_EVICT_REQUEST:
        if (cache2mem_reqstream_rdy)
	  state_next = STATE_EVICT_WAIT;
      
      STATE_EVICT_WAIT:
        if (cache2mem_respstream_val)
	  state_next = STATE_REFILL_REQUEST;

      STATE_WAIT:
        if (proc2cache_respstream_rdy)
	  state_next = STATE_IDLE;

      default:
        state_next = STATE_IDLE;

    endcase

  end

  //---------------------------------------------------------------------
  // Valid/Dirty bits record
  //---------------------------------------------------------------------

  logic [3:0] cachereq_addr_index;

  generate
    if ( p_num_banks == 1 ) begin
      assign cachereq_addr_index = cachereq_addr[7:4];
    end
    else if ( p_num_banks == 4 ) begin
      // handle address mapping for four banks
      assign cachereq_addr_index = cachereq_addr[9:6];

    end
  endgenerate

  logic valid_bit_in;
  logic valid_bits_write_en;
  logic is_valid;

  vc_ResetRegfile_1r1w#(1,16) valid_bits
  (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (cachereq_addr_index),
    .read_data  (is_valid),
    .write_en   (valid_bits_write_en),
    .write_addr (cachereq_addr_index),
    .write_data (valid_bit_in)
  );

  logic dirty_bit_in;
  logic dirty_bits_write_en;
  logic is_dirty;

  vc_ResetRegfile_1r1w#(1,16) dirty_bits
  (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (cachereq_addr_index),
    .read_data  (is_dirty),
    .write_en   (dirty_bits_write_en),
    .write_addr (cachereq_addr_index),
    .write_data (dirty_bit_in)
  );
  
  logic tag_match_reg_out;
  logic tag_match_en;

  vc_EnResetReg #(1,0) tag_match_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (tag_match_en),
    .d      (tag_match_valid),
    .q      (tag_match_reg_out)
  );

  logic [1:0] hit_TC;
  logic tag_match_valid;

  assign tag_match_valid = tag_match && is_valid;
  assign hit = (tag_match_reg_out && !is_init && is_valid)? 2'b1 : 2'b0;
  assign hit_TC = hit;

  //---------------------------------------------------------------------
  // State Outputs
  //---------------------------------------------------------------------

  //2 Input Mux Don't Care
  localparam d_x   = 1'bx;

  // Read Data Mux Sel
  localparam d_arr = 1'b0;
  localparam zero  = 1'b1;

  // Memory Request Addr Mux Sel
  localparam evict = 1'b0;
  localparam req   = 1'b1;
  
  // Write Data Mux Sel
  localparam repl = 1'b0;
  localparam data = 1'b1;

  // Wben Mux Sel
  localparam dec = 1'b0;
  localparam ffff = 1'b1;

  task cs
  (
    input logic cs_cachereq_rdy,
    input logic cs_cacheresp_val,
    input logic cs_cachereq_reg_en,
    input logic cs_tag_array_wen,
    input logic cs_tag_array_ren,
    input logic cs_data_array_wen,
    input logic cs_data_array_ren,
    input logic cs_valid_bit_in,
    input logic cs_valid_bits_write_en,
    input logic cs_dirty_bit_in,
    input logic cs_dirty_bits_write_en,
    input logic cs_read_data_zero_mux_sel,
    input logic cs_read_data_reg_en,
    input logic cs_evict_addr_reg_en,
    input logic cs_memreq_addr_mux_sel,
    input logic cs_write_data_mux_sel,
    input logic cs_wben_mux_sel,
    input logic cs_memresp_en,
    input logic cs_memreq_val,
    input logic cs_memresp_rdy,
  );
  begin
    proc2cache_reqstream_rdy  = cs_cachereq_rdy;
    proc2cache_respstream_val = cs_cacheresp_val;
    cachereq_reg_en           = cs_cachereq_reg_en;
    tag_array_wen             = cs_tag_array_wen;
    tag_array_ren             = cs_tag_array_ren;
    data_array_wen            = cs_data_array_wen;
    data_array_ren            = cs_data_array_ren;
    valid_bit_in              = cs_valid_bit_in;
    valid_bits_write_en       = cs_valid_bits_write_en;
    dirty_bit_in              = cs_dirty_bit_in;
    dirty_bits_write_en       = cs_dirty_bits_write_en;
    read_data_zero_mux_sel    = cs_read_data_zero_mux_sel;
    read_data_reg_en          = cs_read_data_reg_en;
    evict_addr_reg_en         = cs_evict_addr_reg_en;
    memreq_addr_mux_sel       = cs_memreq_addr_mux_sel;
    write_data_mux_sel        = cs_write_data_mux_sel;
    wben_mux_sel              = cs_wben_mux_sel;
    memresp_en                = cs_memresp_en;
    cache2mem_reqstream_val   = cs_memreq_val;
    cache2mem_respstream_rdy  = cs_memresp_rdy;

  end
  endtask

   // Set outputs using a control signal "table"
  always @(*) begin
                               cs( 0,   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    d_x,   0,    0, d_x,  d_x,   d_x,  0,   0,  1);
    case ( state_reg )
      //                          cache cache cache tag   tag   data  data  valid valid dirty dirty read  read evict mem   write wben  mem  mem mem
      //                          req   resp  req   array array array array bit   write bit   write data  data addr addr   data  mux  resp  req resp
      //                          rdy   val   en    wen   ren   wen   ren   in    en    in    en    sel   en   en   sel    sel   sel   en   val rdy
      STATE_IDLE:              cs( 1,   0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    d_x,   0,    0, d_x,   d_x,  d_x,  0,   0,  1);
      STATE_TAG_CHECK:         cs( 0,   0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    d_x,   0,    0, d_x,   d_x,  d_x,  0,   0,  1);
      STATE_INIT_DATA_ACCESS:  cs( 0,   0,    0,    1,    0,    1,    0,    1,    1,    0,    1,    zero,  1,    0, d_x,   repl, dec,  0,   0,  1);
      STATE_READ_DATA_ACCESS:  cs( 0,   0,    0,    0,    1,    0,    1,    0,    0,    0,    0,    d_arr, 1,    0, d_x,   d_x,  d_x,  0,   0,  1);
      STATE_WRITE_DATA_ACCESS: cs( 0,   0,    0,    1,    0,    1,    0,    0,    0,    1,    1,    zero,  1,    0, d_x,   repl, dec,  0,   0,  1);
      STATE_REFILL_REQUEST:    cs( 0,   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    d_x,   0,    0, req,   d_x,  d_x,  0,   1,  1);
      STATE_REFILL_WAIT:       cs( 0,   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    d_x,   0,    0, d_x,   d_x,  d_x,  1,   0,  1);
      STATE_REFILL_UPDATE:     cs( 0,   0,    0,    1,    0,    1,    0,    1,    1,    0,    1,    d_x,   0,    0, d_x,   data, ffff, 1,   0,  0);
      STATE_EVICT_PREPARE:     cs( 0,   0,    0,    0,    1,    0,    1,    0,    0,    0,    0,    d_x,   1,    1, d_x,   d_x,  d_x,  0,   0,  1); 
      STATE_EVICT_REQUEST:     cs( 0,   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    d_arr, 0,    0, evict, d_x,  d_x,  0,   1,  1);
      STATE_EVICT_WAIT:        cs( 0,   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    d_x,   0,    0, d_x,   d_x,  d_x,  1,   1,  1);
      STATE_WAIT:              cs( 0,   1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    d_x,   0,    0, d_x,   d_x,  d_x,  0,   0,  1);
      default:                 cs( 0,   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    d_x,   0,    0, d_x,   d_x,  d_x,  0,   0,  1);

    endcase
  end

  // Hard code cache <-> memory interface val/rdy signals since we are
  // not using this interface yet

  //assign cache2mem_reqstream_val  = 1'b0;
  //assign cache2mem_respstream_rdy = 1'b1;

endmodule

`endif
