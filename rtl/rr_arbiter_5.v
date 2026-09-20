// ==============================================================================
// Module: rr_arbiter_5.v
// Lead: Bhavani (Arbitration & Flow Control Lead)
// Project: 5-Port Network-on-Chip (NoC) Router
// Description: 5-Input Round-Robin Arbiter for an individual output port.
//              Resolves contention when multiple input ports simultaneously request
//              the same output channel.
//              Features:
//                1. Starvation-free: Rotates highest priority to (granted_index + 1).
//                2. Local fairness: Every input gets served within at most 4 cycles.
//                3. Backpressure-aware: Only grants if downstream has credit available.
// Reference: Vinoth Kumar & Senthil Kumar (2014), "Design and Implementation of
//            Router Arbitration in Network on Chip".
// ==============================================================================

`timescale 1ns / 1ps

module rr_arbiter_5 (
    input  wire       clk,
    input  wire       rst_n,

    // 5-bit Request vector from input ports (0:Local, 1:North, 2:South, 3:East, 4:West)
    input  wire [4:0] req,

    // Flow Control Condition: 1 if downstream router has buffer space
    input  wire       credit_ready,

    // 5-bit One-Hot Grant vector
    output reg  [4:0] grant
);

    // Current priority pointer (0 to 4) indicating which port has highest priority
    reg [2:0] priority_ptr;

    // Internal combinatorial grant selection
    reg [4:0] next_grant;
    integer i, idx;

    always @(*) begin
        next_grant = 5'b00000;
        if (credit_ready && (|req)) begin
            // Search circularly starting from priority_ptr
            for (i = 0; i < 5; i = i + 1) begin
                idx = (priority_ptr + i) % 5;
                if (req[idx] && (next_grant == 5'b00000)) begin
                    next_grant[idx] = 1'b1;
                end
            end
        end
    end

    // Sequential output update and priority pointer rotation
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            grant        <= 5'b00000;
            priority_ptr <= 3'd0;
        end else begin
            grant <= next_grant;
            if (|next_grant) begin
                // Update priority to next port cyclically
                if (next_grant[0]) priority_ptr <= 3'd1;
                else if (next_grant[1]) priority_ptr <= 3'd2;
                else if (next_grant[2]) priority_ptr <= 3'd3;
                else if (next_grant[3]) priority_ptr <= 3'd4;
                else if (next_grant[4]) priority_ptr <= 3'd0;
            end
        end
    end

endmodule
