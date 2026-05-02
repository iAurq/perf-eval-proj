"""
GPU Throttle Overlay Plot
=========================
Reads an nvidia-smi CSV and plots Power Draw and GPU Utilization on the same graph
with color-coded background bands (throttle reason from the CSV).

Throttle legend:
  0x01 = GPU idle
  0x00 = No throttle
  0x04 = Power cap
  0x20 = Thermal limit
  0x24 = Power + Thermal

Usage:
  python plot_throttle.py outputs/heaven_directx11.csv
  python plot_throttle.py outputs/heaven_directx11.csv --title "Heaven" --out plot.png
"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from pathlib import Path

# ── Colors ────────────────────────────────────────────────────────────────────
BAND_COLORS = {
    'idle':          "#81aac5",
    'free':          "#90d190",
    'power_cap':     "#ffe4a0",
    'thermal':       "#e4a982",
    'power+thermal': "#df96ba",
    'other':         "#e0e0e0",
}
BAND_ALPHA = 0.55

# Colors for metrics
POWER_COLOR = "#244270"   # blue — Power Draw
UTIL_COLOR  = "#8a2d2d"   # red  — GPU Utilization

BG   = 'white'
GRID = '#cccccc'
TEXT = '#222222'
TICK = '#555555'


def decode_throttle(hex_str):
    try:
        v = int(str(hex_str).strip(), 16)
    except Exception:
        return 'other'
    if v == 0x01: return 'idle'
    if v == 0x00: return 'free'
    if v == 0x04: return 'power_cap'
    if v == 0x20: return 'thermal'
    if v == 0x24: return 'power+thermal'
    return 'other'


def load_csv(path):
    df = pd.read_csv(path, skipinitialspace=True)
    df.columns = df.columns.str.strip()

    sample = str(df['timestamp'].iloc[0]).strip()
    if ' ' in sample:
        df['_dt'] = pd.to_datetime(df['timestamp'].str.strip(),
                                   format='%Y/%m/%d %H:%M:%S.%f')
        df['t'] = (df['_dt'] - df['_dt'].iloc[0]).dt.total_seconds()
    else:
        def ts_to_s(ts):
            m, s = ts.strip().split(':')
            return int(m) * 60 + float(s)
        df['t'] = df['timestamp'].apply(ts_to_s)
        df['t'] -= df['t'].iloc[0]

    df['power']    = df['power.draw [W]'].str.extract(r'([\d.]+)').astype(float)
    df['temp']     = pd.to_numeric(df['temperature.gpu'], errors='coerce')
    df['util']     = df['utilization.gpu [%]'].str.extract(r'(\d+)').astype(float)
    df['throttle'] = df['clocks_event_reasons.active'].apply(decode_throttle)
    
    # Print averages to console
    print(f"\n=== Statistics for {Path(path).name} ===")
    print(f"Average Power Draw: {df['power'].mean():.1f} W")
    print(f"Peak Power Draw: {df['power'].max():.1f} W")
    print(f"Average GPU Utilization: {df['util'].mean():.1f} %")
    print(f"Peak GPU Utilization: {df['util'].max():.1f} %")
    print(f"Average Temperature: {df['temp'].mean():.1f} °C")
    print(f"Peak Temperature: {df['temp'].max():.1f} °C")
    print("=" * 50 + "\n")
    
    return df


def draw_bands(ax, df):
    prev_t  = df['t'].iloc[0]
    prev_st = df['throttle'].iloc[0]
    for i in range(1, len(df)):
        cur_t  = df['t'].iloc[i]
        cur_st = df['throttle'].iloc[i]
        ax.axvspan(prev_t, cur_t,
                   color=BAND_COLORS.get(prev_st, '#eee'),
                   alpha=BAND_ALPHA, linewidth=0, zorder=0)
        prev_t, prev_st = cur_t, cur_st
    ax.axvspan(prev_t, df['t'].iloc[-1],
               color=BAND_COLORS.get(prev_st, '#eee'),
               alpha=BAND_ALPHA, linewidth=0, zorder=0)


def plot(csv_path, title=None, out_path=None):
    df = load_csv(csv_path)
    name = title or Path(csv_path).stem.replace('_', ' ').title()
    out = out_path or Path(csv_path).with_suffix('.png')

    # Single plot for Power Draw + GPU Utilization (dual y-axis)
    fig, ax_power = plt.subplots(1, 1, figsize=(16, 6), facecolor=BG)
    
    fig.suptitle(f'{name}  —  GPU Power Draw & Utilization with Throttle Reason',
                 color=TEXT, fontsize=14, fontweight='bold', y=0.98)

    ax_power.set_facecolor(BG)
    ax_power.tick_params(colors=TICK, labelsize=9, axis='y')
    for sp in ax_power.spines.values():
        sp.set_color(GRID)
        sp.set_linewidth(0.8)
    ax_power.grid(color=GRID, linewidth=0.6, linestyle='--', alpha=0.9, zorder=1)
    ax_power.set_xlabel('Time elapsed (s)', color=TICK, fontsize=9)
    ax_power.set_ylabel('Power Draw (W)', color=POWER_COLOR, fontsize=10, labelpad=6)

    draw_bands(ax_power, df)

    # Power trace (left y-axis)
    power_smooth = df['power'].rolling(3, center=True, min_periods=1).mean()
    ax_power.plot(df['t'], power_smooth, color=POWER_COLOR, lw=1.8, zorder=3)

    # Utilization trace (right y-axis)
    ax_util = ax_power.twinx()
    ax_util.set_facecolor(BG)
    ax_util.tick_params(colors=UTIL_COLOR, labelsize=9, axis='y')
    ax_util.set_ylabel('GPU Utilization (%)', color=UTIL_COLOR, fontsize=10, labelpad=6)
    
    for sp in ax_util.spines.values():
        sp.set_color(GRID)
        sp.set_linewidth(0.8)
    ax_util.spines['right'].set_color(UTIL_COLOR)
    ax_util.spines['right'].set_linewidth(1.5)

    util_smooth = df['util'].rolling(3, center=True, min_periods=1).mean()
    ax_util.plot(df['t'], util_smooth, color=UTIL_COLOR, lw=1.8, zorder=3)

    # ── Legend ────────────────────────────────────────────────────────────────
    band_entries = [
        mpatches.Patch(facecolor=BAND_COLORS['idle'],          alpha=0.8,
                       edgecolor='#aaa', label='Idle  (0x01)'),
        mpatches.Patch(facecolor=BAND_COLORS['free'],          alpha=0.8,
                       edgecolor='#aaa', label='No throttle  (0x00)'),
        mpatches.Patch(facecolor=BAND_COLORS['power_cap'],     alpha=0.8,
                       edgecolor='#aaa', label='Power cap  (0x04)'),
        mpatches.Patch(facecolor=BAND_COLORS['thermal'],       alpha=0.8,
                       edgecolor='#aaa', label='Thermal limit  (0x20)'),
        mpatches.Patch(facecolor=BAND_COLORS['power+thermal'], alpha=0.8,
                       edgecolor='#aaa', label='Power + Thermal  (0x24)'),
    ]

    # Metric legend entries as LINES (not boxes)
    metric_entries = [
        mlines.Line2D([], [], color=POWER_COLOR, linewidth=2, 
                      label='Power Draw'),
        mlines.Line2D([], [], color=UTIL_COLOR, linewidth=2, 
                      label='GPU Utilization'),
    ]

    all_entries = metric_entries + band_entries

    fig.legend(handles=all_entries,
               loc='lower center', ncol=4,
               frameon=True, framealpha=0.9,
               facecolor='white', edgecolor=GRID,
               fontsize=8.5, labelcolor=TEXT,
               bbox_to_anchor=(0.5, -0.02))

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.savefig(out, dpi=160, bbox_inches='tight', facecolor=BG)
    print(f'Saved → {out}')
    plt.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot GPU throttle overlay')
    parser.add_argument('csv',        help='nvidia-smi CSV file')
    parser.add_argument('--title',    help='Chart title override')
    parser.add_argument('--out',      help='Output PNG path')
    args = parser.parse_args()
    plot(args.csv, title=args.title, out_path=args.out)