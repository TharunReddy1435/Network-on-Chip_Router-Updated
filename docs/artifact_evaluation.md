# Artifact Evaluation & Reproducibility Guide

### Project: 5-Port Virtual-Channel Network-on-Chip (NoC) Router & $2 \times 2$ Mesh Interconnect
**Target Venues:** IEEE ISVLSI / IEEE SOCC / IEEE/ACM NOCS  
**ACM/IEEE Badges Claimed:**
* [x] **Artifact Available:** Complete Verilog RTL, testbenches, simulation engines, dataset generators, and synthesis scripts are publicly hosted on GitHub.
* [x] **Artifacts Evaluated - Functional:** All scripts run deterministically to completion with self-checking assertions and zero manual intervention.
* [x] **Results Replicated:** All experimental figures and tables reported in the paper (throughput, latency, HoL blocking reduction, bounded delay, FPGA LUT/FF/Fmax) reproduce exactly from the included codebase.

---

## 1. System Requirements & Prerequisites

| Component | Minimum Specification | Recommended Specification |
| :--- | :--- | :--- |
| **Operating System** | Windows 10/11 64-bit or Ubuntu 20.04/22.04 LTS | Windows 11 64-bit / Linux x86_64 |
| **EDA Toolchain** | AMD / Xilinx Vivado ML Standard (2020.2+) | AMD / Xilinx Vivado ML 2023.1+ |
| **Python Environment** | Python 3.8+ with `matplotlib`, `pillow`, `numpy` | Bundled Vivado Python or System Python 3.8+ |
| **LaTeX Engine (Optional)** | TeX Live 2022+ / MiKTeX / Overleaf | `pdflatex` + `bibtex` |
| **Memory & Storage** | 8 GB RAM, 2 GB free disk space | 16 GB RAM, SSD |

---

## 2. Directory Structure

```
├── paper/                                  # IEEE Conference Paper Package
│   ├── IEEEtran.cls                        # Official IEEE double-column LaTeX class
│   ├── main.tex                            # Complete 6-page camera-ready manuscript
│   ├── references.bib                      # 18 curated citations (2023-2026 IEEE transactions)
│   └── figures/                            # Vector PDF, 300-DPI PNG, and SVG figures
│       ├── fig1_router_microarchitecture.* # Router structural block diagram
│       ├── fig2_mesh_topology.*            # 2x2 mesh topology with credit links
│       ├── fig3_flit_format.*              # 16-bit flit wire format
│       ├── fig4_arbiter_fsm.*              # 10-to-1 round-robin priority rotation
│       └── plot1_... to plot8_...          # 8 publication-grade result plots
├── docs/                                   # Documentation & Artifacts
│   ├── conference_paper.md                 # Complete markdown equivalent with KaTeX
│   ├── artifact_evaluation.md              # This reproducibility guide
│   └── plots/academic/                     # High-res academic figures
├── rtl/                                    # Synthesizable Verilog HDL Core
│   ├── noc_fifo.v                          # FWFT synchronous circular FIFO buffer
│   ├── noc_vc_input_port.v                 # Dual-VC input port unit
│   ├── xy_routing.v                        # Deadlock-free Dimension-Order XY routing
│   ├── rr_arbiter_10.v                     # 10-to-1 Starvation-free Round-Robin arbiter
│   ├── crossbar_10x5.v                     # 10x5 qualified crossbar switch fabric
│   ├── credit_counter.v                    # Credit-based flow control tracker
│   ├── noc_router_5port.v                  # 5-Port Dual-VC router top level
│   ├── noc_mesh_2x2.v                      # 2x2 2D-Mesh multi-node interconnect
│   └── noc_router_single_vc_baseline.v     # Single-VC baseline for HoL comparison
├── tb/                                     # Self-Checking Verification Testbenches
│   ├── tb_noc_dataset_driven.v             # Associative scoreboard multi-dataset engine
│   ├── tb_noc_mesh_2x2.v                   # 2x2 mesh multi-node system testbench
│   ├── tb_noc_router_5port.v               # Standalone 5-port router testbench
│   └── tb_hol_comparison.v                 # Direct HoL blocking side-by-side testbench
├── datasets/                               # 1,000-Flit Benchmark Workload Traces
│   ├── dataset_uniform_random.hex          # Uniform random traffic trace
│   ├── dataset_hotspot_node3.hex           # 45% Hotspot traffic targeting Node 3 (1,1)
│   ├── dataset_matrix_transpose.hex        # Matrix transpose (x,y) -> (y,x) trace
│   ├── dataset_bit_complement.hex          # Bit-complement bisection traffic trace
│   └── dataset_resnet_cnn.hex              # ResNet CNN multi-flit wormhole bursts
└── scripts/                                # Automation Scripts
    ├── generate_noc_dataset.py             # Benchmark dataset generator
    ├── generate_publication_plots.py       # 300-DPI Matplotlib publication plotter
    ├── generate_diagrams_matplotlib.py     # Vector architectural diagram generator
    ├── run_sim.bat                         # Automated Vivado XSIM simulation runner
    └── synth_vc_router.tcl                 # Vivado Kintex-7 FPGA synthesis script
```

---

## 3. Step-by-Step Reproduction Instructions

### Step 1: Regenerate Benchmark Datasets (Optional)
The pre-synthesized 1,000-flit benchmark traces are included in `datasets/*.hex`. To re-generate or modify injection rates:
```powershell
python scripts/generate_noc_dataset.py
```
This produces 5 trace files containing 1,000 hexadecimal flits formatted for `$readmemh` consumption in Verilog.

---

### Step 2: Run Vivado Simulation Regressions

Execute simulations using the unified automated test runner (`scripts\run_sim.bat`):

#### 2.1 Trace-Driven Dataset Benchmark Regression (All 5 Workloads)
```cmd
scripts\run_sim.bat dataset
```
*Expected Output:*
```
================================================================================
  NOC ROUTER DATASET-DRIVEN BENCHMARK TESTBENCH
  Trace: datasets/dataset_resnet_cnn.hex (1000 Flits)
================================================================================
  [T=    55] Node 0 sent Flit 0x5011 (VC0, Dest: (0,0), Type: SINGLE)
  ...
================================================================================
  BENCHMARK SIMULATION COMPLETE
  Total Flits Injected :  1000
  Total Flits Received :  1000
  Data Mismatches      :     0
  Packet Loss Rate     : 0.00%
  Average Latency      : 3.12 cycles
  Overall Result       : *** BENCHMARK TEST PASSED (LOSSLESS) ***
================================================================================
```

#### 2.2 Complete $2 \times 2$ Mesh Multi-Node Interconnect Simulation
```cmd
scripts\run_sim.bat mesh
```
*Expected Output:* Verifies all 4 nodes (PE0, PE1, PE2, PE3) exchanging multi-hop flits with credit backpressure. Status: `ALL TESTS PASSED`.

#### 2.3 Standalone 5-Port Router Simulation
```cmd
scripts\run_sim.bat router
```
*Expected Output:* Tests all 5 physical ports (Local, North, South, East, West) across both VC0 and VC1 simultaneously. Status: `ALL TESTS PASSED`.

#### 2.4 Head-of-Line (HoL) Blocking Comparison Test
```cmd
scripts\run_sim.bat hol
```
*Expected Output:* Compares Single-VC baseline vs Dual-VC router under identical blocked-channel stimuli, verifying an 81.3% reduction in blocked cycles.

---

### Step 3: Run FPGA Synthesis & Timing Closure

To synthesize the design and measure device utilization and $F_{\max}$ on an AMD/Xilinx Kintex-7 FPGA (`xc7k70tfbv676-1`):
```powershell
vivado -mode batch -source scripts/synth_vc_router.tcl
```
*Expected Synthesis Results:*
* **Dual-VC Router:** 1,271 Slice LUTs (3.10%), 810 FFs (0.99%), $F_{\max} = 227.48\text{ MHz}$ ($T_{\min} = 4.396\text{ ns}$).
* **$2 \times 2$ Mesh (4 Routers):** 2,533 Slice LUTs (6.18%), 2,016 FFs (2.46%), $F_{\max} = 229.62\text{ MHz}$ ($T_{\min} = 4.355\text{ ns}$).

---

### Step 4: Regenerate Publication-Grade Plots & Diagrams

All 8 experimental plots and 4 architectural block diagrams can be regenerated in 300-DPI PNG, vector PDF, and SVG:
```powershell
# Generate experimental performance plots
& "D:\xilinx\Vivado\2023.1\tps\win64\python-3.8.3\python.exe" scripts/generate_publication_plots.py

# Generate architectural block diagrams
& "D:\xilinx\Vivado\2023.1\tps\win64\python-3.8.3\python.exe" scripts/generate_diagrams_matplotlib.py
```
Outputs are automatically synced to:
* `paper/figures/` (for LaTeX compilation)
* `docs/plots/academic/` (for GitHub markdown rendering)

---

### Step 5: Compile the IEEE Conference Paper

To compile the camera-ready double-column PDF:
```bash
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```
*Output:* `paper/main.pdf` (6-page IEEE-compliant conference manuscript).  
*Alternative:* Upload the entire `paper/` directory directly to [Overleaf](https://www.overleaf.com) and click **Recompile**.

---

## 4. Formal Proof Verification Matrix

| Theorem | Formal Claim | Verilog RTL Implementation | Simulation Verification |
| :--- | :--- | :--- | :--- |
| **Theorem 1** | Deadlock & livelock freedom via forbidden $Y \to X$ turns | `rtl/xy_routing.v` strictly disallows $N \to E, N \to W, S \to E, S \to W$ turns | Zero deadlocks observed across 5,000 multi-hop benchmark flits |
| **Theorem 2** | Starvation-free arbitration with bounded delay $\le 9$ cycles | `rtl/rr_arbiter_10.v` rotates priority: $\pi(t+1) = (g(t) + 1) \bmod 10$ | Delay histogram measured in XSIM: worst-case delay $\equiv 9$ cycles |
| **Theorem 3** | Lossless transmission: $C(t) + Q(t) = C_{\max}$ | `rtl/credit_counter.v` tracks downstream credits; grant requires $C(t) > 0$ | 0.00% packet loss across 5,000 flits in 5 realistic traffic traces |

---

## 5. Contact & Support

For artifact evaluation queries, reproduction troubleshooting, or questions regarding the HDL architecture:
* **GitHub Repository:** [Network-on-Chip_Router_Final](https://github.com/TharunReddy1435/Network-on-Chip_Router_Final.git)
* **Authors:** Shrestitha, Tharun, Bhavani, Gowtham  
* **Department:** Electronics and Communication Engineering
