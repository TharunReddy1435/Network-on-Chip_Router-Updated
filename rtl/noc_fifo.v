// ==============================================================================
// Module: noc_fifo.v
// Lead: Shrestitha (Buffering & Storage Lead)
// Project: 5-Port Network-on-Chip (NoC) Router
// Description: Synchronous FIFO buffer for storing incoming flits at router input
//              ports. Supports First-Word Fall-Through (FWFT) so the Route Compute
//              unit can immediately inspect the header flit without latency.
//              Generates credit return pulses for credit-based flow control.
// ==============================================================================

`timescale 1ns / 1ps

module noc_fifo #(
    parameter DATA_WIDTH = 16,
    parameter DEPTH      = 8,
    parameter ADDR_WIDTH = 3   // 2^ADDR_WIDTH = DEPTH
)(
    input  wire                  clk,
    input  wire                  rst_n,

    // Write Interface (from incoming physical channel)
    input  wire                  wr_en,
    input  wire [DATA_WIDTH-1:0] din,
    output wire                  full,
    output wire                  almost_full,

    // Read Interface (to Crossbar Switch / Route Compute)
    input  wire                  rd_en,
    output wire [DATA_WIDTH-1:0] dout,
    output wire                  empty,

    // Flow Control Credit Pulse (to upstream transmitter)
    output reg                   credit_out,

    // Diagnostics / Occupancy Status
    output wire [ADDR_WIDTH:0]   occupancy
);

    // Internal Memory Array
    reg [DATA_WIDTH-1:0] mem [DEPTH-1:0];

    // Pointers & Counter
    reg [ADDR_WIDTH-1:0] wr_ptr;
    reg [ADDR_WIDTH-1:0] rd_ptr;
    reg [ADDR_WIDTH:0]   count;

    // Status Flags
    assign full        = (count == DEPTH);
    assign empty       = (count == 0);
    assign almost_full = (count >= DEPTH - 1);
    assign occupancy   = count;

    // First-Word Fall-Through (FWFT): dout reflects the front of queue combinational
    assign dout = mem[rd_ptr];

    // Synchronous Read & Write Logic
    integer i;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr     <= {ADDR_WIDTH{1'b0}};
            rd_ptr     <= {ADDR_WIDTH{1'b0}};
            count      <= {(ADDR_WIDTH+1){1'b0}};
            credit_out <= 1'b0;
            for (i = 0; i < DEPTH; i = i + 1) begin
                mem[i] <= {DATA_WIDTH{1'b0}};
            end
        end else begin
            // Default credit output pulse
            credit_out <= 1'b0;

            // Simultaneous Read and Write
            if (wr_en && !full && rd_en && !empty) begin
                mem[wr_ptr] <= din;
                wr_ptr      <= (wr_ptr == DEPTH - 1) ? {ADDR_WIDTH{1'b0}} : wr_ptr + 1'b1;
                rd_ptr      <= (rd_ptr == DEPTH - 1) ? {ADDR_WIDTH{1'b0}} : rd_ptr + 1'b1;
                credit_out  <= 1'b1; // Freeing one slot
            end
            // Write Only
            else if (wr_en && !full) begin
                mem[wr_ptr] <= din;
                wr_ptr      <= (wr_ptr == DEPTH - 1) ? {ADDR_WIDTH{1'b0}} : wr_ptr + 1'b1;
                count       <= count + 1'b1;
            end
            // Read Only
            else if (rd_en && !empty) begin
                rd_ptr      <= (rd_ptr == DEPTH - 1) ? {ADDR_WIDTH{1'b0}} : rd_ptr + 1'b1;
                count       <= count - 1'b1;
                credit_out  <= 1'b1; // Slot freed, signal credit to upstream router
            end
        end
    end

endmodule
