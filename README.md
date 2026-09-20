# 5-Port Network-on-Chip (NoC) Router in Verilog HDL

Design, functional verification, FPGA synthesis, and benchmarking of a high-performance **5-Port 2D-Mesh NoC Router** developed for the **Data Networks (DN)** course.

---

## 👥 Team & Responsibilities

| Team Member | Role | Key Contributions |
| :--- | :--- | :--- |
| **Shrestitha** | **Buffering & Storage Lead** | Synchronous circular FIFO buffer design (`noc_fifo.v`), First-Word Fall-Through (FWFT) logic, status flags (`full`, `empty`, `almost_full`), and credit generation pulse. |
| **Tharun** | **Routing & Switching Lead** | Dimension-Order XY Routing unit (`xy_routing.v`), deadlock/livelock prevention turn model, and 5x5 Crossbar Switch Matrix (`crossbar_5x5.v`). |
| **Bhavani** | **Arbitration & Flow Control Lead** | 5-input starvation-free Round-Robin Arbiter (`rr_arbiter_5.v`) with rotating cyclic priority, and Credit Counter flow control (`credit_counter.v`). |
| **Gowtham** | **Integration & Verification Lead** | Top-level router integration (`noc_router_top.v`), self-checking testbenches (`tb_noc_router_top.v`), simulation automation, and Kintex-7 FPGA synthesis. |

---

## 🏛️ Architecture Overview

The router employs a modular 2D-Mesh microarchitecture connecting 5 directions: **Local (PE)**, **North**, **South**, **East**, and **West**.

```
                         North Port (1)
                               ▲
                               │
            West Port (4) ◄────┼────► East Port (3)
                               │
                               ▼
                         South Port (2)
                               ▲
                               │
                        Local Core (0)
```

```
+-----------------------------------------------------------------------------------+
|                            5-PORT NoC ROUTER PIPELINE                             |
|                                                                                   |
|  [Input Ports]             [Route Compute]           [Arbitration]   [Crossbar]   |
|   5x Synchronous FIFO  -->  5x Dimension-Order  -->  5x Round Robin  -->  5x5 Mux |
|   (FWFT, Depth 8)           XY Routing Logic         Arbiters             Switch  |
|                                                                                   |
|                            [Flow Control]                                         |
|                       <--  5x Credit Counters (Lossless Backpressure)             |
+-----------------------------------------------------------------------------------+
```

### Key Technical Highlights:
1. **First-Word Fall-Through (FWFT) FIFO**: Flits are immediately available on the FIFO output without requiring a 1-cycle read latency. This allows Route Computation to proceed in parallel with flit arrival.
2. **Deterministic XY Routing**: Routes along the X-dimension until $X_{dest} == X_{curr}$, then along the Y-dimension until $Y_{dest} == Y_{curr}$, and finally to the Local processing element. By strictly prohibiting $Y \to X$ turns, circular channel dependencies are eliminated, guaranteeing deadlock-free and livelock-free routing.
3. **Starvation-Free Round Robin Arbitration (RRA)**: Enforces local fairness by rotating priority to $(grant\_id + 1) \pmod 5$ after each grant, guaranteeing bounded latency (at most 4 cycles waiting time under full contention).
4. **Credit-Based Flow Control**: Tracks downstream receiver buffer capacity. Pauses transmission when credits drop to 0, ensuring zero packet drops under network congestion.

---

## 📁 Repository Structure

```
.
├── rtl/                        # Synthesizable Verilog HDL Source Files
│   ├── noc_fifo.v              # Synchronous FIFO with FWFT & Credit Pulse (Shrestitha)
│   ├── xy_routing.v            # Dimension-Order XY Routing Unit (Tharun)
│   ├── crossbar_5x5.v          # 5x5 Crossbar Switch Matrix (Tharun)
│   ├── rr_arbiter_5.v          # Starvation-Free Round Robin Arbiter (Bhavani)
│   ├── credit_counter.v        # Credit-Based Flow Control Counter (Bhavani)
│   └── noc_router_top.v        # Top-Level 5-Port NoC Router (Gowtham)
│
├── tb/                         # Verification Testbenches
│   └── tb_noc_router_top.v     # 7-Scenario Self-Checking Verification Suite (Gowtham)
│
├── scripts/                    # Automation Scripts
│   ├── run_sim.bat             # One-click Windows batch simulation script
│   └── run_synth.tcl           # Automated Vivado Kintex-7 FPGA synthesis script
│
├── docs/                       # Project Documentation & Presentation
│   ├── presentation_slides_content.md # Complete slide-by-slide text & tables (40 marks)
│   └── team_member_guide.md    # Detailed team role guide, theory & viva Q&A
│
├── synth_utilization.rpt       # Vivado Synthesis Resource Utilization Report
├── synth_timing.rpt            # Vivado Timing Summary & Fmax Report
├── synth_power.rpt             # Vivado Power Analysis Report
└── README.md                   # Project Overview
```

---

## 🧪 Verification & Simulation Results

Run the simulation on Windows using Vivado Simulator by double-clicking `scripts/run_sim.bat` or executing in PowerShell:

```powershell
.\scripts\run_sim.bat
```

### Test Suite Execution Summary (7/7 Tests Passed):
* **Test 1**: Local $\to$ East directed routing — **PASS**
* **Test 2**: Local $\to$ West directed routing — **PASS**
* **Test 3**: Local $\to$ South directed routing — **PASS**
* **Test 4**: Local $\to$ North directed routing — **PASS**
* **Test 5**: North $\to$ Local PE inbound routing — **PASS**
* **Test 6**: Simultaneous contention on Local port (North & West) resolved via Round Robin — **PASS**
* **Test 7**: Credit return pulse and backpressure verification — **PASS**

---

## 📊 Synthesis & Benchmarking Against Published Literature

Synthesized with **AMD Xilinx Vivado 2023.1** targeting a **28nm Xilinx Kintex-7 FPGA (`xc7k70tfbv676-1`)**, matching the benchmark setup of Reference Paper 1 (*Ved et al., IEEE SPIN 2017*).

| Metric / Parameter | Ved et al. (IEEE SPIN 2017) | Vinoth Kumar et al. (2014) | Avinash et al. (IOSR 2018) | **Our Project (Implemented)** |
| :--- | :--- | :--- | :--- | :--- |
| **Router Architecture** | 5-Port 2D-Mesh Router | 5-Port Router | 5-Port Router | **5-Port 2D-Mesh Router** |
| **Routing Algorithm** | Dimension-Order XY | Round Robin / XY | FSM Deterministic XY | **Deterministic Dimension-Order XY** |
| **Arbitration Scheme** | Matrix / Round Robin | Round Robin Arbiter | FSM Controller | **Starvation-Free Round Robin (RRA)** |
| **Flow Control** | Credit-Based / VC | Handshake | Handshake | **Credit-Based Backpressure** |
| **Flit Width** | 38-bit / 68-bit | 8-bit to 40-bit | 8-bit | **16-bit (Configurable)** |
| **Buffer Depth** | Depth 1, 2, 4, 8 | Depth 16 | Depth 16 | **Depth 8 (Configurable)** |
| **Synthesis Target** | Kintex-7 KC705 (28nm) | Spartan-3 (xc3s200) | Spartan-3 / ISE | **Xilinx Kintex-7 (28nm, Vivado 2023.1)** |
| **FPGA Slice LUTs** | Not reported in LUTs | 1242 Slices | ~4 Router Slices | **657 Slice LUTs (1.60% utilization)** |
| **FPGA Registers (FFs)**| Distributed RAMs | Unspecified | Unspecified | **755 Flip-Flops (0.92% utilization)** |
| **Max Clock Freq ($F_{max}$)**| ~120 MHz | ~50 MHz | Unspecified | **180.2 MHz ($T_{min} = 5.549\text{ ns}$)** |
| **Hop Traversal Latency**| 3 clock cycles | Multi-cycle | 3–4 clock cycles | **1–2 clock cycles (FWFT Crossbar)** |
| **Packet Loss Rate** | 0% | 0% | 0% | **0% (Zero loss under backpressure)** |

---

## 📚 Key Reference Papers
1. **Sneha N. Ved, Aparna Arya, Ankit Bhange, Joycee Mekie**, *"A Comparative Study of Input Port and Crossbar Configurations in NoC Router Microarchitectures"*, IEEE SPIN, 2017.
2. **Vinoth Kumar M., Senthil Kumar M.**, *"Design and Implementation of Router Arbitration in Network on Chip"*, SSRN, 2014.
3. **Avinash G., Megha N.**, *"Design and Verification of Five Port Router Network"*, IOSR-JECE, 2018.
4. **Xu Wang, Ge Gan, Dongrui Fan, Shuxu Guo**, *"GFFC: the Global Feedback based Flow Control in the NoC Design for Many-core Processor"*, IEEE NPC, 2009.
5. **J.T. Yantchev et al.**, *"Low-Latency Asynchronous FIFO Buffers"*, IEEE, 1995.
