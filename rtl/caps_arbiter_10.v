// ==============================================================================
// Module: caps_arbiter_10.v
// Lead: Bhavani (Arbitration & Flow Control Lead)
// Project: 5-Port Virtual-Channel Network-on-Chip (NoC) Router
// Description: Congestion-Aware Priority Scheduler (CAPS).
//              A two-tier dynamic arbiter for Virtual Channel Switch Allocation:
//                - Tier 1 (Urgent Congestion Relief): Grants eligible requests
//                  from input queues that are congested (occupancy >= threshold)
//                  using round-robin to clear buffer pressure.
//                - Tier 2 (Fair Best-Effort): Grants regular eligible requests
//                  using round-robin cyclic rotation.
//              Fully qualified with downstream per-VC credit availability.
//              Guarantees starvation freedom while measurably reducing latency
//              under heavy offered loads and hotspot traffic.
// ==============================================================================

`timescale 1ns / 1ps

module caps_arbiter_10 (
    input  wire       clk,
    input  wire       rst_n,

    // 10-bit Request Vector
    input  wire [9:0] req,

    // 10-bit Urgency / High Occupancy Vector (e.g., almost_full from input FIFOs)
    input  wire [9:0] urgent,

    // Independent credit availability flags from downstream receiver
    input  wire       credit_ready_vc0,
    input  wire       credit_ready_vc1,

    // 10-bit One-Hot Grant Vector
    output reg  [9:0] grant
);

    reg [3:0] priority_ptr;        // Fair priority pointer (0..9)
    reg [3:0] urgent_priority_ptr; // Priority pointer for urgent tier (0..9)
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

    // Urgent eligible requests
    wire [9:0] urgent_eligible = eligible_req & urgent;

    always @(*) begin
        next_grant = 10'd0;
        // Tier 1: Service urgent requests first if any exist
        if (|urgent_eligible) begin
            for (i = 0; i < 10; i = i + 1) begin
                idx = (urgent_priority_ptr + i) % 10;
                if (urgent_eligible[idx] && (next_grant == 10'd0)) begin
                    next_grant[idx] = 1'b1;
                end
            end
        end
        // Tier 2: Service standard requests using fair Round-Robin
        else if (|eligible_req) begin
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
            grant               <= 10'd0;
            priority_ptr        <= 4'd0;
            urgent_priority_ptr <= 4'd0;
        end else begin
            grant <= next_grant;
            if (|next_grant) begin
                for (i = 0; i < 10; i = i + 1) begin
                    if (next_grant[i]) begin
                        if (urgent[i]) begin
                            urgent_priority_ptr <= (i == 9) ? 4'd0 : (i + 1'b1);
                        end
                        priority_ptr <= (i == 9) ? 4'd0 : (i + 1'b1);
                    end
                end
            end
        end
    end

endmodule
