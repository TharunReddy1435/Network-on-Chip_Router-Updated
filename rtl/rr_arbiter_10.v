// ==============================================================================
// Module: rr_arbiter_10.v
// Lead: Bhavani (Arbitration & Flow Control Lead)
// Project: 5-Port Virtual-Channel Network-on-Chip (NoC) Router
// Description: 10-Input Starvation-Free Round-Robin Arbiter for Virtual Channel
//              Switch Allocation.
//              Features:
//                1. Independent per-VC credit qualification:
//                   - Even requesters (0, 2, 4, 6, 8) require credit_ready_vc0
//                   - Odd requesters (1, 3, 5, 7, 9) require credit_ready_vc1
//                2. Prevents HoL blocking across virtual channels
//                3. Cyclic priority rotation guaranteeing worst-case delay <= 9 cycles
// ==============================================================================

`timescale 1ns / 1ps

module rr_arbiter_10 (
    input  wire       clk,
    input  wire       rst_n,

    // 10-bit Request Vector:
    // [0]: Local VC0, [1]: Local VC1
    // [2]: North VC0, [3]: North VC1
    // [4]: South VC0, [5]: South VC1
    // [6]: East  VC0, [7]: East  VC1
    // [8]: West  VC0, [9]: West  VC1
    input  wire [9:0] req,

    // Independent credit availability flags from downstream receiver
    input  wire       credit_ready_vc0,
    input  wire       credit_ready_vc1,

    // 10-bit One-Hot Grant Vector
    output reg  [9:0] grant
);

    reg [3:0] priority_ptr; // Points to the requester with highest priority (0..9)
    reg [9:0] next_grant;
    integer i, idx;

    // Per-VC Request Qualification
    wire [9:0] eligible_req;
    assign eligible_req[0] = req[0] & credit_ready_vc0;
    assign eligible_req[1] = req[1] & credit_ready_vc1;
    assign eligible_req[2] = req[2] & credit_ready_vc0;
    assign eligible_req[3] = req[3] & credit_ready_vc1;
    assign eligible_req[4] = req[4] & credit_ready_vc0;
    assign eligible_req[5] = req[5] & credit_ready_vc1;
    assign eligible_req[6] = req[6] & credit_ready_vc0;
    assign eligible_req[7] = req[7] & credit_ready_vc1;
    assign eligible_req[8] = req[8] & credit_ready_vc0;
    assign eligible_req[9] = req[9] & credit_ready_vc1;

    always @(*) begin
        next_grant = 10'd0;
        if (|eligible_req) begin
            for (i = 0; i < 10; i = i + 1) begin
                idx = (priority_ptr + i) % 10;
                if (eligible_req[idx] && (next_grant == 10'd0)) begin
                    next_grant[idx] = 1'b1;
                end
            end
        end
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            grant        <= 10'd0;
            priority_ptr <= 4'd0;
        end else begin
            grant <= next_grant;
            if (|next_grant) begin
                // Update priority pointer cyclically to (granted_index + 1) % 10
                for (i = 0; i < 10; i = i + 1) begin
                    if (next_grant[i]) begin
                        priority_ptr <= (i == 9) ? 4'd0 : (i + 1'b1);
                    end
                end
            end
        end
    end

endmodule
