import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from viz import C, INK, INK2, MUTED, apply_style
from paths import FIG

apply_style()
fig, ax = plt.subplots(figsize=(8.4, 9.6))
ax.axis("off")

STAGES = [
    ("DATA ACQUISITION", C[0], [
        "PMSM test-bench telemetry  (measures_v2.csv)",
        "1,330,816 samples · 2 Hz · 69 sessions · 185 h",
        "13 raw channels · zero missing values",
    ]),
    ("PRE-PROCESSING", C[2], [
        "Type downcast to float32 (570 MB in memory)",
        "Drop target-leaking channels: pm, stator_tooth, stator_yoke",
        "Retain only drive-measurable inputs (8 channels)",
        "Session integrity check · per-profile continuity",
    ]),
    ("FEATURE ENGINEERING", C[3], [
        "Physical:  $i_s,\\ u_s,\\ S_{el}=1.5\\,i_s u_s,\\ i_s^2,\\ P_{mech},\\ P_{loss}$",
        "Thermal:  EWMA + EWM-std at 30 / 120 / 600 / 1800 / 3600 s",
        "Computed PER PROFILE — no history crosses sessions",
        "8 raw  →  104 engineered features",
    ]),
    ("PROFILE-WISE SPLIT", C[7], [
        "Train  64 profiles · 1,211,517 samples",
        "Val     3 profiles ·    63,904 samples",
        "Test    profiles 65 & 72 · 55,395 samples",
        "Entire sessions held out — random splits leak",
    ]),
    ("MODEL DEVELOPMENT", C[6], [
        "Linear Regression  (raw-input baseline)",
        "Ridge Regression   (+ engineered features)",
        "Random Forest      (80 trees, depth 16)",
        "MLP                (2 x 128, early stopping)",
        "LightGBM           (743 trees, early-stopped)",
    ]),
    ("HYPERPARAMETER TUNING", C[2], [
        "RandomizedSearchCV under GroupKFold on profile_id",
        "A candidate is never scored on a session it was fitted on",
        "MLP (8 candidates) vs HistGradientBoosting (10)",
        "Winner refitted on the full training partition and exported",
    ]),
    ("EVALUATION", C[4], [
        "RMSE · MAE · R²  —  average accuracy",
        "Max absolute error  —  the safety-critical metric",
        "% samples within ±2 °C  —  deployability",
        "Predicted-vs-actual traces on unseen sessions",
        "Ablation + leakage study · feature importance",
        "Result: RMSE 1.54 °C · R² 0.9965 · 84.2 % within ±2 °C",
    ]),
]

VIZ = [
    "signal traces, session lengths",
    "target distribution, missing-value audit",
    "correlation matrix, EWMA scatter (r: 0.57 → 0.70)",
    "split diagram, per-profile temperature ranges",
    "model comparison across three metrics",
    "CV vs test, tuned vs untuned",
    "time-series overlay, residuals, error analysis",
]

# --- layout: size the canvas to the content, not the other way round ---
heights = [0.62 + 0.46 * len(l) for _, _, l in STAGES]
GAP, HEADER = 0.62, 1.35
TOTAL = sum(heights) + GAP * (len(STAGES) - 1) + HEADER + 0.3
ax.set_xlim(0, 10); ax.set_ylim(0, TOTAL)
y = TOTAL - HEADER
BOX_W, X0 = 6.6, 0.35
for i, ((title, col, lines), viz) in enumerate(zip(STAGES, VIZ)):
    h = 0.62 + 0.46 * len(lines)
    ax.add_patch(FancyBboxPatch((X0, y - h), BOX_W, h,
                 boxstyle="round,pad=0.06,rounding_size=0.14",
                 facecolor="#ffffff", edgecolor=col, linewidth=1.8))
    ax.add_patch(FancyBboxPatch((X0, y - h), 0.11, h,
                 boxstyle="square,pad=0", facecolor=col, edgecolor="none"))
    ax.text(X0 + 0.34, y - 0.42, f"{i+1}.  {title}", fontsize=10.5,
            fontweight="bold", color=col, va="center")
    for j, ln in enumerate(lines):
        ax.text(X0 + 0.46, y - 0.92 - 0.46 * j, ln, fontsize=8.6,
                color=INK2, va="center")
    # visualisation side-note
    ax.text(X0 + BOX_W + 0.28, y - h / 2, "visualise:\n" + viz,
            fontsize=7.4, color=MUTED, va="center", ha="left", style="italic")
    if i < len(STAGES) - 1:
        ax.add_patch(FancyArrowPatch((X0 + BOX_W / 2, y - h),
                                     (X0 + BOX_W / 2, y - h - 0.52),
                                     arrowstyle="-|>", mutation_scale=13,
                                     color=MUTED, linewidth=1.3))
    y -= h + 0.62

ax.text(X0, TOTAL - 0.12, "Stator Winding Temperature Estimation — Processing Pipeline",
        fontsize=12.6, fontweight="bold", color=INK, va="top")
ax.text(X0, TOTAL - 0.68, "UCS321 MST Mini Project  ·  Problem Statement 6  ·  GE Power Systems",
        fontsize=9, color=MUTED, va="top")
fig.savefig(str(FIG / "00_flow_diagram.png"))
print("flow diagram written")
