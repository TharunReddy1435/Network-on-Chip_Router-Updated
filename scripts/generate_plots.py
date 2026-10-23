#!/usr/bin/env python3
"""
==============================================================================
Script: generate_plots.py
Project: 5-Port Virtual-Channel Network-on-Chip (NoC) Router & 2x2 Mesh
Course: Data Networks (DN) Course Project
Description: Comprehensive Publication-Quality Vector Graphics (SVG) Generator:
               - Academic Publication Style (IEEE Conference / Transactions)
                 Pure white background, high-contrast academic palette,
                 monochrome-friendly markers (circle, square, triangle, diamond),
                 Times-Roman typography, IEEE column-width scaling.
               - Dark Mode Interactive Style (GitHub / Web Display)
                 Modern dark slate palette, subtle gradients, and glow.
               - Structural Microarchitecture & Topology Block Diagrams:
                 1. Router Microarchitecture (fig1_router_microarchitecture)
                 2. 2x2 2D-Mesh Topology & Interconnect (fig2_mesh_topology)
                 3. Flit & Trace Word Format (fig3_flit_format)
                 4. Round-Robin Arbiter State Transition (fig4_arbiter_fsm)
                 5. Performance Plots 1 through 8 (Latency, Throughput, Hotspots,
                    HoL Mitigation, Kintex-7 Hardware, Arbiter Fairness,
                    Multi-Hop CDF, Power vs Frequency).
==============================================================================
"""

import os
import sys
import argparse

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

# ==============================================================================
# SVG Header Builders
# ==============================================================================

def svg_header_dark(width, height, title):
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

def svg_header_academic(width, height, title=""):
    title_xml = f'  <text x="{width/2}" y="28" font-family="Times New Roman, Times, serif" font-size="16" font-weight="bold" fill="#111827" text-anchor="middle">{title}</text>\n' if title else ''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <filter id="box-shadow" x="-2%" y="-2%" width="104%" height="104%">
      <feDropShadow dx="1" dy="1" stdDeviation="1.5" flood-opacity="0.15"/>
    </filter>
  </defs>
  <!-- Clean white academic canvas -->
  <rect width="100%" height="100%" fill="#ffffff"/>
{title_xml}'''

# ==============================================================================
# Plot 1: Average Packet Latency vs. Offered Load
# ==============================================================================

def plot1_latency(out_dir, style="dark"):
    width, height = 800, 500
    is_acad = (style == "academic")
    svg = svg_header_academic(width, height, "Fig. 5: Average Packet Latency vs. Offered Load (2x2 Mesh NoC)") if is_acad else svg_header_dark(width, height, "Average Packet Latency vs. Offered Load (2x2 Mesh NoC)")

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

    grid_col = "#e5e7eb" if is_acad else "#334155"
    text_col = "#1f2937" if is_acad else "#94a3b8"
    font_fam = "Times New Roman, Times, serif" if is_acad else "sans-serif"
    axis_col = "#111827" if is_acad else "#cbd5e1"

    # Gridlines
    for yv in range(0, 19, 3):
        yp = ty(yv)
        svg += f'  <line x1="{ox}" y1="{yp}" x2="{ox+pw}" y2="{yp}" stroke="{grid_col}" stroke-dasharray="3,3" stroke-width="1"/>\n'
        svg += f'  <text x="{ox-12}" y="{yp+4}" font-family="{font_fam}" font-size="12" fill="{text_col}" text-anchor="end">{yv}</text>\n'

    for l in loads:
        xp = tx(l)
        svg += f'  <line x1="{xp}" y1="{oy}" x2="{xp}" y2="{oy-ph}" stroke="{grid_col}" stroke-dasharray="3,3" stroke-width="1"/>\n'
        svg += f'  <text x="{xp}" y="{oy+20}" font-family="{font_fam}" font-size="12" fill="{text_col}" text-anchor="middle">{l:.2f}</text>\n'

    # Axes
    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox+pw}" y2="{oy}" stroke="{axis_col}" stroke-width="1.5"/>\n'
    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-ph}" stroke="{axis_col}" stroke-width="1.5"/>\n'
    svg += f'  <text x="{ox+pw/2}" y="{oy+46}" font-family="{font_fam}" font-size="13" font-weight="bold" fill="{axis_col}" text-anchor="middle">Offered Load (flits / cycle / node)</text>\n'
    svg += f'  <text x="32" y="{oy-ph/2}" font-family="{font_fam}" font-size="13" font-weight="bold" fill="{axis_col}" text-anchor="middle" transform="rotate(-90 32 {oy-ph/2})">Average Packet Latency (cycles)</text>\n'

    # Markers & Polylines
    # 1. Baseline UR (Red / Diamond)
    # 2. Dual-VC UR (Blue / Circle)
    # 3. Baseline HS (Orange / Square)
    # 4. Dual-VC HS (Teal / Triangle)
    c1 = "#b91c1c" if is_acad else "#ef4444"
    c2 = "#1d4ed8" if is_acad else "#22c55e"
    c3 = "#d97706" if is_acad else "#f59e0b"
    c4 = "#0d9488" if is_acad else "#38bdf8"

    def render_series(data, color, dash, marker_type):
        pts = " ".join([f"{tx(l):.1f},{ty(v):.1f}" for l, v in zip(loads, data)])
        res = f'  <polyline fill="none" stroke="{color}" stroke-width="2.2" stroke-dasharray="{dash}" points="{pts}"/>\n'
        for l, v in zip(loads, data):
            cx, cy = tx(l), ty(v)
            if marker_type == "circle":
                res += f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" fill="{color}" stroke="#ffffff" stroke-width="1.5"/>\n'
            elif marker_type == "diamond":
                res += f'  <polygon points="{cx:.1f},{cy-5:.1f} {cx+5:.1f},{cy:.1f} {cx:.1f},{cy+5:.1f} {cx-5:.1f},{cy:.1f}" fill="{color}" stroke="#ffffff" stroke-width="1.5"/>\n'
            elif marker_type == "square":
                res += f'  <rect x="{cx-4:.1f}" y="{cy-4:.1f}" width="8" height="8" fill="{color}" stroke="#ffffff" stroke-width="1.5"/>\n'
            elif marker_type == "triangle":
                res += f'  <polygon points="{cx:.1f},{cy-5.5:.1f} {cx+5:.1f},{cy+4:.1f} {cx-5:.1f},{cy+4:.1f}" fill="{color}" stroke="#ffffff" stroke-width="1.5"/>\n'
        return res

    svg += render_series(base_ur, c1, "6,3", "diamond")
    svg += render_series(vc_ur,   c2, "",    "circle")
    svg += render_series(base_hs, c3, "6,3", "square")
    svg += render_series(vc_hs,   c4, "",    "triangle")

    # Legend
    lx, ly = ox + 25, oy - ph + 25
    bg_leg = "#ffffff" if is_acad else "#0f172a"
    bd_leg = "#9ca3af" if is_acad else "#475569"
    svg += f'  <rect x="{lx-10}" y="{ly-15}" width="290" height="110" fill="{bg_leg}" stroke="{bd_leg}" stroke-width="1" rx="4" filter="url(#box-shadow)"/>\n'
    
    items = [
        ("Baseline (Single-VC) - Uniform", c1, "6,3", "diamond"),
        ("Dual-VC (Proposed) - Uniform",   c2, "",    "circle"),
        ("Baseline (Single-VC) - Hotspot", c3, "6,3", "square"),
        ("Dual-VC (Proposed) - Hotspot",   c4, "",    "triangle")
    ]
    for idx, (lbl, col, dsh, mkr) in enumerate(items):
        item_y = ly + idx * 24
        svg += f'  <line x1="{lx}" y1="{item_y}" x2="{lx+25}" y2="{item_y}" stroke="{col}" stroke-width="2.2" stroke-dasharray="{dsh}"/>\n'
        cx, cy = lx + 12.5, item_y
        if mkr == "circle":
            svg += f'  <circle cx="{cx}" cy="{cy}" r="4" fill="{col}"/>\n'
        elif mkr == "diamond":
            svg += f'  <polygon points="{cx},{cy-4.5} {cx+4.5},{cy} {cx},{cy+4.5} {cx-4.5},{cy}" fill="{col}"/>\n'
        elif mkr == "square":
            svg += f'  <rect x="{cx-3.5}" y="{cy-3.5}" width="7" height="7" fill="{col}"/>\n'
        elif mkr == "triangle":
            svg += f'  <polygon points="{cx},{cy-5} {cx+4.5},{cy+3.5} {cx-4.5},{cy+3.5}" fill="{col}"/>\n'
        svg += f'  <text x="{lx+34}" y="{item_y+4}" font-family="{font_fam}" font-size="12" fill="{text_col}">{lbl}</text>\n'

    # Annotation badge
    ax_x, ax_y = tx(0.70), ty(3.18)
    svg += f'  <circle cx="{ax_x:.1f}" cy="{ax_y:.1f}" r="8" fill="none" stroke="#2563eb" stroke-width="2" stroke-dasharray="2,2"/>\n'
    svg += f'  <text x="{ax_x+12:.1f}" y="{ax_y+5:.1f}" font-family="{font_fam}" font-size="11" font-weight="bold" fill="#2563eb">-12.2% Latency @ 0.70 Load</text>\n'

    svg += '</svg>'
    fname = "plot1_latency_vs_offered_load.svg"
    with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f: f.write(svg)
    print(f"  [OK] Saved ({style}) -> {os.path.join(out_dir, fname)}")

# ==============================================================================
# Plot 2: Sustained Throughput vs. Offered Load
# ==============================================================================

def plot2_throughput(out_dir, style="dark"):
    width, height = 800, 500
    is_acad = (style == "academic")
    svg = svg_header_academic(width, height, "Fig. 6: Sustained Network Throughput vs. Offered Load") if is_acad else svg_header_dark(width, height, "Network Throughput vs. Offered Load (2x2 Mesh NoC)")

    x_min, x_max = 0.10, 1.00
    y_min, y_max = 0, 1.05
    ox, oy = 100, 420
    pw, ph = 640, 340

    loads = [0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 1.00]
    base_tp = [0.104, 0.249, 0.391, 0.551, 0.711, 0.840, 0.860]
    vc_tp   = [0.101, 0.254, 0.399, 0.551, 0.705, 0.862, 0.921]

    def tx(val): return ox + (val - x_min) / (x_max - x_min) * pw
    def ty(val): return oy - (val - y_min) / (y_max - y_min) * ph

    grid_col = "#e5e7eb" if is_acad else "#334155"
    text_col = "#1f2937" if is_acad else "#94a3b8"
    font_fam = "Times New Roman, Times, serif" if is_acad else "sans-serif"
    axis_col = "#111827" if is_acad else "#cbd5e1"

    for yv in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        yp = ty(yv)
        svg += f'  <line x1="{ox}" y1="{yp}" x2="{ox+pw}" y2="{yp}" stroke="{grid_col}" stroke-dasharray="3,3" stroke-width="1"/>\n'
        svg += f'  <text x="{ox-12}" y="{yp+4}" font-family="{font_fam}" font-size="12" fill="{text_col}" text-anchor="end">{yv:.1f}</text>\n'

    for l in loads:
        xp = tx(l)
        svg += f'  <line x1="{xp}" y1="{oy}" x2="{xp}" y2="{oy-ph}" stroke="{grid_col}" stroke-dasharray="3,3" stroke-width="1"/>\n'
        svg += f'  <text x="{xp}" y="{oy+20}" font-family="{font_fam}" font-size="12" fill="{text_col}" text-anchor="middle">{l:.2f}</text>\n'

    # Ideal line
    svg += f'  <line x1="{tx(0.10)}" y1="{ty(0.10)}" x2="{tx(1.00)}" y2="{ty(1.00)}" stroke="#9ca3af" stroke-width="1.5" stroke-dasharray="4,4"/>\n'
    svg += f'  <text x="{tx(0.55)+10}" y="{ty(0.55)+18}" font-family="{font_fam}" font-size="11" fill="#6b7280" font-style="italic">Ideal 100% Throughput</text>\n'

    # Axes
    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox+pw}" y2="{oy}" stroke="{axis_col}" stroke-width="1.5"/>\n'
    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-ph}" stroke="{axis_col}" stroke-width="1.5"/>\n'
    svg += f'  <text x="{ox+pw/2}" y="{oy+46}" font-family="{font_fam}" font-size="13" font-weight="bold" fill="{axis_col}" text-anchor="middle">Offered Load (flits / cycle / node)</text>\n'
    svg += f'  <text x="32" y="{oy-ph/2}" font-family="{font_fam}" font-size="13" font-weight="bold" fill="{axis_col}" text-anchor="middle" transform="rotate(-90 32 {oy-ph/2})">Sustained Throughput (flits / cycle / node)</text>\n'

    c_base = "#b91c1c" if is_acad else "#ef4444"
    c_vc   = "#15803d" if is_acad else "#10b981"

    # Baseline Polyline (Square)
    pts_b = " ".join([f"{tx(l):.1f},{ty(v):.1f}" for l, v in zip(loads, base_tp)])
    svg += f'  <polyline fill="none" stroke="{c_base}" stroke-width="2.4" stroke-dasharray="5,3" points="{pts_b}"/>\n'
    for l, v in zip(loads, base_tp):
        cx, cy = tx(l), ty(v)
        svg += f'  <rect x="{cx-4:.1f}" y="{cy-4:.1f}" width="8" height="8" fill="{c_base}" stroke="#ffffff" stroke-width="1.5"/>\n'

    # Dual-VC Polyline (Circle)
    pts_v = " ".join([f"{tx(l):.1f},{ty(v):.1f}" for l, v in zip(loads, vc_tp)])
    svg += f'  <polyline fill="none" stroke="{c_vc}" stroke-width="2.6" points="{pts_v}"/>\n'
    for l, v in zip(loads, vc_tp):
        cx, cy = tx(l), ty(v)
        svg += f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" fill="{c_vc}" stroke="#ffffff" stroke-width="1.5"/>\n'

    # Peak Gain Annotation
    x_peak, y_peak = tx(1.00), ty(0.921)
    x_bpeak, y_bpeak = tx(1.00), ty(0.860)
    svg += f'  <line x1="{x_peak}" y1="{y_peak}" x2="{x_bpeak}" y2="{y_bpeak}" stroke="#1d4ed8" stroke-width="2"/>\n'
    svg += f'  <text x="{x_peak-15:.1f}" y="{y_peak+20:.1f}" font-family="{font_fam}" font-size="11" font-weight="bold" fill="#1d4ed8" text-anchor="end">+7.1% Peak Capacity Gain</text>\n'

    # Legend
    lx, ly = ox + 35, oy - ph + 35
    bg_leg = "#ffffff" if is_acad else "#0f172a"
    bd_leg = "#9ca3af" if is_acad else "#475569"
    svg += f'  <rect x="{lx-10}" y="{ly-15}" width="265" height="85" fill="{bg_leg}" stroke="{bd_leg}" stroke-width="1" rx="4" filter="url(#box-shadow)"/>\n'
    svg += f'  <line x1="{lx}" y1="{ly}" x2="{lx+25}" y2="{ly}" stroke="{c_base}" stroke-width="2.4" stroke-dasharray="5,3"/>\n'
    svg += f'  <rect x="{lx+8.5}" y="{ly-4}" width="8" height="8" fill="{c_base}"/>\n'
    svg += f'  <text x="{lx+34}" y="{ly+4}" font-family="{font_fam}" font-size="12" fill="{text_col}">Baseline Single-VC (Sat = 0.860)</text>\n'
    svg += f'  <line x1="{lx}" y1="{ly+26}" x2="{lx+25}" y2="{ly+26}" stroke="{c_vc}" stroke-width="2.6"/>\n'
    svg += f'  <circle cx="{lx+12.5}" cy="{ly+26}" r="4.5" fill="{c_vc}"/>\n'
    svg += f'  <text x="{lx+34}" y="{ly+30}" font-family="{font_fam}" font-size="12" fill="{text_col}">Proposed Dual-VC (Sat = 0.921)</text>\n'

    svg += '</svg>'
    fname = "plot2_throughput_vs_offered_load.svg"
    with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f: f.write(svg)
    print(f"  [OK] Saved ({style}) -> {os.path.join(out_dir, fname)}")

# ==============================================================================
# Plot 3: Hotspot Memory Latency Breakdown
# ==============================================================================

def plot3_hotspot_breakdown(out_dir, style="dark"):
    width, height = 800, 500
    is_acad = (style == "academic")
    svg = svg_header_academic(width, height, "Fig. 7: Memory Controller Hotspot Latency Breakdown") if is_acad else svg_header_dark(width, height, "Memory Controller Hotspot Latency Breakdown")

    ox, oy = 100, 420
    pw, ph = 640, 340
    loads = [0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 1.00]
    base_hs = [2.38, 2.51, 2.89, 4.31, 7.65, 9.13, 10.50]
    vc_hs   = [2.37, 2.50, 2.73, 5.83, 12.43, 15.08, 15.85]

    y_max = 18
    def ty(val): return oy - (val / y_max) * ph

    grid_col = "#e5e7eb" if is_acad else "#334155"
    text_col = "#1f2937" if is_acad else "#94a3b8"
    font_fam = "Times New Roman, Times, serif" if is_acad else "sans-serif"
    axis_col = "#111827" if is_acad else "#cbd5e1"

    for yv in range(0, 19, 3):
        yp = ty(yv)
        svg += f'  <line x1="{ox}" y1="{yp}" x2="{ox+pw}" y2="{yp}" stroke="{grid_col}" stroke-dasharray="3,3" stroke-width="1"/>\n'
        svg += f'  <text x="{ox-12}" y="{yp+4}" font-family="{font_fam}" font-size="12" fill="{text_col}" text-anchor="end">{yv}</text>\n'

    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox+pw}" y2="{oy}" stroke="{axis_col}" stroke-width="1.5"/>\n'
    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-ph}" stroke="{axis_col}" stroke-width="1.5"/>\n'
    svg += f'  <text x="{ox+pw/2}" y="{oy+46}" font-family="{font_fam}" font-size="13" font-weight="bold" fill="{axis_col}" text-anchor="middle">Offered Load (flits / cycle / node)</text>\n'
    svg += f'  <text x="32" y="{oy-ph/2}" font-family="{font_fam}" font-size="13" font-weight="bold" fill="{axis_col}" text-anchor="middle" transform="rotate(-90 32 {oy-ph/2})">Average Packet Latency (cycles)</text>\n'

    col_b = "#94a3b8" if is_acad else "#64748b"
    col_v = "#0284c7" if is_acad else "#38bdf8"
    group_width = pw / len(loads)
    bar_w = 20

    for idx, l in enumerate(loads):
        gx = ox + idx * group_width + group_width / 2
        bh = ty(0) - ty(base_hs[idx])
        vh = ty(0) - ty(vc_hs[idx])

        # Baseline bar
        bx = gx - bar_w - 2
        svg += f'  <rect x="{bx:.1f}" y="{ty(base_hs[idx]):.1f}" width="{bar_w}" height="{bh:.1f}" fill="{col_b}" stroke="#1e293b" stroke-width="0.8"/>\n'
        # Dual-VC bar
        vx = gx + 2
        svg += f'  <rect x="{vx:.1f}" y="{ty(vc_hs[idx]):.1f}" width="{bar_w}" height="{vh:.1f}" fill="{col_v}" stroke="#1e293b" stroke-width="0.8"/>\n'
        svg += f'  <text x="{gx:.1f}" y="{oy+20}" font-family="{font_fam}" font-size="12" fill="{text_col}" text-anchor="middle">{l:.2f}</text>\n'

    # Legend
    lx, ly = ox + 35, oy - ph + 35
    bg_leg = "#ffffff" if is_acad else "#0f172a"
    bd_leg = "#9ca3af" if is_acad else "#475569"
    svg += f'  <rect x="{lx-10}" y="{ly-15}" width="260" height="70" fill="{bg_leg}" stroke="{bd_leg}" stroke-width="1" rx="4" filter="url(#box-shadow)"/>\n'
    svg += f'  <rect x="{lx}" y="{ly-6}" width="16" height="12" fill="{col_b}"/>\n'
    svg += f'  <text x="{lx+24}" y="{ly+4}" font-family="{font_fam}" font-size="12" fill="{text_col}">Baseline Single-VC (Hotspot)</text>\n'
    svg += f'  <rect x="{lx}" y="{ly+16}" width="16" height="12" fill="{col_v}"/>\n'
    svg += f'  <text x="{lx+24}" y="{ly+26}" font-family="{font_fam}" font-size="12" fill="{text_col}">Proposed Dual-VC (Hotspot)</text>\n'

    svg += '</svg>'
    fname = "plot3_hotspot_latency_breakdown.svg"
    with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f: f.write(svg)
    print(f"  [OK] Saved ({style}) -> {os.path.join(out_dir, fname)}")

# ==============================================================================
# Plot 4: Head-of-Line (HoL) Blocking Mitigation
# ==============================================================================

def plot4_hol_mitigation(out_dir, style="dark"):
    width, height = 800, 500
    is_acad = (style == "academic")
    svg = svg_header_academic(width, height, "Fig. 8: Head-of-Line (HoL) Blocking Mitigation Ratio") if is_acad else svg_header_dark(width, height, "Head-of-Line (HoL) Blocking Mitigation Ratio")

    ox, oy = 100, 420
    pw, ph = 640, 340
    loads = [0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 1.00]
    hol_base = [12.4, 28.1, 45.6, 64.2, 79.5, 88.2, 92.4]
    hol_vc   = [2.1,  5.4,  8.7,  11.2, 14.5, 16.5, 18.1]

    def tx(val): return ox + (val - 0.10) / (0.90) * pw
    def ty(val): return oy - (val / 100.0) * ph

    grid_col = "#e5e7eb" if is_acad else "#334155"
    text_col = "#1f2937" if is_acad else "#94a3b8"
    font_fam = "Times New Roman, Times, serif" if is_acad else "sans-serif"
    axis_col = "#111827" if is_acad else "#cbd5e1"

    for yv in range(0, 101, 20):
        yp = ty(yv)
        svg += f'  <line x1="{ox}" y1="{yp}" x2="{ox+pw}" y2="{yp}" stroke="{grid_col}" stroke-dasharray="3,3" stroke-width="1"/>\n'
        svg += f'  <text x="{ox-12}" y="{yp+4}" font-family="{font_fam}" font-size="12" fill="{text_col}" text-anchor="end">{yv}%</text>\n'

    for l in loads:
        xp = tx(l)
        svg += f'  <line x1="{xp}" y1="{oy}" x2="{xp}" y2="{oy-ph}" stroke="{grid_col}" stroke-dasharray="3,3" stroke-width="1"/>\n'
        svg += f'  <text x="{xp}" y="{oy+20}" font-family="{font_fam}" font-size="12" fill="{text_col}" text-anchor="middle">{l:.2f}</text>\n'

    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox+pw}" y2="{oy}" stroke="{axis_col}" stroke-width="1.5"/>\n'
    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-ph}" stroke="{axis_col}" stroke-width="1.5"/>\n'
    svg += f'  <text x="{ox+pw/2}" y="{oy+46}" font-family="{font_fam}" font-size="13" font-weight="bold" fill="{axis_col}" text-anchor="middle">Offered Load (flits / cycle / node)</text>\n'
    svg += f'  <text x="32" y="{oy-ph/2}" font-family="{font_fam}" font-size="13" font-weight="bold" fill="{axis_col}" text-anchor="middle" transform="rotate(-90 32 {oy-ph/2})">HoL Blocking Contention Probability (%)</text>\n'

    c_b = "#dc2626" if is_acad else "#ef4444"
    c_v = "#16a34a" if is_acad else "#22c55e"

    pts_b = " ".join([f"{tx(l):.1f},{ty(v):.1f}" for l, v in zip(loads, hol_base)])
    svg += f'  <polyline fill="none" stroke="{c_b}" stroke-width="2.4" stroke-dasharray="5,3" points="{pts_b}"/>\n'
    for l, v in zip(loads, hol_base):
        cx, cy = tx(l), ty(v)
        svg += f'  <rect x="{cx-4:.1f}" y="{cy-4:.1f}" width="8" height="8" fill="{c_b}" stroke="#ffffff" stroke-width="1.5"/>\n'

    pts_v = " ".join([f"{tx(l):.1f},{ty(v):.1f}" for l, v in zip(loads, hol_vc)])
    svg += f'  <polyline fill="none" stroke="{c_v}" stroke-width="2.6" points="{pts_v}"/>\n'
    for l, v in zip(loads, hol_vc):
        cx, cy = tx(l), ty(v)
        svg += f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" fill="{c_v}" stroke="#ffffff" stroke-width="1.5"/>\n'

    # Annotation
    x_ann, y_ann1, y_ann2 = tx(0.85), ty(88.2), ty(16.5)
    svg += f'  <line x1="{x_ann}" y1="{y_ann1}" x2="{x_ann}" y2="{y_ann2}" stroke="#1d4ed8" stroke-width="2"/>\n'
    svg += f'  <text x="{x_ann-12}" y="{(y_ann1+y_ann2)/2}" font-family="{font_fam}" font-size="11" font-weight="bold" fill="#1d4ed8" text-anchor="end">81.3% Contention Reduction</text>\n'

    # Legend
    lx, ly = ox + 35, oy - ph + 35
    bg_leg = "#ffffff" if is_acad else "#0f172a"
    bd_leg = "#9ca3af" if is_acad else "#475569"
    svg += f'  <rect x="{lx-10}" y="{ly-15}" width="280" height="70" fill="{bg_leg}" stroke="{bd_leg}" stroke-width="1" rx="4" filter="url(#box-shadow)"/>\n'
    svg += f'  <line x1="{lx}" y1="{ly}" x2="{lx+25}" y2="{ly}" stroke="{c_b}" stroke-width="2.4" stroke-dasharray="5,3"/>\n'
    svg += f'  <rect x="{lx+8.5}" y="{ly-4}" width="8" height="8" fill="{c_b}"/>\n'
    svg += f'  <text x="{lx+34}" y="{ly+4}" font-family="{font_fam}" font-size="12" fill="{text_col}">Single-Queue FIFO (Severe Contention)</text>\n'
    svg += f'  <line x1="{lx}" y1="{ly+24}" x2="{lx+25}" y2="{ly+24}" stroke="{c_v}" stroke-width="2.6"/>\n'
    svg += f'  <circle cx="{lx+12.5}" cy="{ly+24}" r="4.5" fill="{c_v}"/>\n'
    svg += f'  <text x="{lx+34}" y="{ly+28}" font-family="{font_fam}" font-size="12" fill="{text_col}">Dual Virtual Channels (Decoupled)</text>\n'

    svg += '</svg>'
    fname = "plot4_hol_blocking_mitigation.svg"
    with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f: f.write(svg)
    print(f"  [OK] Saved ({style}) -> {os.path.join(out_dir, fname)}")

# ==============================================================================
# Plot 5: Kintex-7 FPGA Hardware Synthesis & Fmax
# ==============================================================================

def plot5_fpga_hardware(out_dir, style="dark"):
    width, height = 800, 500
    is_acad = (style == "academic")
    svg = svg_header_academic(width, height, "Fig. 9: Kintex-7 FPGA Hardware Utilization & Fmax Comparison") if is_acad else svg_header_dark(width, height, "Kintex-7 FPGA Hardware Synthesis & Fmax Benchmarking")

    ox, oy = 100, 420
    pw, ph = 640, 340

    designs = ["Vinoth Kumar 2014", "Ved et al. 2017", "Bhargavi et al. 2024", "Baseline Router", "Dual-VC Router", "2x2 Mesh (4 Nodes)"]
    fmax    = [50.0, 120.0, 205.0, 180.2, 227.48, 229.62]
    luts    = [1242, 1100, 1400, 657, 1271, 2533]

    def ty(val): return oy - (val / 250.0) * ph
    grid_col = "#e5e7eb" if is_acad else "#334155"
    text_col = "#1f2937" if is_acad else "#94a3b8"
    font_fam = "Times New Roman, Times, serif" if is_acad else "sans-serif"
    axis_col = "#111827" if is_acad else "#cbd5e1"

    for yv in range(0, 251, 50):
        yp = ty(yv)
        svg += f'  <line x1="{ox}" y1="{yp}" x2="{ox+pw}" y2="{yp}" stroke="{grid_col}" stroke-dasharray="3,3" stroke-width="1"/>\n'
        svg += f'  <text x="{ox-12}" y="{yp+4}" font-family="{font_fam}" font-size="12" fill="{text_col}" text-anchor="end">{yv}</text>\n'

    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox+pw}" y2="{oy}" stroke="{axis_col}" stroke-width="1.5"/>\n'
    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-ph}" stroke="{axis_col}" stroke-width="1.5"/>\n'
    svg += f'  <text x="32" y="{oy-ph/2}" font-family="{font_fam}" font-size="13" font-weight="bold" fill="{axis_col}" text-anchor="middle" transform="rotate(-90 32 {oy-ph/2})">Maximum Clock Frequency Fmax (MHz)</text>\n'

    group_w = pw / len(designs)
    bar_w = 42

    for idx, (des, fv, lv) in enumerate(zip(designs, fmax, luts)):
        gx = ox + idx * group_w + group_w / 2
        bh = ty(0) - ty(fv)
        col = "#2563eb" if idx >= 3 else "#9ca3af"
        if idx == 4: col = "#059669"
        if idx == 5: col = "#7c3aed"

        svg += f'  <rect x="{gx-bar_w/2:.1f}" y="{ty(fv):.1f}" width="{bar_w}" height="{bh:.1f}" fill="{col}" stroke="#1e293b" stroke-width="1" rx="3"/>\n'
        svg += f'  <text x="{gx:.1f}" y="{ty(fv)-8:.1f}" font-family="{font_fam}" font-size="11" font-weight="bold" fill="{col}" text-anchor="middle">{fv:.1f} MHz</text>\n'
        svg += f'  <text x="{gx:.1f}" y="{ty(fv)-22:.1f}" font-family="{font_fam}" font-size="10" fill="{text_col}" text-anchor="middle">{lv} LUTs</text>\n'

        # Rotated labels for X-axis
        svg += f'  <text x="{gx:.1f}" y="{oy+18}" font-family="{font_fam}" font-size="11" fill="{text_col}" text-anchor="end" transform="rotate(-30 {gx} {oy+18})">{des}</text>\n'

    svg += '</svg>'
    fname = "plot5_fpga_hardware_utilization.svg"
    with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f: f.write(svg)
    print(f"  [OK] Saved ({style}) -> {os.path.join(out_dir, fname)}")

# ==============================================================================
# Plot 6: 10-to-1 Round-Robin Arbiter Fairness & Delay
# ==============================================================================

def plot6_arbitration(out_dir, style="dark"):
    width, height = 800, 500
    is_acad = (style == "academic")
    svg = svg_header_academic(width, height, "Fig. 10: 10-to-1 Round-Robin Arbiter Bandwidth Fairness") if is_acad else svg_header_dark(width, height, "10-to-1 Round-Robin Arbiter Fairness & Service Delay")

    ox, oy = 100, 420
    pw, ph = 640, 340

    vcs = ["L0", "L1", "N0", "N1", "S0", "S1", "E0", "E1", "W0", "W1"]
    shares = [9.9, 10.1, 10.0, 9.8, 10.2, 10.0, 9.9, 10.1, 10.0, 10.0]

    def ty(val): return oy - (val / 15.0) * ph
    grid_col = "#e5e7eb" if is_acad else "#334155"
    text_col = "#1f2937" if is_acad else "#94a3b8"
    font_fam = "Times New Roman, Times, serif" if is_acad else "sans-serif"
    axis_col = "#111827" if is_acad else "#cbd5e1"

    for yv in [0, 3, 6, 9, 12, 15]:
        yp = ty(yv)
        svg += f'  <line x1="{ox}" y1="{yp}" x2="{ox+pw}" y2="{yp}" stroke="{grid_col}" stroke-dasharray="3,3" stroke-width="1"/>\n'
        svg += f'  <text x="{ox-12}" y="{yp+4}" font-family="{font_fam}" font-size="12" fill="{text_col}" text-anchor="end">{yv}%</text>\n'

    # Ideal 10% line
    y_10 = ty(10.0)
    svg += f'  <line x1="{ox}" y1="{y_10}" x2="{ox+pw}" y2="{y_10}" stroke="#b91c1c" stroke-width="2" stroke-dasharray="5,4"/>\n'
    svg += f'  <text x="{ox+pw-10}" y="{y_10-8}" font-family="{font_fam}" font-size="11" font-weight="bold" fill="#b91c1c" text-anchor="end">Ideal Fair Share = 10.0% (Worst-case Wait = 9 cyc)</text>\n'

    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox+pw}" y2="{oy}" stroke="{axis_col}" stroke-width="1.5"/>\n'
    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-ph}" stroke="{axis_col}" stroke-width="1.5"/>\n'
    svg += f'  <text x="{ox+pw/2}" y="{oy+46}" font-family="{font_fam}" font-size="13" font-weight="bold" fill="{axis_col}" text-anchor="middle">Competing Input Virtual Channels</text>\n'
    svg += f'  <text x="32" y="{oy-ph/2}" font-family="{font_fam}" font-size="13" font-weight="bold" fill="{axis_col}" text-anchor="middle" transform="rotate(-90 32 {oy-ph/2})">Allocated Bandwidth Share (%)</text>\n'

    bar_w = 32
    group_w = pw / len(vcs)
    for idx, (vc, s) in enumerate(zip(vcs, shares)):
        gx = ox + idx * group_w + group_w / 2
        bh = ty(0) - ty(s)
        col = "#1d4ed8" if is_acad else "#3b82f6"
        svg += f'  <rect x="{gx-bar_w/2:.1f}" y="{ty(s):.1f}" width="{bar_w}" height="{bh:.1f}" fill="{col}" stroke="#1e293b" stroke-width="0.8" rx="2"/>\n'
        svg += f'  <text x="{gx:.1f}" y="{ty(s)-6:.1f}" font-family="{font_fam}" font-size="11" font-weight="bold" fill="{col}" text-anchor="middle">{s:.1f}%</text>\n'
        svg += f'  <text x="{gx:.1f}" y="{oy+20}" font-family="{font_fam}" font-size="12" fill="{text_col}" text-anchor="middle">{vc}</text>\n'

    svg += '</svg>'
    fname = "plot6_arbitration_fairness_and_delay.svg"
    with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f: f.write(svg)
    print(f"  [OK] Saved ({style}) -> {os.path.join(out_dir, fname)}")

# ==============================================================================
# Plot 7: Multi-Hop Latency Distribution (CDF)
# ==============================================================================

def plot7_multihop_cdf(out_dir, style="dark"):
    width, height = 800, 500
    is_acad = (style == "academic")
    svg = svg_header_academic(width, height, "Fig. 11: Multi-Hop End-to-End Latency CDF (2x2 Mesh)") if is_acad else svg_header_dark(width, height, "2x2 Mesh Multi-Hop Latency Distribution (CDF)")

    ox, oy = 100, 420
    pw, ph = 640, 340
    latencies = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    cdf_single_hop = [0, 15, 65, 92, 98, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100]
    cdf_multi_hop  = [0, 0, 0, 8, 48, 78, 89, 94, 97, 98, 99, 99.5, 100, 100, 100]

    def tx(val): return ox + (val - 1) / (14.0) * pw
    def ty(val): return oy - (val / 100.0) * ph

    grid_col = "#e5e7eb" if is_acad else "#334155"
    text_col = "#1f2937" if is_acad else "#94a3b8"
    font_fam = "Times New Roman, Times, serif" if is_acad else "sans-serif"
    axis_col = "#111827" if is_acad else "#cbd5e1"

    for yv in range(0, 101, 20):
        yp = ty(yv)
        svg += f'  <line x1="{ox}" y1="{yp}" x2="{ox+pw}" y2="{yp}" stroke="{grid_col}" stroke-dasharray="3,3" stroke-width="1"/>\n'
        svg += f'  <text x="{ox-12}" y="{yp+4}" font-family="{font_fam}" font-size="12" fill="{text_col}" text-anchor="end">{yv}%</text>\n'

    for lv in latencies:
        xp = tx(lv)
        svg += f'  <line x1="{xp}" y1="{oy}" x2="{xp}" y2="{oy-ph}" stroke="{grid_col}" stroke-dasharray="3,3" stroke-width="1"/>\n'
        svg += f'  <text x="{xp}" y="{oy+20}" font-family="{font_fam}" font-size="12" fill="{text_col}" text-anchor="middle">{lv}</text>\n'

    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox+pw}" y2="{oy}" stroke="{axis_col}" stroke-width="1.5"/>\n'
    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-ph}" stroke="{axis_col}" stroke-width="1.5"/>\n'
    svg += f'  <text x="{ox+pw/2}" y="{oy+46}" font-family="{font_fam}" font-size="13" font-weight="bold" fill="{axis_col}" text-anchor="middle">Packet Traversal Latency (clock cycles)</text>\n'
    svg += f'  <text x="32" y="{oy-ph/2}" font-family="{font_fam}" font-size="13" font-weight="bold" fill="{axis_col}" text-anchor="middle" transform="rotate(-90 32 {oy-ph/2})">Cumulative Distribution (CDF %)</text>\n'

    c_s = "#15803d" if is_acad else "#10b981"
    c_m = "#4338ca" if is_acad else "#6366f1"

    pts_s = " ".join([f"{tx(l):.1f},{ty(v):.1f}" for l, v in zip(latencies, cdf_single_hop)])
    svg += f'  <polyline fill="none" stroke="{c_s}" stroke-width="2.6" points="{pts_s}"/>\n'
    for l, v in zip(latencies, cdf_single_hop):
        cx, cy = tx(l), ty(v)
        svg += f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="4" fill="{c_s}"/>\n'

    pts_m = " ".join([f"{tx(l):.1f},{ty(v):.1f}" for l, v in zip(latencies, cdf_multi_hop)])
    svg += f'  <polyline fill="none" stroke="{c_m}" stroke-width="2.6" stroke-dasharray="6,3" points="{pts_m}"/>\n'
    for l, v in zip(latencies, cdf_multi_hop):
        cx, cy = tx(l), ty(v)
        svg += f'  <rect x="{cx-3.5:.1f}" y="{cy-3.5:.1f}" width="7" height="7" fill="{c_m}"/>\n'

    # Marker for 5 cycles
    x5 = tx(5)
    svg += f'  <line x1="{x5}" y1="{oy}" x2="{x5}" y2="{ty(48)}" stroke="#d97706" stroke-width="1.8" stroke-dasharray="3,3"/>\n'
    svg += f'  <text x="{x5+6}" y="{ty(48)+25}" font-family="{font_fam}" font-size="11" font-weight="bold" fill="#d97706">2-Hop Zero-Load Bound = 5 cycles</text>\n'

    # Legend
    lx, ly = ox + 35, oy - ph + 40
    bg_leg = "#ffffff" if is_acad else "#0f172a"
    bd_leg = "#9ca3af" if is_acad else "#475569"
    svg += f'  <rect x="{lx-10}" y="{ly-15}" width="280" height="65" fill="{bg_leg}" stroke="{bd_leg}" stroke-width="1" rx="4" filter="url(#box-shadow)"/>\n'
    svg += f'  <line x1="{lx}" y1="{ly}" x2="{lx+25}" y2="{ly}" stroke="{c_s}" stroke-width="2.6"/>\n'
    svg += f'  <circle cx="{lx+12.5}" cy="{ly}" r="4" fill="{c_s}"/>\n'
    svg += f'  <text x="{lx+34}" y="{ly+4}" font-family="{font_fam}" font-size="12" fill="{text_col}">1-Hop Transfers (PE0 -&gt; PE1)</text>\n'
    svg += f'  <line x1="{lx}" y1="{ly+24}" x2="{lx+25}" y2="{ly+24}" stroke="{c_m}" stroke-width="2.6" stroke-dasharray="6,3"/>\n'
    svg += f'  <rect x="{lx+9}" y="{ly+20.5}" width="7" height="7" fill="{c_m}"/>\n'
    svg += f'  <text x="{lx+34}" y="{ly+28}" font-family="{font_fam}" font-size="12" fill="{text_col}">2-Hop Diagonal Transfers (PE0 -&gt; PE3)</text>\n'

    svg += '</svg>'
    fname = "plot7_multihop_latency_distribution.svg"
    with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f: f.write(svg)
    print(f"  [OK] Saved ({style}) -> {os.path.join(out_dir, fname)}")

# ==============================================================================
# Plot 8: Power Dissipation vs. Clock Frequency & Logic Activity
# ==============================================================================

def plot8_power_breakdown(out_dir, style="dark"):
    width, height = 800, 500
    is_acad = (style == "academic")
    svg = svg_header_academic(width, height, "Fig. 12: Dynamic and Static Power Scaling vs. Clock Frequency") if is_acad else svg_header_dark(width, height, "On-Chip Power Scaling on Kintex-7 FPGA (xc7k70t)")

    ox, oy = 100, 420
    pw, ph = 640, 340
    freqs = [50, 100, 150, 200, 227.48]
    # Router Power: Static = 0.081 W across all, Dynamic scales linearly
    dyn_router = [0.027, 0.054, 0.081, 0.108, 0.123]
    tot_router = [d + 0.081 for d in dyn_router]
    # Mesh Power (4 Routers)
    dyn_mesh   = [0.020, 0.040, 0.060, 0.080, 0.092]
    tot_mesh   = [d + 0.081 for d in dyn_mesh]

    def tx(val): return ox + (val - 50) / (250 - 50) * pw
    def ty(val): return oy - (val / 0.25) * ph

    grid_col = "#e5e7eb" if is_acad else "#334155"
    text_col = "#1f2937" if is_acad else "#94a3b8"
    font_fam = "Times New Roman, Times, serif" if is_acad else "sans-serif"
    axis_col = "#111827" if is_acad else "#cbd5e1"

    for yv in [0.00, 0.05, 0.10, 0.15, 0.20, 0.25]:
        yp = ty(yv)
        svg += f'  <line x1="{ox}" y1="{yp}" x2="{ox+pw}" y2="{yp}" stroke="{grid_col}" stroke-dasharray="3,3" stroke-width="1"/>\n'
        svg += f'  <text x="{ox-12}" y="{yp+4}" font-family="{font_fam}" font-size="12" fill="{text_col}" text-anchor="end">{yv:.2f} W</text>\n'

    for fq in freqs:
        xp = tx(fq)
        svg += f'  <line x1="{xp}" y1="{oy}" x2="{xp}" y2="{oy-ph}" stroke="{grid_col}" stroke-dasharray="3,3" stroke-width="1"/>\n'
        lbl = f"{fq:.0f}" if fq != 227.48 else "227.5"
        svg += f'  <text x="{xp}" y="{oy+20}" font-family="{font_fam}" font-size="12" fill="{text_col}" text-anchor="middle">{lbl}</text>\n'

    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox+pw}" y2="{oy}" stroke="{axis_col}" stroke-width="1.5"/>\n'
    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-ph}" stroke="{axis_col}" stroke-width="1.5"/>\n'
    svg += f'  <text x="{ox+pw/2}" y="{oy+46}" font-family="{font_fam}" font-size="13" font-weight="bold" fill="{axis_col}" text-anchor="middle">Clock Frequency (MHz)</text>\n'
    svg += f'  <text x="32" y="{oy-ph/2}" font-family="{font_fam}" font-size="13" font-weight="bold" fill="{axis_col}" text-anchor="middle" transform="rotate(-90 32 {oy-ph/2})">Total Power Dissipation (Watts)</text>\n'

    # Static power baseline
    ys = ty(0.081)
    svg += f'  <line x1="{ox}" y1="{ys}" x2="{ox+pw}" y2="{ys}" stroke="#64748b" stroke-width="1.8" stroke-dasharray="4,4"/>\n'
    svg += f'  <text x="{ox+15}" y="{ys-6}" font-family="{font_fam}" font-size="11" fill="#64748b">Device Static Power Floor (0.081 W)</text>\n'

    c_r = "#b91c1c" if is_acad else "#f43f5e"
    c_m = "#1d4ed8" if is_acad else "#3b82f6"

    pts_r = " ".join([f"{tx(f):.1f},{ty(p):.1f}" for f, p in zip(freqs, tot_router)])
    svg += f'  <polyline fill="none" stroke="{c_r}" stroke-width="2.5" points="{pts_r}"/>\n'
    for f, p in zip(freqs, tot_router):
        cx, cy = tx(f), ty(p)
        svg += f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" fill="{c_r}"/>\n'

    pts_m = " ".join([f"{tx(f):.1f},{ty(p):.1f}" for f, p in zip(freqs, tot_mesh)])
    svg += f'  <polyline fill="none" stroke="{c_m}" stroke-width="2.5" stroke-dasharray="6,3" points="{pts_m}"/>\n'
    for f, p in zip(freqs, tot_mesh):
        cx, cy = tx(f), ty(p)
        svg += f'  <rect x="{cx-3.5:.1f}" y="{cy-3.5:.1f}" width="7" height="7" fill="{c_m}"/>\n'

    # Legend
    lx, ly = ox + 35, oy - ph + 35
    bg_leg = "#ffffff" if is_acad else "#0f172a"
    bd_leg = "#9ca3af" if is_acad else "#475569"
    svg += f'  <rect x="{lx-10}" y="{ly-15}" width="280" height="65" fill="{bg_leg}" stroke="{bd_leg}" stroke-width="1" rx="4" filter="url(#box-shadow)"/>\n'
    svg += f'  <line x1="{lx}" y1="{ly}" x2="{lx+25}" y2="{ly}" stroke="{c_r}" stroke-width="2.5"/>\n'
    svg += f'  <circle cx="{lx+12.5}" cy="{ly}" r="4" fill="{c_r}"/>\n'
    svg += f'  <text x="{lx+34}" y="{ly+4}" font-family="{font_fam}" font-size="12" fill="{text_col}">Dual-VC Router (Total Power = 0.189 W)</text>\n'
    svg += f'  <line x1="{lx}" y1="{ly+24}" x2="{lx+25}" y2="{ly+24}" stroke="{c_m}" stroke-width="2.5" stroke-dasharray="6,3"/>\n'
    svg += f'  <rect x="{lx+9}" y="{ly+20.5}" width="7" height="7" fill="{c_m}"/>\n'
    svg += f'  <text x="{lx+34}" y="{ly+28}" font-family="{font_fam}" font-size="12" fill="{text_col}">2x2 Mesh Interconnect (Total = 0.162 W)</text>\n'

    svg += '</svg>'
    fname = "plot8_power_breakdown.svg"
    with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f: f.write(svg)
    print(f"  [OK] Saved ({style}) -> {os.path.join(out_dir, fname)}")

# ==============================================================================
# Architectural Figure 1: Router Microarchitecture Block Diagram
# ==============================================================================

def generate_fig1_router_architecture(out_dir):
    width, height = 900, 600
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <filter id="card-shadow" x="-3%" y="-3%" width="106%" height="106%">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.12"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#1e293b"/>
    </marker>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/>
    </marker>
  </defs>

  <!-- Clean Canvas -->
  <rect width="100%" height="100%" fill="#ffffff"/>
  <rect x="10" y="10" width="{width-20}" height="{height-20}" fill="none" stroke="#cbd5e1" stroke-width="1.5" rx="8"/>
  <text x="{width/2}" y="36" font-family="Times New Roman, Times, serif" font-size="18" font-weight="bold" fill="#0f172a" text-anchor="middle">Fig. 1: 5-Port Virtual-Channel Network-on-Chip Router Microarchitecture</text>

  <!-- 1. Input Ports Stage -->
  <g id="input-stage">
    <rect x="40" y="65" width="220" height="505" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.2" rx="6" filter="url(#card-shadow)"/>
    <text x="150" y="90" font-family="Times New Roman, Times, serif" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">1. Input Buffering (5 Ports)</text>
    <text x="150" y="106" font-family="Arial, sans-serif" font-size="10" fill="#64748b" text-anchor="middle">Dual-VC FWFT Synchronous FIFOs</text>

    <!-- 5 Port Blocks -->
'''
    ports = ["Local (PE)", "North (N)", "South (S)", "East (E)", "West (W)"]
    for idx, p in enumerate(ports):
        by = 120 + idx * 88
        svg += f'''    <!-- Port {p} -->
    <g transform="translate(50, {by})">
      <rect width="200" height="74" fill="#ffffff" stroke="#cbd5e1" stroke-width="1" rx="4"/>
      <text x="10" y="16" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#0284c7">Port: {p}</text>
      <!-- VC0 Box -->
      <rect x="10" y="24" width="85" height="30" fill="#f1f5f9" stroke="#94a3b8" stroke-width="0.8" rx="2"/>
      <text x="52.5" y="43" font-family="Arial, sans-serif" font-size="10" fill="#334155" text-anchor="middle">VC0 (4 Flits)</text>
      <!-- VC1 Box -->
      <rect x="105" y="24" width="85" height="30" fill="#f1f5f9" stroke="#94a3b8" stroke-width="0.8" rx="2"/>
      <text x="147.5" y="43" font-family="Arial, sans-serif" font-size="10" fill="#334155" text-anchor="middle">VC1 (4 Flits)</text>
      <text x="100" y="68" font-family="Arial, sans-serif" font-size="9" fill="#059669" text-anchor="middle">&#10003; Credit Return Signal (To Upstream)</text>
    </g>
'''
    svg += f'''  </g>

  <!-- Connecting Arrows from Input to RC & Arbiter -->
  <path d="M 260 157 L 310 157" stroke="#1e293b" stroke-width="1.5" marker-end="url(#arrow)"/>
  <path d="M 260 245 L 310 245" stroke="#1e293b" stroke-width="1.5" marker-end="url(#arrow)"/>
  <path d="M 260 333 L 310 333" stroke="#1e293b" stroke-width="1.5" marker-end="url(#arrow)"/>
  <path d="M 260 421 L 310 421" stroke="#1e293b" stroke-width="1.5" marker-end="url(#arrow)"/>
  <path d="M 260 509 L 310 509" stroke="#1e293b" stroke-width="1.5" marker-end="url(#arrow)"/>

  <!-- 2. Dimension-Order XY Route Compute -->
  <g id="route-compute">
    <rect x="310" y="65" width="170" height="505" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.2" rx="6" filter="url(#card-shadow)"/>
    <text x="395" y="90" font-family="Times New Roman, Times, serif" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">2. Route Computation</text>
    <text x="395" y="106" font-family="Arial, sans-serif" font-size="10" fill="#64748b" text-anchor="middle">10x Parallel XY Turn Model</text>
'''
    for idx, p in enumerate(ports):
        by = 120 + idx * 88
        svg += f'''    <g transform="translate(320, {by})">
      <rect width="150" height="74" fill="#ffffff" stroke="#cbd5e1" stroke-width="1" rx="4"/>
      <text x="75" y="24" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#4338ca" text-anchor="middle">XY Unit ({p[:5]})</text>
      <text x="75" y="44" font-family="Arial, sans-serif" font-size="9.5" fill="#475569" text-anchor="middle">X-first: (dx &gt; cx) &#8594; E</text>
      <text x="75" y="60" font-family="Arial, sans-serif" font-size="9.5" fill="#475569" text-anchor="middle">Y-next: (dy &gt; cy) &#8594; S</text>
    </g>
'''
    svg += f'''  </g>

  <!-- 3. Arbitration & Flow Control Stage -->
  <g id="arbitration-stage">
    <rect x="515" y="65" width="185" height="505" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.2" rx="6" filter="url(#card-shadow)"/>
    <text x="607" y="90" font-family="Times New Roman, Times, serif" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">3. Switch Allocation</text>
    <text x="607" y="106" font-family="Arial, sans-serif" font-size="10" fill="#64748b" text-anchor="middle">10-to-1 Round-Robin Arbiters</text>
'''
    for idx, p in enumerate(ports):
        by = 120 + idx * 88
        svg += f'''    <g transform="translate(525, {by})">
      <rect width="165" height="74" fill="#ffffff" stroke="#cbd5e1" stroke-width="1" rx="4"/>
      <text x="82.5" y="22" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#b91c1c" text-anchor="middle">RR Arbiter: Port {p[:5]}</text>
      <text x="82.5" y="40" font-family="Arial, sans-serif" font-size="9" fill="#334155" text-anchor="middle">10 Request Lines &#8594; Grant</text>
      <rect x="15" y="48" width="135" height="18" fill="#fef2f2" stroke="#fca5a5" stroke-width="0.8" rx="2"/>
      <text x="82.5" y="61" font-family="Arial, sans-serif" font-size="9" font-weight="bold" fill="#991b1b" text-anchor="middle">Credit Status (Count &gt; 0)</text>
    </g>
'''
    svg += f'''  </g>

  <!-- Connecting to Crossbar -->
  <path d="M 480 317 L 515 317" stroke="#1e293b" stroke-width="1.5" marker-end="url(#arrow)"/>
  <path d="M 700 317 L 735 317" stroke="#1e293b" stroke-width="1.5" marker-end="url(#arrow)"/>

  <!-- 4. Crossbar Matrix Stage -->
  <g id="crossbar-stage">
    <rect x="735" y="65" width="125" height="505" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.2" rx="6" filter="url(#card-shadow)"/>
    <text x="797" y="90" font-family="Times New Roman, Times, serif" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">4. Crossbar</text>
    <text x="797" y="106" font-family="Arial, sans-serif" font-size="10" fill="#64748b" text-anchor="middle">10x5 Switch</text>
    
    <rect x="745" y="125" width="105" height="430" fill="#eff6ff" stroke="#93c5fd" stroke-width="1.5" rx="4"/>
    <text x="797" y="325" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#1e40af" text-anchor="middle" transform="rotate(-90 797 325)">10x5 Crossbar Matrix</text>

    <!-- Outgoing Channels -->
'''
    out_ports = ["PE Out", "North Out", "South Out", "East Out", "West Out"]
    for idx, op in enumerate(out_ports):
        by = 150 + idx * 88
        svg += f'''    <line x1="850" y1="{by}" x2="885" y2="{by}" stroke="#2563eb" stroke-width="2.5" marker-end="url(#arrow-blue)"/>
    <text x="860" y="{by-6}" font-family="Arial, sans-serif" font-size="9" font-weight="bold" fill="#1e3a8a">{op}</text>
'''
    svg += '''  </g>
</svg>'''
    fname = "fig1_router_microarchitecture.svg"
    with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f: f.write(svg)
    print(f"  [OK] Saved -> {os.path.join(out_dir, fname)}")

# ==============================================================================
# Architectural Figure 2: 2x2 2D-Mesh Interconnect Topology
# ==============================================================================

def generate_fig2_mesh_topology(out_dir):
    width, height = 700, 520
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <filter id="mesh-shadow" x="-3%" y="-3%" width="106%" height="106%">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.15"/>
    </filter>
    <marker id="bi-arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 2 L 8 5 L 0 8 z" fill="#0284c7"/>
    </marker>
    <marker id="pe-arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 2 L 8 5 L 0 8 z" fill="#15803d"/>
    </marker>
  </defs>

  <rect width="100%" height="100%" fill="#ffffff"/>
  <rect x="8" y="8" width="{width-16}" height="{height-16}" fill="none" stroke="#cbd5e1" stroke-width="1.5" rx="8"/>
  <text x="{width/2}" y="34" font-family="Times New Roman, Times, serif" font-size="18" font-weight="bold" fill="#0f172a" text-anchor="middle">Fig. 2: 2x2 2D-Mesh Network-on-Chip Interconnect Topology</text>

  <!-- Router Coordinates -->
  <!-- R(0,0): (180, 160) -->
  <!-- R(1,0): (520, 160) -->
  <!-- R(0,1): (180, 390) -->
  <!-- R(1,1): (520, 390) -->

  <!-- Inter-Router Channels (East-West & North-South) -->
  <!-- Horizontal R00 <-> R10 -->
  <line x1="260" y1="150" x2="435" y2="150" stroke="#0284c7" stroke-width="3" marker-end="url(#bi-arr)"/>
  <line x1="440" y1="170" x2="265" y2="170" stroke="#0284c7" stroke-width="3" marker-end="url(#bi-arr)"/>
  <text x="350" y="142" font-family="Arial, sans-serif" font-size="10" font-weight="bold" fill="#0369a1" text-anchor="middle">East Channel (16-bit Flit + Credits)</text>
  <text x="350" y="186" font-family="Arial, sans-serif" font-size="10" font-weight="bold" fill="#0369a1" text-anchor="middle">West Channel (16-bit Flit + Credits)</text>

  <!-- Horizontal R01 <-> R11 -->
  <line x1="260" y1="380" x2="435" y2="380" stroke="#0284c7" stroke-width="3" marker-end="url(#bi-arr)"/>
  <line x1="440" y1="400" x2="265" y2="400" stroke="#0284c7" stroke-width="3" marker-end="url(#bi-arr)"/>
  <text x="350" y="372" font-family="Arial, sans-serif" font-size="10" font-weight="bold" fill="#0369a1" text-anchor="middle">East Channel (16-bit Flit + Credits)</text>
  <text x="350" y="416" font-family="Arial, sans-serif" font-size="10" font-weight="bold" fill="#0369a1" text-anchor="middle">West Channel (16-bit Flit + Credits)</text>

  <!-- Vertical R00 <-> R01 -->
  <line x1="170" y1="220" x2="170" y2="325" stroke="#0284c7" stroke-width="3" marker-end="url(#bi-arr)"/>
  <line x1="190" y1="330" x2="190" y2="225" stroke="#0284c7" stroke-width="3" marker-end="url(#bi-arr)"/>
  <text x="130" y="275" font-family="Arial, sans-serif" font-size="10" font-weight="bold" fill="#0369a1" text-anchor="middle" transform="rotate(-90 130 275)">South Channel</text>
  <text x="230" y="275" font-family="Arial, sans-serif" font-size="10" font-weight="bold" fill="#0369a1" text-anchor="middle" transform="rotate(-90 230 275)">North Channel</text>

  <!-- Vertical R10 <-> R11 -->
  <line x1="510" y1="220" x2="510" y2="325" stroke="#0284c7" stroke-width="3" marker-end="url(#bi-arr)"/>
  <line x1="530" y1="330" x2="530" y2="225" stroke="#0284c7" stroke-width="3" marker-end="url(#bi-arr)"/>
  <text x="470" y="275" font-family="Arial, sans-serif" font-size="10" font-weight="bold" fill="#0369a1" text-anchor="middle" transform="rotate(-90 470 275)">South Channel</text>
  <text x="570" y="275" font-family="Arial, sans-serif" font-size="10" font-weight="bold" fill="#0369a1" text-anchor="middle" transform="rotate(-90 570 275)">North Channel</text>

  <!-- Routers & PEs -->
'''
    routers = [
        ("PE0", "R (0, 0)", 180, 160, 60, 65),
        ("PE1", "R (1, 0)", 520, 160, 640, 65),
        ("PE2", "R (0, 1)", 180, 390, 60, 445),
        ("PE3", "R (1, 1) [Memory Ctrl]", 520, 390, 640, 445)
    ]
    for pe_lbl, r_lbl, rx, ry, px, py in routers:
        svg += f'''  <!-- Node: {r_lbl} -->
  <rect x="{rx-75}" y="{ry-50}" width="150" height="100" fill="#f8fafc" stroke="#334155" stroke-width="2" rx="8" filter="url(#mesh-shadow)"/>
  <text x="{rx}" y="{ry-22}" font-family="Times New Roman, Times, serif" font-size="16" font-weight="bold" fill="#0f172a" text-anchor="middle">{r_lbl}</text>
  <rect x="{rx-60}" y="{ry-10}" width="120" height="48" fill="#e2e8f0" stroke="#94a3b8" stroke-width="0.8" rx="4"/>
  <text x="{rx}" y="{ry+8}" font-family="Arial, sans-serif" font-size="10" font-weight="bold" fill="#1e293b" text-anchor="middle">5 Ports x 2 VCs</text>
  <text x="{rx}" y="{ry+24}" font-family="Arial, sans-serif" font-size="9" fill="#475569" text-anchor="middle">10x5 Crossbar Switch</text>

  <!-- PE Block -->
  <rect x="{px-45}" y="{py-25}" width="90" height="50" fill="#f0fdf4" stroke="#16a34a" stroke-width="1.5" rx="6" filter="url(#mesh-shadow)"/>
  <text x="{px}" y="{py+5}" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#166534" text-anchor="middle">{pe_lbl}</text>

  <!-- PE Interconnect Link -->
  <line x1="{px+45 if px < rx else px-45}" y1="{py}" x2="{rx-75 if px < rx else rx+75}" y2="{ry}" stroke="#15803d" stroke-width="2.2" stroke-dasharray="3,2" marker-end="url(#pe-arr)"/>
'''

    svg += '''</svg>'''
    fname = "fig2_mesh_topology.svg"
    with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f: f.write(svg)
    print(f"  [OK] Saved -> {os.path.join(out_dir, fname)}")

# ==============================================================================
# Architectural Figure 3: Flit Format & Trace Word Bit-Mapping
# ==============================================================================

def generate_fig3_flit_format(out_dir):
    width, height = 750, 420
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <filter id="fmt-shadow" x="-2%" y="-2%" width="104%" height="104%">
      <feDropShadow dx="1" dy="1" stdDeviation="2" flood-opacity="0.12"/>
    </filter>
  </defs>

  <rect width="100%" height="100%" fill="#ffffff"/>
  <rect x="8" y="8" width="{width-16}" height="{height-16}" fill="none" stroke="#cbd5e1" stroke-width="1.5" rx="8"/>
  <text x="{width/2}" y="32" font-family="Times New Roman, Times, serif" font-size="18" font-weight="bold" fill="#0f172a" text-anchor="middle">Fig. 3: 16-Bit Flit Wire Protocol &amp; 32-Bit Replay Trace Word</text>

  <!-- 1. 16-Bit Physical Flit Format -->
  <text x="50" y="72" font-family="Times New Roman, Times, serif" font-size="14" font-weight="bold" fill="#1e293b">A. 16-Bit Physical Flit Wire Format (Inter-Router &amp; Local PE Channels)</text>
  
  <g transform="translate(50, 85)">
    <!-- Bit markers -->
    <text x="35" y="-6" font-family="Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">[15:14]</text>
    <text x="110" y="-6" font-family="Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">[13:12]</text>
    <text x="185" y="-6" font-family="Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">[11:10]</text>
    <text x="260" y="-6" font-family="Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">[9:8]</text>
    <text x="335" y="-6" font-family="Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">[7:6]</text>
    <text x="400" y="-6" font-family="Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">[5]</text>
    <text x="530" y="-6" font-family="Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">[4:0]</text>

    <!-- Fields -->
    <rect x="0" y="0" width="70" height="42" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5"/>
    <text x="35" y="20" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#1e40af" text-anchor="middle">ftype</text>
    <text x="35" y="34" font-family="Arial, sans-serif" font-size="9" fill="#1e3a8a" text-anchor="middle">2 bits</text>

    <rect x="70" y="0" width="80" height="42" fill="#e0e7ff" stroke="#4338ca" stroke-width="1.5"/>
    <text x="110" y="20" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#312e81" text-anchor="middle">dest_x</text>
    <text x="110" y="34" font-family="Arial, sans-serif" font-size="9" fill="#312e81" text-anchor="middle">2 bits</text>

    <rect x="150" y="0" width="80" height="42" fill="#e0e7ff" stroke="#4338ca" stroke-width="1.5"/>
    <text x="190" y="20" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#312e81" text-anchor="middle">dest_y</text>
    <text x="190" y="34" font-family="Arial, sans-serif" font-size="9" fill="#312e81" text-anchor="middle">2 bits</text>

    <rect x="230" y="0" width="70" height="42" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>
    <text x="265" y="20" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#334155" text-anchor="middle">src_x</text>
    <text x="265" y="34" font-family="Arial, sans-serif" font-size="9" fill="#334155" text-anchor="middle">2 bits</text>

    <rect x="300" y="0" width="70" height="42" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>
    <text x="335" y="20" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#334155" text-anchor="middle">src_y</text>
    <text x="335" y="34" font-family="Arial, sans-serif" font-size="9" fill="#334155" text-anchor="middle">2 bits</text>

    <rect x="370" y="0" width="60" height="42" fill="#fef3c7" stroke="#d97706" stroke-width="1.5"/>
    <text x="400" y="20" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#92400e" text-anchor="middle">vc_id</text>
    <text x="400" y="34" font-family="Arial, sans-serif" font-size="9" fill="#92400e" text-anchor="middle">1 bit</text>

    <rect x="430" y="0" width="210" height="42" fill="#dcfce7" stroke="#16a34a" stroke-width="1.5"/>
    <text x="535" y="20" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#14532d" text-anchor="middle">payload (Packet Data / Checksum)</text>
    <text x="535" y="34" font-family="Arial, sans-serif" font-size="9" fill="#14532d" text-anchor="middle">5 bits</text>
  </g>

  <!-- Flit Type Table -->
  <g transform="translate(50, 140)">
    <rect width="640" height="34" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1" rx="4"/>
    <text x="15" y="22" font-family="Arial, sans-serif" font-size="10" font-weight="bold" fill="#334155">Flit Type Encoding:</text>
    <text x="140" y="22" font-family="Arial, sans-serif" font-size="10" fill="#1e40af"><tspan font-weight="bold">2'b11:</tspan> SINGLE</text>
    <text x="260" y="22" font-family="Arial, sans-serif" font-size="10" fill="#1e40af"><tspan font-weight="bold">2'b01:</tspan> HEAD (Route Init)</text>
    <text x="400" y="22" font-family="Arial, sans-serif" font-size="10" fill="#1e40af"><tspan font-weight="bold">2'b00:</tspan> BODY</text>
    <text x="510" y="22" font-family="Arial, sans-serif" font-size="10" fill="#1e40af"><tspan font-weight="bold">2'b10:</tspan> TAIL (Release)</text>
  </g>

  <!-- 2. 32-Bit Trace Replay Word Format -->
  <text x="50" y="215" font-family="Times New Roman, Times, serif" font-size="14" font-weight="bold" fill="#1e293b">B. 32-Bit Verification Trace Word Format ($readmemh Dataset File Ingestion)</text>

  <g transform="translate(50, 230)">
    <text x="105" y="-6" font-family="Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">[31:20] (12 bits)</text>
    <text x="245" y="-6" font-family="Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">[19:18] (2 bits)</text>
    <text x="295" y="-6" font-family="Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">[17:16]</text>
    <text x="475" y="-6" font-family="Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">[15:0] (16 bits)</text>

    <rect x="0" y="0" width="210" height="42" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
    <text x="105" y="20" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#991b1b" text-anchor="middle">inject_cycle</text>
    <text x="105" y="34" font-family="Arial, sans-serif" font-size="9" fill="#991b1b" text-anchor="middle">Clock Cycle Timestamp (0..4095)</text>

    <rect x="210" y="0" width="70" height="42" fill="#fef3c7" stroke="#d97706" stroke-width="1.5"/>
    <text x="245" y="20" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#92400e" text-anchor="middle">src_pe</text>
    <text x="245" y="34" font-family="Arial, sans-serif" font-size="9" fill="#92400e" text-anchor="middle">PE 0..3</text>

    <rect x="280" y="0" width="30" height="42" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"/>
    <text x="295" y="25" font-family="Arial, sans-serif" font-size="9" fill="#64748b" text-anchor="middle">Rsrv</text>

    <rect x="310" y="0" width="330" height="42" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5"/>
    <text x="475" y="20" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#1e40af" text-anchor="middle">16-bit Flit Payload Word</text>
    <text x="475" y="34" font-family="Arial, sans-serif" font-size="9" fill="#1e40af" text-anchor="middle">Directly driven into Router input on inject_cycle</text>
  </g>

  <!-- Flow Control Invariant Note -->
  <g transform="translate(50, 305)">
    <rect width="640" height="90" fill="#f0fdf4" stroke="#86efac" stroke-width="1.2" rx="6"/>
    <text x="15" y="22" font-family="Times New Roman, Times, serif" font-size="12" font-weight="bold" fill="#14532d">Formal Invariant Guarantees:</text>
    <text x="15" y="42" font-family="Arial, sans-serif" font-size="10.5" fill="#166534">&#8226; <tspan font-weight="bold">Dimension Order Turn Model:</tspan> Deadlock-free by eliminating all four Y &#8594; X turns.</text>
    <text x="15" y="60" font-family="Arial, sans-serif" font-size="10.5" fill="#166534">&#8226; <tspan font-weight="bold">Credit Flow Invariant:</tspan> Credit Count C(t) + Queue Occupancy Q(t) = C_max = 8 (Zero buffer overflow).</text>
    <text x="15" y="78" font-family="Arial, sans-serif" font-size="10.5" fill="#166534">&#8226; <tspan font-weight="bold">Fairness Bound:</tspan> 10-input Round-Robin guarantees worst-case grant waiting delay &#8804; 9 cycles.</text>
  </g>
</svg>'''
    fname = "fig3_flit_format.svg"
    with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f: f.write(svg)
    print(f"  [OK] Saved -> {os.path.join(out_dir, fname)}")

# ==============================================================================
# Architectural Figure 4: Round-Robin Arbiter Priority Progression FSM
# ==============================================================================

def generate_fig4_arbiter_fsm(out_dir):
    width, height = 700, 450
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <marker id="fsm-arr" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/>
    </marker>
  </defs>

  <rect width="100%" height="100%" fill="#ffffff"/>
  <rect x="8" y="8" width="{width-16}" height="{height-16}" fill="none" stroke="#cbd5e1" stroke-width="1.5" rx="8"/>
  <text x="{width/2}" y="32" font-family="Times New Roman, Times, serif" font-size="18" font-weight="bold" fill="#0f172a" text-anchor="middle">Fig. 4: 10-Input Round-Robin Arbiter Cyclic Priority Progression</text>

  <!-- Circular 10-State Priority Ring -->
  <g transform="translate(350, 230)">
    <!-- Ring circle -->
    <circle cx="0" cy="0" r="140" fill="none" stroke="#e2e8f0" stroke-width="2" stroke-dasharray="4,4"/>

    <!-- Center equation -->
    <rect x="-95" y="-35" width="190" height="70" fill="#f8fafc" stroke="#94a3b8" stroke-width="1" rx="6"/>
    <text x="0" y="-12" font-family="Times New Roman, Times, serif" font-size="12" font-weight="bold" fill="#0f172a" text-anchor="middle">Priority Pointer Update:</text>
    <text x="0" y="8" font-family="Courier New, monospace" font-size="12" font-weight="bold" fill="#b91c1c" text-anchor="middle">&#960;(t+1) = (g(t) + 1) % 10</text>
    <text x="0" y="25" font-family="Arial, sans-serif" font-size="10" fill="#15803d" text-anchor="middle">Bounded Wait &#8804; 9 Cycles</text>
'''
    import math
    states = ["L0 (0)", "L1 (1)", "N0 (2)", "N1 (3)", "S0 (4)", "S1 (5)", "E0 (6)", "E1 (7)", "W0 (8)", "W1 (9)"]
    for i in range(10):
        angle = (i * 36 - 90) * math.pi / 180.0
        cx = 140 * math.cos(angle)
        cy = 140 * math.sin(angle)
        svg += f'''    <!-- Node {i} -->
    <circle cx="{cx:.1f}" cy="{cy:.1f}" r="22" fill="#eff6ff" stroke="#2563eb" stroke-width="1.8"/>
    <text x="{cx:.1f}" y="{cy+4:.1f}" font-family="Arial, sans-serif" font-size="9" font-weight="bold" fill="#1e40af" text-anchor="middle">{states[i]}</text>
'''
    svg += '''  </g>
  <!-- Caption -->
  <text x="350" y="420" font-family="Times New Roman, Times, serif" font-size="12" font-style="italic" fill="#475569" text-anchor="middle">Rotating priority ensures zero starvation and exact 10.0% bandwidth allocation across 10 Virtual Channels.</text>
</svg>'''
    fname = "fig4_arbiter_fsm.svg"
    with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f: f.write(svg)
    print(f"  [OK] Saved -> {os.path.join(out_dir, fname)}")

# ==============================================================================
# Master Generator CLI
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="NoC Router Publication Plot & Figure Generator")
    parser.add_argument("--style", choices=["dark", "academic", "all"], default="all",
                        help="Plot visual style: academic (IEEE white), dark (GitHub web), or all (default)")
    parser.add_argument("--outdir", default=None, help="Target output directory override")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_dir  = os.path.join(base_dir, "..", "docs", "plots")
    acad_dir = os.path.join(base_dir, "..", "paper", "figures")
    docs_acad_dir = os.path.join(base_dir, "..", "docs", "plots", "academic")

    ensure_dir(web_dir)
    ensure_dir(acad_dir)
    ensure_dir(docs_acad_dir)

    target_styles = ["academic", "dark"] if args.style == "all" else [args.style]

    print("=" * 76)
    print("  NETWORK-ON-CHIP (NoC) PUBLICATION GRAPH & FIGURE GENERATOR")
    print(f"  Target Styles: {target_styles}")
    print("=" * 76)

    for style in target_styles:
        out_dirs = [acad_dir, docs_acad_dir] if style == "academic" else [web_dir]
        if args.outdir:
            out_dirs = [args.outdir]

        for d in out_dirs:
            ensure_dir(d)
            print(f"\n--> Generating Performance Plots ({style.upper()}) in: {os.path.abspath(d)}")
            plot1_latency(d, style)
            plot2_throughput(d, style)
            plot3_hotspot_breakdown(d, style)
            plot4_hol_mitigation(d, style)
            plot5_fpga_hardware(d, style)
            plot6_arbitration(d, style)
            plot7_multihop_cdf(d, style)
            plot8_power_breakdown(d, style)

    # Always generate the 4 architectural figures in paper/figures and docs/plots/academic
    print(f"\n--> Generating Microarchitectural Block Diagrams...")
    for fig_dir in [acad_dir, docs_acad_dir]:
        generate_fig1_router_architecture(fig_dir)
        generate_fig2_mesh_topology(fig_dir)
        generate_fig3_flit_format(fig_dir)
        generate_fig4_arbiter_fsm(fig_dir)

    print("\n" + "=" * 76)
    print("  All Plots and Microarchitectural Figures Successfully Synthesized!")
    print("=" * 76 + "\n")

if __name__ == '__main__':
    main()
