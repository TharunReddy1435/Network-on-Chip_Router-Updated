#!/usr/bin/env python3
"""
Publication-Quality Architectural Diagram Generator for IEEE Conference Paper.
Generates:
  - fig1_router_microarchitecture (PDF, PNG, SVG)
  - fig2_mesh_topology (PDF, PNG, SVG)
  - fig3_flit_format (PDF, PNG, SVG)
  - fig4_arbiter_fsm (PDF, PNG, SVG)

Target directories:
  - paper/figures/
  - docs/plots/academic/
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle

OUT_DIRS = [
    os.path.join("paper", "figures"),
    os.path.join("docs", "plots", "academic"),
]

for d in OUT_DIRS:
    os.makedirs(d, exist_ok=True)

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10
plt.rcParams['mathtext.fontset'] = 'cm'

def save_fig(fig, base_name):
    for d in OUT_DIRS:
        pdf_path = os.path.join(d, f"{base_name}.pdf")
        png_path = os.path.join(d, f"{base_name}.png")
        svg_path = os.path.join(d, f"{base_name}.svg")
        fig.savefig(pdf_path, bbox_inches='tight', dpi=300)
        fig.savefig(png_path, bbox_inches='tight', dpi=300)
        fig.savefig(svg_path, bbox_inches='tight')
    plt.close(fig)
    print(f"  [OK] Saved -> {base_name}.(pdf/png/svg)")

# ---------------------------------------------------------------------------
# FIG 1: 5-PORT DUAL-VC ROUTER MICROARCHITECTURE
# ---------------------------------------------------------------------------
def draw_fig1():
    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Background Router Box
    router_box = patches.FancyBboxPatch((15, 5), 72, 90, boxstyle="round,pad=1.5",
                                        facecolor="#f8f9fa", edgecolor="#333333", linewidth=2.0)
    ax.add_patch(router_box)
    ax.text(51, 92, "5-Port Virtual-Channel NoC Router Microarchitecture", 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#111111')

    # Ports labels
    ports = [("Local In", 22, 78), ("North In", 22, 60), ("South In", 22, 42), ("East In", 22, 24), ("West In", 22, 10)]
    for name, x, y in ports:
        # Physical port box
        ax.add_patch(patches.Rectangle((x-18, y-3), 14, 8, facecolor='#e9ecef', edgecolor='#495057', lw=1.2))
        ax.text(x-11, y+1, name, ha='center', va='center', fontsize=8, fontweight='bold')
        # Arrow into VC
        ax.annotate('', xy=(x, y+2), xytext=(x-4, y+2),
                    arrowprops=dict(arrowstyle="->", lw=1.2, color='#212529'))
        ax.annotate('', xy=(x, y-1), xytext=(x-4, y-1),
                    arrowprops=dict(arrowstyle="->", lw=1.2, color='#212529'))

        # VC0 and VC1 buffers
        ax.add_patch(patches.Rectangle((x, y+1), 16, 4.5, facecolor='#d0ebff', edgecolor='#1971c2', lw=1.2))
        ax.text(x+8, y+3.25, f"{name[:2]} VC0 (FWFT)", ha='center', va='center', fontsize=7.5, color='#0c4a6e')

        ax.add_patch(patches.Rectangle((x, y-3), 16, 4.5, facecolor='#d0ebff', edgecolor='#1971c2', lw=1.2))
        ax.text(x+8, y-0.75, f"{name[:2]} VC1 (FWFT)", ha='center', va='center', fontsize=7.5, color='#0c4a6e')

    # Route Computation Block
    ax.add_patch(patches.FancyBboxPatch((42, 15), 12, 70, boxstyle="round,pad=0.5",
                                        facecolor='#d3f9d8', edgecolor='#2b8a3e', lw=1.5))
    ax.text(48, 50, "Route\nComputation\n(RC Units)\n\nXY Routing\nAlgorithm\n\n10 Lanes",
            ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1b4332')

    # Connections from FIFOs to RC
    ax.annotate('', xy=(42, 50), xytext=(38, 50),
                arrowprops=dict(arrowstyle="->", lw=1.5, color='#2b8a3e'))

    # Round Robin Arbiters Block
    ax.add_patch(patches.FancyBboxPatch((58, 15), 12, 70, boxstyle="round,pad=0.5",
                                        facecolor='#fff3bf', edgecolor='#e67700', lw=1.5))
    ax.text(64, 50, "Switch\nAllocation\n(SA)\n\n5x 10-to-1\nRound-Robin\nArbiters\n\nCredit Aware",
            ha='center', va='center', fontsize=8.5, fontweight='bold', color='#7c2d12')

    # Arrow RC -> SA
    ax.annotate('', xy=(58, 50), xytext=(54, 50),
                arrowprops=dict(arrowstyle="->", lw=1.5, color='#e67700'))

    # Crossbar Switch Fabric
    ax.add_patch(patches.FancyBboxPatch((74, 15), 11, 70, boxstyle="round,pad=0.5",
                                        facecolor='#ffe3e3', edgecolor='#c92a2a', lw=1.5))
    ax.text(79.5, 50, "10x5\nCrossbar\nSwitch\nFabric\n\nMultiplexer\nArray",
            ha='center', va='center', fontsize=8.5, fontweight='bold', color='#991b1b')

    # Output Ports
    out_ports = [("Local Out", 90, 78), ("North Out", 90, 60), ("South Out", 90, 42), ("East Out", 90, 24), ("West Out", 90, 10)]
    for name, x, y in out_ports:
        # Arrow from XBar to Out
        ax.annotate('', xy=(x, y+1), xytext=(85, y+1),
                    arrowprops=dict(arrowstyle="->", lw=1.2, color='#c92a2a'))
        ax.add_patch(patches.Rectangle((x, y-3), 14, 8, facecolor='#e9ecef', edgecolor='#495057', lw=1.2))
        ax.text(x+7, y+1, name, ha='center', va='center', fontsize=8, fontweight='bold')

    # Credit Feedback Counter Box
    ax.add_patch(patches.FancyBboxPatch((42, 6), 43, 6, boxstyle="round,pad=0.3",
                                        facecolor='#f3f0ff', edgecolor='#5f3dc4', lw=1.2))
    ax.text(63.5, 9, "Credit Counters (Flow Control) | Conservation Invariant: C(t) + Q(t) = Cmax",
            ha='center', va='center', fontsize=7.5, fontweight='bold', color='#49129c')

    save_fig(fig, "fig1_router_microarchitecture")

# ---------------------------------------------------------------------------
# FIG 2: 2x2 MESH TOPOLOGY
# ---------------------------------------------------------------------------
def draw_fig2():
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    ax.text(50, 95, "2x2 2D-Mesh Interconnect Architecture", 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#111111')

    # Node positions: (0,0), (1,0), (0,1), (1,1)
    nodes = {
        "R00": (25, 70, "Router (0,0)", "PE0", "#1971c2"),
        "R10": (75, 70, "Router (1,0)", "PE1", "#2b8a3e"),
        "R01": (25, 25, "Router (0,1)", "PE2", "#e67700"),
        "R11": (75, 25, "Router (1,1)", "PE3 (Hotspot)", "#c92a2a"),
    }

    for key, (x, y, rname, pename, col) in nodes.items():
        # Router box
        ax.add_patch(patches.FancyBboxPatch((x-12, y-10), 24, 20, boxstyle="round,pad=0.5",
                                            facecolor='#f8f9fa', edgecolor=col, linewidth=2.0))
        ax.text(x, y+4, rname, ha='center', va='center', fontsize=9, fontweight='bold', color='#212529')
        
        # PE box attached to Local port
        pe_x = x - 18 if x < 50 else x + 18
        ax.add_patch(patches.Rectangle((pe_x-6, y-4), 12, 8, facecolor=col, edgecolor='#111111', lw=1.2))
        ax.text(pe_x, y, pename, ha='center', va='center', fontsize=8, fontweight='bold', color='#ffffff')
        # Link PE <-> Router
        ax.annotate('', xy=(x-12 if x<50 else x+12, y), xytext=(pe_x+6 if x<50 else pe_x-6, y),
                    arrowprops=dict(arrowstyle="<->", lw=1.5, color=col))

    # Horizontal links (R00 <-> R10 and R01 <-> R11)
    # Top link
    ax.annotate('', xy=(63, 73), xytext=(37, 73),
                arrowprops=dict(arrowstyle="->", lw=1.8, color='#1971c2'))
    ax.annotate('', xy=(37, 67), xytext=(63, 67),
                arrowprops=dict(arrowstyle="->", lw=1.8, color='#2b8a3e'))
    ax.text(50, 75, "East Data / West Credit", ha='center', va='bottom', fontsize=7.5, color='#1971c2')
    ax.text(50, 65, "West Data / East Credit", ha='center', va='top', fontsize=7.5, color='#2b8a3e')

    # Bottom link
    ax.annotate('', xy=(63, 28), xytext=(37, 28),
                arrowprops=dict(arrowstyle="->", lw=1.8, color='#e67700'))
    ax.annotate('', xy=(37, 22), xytext=(63, 22),
                arrowprops=dict(arrowstyle="->", lw=1.8, color='#c92a2a'))
    ax.text(50, 30, "East Data / West Credit", ha='center', va='bottom', fontsize=7.5, color='#e67700')
    ax.text(50, 20, "West Data / East Credit", ha='center', va='top', fontsize=7.5, color='#c92a2a')

    # Vertical links (R00 <-> R01 and R10 <-> R11)
    # Left vertical
    ax.annotate('', xy=(22, 35), xytext=(22, 60),
                arrowprops=dict(arrowstyle="->", lw=1.8, color='#1971c2'))
    ax.annotate('', xy=(28, 60), xytext=(28, 35),
                arrowprops=dict(arrowstyle="->", lw=1.8, color='#e67700'))
    ax.text(18, 47.5, "South Data", ha='right', va='center', fontsize=7.5, rotation=90, color='#1971c2')
    ax.text(32, 47.5, "North Data", ha='left', va='center', fontsize=7.5, rotation=90, color='#e67700')

    # Right vertical
    ax.annotate('', xy=(72, 35), xytext=(72, 60),
                arrowprops=dict(arrowstyle="->", lw=1.8, color='#2b8a3e'))
    ax.annotate('', xy=(78, 60), xytext=(78, 35),
                arrowprops=dict(arrowstyle="->", lw=1.8, color='#c92a2a'))
    ax.text(68, 47.5, "South Data", ha='right', va='center', fontsize=7.5, rotation=90, color='#2b8a3e')
    ax.text(82, 47.5, "North Data", ha='left', va='center', fontsize=7.5, rotation=90, color='#c92a2a')

    save_fig(fig, "fig2_mesh_topology")

# ---------------------------------------------------------------------------
# FIG 3: 16-BIT FLIT PACKET FORMAT
# ---------------------------------------------------------------------------
def draw_fig3():
    fig, ax = plt.subplots(figsize=(9, 3.2))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 40)
    ax.axis('off')

    ax.text(50, 36, "16-Bit Standardized Flit Packet Wire Format", 
            ha='center', va='center', fontsize=11, fontweight='bold', color='#111111')

    # Field specifications: (name, bits, width, color, text_color, desc)
    fields = [
        ("ftype [15:14]", 2, 14, "#339af0", "#ffffff", "Flit Type (00:Body, 01:Head, 10:Tail, 11:Single)"),
        ("dest_x [13:12]", 2, 13, "#51cf66", "#ffffff", "Destination X Coordinate (0-1)"),
        ("dest_y [11:10]", 2, 13, "#69db7c", "#111111", "Destination Y Coordinate (0-1)"),
        ("src_x [9:8]", 2, 12, "#ffd43b", "#111111", "Source X Coordinate (0-1)"),
        ("src_y [7:6]", 2, 12, "#fcc419", "#111111", "Source Y Coordinate (0-1)"),
        ("vc_id [5]", 1, 9, "#ff922b", "#ffffff", "Virtual Channel (0: VC0, 1: VC1)"),
        ("payload [4:0]", 5, 23, "#ff6b6b", "#ffffff", "Data Payload (5-bit Word)"),
    ]

    x_start = 2
    y_pos = 18
    height = 10

    for name, bits, width, bg_col, txt_col, desc in fields:
        ax.add_patch(patches.Rectangle((x_start, y_pos), width, height, facecolor=bg_col, edgecolor='#212529', lw=1.2))
        ax.text(x_start + width/2, y_pos + height/2 + 1, name, ha='center', va='center', fontsize=8, fontweight='bold', color=txt_col)
        ax.text(x_start + width/2, y_pos + height/2 - 2.5, f"{bits}b", ha='center', va='center', fontsize=7, color=txt_col)
        x_start += width

    # Explanatory legend below
    ax.text(9, 10, "Flit Header & Routing Information (Dimension-Order XY)", ha='left', va='center', fontsize=8, color='#2b8a3e')
    ax.text(65, 10, "VC Steering & Data Payload", ha='left', va='center', fontsize=8, color='#c92a2a')

    save_fig(fig, "fig3_flit_format")

# ---------------------------------------------------------------------------
# FIG 4: 10-TO-1 ARBITER FSM & PRIORITY ROTATION
# ---------------------------------------------------------------------------
def draw_fig4():
    import numpy as np
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    ax.axis('off')

    ax.text(0, 1.28, "10-to-1 Round-Robin Priority Rotation Mechanism", 
            ha='center', va='center', fontsize=11, fontweight='bold', color='#111111')
    ax.text(0, 1.15, "pi(t+1) = (g(t) + 1) mod 10  -->  Worst-case latency <= 9 cycles", 
            ha='center', va='center', fontsize=9, color='#495057')

    radius = 0.85
    labels = ["L0 (0)", "L1 (1)", "N0 (2)", "N1 (3)", "S0 (4)", 
              "S1 (5)", "E0 (6)", "E1 (7)", "W0 (8)", "W1 (9)"]

    angles = [np.pi/2 - i * (2*np.pi/10) for i in range(10)]

    for i, (ang, lbl) in enumerate(zip(angles, labels)):
        x = radius * np.cos(ang)
        y = radius * np.sin(ang)

        # Draw circle node
        circle = patches.Circle((x, y), 0.13, facecolor="#e7f5ff" if i%2==0 else "#fff4e6", 
                                edgecolor="#1971c2" if i%2==0 else "#e8590c", lw=1.5)
        ax.add_patch(circle)
        ax.text(x, y, lbl, ha='center', va='center', fontsize=7.5, fontweight='bold', color='#212529')

        # Curved arrow to next node
        next_ang = angles[(i + 1) % 10]
        mid_ang = (ang + next_ang) / 2
        # Use arc patch or annotate
        ax.annotate('', 
                    xy=(radius * np.cos(next_ang) - 0.08 * np.sin(next_ang), 
                        radius * np.sin(next_ang) + 0.08 * np.cos(next_ang)),
                    xytext=(x - 0.08 * np.sin(ang), y + 0.08 * np.cos(ang)),
                    arrowprops=dict(arrowstyle="->", lw=1.2, color='#495057', 
                                    connectionstyle="arc3,rad=-0.15"))

    # Center box with theorem bound
    ax.add_patch(patches.FancyBboxPatch((-0.42, -0.22), 0.84, 0.44, boxstyle="round,pad=0.08",
                                        facecolor='#d3f9d8', edgecolor='#2b8a3e', lw=1.5))
    ax.text(0, 0.06, "Starvation-Free\nArbitration", ha='center', va='center', fontsize=9, fontweight='bold', color='#1b4332')
    ax.text(0, -0.10, "Delay Bound: N-1 = 9", ha='center', va='center', fontsize=8, color='#1b4332')

    save_fig(fig, "fig4_arbiter_fsm")

if __name__ == "__main__":
    print("=" * 70)
    print("  GENERATING ARCHITECTURAL DIAGRAMS (PDF, PNG, SVG)")
    print("=" * 70)
    draw_fig1()
    draw_fig2()
    draw_fig3()
    draw_fig4()
    print("=" * 70)
    print("  All Architectural Figures Generated in PDF, PNG (300 DPI), and SVG!")
    print("=" * 70)
