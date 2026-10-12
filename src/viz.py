"""Shared plot styling — one place, so every figure in the repo, the report
and the slide deck reads as the same system.

Exports at 300 dpi: crisp when zoomed in a README, and print-quality in the
report. Type sizes are set for a figure that will be shown at roughly half its
pixel width, which is how they land on a GitHub page and on a projector."""
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
        "font.size": 10.5,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.titlecolor": INK,
        "axes.titlepad": 9,
        "axes.labelsize": 10.5,
        "axes.labelweight": "medium",
        "axes.labelcolor": INK2,
        "axes.edgecolor": GRID,
        "axes.linewidth": 0.9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.axisbelow": True,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "xtick.major.size": 3.5,
        "ytick.major.size": 3.5,
        "xtick.major.width": 0.9,
        "ytick.major.width": 0.9,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "legend.frameon": False,
        "legend.fontsize": 10,
        "legend.handlelength": 1.6,
        "legend.columnspacing": 1.4,
        "lines.linewidth": 1.8,
        "lines.solid_capstyle": "round",
        "patch.linewidth": 0,
        "figure.dpi": 130,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.12,
    })


def finish(ax, title=None, sub=None, xlabel=None, ylabel=None, grid="y"):
    if title:
        ax.set_title(title, loc="left", pad=17 if sub else 9)
    if sub:
        ax.text(0, 1.015, sub, transform=ax.transAxes, fontsize=9.5,
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


def suptitle(fig, title, sub=None, x=0.005, y=1.0):
    """Figure-level headline + one-line explanation, left-aligned together.

    The gap is computed from the figure height in inches, so it stays visually
    constant instead of scaling with the panel count (which collides)."""
    fig.text(x, y, title, ha="left", va="bottom", fontsize=14,
             fontweight="bold", color=INK)
    if sub:
        gap = 0.26 / fig.get_figheight()     # ~0.26 in below the title baseline
        fig.text(x, y - gap, sub, ha="left", va="top", fontsize=10.5, color=MUTED)


def annotate(ax, text, xy, xytext, color=None, size=9.5):
    """A short callout with a thin leader line."""
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=size,
                color=color or INK2, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=color or MUTED,
                                linewidth=0.9, shrinkA=0, shrinkB=3))


def despine_all(ax):
    for sp in ax.spines.values():
        sp.set_visible(False)
