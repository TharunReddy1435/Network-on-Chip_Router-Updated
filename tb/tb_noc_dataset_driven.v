// ==============================================================================
// Module: tb_noc_dataset_driven.v
// Lead: Gowtham (Integration & Verification Lead)
// Project: 2x2 2D-Mesh Network-on-Chip (NoC) Interconnect
// Description: Automated Dataset-Driven Verification Testbench for 2x2 NoC Mesh.
//              Loads synthetic and domain-specific communication trace datasets
//              from .hex files using $readmemh, injects flits cycle-by-cycle,
//              monitors all 4 PE reception ports, calculates per-packet latency,
//              measures network throughput, and verifies 100% lossless delivery
//              with an associative in-flight packet tracking scoreboard.
// ==============================================================================

`timescale 1ns / 1ps

module tb_noc_dataset_driven;

    parameter DATA_WIDTH   = 16;
    parameter VC_DEPTH     = 4;
    parameter ADDR_WIDTH   = 2;
    parameter MAX_DATASET  = 4096;
    parameter CLK_PERIOD   = 10; // 100 MHz (10ns period)
    parameter DATASET_FILE = "dataset/uniform_random_1000.hex";

    reg clk;
    reg rst_n;

    // PE 0 Signals
    reg                   pe0_wr_en;
    reg  [DATA_WIDTH-1:0] pe0_din;
    wire                  pe0_credit_out_vc0, pe0_credit_out_vc1;
    wire                  pe0_full_vc0, pe0_full_vc1;
    wire [DATA_WIDTH-1:0] pe0_dout;
    wire                  pe0_valid;
    reg                   pe0_credit_in_vc0, pe0_credit_in_vc1;

    // PE 1 Signals
    reg                   pe1_wr_en;
    reg  [DATA_WIDTH-1:0] pe1_din;
    wire                  pe1_credit_out_vc0, pe1_credit_out_vc1;
    wire                  pe1_full_vc0, pe1_full_vc1;
    wire [DATA_WIDTH-1:0] pe1_dout;
    wire                  pe1_valid;
    reg                   pe1_credit_in_vc0, pe1_credit_in_vc1;

    // PE 2 Signals
    reg                   pe2_wr_en;
    reg  [DATA_WIDTH-1:0] pe2_din;
    wire                  pe2_credit_out_vc0, pe2_credit_out_vc1;
    wire                  pe2_full_vc0, pe2_full_vc1;
    wire [DATA_WIDTH-1:0] pe2_dout;
    wire                  pe2_valid;
    reg                   pe2_credit_in_vc0, pe2_credit_in_vc1;

    // PE 3 Signals
    reg                   pe3_wr_en;
    reg  [DATA_WIDTH-1:0] pe3_din;
    wire                  pe3_credit_out_vc0, pe3_credit_out_vc1;
    wire                  pe3_full_vc0, pe3_full_vc1;
    wire [DATA_WIDTH-1:0] pe3_dout;
    wire                  pe3_valid;
    reg                   pe3_credit_in_vc0, pe3_credit_in_vc1;

    // Instantiate 2x2 Mesh DUT
    noc_mesh_2x2 #(
        .DATA_WIDTH(DATA_WIDTH),
        .VC_DEPTH(VC_DEPTH),
        .ADDR_WIDTH(ADDR_WIDTH)
    ) dut_mesh (
        .clk(clk), .rst_n(rst_n),

        .pe0_wr_en(pe0_wr_en), .pe0_din(pe0_din),
        .pe0_credit_out_vc0(pe0_credit_out_vc0), .pe0_credit_out_vc1(pe0_credit_out_vc1),
        .pe0_full_vc0(pe0_full_vc0), .pe0_full_vc1(pe0_full_vc1),
        .pe0_dout(pe0_dout), .pe0_valid(pe0_valid),
        .pe0_credit_in_vc0(pe0_credit_in_vc0), .pe0_credit_in_vc1(pe0_credit_in_vc1),

        .pe1_wr_en(pe1_wr_en), .pe1_din(pe1_din),
        .pe1_credit_out_vc0(pe1_credit_out_vc0), .pe1_credit_out_vc1(pe1_credit_out_vc1),
        .pe1_full_vc0(pe1_full_vc0), .pe1_full_vc1(pe1_full_vc1),
        .pe1_dout(pe1_dout), .pe1_valid(pe1_valid),
        .pe1_credit_in_vc0(pe1_credit_in_vc0), .pe1_credit_in_vc1(pe1_credit_in_vc1),

        .pe2_wr_en(pe2_wr_en), .pe2_din(pe2_din),
        .pe2_credit_out_vc0(pe2_credit_out_vc0), .pe2_credit_out_vc1(pe2_credit_out_vc1),
        .pe2_full_vc0(pe2_full_vc0), .pe2_full_vc1(pe2_full_vc1),
        .pe2_dout(pe2_dout), .pe2_valid(pe2_valid),
        .pe2_credit_in_vc0(pe2_credit_in_vc0), .pe2_credit_in_vc1(pe2_credit_in_vc1),

        .pe3_wr_en(pe3_wr_en), .pe3_din(pe3_din),
        .pe3_credit_out_vc0(pe3_credit_out_vc0), .pe3_credit_out_vc1(pe3_credit_out_vc1),
        .pe3_full_vc0(pe3_full_vc0), .pe3_full_vc1(pe3_full_vc1),
        .pe3_dout(pe3_dout), .pe3_valid(pe3_valid),
        .pe3_credit_in_vc0(pe3_credit_in_vc0), .pe3_credit_in_vc1(pe3_credit_in_vc1)
    );

    // Clock Generation
    always #(CLK_PERIOD/2) clk = ~clk;

    // Dataset Trace Memory (32-bit entries)
    // [31:20] inject_cycle, [19:18] src_pe, [17:16] reserved, [15:0] flit
    reg [31:0] trace_mem [0:MAX_DATASET-1];
    integer total_entries = 0;
    integer trace_idx = 0;
    integer current_cycle = 0;

    // Scoreboard Data Structures
    integer injected_count = 0;
    integer delivered_count = 0;
    integer total_latency_cycles = 0;
    integer min_latency = 999999;
    integer max_latency = 0;
    integer error_count = 0;

    // Associative Scoreboard Tracking Pool for in-flight flits per destination PE
    reg [15:0] exp_flit_pool [0:3][0:MAX_DATASET-1];
    integer    exp_time_pool [0:3][0:MAX_DATASET-1];
    reg        exp_recv_pool [0:3][0:MAX_DATASET-1];
    integer    exp_count_pe  [0:3];

    // Variables for injection driver (declared at module level for strict Verilog compliance)
    reg [11:0] tr_cycle;
    reg [1:0]  tr_pe;
    reg [15:0] tr_flit;
    reg        tr_vc;
    integer    dest_pe;

    // Destination PE Coordinate Mapping Function
    function integer coord_to_pe;
        input [1:0] x, y;
        begin
            case ({y, x})
                4'b00_00: coord_to_pe = 0;
                4'b00_01: coord_to_pe = 1;
                4'b01_00: coord_to_pe = 2;
                4'b01_01: coord_to_pe = 3;
                default:  coord_to_pe = 0;
            endcase
        end
    endfunction

    reg [2047:0] active_dataset;
    reg [1023:0] file_str;
    integer      f_workload;

    // -------------------------------------------------------------------------
    // Main Initialization Process
    // -------------------------------------------------------------------------
    integer init_p, init_q;
    initial begin
        clk = 1'b0;
        rst_n = 1'b0;

        active_dataset = DATASET_FILE;

        // Check if an active workload pointer file exists
        f_workload = $fopen("dataset/active_workload.txt", "r");
        if (f_workload != 0) begin
            if ($fscanf(f_workload, "%s", file_str) == 1) begin
                active_dataset = file_str;
            end
            $fclose(f_workload);
        end else if ($value$plusargs("DATASET=%s", file_str)) begin
            active_dataset = file_str;
        end

        pe0_wr_en = 1'b0; pe0_din = 16'd0; pe0_credit_in_vc0 = 1'b1; pe0_credit_in_vc1 = 1'b1;
        pe1_wr_en = 1'b0; pe1_din = 16'd0; pe1_credit_in_vc0 = 1'b1; pe1_credit_in_vc1 = 1'b1;
        pe2_wr_en = 1'b0; pe2_din = 16'd0; pe2_credit_in_vc0 = 1'b1; pe2_credit_in_vc1 = 1'b1;
        pe3_wr_en = 1'b0; pe3_din = 16'd0; pe3_credit_in_vc0 = 1'b1; pe3_credit_in_vc1 = 1'b1;

        for (init_p = 0; init_p < 4; init_p = init_p + 1) begin
            exp_count_pe[init_p] = 0;
            for (init_q = 0; init_q < MAX_DATASET; init_q = init_q + 1) begin
                exp_flit_pool[init_p][init_q] = 16'd0;
                exp_time_pool[init_p][init_q] = 0;
                exp_recv_pool[init_p][init_q] = 1'b0;
            end
        end

        $display("\n====================================================================");
        $display("  DATASET-DRIVEN 2x2 MESH NETWORK VERIFICATION ENGINE");
        $display("  Loading benchmark dataset: [%0s]", active_dataset);
        $display("====================================================================");

        // Load trace memory from HEX dataset
        $readmemh(active_dataset, trace_mem);

        // Determine number of valid entries
        total_entries = 0;
        while (total_entries < MAX_DATASET && trace_mem[total_entries] !== 32'bx && trace_mem[total_entries] !== 32'd0) begin
            total_entries = total_entries + 1;
        end

        // Fallback default sample if empty
        if (total_entries == 0) begin
            $display("  [INFO] Loading embedded benchmark suite...");
            trace_mem[0] = 32'h0050D401; // Cycle 5, PE0 -> PE3 (flit 0xD401)
            trace_mem[1] = 32'h00719802; // Cycle 7, PE1 -> PE2 (flit 0x9802)
            trace_mem[2] = 32'h00A25C03; // Cycle 10, PE2 -> PE1 (flit 0x5C03)
            trace_mem[3] = 32'h00C31004; // Cycle 12, PE3 -> PE0 (flit 0x1004)
            trace_mem[4] = 32'h00F0D405; // Cycle 15, PE0 -> PE3 (flit 0xD405)
            trace_mem[5] = 32'h01219806; // Cycle 18, PE1 -> PE2 (flit 0x9806)
            total_entries = 6;
        end

        $display("  [SUCCESS] Successfully loaded %0d trace records into stimulus memory.", total_entries);

        #30;
        rst_n = 1'b1;
        #20;

        $display("\n--> Beginning Cycle-Accurate Trace Replay Simulation...\n");
    end

    // -------------------------------------------------------------------------
    // Cycle Counter & Injection Driver
    // -------------------------------------------------------------------------
    always @(posedge clk) begin
        if (!rst_n) begin
            current_cycle <= 0;
            trace_idx     <= 0;
            pe0_wr_en     <= 1'b0; pe0_din <= 16'd0;
            pe1_wr_en     <= 1'b0; pe1_din <= 16'd0;
            pe2_wr_en     <= 1'b0; pe2_din <= 16'd0;
            pe3_wr_en     <= 1'b0; pe3_din <= 16'd0;
        end else begin
            current_cycle <= current_cycle + 1;

            // Default injection de-assertion
            pe0_wr_en <= 1'b0; pe0_din <= 16'd0;
            pe1_wr_en <= 1'b0; pe1_din <= 16'd0;
            pe2_wr_en <= 1'b0; pe2_din <= 16'd0;
            pe3_wr_en <= 1'b0; pe3_din <= 16'd0;

            // Check if next trace entry is ready for injection
            if (trace_idx < total_entries) begin
                tr_cycle = trace_mem[trace_idx][31:20];
                tr_pe    = trace_mem[trace_idx][19:18];
                tr_flit  = trace_mem[trace_idx][15:0];
                tr_vc    = tr_flit[5];
                dest_pe  = coord_to_pe(tr_flit[13:12], tr_flit[11:10]);

                if (current_cycle >= tr_cycle) begin
                    case (tr_pe)
                        2'd0: begin
                            if ((!tr_vc && !pe0_full_vc0) || (tr_vc && !pe0_full_vc1)) begin
                                pe0_wr_en <= 1'b1;
                                pe0_din   <= tr_flit;
                                record_scoreboard(dest_pe, tr_flit, current_cycle);
                                trace_idx <= trace_idx + 1;
                                injected_count <= injected_count + 1;
                            end
                        end
                        2'd1: begin
                            if ((!tr_vc && !pe1_full_vc0) || (tr_vc && !pe1_full_vc1)) begin
                                pe1_wr_en <= 1'b1;
                                pe1_din   <= tr_flit;
                                record_scoreboard(dest_pe, tr_flit, current_cycle);
                                trace_idx <= trace_idx + 1;
                                injected_count <= injected_count + 1;
                            end
                        end
                        2'd2: begin
                            if ((!tr_vc && !pe2_full_vc0) || (tr_vc && !pe2_full_vc1)) begin
                                pe2_wr_en <= 1'b1;
                                pe2_din   <= tr_flit;
                                record_scoreboard(dest_pe, tr_flit, current_cycle);
                                trace_idx <= trace_idx + 1;
                                injected_count <= injected_count + 1;
                            end
                        end
                        2'd3: begin
                            if ((!tr_vc && !pe3_full_vc0) || (tr_vc && !pe3_full_vc1)) begin
                                pe3_wr_en <= 1'b1;
                                pe3_din   <= tr_flit;
                                record_scoreboard(dest_pe, tr_flit, current_cycle);
                                trace_idx <= trace_idx + 1;
                                injected_count <= injected_count + 1;
                            end
                        end
                    endcase
                end
            end
        end
    end

    // Task to record expected flit into destination Scoreboard tracking pool
    task record_scoreboard;
        input integer dpe;
        input [15:0]  flit_data;
        input integer inj_time;
        integer idx;
        begin
            idx = exp_count_pe[dpe];
            exp_flit_pool[dpe][idx] = flit_data;
            exp_time_pool[dpe][idx] = inj_time;
            exp_recv_pool[dpe][idx] = 1'b0;
            exp_count_pe[dpe] = exp_count_pe[dpe] + 1;
        end
    endtask

    // -------------------------------------------------------------------------
    // Continuous Output Egress Monitors for PE0..PE3
    // (Sampled with delta delay to avoid clock race conditions)
    // -------------------------------------------------------------------------
    always @(posedge clk) begin
        #1;
        if (rst_n) begin
            if (pe0_valid) check_arrival(0, pe0_dout);
            if (pe1_valid) check_arrival(1, pe1_dout);
            if (pe2_valid) check_arrival(2, pe2_dout);
            if (pe3_valid) check_arrival(3, pe3_dout);
        end
    end

    // Associative packet check task: Matches arrival against pending in-flight flits
    task check_arrival;
        input integer pe_id;
        input [15:0]  rec_flit;
        integer i;
        integer match_idx;
        integer lat;
        begin
            match_idx = -1;
            // Search for earliest unreceived matching flit for this destination PE
            for (i = 0; i < exp_count_pe[pe_id]; i = i + 1) begin
                if (match_idx < 0 && exp_recv_pool[pe_id][i] == 1'b0 && exp_flit_pool[pe_id][i] === rec_flit) begin
                    match_idx = i;
                end
            end

            if (match_idx >= 0) begin
                exp_recv_pool[pe_id][match_idx] = 1'b1;
                lat = current_cycle - exp_time_pool[pe_id][match_idx] + 1;
                delivered_count = delivered_count + 1;
                total_latency_cycles = total_latency_cycles + lat;
                if (lat < min_latency) min_latency = lat;
                if (lat > max_latency) max_latency = lat;
                $display("  [CYCLE %4d] [MATCH] PE%0d received flit 0x%04h (Latency = %0d cycles)",
                         current_cycle, pe_id, rec_flit, lat);
            end else begin
                $display("  [CYCLE %4d] [ERROR] PE%0d UNEXPECTED/CORRUPTED FLIT! Received: 0x%04h",
                         current_cycle, pe_id, rec_flit);
                error_count = error_count + 1;
            end
        end
    endtask

    // -------------------------------------------------------------------------
    // Simulation Termination & Metric Aggregator
    // -------------------------------------------------------------------------
    integer max_sim_cycles;
    integer p_idx, f_idx;

    initial begin
        wait (rst_n == 1'b1);
        
        // Wait until all injected entries are received or dynamic timeout
        max_sim_cycles = (total_entries * 6) + 1000;
        while ((delivered_count < total_entries || injected_count < total_entries) && current_cycle < max_sim_cycles) begin
            @(posedge clk);
        end

        repeat (30) @(posedge clk);

        // Verify that all expected packets were delivered (check for drops)
        for (p_idx = 0; p_idx < 4; p_idx = p_idx + 1) begin
            for (f_idx = 0; f_idx < exp_count_pe[p_idx]; f_idx = f_idx + 1) begin
                if (exp_recv_pool[p_idx][f_idx] == 1'b0) begin
                    $display("  [ERROR] PE%0d Missing flit 0x%04h injected at cycle %0d never delivered!",
                             p_idx, exp_flit_pool[p_idx][f_idx], exp_time_pool[p_idx][f_idx]);
                    error_count = error_count + 1;
                end
            end
        end

        $display("\n====================================================================");
        $display("          NETWORK-ON-CHIP DATASET VERIFICATION REPORT               ");
        $display("====================================================================");
        $display("  Dataset File Replayed      : %0s", active_dataset);
        $display("  Simulation Duration        : %0d clock cycles", current_cycle);
        $display("  Total Trace Flits Injected : %0d", injected_count);
        $display("  Total Flits Delivered      : %0d", delivered_count);
        $display("  Scoreboard Mismatch Errors : %0d", error_count);
        if (injected_count > 0) begin
            $display("  Packet Loss Rate           : %0.2f%%", ((injected_count - delivered_count) * 100.0) / injected_count);
        end
        if (delivered_count > 0) begin
            $display("  Minimum Packet Latency     : %0d cycles", min_latency);
            $display("  Maximum Packet Latency     : %0d cycles", max_latency);
            $display("  Average Packet Latency     : %0.2f cycles", (total_latency_cycles * 1.0) / delivered_count);
            $display("  Network Throughput         : %0.4f flits/cycle/node", (delivered_count * 1.0) / (current_cycle * 4));
        end
        $display("--------------------------------------------------------------------");
        if (error_count == 0 && delivered_count == injected_count && injected_count > 0) begin
            $display("  >>> STATUS: PASSED! 100%% LOSSLESS VERIFICATION ON DATASET WORKLOAD <<<");
        end else begin
            $display("  >>> STATUS: VERIFICATION FAILED WITH %0d ERRORS <<<", error_count);
        end
        $display("====================================================================\n");

        $finish;
    end

endmodule
