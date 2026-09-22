# ==============================================================================
# Script: run_synth_vc.tcl
# Lead: Gowtham (Integration & Verification Lead)
# Project: Upgraded Virtual-Channel Router & 2x2 Mesh NoC
# Description: Automated Vivado batch synthesis script targeting Kintex-7 FPGA
#              (xc7k70tfbv676-1). Synthesizes both noc_router_vc and noc_mesh_2x2.
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Synthesize 5-Port Virtual-Channel Router (noc_router_vc)
# ------------------------------------------------------------------------------
create_project -in_memory -part xc7k70tfbv676-1

read_verilog rtl/noc_fifo.v
read_verilog rtl/noc_vc_input_port.v
read_verilog rtl/xy_routing.v
read_verilog rtl/credit_counter.v
read_verilog rtl/rr_arbiter_10.v
read_verilog rtl/crossbar_10x5.v
read_verilog rtl/noc_router_vc.v

synth_design -top noc_router_vc -part xc7k70tfbv676-1
create_clock -period 5.000 -name clk [get_ports clk]

report_utilization -file synth_vc_router_utilization.rpt
report_timing_summary -file synth_vc_router_timing.rpt
report_power -file synth_power_vc_router.rpt

close_project

# ------------------------------------------------------------------------------
# 2. Synthesize 2x2 Mesh Interconnect (noc_mesh_2x2)
# ------------------------------------------------------------------------------
create_project -in_memory -part xc7k70tfbv676-1

read_verilog rtl/noc_fifo.v
read_verilog rtl/noc_vc_input_port.v
read_verilog rtl/xy_routing.v
read_verilog rtl/credit_counter.v
read_verilog rtl/rr_arbiter_10.v
read_verilog rtl/crossbar_10x5.v
read_verilog rtl/noc_router_vc.v
read_verilog rtl/noc_mesh_2x2.v

synth_design -top noc_mesh_2x2 -part xc7k70tfbv676-1
create_clock -period 6.000 -name clk [get_ports clk]

report_utilization -file synth_mesh_2x2_utilization.rpt
report_timing_summary -file synth_mesh_2x2_timing.rpt
report_power -file synth_power_mesh_2x2.rpt

puts "\n===================================================================="
puts ">>> UPGRADED DESIGN SYNTHESIS COMPLETED SUCCESSFULLY! <<<"
puts "====================================================================\n"

exit
