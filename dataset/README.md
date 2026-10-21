# Network-on-Chip (NoC) Benchmark & Verification Datasets

Comprehensive synthetic and domain-specific communication traffic datasets designed for functional verification, cycle-accurate simulation, and performance benchmarking of the **5-Port Virtual-Channel NoC Router** and **2x2 2D-Mesh Interconnect**.

---

## 📁 Dataset Catalog & Workload Profiles

The `dataset/` directory contains five benchmark workloads representing standard microarchitecture traffic models and modern deep learning accelerator communication:

| Dataset File | Traffic Model | Communication Characteristics | Target Stress Area | Standard Suite / Full Scale |
| :--- | :--- | :--- | :--- | :---: |
| **`uniform_random_1000`** | Uniform Random (UR) | Destination chosen uniformly at random across all remaining mesh nodes with equal probability ($\mathcal{U}[0, N-1]$). | Baseline router pipeline delay, arbiter rotation fairness under balanced load. | 60 flits / 1,000 flits |
| **`hotspot_memory_1000`** | Hotspot Traffic (HS) | 45% of all injected packets converge onto Node (1,1) / PE3 (representing a shared centralized L2/HBM memory controller). Remaining 55% distributed uniformly. | Head-of-Line (HoL) blocking, buffer saturation backpressure, credit depletion. | 60 flits / 1,000 flits |
| **`transpose_1000`** | Matrix Transpose (TR) | Nodes transmit to their transpose coordinates: $(x,y) \to (y,x)$. In 2x2: PE0 $\leftrightarrow$ PE3, PE1 $\leftrightarrow$ PE2. | Localized link bottlenecks, diagonal bisection bandwidth. | 60 flits / 1,000 flits |
| **`bit_complement_1000`** | Bit-Complement (BC) | Node $(x,y)$ transmits to $(\sim x, \sim y)$ in binary: PE0 (0,0) $\to$ PE3 (1,1) and PE1 (1,0) $\to$ PE2 (0,1). | Maximum bisection channel stress, router crossbar contention. | 60 flits / 1,000 flits |
| **`cnn_resnet_layer_traffic`** | Pipelined Deep Learning CNN | Pipelined activation transfers (70%), residual bypass connections (15%), and backward parameter updates (15%) with 3-flit wormhole bursts (Head $\to$ Body $\to$ Tail). | Multi-flit wormhole routing, Virtual Channel lane isolation, bursty queuing. | 60 flits / 1,000 flits |

> **Note on Dataset Sizing**: All 5 benchmark datasets in this directory are synthesized at the full 1,000-flit scale and verified with 0% packet loss in AMD Vivado XSIM. To re-generate or synthesize smaller/larger traces (e.g., 60 flits for sub-microsecond debug), run `python scripts/generate_noc_dataset.py --packets <N>`.


---

## 📐 Dataset Formats & Schema Specification

Each workload is provided in two synchronized formats:

### 1. Tabular CSV Format (`.csv`)
Human-readable, machine-parseable dataset with complete packet routing and payload metadata:
```csv
entry_id,inject_cycle,src_pe,src_x,src_y,dest_pe,dest_x,dest_y,vc_id,flit_type,payload,hex_flit,hex_trace_word
0,6,0,0,0,3,1,1,0,SINGLE,1,0xD0C1,0x0060D0C1
1,8,2,0,1,1,1,0,1,SINGLE,2,0x9862,0x00889862
...
```

#### Field Descriptions:
- **`entry_id`**: Sequential index of the flit record ($0 \dots 999$).
- **`inject_cycle`**: Simulation cycle timestamp at which the Processing Element asserts `wr_en` and injects the flit into the router input port.
- **`src_pe`**: Injection node ID ($0$: R(0,0), $1$: R(1,0), $2$: R(0,1), $3$: R(1,1)).
- **`src_x`, `src_y`**: 2D-Mesh grid coordinates of the source node ($0$ or $1$).
- **`dest_pe`**: Egress destination PE ID ($0 \dots 3$).
- **`dest_x`, `dest_y`**: 2D-Mesh grid coordinates of the destination node.
- **`vc_id`**: Assigned Virtual Channel queue ($0$ for VC0, $1$ for VC1).
- **`flit_type`**: Packet protocol role:
  - `SINGLE` (`2'b11`): Standalone single-flit packet containing both header and payload.
  - `HEAD` (`2'b01`): First flit of a multi-flit packet; establishes wormhole routing path.
  - `BODY` (`2'b00`): Intermediate payload flit following the head path.
  - `TAIL` (`2'b10`): Final flit; releases router switch state and closes transaction.
- **`payload`**: 5-bit data payload (`0x00` to `0x1F`) used by the verification scoreboard for bit-level data integrity checking.
- **`hex_flit`**: 16-bit packed flit word transmitted across physical inter-router wires.
- **`hex_trace_word`**: 32-bit packed trace word formatted for Verilog testbench ingestion.

---

### 2. Verilog Memory HEX Format (`.hex`)
Formatted specifically for Verilog `$readmemh` system task:
```text
0060D0C1
00889862
00B47403
00C49804
...
```

#### 32-bit Word Bit-Mapping:
```
 31                 20 19    18 17   16 15  14 13  12 11  10 9    8 7    6  5   4        0
┌─────────────────────┬────────┬───────┬──────┬──────┬──────┬──────┬──────┬───┬────────────┐
│    inject_cycle     │ src_pe │ Rsrvd │ ftype│ destX│ destY│ srcX │ srcY │vc │  payload   │
│      (12-bit)       │ (2-bit)│(2-bit)│(2-bit│(2-bit│(2-bit│(2-bit│(2-bit│(1)│   (5-bit)  │
└─────────────────────┴────────┴───────┴──────┴──────┴──────┴──────┴──────┴───┴────────────┘
```

---

## 🛠️ Reproduction & Simulation Launch Commands

### 1. Regenerate Trace Datasets
To regenerate datasets with custom sizes (default: 1,000 flits) or seeds:
```powershell
python scripts/generate_noc_dataset.py --packets 1000
# Or for rapid regression:
python scripts/generate_noc_dataset.py --packets 60
```

### 2. Run Dataset-Driven Verification in AMD Xilinx Vivado
Using the automated batch launcher:
```powershell
scripts\run_sim.bat dataset    # Uniform Random workload
scripts\run_sim.bat hotspot    # Hotspot Memory Controller workload
scripts\run_sim.bat transpose  # Matrix Transpose permutation workload
scripts\run_sim.bat bitcomp    # Bit-Complement bisection stress workload
scripts\run_sim.bat cnn        # Pipelined Deep Learning CNN workload
```

Or manually:
```powershell
& 'D:\xilinx\Vivado\2023.1\bin\xvlog.bat' -work work rtl/*.v tb/tb_noc_dataset_driven.v
& 'D:\xilinx\Vivado\2023.1\bin\xelab.bat' -generic_top DATASET_FILE=\"dataset/uniform_random_1000.hex\" -top tb_noc_dataset_driven -snapshot dataset_sim -debug typical
& 'D:\xilinx\Vivado\2023.1\bin\xsim.bat' dataset_sim -R
```

