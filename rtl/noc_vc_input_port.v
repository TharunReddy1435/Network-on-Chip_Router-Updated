// ==============================================================================
// Module: noc_vc_input_port.v
// Lead: Shrestitha (Buffering & Storage Lead)
// Project: 5-Port Virtual-Channel Network-on-Chip (NoC) Router
// Description: Dual Virtual-Channel (VC0, VC1) input buffer module.
//              Provides two independent First-Word Fall-Through (FWFT) FIFOs
//              per physical port. Completely resolves Head-of-Line (HoL) blocking.
//              Generates accurate request-readiness signals (req_ready) to prevent
//              spurious grants and dead cycles.
// ==============================================================================

`timescale 1ns / 1ps

module noc_vc_input_port #(
    parameter DATA_WIDTH = 16,
    parameter VC_DEPTH   = 4,
    parameter ADDR_WIDTH = 2
)(
    input  wire                  clk,
    input  wire                  rst_n,

    // Incoming Physical Channel
    input  wire                  wr_en,
    input  wire [DATA_WIDTH-1:0] din,
    output wire                  full_vc0,
    output wire                  full_vc1,
    output wire                  almost_full_vc0,
    output wire                  almost_full_vc1,
    output wire                  credit_out_vc0,
    output wire                  credit_out_vc1,

    // Outgoing Interface to Routing & Switch Allocation
    // VC0 Channel
    input  wire                  rd_en_vc0,
    output wire [DATA_WIDTH-1:0] dout_vc0,
    output wire                  empty_vc0,
    output wire                  req_ready_vc0,

    // VC1 Channel
    input  wire                  rd_en_vc1,
    output wire [DATA_WIDTH-1:0] dout_vc1,
    output wire                  empty_vc1,
    output wire                  req_ready_vc1
);

    // Extract VC ID from incoming flit (Bit [5] of flit)
    wire incoming_vc = din[5];

    wire wr_en_vc0 = wr_en && (incoming_vc == 1'b0);
    wire wr_en_vc1 = wr_en && (incoming_vc == 1'b1);

    wire [ADDR_WIDTH:0] count_vc0;
    wire [ADDR_WIDTH:0] count_vc1;

    // Instantiate VC0 FIFO
    noc_fifo #(
        .DATA_WIDTH(DATA_WIDTH),
        .DEPTH(VC_DEPTH),
        .ADDR_WIDTH(ADDR_WIDTH)
    ) fifo_vc0 (
        .clk(clk),
        .rst_n(rst_n),
        .wr_en(wr_en_vc0),
        .din(din),
        .full(full_vc0),
        .almost_full(almost_full_vc0),
        .rd_en(rd_en_vc0),
        .dout(dout_vc0),
        .empty(empty_vc0),
        .credit_out(credit_out_vc0),
        .occupancy(count_vc0)
    );

    // Instantiate VC1 FIFO
    noc_fifo #(
        .DATA_WIDTH(DATA_WIDTH),
        .DEPTH(VC_DEPTH),
        .ADDR_WIDTH(ADDR_WIDTH)
    ) fifo_vc1 (
        .clk(clk),
        .rst_n(rst_n),
        .wr_en(wr_en_vc1),
        .din(din),
        .full(full_vc1),
        .almost_full(almost_full_vc1),
        .rd_en(rd_en_vc1),
        .dout(dout_vc1),
        .empty(empty_vc1),
        .credit_out(credit_out_vc1),
        .occupancy(count_vc1)
    );

    // A VC is ready to request only when it has data and is not currently being read out,
    // ensuring the next flit settles on dout before route computation and arbitration
    assign req_ready_vc0 = !empty_vc0 && !rd_en_vc0;
    assign req_ready_vc1 = !empty_vc1 && !rd_en_vc1;

endmodule
