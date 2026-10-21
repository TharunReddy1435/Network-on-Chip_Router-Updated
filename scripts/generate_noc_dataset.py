#!/usr/bin/env python3
"""
==============================================================================
Script: generate_noc_dataset.py
Project: 5-Port Virtual-Channel Network-on-Chip (NoC) Router & 2x2 Mesh
Course: Data Networks (DN) Course Project
Description: Synthesizes realistic verification & benchmark traffic datasets
             for cycle-accurate Verilog simulation and performance evaluation.
             Generates:
               1. Uniform Random Workload (dataset/uniform_random_1000)
               2. Hotspot Memory Controller Workload (dataset/hotspot_memory_1000)
               3. Matrix Transpose Workload (dataset/transpose_1000)
               4. Bit-Complement Bisection Stress Workload (dataset/bit_complement_1000)
               5. Pipelined Deep Learning CNN Layer Workload (dataset/cnn_resnet_layer_traffic)
             
             Output Formats:
               - .csv : Comprehensive human-readable tabular dataset with packet metadata
               - .hex : Verilog $readmemh compatible 32-bit word format:
                        [31:20] inject_cycle (12-bit)
                        [19:18] src_pe (2-bit)
                        [17:16] reserved (2-bit)
                        [15:0]  16-bit NoC Flit ({ftype[1:0], dx[1:0], dy[1:0], sx[1:0], sy[1:0], vc[0], payload[4:0]})
==============================================================================
"""

import os
import random

# Coordinates mapping for 2x2 Mesh
PE_COORDS = {
    0: (0, 0),
    1: (1, 0),
    2: (0, 1),
    3: (1, 1)
}

COORD_TO_PE = {v: k for k, v in PE_COORDS.items()}

# Flit types
FTYPE_SINGLE = 0b11 # 3
FTYPE_HEAD   = 0b01 # 1
FTYPE_BODY   = 0b00 # 0
FTYPE_TAIL   = 0b10 # 2

def pack_flit(ftype, dx, dy, sx, sy, vc, payload):
    """Packs fields into a 16-bit NoC flit."""
    return ((ftype & 0x3) << 14) | \
           ((dx & 0x3) << 12) | \
           ((dy & 0x3) << 10) | \
           ((sx & 0x3) << 8) | \
           ((sy & 0x3) << 6) | \
           ((vc & 0x1) << 5) | \
           (payload & 0x1F)

def pack_trace_word(cycle, src_pe, flit_16):
    """Packs cycle, source PE, and 16-bit flit into a 32-bit trace word."""
    return ((cycle & 0xFFF) << 20) | \
           ((src_pe & 0x3) << 18) | \
           (flit_16 & 0xFFFF)

def write_dataset(base_name, entries, description):
    """Writes dataset to both CSV and HEX formats."""
    csv_file = f"{base_name}.csv"
    hex_file = f"{base_name}.hex"

    # Write CSV
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write("# " + description + "\n")
        f.write("entry_id,inject_cycle,src_pe,src_x,src_y,dest_pe,dest_x,dest_y,vc_id,flit_type,payload,hex_flit,hex_trace_word\n")
        for idx, e in enumerate(entries):
            ftype_str = {0b11: "SINGLE", 0b01: "HEAD", 0b00: "BODY", 0b10: "TAIL"}[e['ftype']]
            f.write(f"{idx},{e['cycle']},{e['src_pe']},{e['sx']},{e['sy']},{e['dest_pe']},{e['dx']},{e['dy']},{e['vc']},{ftype_str},{e['payload']},0x{e['flit']:04X},0x{e['trace_word']:08X}\n")

    # Write HEX for Verilog $readmemh
    with open(hex_file, 'w', encoding='utf-8') as f:
        for e in entries:
            f.write(f"{e['trace_word']:08X}\n")

    print(f"  [OK] Generated {len(entries)} flits -> {csv_file} & {hex_file}")

def generate_uniform_random(num_packets=1000, seed=42):
    random.seed(seed)
    entries = []
    current_cycle = 5
    for i in range(num_packets):
        # Staggered injection across 4 PEs
        src_pe = random.choice([0, 1, 2, 3])
        dest_pe = random.choice([p for p in [0, 1, 2, 3] if p != src_pe])
        sx, sy = PE_COORDS[src_pe]
        dx, dy = PE_COORDS[dest_pe]
        vc = random.choice([0, 1])
        payload = (i + 1) & 0x1F
        ftype = FTYPE_SINGLE

        current_cycle += random.choice([1, 2, 3]) # average load ~0.50
        flit = pack_flit(ftype, dx, dy, sx, sy, vc, payload)
        trace_word = pack_trace_word(current_cycle, src_pe, flit)

        entries.append({
            'cycle': current_cycle, 'src_pe': src_pe, 'dest_pe': dest_pe,
            'sx': sx, 'sy': sy, 'dx': dx, 'dy': dy, 'vc': vc,
            'payload': payload, 'ftype': ftype, 'flit': flit, 'trace_word': trace_word
        })
    return entries

def generate_hotspot(num_packets=1000, hotspot_pe=3, hotspot_ratio=0.45, seed=101):
    random.seed(seed)
    entries = []
    current_cycle = 5
    for i in range(num_packets):
        src_pe = random.choice([0, 1, 2, 3])
        if random.random() < hotspot_ratio and src_pe != hotspot_pe:
            dest_pe = hotspot_pe
        else:
            candidates = [p for p in [0, 1, 2, 3] if p != src_pe]
            dest_pe = random.choice(candidates)

        sx, sy = PE_COORDS[src_pe]
        dx, dy = PE_COORDS[dest_pe]
        vc = random.choice([0, 1])
        payload = (i + 1) & 0x1F
        ftype = FTYPE_SINGLE

        current_cycle += random.choice([1, 2, 2, 3])
        flit = pack_flit(ftype, dx, dy, sx, sy, vc, payload)
        trace_word = pack_trace_word(current_cycle, src_pe, flit)

        entries.append({
            'cycle': current_cycle, 'src_pe': src_pe, 'dest_pe': dest_pe,
            'sx': sx, 'sy': sy, 'dx': dx, 'dy': dy, 'vc': vc,
            'payload': payload, 'ftype': ftype, 'flit': flit, 'trace_word': trace_word
        })
    return entries

def generate_transpose(num_packets=1000, seed=202):
    random.seed(seed)
    entries = []
    current_cycle = 5
    # Matrix Transpose mapping: (x, y) -> (y, x)
    # (0,0) -> (1,1) [cross-diagonal], (1,0) -> (0,1), (0,1) -> (1,0), (1,1) -> (0,0)
    transpose_map = {0: 3, 1: 2, 2: 1, 3: 0}

    for i in range(num_packets):
        src_pe = random.choice([0, 1, 2, 3])
        dest_pe = transpose_map[src_pe]
        sx, sy = PE_COORDS[src_pe]
        dx, dy = PE_COORDS[dest_pe]
        vc = (i % 2) # Alternate VCs to balance lanes
        payload = (i + 1) & 0x1F
        ftype = FTYPE_SINGLE

        current_cycle += random.choice([1, 2, 3])
        flit = pack_flit(ftype, dx, dy, sx, sy, vc, payload)
        trace_word = pack_trace_word(current_cycle, src_pe, flit)

        entries.append({
            'cycle': current_cycle, 'src_pe': src_pe, 'dest_pe': dest_pe,
            'sx': sx, 'sy': sy, 'dx': dx, 'dy': dy, 'vc': vc,
            'payload': payload, 'ftype': ftype, 'flit': flit, 'trace_word': trace_word
        })
    return entries

def generate_bit_complement(num_packets=1000, seed=303):
    random.seed(seed)
    entries = []
    current_cycle = 5
    # Bit complement: dx = ~sx, dy = ~sy (in 1-bit binary)
    # (0,0) -> (1,1) [PE0 -> PE3]
    # (1,0) -> (0,1) [PE1 -> PE2]
    # (0,1) -> (1,0) [PE2 -> PE1]
    # (1,1) -> (0,0) [PE3 -> PE0]
    complement_map = {0: 3, 1: 2, 2: 1, 3: 0}

    for i in range(num_packets):
        src_pe = random.choice([0, 1, 2, 3])
        dest_pe = complement_map[src_pe]
        sx, sy = PE_COORDS[src_pe]
        dx, dy = PE_COORDS[dest_pe]
        vc = random.choice([0, 1])
        payload = (i * 3 + 7) & 0x1F
        ftype = FTYPE_SINGLE

        current_cycle += random.choice([1, 2, 2, 3])
        flit = pack_flit(ftype, dx, dy, sx, sy, vc, payload)
        trace_word = pack_trace_word(current_cycle, src_pe, flit)

        entries.append({
            'cycle': current_cycle, 'src_pe': src_pe, 'dest_pe': dest_pe,
            'sx': sx, 'sy': sy, 'dx': dx, 'dy': dy, 'vc': vc,
            'payload': payload, 'ftype': ftype, 'flit': flit, 'trace_word': trace_word
        })
    return entries

def generate_cnn_resnet_workload(num_packets=1000, seed=404):
    """
    Simulates pipelined spatial CNN inference on 4 processing elements:
      PE0: Input activation stream & Conv1 filter
      PE1: Conv2 & Depthwise spatial convolution
      PE2: Residual Skip-Connection Addition & MaxPooling
      PE3: Dense Fully-Connected Layer & Softmax Classification
    Communication patterns feature:
      - 70% forward activation streaming: PE0->PE1, PE1->PE2, PE2->PE3
      - 15% skip/residual connections: PE0->PE2
      - 15% backward parameter updates & gradient/sync pulses: PE3->PE0, PE3->PE1
      - Multi-flit wormhole bursts (Head -> Body -> Tail)
    """
    random.seed(seed)
    entries = []
    current_cycle = 5
    pkt_id = 0

    while len(entries) < num_packets:
        r = random.random()
        if r < 0.70:
            # Sequential pipeline stage forwarding
            stage = random.choice([(0, 1), (1, 2), (2, 3)])
            src_pe, dest_pe = stage
        elif r < 0.85:
            # Residual connection bypass
            src_pe, dest_pe = (0, 2)
        else:
            # Sync pulse
            src_pe = 3
            dest_pe = random.choice([0, 1, 2])

        sx, sy = PE_COORDS[src_pe]
        dx, dy = PE_COORDS[dest_pe]
        vc = 1 if (src_pe, dest_pe) == (0, 2) else 0 # Priority VC1 for residual bypass!

        # 30% are 3-flit wormhole packets (Head, Body, Tail), 70% Single flits
        is_wormhole = random.random() < 0.30 and (len(entries) + 3 <= num_packets)

        if is_wormhole:
            # Head flit
            pkt_id += 1
            current_cycle += random.choice([2, 3, 4])
            flit_h = pack_flit(FTYPE_HEAD, dx, dy, sx, sy, vc, pkt_id & 0x1F)
            trace_h = pack_trace_word(current_cycle, src_pe, flit_h)
            entries.append({
                'cycle': current_cycle, 'src_pe': src_pe, 'dest_pe': dest_pe,
                'sx': sx, 'sy': sy, 'dx': dx, 'dy': dy, 'vc': vc,
                'payload': pkt_id & 0x1F, 'ftype': FTYPE_HEAD, 'flit': flit_h, 'trace_word': trace_h
            })

            # Body flit
            current_cycle += 1
            flit_b = pack_flit(FTYPE_BODY, dx, dy, sx, sy, vc, (pkt_id + 1) & 0x1F)
            trace_b = pack_trace_word(current_cycle, src_pe, flit_b)
            entries.append({
                'cycle': current_cycle, 'src_pe': src_pe, 'dest_pe': dest_pe,
                'sx': sx, 'sy': sy, 'dx': dx, 'dy': dy, 'vc': vc,
                'payload': (pkt_id + 1) & 0x1F, 'ftype': FTYPE_BODY, 'flit': flit_b, 'trace_word': trace_b
            })

            # Tail flit
            current_cycle += 1
            flit_t = pack_flit(FTYPE_TAIL, dx, dy, sx, sy, vc, (pkt_id + 2) & 0x1F)
            trace_t = pack_trace_word(current_cycle, src_pe, flit_t)
            entries.append({
                'cycle': current_cycle, 'src_pe': src_pe, 'dest_pe': dest_pe,
                'sx': sx, 'sy': sy, 'dx': dx, 'dy': dy, 'vc': vc,
                'payload': (pkt_id + 2) & 0x1F, 'ftype': FTYPE_TAIL, 'flit': flit_t, 'trace_word': trace_t
            })
        else:
            pkt_id += 1
            current_cycle += random.choice([1, 2, 3])
            flit = pack_flit(FTYPE_SINGLE, dx, dy, sx, sy, vc, pkt_id & 0x1F)
            trace = pack_trace_word(current_cycle, src_pe, flit)
            entries.append({
                'cycle': current_cycle, 'src_pe': src_pe, 'dest_pe': dest_pe,
                'sx': sx, 'sy': sy, 'dx': dx, 'dy': dy, 'vc': vc,
                'payload': pkt_id & 0x1F, 'ftype': FTYPE_SINGLE, 'flit': flit, 'trace_word': trace
            })

    return entries[:num_packets]

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Network-on-Chip (NoC) Benchmark Dataset Generator")
    parser.add_argument("--packets", type=int, default=1000, help="Number of flits to synthesize per dataset (default: 1000)")
    parser.add_argument("--workload", type=str, default="all", choices=["all", "uniform", "hotspot", "transpose", "bitcomp", "cnn"],
                        help="Specific workload to synthesize (default: all)")
    parser.add_argument("--outdir", type=str, default=None, help="Target output directory (default: ../dataset)")
    args = parser.parse_args()

    default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dataset")
    target_dir = args.outdir if args.outdir else default_dir
    os.makedirs(target_dir, exist_ok=True)

    num_pkts = args.packets
    print("=" * 76)
    print("  NETWORK-ON-CHIP (NoC) DATASET GENERATOR")
    print(f"  Target Destination Directory: [{os.path.abspath(target_dir)}]")
    print(f"  Trace Packet Count per Workload: [{num_pkts}]")
    print("=" * 76)

    # 1. Uniform Random Workload
    if args.workload in ["all", "uniform"]:
        print(f"\n--> 1. Generating Uniform Random Dataset ({num_pkts} flits)...")
        d_uniform = generate_uniform_random(num_pkts, seed=42)
        write_dataset(
            os.path.join(target_dir, "uniform_random_1000"),
            d_uniform,
            f"Workload: Uniform Random Synthetic Traffic Dataset for 2x2 Mesh NoC ({num_pkts} flits)"
        )

    # 2. Hotspot Memory Controller Workload
    if args.workload in ["all", "hotspot"]:
        print(f"\n--> 2. Generating Hotspot Memory Controller Dataset ({num_pkts} flits)...")
        d_hotspot = generate_hotspot(num_pkts, hotspot_pe=3, hotspot_ratio=0.45, seed=101)
        write_dataset(
            os.path.join(target_dir, "hotspot_memory_1000"),
            d_hotspot,
            f"Workload: Hotspot Traffic Dataset (45% Concentrated on PE3 Memory Controller, {num_pkts} flits)"
        )

    # 3. Matrix Transpose Workload
    if args.workload in ["all", "transpose"]:
        print(f"\n--> 3. Generating Matrix Transpose Dataset ({num_pkts} flits)...")
        d_transpose = generate_transpose(num_pkts, seed=202)
        write_dataset(
            os.path.join(target_dir, "transpose_1000"),
            d_transpose,
            f"Workload: Matrix Transpose Permutation Dataset for 2x2 Mesh NoC ({num_pkts} flits)"
        )

    # 4. Bit-Complement Workload
    if args.workload in ["all", "bitcomp"]:
        print(f"\n--> 4. Generating Bit-Complement Dataset ({num_pkts} flits)...")
        d_bitcomp = generate_bit_complement(num_pkts, seed=303)
        write_dataset(
            os.path.join(target_dir, "bit_complement_1000"),
            d_bitcomp,
            f"Workload: Bit-Complement Maximum Bisection Traffic Dataset ({num_pkts} flits)"
        )

    # 5. Pipelined Deep Learning CNN Layer Workload
    if args.workload in ["all", "cnn"]:
        print(f"\n--> 5. Generating Pipelined CNN ResNet Workload ({num_pkts} flits)...")
        d_cnn = generate_cnn_resnet_workload(num_pkts, seed=404)
        write_dataset(
            os.path.join(target_dir, "cnn_resnet_layer_traffic"),
            d_cnn,
            f"Workload: 4-Tile Deep Learning CNN Layer Activation & Residual Bypass Dataset ({num_pkts} flits)"
        )

    print("\n" + "=" * 76)
    print("  Datasets Successfully Synthesized in .csv and .hex Formats!")
    print("=" * 76 + "\n")

if __name__ == '__main__':
    main()

