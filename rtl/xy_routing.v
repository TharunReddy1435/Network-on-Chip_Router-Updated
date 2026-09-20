// ==============================================================================
// Module: xy_routing.v
// Lead: Tharun (Routing & Switching Lead)
// Project: 5-Port Network-on-Chip (NoC) Router
// Description: Deterministic Dimension-Order XY Routing Unit for 2D Mesh topology.
//              Packets are routed along the X-dimension first until X_dest == X_curr,
//              then routed along the Y-dimension until Y_dest == Y_curr, and then
//              directed to the Local Processing Element (PE).
//              This guarantees deadlock-free and livelock-free packet delivery.
//
// Coordinate Convention:
//   - X-axis: 0 (West) to Max (East)    -> dx > cx => EAST,  dx < cx => WEST
//   - Y-axis: 0 (North) to Max (South)  -> dy > cy => SOUTH, dy < cy => NORTH
//   - Matching: dx == cx && dy == cy    => LOCAL
//
// Port One-Hot Encoding:
//   Bit [0] = LOCAL (Port 0)
//   Bit [1] = NORTH (Port 1)
//   Bit [2] = SOUTH (Port 2)
//   Bit [3] = EAST  (Port 3)
//   Bit [4] = WEST  (Port 4)
// ==============================================================================

`timescale 1ns / 1ps

module xy_routing #(
    parameter [1:0] CURRENT_X = 2'd1,
    parameter [1:0] CURRENT_Y = 2'd1
)(
    input  wire       valid_in,     // High if flit/header is present
    input  wire [1:0] dest_x,       // Destination X coordinate
    input  wire [1:0] dest_y,       // Destination Y coordinate
    output reg  [4:0] req_port,     // One-hot request vector to output port arbiters
    output reg  [2:0] port_id       // Binary port ID (0:Local, 1:N, 2:S, 3:E, 4:W)
);

    localparam PORT_LOCAL = 3'd0;
    localparam PORT_NORTH = 3'd1;
    localparam PORT_SOUTH = 3'd2;
    localparam PORT_EAST  = 3'd3;
    localparam PORT_WEST  = 3'd4;

    always @(*) begin
        if (!valid_in) begin
            req_port = 5'b00000;
            port_id  = 3'd7; // Invalid
        end else begin
            // Dimension Order XY: First check X-dimension
            if (dest_x > CURRENT_X) begin
                req_port = 5'b01000; // EAST (Bit 3)
                port_id  = PORT_EAST;
            end else if (dest_x < CURRENT_X) begin
                req_port = 5'b10000; // WEST (Bit 4)
                port_id  = PORT_WEST;
            end
            // X-dimension matched; now check Y-dimension
            else if (dest_y > CURRENT_Y) begin
                req_port = 5'b00100; // SOUTH (Bit 2)
                port_id  = PORT_SOUTH;
            end else if (dest_y < CURRENT_Y) begin
                req_port = 5'b00010; // NORTH (Bit 1)
                port_id  = PORT_NORTH;
            end
            // Both X and Y matched; destination is this router's PE
            else begin
                req_port = 5'b00001; // LOCAL (Bit 0)
                port_id  = PORT_LOCAL;
            end
        end
    end

endmodule
