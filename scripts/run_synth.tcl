# ==============================================================================
# Script: run_synth.tcl
# Lead: Gowtham (Integration & Verification Lead)
# Project: 5-Port Network-on-Chip (NoC) Router
# Description: Automated Vivado batch synthesis script targeting Kintex-7 FPGA
#              (28nm, matching Reference Paper 1: Ved et al., IEEE SPIN 2017).
#              Applies clock constraint (200 MHz) to extract setup slack and Fmax.
# ==============================================================================

create_project -in_memory -part xc7k70tfbv676-1

# Read all RTL source files
read_verilog rtl/noc_fifo.v
read_verilog rtl/xy_routing.v
read_verilog rtl/crossbar_5x5.v
read_verilog rtl/rr_arbiter_5.v
read_verilog rtl/credit_counter.v
read_verilog rtl/noc_router_top.v

# Run synthesis targeting 5-Port NoC Router Top Module
synth_design -top noc_router_top -part xc7k70tfbv676-1

# Create 200 MHz target clock (5.0 ns period)
create_clock -period 5.000 -name clk [get_ports clk]

# Generate detailed reports
report_utilization -file synth_utilization.rpt
report_timing_summary -file synth_timing.rpt
report_power -file synth_power.rpt

puts "\n===================================================================="
puts ">>> SYNTHESIS COMPLETED WITH TIMING CONSTRAINTS. <<<"
puts "====================================================================\n"

exit
