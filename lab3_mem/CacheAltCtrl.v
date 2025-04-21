//=========================================================================
// Alt Blocking Cache Control
//=========================================================================

`ifndef LAB3_MEM_CACHE_ALT_CTRL_V
`define LAB3_MEM_CACHE_ALT_CTRL_V

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Include necessary files
//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
`include "vc/regfiles.v"
`include "vc/mem-msgs.v"

module lab3_mem_CacheAltCtrl
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
  output logic        tag_array_1_wen,  
  output logic        tag_array_0_wen,
  output logic        tag_array_ren,
  output logic        data_array_1_wen,
  output logic        data_array_0_wen,
  output logic        data_array_1_ren,
  output logic        data_array_0_ren,
  output logic [1:0]  read_data_zero_mux_sel,
  output logic        read_data_reg_en,
  output logic [1:0]  hit,
  output logic        mk_addr_mux_sel,
  output logic        evict_addr_reg_en,
  output logic        memreq_addr_mux_sel,
  output logic [2:0]  memreq_type,
  output logic        memresp_en,
  output logic        write_data_mux_sel,
  output logic        wben_mux_sel,

  // status signals (dpath->ctrl)

  input  logic [2:0]  cachereq_type,
  input  logic [31:0] cachereq_addr,
  input  logic        tag_match_1,
  input  logic        tag_match_0 
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
        else if (is_read && (tag_match_1_valid || tag_match_0_valid))
          state_next = STATE_READ_DATA_ACCESS;
        else if (is_write && (tag_match_1_valid || tag_match_0_valid))
          state_next = STATE_WRITE_DATA_ACCESS;
        else if (!(tag_match_1_valid || tag_match_0_valid) && !(is_dirty_0 || is_dirty_1))
          state_next = STATE_REFILL_REQUEST;
        else if (!(tag_match_1_valid || tag_match_0_valid)  && (is_dirty_0 || is_dirty_1))
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
      assign cachereq_addr_index = cachereq_addr[6:4];
    end
    else if ( p_num_banks == 4 ) begin
      // handle address mapping for four banks
      assign cachereq_addr_index = cachereq_addr[8:6];

    end
  endgenerate

  logic valid_bit_in;

  // Valids Bits Way 1
  logic valid_bits_1_write_en;
  logic is_valid_1;

  vc_ResetRegfile_1r1w#(1,8) valid_bits_1
  (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (cachereq_addr_index),
    .read_data  (is_valid_1),
    .write_en   (valid_bits_1_write_en),
    .write_addr (cachereq_addr_index),
    .write_data (valid_bit_in)
  );

  // Valid Bits Way 0
  logic valid_bits_0_write_en;
  logic is_valid_0;

  vc_ResetRegfile_1r1w#(1,8) valid_bits_0
  (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (cachereq_addr_index),
    .read_data  (is_valid_0),
    .write_en   (valid_bits_0_write_en),
    .write_addr (cachereq_addr_index),
    .write_data (valid_bit_in)
  );

  logic dirty_bit_in;

  // Dirty Bits Way 1
  logic dirty_bits_1_write_en;
  logic is_dirty_1;

  vc_ResetRegfile_1r1w#(1,8) dirty_bits_1
  (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (cachereq_addr_index),
    .read_data  (is_dirty_1),
    .write_en   (dirty_bits_1_write_en),
    .write_addr (cachereq_addr_index),
    .write_data (dirty_bit_in)
  );

  // Dirty Bits Way 0
  logic dirty_bits_0_write_en;
  logic is_dirty_0;

  vc_ResetRegfile_1r1w#(1,8) dirty_bits_0
  (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (cachereq_addr_index),
    .read_data  (is_dirty_0),
    .write_en   (dirty_bits_0_write_en),
    .write_addr (cachereq_addr_index),
    .write_data (dirty_bit_in)
  );

  // LRU Array
  logic lru;
  logic lru_en;
  logic lru_in;

  vc_ResetRegfile_1r1w#(1,8) lru_array
  (
    .clk        (clk),
    .reset      (reset),
    .read_addr  (cachereq_addr_index),
    .read_data  (lru),
    .write_en   (lru_en),
    .write_addr (cachereq_addr_index),
    .write_data (lru_in)
  );

  logic tag_match_1_reg_out;
  logic tag_match_en;

  vc_EnResetReg #(1,0) tag_match_1_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (tag_match_en),
    .d      (tag_match_1_valid),
    .q      (tag_match_1_reg_out)
  );

  logic tag_match_0_reg_out;

  vc_EnResetReg #(1,0) tag_match_0_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (tag_match_en),
    .d      (tag_match_0_valid),
    .q      (tag_match_0_reg_out)
  );

  logic [1:0] hit_TC;
  logic tag_match_1_valid;
  logic tag_match_0_valid;

  assign tag_match_1_valid = tag_match_1 && is_valid_1;
  assign tag_match_0_valid = tag_match_0 && is_valid_0;
  assign hit = ((tag_match_1_reg_out || tag_match_0_reg_out) && !is_init)? 2'b1 : 2'b0;
  assign hit_TC = hit;
 // assign way_select = (tag_match_1_valid || tag_match_0_valid)? lru : lru_in;

  //---------------------------------------------------------------------
  // State Outputs
  //---------------------------------------------------------------------

  //2 Input Mux Don't Care
  localparam d_x   = 1'bx;

  // Read Data Mux Sel
  localparam d_x2   = 2'bx;
  localparam d_arr1 = 2'b0;
  localparam d_arr0 = 2'b1;
  localparam zero  =  2'd2;

  // Memory Request Addr Mux Sel
  localparam evict = 1'b0;
  localparam req   = 1'b1;

  // Write Data Mux Sel
  localparam repl = 1'b0;
  localparam data = 1'b1;

  // Wben Mux Sel
  localparam dec = 1'b0;
  localparam ffff = 1'b1;

  logic tm_1;
  logic tm_0;

  assign tm_1 = tag_match_1_valid;
  assign tm_0 = tag_match_0_valid;

  logic d_arr;
  assign d_arr = (tag_match_1_valid)? d_arr1 : d_arr0;

  logic lru_tm;
  logic tm;
  logic wen1;
  logic wen0;

  assign tm = (tag_match_1_reg_out || tag_match_0_reg_out);
  assign wen1 = (tm)? ( (tag_match_1_reg_out)? 1'b1 : 1'b0 ) : lru;
  assign wen0 = (tm)? ( (tag_match_0_reg_out)? 1'b1 : 1'b0 ) : !lru;
  assign lru_tm = (tm)? ((tag_match_1_reg_out)? 1'b0 : 1'b1): !lru;
  

  logic [1:0] vict;
  assign vict = (lru)? d_arr1 : d_arr0;

  task cs
  (
    input logic       cs_cachereq_rdy,
    input logic       cs_cacheresp_val,
    input logic       cs_cachereq_reg_en,
    input logic       cs_tag_array_1_wen,
    input logic       cs_tag_array_0_wen,
    input logic       cs_tag_array_ren,
    input logic       cs_data_array_1_wen,
    input logic       cs_data_array_0_wen,
    input logic       cs_data_array_1_ren,
    input logic       cs_data_array_0_ren,
    input logic       cs_valid_bit_in,
    input logic       cs_valid_bits_1_write_en,
    input logic       cs_valid_bits_0_write_en,
    input logic       cs_dirty_bit_in,
    input logic       cs_dirty_bits_1_write_en,
    input logic       cs_dirty_bits_0_write_en,
    input logic       cs_lru_in,
    input logic       cs_lru_en,
    input logic [1:0] cs_read_data_zero_mux_sel,
    input logic       cs_read_data_reg_en,
    input logic       cs_mk_addr_mux_sel,
    input logic       cs_evict_addr_reg_en,
    input logic       cs_memreq_addr_mux_sel,
    input logic       cs_write_data_mux_sel,
    input logic       cs_wben_mux_sel,
    input logic       cs_memresp_en,
    input logic       cs_memreq_val,
    input logic       cs_memresp_rdy,
  );
  begin
    proc2cache_reqstream_rdy  = cs_cachereq_rdy;
    proc2cache_respstream_val = cs_cacheresp_val;
    cachereq_reg_en           = cs_cachereq_reg_en;
    tag_array_1_wen           = cs_tag_array_1_wen;
    tag_array_0_wen           = cs_tag_array_0_wen;
    tag_array_ren             = cs_tag_array_ren;
    data_array_1_wen          = cs_data_array_1_wen;
    data_array_0_wen          = cs_data_array_0_wen;
    data_array_1_ren          = cs_data_array_1_ren;
    data_array_0_ren          = cs_data_array_0_ren;
    valid_bit_in              = cs_valid_bit_in;
    valid_bits_1_write_en     = cs_valid_bits_1_write_en;
    valid_bits_0_write_en     = cs_valid_bits_0_write_en;
    dirty_bit_in              = cs_dirty_bit_in;
    dirty_bits_1_write_en     = cs_dirty_bits_1_write_en;
    dirty_bits_0_write_en     = cs_dirty_bits_0_write_en;
    lru_in                    = cs_lru_in;
    lru_en                    = cs_lru_en;
    read_data_zero_mux_sel    = cs_read_data_zero_mux_sel;
    read_data_reg_en          = cs_read_data_reg_en;
    mk_addr_mux_sel           = cs_mk_addr_mux_sel;
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
                               cs( 0,   0,    0,    0,    0,     0,    0,    0,     0,    0,    0,    0,    0,     0,    0,    0,    0,      0,  d_x2,   0,  d_x,  0,  d_x,  d_x,   d_x,  0,   0,  1);
    case ( state_reg )
      //                          cache cache cache tag   tag    tag   data  data   data  data  valid valid valid  dirty dirty dirty lru    lru read   read  mk   evict mem   write wben  mem  mem mem
      //                          req   resp  req   arr   arr    arr   arr   arr    arr   arr   bit   write write  bit   write write in     en  data   data  addr addr addr   data  mux  resp  req resp
      //                          rdy   val   en    wen1  wen0   ren   wen1  wen0   ren1  ren0  in    en1   en0    in    en1   en0              sel    en    sel  en   sel    sel   sel   en   val rdy
      STATE_IDLE:              cs( 1,   0,    1,    0,    0,     0,    0,    0,     0,    0,    0,    0,    0,     0,    0,    0,    0,      0,  d_x2,   0,  d_x,  0,  d_x,   d_x,  d_x,  0,   0,  1);
      STATE_TAG_CHECK:         cs( 0,   0,    0,    0,    0,     1,    0,    0,     0,    0,    0,    0,    0,     0,    0,    0,    0,      0,  d_x2,   0,  d_x,  0,  d_x,   d_x,  d_x,  0,   0,  1);
      STATE_INIT_DATA_ACCESS:  cs( 0,   0,    0,    wen1, wen0,  0,    wen1, wen0,  0,    0,    1,    wen1, wen0,   0,   wen1, wen0, 0,      0,  zero,   1,  d_x,  0,  d_x,   repl, dec,  0,   0,  1);
      STATE_READ_DATA_ACCESS:  cs( 0,   0,    0,    0,    0,     1,    0,    0,     tm_1, tm_0, 0,    0,    0,     0,    0,    0,    lru_tm, 1,  d_arr,  1,  d_x,  0,  d_x,   d_x,  d_x,  0,   0,  1);
      STATE_WRITE_DATA_ACCESS: cs( 0,   0,    0,    wen1, wen0,  0,    wen1, wen0,  0,    0,    1,    0,    0,     1,    wen1, wen0, lru_tm, 1,  zero,   1,  d_x,  0,  d_x,   repl, dec,  0,   0,  1);
      STATE_REFILL_REQUEST:    cs( 0,   0,    0,    0,    0,     0,    0,    0,     0,    0,    0,    0,    0,     0,    0,    0,    0,      0,  d_x2,   0,  d_x,  0,  req,   d_x,  d_x,  0,   1,  1);
      STATE_REFILL_WAIT:       cs( 0,   0,    0,    0,    0,     0,    0,    0,     0,    0,    0,    0,    0,     0,    0,    0,    0,      0,  d_x2,   0,  d_x,  0,  d_x,   d_x,  d_x,  1,   0,  1);
      STATE_REFILL_UPDATE:     cs( 0,   0,    0,    lru,  !lru,  0,    lru,  !lru,  0,    0,    1,    lru, !lru,   0,    0,    0,    0,      0,  d_x2,   0,  d_x,  0,  d_x,   data, ffff, 1,   0,  0);
      STATE_EVICT_PREPARE:     cs( 0,   0,    0,    0,    0,     1,    0,    0,     1,    1,    0,    0,    0,     0,    0,    0,    0,      0,  vict,   1,  !lru, 1,  d_x,   d_x,  d_x,  0,   0,  1);
      STATE_EVICT_REQUEST:     cs( 0,   0,    0,    0,    0,     0,    0,    0,     0,    0,    0,    0,    0,     0,    0,    0,    0,      0,  d_x2,   0,  d_x,  0,  evict, d_x,  d_x,  0,   1,  1);
      STATE_EVICT_WAIT:        cs( 0,   0,    0,    0,    0,     0,    0,    0,     0,    0,    0,    0,    0,     0,    0,    0,    0,      0,  d_x2,   0,  d_x,  0,  d_x,   d_x,  d_x,  1,   1,  1);
      STATE_WAIT:              cs( 0,   1,    0,    0,    0,     0,    0,    0,     0,    0,    0,    0,    0,     0,    0,    0,    0,      0,  d_x2,   0,  d_x,  0,  d_x,   d_x,  d_x,  0,   0,  1);
      default:                 cs( 0,   0,    0,    0,    0,     0,    0,    0,     0,    0,    0,    0,    0,     0,    0,    0,    0,      0,  d_x2,   0,  d_x,  0,  d_x,   d_x,  d_x,  0,   0,  1);

    endcase
  end

endmodule

`endif
