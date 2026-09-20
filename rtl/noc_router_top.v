// ==============================================================================
// Module: noc_router_top.v
// Lead: Gowtham (Integration & Verification Lead)
// Project: 5-Port Network-on-Chip (NoC) Router
// Description: Top-Level 5-Port NoC Router module integrating:
//                1. 5 Input Port FIFOs (Shrestitha)
//                2. 5 Dimension-Order XY Routing Units (Tharun)
//                3. 5-Output 5x5 Crossbar Matrix (Tharun)
//                4. 5 Starvation-Free Round-Robin Arbiters (Bhavani)
//                5. 5 Credit Counter Flow Control Blocks (Bhavani)
//
// Topology & Coordinate Setup:
//   - Parameterized coordinates (CURRENT_X, CURRENT_Y)
//   - Ports: Local (0), North (1), South (2), East (3), West (4)
// ==============================================================================

`timescale 1ns / 1ps

module noc_router_top #(
    parameter [1:0] CURRENT_X  = 2'd1,
    parameter [1:0] CURRENT_Y  = 2'd1,
    parameter       DATA_WIDTH = 16,
    parameter       FIFO_DEPTH = 8,
    parameter       ADDR_WIDTH = 3
)(
    input  wire                  clk,
    input  wire                  rst_n,

    // =========================================================================
    // 5 Input Channels (from Neighboring Routers / Local Processing Element)
    // =========================================================================
    // Local Port (PE)
    input  wire                  wr_en_local,
    input  wire [DATA_WIDTH-1:0] din_local,
    output wire                  credit_out_local,
    output wire                  full_local,

    // North Port
    input  wire                  wr_en_north,
    input  wire [DATA_WIDTH-1:0] din_north,
    output wire                  credit_out_north,
    output wire                  full_north,

    // South Port
    input  wire                  wr_en_south,
    input  wire [DATA_WIDTH-1:0] din_south,
    output wire                  credit_out_south,
    output wire                  full_south,

    // East Port
    input  wire                  wr_en_east,
    input  wire [DATA_WIDTH-1:0] din_east,
    output wire                  credit_out_east,
    output wire                  full_east,

    // West Port
    input  wire                  wr_en_west,
    input  wire [DATA_WIDTH-1:0] din_west,
    output wire                  credit_out_west,
    output wire                  full_west,

    // =========================================================================
    // 5 Output Channels (to Neighboring Routers / Local Processing Element)
    // =========================================================================
    // Local Port (PE)
    output wire [DATA_WIDTH-1:0] dout_local,
    output wire                  valid_local,
    input  wire                  credit_in_local,

    // North Port
    output wire [DATA_WIDTH-1:0] dout_north,
    output wire                  valid_north,
    input  wire                  credit_in_north,

    // South Port
    output wire [DATA_WIDTH-1:0] dout_south,
    output wire                  valid_south,
    input  wire                  credit_in_south,

    // East Port
    output wire [DATA_WIDTH-1:0] dout_east,
    output wire                  valid_east,
    input  wire                  credit_in_east,

    // West Port
    output wire [DATA_WIDTH-1:0] dout_west,
    output wire                  valid_west,
    input  wire                  credit_in_west
);

    // =========================================================================
    // Internal Signals
    // =========================================================================
    // FIFO Read Data & Flags
    wire [DATA_WIDTH-1:0] fifo_dout_local, fifo_dout_north, fifo_dout_south, fifo_dout_east, fifo_dout_west;
    wire                  empty_local, empty_north, empty_south, empty_east, empty_west;
    wire                  rd_en_local, rd_en_north, rd_en_south, rd_en_east, rd_en_west;

    // Routing Unit Requests (One-Hot per Input: [0]=Local, [1]=North, [2]=South, [3]=East, [4]=West)
    wire [4:0] req_local, req_north, req_south, req_east, req_west;

    // Arbiter Grant Vectors (One per Output Port: [0]=Local, [1]=North, [2]=South, [3]=East, [4]=West)
    wire [4:0] grant_local, grant_north, grant_south, grant_east, grant_west;

    // Credit Counter Status (from Downstream Receivers)
    wire has_credit_local, has_credit_north, has_credit_south, has_credit_east, has_credit_west;

    // Flit Header Parsing (Destination Coordinates)
    // Assuming standard format: [DATA_WIDTH-3 : DATA_WIDTH-4] = Dest_X, [DATA_WIDTH-5 : DATA_WIDTH-6] = Dest_Y
    wire [1:0] dest_x_local = fifo_dout_local[DATA_WIDTH-3 : DATA_WIDTH-4];
    wire [1:0] dest_y_local = fifo_dout_local[DATA_WIDTH-5 : DATA_WIDTH-6];

    wire [1:0] dest_x_north = fifo_dout_north[DATA_WIDTH-3 : DATA_WIDTH-4];
    wire [1:0] dest_y_north = fifo_dout_north[DATA_WIDTH-5 : DATA_WIDTH-6];

    wire [1:0] dest_x_south = fifo_dout_south[DATA_WIDTH-3 : DATA_WIDTH-4];
    wire [1:0] dest_y_south = fifo_dout_south[DATA_WIDTH-5 : DATA_WIDTH-6];

    wire [1:0] dest_x_east  = fifo_dout_east[DATA_WIDTH-3 : DATA_WIDTH-4];
    wire [1:0] dest_y_east  = fifo_dout_east[DATA_WIDTH-5 : DATA_WIDTH-6];

    wire [1:0] dest_x_west  = fifo_dout_west[DATA_WIDTH-3 : DATA_WIDTH-4];
    wire [1:0] dest_y_west  = fifo_dout_west[DATA_WIDTH-5 : DATA_WIDTH-6];

    // =========================================================================
    // 1. Input Buffers (Shrestitha)
    // =========================================================================
    noc_fifo #(.DATA_WIDTH(DATA_WIDTH), .DEPTH(FIFO_DEPTH), .ADDR_WIDTH(ADDR_WIDTH))
    fifo_inst_local (
        .clk(clk), .rst_n(rst_n),
        .wr_en(wr_en_local), .din(din_local), .full(full_local), .almost_full(),
        .rd_en(rd_en_local), .dout(fifo_dout_local), .empty(empty_local),
        .credit_out(credit_out_local), .occupancy()
    );

    noc_fifo #(.DATA_WIDTH(DATA_WIDTH), .DEPTH(FIFO_DEPTH), .ADDR_WIDTH(ADDR_WIDTH))
    fifo_inst_north (
        .clk(clk), .rst_n(rst_n),
        .wr_en(wr_en_north), .din(din_north), .full(full_north), .almost_full(),
        .rd_en(rd_en_north), .dout(fifo_dout_north), .empty(empty_north),
        .credit_out(credit_out_north), .occupancy()
    );

    noc_fifo #(.DATA_WIDTH(DATA_WIDTH), .DEPTH(FIFO_DEPTH), .ADDR_WIDTH(ADDR_WIDTH))
    fifo_inst_south (
        .clk(clk), .rst_n(rst_n),
        .wr_en(wr_en_south), .din(din_south), .full(full_south), .almost_full(),
        .rd_en(rd_en_south), .dout(fifo_dout_south), .empty(empty_south),
        .credit_out(credit_out_south), .occupancy()
    );

    noc_fifo #(.DATA_WIDTH(DATA_WIDTH), .DEPTH(FIFO_DEPTH), .ADDR_WIDTH(ADDR_WIDTH))
    fifo_inst_east (
        .clk(clk), .rst_n(rst_n),
        .wr_en(wr_en_east), .din(din_east), .full(full_east), .almost_full(),
        .rd_en(rd_en_east), .dout(fifo_dout_east), .empty(empty_east),
        .credit_out(credit_out_east), .occupancy()
    );

    noc_fifo #(.DATA_WIDTH(DATA_WIDTH), .DEPTH(FIFO_DEPTH), .ADDR_WIDTH(ADDR_WIDTH))
    fifo_inst_west (
        .clk(clk), .rst_n(rst_n),
        .wr_en(wr_en_west), .din(din_west), .full(full_west), .almost_full(),
        .rd_en(rd_en_west), .dout(fifo_dout_west), .empty(empty_west),
        .credit_out(credit_out_west), .occupancy()
    );

    // =========================================================================
    // 2. XY Route Compute Units (Tharun)
    // =========================================================================
    xy_routing #(.CURRENT_X(CURRENT_X), .CURRENT_Y(CURRENT_Y))
    rc_inst_local (
        .valid_in(!empty_local), .dest_x(dest_x_local), .dest_y(dest_y_local),
        .req_port(req_local), .port_id()
    );

    xy_routing #(.CURRENT_X(CURRENT_X), .CURRENT_Y(CURRENT_Y))
    rc_inst_north (
        .valid_in(!empty_north), .dest_x(dest_x_north), .dest_y(dest_y_north),
        .req_port(req_north), .port_id()
    );

    xy_routing #(.CURRENT_X(CURRENT_X), .CURRENT_Y(CURRENT_Y))
    rc_inst_south (
        .valid_in(!empty_south), .dest_x(dest_x_south), .dest_y(dest_y_south),
        .req_port(req_south), .port_id()
    );

    xy_routing #(.CURRENT_X(CURRENT_X), .CURRENT_Y(CURRENT_Y))
    rc_inst_east (
        .valid_in(!empty_east), .dest_x(dest_x_east), .dest_y(dest_y_east),
        .req_port(req_east), .port_id()
    );

    xy_routing #(.CURRENT_X(CURRENT_X), .CURRENT_Y(CURRENT_Y))
    rc_inst_west (
        .valid_in(!empty_west), .dest_x(dest_x_west), .dest_y(dest_y_west),
        .req_port(req_west), .port_id()
    );

    // =========================================================================
    // 3. Credit Counters for Downstream Routers (Bhavani)
    // =========================================================================
    credit_counter #(.MAX_CREDITS(FIFO_DEPTH), .COUNTER_WIDTH(ADDR_WIDTH+1))
    cc_inst_local (
        .clk(clk), .rst_n(rst_n),
        .tx_fire(|grant_local), .credit_in(credit_in_local),
        .has_credit(has_credit_local), .credit_count()
    );

    credit_counter #(.MAX_CREDITS(FIFO_DEPTH), .COUNTER_WIDTH(ADDR_WIDTH+1))
    cc_inst_north (
        .clk(clk), .rst_n(rst_n),
        .tx_fire(|grant_north), .credit_in(credit_in_north),
        .has_credit(has_credit_north), .credit_count()
    );

    credit_counter #(.MAX_CREDITS(FIFO_DEPTH), .COUNTER_WIDTH(ADDR_WIDTH+1))
    cc_inst_south (
        .clk(clk), .rst_n(rst_n),
        .tx_fire(|grant_south), .credit_in(credit_in_south),
        .has_credit(has_credit_south), .credit_count()
    );

    credit_counter #(.MAX_CREDITS(FIFO_DEPTH), .COUNTER_WIDTH(ADDR_WIDTH+1))
    cc_inst_east (
        .clk(clk), .rst_n(rst_n),
        .tx_fire(|grant_east), .credit_in(credit_in_east),
        .has_credit(has_credit_east), .credit_count()
    );

    credit_counter #(.MAX_CREDITS(FIFO_DEPTH), .COUNTER_WIDTH(ADDR_WIDTH+1))
    cc_inst_west (
        .clk(clk), .rst_n(rst_n),
        .tx_fire(|grant_west), .credit_in(credit_in_west),
        .has_credit(has_credit_west), .credit_count()
    );

    // =========================================================================
    // 4. Round Robin Arbiters for Output Ports (Bhavani)
    //    Each arbiter takes requests from all 5 inputs for its specific output
    // =========================================================================
    // Local Output Arbiter: checks bit [0] of all request vectors
    wire [4:0] req_for_local = {req_west[0], req_east[0], req_south[0], req_north[0], req_local[0]};
    rr_arbiter_5 arb_inst_local (
        .clk(clk), .rst_n(rst_n),
        .req(req_for_local), .credit_ready(has_credit_local),
        .grant(grant_local)
    );

    // North Output Arbiter: checks bit [1] of all request vectors
    wire [4:0] req_for_north = {req_west[1], req_east[1], req_south[1], req_north[1], req_local[1]};
    rr_arbiter_5 arb_inst_north (
        .clk(clk), .rst_n(rst_n),
        .req(req_for_north), .credit_ready(has_credit_north),
        .grant(grant_north)
    );

    // South Output Arbiter: checks bit [2] of all request vectors
    wire [4:0] req_for_south = {req_west[2], req_east[2], req_south[2], req_north[2], req_local[2]};
    rr_arbiter_5 arb_inst_south (
        .clk(clk), .rst_n(rst_n),
        .req(req_for_south), .credit_ready(has_credit_south),
        .grant(grant_south)
    );

    // East Output Arbiter: checks bit [3] of all request vectors
    wire [4:0] req_for_east = {req_west[3], req_east[3], req_south[3], req_north[3], req_local[3]};
    rr_arbiter_5 arb_inst_east (
        .clk(clk), .rst_n(rst_n),
        .req(req_for_east), .credit_ready(has_credit_east),
        .grant(grant_east)
    );

    // West Output Arbiter: checks bit [4] of all request vectors
    wire [4:0] req_for_west = {req_west[4], req_east[4], req_south[4], req_north[4], req_local[4]};
    rr_arbiter_5 arb_inst_west (
        .clk(clk), .rst_n(rst_n),
        .req(req_for_west), .credit_ready(has_credit_west),
        .grant(grant_west)
    );

    // =========================================================================
    // 5. FIFO Read Enables
    //    An input FIFO is read whenever any output arbiter grants that input
    // =========================================================================
    assign rd_en_local = grant_local[0] | grant_north[0] | grant_south[0] | grant_east[0] | grant_west[0];
    assign rd_en_north = grant_local[1] | grant_north[1] | grant_south[1] | grant_east[1] | grant_west[1];
    assign rd_en_south = grant_local[2] | grant_north[2] | grant_south[2] | grant_east[2] | grant_west[2];
    assign rd_en_east  = grant_local[3] | grant_north[3] | grant_south[3] | grant_east[3] | grant_west[3];
    assign rd_en_west  = grant_local[4] | grant_north[4] | grant_south[4] | grant_east[4] | grant_west[4];

    // =========================================================================
    // 6. Crossbar Switch Fabric (Tharun)
    // =========================================================================
    crossbar_5x5 #(.DATA_WIDTH(DATA_WIDTH))
    xbar_inst (
        .din_local(fifo_dout_local),
        .din_north(fifo_dout_north),
        .din_south(fifo_dout_south),
        .din_east(fifo_dout_east),
        .din_west(fifo_dout_west),

        .grant_local(grant_local),
        .grant_north(grant_north),
        .grant_south(grant_south),
        .grant_east(grant_east),
        .grant_west(grant_west),

        .dout_local(dout_local),
        .dout_north(dout_north),
        .dout_south(dout_south),
        .dout_east(dout_east),
        .dout_west(dout_west),

        .valid_local(valid_local),
        .valid_north(valid_north),
        .valid_south(valid_south),
        .valid_east(valid_east),
        .valid_west(valid_west)
    );

endmodule
