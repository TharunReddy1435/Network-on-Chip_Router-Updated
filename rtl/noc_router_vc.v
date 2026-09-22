// ==============================================================================
// Module: noc_router_vc.v
// Lead: Gowtham (Integration & Verification Lead)
// Project: 5-Port Virtual-Channel Network-on-Chip (NoC) Router
// Description: Advanced 5-Port NoC Router with Dual Virtual Channels (VC0, VC1).
//              Integrates:
//                1. 5 Dual-VC Input Ports (10 FWFT FIFOs total - Shrestitha)
//                2. 10 XY Routing Compute Units (Tharun)
//                3. 5 10-to-1 Round Robin Arbiters (Bhavani)
//                4. 10 Credit Counters for downstream flow control (Bhavani)
//                5. 10x5 High-Speed Crossbar Matrix (Tharun)
// ==============================================================================

`timescale 1ns / 1ps

module noc_router_vc #(
    parameter [1:0] CURRENT_X  = 2'd1,
    parameter [1:0] CURRENT_Y  = 2'd1,
    parameter       DATA_WIDTH = 16,
    parameter       VC_DEPTH   = 4,
    parameter       ADDR_WIDTH = 2
)(
    input  wire                  clk,
    input  wire                  rst_n,

    // 5 Input Channels
    input  wire                  wr_en_local,
    input  wire [DATA_WIDTH-1:0] din_local,
    output wire                  credit_out_local_vc0, credit_out_local_vc1,
    output wire                  full_local_vc0, full_local_vc1,

    input  wire                  wr_en_north,
    input  wire [DATA_WIDTH-1:0] din_north,
    output wire                  credit_out_north_vc0, credit_out_north_vc1,
    output wire                  full_north_vc0, full_north_vc1,

    input  wire                  wr_en_south,
    input  wire [DATA_WIDTH-1:0] din_south,
    output wire                  credit_out_south_vc0, credit_out_south_vc1,
    output wire                  full_south_vc0, full_south_vc1,

    input  wire                  wr_en_east,
    input  wire [DATA_WIDTH-1:0] din_east,
    output wire                  credit_out_east_vc0, credit_out_east_vc1,
    output wire                  full_east_vc0, full_east_vc1,

    input  wire                  wr_en_west,
    input  wire [DATA_WIDTH-1:0] din_west,
    output wire                  credit_out_west_vc0, credit_out_west_vc1,
    output wire                  full_west_vc0, full_west_vc1,

    // 5 Output Channels
    output wire [DATA_WIDTH-1:0] dout_local,
    output wire                  valid_local,
    input  wire                  credit_in_local_vc0, credit_in_local_vc1,

    output wire [DATA_WIDTH-1:0] dout_north,
    output wire                  valid_north,
    input  wire                  credit_in_north_vc0, credit_in_north_vc1,

    output wire [DATA_WIDTH-1:0] dout_south,
    output wire                  valid_south,
    input  wire                  credit_in_south_vc0, credit_in_south_vc1,

    output wire [DATA_WIDTH-1:0] dout_east,
    output wire                  valid_east,
    input  wire                  credit_in_east_vc0, credit_in_east_vc1,

    output wire [DATA_WIDTH-1:0] dout_west,
    output wire                  valid_west,
    input  wire                  credit_in_west_vc0, credit_in_west_vc1
);

    // 10 VC Data Outputs and Status
    wire [DATA_WIDTH-1:0] dout_l_vc0, dout_l_vc1;
    wire [DATA_WIDTH-1:0] dout_n_vc0, dout_n_vc1;
    wire [DATA_WIDTH-1:0] dout_s_vc0, dout_s_vc1;
    wire [DATA_WIDTH-1:0] dout_e_vc0, dout_e_vc1;
    wire [DATA_WIDTH-1:0] dout_w_vc0, dout_w_vc1;

    wire empty_l_vc0, empty_l_vc1;
    wire empty_n_vc0, empty_n_vc1;
    wire empty_s_vc0, empty_s_vc1;
    wire empty_e_vc0, empty_e_vc1;
    wire empty_w_vc0, empty_w_vc1;

    wire req_rdy_l_vc0, req_rdy_l_vc1;
    wire req_rdy_n_vc0, req_rdy_n_vc1;
    wire req_rdy_s_vc0, req_rdy_s_vc1;
    wire req_rdy_e_vc0, req_rdy_e_vc1;
    wire req_rdy_w_vc0, req_rdy_w_vc1;

    wire rd_en_l_vc0, rd_en_l_vc1;
    wire rd_en_n_vc0, rd_en_n_vc1;
    wire rd_en_s_vc0, rd_en_s_vc1;
    wire rd_en_e_vc0, rd_en_e_vc1;
    wire rd_en_w_vc0, rd_en_w_vc1;

    // Routing requests from each of the 10 VCs
    wire [4:0] req_l_vc0, req_l_vc1;
    wire [4:0] req_n_vc0, req_n_vc1;
    wire [4:0] req_s_vc0, req_s_vc1;
    wire [4:0] req_e_vc0, req_e_vc1;
    wire [4:0] req_w_vc0, req_w_vc1;

    // Arbiter Grants
    wire [9:0] grant_local, grant_north, grant_south, grant_east, grant_west;
    wire has_credit_l, has_credit_n, has_credit_s, has_credit_e, has_credit_w;

    // =========================================================================
    // 1. Dual-VC Input Ports (Shrestitha)
    // =========================================================================
    noc_vc_input_port #(.DATA_WIDTH(DATA_WIDTH), .VC_DEPTH(VC_DEPTH), .ADDR_WIDTH(ADDR_WIDTH))
    in_port_local (
        .clk(clk), .rst_n(rst_n),
        .wr_en(wr_en_local), .din(din_local),
        .full_vc0(full_local_vc0), .full_vc1(full_local_vc1),
        .credit_out_vc0(credit_out_local_vc0), .credit_out_vc1(credit_out_local_vc1),
        .rd_en_vc0(rd_en_l_vc0), .dout_vc0(dout_l_vc0), .empty_vc0(empty_l_vc0), .req_ready_vc0(req_rdy_l_vc0),
        .rd_en_vc1(rd_en_l_vc1), .dout_vc1(dout_l_vc1), .empty_vc1(empty_l_vc1), .req_ready_vc1(req_rdy_l_vc1)
    );

    noc_vc_input_port #(.DATA_WIDTH(DATA_WIDTH), .VC_DEPTH(VC_DEPTH), .ADDR_WIDTH(ADDR_WIDTH))
    in_port_north (
        .clk(clk), .rst_n(rst_n),
        .wr_en(wr_en_north), .din(din_north),
        .full_vc0(full_north_vc0), .full_vc1(full_north_vc1),
        .credit_out_vc0(credit_out_north_vc0), .credit_out_vc1(credit_out_north_vc1),
        .rd_en_vc0(rd_en_n_vc0), .dout_vc0(dout_n_vc0), .empty_vc0(empty_n_vc0), .req_ready_vc0(req_rdy_n_vc0),
        .rd_en_vc1(rd_en_n_vc1), .dout_vc1(dout_n_vc1), .empty_vc1(empty_n_vc1), .req_ready_vc1(req_rdy_n_vc1)
    );

    noc_vc_input_port #(.DATA_WIDTH(DATA_WIDTH), .VC_DEPTH(VC_DEPTH), .ADDR_WIDTH(ADDR_WIDTH))
    in_port_south (
        .clk(clk), .rst_n(rst_n),
        .wr_en(wr_en_south), .din(din_south),
        .full_vc0(full_south_vc0), .full_vc1(full_south_vc1),
        .credit_out_vc0(credit_out_south_vc0), .credit_out_vc1(credit_out_south_vc1),
        .rd_en_vc0(rd_en_s_vc0), .dout_vc0(dout_s_vc0), .empty_vc0(empty_s_vc0), .req_ready_vc0(req_rdy_s_vc0),
        .rd_en_vc1(rd_en_s_vc1), .dout_vc1(dout_s_vc1), .empty_vc1(empty_s_vc1), .req_ready_vc1(req_rdy_s_vc1)
    );

    noc_vc_input_port #(.DATA_WIDTH(DATA_WIDTH), .VC_DEPTH(VC_DEPTH), .ADDR_WIDTH(ADDR_WIDTH))
    in_port_east (
        .clk(clk), .rst_n(rst_n),
        .wr_en(wr_en_east), .din(din_east),
        .full_vc0(full_east_vc0), .full_vc1(full_east_vc1),
        .credit_out_vc0(credit_out_east_vc0), .credit_out_vc1(credit_out_east_vc1),
        .rd_en_vc0(rd_en_e_vc0), .dout_vc0(dout_e_vc0), .empty_vc0(empty_e_vc0), .req_ready_vc0(req_rdy_e_vc0),
        .rd_en_vc1(rd_en_e_vc1), .dout_vc1(dout_e_vc1), .empty_vc1(empty_e_vc1), .req_ready_vc1(req_rdy_e_vc1)
    );

    noc_vc_input_port #(.DATA_WIDTH(DATA_WIDTH), .VC_DEPTH(VC_DEPTH), .ADDR_WIDTH(ADDR_WIDTH))
    in_port_west (
        .clk(clk), .rst_n(rst_n),
        .wr_en(wr_en_west), .din(din_west),
        .full_vc0(full_west_vc0), .full_vc1(full_west_vc1),
        .credit_out_vc0(credit_out_west_vc0), .credit_out_vc1(credit_out_west_vc1),
        .rd_en_vc0(rd_en_w_vc0), .dout_vc0(dout_w_vc0), .empty_vc0(empty_w_vc0), .req_ready_vc0(req_rdy_w_vc0),
        .rd_en_vc1(rd_en_w_vc1), .dout_vc1(dout_w_vc1), .empty_vc1(empty_w_vc1), .req_ready_vc1(req_rdy_w_vc1)
    );

    // =========================================================================
    // 2. XY Routing Evaluation Units for 10 VCs (Tharun)
    // =========================================================================
    xy_routing #(.CURRENT_X(CURRENT_X), .CURRENT_Y(CURRENT_Y)) rc_l_vc0 (.valid_in(req_rdy_l_vc0), .dest_x(dout_l_vc0[13:12]), .dest_y(dout_l_vc0[11:10]), .req_port(req_l_vc0), .port_id());
    xy_routing #(.CURRENT_X(CURRENT_X), .CURRENT_Y(CURRENT_Y)) rc_l_vc1 (.valid_in(req_rdy_l_vc1), .dest_x(dout_l_vc1[13:12]), .dest_y(dout_l_vc1[11:10]), .req_port(req_l_vc1), .port_id());

    xy_routing #(.CURRENT_X(CURRENT_X), .CURRENT_Y(CURRENT_Y)) rc_n_vc0 (.valid_in(req_rdy_n_vc0), .dest_x(dout_n_vc0[13:12]), .dest_y(dout_n_vc0[11:10]), .req_port(req_n_vc0), .port_id());
    xy_routing #(.CURRENT_X(CURRENT_X), .CURRENT_Y(CURRENT_Y)) rc_n_vc1 (.valid_in(req_rdy_n_vc1), .dest_x(dout_n_vc1[13:12]), .dest_y(dout_n_vc1[11:10]), .req_port(req_n_vc1), .port_id());

    xy_routing #(.CURRENT_X(CURRENT_X), .CURRENT_Y(CURRENT_Y)) rc_s_vc0 (.valid_in(req_rdy_s_vc0), .dest_x(dout_s_vc0[13:12]), .dest_y(dout_s_vc0[11:10]), .req_port(req_s_vc0), .port_id());
    xy_routing #(.CURRENT_X(CURRENT_X), .CURRENT_Y(CURRENT_Y)) rc_s_vc1 (.valid_in(req_rdy_s_vc1), .dest_x(dout_s_vc1[13:12]), .dest_y(dout_s_vc1[11:10]), .req_port(req_s_vc1), .port_id());

    xy_routing #(.CURRENT_X(CURRENT_X), .CURRENT_Y(CURRENT_Y)) rc_e_vc0 (.valid_in(req_rdy_e_vc0), .dest_x(dout_e_vc0[13:12]), .dest_y(dout_e_vc0[11:10]), .req_port(req_e_vc0), .port_id());
    xy_routing #(.CURRENT_X(CURRENT_X), .CURRENT_Y(CURRENT_Y)) rc_e_vc1 (.valid_in(req_rdy_e_vc1), .dest_x(dout_e_vc1[13:12]), .dest_y(dout_e_vc1[11:10]), .req_port(req_e_vc1), .port_id());

    xy_routing #(.CURRENT_X(CURRENT_X), .CURRENT_Y(CURRENT_Y)) rc_w_vc0 (.valid_in(req_rdy_w_vc0), .dest_x(dout_w_vc0[13:12]), .dest_y(dout_w_vc0[11:10]), .req_port(req_w_vc0), .port_id());
    xy_routing #(.CURRENT_X(CURRENT_X), .CURRENT_Y(CURRENT_Y)) rc_w_vc1 (.valid_in(req_rdy_w_vc1), .dest_x(dout_w_vc1[13:12]), .dest_y(dout_w_vc1[11:10]), .req_port(req_w_vc1), .port_id());

    // =========================================================================
    // 3. Credit Counters for Downstream Flow Control (Bhavani)
    // =========================================================================
    credit_counter #(.MAX_CREDITS(VC_DEPTH*2), .COUNTER_WIDTH(ADDR_WIDTH+2))
    cc_l (.clk(clk), .rst_n(rst_n), .tx_fire(valid_local), .credit_in(credit_in_local_vc0 | credit_in_local_vc1), .has_credit(has_credit_l), .credit_count());

    credit_counter #(.MAX_CREDITS(VC_DEPTH*2), .COUNTER_WIDTH(ADDR_WIDTH+2))
    cc_n (.clk(clk), .rst_n(rst_n), .tx_fire(valid_north), .credit_in(credit_in_north_vc0 | credit_in_north_vc1), .has_credit(has_credit_n), .credit_count());

    credit_counter #(.MAX_CREDITS(VC_DEPTH*2), .COUNTER_WIDTH(ADDR_WIDTH+2))
    cc_s (.clk(clk), .rst_n(rst_n), .tx_fire(valid_south), .credit_in(credit_in_south_vc0 | credit_in_south_vc1), .has_credit(has_credit_s), .credit_count());

    credit_counter #(.MAX_CREDITS(VC_DEPTH*2), .COUNTER_WIDTH(ADDR_WIDTH+2))
    cc_e (.clk(clk), .rst_n(rst_n), .tx_fire(valid_east),  .credit_in(credit_in_east_vc0  | credit_in_east_vc1),  .has_credit(has_credit_e), .credit_count());

    credit_counter #(.MAX_CREDITS(VC_DEPTH*2), .COUNTER_WIDTH(ADDR_WIDTH+2))
    cc_w (.clk(clk), .rst_n(rst_n), .tx_fire(valid_west),  .credit_in(credit_in_west_vc0  | credit_in_west_vc1),  .has_credit(has_credit_w), .credit_count());

    // =========================================================================
    // 4. 10-Input Round Robin Arbiters for Output Ports (Bhavani)
    // =========================================================================
    wire [9:0] req_for_local = {req_w_vc1[0], req_w_vc0[0], req_e_vc1[0], req_e_vc0[0],
                                req_s_vc1[0], req_s_vc0[0], req_n_vc1[0], req_n_vc0[0],
                                req_l_vc1[0], req_l_vc0[0]};
    rr_arbiter_10 arb_local (.clk(clk), .rst_n(rst_n), .req(req_for_local), .credit_ready(has_credit_l), .grant(grant_local));

    wire [9:0] req_for_north = {req_w_vc1[1], req_w_vc0[1], req_e_vc1[1], req_e_vc0[1],
                                req_s_vc1[1], req_s_vc0[1], req_n_vc1[1], req_n_vc0[1],
                                req_l_vc1[1], req_l_vc0[1]};
    rr_arbiter_10 arb_north (.clk(clk), .rst_n(rst_n), .req(req_for_north), .credit_ready(has_credit_n), .grant(grant_north));

    wire [9:0] req_for_south = {req_w_vc1[2], req_w_vc0[2], req_e_vc1[2], req_e_vc0[2],
                                req_s_vc1[2], req_s_vc0[2], req_n_vc1[2], req_n_vc0[2],
                                req_l_vc1[2], req_l_vc0[2]};
    rr_arbiter_10 arb_south (.clk(clk), .rst_n(rst_n), .req(req_for_south), .credit_ready(has_credit_s), .grant(grant_south));

    wire [9:0] req_for_east  = {req_w_vc1[3], req_w_vc0[3], req_e_vc1[3], req_e_vc0[3],
                                req_s_vc1[3], req_s_vc0[3], req_n_vc1[3], req_n_vc0[3],
                                req_l_vc1[3], req_l_vc0[3]};
    rr_arbiter_10 arb_east  (.clk(clk), .rst_n(rst_n), .req(req_for_east), .credit_ready(has_credit_e), .grant(grant_east));

    wire [9:0] req_for_west  = {req_w_vc1[4], req_w_vc0[4], req_e_vc1[4], req_e_vc0[4],
                                req_s_vc1[4], req_s_vc0[4], req_n_vc1[4], req_n_vc0[4],
                                req_l_vc1[4], req_l_vc0[4]};
    rr_arbiter_10 arb_west  (.clk(clk), .rst_n(rst_n), .req(req_for_west), .credit_ready(has_credit_w), .grant(grant_west));

    // =========================================================================
    // 5. FIFO Read Enables per Virtual Channel (Only when granted and not empty)
    // =========================================================================
    assign rd_en_l_vc0 = (grant_local[0] | grant_north[0] | grant_south[0] | grant_east[0] | grant_west[0]) & !empty_l_vc0;
    assign rd_en_l_vc1 = (grant_local[1] | grant_north[1] | grant_south[1] | grant_east[1] | grant_west[1]) & !empty_l_vc1;
    assign rd_en_n_vc0 = (grant_local[2] | grant_north[2] | grant_south[2] | grant_east[2] | grant_west[2]) & !empty_n_vc0;
    assign rd_en_n_vc1 = (grant_local[3] | grant_north[3] | grant_south[3] | grant_east[3] | grant_west[3]) & !empty_n_vc1;
    assign rd_en_s_vc0 = (grant_local[4] | grant_north[4] | grant_south[4] | grant_east[4] | grant_west[4]) & !empty_s_vc0;
    assign rd_en_s_vc1 = (grant_local[5] | grant_north[5] | grant_south[5] | grant_east[5] | grant_west[5]) & !empty_s_vc1;
    assign rd_en_e_vc0 = (grant_local[6] | grant_north[6] | grant_south[6] | grant_east[6] | grant_west[6]) & !empty_e_vc0;
    assign rd_en_e_vc1 = (grant_local[7] | grant_north[7] | grant_south[7] | grant_east[7] | grant_west[7]) & !empty_e_vc1;
    assign rd_en_w_vc0 = (grant_local[8] | grant_north[8] | grant_south[8] | grant_east[8] | grant_west[8]) & !empty_w_vc0;
    assign rd_en_w_vc1 = (grant_local[9] | grant_north[9] | grant_south[9] | grant_east[9] | grant_west[9]) & !empty_w_vc1;

    // Vector of empty status for all 10 queues
    wire [9:0] all_empty = {empty_w_vc1, empty_w_vc0, empty_e_vc1, empty_e_vc0,
                            empty_s_vc1, empty_s_vc0, empty_n_vc1, empty_n_vc0,
                            empty_l_vc1, empty_l_vc0};

    // =========================================================================
    // 6. 10x5 Crossbar Switch Fabric (Tharun)
    // =========================================================================
    crossbar_10x5 #(.DATA_WIDTH(DATA_WIDTH))
    xbar_vc (
        .din_local_vc0(dout_l_vc0), .din_local_vc1(dout_l_vc1),
        .din_north_vc0(dout_n_vc0), .din_north_vc1(dout_n_vc1),
        .din_south_vc0(dout_s_vc0), .din_south_vc1(dout_s_vc1),
        .din_east_vc0(dout_e_vc0),  .din_east_vc1(dout_e_vc1),
        .din_west_vc0(dout_w_vc0),  .din_west_vc1(dout_w_vc1),

        .empty_inputs(all_empty),

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
