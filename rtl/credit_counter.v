// ==============================================================================
// Module: credit_counter.v
// Lead: Bhavani (Arbitration & Flow Control Lead)
// Project: 5-Port Network-on-Chip (NoC) Router
// Description: Credit-based flow control tracker for an output channel.
//              Maintains a running tally of free buffer slots available in the
//              downstream router's input FIFO. Prevents buffer overflow and packet
//              dropping under heavy traffic congestion.
// ==============================================================================

`timescale 1ns / 1ps

module credit_counter #(
    parameter MAX_CREDITS   = 8,
    parameter COUNTER_WIDTH = 4  // Must hold 0..MAX_CREDITS
)(
    input  wire                     clk,
    input  wire                     rst_n,

    // Decrement trigger: flit successfully dispatched through this output
    input  wire                     tx_fire,

    // Increment trigger: credit return pulse from downstream router FIFO
    input  wire                     credit_in,

    // Credit status to Arbiter
    output wire                     has_credit,
    output wire [COUNTER_WIDTH-1:0] credit_count
);

    reg [COUNTER_WIDTH-1:0] credits;

    assign has_credit   = (credits > 0);
    assign credit_count = credits;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            credits <= MAX_CREDITS[COUNTER_WIDTH-1:0];
        end else begin
            case ({tx_fire, credit_in})
                2'b10: begin
                    if (credits > 0)
                        credits <= credits - 1'b1;
                end
                2'b01: begin
                    if (credits < MAX_CREDITS[COUNTER_WIDTH-1:0])
                        credits <= credits + 1'b1;
                end
                2'b11: begin
                    // Net change zero
                    credits <= credits;
                end
                default: begin
                    credits <= credits;
                end
            endcase
        end
    end

endmodule
