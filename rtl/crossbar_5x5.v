// ==============================================================================
// Module: crossbar_5x5.v
// Lead: Tharun (Routing & Switching Lead)
// Project: 5-Port Network-on-Chip (NoC) Router
// Description: 5x5 Crossbar Switch Matrix multiplexing data flits from 5 input
//              ports (Local, North, South, East, West) to 5 output ports.
//              Controlled by the grant vectors issued by Bhavani's Round-Robin
//              Arbiters. Prevents packet collision and enables up to 5 concurrent
//              transmissions between non-conflicting port pairs.
// ==============================================================================

`timescale 1ns / 1ps

module crossbar_5x5 #(
    parameter DATA_WIDTH = 16
)(
    // Data Inputs from 5 Input Port FIFOs
    input  wire [DATA_WIDTH-1:0] din_local,
    input  wire [DATA_WIDTH-1:0] din_north,
    input  wire [DATA_WIDTH-1:0] din_south,
    input  wire [DATA_WIDTH-1:0] din_east,
    input  wire [DATA_WIDTH-1:0] din_west,

    // One-Hot Grant Vectors from the 5 Arbiters
    // grant_X[0]=Local, [1]=North, [2]=South, [3]=East, [4]=West
    input  wire [4:0]            grant_local,
    input  wire [4:0]            grant_north,
    input  wire [4:0]            grant_south,
    input  wire [4:0]            grant_east,
    input  wire [4:0]            grant_west,

    // Data Outputs to the 5 Output Channels
    output reg  [DATA_WIDTH-1:0] dout_local,
    output reg  [DATA_WIDTH-1:0] dout_north,
    output reg  [DATA_WIDTH-1:0] dout_south,
    output reg  [DATA_WIDTH-1:0] dout_east,
    output reg  [DATA_WIDTH-1:0] dout_west,

    // Valid Flags for Outgoing Channels
    output reg                   valid_local,
    output reg                   valid_north,
    output reg                   valid_south,
    output reg                   valid_east,
    output reg                   valid_west
);

    // MUX for LOCAL Output Port
    always @(*) begin
        valid_local = |grant_local;
        case (grant_local)
            5'b00001: dout_local = din_local; // U-turn (rare, loopback)
            5'b00010: dout_local = din_north;
            5'b00100: dout_local = din_south;
            5'b01000: dout_local = din_east;
            5'b10000: dout_local = din_west;
            default:  dout_local = {DATA_WIDTH{1'b0}};
        endcase
    end

    // MUX for NORTH Output Port
    always @(*) begin
        valid_north = |grant_north;
        case (grant_north)
            5'b00001: dout_north = din_local;
            5'b00010: dout_north = din_north;
            5'b00100: dout_north = din_south;
            5'b01000: dout_north = din_east;
            5'b10000: dout_north = din_west;
            default:  dout_north = {DATA_WIDTH{1'b0}};
        endcase
    end

    // MUX for SOUTH Output Port
    always @(*) begin
        valid_south = |grant_south;
        case (grant_south)
            5'b00001: dout_south = din_local;
            5'b00010: dout_south = din_north;
            5'b00100: dout_south = din_south;
            5'b01000: dout_south = din_east;
            5'b10000: dout_south = din_west;
            default:  dout_south = {DATA_WIDTH{1'b0}};
        endcase
    end

    // MUX for EAST Output Port
    always @(*) begin
        valid_east = |grant_east;
        case (grant_east)
            5'b00001: dout_east = din_local;
            5'b00010: dout_east = din_north;
            5'b00100: dout_east = din_south;
            5'b01000: dout_east = din_east;
            5'b10000: dout_east = din_west;
            default:  dout_east = {DATA_WIDTH{1'b0}};
        endcase
    end

    // MUX for WEST Output Port
    always @(*) begin
        valid_west = |grant_west;
        case (grant_west)
            5'b00001: dout_west = din_local;
            5'b00010: dout_west = din_north;
            5'b00100: dout_west = din_south;
            5'b01000: dout_west = din_east;
            5'b10000: dout_west = din_west;
            default:  dout_west = {DATA_WIDTH{1'b0}};
        endcase
    end

endmodule
