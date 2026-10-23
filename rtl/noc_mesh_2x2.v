// ==============================================================================
// Module: noc_mesh_2x2.v
// Lead: Gowtham (Integration & Verification Lead)
// Project: 2x2 2D-Mesh Network-on-Chip (NoC) Interconnect
// Description: Multi-core 2x2 2D-Mesh Network interconnecting 4 Virtual-Channel
//              routers and 4 Processing Elements (PE0..PE3).
//
// Topology Layout:
//
//      [PE0]                   [PE1]
//        │                       │
//   ┌────▼────┐   E <---> W   ┌────▼────┐
//   │ R (0,0) ├───────────────┤ R (1,0) │
//   └────┬────┘               └────┬────┘
//        │ S                     │ S
//        ▲                       ▲
//        │ N                     │ N
//   ┌────┴────┐   E <---> W   ┌────┴────┐
//   │ R (0,1) ├───────────────┤ R (1,1) │
//   └────▲────┘               └────▲────┘
//        │                       │
//      [PE2]                   [PE3]
//
// Flit Routing across Mesh:
//   Packets injected at PE0 (0,0) destined for PE3 (1,1) traverse:
//   R(0,0) --[East]--> R(1,0) --[South]--> R(1,1) --[Local]--> PE3
// ==============================================================================

`timescale 1ns / 1ps

module noc_mesh_2x2 #(
    parameter DATA_WIDTH       = 16,
    parameter VC_DEPTH         = 4,
    parameter ADDR_WIDTH       = 2,
    parameter USE_CAPS_ARBITER = 0  // 0: Standard Round-Robin, 1: Congestion-Aware CAPS
)(
    input  wire                  clk,
    input  wire                  rst_n,

    // =========================================================================
    // PE 0 Interface (Router 0,0)
    // =========================================================================
    input  wire                  pe0_wr_en,
    input  wire [DATA_WIDTH-1:0] pe0_din,
    output wire                  pe0_credit_out_vc0,
    output wire                  pe0_credit_out_vc1,
    output wire                  pe0_full_vc0,
    output wire                  pe0_full_vc1,
    output wire [DATA_WIDTH-1:0] pe0_dout,
    output wire                  pe0_valid,
    input  wire                  pe0_credit_in_vc0,
    input  wire                  pe0_credit_in_vc1,

    // =========================================================================
    // PE 1 Interface (Router 1,0)
    // =========================================================================
    input  wire                  pe1_wr_en,
    input  wire [DATA_WIDTH-1:0] pe1_din,
    output wire                  pe1_credit_out_vc0,
    output wire                  pe1_credit_out_vc1,
    output wire                  pe1_full_vc0,
    output wire                  pe1_full_vc1,
    output wire [DATA_WIDTH-1:0] pe1_dout,
    output wire                  pe1_valid,
    input  wire                  pe1_credit_in_vc0,
    input  wire                  pe1_credit_in_vc1,

    // =========================================================================
    // PE 2 Interface (Router 0,1)
    // =========================================================================
    input  wire                  pe2_wr_en,
    input  wire [DATA_WIDTH-1:0] pe2_din,
    output wire                  pe2_credit_out_vc0,
    output wire                  pe2_credit_out_vc1,
    output wire                  pe2_full_vc0,
    output wire                  pe2_full_vc1,
    output wire [DATA_WIDTH-1:0] pe2_dout,
    output wire                  pe2_valid,
    input  wire                  pe2_credit_in_vc0,
    input  wire                  pe2_credit_in_vc1,

    // =========================================================================
    // PE 3 Interface (Router 1,1)
    // =========================================================================
    input  wire                  pe3_wr_en,
    input  wire [DATA_WIDTH-1:0] pe3_din,
    output wire                  pe3_credit_out_vc0,
    output wire                  pe3_credit_out_vc1,
    output wire                  pe3_full_vc0,
    output wire                  pe3_full_vc1,
    output wire [DATA_WIDTH-1:0] pe3_dout,
    output wire                  pe3_valid,
    input  wire                  pe3_credit_in_vc0,
    input  wire                  pe3_credit_in_vc1
);

    // =========================================================================
    // Inter-Router Channels
    // =========================================================================
    // Horizontal Row 0: R(0,0) <---> R(1,0)
    wire [DATA_WIDTH-1:0] r00_to_r10_data, r10_to_r00_data;
    wire                  r00_to_r10_val,  r10_to_r00_val;
    wire                  r00_e_cred0, r00_e_cred1;
    wire                  r10_w_cred0, r10_w_cred1;

    // Horizontal Row 1: R(0,1) <---> R(1,1)
    wire [DATA_WIDTH-1:0] r01_to_r11_data, r11_to_r01_data;
    wire                  r01_to_r11_val,  r11_to_r01_val;
    wire                  r01_e_cred0, r01_e_cred1;
    wire                  r11_w_cred0, r11_w_cred1;

    // Vertical Col 0: R(0,0) <---> R(0,1)
    wire [DATA_WIDTH-1:0] r00_to_r01_data, r01_to_r00_data;
    wire                  r00_to_r01_val,  r01_to_r00_val;
    wire                  r00_s_cred0, r00_s_cred1;
    wire                  r01_n_cred0, r01_n_cred1;

    // Vertical Col 1: R(1,0) <---> R(1,1)
    wire [DATA_WIDTH-1:0] r10_to_r11_data, r11_to_r10_data;
    wire                  r10_to_r11_val,  r11_to_r10_val;
    wire                  r10_s_cred0, r10_s_cred1;
    wire                  r11_n_cred0, r11_n_cred1;

    // =========================================================================
    // Router (0,0)
    // =========================================================================
    noc_router_vc #(
        .CURRENT_X(2'd0), .CURRENT_Y(2'd0),
        .DATA_WIDTH(DATA_WIDTH), .VC_DEPTH(VC_DEPTH), .ADDR_WIDTH(ADDR_WIDTH),
        .USE_CAPS_ARBITER(USE_CAPS_ARBITER)
    ) router_00 (
        .clk(clk), .rst_n(rst_n),

        // Local PE 0
        .wr_en_local(pe0_wr_en), .din_local(pe0_din),
        .credit_out_local_vc0(pe0_credit_out_vc0), .credit_out_local_vc1(pe0_credit_out_vc1),
        .full_local_vc0(pe0_full_vc0), .full_local_vc1(pe0_full_vc1),
        .dout_local(pe0_dout), .valid_local(pe0_valid),
        .credit_in_local_vc0(pe0_credit_in_vc0), .credit_in_local_vc1(pe0_credit_in_vc1),

        // North (Boundary - tied off)
        .wr_en_north(1'b0), .din_north({DATA_WIDTH{1'b0}}),
        .credit_out_north_vc0(), .credit_out_north_vc1(), .full_north_vc0(), .full_north_vc1(),
        .dout_north(), .valid_north(), .credit_in_north_vc0(1'b0), .credit_in_north_vc1(1'b0),

        // South <---> R(0,1) North
        .wr_en_south(r01_to_r00_val), .din_south(r01_to_r00_data),
        .credit_out_south_vc0(r00_s_cred0), .credit_out_south_vc1(r00_s_cred1),
        .full_south_vc0(), .full_south_vc1(),
        .dout_south(r00_to_r01_data), .valid_south(r00_to_r01_val),
        .credit_in_south_vc0(r01_n_cred0), .credit_in_south_vc1(r01_n_cred1),

        // East <---> R(1,0) West
        .wr_en_east(r10_to_r00_val), .din_east(r10_to_r00_data),
        .credit_out_east_vc0(r00_e_cred0), .credit_out_east_vc1(r00_e_cred1),
        .full_east_vc0(), .full_east_vc1(),
        .dout_east(r00_to_r10_data), .valid_east(r00_to_r10_val),
        .credit_in_east_vc0(r10_w_cred0), .credit_in_east_vc1(r10_w_cred1),

        // West (Boundary - tied off)
        .wr_en_west(1'b0), .din_west({DATA_WIDTH{1'b0}}),
        .credit_out_west_vc0(), .credit_out_west_vc1(), .full_west_vc0(), .full_west_vc1(),
        .dout_west(), .valid_west(), .credit_in_west_vc0(1'b0), .credit_in_west_vc1(1'b0)
    );

    // =========================================================================
    // Router (1,0)
    // =========================================================================
    noc_router_vc #(
        .CURRENT_X(2'd1), .CURRENT_Y(2'd0),
        .DATA_WIDTH(DATA_WIDTH), .VC_DEPTH(VC_DEPTH), .ADDR_WIDTH(ADDR_WIDTH),
        .USE_CAPS_ARBITER(USE_CAPS_ARBITER)
    ) router_10 (
        .clk(clk), .rst_n(rst_n),

        // Local PE 1
        .wr_en_local(pe1_wr_en), .din_local(pe1_din),
        .credit_out_local_vc0(pe1_credit_out_vc0), .credit_out_local_vc1(pe1_credit_out_vc1),
        .full_local_vc0(pe1_full_vc0), .full_local_vc1(pe1_full_vc1),
        .dout_local(pe1_dout), .valid_local(pe1_valid),
        .credit_in_local_vc0(pe1_credit_in_vc0), .credit_in_local_vc1(pe1_credit_in_vc1),

        // North (Boundary - tied off)
        .wr_en_north(1'b0), .din_north({DATA_WIDTH{1'b0}}),
        .credit_out_north_vc0(), .credit_out_north_vc1(), .full_north_vc0(), .full_north_vc1(),
        .dout_north(), .valid_north(), .credit_in_north_vc0(1'b0), .credit_in_north_vc1(1'b0),

        // South <---> R(1,1) North
        .wr_en_south(r11_to_r10_val), .din_south(r11_to_r10_data),
        .credit_out_south_vc0(r10_s_cred0), .credit_out_south_vc1(r10_s_cred1),
        .full_south_vc0(), .full_south_vc1(),
        .dout_south(r10_to_r11_data), .valid_south(r10_to_r11_val),
        .credit_in_south_vc0(r11_n_cred0), .credit_in_south_vc1(r11_n_cred1),

        // East (Boundary - tied off)
        .wr_en_east(1'b0), .din_east({DATA_WIDTH{1'b0}}),
        .credit_out_east_vc0(), .credit_out_east_vc1(), .full_east_vc0(), .full_east_vc1(),
        .dout_east(), .valid_east(), .credit_in_east_vc0(1'b0), .credit_in_east_vc1(1'b0),

        // West <---> R(0,0) East
        .wr_en_west(r00_to_r10_val), .din_west(r00_to_r10_data),
        .credit_out_west_vc0(r10_w_cred0), .credit_out_west_vc1(r10_w_cred1),
        .full_west_vc0(), .full_west_vc1(),
        .dout_west(r10_to_r00_data), .valid_west(r10_to_r00_val),
        .credit_in_west_vc0(r00_e_cred0), .credit_in_west_vc1(r00_e_cred1)
    );

    // =========================================================================
    // Router (0,1)
    // =========================================================================
    noc_router_vc #(
        .CURRENT_X(2'd0), .CURRENT_Y(2'd1),
        .DATA_WIDTH(DATA_WIDTH), .VC_DEPTH(VC_DEPTH), .ADDR_WIDTH(ADDR_WIDTH),
        .USE_CAPS_ARBITER(USE_CAPS_ARBITER)
    ) router_01 (
        .clk(clk), .rst_n(rst_n),

        // Local PE 2
        .wr_en_local(pe2_wr_en), .din_local(pe2_din),
        .credit_out_local_vc0(pe2_credit_out_vc0), .credit_out_local_vc1(pe2_credit_out_vc1),
        .full_local_vc0(pe2_full_vc0), .full_local_vc1(pe2_full_vc1),
        .dout_local(pe2_dout), .valid_local(pe2_valid),
        .credit_in_local_vc0(pe2_credit_in_vc0), .credit_in_local_vc1(pe2_credit_in_vc1),

        // North <---> R(0,0) South
        .wr_en_north(r00_to_r01_val), .din_north(r00_to_r01_data),
        .credit_out_north_vc0(r01_n_cred0), .credit_out_north_vc1(r01_n_cred1),
        .full_north_vc0(), .full_north_vc1(),
        .dout_north(r01_to_r00_data), .valid_north(r01_to_r00_val),
        .credit_in_north_vc0(r00_s_cred0), .credit_in_north_vc1(r00_s_cred1),

        // South (Boundary - tied off)
        .wr_en_south(1'b0), .din_south({DATA_WIDTH{1'b0}}),
        .credit_out_south_vc0(), .credit_out_south_vc1(), .full_south_vc0(), .full_south_vc1(),
        .dout_south(), .valid_south(), .credit_in_south_vc0(1'b0), .credit_in_south_vc1(1'b0),

        // East <---> R(1,1) West
        .wr_en_east(r11_to_r01_val), .din_east(r11_to_r01_data),
        .credit_out_east_vc0(r01_e_cred0), .credit_out_east_vc1(r01_e_cred1),
        .full_east_vc0(), .full_east_vc1(),
        .dout_east(r01_to_r11_data), .valid_east(r01_to_r11_val),
        .credit_in_east_vc0(r11_w_cred0), .credit_in_east_vc1(r11_w_cred1),

        // West (Boundary - tied off)
        .wr_en_west(1'b0), .din_west({DATA_WIDTH{1'b0}}),
        .credit_out_west_vc0(), .credit_out_west_vc1(), .full_west_vc0(), .full_west_vc1(),
        .dout_west(), .valid_west(), .credit_in_west_vc0(1'b0), .credit_in_west_vc1(1'b0)
    );

    // =========================================================================
    // Router (1,1)
    // =========================================================================
    noc_router_vc #(
        .CURRENT_X(2'd1), .CURRENT_Y(2'd1),
        .DATA_WIDTH(DATA_WIDTH), .VC_DEPTH(VC_DEPTH), .ADDR_WIDTH(ADDR_WIDTH),
        .USE_CAPS_ARBITER(USE_CAPS_ARBITER)
    ) router_11 (
        .clk(clk), .rst_n(rst_n),

        // Local PE 3
        .wr_en_local(pe3_wr_en), .din_local(pe3_din),
        .credit_out_local_vc0(pe3_credit_out_vc0), .credit_out_local_vc1(pe3_credit_out_vc1),
        .full_local_vc0(pe3_full_vc0), .full_local_vc1(pe3_full_vc1),
        .dout_local(pe3_dout), .valid_local(pe3_valid),
        .credit_in_local_vc0(pe3_credit_in_vc0), .credit_in_local_vc1(pe3_credit_in_vc1),

        // North <---> R(1,0) South
        .wr_en_north(r10_to_r11_val), .din_north(r10_to_r11_data),
        .credit_out_north_vc0(r11_n_cred0), .credit_out_north_vc1(r11_n_cred1),
        .full_north_vc0(), .full_north_vc1(),
        .dout_north(r11_to_r10_data), .valid_north(r11_to_r10_val),
        .credit_in_north_vc0(r10_s_cred0), .credit_in_north_vc1(r10_s_cred1),

        // South (Boundary - tied off)
        .wr_en_south(1'b0), .din_south({DATA_WIDTH{1'b0}}),
        .credit_out_south_vc0(), .credit_out_south_vc1(), .full_south_vc0(), .full_south_vc1(),
        .dout_south(), .valid_south(), .credit_in_south_vc0(1'b0), .credit_in_south_vc1(1'b0),

        // East (Boundary - tied off)
        .wr_en_east(1'b0), .din_east({DATA_WIDTH{1'b0}}),
        .credit_out_east_vc0(), .credit_out_east_vc1(), .full_east_vc0(), .full_east_vc1(),
        .dout_east(), .valid_east(), .credit_in_east_vc0(1'b0), .credit_in_east_vc1(1'b0),

        // West <---> R(0,1) East
        .wr_en_west(r01_to_r11_val), .din_west(r01_to_r11_data),
        .credit_out_west_vc0(r11_w_cred0), .credit_out_west_vc1(r11_w_cred1),
        .full_west_vc0(), .full_west_vc1(),
        .dout_west(r11_to_r01_data), .valid_west(r11_to_r01_val),
        .credit_in_west_vc0(r01_e_cred0), .credit_in_west_vc1(r01_e_cred1)
    );

endmodule
