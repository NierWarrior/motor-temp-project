"""
Three figures the first pass was missing:

  10  the split protocol made concrete - which sessions train, validate, test
  11  tuning results - CV vs test, tuned vs untuned
  12  error analysis - where the error actually lives
"""
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from viz import C, INK, INK2, MUTED, GRID, SEQ, apply_style, finish, suptitle, despine_all
from paths import FIG, OUT, DATA
from features import TARGET

apply_style()
FS = 2.0
TEST_P, VAL_P = [65, 72], [60, 62, 74]
R = json.load(open(OUT / "results.json"))
P = np.load(OUT / "predictions.npz")

# ============ FIG 10: the split protocol, made concrete ============
meta = pd.read_csv(DATA, usecols=["profile_id", TARGET, "i_d", "i_q"])
meta["i_s"] = np.sqrt(meta.i_d ** 2 + meta.i_q ** 2)
g = meta.groupby("profile_id").agg(
    n=(TARGET, "size"), tmin=(TARGET, "min"), tmax=(TARGET, "max"),
    imax=("i_s", "max")).reset_index()
g["minutes"] = g.n / FS / 60
g["role"] = np.where(g.profile_id.isin(TEST_P), "test",
            np.where(g.profile_id.isin(VAL_P), "validation", "train"))
g = g.sort_values("tmax").reset_index(drop=True)
ROLE_C = {"train": "#c3cbd4", "validation": C[3], "test": C[7]}

fig, axes = plt.subplots(2, 1, figsize=(12.4, 8.2),
                         gridspec_kw={"height_ratios": [7, 1.25], "hspace": 0.34})
ax = axes[0]
for i, r in g.iterrows():
    ax.plot([r.tmin, r.tmax], [i, i], color=ROLE_C[r.role],
            lw=3.6 if r.role != "train" else 2.6, solid_capstyle="round",
            zorder=3 if r.role != "train" else 2)
# label the held-out sessions at their cold end, nudging apart any that collide
held = g[g.role != "train"].sort_values("tmin")
placed = []
for i, r in held.iterrows():
    y = i
    while any(abs(y - q) < 2.2 for q in placed):
        y += 2.2
    placed.append(y)
    ax.annotate(f"profile {r.profile_id}", xy=(r.tmin, i), xytext=(r.tmin - 3.5, y),
                va="center", ha="right", fontsize=9.5, color=ROLE_C[r.role],
                fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=ROLE_C[r.role],
                                linewidth=0.8, shrinkA=1, shrinkB=1))
ax.set_ylim(-1.5, len(g) + 0.5)
ax.set_xlim(8, 150)
ax.set_yticks([])
ax.legend(handles=[Patch(color=ROLE_C["train"], label=f"train — {(g.role=='train').sum()} sessions"),
                   Patch(color=ROLE_C["validation"], label=f"validation — {len(VAL_P)} sessions"),
                   Patch(color=ROLE_C["test"], label=f"test — {len(TEST_P)} sessions, held out")],
          loc="lower right", ncol=1)
finish(ax, "Every session is assigned whole",
       sub="each bar is one recording session, spanning the winding temperatures it reached",
       xlabel="stator winding temperature covered (°C)", grid="x")
despine_all(ax)

# proportion bar — honest about how lopsided the partition is
ax = axes[1]
summ = g.groupby("role").agg(sessions=("profile_id", "size"),
                             samples=("n", "sum"),
                             hours=("minutes", lambda x: x.sum() / 60)).reindex(
    ["train", "validation", "test"])
total = summ.samples.sum()
left = 0.0
for role, row in summ.iterrows():
    frac = row.samples / total * 100
    ax.barh(0, frac, left=left, height=0.5, color=ROLE_C[role])
    mid = left + frac / 2
    if frac > 20:   # only the train block has room for an inline label
        ax.text(mid, 0, f"{row.samples:,.0f}  ({frac:.1f}%)", ha="center",
                va="center", fontsize=11.5, fontweight="bold", color=INK)
    left += frac
# the two small partitions get a legend row instead of squeezed inline text
parts = [f"{role}  {row.samples:,.0f} ({row.samples/total*100:.1f}%) · "
         f"{int(row.sessions)} sessions · {row.hours:.0f} h"
         for role, row in summ.iterrows()]
for k, (role, txt) in enumerate(zip(summ.index, parts)):
    ax.text(k * 34.0, -0.78, "■", ha="left", va="center", fontsize=11,
            color=ROLE_C[role])
    ax.text(k * 34.0 + 2.2, -0.78, txt, ha="left", va="center", fontsize=9.5,
            color=INK2)
ax.set_xlim(0, 100); ax.set_ylim(-1.25, 0.75)
ax.set_yticks([]); ax.set_xticks([])
finish(ax, None, grid=None)
despine_all(ax)
ax.text(0, 1.02, "Samples by partition", transform=ax.transAxes, fontsize=12,
        fontweight="bold", color=INK, va="bottom")

suptitle(fig, "Profile-wise splitting", y=1.012,
         sub="No sample from a test session appears in training in any form — the model is scored on motors it has never run.")
fig.savefig(FIG / "10_split_protocol.png"); plt.close(fig)
print("10_split_protocol.png")

# ============ FIG 11: tuning results ============
T = json.load(open(OUT / "tuning.json"))
base = R["results"]["MLP (2 x 128)"]
# one colour per model, held constant across all three panels, so colour
# never silently changes meaning from panel to panel
rows = [("MLP\nuntuned", None, base, "#9aa5b1"),
        ("MLP\ntuned", T["models"]["MLP"]["cv_rmse"], T["models"]["MLP"]["test"], C[2]),
        ("HistGradientBoosting\ntuned", T["models"]["HistGradientBoosting"]["cv_rmse"],
         T["models"]["HistGradientBoosting"]["test"], C[1])]

fig, axes = plt.subplots(1, 3, figsize=(13.4, 4.8), gridspec_kw={"wspace": 0.3})
x = np.arange(len(rows))
labels = [r[0] for r in rows]

ax = axes[0]
cv = [r[1] if r[1] else np.nan for r in rows]
te = [r[2]["RMSE"] for r in rows]
bt = int(np.argmin(te))
ax.bar(x - 0.19, cv, width=0.36, color="#dfe3e8", label="grouped CV")
ax.bar(x + 0.19, te, width=0.36, color=[r[3] for r in rows], label="held-out test")
for i, (a, b) in enumerate(zip(cv, te)):
    if not np.isnan(a):
        ax.text(i - 0.19, a + 0.09, f"{a:.2f}", ha="center", fontsize=9.5, color=MUTED)
    ax.text(i + 0.19, b + 0.09, f"{b:.2f}", ha="center", fontsize=10.5,
            fontweight="bold", color=INK)
ax.text(bt + 0.19, te[bt] / 2, "best", ha="center", va="center", fontsize=9.5,
        fontweight="bold", color="#ffffff")
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9.5)
ax.set_ylim(0, 5.3)
from matplotlib.patches import Patch as _P
ax.legend(handles=[_P(color="#dfe3e8", label="grouped CV")], loc="upper left")
finish(ax, "RMSE (°C)", sub="coloured bars = held-out test")

ax = axes[1]
mx = [r[2]["MaxAE"] for r in rows]
ax.bar(x, mx, width=0.52, color=[r[3] for r in rows])
best = int(np.argmin(mx))
for i, v in enumerate(mx):
    ax.text(i, v + 0.22, f"{v:.2f}", ha="center", fontsize=10.5,
            fontweight="bold", color=INK)
ax.text(best, mx[best] / 2, "best", ha="center", va="center", fontsize=9.5,
        fontweight="bold", color="#ffffff")
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9.5)
ax.set_ylim(0, 13.6)
finish(ax, "Worst-case error (°C)",
       sub="tuning for RMSE made the tail slightly worse")

ax = axes[2]
w2 = [r[2]["within_2C"] for r in rows]
ax.bar(x, w2, width=0.52, color=[r[3] for r in rows])
bw = int(np.argmax(w2))
ax.text(bw, w2[bw] / 2, "best", ha="center", va="center", fontsize=9.5,
        fontweight="bold", color="#ffffff")
for i, v in enumerate(w2):
    ax.text(i, v + 1.3, f"{v:.1f}%", ha="center", fontsize=10.5,
            fontweight="bold", color=INK)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9.5)
ax.set_ylim(0, 99)
finish(ax, "Within ±2 °C (%)", sub="share of running time directly usable")

suptitle(fig, "What tuning bought", y=1.15,
         sub="RandomizedSearchCV under GroupKFold on profile_id — RMSE and MAE improved; worst-case error did not.")
fig.savefig(FIG / "11_tuning_results.png"); plt.close(fig)
print("11_tuning_results.png")

# ============ FIG 12: where the error lives ============
yte, pid = P["yte"], P["pid"]
pb = P["MLP_(2_x_128)"]
err = np.abs(yte - pb)
test_i = meta[meta.profile_id.isin(TEST_P)].reset_index(drop=True)
i_s = test_i["i_s"].to_numpy()[:len(err)]

fig, axes = plt.subplots(1, 3, figsize=(13.4, 5.0), gridspec_kw={"wspace": 0.3})

ax = axes[0]
bands = [(18, 40), (40, 60), (60, 80), (80, 100), (100, 145)]
data = [err[(yte >= a) & (yte < b)] for a, b in bands]
bp = ax.boxplot(data, widths=0.56, patch_artist=True, showfliers=False,
                medianprops=dict(color=INK, linewidth=1.8),
                whiskerprops=dict(color=MUTED, linewidth=1.1),
                capprops=dict(color=MUTED, linewidth=1.1))
for patch, col in zip(bp["boxes"], SEQ(np.linspace(0.25, 0.9, len(bands)))):
    patch.set_facecolor(col); patch.set_edgecolor("none")
ax.axhline(2, color=C[7], ls=":", lw=1.3)
ax.text(0.98, 0.93, "±2 °C", transform=ax.transAxes, ha="right",
        fontsize=9.5, color=C[7])
ax.set_xticklabels([f"{a}–{b}" for a, b in bands], fontsize=9.5)
finish(ax, "By operating temperature", sub="the hot regime is the one that matters",
       xlabel="measured winding temp (°C)", ylabel="absolute error (°C)")

ax = axes[1]
# fixed physical bands, not quantiles: 40 % of test samples sit near idle,
# so quintile edges collapse onto each other and say nothing
lbands = [(0, 5), (5, 75), (75, 150), (150, 250), (250, 400)]
lnames = ["idle\n<5", "light\n5–75", "moderate\n75–150", "heavy\n150–250", "peak\n>250"]
data = [err[(i_s >= a) & (i_s < b)] for a, b in lbands]
bp = ax.boxplot(data, widths=0.56, patch_artist=True, showfliers=False,
                medianprops=dict(color=INK, linewidth=1.8),
                whiskerprops=dict(color=MUTED, linewidth=1.1),
                capprops=dict(color=MUTED, linewidth=1.1))
for patch, col in zip(bp["boxes"], SEQ(np.linspace(0.25, 0.9, 5))):
    patch.set_facecolor(col); patch.set_edgecolor("none")
ax.axhline(2, color=C[7], ls=":", lw=1.3)
ax.set_xticklabels(lnames, fontsize=9.5)
finish(ax, "By load", sub="stator current magnitude, $i_s$ (A)",
       xlabel=None, ylabel="absolute error (°C)")

ax = axes[2]
for q, col in zip(TEST_P, [C[0], C[2]]):
    m = pid == q
    t = np.arange(m.sum()) / FS / 60
    e = err[m]
    k = 240  # 2-minute rolling mean
    ax.plot(t[k - 1:], np.convolve(e, np.ones(k) / k, mode="valid"),
            color=col, lw=1.8, label=f"profile {q}")
ax.axvline(60, color=MUTED, ls="--", lw=1.0)
ax.legend(loc="upper right", ncol=2)
ax.text(63, ax.get_ylim()[1] * 0.70, "longest EWMA span\n(3600 s) converged",
        fontsize=9, color=MUTED, va="top")
finish(ax, "By time into the session", sub="2-minute rolling mean — the warm-up penalty",
       xlabel="minutes since session start", ylabel="absolute error (°C)")

suptitle(fig, "Where the error actually lives", y=1.13,
         sub="Median error stays near 1 °C in every regime. The tail widens under load, and the worst errors sit in the first minutes, while the long filters are still converging.")
fig.savefig(FIG / "12_error_analysis.png"); plt.close(fig)
print("12_error_analysis.png")
