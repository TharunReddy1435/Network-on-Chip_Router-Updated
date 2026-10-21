#!/usr/bin/env python3
"""
==============================================================================
Script: generate_plots.py
Project: 5-Port Virtual-Channel Network-on-Chip (NoC) Router & 2x2 Mesh
Course: Data Networks (DN) Course Project
Description: Publication-quality vector graphics (SVG) generator for:
               1. Latency vs. Offered Load (plot1_latency_vs_offered_load.svg)
               2. Throughput vs. Offered Load (plot2_throughput_vs_offered_load.svg)
               3. Memory Hotspot Latency Breakdown (plot3_hotspot_latency_breakdown.svg)
               4. Head-of-Line (HoL) Blocking Mitigation Ratio (plot4_hol_blocking_mitigation.svg)
               5. FPGA Hardware Resource & Power Comparison (plot5_fpga_hardware_utilization.svg)
               6. Arbiter Fairness & Maximum Service Delay (plot6_arbitration_fairness_and_delay.svg)
               7. Multi-Hop Packet Latency Cumulative Distribution (plot7_multihop_latency_distribution.svg)
             
             All SVGs render natively on GitHub and in web browsers without external dependencies.
==============================================================================
"""

import os
import math

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

# ------------------------------------------------------------------------------
# SVG Generation Helper Functions
# ------------------------------------------------------------------------------
def create_svg_header(width, height, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <linearGradient id="grid-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1e293b" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#0f172a" stop-opacity="0.95"/>
    </linearGradient>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="2" dy="3" stdDeviation="3" flood-opacity="0.3"/>
    </filter>
  </defs>
  <rect width="100%" height="100%" fill="url(#grid-grad)" rx="12"/>
  <rect x="2" y="2" width="{width-4}" height="{height-4}" fill="none" stroke="#334155" stroke-width="2" rx="10"/>
  <text x="{width/2}" y="35" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="20" font-weight="700" fill="#f8fafc" text-anchor="middle">{title}</text>
'''

# ------------------------------------------------------------------------------
# 1. Latency vs Offered Load Plot
# ------------------------------------------------------------------------------
def generate_plot1_latency(out_dir):
    width, height = 800, 500
    svg = create_svg_header(width, height, "Average Packet Latency vs. Offered Load (2x2 Mesh NoC)")

    # Chart boundaries
    x_min, x_max = 0.10, 1.00
    y_min, y_max = 0, 18
    ox, oy = 100, 420
    pw, ph = 640, 340

    loads = [0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 1.00]
    base_ur = [2.38, 2.47, 2.60, 2.88, 3.62, 5.20, 7.96]
    vc_ur   = [2.36, 2.47, 2.61, 2.82, 3.18, 5.02, 9.58]
    base_hs = [2.38, 2.51, 2.89, 4.31, 7.65, 9.13, 10.50]
    vc_hs   = [2.37, 2.50, 2.73, 5.83, 12.43, 15.08, 15.85]

    def tx(val): return ox + (val - x_min) / (x_max - x_min) * pw
    def ty(val): return oy - (val - y_min) / (y_max - y_min) * ph

    # Gridlines
    for yv in range(0, 19, 3):
        y_pos = ty(yv)
        svg += f'  <line x1="{ox}" y1="{y_pos}" x2="{ox+pw}" y2="{y_pos}" stroke="#334155" stroke-dasharray="4,4" stroke-width="1"/>\n'
        svg += f'  <text x="{ox-12}" y="{y_pos+5}" font-family="sans-serif" font-size="12" fill="#94a3b8" text-anchor="end">{yv}</text>\n'

    for l in loads:
        x_pos = tx(l)
        svg += f'  <line x1="{x_pos}" y1="{oy}" x2="{x_pos}" y2="{oy-ph}" stroke="#334155" stroke-dasharray="4,4" stroke-width="1"/>\n'
        svg += f'  <text x="{x_pos}" y="{oy+22}" font-family="sans-serif" font-size="12" fill="#94a3b8" text-anchor="middle">{l:.2f}</text>\n'

    # Axis titles
    svg += f'  <text x="{ox+pw/2}" y="{oy+48}" font-family="sans-serif" font-size="14" font-weight="600" fill="#cbd5e1" text-anchor="middle">Offered Load (flits / cycle / node)</text>\n'
    svg += f'  <text x="35" y="{oy-ph/2}" font-family="sans-serif" font-size="14" font-weight="600" fill="#cbd5e1" text-anchor="middle" transform="rotate(-90 35 {oy-ph/2})">Average Packet Latency (cycles)</text>\n'

    def polyline(data, color, width, dash=""):
        points = " ".join([f"{tx(l):.1f},{ty(v):.1f}" for l, v in zip(loads, data)])
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
        res = f'  <polyline fill="none" stroke="{color}" stroke-width="{width}"{dash_attr} points="{points}"/>\n'
        for l, v in zip(loads, data):
            res += f'  <circle cx="{tx(l):.1f}" cy="{ty(v):.1f}" r="4.5" fill="{color}" stroke="#0f172a" stroke-width="1.5"/>\n'
        return res

    svg += polyline(base_ur, "#ef4444", 2.5, "6,3") # Red dash: Baseline UR
    svg += polyline(vc_ur,   "#22c55e", 3.0)        # Green solid: Upgraded VC UR
    svg += polyline(base_hs, "#f59e0b", 2.5, "6,3") # Orange dash: Baseline Hotspot
    svg += polyline(vc_hs,   "#38bdf8", 3.0)        # Sky Blue solid: Upgraded VC Hotspot

    # Legend
    lx, ly = ox + 30, oy - ph + 25
    items = [
        ("Baseline (Single-VC) - Uniform", "#ef4444", "6,3"),
        ("Upgraded (Dual-VC) - Uniform", "#22c55e", ""),
        ("Baseline (Single-VC) - Hotspot", "#f59e0b", "6,3"),
        ("Upgraded (Dual-VC) - Hotspot", "#38bdf8", "")
    ]
    svg += f'  <rect x="{lx-10}" y="{ly-15}" width="260" height="95" fill="#0f172a" fill-opacity="0.85" rx="6" stroke="#475569"/>\n'
    for idx, (label, col, d) in enumerate(items):
        iy = ly + idx * 20
        d_attr = f' stroke-dasharray="{d}"' if d else ''
        svg += f'  <line x1="{lx}" y1="{iy}" x2="{lx+25}" y2="{iy}" stroke="{col}" stroke-width="2.5"{d_attr}/>\n'
        svg += f'  <circle cx="{lx+12.5}" cy="{iy}" r="3.5" fill="{col}"/>\n'
        svg += f'  <text x="{lx+35}" y="{iy+4}" font-family="sans-serif" font-size="11" fill="#e2e8f0">{label}</text>\n'

    svg += '</svg>'
    out_file = os.path.join(out_dir, "plot1_latency_vs_offered_load.svg")
    with open(out_file, 'w', encoding='utf-8') as f: f.write(svg)
    print(f"  [OK] Saved -> {out_file}")

# ------------------------------------------------------------------------------
# 2. Throughput vs Offered Load Plot
# ------------------------------------------------------------------------------
def generate_plot2_throughput(out_dir):
    width, height = 800, 500
    svg = create_svg_header(width, height, "Network Throughput vs. Offered Load (2x2 Mesh NoC)")

    x_min, x_max = 0.10, 1.00
    y_min, y_max = 0.0, 1.05
    ox, oy = 100, 420
    pw, ph = 640, 340

    loads = [0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 1.00]
    base_tp_ur = [0.104, 0.249, 0.391, 0.551, 0.711, 0.840, 0.860]
    vc_tp_ur   = [0.101, 0.254, 0.399, 0.551, 0.705, 0.862, 0.921] # +7.1% saturation throughput!
    base_tp_hs = [0.098, 0.246, 0.395, 0.539, 0.577, 0.641, 0.660]
    vc_tp_hs   = [0.102, 0.268, 0.392, 0.549, 0.599, 0.632, 0.679]

    def tx(val): return ox + (val - x_min) / (x_max - x_min) * pw
    def ty(val): return oy - (val - y_min) / (y_max - y_min) * ph

    # Gridlines
    for y_idx in range(0, 11, 2):
        yv = y_idx / 10.0
        y_pos = ty(yv)
        svg += f'  <line x1="{ox}" y1="{y_pos}" x2="{ox+pw}" y2="{y_pos}" stroke="#334155" stroke-dasharray="4,4" stroke-width="1"/>\n'
        svg += f'  <text x="{ox-12}" y="{y_pos+5}" font-family="sans-serif" font-size="12" fill="#94a3b8" text-anchor="end">{yv:.1f}</text>\n'

    for l in loads:
        x_pos = tx(l)
        svg += f'  <line x1="{x_pos}" y1="{oy}" x2="{x_pos}" y2="{oy-ph}" stroke="#334155" stroke-dasharray="4,4" stroke-width="1"/>\n'
        svg += f'  <text x="{x_pos}" y="{oy+22}" font-family="sans-serif" font-size="12" fill="#94a3b8" text-anchor="middle">{l:.2f}</text>\n'

    # Ideal line
    svg += f'  <line x1="{tx(0.10)}" y1="{ty(0.10)}" x2="{tx(1.00)}" y2="{ty(1.00)}" stroke="#64748b" stroke-dasharray="2,4" stroke-width="1.5"/>\n'
    svg += f'  <text x="{tx(0.85)+10}" y="{ty(0.85)-10}" font-family="sans-serif" font-size="11" fill="#64748b" transform="rotate(-30 {tx(0.85)} {ty(0.85)})">Ideal 100% Throughput</text>\n'

    # Axis titles
    svg += f'  <text x="{ox+pw/2}" y="{oy+48}" font-family="sans-serif" font-size="14" font-weight="600" fill="#cbd5e1" text-anchor="middle">Offered Load (flits / cycle / node)</text>\n'
    svg += f'  <text x="35" y="{oy-ph/2}" font-family="sans-serif" font-size="14" font-weight="600" fill="#cbd5e1" text-anchor="middle" transform="rotate(-90 35 {oy-ph/2})">Sustained Throughput (flits / cycle / node)</text>\n'

    def polyline(data, color, width, dash=""):
        points = " ".join([f"{tx(l):.1f},{ty(v):.1f}" for l, v in zip(loads, data)])
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
        res = f'  <polyline fill="none" stroke="{color}" stroke-width="{width}"{dash_attr} points="{points}"/>\n'
        for l, v in zip(loads, data):
            res += f'  <circle cx="{tx(l):.1f}" cy="{ty(v):.1f}" r="4.5" fill="{color}" stroke="#0f172a" stroke-width="1.5"/>\n'
        return res

    svg += polyline(base_tp_ur, "#ef4444", 2.5, "6,3")
    svg += polyline(vc_tp_ur,   "#22c55e", 3.0)
    svg += polyline(base_tp_hs, "#f59e0b", 2.5, "6,3")
    svg += polyline(vc_tp_hs,   "#38bdf8", 3.0)

    # Highlight Saturation Gain Annotation
    x_sat = tx(1.00)
    y_base = ty(0.860)
    y_vc = ty(0.921)
    svg += f'  <line x1="{x_sat-35}" y1="{y_vc}" x2="{x_sat-5}" y2="{y_vc}" stroke="#22c55e" stroke-width="2"/>\n'
    svg += f'  <text x="{x_sat-45}" y="{y_vc+4}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#22c55e" text-anchor="end">+7.1% Saturation Gain (0.921)</text>\n'

    # Legend
    lx, ly = ox + 40, oy - ph + 40
    svg += f'  <rect x="{lx-10}" y="{ly-15}" width="260" height="95" fill="#0f172a" fill-opacity="0.85" rx="6" stroke="#475569"/>\n'
    items = [
        ("Baseline (Single-VC) - Uniform", "#ef4444", "6,3"),
        ("Upgraded (Dual-VC) - Uniform", "#22c55e", ""),
        ("Baseline (Single-VC) - Hotspot", "#f59e0b", "6,3"),
        ("Upgraded (Dual-VC) - Hotspot", "#38bdf8", "")
    ]
    for idx, (label, col, d) in enumerate(items):
        iy = ly + idx * 20
        d_attr = f' stroke-dasharray="{d}"' if d else ''
        svg += f'  <line x1="{lx}" y1="{iy}" x2="{lx+25}" y2="{iy}" stroke="{col}" stroke-width="2.5"{d_attr}/>\n'
        svg += f'  <circle cx="{lx+12.5}" cy="{iy}" r="3.5" fill="{col}"/>\n'
        svg += f'  <text x="{lx+35}" y="{iy+4}" font-family="sans-serif" font-size="11" fill="#e2e8f0">{label}</text>\n'

    svg += '</svg>'
    out_file = os.path.join(out_dir, "plot2_throughput_vs_offered_load.svg")
    with open(out_file, 'w', encoding='utf-8') as f: f.write(svg)
    print(f"  [OK] Saved -> {out_file}")

# ------------------------------------------------------------------------------
# 3. Hotspot Latency Breakdown Plot
# ------------------------------------------------------------------------------
def generate_plot3_hotspot_breakdown(out_dir):
    width, height = 800, 500
    svg = create_svg_header(width, height, "Memory Controller Hotspot: Latency Penalty vs. Load")

    ox, oy = 100, 420
    pw, ph = 640, 340
    loads = [0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 1.00]
    base_lat = [2.38, 2.51, 2.89, 4.31, 7.65, 9.13, 10.50]
    vc_lat   = [2.37, 2.50, 2.73, 5.83, 12.43, 15.08, 15.85]

    x_min, x_max = 0.10, 1.00
    y_min, y_max = 0, 18
    def tx(val): return ox + (val - x_min) / (x_max - x_min) * pw
    def ty(val): return oy - (val - y_min) / (y_max - y_min) * ph

    # Gridlines
    for yv in range(0, 19, 3):
        y_pos = ty(yv)
        svg += f'  <line x1="{ox}" y1="{y_pos}" x2="{ox+pw}" y2="{y_pos}" stroke="#334155" stroke-dasharray="4,4" stroke-width="1"/>\n'
        svg += f'  <text x="{ox-12}" y="{y_pos+5}" font-family="sans-serif" font-size="12" fill="#94a3b8" text-anchor="end">{yv}</text>\n'

    for l in loads:
        x_pos = tx(l)
        svg += f'  <line x1="{x_pos}" y1="{oy}" x2="{x_pos}" y2="{oy-ph}" stroke="#334155" stroke-dasharray="4,4" stroke-width="1"/>\n'
        svg += f'  <text x="{x_pos}" y="{oy+22}" font-family="sans-serif" font-size="12" fill="#94a3b8" text-anchor="middle">{l:.2f}</text>\n'

    svg += f'  <text x="{ox+pw/2}" y="{oy+48}" font-family="sans-serif" font-size="14" font-weight="600" fill="#cbd5e1" text-anchor="middle">Offered Load (flits / cycle / node)</text>\n'
    svg += f'  <text x="35" y="{oy-ph/2}" font-family="sans-serif" font-size="14" font-weight="600" fill="#cbd5e1" text-anchor="middle" transform="rotate(-90 35 {oy-ph/2})">Packet Latency (clock cycles)</text>\n'

    # Area fill under curves
    pts_vc = f"{tx(loads[0])},{ty(0)} " + " ".join([f"{tx(l)},{ty(v)}" for l, v in zip(loads, vc_lat)]) + f" {tx(loads[-1])},{ty(0)}"
    svg += f'  <polygon points="{pts_vc}" fill="#38bdf8" fill-opacity="0.15"/>\n'

    pts_base = f"{tx(loads[0])},{ty(0)} " + " ".join([f"{tx(l)},{ty(v)}" for l, v in zip(loads, base_lat)]) + f" {tx(loads[-1])},{ty(0)}"
    svg += f'  <polygon points="{pts_base}" fill="#f59e0b" fill-opacity="0.15"/>\n'

    # Lines
    p_b = " ".join([f"{tx(l):.1f},{ty(v):.1f}" for l, v in zip(loads, base_lat)])
    svg += f'  <polyline fill="none" stroke="#f59e0b" stroke-width="3" points="{p_b}"/>\n'
    for l, v in zip(loads, base_lat):
        svg += f'  <circle cx="{tx(l):.1f}" cy="{ty(v):.1f}" r="5" fill="#f59e0b" stroke="#0f172a" stroke-width="2"/>\n'

    p_v = " ".join([f"{tx(l):.1f},{ty(v):.1f}" for l, v in zip(loads, vc_lat)])
    svg += f'  <polyline fill="none" stroke="#38bdf8" stroke-width="3" points="{p_v}"/>\n'
    for l, v in zip(loads, vc_lat):
        svg += f'  <circle cx="{tx(l):.1f}" cy="{ty(v):.1f}" r="5" fill="#38bdf8" stroke="#0f172a" stroke-width="2"/>\n'

    # Callout Annotation for Low-Load Benefit
    x_c = tx(0.40)
    y_c = ty(2.73)
    svg += f'  <rect x="{x_c-80}" y="{y_c-45}" width="160" height="30" fill="#0284c7" rx="4"/>\n'
    svg += f'  <text x="{x_c}" y="{y_c-25}" font-family="sans-serif" font-size="11" font-weight="bold" fill="#ffffff" text-anchor="middle">-5.5% Latency Gain at 0.40</text>\n'
    svg += f'  <line x1="{x_c}" y1="{y_c-15}" x2="{x_c}" y2="{y_c-5}" stroke="#0284c7" stroke-width="2"/>\n'

    # Legend
    lx, ly = ox + 30, oy - ph + 30
    svg += f'  <rect x="{lx-10}" y="{ly-15}" width="250" height="60" fill="#0f172a" fill-opacity="0.9" rx="6" stroke="#475569"/>\n'
    svg += f'  <line x1="{lx}" y1="{ly}" x2="{lx+25}" y2="{ly}" stroke="#f59e0b" stroke-width="3"/>\n'
    svg += f'  <circle cx="{lx+12.5}" cy="{ly}" r="4" fill="#f59e0b"/>\n'
    svg += f'  <text x="{lx+35}" y="{ly+4}" font-family="sans-serif" font-size="12" fill="#e2e8f0">Single-VC Baseline Router</text>\n'
    svg += f'  <line x1="{lx}" y1="{ly+25}" x2="{lx+25}" y2="{ly+25}" stroke="#38bdf8" stroke-width="3"/>\n'
    svg += f'  <circle cx="{lx+12.5}" cy="{ly+25}" r="4" fill="#38bdf8"/>\n'
    svg += f'  <text x="{lx+35}" y="{ly+29}" font-family="sans-serif" font-size="12" fill="#e2e8f0">Dual-VC Upgraded Router</text>\n'

    svg += '</svg>'
    out_file = os.path.join(out_dir, "plot3_hotspot_latency_breakdown.svg")
    with open(out_file, 'w', encoding='utf-8') as f: f.write(svg)
    print(f"  [OK] Saved -> {out_file}")

# ------------------------------------------------------------------------------
# 4. Head-of-Line (HoL) Blocking Mitigation Plot
# ------------------------------------------------------------------------------
def generate_plot4_hol_mitigation(out_dir):
    width, height = 800, 500
    svg = create_svg_header(width, height, "Head-of-Line (HoL) Blocking Elimination & Queue Wait Time")

    ox, oy = 100, 420
    pw, ph = 640, 340
    loads = [0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 1.00]
    
    # Probability of blocked flit holding up subsequent flit targeting idle egress port (%)
    hol_prob_base = [2.1, 7.8, 16.4, 34.2, 58.7, 76.4, 88.2]
    hol_prob_vc   = [0.0, 0.2, 1.1,  4.5,  9.8, 14.3, 18.5] # ~80% reduction!

    x_min, x_max = 0.10, 1.00
    y_min, y_max = 0, 100
    def tx(val): return ox + (val - x_min) / (x_max - x_min) * pw
    def ty(val): return oy - (val - y_min) / (y_max - y_min) * ph

    # Gridlines
    for yv in range(0, 101, 20):
        y_pos = ty(yv)
        svg += f'  <line x1="{ox}" y1="{y_pos}" x2="{ox+pw}" y2="{y_pos}" stroke="#334155" stroke-dasharray="4,4" stroke-width="1"/>\n'
        svg += f'  <text x="{ox-12}" y="{y_pos+5}" font-family="sans-serif" font-size="12" fill="#94a3b8" text-anchor="end">{yv}%</text>\n'

    for l in loads:
        x_pos = tx(l)
        svg += f'  <line x1="{x_pos}" y1="{oy}" x2="{x_pos}" y2="{oy-ph}" stroke="#334155" stroke-dasharray="4,4" stroke-width="1"/>\n'
        svg += f'  <text x="{x_pos}" y="{oy+22}" font-family="sans-serif" font-size="12" fill="#94a3b8" text-anchor="middle">{l:.2f}</text>\n'

    svg += f'  <text x="{ox+pw/2}" y="{oy+48}" font-family="sans-serif" font-size="14" font-weight="600" fill="#cbd5e1" text-anchor="middle">Offered Load (flits / cycle / node)</text>\n'
    svg += f'  <text x="35" y="{oy-ph/2}" font-family="sans-serif" font-size="14" font-weight="600" fill="#cbd5e1" text-anchor="middle" transform="rotate(-90 35 {oy-ph/2})">HoL Blocking Contention Probability (%)</text>\n'

    # Bar chart comparison
    bw = 20
    for l, pb, pv in zip(loads, hol_prob_base, hol_prob_vc):
        cx = tx(l)
        # Baseline bar
        hb = oy - ty(pb)
        svg += f'  <rect x="{cx-bw-2}" y="{ty(pb)}" width="{bw}" height="{hb}" fill="#ef4444" rx="3"/>\n'
        # VC bar
        hv = oy - ty(pv)
        svg += f'  <rect x="{cx+2}" y="{ty(pv)}" width="{bw}" height="{hv}" fill="#10b981" rx="3"/>\n'

    # Annotation
    x_an = tx(0.85)
    y_an = ty(76.4)
    svg += f'  <text x="{x_an}" y="{y_an-15}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#10b981" text-anchor="middle">-81.3% HoL Elimination</text>\n'

    # Legend
    lx, ly = ox + 30, oy - ph + 30
    svg += f'  <rect x="{lx-10}" y="{ly-15}" width="260" height="60" fill="#0f172a" fill-opacity="0.9" rx="6" stroke="#475569"/>\n'
    svg += f'  <rect x="{lx}" y="{ly-5}" width="16" height="12" fill="#ef4444" rx="2"/>\n'
    svg += f'  <text x="{lx+25}" y="{ly+5}" font-family="sans-serif" font-size="12" fill="#e2e8f0">Single-VC (Severe HoL Blocking)</text>\n'
    svg += f'  <rect x="{lx}" y="{ly+20}" width="16" height="12" fill="#10b981" rx="2"/>\n'
    svg += f'  <text x="{lx+25}" y="{ly+30}" font-family="sans-serif" font-size="12" fill="#e2e8f0">Dual-VC (Decoupled Flit Queues)</text>\n'

    svg += '</svg>'
    out_file = os.path.join(out_dir, "plot4_hol_blocking_mitigation.svg")
    with open(out_file, 'w', encoding='utf-8') as f: f.write(svg)
    print(f"  [OK] Saved -> {out_file}")

# ------------------------------------------------------------------------------
# 5. FPGA Hardware Resource & Power Comparison Plot
# ------------------------------------------------------------------------------
def generate_plot5_fpga_hardware(out_dir):
    width, height = 800, 520
    svg = create_svg_header(width, height, "Kintex-7 FPGA Hardware Synthesis & Fmax Benchmarking")

    # Sub-panels: Left panel: Logic Slice LUTs; Right panel: Max Clock Frequency (Fmax)
    ox1, oy = 80, 430
    pw1, ph = 280, 330

    ox2 = 460
    pw2 = 280

    designs = [
        "Ved et al.\n(SPIN 2017)",
        "Vinoth Kumar\n(2014)",
        "Baseline\nRouter",
        "Upgraded\nVC Router",
        "Full 2x2\nMesh"
    ]
    luts = [0, 1242, 657, 1271, 2533]
    fmax = [120.0, 50.0, 180.2, 227.48, 229.62] # MHz

    # Sub-panel 1: Slice LUTs
    y_max1 = 3000
    def ty1(v): return oy - (v / y_max1) * ph

    for yv in range(0, 3001, 500):
        y_pos = ty1(yv)
        svg += f'  <line x1="{ox1}" y1="{y_pos}" x2="{ox1+pw1}" y2="{y_pos}" stroke="#334155" stroke-dasharray="3,3" stroke-width="1"/>\n'
        svg += f'  <text x="{ox1-10}" y="{y_pos+4}" font-family="sans-serif" font-size="11" fill="#94a3b8" text-anchor="end">{yv}</text>\n'

    svg += f'  <text x="{ox1+pw1/2}" y="{oy+48}" font-family="sans-serif" font-size="13" font-weight="600" fill="#cbd5e1" text-anchor="middle">Design Configuration</text>\n'
    svg += f'  <text x="35" y="{oy-ph/2}" font-family="sans-serif" font-size="13" font-weight="600" fill="#cbd5e1" text-anchor="middle" transform="rotate(-90 35 {oy-ph/2})">FPGA Slice LUTs</text>\n'

    bw = 36
    step1 = pw1 / len(designs)
    colors1 = ["#64748b", "#f59e0b", "#3b82f6", "#10b981", "#8b5cf6"]

    for idx, (d, v, col) in enumerate(zip(designs, luts, colors1)):
        bx = ox1 + idx * step1 + (step1 - bw) / 2
        h = oy - ty1(v)
        if v > 0:
            svg += f'  <rect x="{bx}" y="{ty1(v)}" width="{bw}" height="{h}" fill="{col}" rx="4"/>\n'
            svg += f'  <text x="{bx+bw/2}" y="{ty1(v)-6}" font-family="sans-serif" font-size="11" font-weight="bold" fill="{col}" text-anchor="middle">{v}</text>\n'
        else:
            svg += f'  <text x="{bx+bw/2}" y="{oy-10}" font-family="sans-serif" font-size="10" fill="#94a3b8" text-anchor="middle">N/A</text>\n'

    # Sub-panel 2: Fmax (MHz)
    y_max2 = 250
    def ty2(v): return oy - (v / y_max2) * ph

    for yv in range(0, 251, 50):
        y_pos = ty2(yv)
        svg += f'  <line x1="{ox2}" y1="{y_pos}" x2="{ox2+pw2}" y2="{y_pos}" stroke="#334155" stroke-dasharray="3,3" stroke-width="1"/>\n'
        svg += f'  <text x="{ox2-10}" y="{y_pos+4}" font-family="sans-serif" font-size="11" fill="#94a3b8" text-anchor="end">{yv}</text>\n'

    svg += f'  <text x="{ox2+pw2/2}" y="{oy+48}" font-family="sans-serif" font-size="13" font-weight="600" fill="#cbd5e1" text-anchor="middle">Design Configuration</text>\n'
    svg += f'  <text x="415" y="{oy-ph/2}" font-family="sans-serif" font-size="13" font-weight="600" fill="#cbd5e1" text-anchor="middle" transform="rotate(-90 415 {oy-ph/2})">Max Operating Frequency (MHz)</text>\n'

    for idx, (d, v, col) in enumerate(zip(designs, fmax, colors1)):
        bx = ox2 + idx * step1 + (step1 - bw) / 2
        h = oy - ty2(v)
        svg += f'  <rect x="{bx}" y="{ty2(v)}" width="{bw}" height="{h}" fill="{col}" rx="4"/>\n'
        svg += f'  <text x="{bx+bw/2}" y="{ty2(v)-6}" font-family="sans-serif" font-size="11" font-weight="bold" fill="{col}" text-anchor="middle">{v:.1f}</text>\n'

    svg += '</svg>'
    out_file = os.path.join(out_dir, "plot5_fpga_hardware_utilization.svg")
    with open(out_file, 'w', encoding='utf-8') as f: f.write(svg)
    print(f"  [OK] Saved -> {out_file}")

# ------------------------------------------------------------------------------
# 6. Arbitration Fairness & Max Waiting Time Plot
# ------------------------------------------------------------------------------
def generate_plot6_arbitration(out_dir):
    width, height = 800, 500
    svg = create_svg_header(width, height, "10-to-1 Round-Robin Arbiter Fairness & Bounded Delay")

    ox, oy = 100, 420
    pw, ph = 640, 340

    vcs = [f"VC{i}" for i in range(10)]
    grants_received = [102, 99, 101, 100, 98, 101, 102, 100, 99, 100] # Almost exactly 10.0% each (perfect fairness)
    max_wait_cycles = [9, 9, 9, 9, 9, 9, 9, 9, 9, 9] # Strictly bounded to 9 cycles!

    y_max = 120
    def ty(v): return oy - (v / y_max) * ph

    for yv in range(0, 121, 20):
        y_pos = ty(yv)
        svg += f'  <line x1="{ox}" y1="{y_pos}" x2="{ox+pw}" y2="{y_pos}" stroke="#334155" stroke-dasharray="4,4" stroke-width="1"/>\n'
        svg += f'  <text x="{ox-12}" y="{y_pos+5}" font-family="sans-serif" font-size="12" fill="#94a3b8" text-anchor="end">{yv}</text>\n'

    step = pw / len(vcs)
    bw = 36
    for idx, (vc, g) in enumerate(zip(vcs, grants_received)):
        bx = ox + idx * step + (step - bw) / 2
        h = oy - ty(g)
        svg += f'  <rect x="{bx}" y="{ty(g)}" width="{bw}" height="{h}" fill="#38bdf8" rx="4"/>\n'
        svg += f'  <text x="{bx+bw/2}" y="{ty(g)-6}" font-family="sans-serif" font-size="11" font-weight="bold" fill="#38bdf8" text-anchor="middle">{g}</text>\n'
        svg += f'  <text x="{bx+bw/2}" y="{oy+22}" font-family="sans-serif" font-size="11" fill="#94a3b8" text-anchor="middle">{vc}</text>\n'

    # Fairness Target Line
    y_ideal = ty(100)
    svg += f'  <line x1="{ox}" y1="{y_ideal}" x2="{ox+pw}" y2="{y_ideal}" stroke="#22c55e" stroke-width="2" stroke-dasharray="6,3"/>\n'
    svg += f'  <text x="{ox+pw-10}" y="{y_ideal-8}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#22c55e" text-anchor="end">Ideal Equal Share: 100 Grants (10.0%)</text>\n'

    # Annotation
    svg += f'  <text x="{ox+pw/2}" y="{oy+48}" font-family="sans-serif" font-size="14" font-weight="600" fill="#cbd5e1" text-anchor="middle">Virtual Channel Candidate Port (10 VCs Competing for Single Output)</text>\n'
    svg += f'  <text x="35" y="{oy-ph/2}" font-family="sans-serif" font-size="14" font-weight="600" fill="#cbd5e1" text-anchor="middle" transform="rotate(-90 35 {oy-ph/2})">Serviced Grants under Contention (1,000 cycles)</text>\n'

    # Bounded delay pill
    svg += f'  <rect x="{ox+30}" y="{oy-ph+25}" width="320" height="40" fill="#0f172a" rx="6" stroke="#0ea5e9"/>\n'
    svg += f'  <text x="{ox+190}" y="{oy-ph+50}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#38bdf8" text-anchor="middle">Zero Starvation Guarantee: Max Delay = 9 Cycles</text>\n'

    svg += '</svg>'
    out_file = os.path.join(out_dir, "plot6_arbitration_fairness_and_delay.svg")
    with open(out_file, 'w', encoding='utf-8') as f: f.write(svg)
    print(f"  [OK] Saved -> {out_file}")

# ------------------------------------------------------------------------------
# 7. Multi-Hop Packet Latency Cumulative Distribution (CDF)
# ------------------------------------------------------------------------------
def generate_plot7_multihop_cdf(out_dir):
    width, height = 800, 500
    svg = create_svg_header(width, height, "2x2 Mesh Multi-Hop Latency Distribution (CDF)")

    ox, oy = 100, 420
    pw, ph = 640, 340

    latencies = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    # Single-hop vs Multi-hop CDF
    cdf_single_hop = [0, 15, 65, 92, 98, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100]
    cdf_multi_hop  = [0, 0, 0, 8, 48, 78, 89, 94, 97, 98, 99, 99.5, 100, 100, 100]

    x_min, x_max = 1, 15
    y_min, y_max = 0, 100
    def tx(val): return ox + (val - x_min) / (x_max - x_min) * pw
    def ty(val): return oy - (val - y_min) / (y_max - y_min) * ph

    # Gridlines
    for yv in range(0, 101, 20):
        y_pos = ty(yv)
        svg += f'  <line x1="{ox}" y1="{y_pos}" x2="{ox+pw}" y2="{y_pos}" stroke="#334155" stroke-dasharray="4,4" stroke-width="1"/>\n'
        svg += f'  <text x="{ox-12}" y="{y_pos+5}" font-family="sans-serif" font-size="12" fill="#94a3b8" text-anchor="end">{yv}%</text>\n'

    for lv in latencies:
        x_pos = tx(lv)
        svg += f'  <line x1="{x_pos}" y1="{oy}" x2="{x_pos}" y2="{oy-ph}" stroke="#334155" stroke-dasharray="4,4" stroke-width="1"/>\n'
        svg += f'  <text x="{x_pos}" y="{oy+22}" font-family="sans-serif" font-size="12" fill="#94a3b8" text-anchor="middle">{lv}</text>\n'

    svg += f'  <text x="{ox+pw/2}" y="{oy+48}" font-family="sans-serif" font-size="14" font-weight="600" fill="#cbd5e1" text-anchor="middle">End-to-End Latency (clock cycles)</text>\n'
    svg += f'  <text x="35" y="{oy-ph/2}" font-family="sans-serif" font-size="14" font-weight="600" fill="#cbd5e1" text-anchor="middle" transform="rotate(-90 35 {oy-ph/2})">Cumulative Distribution (CDF %)</text>\n'

    def polyline(data, color, width):
        points = " ".join([f"{tx(l):.1f},{ty(v):.1f}" for l, v in zip(latencies, data)])
        res = f'  <polyline fill="none" stroke="{color}" stroke-width="{width}" points="{points}"/>\n'
        for l, v in zip(latencies, data):
            res += f'  <circle cx="{tx(l):.1f}" cy="{ty(v):.1f}" r="4" fill="{color}"/>\n'
        return res

    svg += polyline(cdf_single_hop, "#10b981", 3.0)
    svg += polyline(cdf_multi_hop,  "#6366f1", 3.0)

    # 5-cycle deterministic multi-hop marker
    x_5 = tx(5)
    svg += f'  <line x1="{x_5}" y1="{oy}" x2="{x_5}" y2="{ty(48)}" stroke="#f59e0b" stroke-width="2" stroke-dasharray="4,4"/>\n'
    svg += f'  <text x="{x_5+8}" y="{ty(48)+20}" font-family="sans-serif" font-size="11" font-weight="bold" fill="#f59e0b">Zero-load 2-hop baseline = 5 cyc</text>\n'

    # Legend
    lx, ly = ox + 30, oy - ph + 40
    svg += f'  <rect x="{lx-10}" y="{ly-15}" width="280" height="65" fill="#0f172a" fill-opacity="0.9" rx="6" stroke="#475569"/>\n'
    svg += f'  <line x1="{lx}" y1="{ly}" x2="{lx+25}" y2="{ly}" stroke="#10b981" stroke-width="3"/>\n'
    svg += f'  <circle cx="{lx+12.5}" cy="{ly}" r="4" fill="#10b981"/>\n'
    svg += f'  <text x="{lx+35}" y="{ly+4}" font-family="sans-serif" font-size="12" fill="#e2e8f0">1-Hop Local Transfers (PE0 -> PE1)</text>\n'
    svg += f'  <line x1="{lx}" y1="{ly+25}" x2="{lx+25}" y2="{ly+25}" stroke="#6366f1" stroke-width="3"/>\n'
    svg += f'  <circle cx="{lx+12.5}" cy="{ly+25}" r="4" fill="#6366f1"/>\n'
    svg += f'  <text x="{lx+35}" y="{ly+29}" font-family="sans-serif" font-size="12" fill="#e2e8f0">2-Hop Diagonal Transfers (PE0 -> PE3)</text>\n'

    svg += '</svg>'
    out_file = os.path.join(out_dir, "plot7_multihop_latency_distribution.svg")
    with open(out_file, 'w', encoding='utf-8') as f: f.write(svg)
    print(f"  [OK] Saved -> {out_file}")

# ------------------------------------------------------------------------------
# Master Plot Engine
# ------------------------------------------------------------------------------
def main():
    target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "plots")
    ensure_dir(target_dir)

    print("=" * 76)
    print("  NETWORK-ON-CHIP (NoC) GRAPH & PLOT GENERATOR")
    print(f"  Target Destination Directory: [{os.path.abspath(target_dir)}]")
    print("=" * 76)

    print("\n--> 1. Generating Plot 1: Latency vs. Offered Load...")
    generate_plot1_latency(target_dir)

    print("\n--> 2. Generating Plot 2: Throughput vs. Offered Load...")
    generate_plot2_throughput(target_dir)

    print("\n--> 3. Generating Plot 3: Hotspot Memory Latency Breakdown...")
    generate_plot3_hotspot_breakdown(target_dir)

    print("\n--> 4. Generating Plot 4: Head-of-Line (HoL) Blocking Mitigation...")
    generate_plot4_hol_mitigation(target_dir)

    print("\n--> 5. Generating Plot 5: Kintex-7 FPGA Hardware Synthesis & Fmax...")
    generate_plot5_fpga_hardware(target_dir)

    print("\n--> 6. Generating Plot 6: 10-to-1 Round-Robin Arbiter Fairness & Delay...")
    generate_plot6_arbitration(target_dir)

    print("\n--> 7. Generating Plot 7: 2x2 Mesh Multi-Hop Latency Distribution (CDF)...")
    generate_plot7_multihop_cdf(target_dir)

    print("\n" + "=" * 76)
    print("  All 7 Vector Graphics Plots Successfully Generated in docs/plots/!")
    print("=" * 76 + "\n")

if __name__ == '__main__':
    main()
