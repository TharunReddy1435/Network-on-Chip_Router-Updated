// ==============================================================================
// Module: crossbar_10x5.v
// Lead: Tharun (Routing & Switching Lead)
// Project: 5-Port Virtual-Channel Network-on-Chip (NoC) Router
// Description: 10x5 Crossbar Switch Matrix. Multiplexes data flits from 10 Virtual
//              Channel input queues to the 5 physical output channels.
//              Qualifies outgoing valid signals with non-empty input status to
//              strictly prevent spurious 0-data transmission.
// ==============================================================================

`timescale 1ns / 1ps

module crossbar_10x5 #(
    parameter DATA_WIDTH = 16
)(
    // 10 VC Data Inputs from the 5 Input Ports
    input  wire [DATA_WIDTH-1:0] din_local_vc0,
    input  wire [DATA_WIDTH-1:0] din_local_vc1,
    input  wire [DATA_WIDTH-1:0] din_north_vc0,
    input  wire [DATA_WIDTH-1:0] din_north_vc1,
    input  wire [DATA_WIDTH-1:0] din_south_vc0,
    input  wire [DATA_WIDTH-1:0] din_south_vc1,
    input  wire [DATA_WIDTH-1:0] din_east_vc0,
    input  wire [DATA_WIDTH-1:0] din_east_vc1,
    input  wire [DATA_WIDTH-1:0] din_west_vc0,
    input  wire [DATA_WIDTH-1:0] din_west_vc1,

    // Empty status of each of the 10 input queues
    input  wire [9:0]            empty_inputs,

    // 10-bit One-Hot Grant Vectors from the 5 Arbiters
    input  wire [9:0]            grant_local,
    input  wire [9:0]            grant_north,
    input  wire [9:0]            grant_south,
    input  wire [9:0]            grant_east,
    input  wire [9:0]            grant_west,

    // Data Outputs to 5 Physical Channels
    output reg  [DATA_WIDTH-1:0] dout_local,
    output reg  [DATA_WIDTH-1:0] dout_north,
    output reg  [DATA_WIDTH-1:0] dout_south,
    output reg  [DATA_WIDTH-1:0] dout_east,
    output reg  [DATA_WIDTH-1:0] dout_west,

    // Valid Flags for Outgoing Channels (Active only when granted input is not empty)
    output reg                   valid_local,
    output reg                   valid_north,
    output reg                   valid_south,
    output reg                   valid_east,
    output reg                   valid_west
);

    // MUX Function for 10 Inputs
    function [DATA_WIDTH-1:0] mux10;
        input [9:0]            grant;
        input [DATA_WIDTH-1:0] d0, d1, d2, d3, d4, d5, d6, d7, d8, d9;
        begin
            case (grant)
                10'b0000000001: mux10 = d0; // Local VC0
                10'b0000000010: mux10 = d1; // Local VC1
                10'b0000000100: mux10 = d2; // North VC0
                10'b0000001000: mux10 = d3; // North VC1
                10'b0000010000: mux10 = d4; // South VC0
                10'b0000100000: mux10 = d5; // South VC1
                10'b0001000000: mux10 = d6; // East  VC0
                10'b0010000000: mux10 = d7; // East  VC1
                10'b0100000000: mux10 = d8; // West  VC0
                10'b1000000000: mux10 = d9; // West  VC1
                default:        mux10 = {DATA_WIDTH{1'b0}};
            endcase
        end
    endfunction

    always @(*) begin
        valid_local = |(grant_local & ~empty_inputs);
        dout_local  = mux10(grant_local, din_local_vc0, din_local_vc1,
                            din_north_vc0, din_north_vc1, din_south_vc0, din_south_vc1,
                            din_east_vc0, din_east_vc1, din_west_vc0, din_west_vc1);

        valid_north = |(grant_north & ~empty_inputs);
        dout_north  = mux10(grant_north, din_local_vc0, din_local_vc1,
                            din_north_vc0, din_north_vc1, din_south_vc0, din_south_vc1,
                            din_east_vc0, din_east_vc1, din_west_vc0, din_west_vc1);

        valid_south = |(grant_south & ~empty_inputs);
        dout_south  = mux10(grant_south, din_local_vc0, din_local_vc1,
                            din_north_vc0, din_north_vc1, din_south_vc0, din_south_vc1,
                            din_east_vc0, din_east_vc1, din_west_vc0, din_west_vc1);

        valid_east  = |(grant_east & ~empty_inputs);
        dout_east   = mux10(grant_east, din_local_vc0, din_local_vc1,
                            din_north_vc0, din_north_vc1, din_south_vc0, din_south_vc1,
                            din_east_vc0, din_east_vc1, din_west_vc0, din_west_vc1);

        valid_west  = |(grant_west & ~empty_inputs);
        dout_west   = mux10(grant_west, din_local_vc0, din_local_vc1,
                            din_north_vc0, din_north_vc1, din_south_vc0, din_south_vc1,
                            din_east_vc0, din_east_vc1, din_west_vc0, din_west_vc1);
    end

endmodule
