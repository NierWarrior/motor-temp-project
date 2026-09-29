"""Shared plot styling. One place so every figure in the report matches."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Validated categorical palette, assigned in fixed order (never cycled).
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8a8985"
GRID = "#e2e1dd"
SURF = "#ffffff"

# Diverging pair for correlation (two hues, neutral gray midpoint)
DIVERGING = matplotlib.colors.LinearSegmentedColormap.from_list(
    "div", ["#2a78d6", "#f2f2f0", "#eb6834"]
)
# Sequential, single hue light->dark
SEQ = matplotlib.colors.LinearSegmentedColormap.from_list(
    "seq", ["#eaf2fc", "#2a78d6", "#123d70"]
)


def apply_style():
    plt.rcParams.update({
        "figure.facecolor": SURF,
        "axes.facecolor": SURF,
        "savefig.facecolor": SURF,
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 10.5,
        "axes.titleweight": "bold",
        "axes.titlecolor": INK,
        "axes.labelsize": 9,
        "axes.labelcolor": INK2,
        "axes.edgecolor": GRID,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "grid.color": GRID,
        "grid.linewidth": 0.7,
        "legend.frameon": False,
        "legend.fontsize": 8.5,
        "lines.linewidth": 1.6,
        "figure.dpi": 130,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    })


def finish(ax, title=None, sub=None, xlabel=None, ylabel=None, grid="y"):
    if title:
        ax.set_title(title, loc="left", pad=14 if sub else 8)
    if sub:
        ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=8.5,
                color=MUTED, va="bottom", ha="left")
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if grid in ("y", "both"):
        ax.yaxis.grid(True); ax.set_axisbelow(True)
    if grid in ("x", "both"):
        ax.xaxis.grid(True); ax.set_axisbelow(True)
    return ax
