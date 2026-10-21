@echo off
REM ==============================================================================
REM Batch script to compile and run simulation using Vivado Simulator (xsim)
REM
REM Usage:
REM   run_sim.bat dataset    --> Runs Uniform Random Dataset Verification (1,000 flits)
REM   run_sim.bat hotspot    --> Runs Hotspot Memory Controller Dataset Verification (1,000 flits)
REM   run_sim.bat transpose  --> Runs Matrix Transpose Dataset Verification (1,000 flits)
REM   run_sim.bat bitcomp    --> Runs Bit-Complement Bisection Stress Dataset Verification (1,000 flits)
REM   run_sim.bat cnn        --> Runs Pipelined CNN ResNet Workload Verification (1,000 flits)
REM   run_sim.bat mesh       --> Runs 2x2 Mesh System-Level Multi-Hop TB (9 Directed Scenarios)
REM   run_sim.bat sb         --> Runs Constrained-Random Scoreboard TB (Single Router)
REM   run_sim.bat baseline   --> Runs Baseline 7-Scenario Directed TB
REM ==============================================================================

set TARGET=%1
if "%TARGET%"=="" set TARGET=dataset

echo ====================================================================
echo   NETWORK-ON-CHIP (NoC) SIMULATION LAUNCHER: Target [%TARGET%]
echo ====================================================================

set DSET_FILE=dataset/uniform_random_1000.hex
if "%TARGET%"=="hotspot" (
    set DSET_FILE=dataset/hotspot_memory_1000.hex
) else if "%TARGET%"=="transpose" (
    set DSET_FILE=dataset/transpose_1000.hex
) else if "%TARGET%"=="bitcomp" (
    set DSET_FILE=dataset/bit_complement_1000.hex
) else if "%TARGET%"=="cnn" (
    set DSET_FILE=dataset/cnn_resnet_layer_traffic.hex
)

set RTL_FILES=rtl\credit_counter.v rtl\crossbar_10x5.v rtl\crossbar_5x5.v rtl\noc_fifo.v rtl\noc_mesh_2x2.v rtl\noc_router_top.v rtl\noc_router_vc.v rtl\noc_vc_input_port.v rtl\rr_arbiter_10.v rtl\rr_arbiter_5.v rtl\xy_routing.v

if "%TARGET%"=="dataset" goto run_dataset_flow
if "%TARGET%"=="hotspot" goto run_dataset_flow
if "%TARGET%"=="transpose" goto run_dataset_flow
if "%TARGET%"=="bitcomp" goto run_dataset_flow
if "%TARGET%"=="cnn" goto run_dataset_flow
if "%TARGET%"=="mesh" goto run_mesh_flow
if "%TARGET%"=="sb" goto run_sb_flow
goto run_baseline_flow

:run_dataset_flow
echo [1/3] Compiling RTL and Dataset-Driven Testbench...
call "D:\xilinx\Vivado\2023.1\bin\xvlog.bat" -work work %RTL_FILES% tb\tb_noc_dataset_driven.v
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

echo [2/3] Elaborating dataset simulation snapshot...
call "D:\xilinx\Vivado\2023.1\bin\xelab.bat" -top tb_noc_dataset_driven -snapshot dataset_sim -debug typical
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

echo [3/3] Running dataset replay simulation for [%DSET_FILE%]...
echo %DSET_FILE% > dataset\active_workload.txt
call "D:\xilinx\Vivado\2023.1\bin\xsim.bat" dataset_sim -R
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
goto end_script

:run_mesh_flow
echo [1/3] Compiling RTL and 2x2 Mesh Testbench...
call "D:\xilinx\Vivado\2023.1\bin\xvlog.bat" -work work %RTL_FILES% tb\tb_noc_mesh_2x2.v
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

echo [2/3] Elaborating mesh simulation snapshot...
call "D:\xilinx\Vivado\2023.1\bin\xelab.bat" -top tb_noc_mesh_2x2 -snapshot mesh_sim -debug typical
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

echo [3/3] Running simulation...
call "D:\xilinx\Vivado\2023.1\bin\xsim.bat" mesh_sim -R
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
goto end_script

:run_sb_flow
echo [1/3] Compiling RTL and Scoreboard Testbench...
call "D:\xilinx\Vivado\2023.1\bin\xvlog.bat" -work work %RTL_FILES% tb\tb_noc_random_scoreboard.v
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

echo [2/3] Elaborating scoreboard simulation snapshot...
call "D:\xilinx\Vivado\2023.1\bin\xelab.bat" -top tb_noc_random_scoreboard -snapshot noc_sb_sim -debug typical
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

echo [3/3] Running simulation...
call "D:\xilinx\Vivado\2023.1\bin\xsim.bat" noc_sb_sim -R
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
goto end_script

:run_baseline_flow
echo [1/3] Compiling Baseline Router...
call "D:\xilinx\Vivado\2023.1\bin\xvlog.bat" -work work %RTL_FILES% tb\tb_noc_router_top.v
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

echo [2/3] Elaborating baseline snapshot...
call "D:\xilinx\Vivado\2023.1\bin\xelab.bat" -top tb_noc_router_top -snapshot noc_router_sim -debug typical
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

echo [3/3] Running simulation...
call "D:\xilinx\Vivado\2023.1\bin\xsim.bat" noc_router_sim -R
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
goto end_script

:end_script
echo.
echo ====================================================================
echo   Simulation Completed Successfully!
echo ====================================================================
