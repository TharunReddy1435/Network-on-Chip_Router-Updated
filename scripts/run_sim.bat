@echo off
REM ==============================================================================
REM Batch script to compile and run simulation using Vivado Simulator
REM ==============================================================================

echo [1/3] Compiling Verilog RTL and Testbench...
call "D:\xilinx\Vivado\2023.1\bin\xvlog.bat" -work work rtl/noc_fifo.v rtl/xy_routing.v rtl/crossbar_5x5.v rtl/rr_arbiter_5.v rtl/credit_counter.v rtl/noc_router_top.v tb/tb_noc_router_top.v
if %ERRORLEVEL% NEQ 0 (
    echo Compilation failed!
    exit /b %ERRORLEVEL%
)

echo [2/3] Elaborating simulation snapshot...
call "D:\xilinx\Vivado\2023.1\bin\xelab.bat" -top tb_noc_router_top -snapshot noc_router_sim -debug typical
if %ERRORLEVEL% NEQ 0 (
    echo Elaboration failed!
    exit /b %ERRORLEVEL%
)

echo [3/3] Running simulation...
call "D:\xilinx\Vivado\2023.1\bin\xsim.bat" noc_router_sim -R

echo Simulation Complete!
pause
