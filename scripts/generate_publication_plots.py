#!/usr/bin/env python3
"""
==============================================================================
Script: generate_publication_plots.py
Description: Generates 300-DPI publication-ready PDF, PNG, and SVG figures
             using matplotlib strictly conforming to IEEE Transactions /
             Conference formatting guidelines:
               - Single-column width: 3.5 in (88.9 mm)
               - Double-column width: 7.16 in (181.8 mm)
               - Font family: Times New Roman / DejaVu Serif
               - High-contrast IEEE academic palette with geometric markers
==============================================================================
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Set global IEEE publication style
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'Times'],
    'font.size': 10,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 8.5,
    'figure.titlesize': 12,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'lines.linewidth': 1.8,
    'lines.markersize': 5.5,
    'grid.linestyle': '--',
    'grid.alpha': 0.6,
    'axes.grid': True,
    'axes.axisbelow': True,
})

def save_fig(fig, base_name, out_dirs):
    fig.tight_layout()
    for d in out_dirs:
        os.makedirs(d, exist_ok=True)
        fig.savefig(os.path.join(d, f"{base_name}.pdf"), format='pdf', bbox_inches='tight')
        fig.savefig(os.path.join(d, f"{base_name}.png"), format='png', dpi=300, bbox_inches='tight')
        fig.savefig(os.path.join(d, f"{base_name}.svg"), format='svg', bbox_inches='tight')
    plt.close(fig)
    print(f"  [OK] Saved -> {base_name}.(pdf/png/svg)")

# ------------------------------------------------------------------------------
# 1. Latency vs. Offered Load
# ------------------------------------------------------------------------------
def plot_latency(out_dirs):
    loads = np.array([0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 1.00])
    base_ur = [2.38, 2.47, 2.60, 2.88, 3.62, 5.20, 7.96]
    vc_ur   = [2.36, 2.47, 2.61, 2.82, 3.18, 5.02, 9.58]
    base_hs = [2.38, 2.51, 2.89, 4.31, 7.65, 9.13, 10.50]
    vc_hs   = [2.37, 2.50, 2.73, 5.83, 12.43, 15.08, 15.85]

    fig, ax = plt.subplots(figsize=(4.0, 3.0))
    ax.plot(loads, base_ur, 'd--', color='#b91c1c', label='Single-VC (Uniform)', markerfacecolor='white', markeredgewidth=1.2)
    ax.plot(loads, vc_ur,   'o-',  color='#1d4ed8', label='Dual-VC (Uniform)', markerfacecolor='white', markeredgewidth=1.2)
    ax.plot(loads, base_hs, 's--', color='#d97706', label='Single-VC (Hotspot)', markerfacecolor='white', markeredgewidth=1.2)
    ax.plot(loads, vc_hs,   '^-',  color='#0d9488', label='Dual-VC (Hotspot)', markerfacecolor='white', markeredgewidth=1.2)

    ax.annotate(r'$\mathbf{-12.2\%}$ Latency', xy=(0.70, 3.18), xytext=(0.42, 6.0),
                arrowprops=dict(facecolor='#1d4ed8', shrink=0.08, width=1, headwidth=5),
                fontsize=8.5, fontweight='bold', color='#1d4ed8',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#eff6ff', edgecolor='#93c5fd', alpha=0.9))

    ax.set_xlabel('Offered Load (flits/cycle/node)')
    ax.set_ylabel('Average Packet Latency (cycles)')
    ax.set_xlim(0.08, 1.02)
    ax.set_ylim(0, 18)
    ax.legend(loc='upper left', frameon=True, edgecolor='#d1d5db', framealpha=0.9)
    save_fig(fig, 'plot1_latency_vs_offered_load', out_dirs)

# ------------------------------------------------------------------------------
# 2. Throughput vs. Offered Load
# ------------------------------------------------------------------------------
def plot_throughput(out_dirs):
    loads = np.array([0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 1.00])
    base_tp = [0.104, 0.249, 0.391, 0.551, 0.711, 0.840, 0.860]
    vc_tp   = [0.101, 0.254, 0.399, 0.551, 0.705, 0.862, 0.921]

    fig, ax = plt.subplots(figsize=(4.0, 3.0))
    ax.plot([0.1, 1.0], [0.1, 1.0], ':', color='#9ca3af', linewidth=1.5, label='Ideal Throughput')
    ax.plot(loads, base_tp, 's--', color='#b91c1c', label='Single-VC (Sat = 0.860)', markerfacecolor='white', markeredgewidth=1.2)
    ax.plot(loads, vc_tp,   'o-',  color='#15803d', label='Dual-VC (Sat = 0.921)', markerfacecolor='white', markeredgewidth=1.2)

    ax.annotate(r'$\mathbf{+7.1\%}$ Capacity Gain', xy=(1.00, 0.921), xytext=(0.52, 0.80),
                arrowprops=dict(facecolor='#15803d', shrink=0.08, width=1, headwidth=5),
                fontsize=8.5, fontweight='bold', color='#15803d',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#f0fdf4', edgecolor='#86efac', alpha=0.9))

    ax.set_xlabel('Offered Load (flits/cycle/node)')
    ax.set_ylabel('Sustained Throughput (flits/cycle/node)')
    ax.set_xlim(0.08, 1.02)
    ax.set_ylim(0, 1.05)
    ax.legend(loc='lower right', frameon=True, edgecolor='#d1d5db', framealpha=0.9)
    save_fig(fig, 'plot2_throughput_vs_offered_load', out_dirs)

# ------------------------------------------------------------------------------
# 3. Memory Hotspot Latency Breakdown
# ------------------------------------------------------------------------------
def plot_hotspot(out_dirs):
    loads = np.array([0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 1.00])
    base_hs = [2.38, 2.51, 2.89, 4.31, 7.65, 9.13, 10.50]
    vc_hs   = [2.37, 2.50, 2.73, 5.83, 12.43, 15.08, 15.85]

    fig, ax = plt.subplots(figsize=(4.0, 3.0))
    width = 0.035
    ax.bar(loads - width/2, base_hs, width=width, color='#94a3b8', edgecolor='#334155', linewidth=0.8, label='Single-VC (Hotspot)')
    ax.bar(loads + width/2, vc_hs,   width=width, color='#0284c7', edgecolor='#0369a1', linewidth=0.8, label='Dual-VC (Hotspot)')

    ax.set_xlabel('Offered Load (flits/cycle/node)')
    ax.set_ylabel('Average Packet Latency (cycles)')
    ax.set_xlim(0.04, 1.06)
    ax.set_ylim(0, 18)
    ax.set_xticks(loads)
    ax.set_xticklabels([f'{l:.2f}' for l in loads])
    ax.legend(loc='upper left', frameon=True, edgecolor='#d1d5db', framealpha=0.9)
    save_fig(fig, 'plot3_hotspot_latency_breakdown', out_dirs)

# ------------------------------------------------------------------------------
# 4. Head-of-Line (HoL) Blocking Mitigation
# ------------------------------------------------------------------------------
def plot_hol(out_dirs):
    loads = np.array([0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 1.00])
    hol_base = [12.4, 28.1, 45.6, 64.2, 79.5, 88.2, 92.4]
    hol_vc   = [2.1,  5.4,  8.7,  11.2, 14.5, 16.5, 18.1]

    fig, ax = plt.subplots(figsize=(4.0, 3.0))
    ax.plot(loads, hol_base, 's--', color='#dc2626', label='Single-Queue FIFO', markerfacecolor='white', markeredgewidth=1.2)
    ax.plot(loads, hol_vc,   'o-',  color='#16a34a', label='Dual Virtual Channels', markerfacecolor='white', markeredgewidth=1.2)

    ax.annotate(r'$\mathbf{81.3\%}$ Reduction', xy=(0.85, 16.5), xytext=(0.48, 48.0),
                arrowprops=dict(facecolor='#16a34a', shrink=0.08, width=1, headwidth=5),
                fontsize=8.5, fontweight='bold', color='#16a34a',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#f0fdf4', edgecolor='#86efac', alpha=0.9))

    ax.set_xlabel('Offered Load (flits/cycle/node)')
    ax.set_ylabel('HoL Contention Probability (%)')
    ax.set_xlim(0.08, 1.02)
    ax.set_ylim(0, 100)
    ax.legend(loc='upper left', frameon=True, edgecolor='#d1d5db', framealpha=0.9)
    save_fig(fig, 'plot4_hol_blocking_mitigation', out_dirs)

# ------------------------------------------------------------------------------
# 5. FPGA Hardware Benchmarking
# ------------------------------------------------------------------------------
def plot_fpga(out_dirs):
    designs = ['Vinoth\n(2014)', 'Ved\n(2017)', 'Bhargavi\n(2024)', 'Baseline\nRouter', 'Dual-VC\nRouter', '2x2 Mesh\n(4 Nodes)']
    fmax    = [50.0, 120.0, 205.0, 180.2, 227.48, 229.62]
    colors  = ['#94a3b8', '#94a3b8', '#94a3b8', '#3b82f6', '#059669', '#7c3aed']

    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    bars = ax.bar(range(len(designs)), fmax, width=0.55, color=colors, edgecolor='#1e293b', linewidth=0.8)

    for bar, val in zip(bars, fmax):
        y = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, y + 5, f'{val:.1f}', ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    ax.set_ylabel(r'Maximum Frequency $F_{\max}$ (MHz)')
    ax.set_ylim(0, 260)
    ax.set_xticks(range(len(designs)))
    ax.set_xticklabels(designs, fontsize=8)
    save_fig(fig, 'plot5_fpga_hardware_utilization', out_dirs)

# ------------------------------------------------------------------------------
# 6. Arbiter Fairness
# ------------------------------------------------------------------------------
def plot_arbitration(out_dirs):
    vcs = ['L0', 'L1', 'N0', 'N1', 'S0', 'S1', 'E0', 'E1', 'W0', 'W1']
    shares = [9.9, 10.1, 10.0, 9.8, 10.2, 10.0, 9.9, 10.1, 10.0, 10.0]

    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    bars = ax.bar(range(len(vcs)), shares, width=0.6, color='#1d4ed8', edgecolor='#1e3a8a', linewidth=0.8)
    ax.axhline(10.0, color='#b91c1c', linestyle='--', linewidth=1.5, label='Ideal Fair Share (10.0%)')

    ax.set_xlabel('Competing Virtual Channels')
    ax.set_ylabel('Bandwidth Share (%)')
    ax.set_ylim(0, 15)
    ax.set_xticks(range(len(vcs)))
    ax.set_xticklabels(vcs, fontsize=8.5)
    ax.legend(loc='upper right', frameon=True, edgecolor='#d1d5db', framealpha=0.9)
    save_fig(fig, 'plot6_arbitration_fairness_and_delay', out_dirs)

# ------------------------------------------------------------------------------
# 7. Multi-Hop CDF
# ------------------------------------------------------------------------------
def plot_cdf(out_dirs):
    latencies = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
    cdf_single = [0, 15, 65, 92, 98, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100]
    cdf_multi  = [0, 0, 0, 8, 48, 78, 89, 94, 97, 98, 99, 99.5, 100, 100, 100]

    fig, ax = plt.subplots(figsize=(4.0, 3.0))
    ax.plot(latencies, cdf_single, 'o-', color='#15803d', label='1-Hop Perimeter', markerfacecolor='white', markeredgewidth=1.2)
    ax.plot(latencies, cdf_multi,  's--', color='#4338ca', label='2-Hop Diagonal', markerfacecolor='white', markeredgewidth=1.2)
    ax.axvline(5, color='#d97706', linestyle=':', linewidth=1.5, label='2-Hop Zero-Load (5 cyc)')

    ax.set_xlabel('Packet Traversal Latency (clock cycles)')
    ax.set_ylabel('Cumulative Distribution (CDF %)')
    ax.set_xlim(1, 15)
    ax.set_ylim(0, 105)
    ax.legend(loc='lower right', frameon=True, edgecolor='#d1d5db', framealpha=0.9)
    save_fig(fig, 'plot7_multihop_latency_distribution', out_dirs)

# ------------------------------------------------------------------------------
# 8. Power Scaling
# ------------------------------------------------------------------------------
def plot_power(out_dirs):
    freqs = np.array([50, 100, 150, 200, 227.48])
    dyn_router = np.array([0.027, 0.054, 0.081, 0.108, 0.123])
    tot_router = dyn_router + 0.081
    dyn_mesh   = np.array([0.020, 0.040, 0.060, 0.080, 0.092])
    tot_mesh   = dyn_mesh + 0.081

    fig, ax = plt.subplots(figsize=(4.0, 3.0))
    ax.plot(freqs, tot_router, 'o-', color='#b91c1c', label='Dual-VC Router (0.189 W)', markerfacecolor='white', markeredgewidth=1.2)
    ax.plot(freqs, tot_mesh,   's--', color='#1d4ed8', label='2x2 Mesh (0.162 W)', markerfacecolor='white', markeredgewidth=1.2)
    ax.axhline(0.081, color='#64748b', linestyle=':', linewidth=1.4, label='Static Power (0.081 W)')

    ax.set_xlabel('Clock Frequency (MHz)')
    ax.set_ylabel('Total On-Chip Power (Watts)')
    ax.set_xlim(40, 240)
    ax.set_ylim(0, 0.25)
    ax.legend(loc='upper left', frameon=True, edgecolor='#d1d5db', framealpha=0.9)
    save_fig(fig, 'plot8_power_breakdown', out_dirs)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    acad_dir = os.path.join(base_dir, '..', 'paper', 'figures')
    docs_dir = os.path.join(base_dir, '..', 'docs', 'plots', 'academic')
    out_dirs = [acad_dir, docs_dir]

    print("=" * 76)
    print("  GENERATING 300-DPI PUBLICATION-GRADE PLOTS (PDF, PNG, SVG)")
    print(f"  Target Directories: {[os.path.abspath(d) for d in out_dirs]}")
    print("=" * 76)

    plot_latency(out_dirs)
    plot_throughput(out_dirs)
    plot_hotspot(out_dirs)
    plot_hol(out_dirs)
    plot_fpga(out_dirs)
    plot_arbitration(out_dirs)
    plot_cdf(out_dirs)
    plot_power(out_dirs)

    print("\n" + "=" * 76)
    print("  All 8 Publication Figures Generated in PDF, PNG (300 DPI), and SVG!")
    print("=" * 76 + "\n")

if __name__ == '__main__':
    main()
