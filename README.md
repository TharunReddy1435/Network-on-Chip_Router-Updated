# 5-Port Virtual-Channel Network-on-Chip (NoC) Router & 2x2 Mesh Interconnect in Verilog HDL

Design, functional verification, FPGA synthesis, and network traffic benchmarking of an advanced **5-Port Virtual-Channel NoC Router** and **2x2 2D-Mesh Interconnect** developed for the **Data Networks (DN)** course.

---

## 👥 Team & Responsibilities

| Team Member | Role | Key Contributions |
| :--- | :--- | :--- |
| **Shrestitha** | **Buffering & Storage Lead** | Dual Virtual-Channel input buffers (`noc_vc_input_port.v`), synchronous circular FIFO design (`noc_fifo.v`), First-Word Fall-Through (FWFT) logic, Head-of-Line (HoL) blocking elimination, and credit pulse generation. |
| **Tharun** | **Routing & Switching Lead** | Dimension-Order XY Routing units (`xy_routing.v`), deadlock/livelock prevention turn model, and 10x5 Crossbar Switch Matrix (`crossbar_10x5.v`) with non-empty output qualification. |
| **Bhavani** | **Arbitration & Flow Control Lead** | 10-input starvation-free Round-Robin Arbiter (`rr_arbiter_10.v`) with rotating cyclic priority, bounded latency guarantees, and Credit Counter flow control (`credit_counter.v`). |
| **Gowtham** | **Integration & Verification Lead** | 2x2 2D-Mesh Interconnect (`noc_mesh_2x2.v`), Constrained-Random Scoreboard testbench (`tb_noc_random_scoreboard.v`), system testbench (`tb_noc_mesh_2x2.v`), traffic benchmark suite, and Kintex-7 FPGA synthesis. |

---

## 🏛️ Architecture Overview

The system implements a scalable packet-switched 2D-Mesh Network-on-Chip (NoC) interconnect supporting multi-flit wormhole routing, dual virtual channels per physical port, and credit-based flow control.

### 1. 2x2 2D-Mesh Network Topology
```
         [PE0]                   [PE1]
           │                       │
      ┌────▼────┐   E <---> W   ┌────▼────┐
      │ R (0,0) ├───────────────┤ R (1,0) │
      └────┬────┘               └────┬────┘
           │ S                     │ S
           ▲                       ▲
           │ N                     │ N
      ┌────┴────┐   E <---> W   ┌────┴────┐
      │ R (0,1) ├───────────────┤ R (1,1) │
      └────▲────┘               └────▲────┘
           │                       │
         [PE2]                   [PE3]
```

### 2. Dual Virtual-Channel Router Pipeline
```
+-------------------------------------------------------------------------------------------------+
|                                 5-PORT VIRTUAL-CHANNEL NoC ROUTER                               |
|                                                                                                 |
|   [Input Ports]                 [Route Compute]           [Arbitration]        [Crossbar]       |
|    5x Physical Ports     -->     10x Dimension-Order  -->  5x 10-to-1     -->   10x5 Switch     |
|    (10x FWFT FIFOs,              XY Routing Logic          Round-Robin          Matrix          |
|     VC0 & VC1 per port)                                    Arbiters                             |
|                                                                                                 |
|                                 [Flow Control]                                                  |
|                            <--   5x Credit Counters (Lossless Backpressure)                     |
+-------------------------------------------------------------------------------------------------+
```

### 3. Key Technical Highlights:
1. **Dual Virtual Channels (VC0, VC1)**: Mitigates Head-of-Line (HoL) blocking by decoupling independent packet flows over shared physical links. Blocked packets waiting for busy egress ports do not impede packets targeting idle ports.
2. **First-Word Fall-Through (FWFT) FIFO**: Flit headers are immediately exposed at `dout` combinatorially, allowing Route Computation to proceed without a 1-cycle FIFO read latency bubble.
3. **Deterministic XY Routing**: Traverses the X-dimension until $X_{dest} == X_{curr}$, then traverses the Y-dimension until $Y_{dest} == Y_{curr}$, then delivers to Local PE. By strictly prohibiting all four $Y \to X$ turns, circular waiting chains cannot form, guaranteeing zero deadlock and livelock.
4. **Starvation-Free Round Robin Arbitration**: Rotates priority pointer $\text{priority\_ptr} \leftarrow (grant\_id + 1) \pmod{10}$, guaranteeing bounded latency (at most 9 cycles waiting time under full contention across all 10 VCs).
5. **Credit-Based Lossless Flow Control**: Maintains real-time tracking of downstream buffer slots, applying active backpressure when credits reach zero to guarantee 0% packet drop.

---

## 📁 Repository Structure

```
.
├── rtl/                                # Synthesizable Verilog HDL Source Files
│   ├── noc_fifo.v                      # Synchronous Circular FIFO with FWFT & Credit Pulse (Shrestitha)
│   ├── noc_vc_input_port.v             # Dual Virtual-Channel Input Port Unit (Shrestitha)
│   ├── xy_routing.v                    # Dimension-Order XY Routing Unit (Tharun)
│   ├── crossbar_5x5.v                  # Baseline 5x5 Crossbar Switch Matrix (Tharun)
│   ├── crossbar_10x5.v                 # Upgraded 10x5 Crossbar Matrix (Tharun)
│   ├── rr_arbiter_5.v                  # Baseline 5-Input Round-Robin Arbiter (Bhavani)
│   ├── rr_arbiter_10.v                 # Upgraded 10-Input Round-Robin Arbiter (Bhavani)
│   ├── credit_counter.v                # Credit-Based Flow Control Counter (Bhavani)
│   ├── noc_router_top.v                # Baseline 5-Port Router Top (Gowtham)
│   ├── noc_router_vc.v                 # Upgraded 5-Port Virtual-Channel Router (Gowtham)
│   └── noc_mesh_2x2.v                  # 2x2 2D-Mesh Interconnect (4 Routers, 4 PEs) (Gowtham)
│
├── tb/                                 # Verification Testbenches
│   ├── tb_noc_router_top.v             # Baseline 7-Scenario Directed Testbench
│   ├── tb_noc_random_scoreboard.v      # Constrained-Random Scoreboard & Assertion TB
│   └── tb_noc_mesh_2x2.v               # System-Level 2x2 Mesh Multi-Hop Testbench
│
├── scripts/                            # Automation & Benchmarking Scripts
│   ├── run_sim.bat                     # Windows batch simulation launcher
│   ├── run_synth.tcl                   # Baseline router synthesis script
│   ├── run_synth_vc.tcl                # Upgraded VC router & 2x2 mesh synthesis script
│   └── benchmark_traffic.py            # Python discrete-event traffic benchmark engine
│
├── docs/                               # Project Documentation & Viva Guides
│   ├── presentation_slides_content.md  # Complete 10-slide ready-to-present evaluation deck
│   ├── team_member_guide.md            # Comprehensive team guide, viva Q&A & live demo commands
│   └── traffic_benchmarks.md           # Traffic benchmark summary report
│
├── synth_vc_router_utilization.rpt     # Kintex-7 VC Router Utilization Report
├── synth_vc_router_timing.rpt          # Kintex-7 VC Router Timing & Fmax Report
├── synth_power_vc_router.rpt           # Kintex-7 VC Router Power Analysis Report
├── synth_mesh_2x2_utilization.rpt      # Kintex-7 2x2 Mesh Utilization Report
├── synth_mesh_2x2_timing.rpt           # Kintex-7 2x2 Mesh Timing & Fmax Report
├── synth_power_mesh_2x2.rpt            # Kintex-7 2x2 Mesh Power Analysis Report
└── README.md                           # Master Project Overview
```

---

## 🧪 Verification & Simulation Results

All testbenches compiled and verified cleanly with **AMD Xilinx Vivado 2023.1** (`xvlog`, `xelab`, `xsim`) with **zero errors and zero warnings**.

### 1. Constrained-Random Scoreboard Verification (`tb_noc_random_scoreboard.v`)
- **Total Packets Injected**: 52
- **Total Packets Matched by Golden Model**: 52 (100% Match Rate)
- **Scoreboard Errors**: 0
- **Safety Assertions**: 0 Violations (FIFO write-on-full, invalid grants, and spurious emissions verified)

### 2. System-Level 2x2 Mesh Multi-Hop Verification (`tb_noc_mesh_2x2.v`)
- **Test 1 (Multi-Hop Diagonal)**: PE0 (0,0) $\to$ R(0,0) $\to$ R(1,0) $\to$ R(1,1) $\to$ PE3 (1,1) in **5 clock cycles** (**PASS**)
- **Test 2 (Multi-Hop Counter-Diagonal)**: PE1 (1,0) $\to$ R(1,0) $\to$ R(0,0) $\to$ R(0,1) $\to$ PE2 (0,1) in **5 clock cycles** (**PASS**)
- **Test 3 (Multi-Flit Wormhole)**: Head $\to$ Body $\to$ Tail packet from PE2 to PE1 received sequentially (**PASS**)
- **Test 4 (Concurrent 4-Node Traffic)**: All 4 PEs inject packets simultaneously; all received in 5 cycles with zero deadlock (**PASS**)

---

## 📈 Network Traffic Performance Benchmarks

Evaluated using `scripts/benchmark_traffic.py` across 1,200 simulation cycles under realistic synthetic traffic patterns:

| Traffic Workload | Offered Load | Baseline Latency | Upgraded VC Latency | Baseline Throughput | Upgraded VC Throughput | Performance Gain |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Uniform Random** | 0.55 | 2.88 cyc | 2.82 cyc | 0.551 | 0.551 | **-2.1% Latency** |
| **Uniform Random** | 0.70 | 3.62 cyc | 3.18 cyc | 0.711 | 0.705 | **-12.2% Latency** |
| **Uniform Random** | 0.85 | 5.20 cyc | 5.02 cyc | 0.840 | 0.862 | **-3.5% Latency** |
| **Uniform Random** | 1.00 | 7.96 cyc | 9.58 cyc | 0.860 | 0.921 | **+7.1% Throughput** |
| **Hotspot (PE3 Memory)** | 0.40 | 2.89 cyc | 2.73 cyc | 0.395 | 0.392 | **-5.5% Latency** |
| **Hotspot (PE3 Memory)** | 0.70 | 7.65 cyc | 12.43 cyc | 0.577 | 0.599 | **+3.8% Throughput** |
| **Matrix Transpose** | 1.00 | 3.00 cyc | 3.00 cyc | 1.000 | 1.000 | **Zero Contention** |

---

## 📊 FPGA Synthesis & Hardware Benchmarking

Synthesized with **AMD Xilinx Vivado 2023.1** targeting **28nm Xilinx Kintex-7 FPGA (`xc7k70tfbv676-1`)**, matching the benchmark setup of Reference Paper 1 (*Ved et al., IEEE SPIN 2017*).

| Metric / Parameter | Ved et al. (IEEE SPIN 2017) | Vinoth Kumar et al. (2014) | Baseline Router | **Upgraded VC Router** | **Full 2x2 Mesh Interconnect** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Topology** | 2D-Mesh Router | Single Router | 5-Port Router | **5-Port VC Router** | **2x2 2D-Mesh (4 Routers, 4 PEs)** |
| **Virtual Channels** | 1 or 2 VCs | 1 VC | 1 VC | **2 VCs per port (10 total)** | **2 VCs per port (40 total)** |
| **Arbitration** | Round Robin | Round Robin | 5-to-1 RR | **10-to-1 Round Robin** | **Distributed 10-to-1 Arbiters** |
| **FPGA Slice LUTs** | Not reported | 1,242 Slices | 657 (1.60%) | **1,271 (3.10%)** | **2,533 (6.18%)** |
| **FPGA Registers (FFs)**| Distributed RAMs| Unspecified | 755 (0.92%) | **810 (0.99%)** | **2,016 (2.46%)** |
| **Max Clock Freq ($F_{max}$)**| ~120.0 MHz | ~50.0 MHz | 180.2 MHz | **227.48 MHz ($T_{min}=4.396\text{ ns}$)**| **229.62 MHz ($T_{min}=4.355\text{ ns}$)**|
| **Total On-Chip Power** | ~0.250 W | ~1.446 $\mu$W | 0.138 W | **0.189 W** | **0.162 W** |
| **Hop Latency** | 3 cycles | Multi-cycle | 1–2 cycles | **1–2 cycles** | **5 cycles (2 network hops)** |
| **Packet Loss Rate** | 0% | 0% | 0% | **0% (Lossless credit backpressure)**| **0% (Lossless credit backpressure)**|

---

## 🚀 Execution & Reproduction Commands

All commands can be executed directly in Windows PowerShell:

### 1. Run Constrained-Random Scoreboard Verification:
```powershell
& 'D:\xilinx\Vivado\2023.1\bin\xvlog.bat' -work work rtl/*.v tb/tb_noc_random_scoreboard.v
& 'D:\xilinx\Vivado\2023.1\bin\xelab.bat' -top tb_noc_random_scoreboard -snapshot noc_sb_sim5 -debug typical
& 'D:\xilinx\Vivado\2023.1\bin\xsim.bat' noc_sb_sim5 -R
```

### 2. Run 2x2 Mesh Multi-Hop System Verification:
```powershell
& 'D:\xilinx\Vivado\2023.1\bin\xvlog.bat' -work work tb/tb_noc_mesh_2x2.v
& 'D:\xilinx\Vivado\2023.1\bin\xelab.bat' -top tb_noc_mesh_2x2 -snapshot mesh_sim2 -debug typical
& 'D:\xilinx\Vivado\2023.1\bin\xsim.bat' mesh_sim2 -R
```

### 3. Run Traffic Performance Benchmarks (Latency vs Load Curves):
```powershell
& 'D:\xilinx\Vivado\2023.1\tps\win64\python-3.8.3\python.exe' scripts/benchmark_traffic.py
```

### 4. Run FPGA Synthesis on Xilinx Kintex-7:
```powershell
& 'D:\xilinx\Vivado\2023.1\bin\vivado.bat' -mode batch -source scripts/run_synth_vc.tcl
```

---

## 📚 Key Reference Literature
1. **Sneha N. Ved, Aparna Arya, Ankit Bhange, Joycee Mekie**, *"A Comparative Study of Input Port and Crossbar Configurations in NoC Router Microarchitectures"*, IEEE 4th International Conference on Signal Processing and Integrated Networks (SPIN), 2017.
2. **Vinoth Kumar M., Senthil Kumar M.**, *"Design and Implementation of Router Arbitration in Network on Chip"*, SSRN Electronic Journal, 2014.
3. **Avinash G., Megha N.**, *"Design and Verification of Five Port Router Network"*, IOSR Journal of Electronics and Communication Engineering (IOSR-JECE), Vol. 13, Issue 2, 2018.
4. **Xu Wang, Ge Gan, Dongrui Fan, Shuxu Guo**, *"GFFC: the Global Feedback based Flow Control in the NoC Design for Many-core Processor"*, IEEE NPC, 2009.
5. **J.T. Yantchev et al.**, *"Low-Latency Asynchronous FIFO Buffers"*, IEEE, 1995.
