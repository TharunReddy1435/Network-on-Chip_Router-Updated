# Network-on-Chip (NoC) Router & 2x2 Mesh: Comprehensive Team Guide & Viva Manual

This guide is tailored specifically for **Shrestitha (`24ECB0B24`)**, **Tharun (`24ECB0B20`)**, **Bhavani (`24ECB0B60`)**, and **Gowtham (`24ECB0B41`)**. It provides complete technical explanations of each person's hardware modules, execution commands, architecture diagrams, benchmark datasets, visual plots, and anticipated viva/defense questions with exact model answers.

---

## 👥 Team Roster & Module Ownership

| Roll Number | Team Member | Engineering Role | Core Hardware Modules & Scripts |
| :---: | :--- | :--- | :--- |
| **`24ECB0B24`** | **Shrestitha** | **Buffering & Storage Lead** | Dual Virtual-Channel input buffers (`noc_vc_input_port.v`), synchronous circular FIFO (`noc_fifo.v`), First-Word Fall-Through (FWFT) logic, Head-of-Line (HoL) blocking elimination, credit pulse generation. |
| **`24ECB0B20`** | **Tharun** | **Routing & Switching Lead** | Dimension-Order XY Routing units (`xy_routing.v`), deadlock/livelock prevention turn model, 10x5 Crossbar Switch Matrix (`crossbar_10x5.v`) with non-empty output qualification. |
| **`24ECB0B60`** | **Bhavani** | **Arbitration & Flow Control Lead** | 10-input starvation-free Round-Robin Arbiter (`rr_arbiter_10.v`) with rotating cyclic priority, bounded latency guarantees ($\le 9$ cycles), Credit Counter flow control (`credit_counter.v`). |
| **`24ECB0B41`** | **Gowtham** | **Integration & Verification Lead** | 2x2 2D-Mesh Interconnect (`noc_mesh_2x2.v`), Dataset-Driven Verification (`tb_noc_dataset_driven.v`), Scoreboard TB (`tb_noc_random_scoreboard.v`), Benchmark Suite (`generate_noc_dataset.py`, `generate_plots.py`), Kintex-7 FPGA Synthesis. |

---

## 1. Shrestitha (`24ECB0B24`): Buffering & Storage Lead

### Assigned Modules:
* [`rtl/noc_fifo.v`](file:///d:/DN%20Project/rtl/noc_fifo.v) — First-Word Fall-Through (FWFT) Circular FIFO Buffer
* [`rtl/noc_vc_input_port.v`](file:///d:/DN%20Project/rtl/noc_vc_input_port.v) — Dual Virtual-Channel Input Buffer Unit

### Module Architecture & Technical Deep-Dive:
1. **First-Word Fall-Through (FWFT) Mechanism**:
   - In standard synchronous FIFOs, data appears at `dout` only on the clock edge *after* `rd_en` is asserted (1-cycle read latency).
   - In `noc_fifo.v`, FWFT is implemented via `assign dout = mem[rd_ptr];`.
   - **Why this matters**: As soon as a flit enters the buffer, its header (destination coordinates) is combinatorially visible to the Routing Unit and Arbiter immediately without an extra read cycle, eliminating pipeline bubbles.
2. **Dual Virtual Channels (VC0 and VC1)**:
   - Each physical input channel is equipped with **two independent FIFOs** (`fifo_vc0` and `fifo_vc1`).
   - Incoming flit bit `[5]` indicates the virtual channel ID (`0 = VC0`, `1 = VC1`).
   - Demultiplexing logic routes writes into the appropriate queue:
     ```verilog
     wire wr_en_vc0 = wr_en && (incoming_vc == 1'b0);
     wire wr_en_vc1 = wr_en && (incoming_vc == 1'b1);
     ```
3. **Head-of-Line (HoL) Blocking Elimination**:
   - In a single-VC router, if packet A at the head of the queue is blocked (e.g. waiting for a congested East port), packet B behind it is trapped—even if packet B wants an idle North port.
   - With Dual VCs, packet A resides in VC0 while packet B resides in VC1. VC1 requests the North port independently, completely bypassing the blocked VC0!
   - Our benchmarks confirm an **81.3% reduction in HoL contention** (see `docs/plots/plot4_hol_blocking_mitigation.svg`).
4. **Credit Pulse Generation**:
   - Whenever a flit is read out (`rd_en && !empty`), `credit_out` pulses high for exactly 1 clock cycle to notify the upstream sending router that one buffer slot has been freed.

### Anticipated Viva / Review Questions for Shrestitha:
1. **Q: How does your FIFO handle simultaneous read and write in the same clock cycle?**
   - *Answer*: "When `wr_en && !full && rd_en && !empty` occur simultaneously, `wr_ptr` advances to write the new flit into memory, while `rd_ptr` advances to read the old flit. The occupancy `count` remains unchanged. A `credit_out` pulse is emitted because a buffer slot was freed."
2. **Q: Why is FWFT critical for NoC router performance?**
   - *Answer*: "Standard FIFOs add an extra clock cycle just to pop the header before route evaluation can begin. FWFT makes the header immediately available at `dout` combinatorially, allowing route computation and switch allocation to happen in the current cycle, reducing hop latency to 1 cycle."
3. **Q: Why use Dual Virtual Channels instead of simply doubling the single FIFO depth?**
   - *Answer*: "Doubling the depth of a single FIFO does not solve Head-of-Line blocking; in fact, a deeper single FIFO worsens HoL blocking because more packets get trapped behind a stalled head flit. Splitting the storage into two independent Virtual Channels allows packets destined for unblocked ports to bypass blocked packets."

---

## 2. Tharun (`24ECB0B20`): Routing & Switching Lead

### Assigned Modules:
* [`rtl/xy_routing.v`](file:///d:/DN%20Project/rtl/xy_routing.v) — Deterministic Dimension-Order XY Routing Unit
* [`rtl/crossbar_10x5.v`](file:///d:/DN%20Project/rtl/crossbar_10x5.v) — 10x5 Crossbar Switch Fabric
* [`rtl/crossbar_5x5.v`](file:///d:/DN%20Project/rtl/crossbar_5x5.v) — Baseline 5x5 Crossbar Switch Fabric

### Module Architecture & Technical Deep-Dive:
1. **Deterministic Dimension-Order XY Routing**:
   - Evaluates destination coordinates $(X_{dest}, Y_{dest})$ against current router coordinates $(X_{curr}, Y_{curr})$:
     1. If $X_{dest} > X_{curr} \implies$ Request **EAST** port (`req_port[3] = 1`).
     2. If $X_{dest} < X_{curr} \implies$ Request **WEST** port (`req_port[4] = 1`).
     3. If $X_{dest} == X_{curr}$ and $Y_{dest} > Y_{curr} \implies$ Request **SOUTH** port (`req_port[2] = 1`).
     4. If $X_{dest} == X_{curr}$ and $Y_{dest} < Y_{curr} \implies$ Request **NORTH** port (`req_port[1] = 1`).
     5. If $X_{dest} == X_{curr}$ and $Y_{dest} == Y_{curr} \implies$ Request **LOCAL** PE port (`req_port[0] = 1`).
2. **Deadlock Freedom Proof (Turn Model)**:
   - Dally & Seitz established that network deadlock occurs if and only if there is a cycle in the channel dependency graph.
   - XY routing enforces that packets must complete all X-dimension travel before making any turn into the Y-dimension.
   - Consequently, all four $Y \to X$ turns (North $\to$ East, North $\to$ West, South $\to$ East, South $\to$ West) are **strictly forbidden**.
   - With 4 out of 8 possible turns eliminated, circular waiting chains cannot form, mathematically guaranteeing zero deadlock and livelock.
3. **10x5 Crossbar Switch Fabric**:
   - The upgraded Virtual-Channel router has 10 candidate input queues (2 VCs $\times$ 5 physical ports) and 5 physical output channels.
   - Consists of 5 independent 10-to-1 multiplexers controlled by 10-bit one-hot grant vectors from the arbiters.
   - **Spurious Emission Prevention**: Outgoing valid flags are qualified with the non-empty status of the granted buffer:
     ```verilog
     valid_local = |(grant_local & ~empty_inputs);
     ```
     This strictly prevents the transmission of empty 0x0000 data when an arbiter grants an empty queue.

### Anticipated Viva / Review Questions for Tharun:
1. **Q: Why choose deterministic XY routing over adaptive routing (such as DyXY)?**
   - *Answer*: "Deterministic XY routing has minimal logic depth (only simple combinational comparators), requires no complex congestion-sensing wires between adjacent routers, and provides an unconditional mathematical guarantee of deadlock freedom. Adaptive routing requires virtual channel routing restrictions and complex arbitration that significantly increase area, power, and cycle time."
2. **Q: How does the crossbar switch handle multiple packets at the same time?**
   - *Answer*: "The crossbar has 5 separate multiplexers operating in parallel. As long as the granted packets are destined for different output ports (e.g. one packet going East, one going South, one going Local), all 5 transfers execute concurrently within the exact same clock cycle."
3. **Q: What is the purpose of qualifying `valid_out` with `~empty_inputs`?**
   - *Answer*: "In a synchronous arbiter, the grant register updates at the clock edge. If a queue was read in cycle $T$, it becomes empty in cycle $T+1$. By gating the output valid signal with `~empty_inputs`, we ensure that if an arbiter grants an empty FIFO, no false valid pulse or 0-data is emitted downstream."

---

## 3. Bhavani (`24ECB0B60`): Arbitration & Flow Control Lead

### Assigned Modules:
* [`rtl/rr_arbiter_10.v`](file:///d:/DN%20Project/rtl/rr_arbiter_10.v) — 10-Input Starvation-Free Round-Robin Arbiter
* [`rtl/rr_arbiter_5.v`](file:///d:/DN%20Project/rtl/rr_arbiter_5.v) — Baseline 5-Input Round-Robin Arbiter
* [`rtl/credit_counter.v`](file:///d:/DN%20Project/rtl/credit_counter.v) — Credit-Based Backpressure Tracker

### Module Architecture & Technical Deep-Dive:
1. **10-Input Round-Robin Arbiter (RRA)**:
   - Arbitrates between 10 Virtual Channel request lines competing for a shared output channel:
     - Bit `[0..1]`: Local VC0, VC1
     - Bit `[2..3]`: North VC0, VC1
     - Bit `[4..5]`: South VC0, VC1
     - Bit `[6..7]`: East VC0, VC1
     - Bit `[8..9]`: West VC0, VC1
   - **Dynamic Priority Rotation**:
     - Maintains a cyclic priority pointer `priority_ptr` ($0 \dots 9$).
     - The port granted in the current cycle is demoted to lowest priority in the next cycle:
       $$\text{priority\_ptr} \leftarrow (\text{granted\_id} + 1) \pmod{10}$$
     - **Bounded Latency Guarantee**: Any requesting virtual channel is guaranteed to be serviced within at most 9 clock cycles, eliminating starvation (see `docs/plots/plot6_arbitration_fairness_and_delay.svg`).
2. **Credit-Based Flow Control**:
   - Prevents buffer overflow and packet dropping under network congestion.
   - An internal counter `credits` is initialized on reset to `MAX_CREDITS` (8 buffer slots).
   - When a packet is transmitted through the output channel (`tx_fire`), the counter decrements by 1.
   - When the downstream router pops a flit, it returns a 1-cycle credit pulse (`credit_in`), incrementing the counter.
   - The arbiter is qualified by `credit_ready = (credits > 0)`. If the downstream buffer is full, grants are withheld, applying lossless backpressure.

### Anticipated Viva / Review Questions for Bhavani:
1. **Q: Why is Round Robin arbitration preferred over Strict Priority or FCFS?**
   - *Answer*: "Strict priority permanently starves lower-priority ports during traffic bursts. First-Come-First-Served (FCFS) requires timestamp generators and comparators, which require significant silicon area and logic latency. Round Robin provides fair bandwidth allocation with bounded waiting latency using simple rotating pointers."
2. **Q: How does credit-based flow control eliminate packet drops?**
   - *Answer*: "Unlike lossy networks (like standard Ethernet) that drop packets when buffers fill up and rely on retransmissions, our credit-based flow control maintains exact real-time bookkeeping of downstream buffer space. A packet is never dispatched unless the downstream router is guaranteed to have a free slot, resulting in a strictly lossless NoC."
3. **Q: What happens to credits when a packet is transmitted and a credit return arrives in the same cycle?**
   - *Answer*: "In `credit_counter.v`, when `{tx_fire, credit_in} == 2'b11`, the decrement and increment cancel out (`credits <= credits`), preserving the exact buffer count."

---

## 4. Gowtham (`24ECB0B41`): Integration & Verification Lead

### Assigned Modules & Scripts:
* [`rtl/noc_router_vc.v`](file:///d:/DN%20Project/rtl/noc_router_vc.v) — Upgraded 5-Port Virtual-Channel Router Top
* [`rtl/noc_mesh_2x2.v`](file:///d:/DN%20Project/rtl/noc_mesh_2x2.v) — Multi-Core 2x2 2D-Mesh Interconnect (4 Routers, 4 PEs)
* [`tb/tb_noc_dataset_driven.v`](file:///d:/DN%20Project/tb/tb_noc_dataset_driven.v) — Dataset-Driven Verification Testbench
* [`tb/tb_noc_random_scoreboard.v`](file:///d:/DN%20Project/tb/tb_noc_random_scoreboard.v) — Constrained-Random Scoreboard Testbench
* [`tb/tb_noc_mesh_2x2.v`](file:///d:/DN%20Project/tb/tb_noc_mesh_2x2.v) — System-Level 2x2 Mesh Multi-Hop Testbench
* [`scripts/generate_noc_dataset.py`](file:///d:/DN%20Project/scripts/generate_noc_dataset.py) — Dataset Generator Suite
* [`scripts/generate_plots.py`](file:///d:/DN%20Project/scripts/generate_plots.py) — Publication-Quality Vector Plots Generator
* [`scripts/run_synth_vc.tcl`](file:///d:/DN%20Project/scripts/run_synth_vc.tcl) — Vivado Kintex-7 FPGA Synthesis Script

### Module Architecture & Verification Deep-Dive:
1. **Dataset-Driven Verification (`tb_noc_dataset_driven.v`)**:
   - Ingests 5 standardized benchmark datasets from `dataset/` using `$readmemh`.
   - Replays cycle-accurate traces, computes packet latency, tracks network throughput, and verifies 100% lossless delivery.
2. **Constrained-Random Verification (CRV) with Automated Scoreboard**:
   - In `tb_noc_random_scoreboard.v`, an automated stimulus generator injects random flits with varying destinations, VCs, and payloads.
   - An independent Golden Reference Model checks flit arrival order, data corruption, and packet loss.
   - **Result**: 52/52 packets verified with **0 scoreboard errors** and **0 assertion failures**!
3. **2x2 2D-Mesh System Interconnect**:
   - Connects 4 routers in a 2D mesh layout with 4 Processing Elements (`PE0`..`PE3`).
   - Verified multi-hop routing from PE0 to PE3 (2 hops, 5 cycles), wormhole packets (Head $\to$ Body $\to$ Tail), and concurrent 4-node traffic matrix with zero deadlock!
4. **Traffic Performance Benchmarking & Visual Plots**:
   - Evaluates Uniform Random, Hotspot (PE3 Memory), Transpose, Bit-Complement, and CNN ResNet workloads.
   - Generates 7 visual vector plots in `docs/plots/` covering latency, throughput, HoL blocking, FPGA utilization, arbiter fairness, and latency CDF.

### Anticipated Viva / Review Questions for Gowtham:
1. **Q: How did you implement the Professor's suggestions?**
   - *Answer*: "We addressed all three suggestions: (1) Created 5 benchmark datasets in CSV and HEX formats with a dataset-driven testbench (`tb_noc_dataset_driven.v`); (2) Generated 7 publication-quality visual plots in `docs/plots/` showing latency-load curves, saturation throughput, and FPGA hardware comparisons; (3) Added a comprehensive 2023–2026 literature survey in `docs/literature_survey_2023_2026.md` comparing our work against premier IEEE papers."
2. **Q: What is the hardware area cost of adding Virtual Channels?**
   - *Answer*: "Doubling the FIFOs from 5 to 10 and expanding the crossbar from 5x5 to 10x5 increases slice LUT utilization from 657 LUTs to 1,271 LUTs on Kintex-7. However, this represents only 3.10% of the FPGA, operating at 227.48 MHz, while delaying network saturation and providing higher throughput."
3. **Q: How does wormhole routing work in your multi-flit packet test?**
   - *Answer*: "A multi-flit packet consists of a Head flit (allocates the routing path and VC), Body flits (carry raw payload), and a Tail flit (releases the route). Body and Tail flits inherit the path established by the Head flit, verified in Test 3 of `tb_noc_mesh_2x2.v` and in `dataset/cnn_resnet_layer_traffic`."

---

## 5. Ready-to-Run Live Demonstration Commands

Run these exact commands in PowerShell in the project directory (`d:\DN Project`):

### 1. Run Dataset-Driven Verification Simulation:
```powershell
scripts\run_sim.bat dataset    # Uniform Random workload
scripts\run_sim.bat hotspot    # Hotspot Memory Controller workload
scripts\run_sim.bat transpose  # Matrix Transpose permutation workload
scripts\run_sim.bat bitcomp    # Bit-Complement bisection stress workload
scripts\run_sim.bat cnn        # Pipelined Deep Learning CNN workload

# Or manual execution:
& 'D:\xilinx\Vivado\2023.1\bin\xvlog.bat' -work work rtl/*.v tb/tb_noc_dataset_driven.v
& 'D:\xilinx\Vivado\2023.1\bin\xelab.bat' -generic_top DATASET_FILE=\"dataset/uniform_random_1000.hex\" -top tb_noc_dataset_driven -snapshot dataset_sim -debug typical
& 'D:\xilinx\Vivado\2023.1\bin\xsim.bat' dataset_sim -R
```

### 2. Run Constrained-Random Scoreboard Simulation (Dual-VC Router):
```powershell
& 'D:\xilinx\Vivado\2023.1\bin\xvlog.bat' -work work rtl/*.v tb/tb_noc_random_scoreboard.v
& 'D:\xilinx\Vivado\2023.1\bin\xelab.bat' -top tb_noc_random_scoreboard -snapshot noc_sb_sim5 -debug typical
& 'D:\xilinx\Vivado\2023.1\bin\xsim.bat' noc_sb_sim5 -R
```

### 3. Run System-Level 2x2 2D-Mesh Multi-Hop Simulation:
```powershell
& 'D:\xilinx\Vivado\2023.1\bin\xvlog.bat' -work work rtl/*.v tb/tb_noc_mesh_2x2.v
& 'D:\xilinx\Vivado\2023.1\bin\xelab.bat' -top tb_noc_mesh_2x2 -snapshot mesh_sim2 -debug typical
& 'D:\xilinx\Vivado\2023.1\bin\xsim.bat' mesh_sim2 -R
```

### 4. Regenerate Benchmark Datasets & Graphical Plots:
```powershell
python scripts/generate_noc_dataset.py
python scripts/generate_plots.py
```

### 5. Run FPGA Synthesis on Xilinx Kintex-7:
```powershell
& 'D:\xilinx\Vivado\2023.1\bin\vivado.bat' -mode batch -source scripts/run_synth_vc.tcl
```
