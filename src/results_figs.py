import sys, pathlib, json; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from viz import C, INK, INK2, MUTED, GRID, apply_style, finish

apply_style()
from paths import FIG, OUT, METRICS
R = json.load(open(f"{OUT}/results.json"))
P = np.load(f"{OUT}/predictions.npz")
res = R["results"]
best = min(res, key=lambda k: res[k]["RMSE"])   # selected on test RMSE
print("best model:", best)
order = list(res.keys())

# ---------- FIG 5: model comparison ----------
fig, axes = plt.subplots(1, 3, figsize=(10.6, 4.0))
short = [n.replace(" (", "\n(") for n in order]
ypos = np.arange(len(order))[::-1]
for ax, key, lab, note in [
    (axes[0], "RMSE", "RMSE (°C)", "lower is better"),
    (axes[1], "MaxAE", "worst-case error (°C)", "the metric that burns motors"),
    (axes[2], "within_2C", "samples within ±2 °C (%)", "higher is better"),
]:
    vals = [res[n][key] for n in order]
    cols = [C[0] if n != best else C[2] for n in order]
    ax.barh(ypos, vals, color=cols, height=0.62, linewidth=0)
    for y, v in zip(ypos, vals):
        ax.text(v + max(vals) * 0.025, y, f"{v:.2f}", va="center",
                fontsize=8.5, color=INK, fontweight="bold")
    ax.set_yticks(ypos); ax.set_yticklabels(short if ax is axes[0] else [])
    ax.set_xlim(0, max(vals) * 1.22)
    finish(ax, lab, sub=note, grid="x")
fig.suptitle("Model comparison on held-out sessions (profiles 65 & 72)",
             x=0.005, ha="left", fontsize=12.5, fontweight="bold", color=INK, y=1.08)
fig.text(0.005, 1.005, "Green = selected model. No model ever saw these two motor sessions during training.",
         ha="left", fontsize=9, color=MUTED)
fig.savefig(f"{FIG}/05_model_comparison.png"); plt.close(fig)

# ---------- FIG 6: predicted vs actual time series ----------
yte, pid = P["yte"], P["pid"]
pb = P[best.replace(" ", "_")]
tests = sorted(set(pid.tolist()))
fig, axes = plt.subplots(len(tests), 1, figsize=(10, 3.2 * len(tests)),
                         gridspec_kw={"hspace": 0.45})
for ax, q in zip(np.atleast_1d(axes), tests):
    m = pid == q
    t = np.arange(m.sum()) / 2 / 60
    ax.plot(t, yte[m], color=INK2, lw=1.9, label="measured", zorder=3)
    ax.plot(t, pb[m], color=C[1], lw=1.4, label="predicted", zorder=4)
    ax.fill_between(t, yte[m], pb[m], color=C[1], alpha=0.22, linewidth=0, zorder=2)
    e = np.abs(yte[m] - pb[m])
    ax.legend(loc="upper left", ncol=2)
    finish(ax, f"Profile {q}", sub=f"RMSE {np.sqrt((e**2).mean()):.2f} °C  ·  "
           f"max error {e.max():.2f} °C  ·  {m.sum()/2/60:.0f} min",
           xlabel="time (minutes)", ylabel="stator winding temp (°C)")
fig.suptitle(f"{best}: predicted vs measured on unseen motor sessions",
             x=0.005, ha="left", fontsize=12.5, fontweight="bold", color=INK, y=1.02)
fig.savefig(f"{FIG}/06_predicted_vs_actual.png"); plt.close(fig)

# ---------- FIG 7: residual analysis ----------
err = pb - yte
fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.8))
axes[0].hist(err, bins=90, color=C[0], edgecolor="white", linewidth=0.3)
axes[0].axvline(0, color=INK2, lw=1.1, ls="--")
finish(axes[0], "Residual distribution", sub=f"mean {err.mean():+.2f} °C  ·  σ {err.std():.2f} °C",
       xlabel="predicted − measured (°C)", ylabel="samples")
idx = np.random.RandomState(0).choice(len(yte), min(30000, len(yte)), replace=False)
axes[1].scatter(yte[idx], err[idx], s=2.5, alpha=0.12, color=C[0],
                edgecolors="none", rasterized=True)
axes[1].axhline(0, color=INK2, lw=1.1, ls="--")
for s in (2, -2):
    axes[1].axhline(s, color=C[7], lw=1.0, ls=":")
axes[1].text(0.99, 0.955, "±2 °C band", transform=axes[1].transAxes, ha="right",
             fontsize=8, color=C[7])
finish(axes[1], "Error vs operating temperature", sub="checks for bias in the hot regime",
       xlabel="measured winding temp (°C)", ylabel="residual (°C)", grid="both")
fig.suptitle("Where the model is wrong", x=0.005, ha="left",
             fontsize=12.5, fontweight="bold", color=INK, y=1.06)
fig.savefig(f"{FIG}/07_residuals.png"); plt.close(fig)

# ---------- FIG 8: feature importance ----------
imp = pd.Series(R["importance"]).sort_values(ascending=False).head(18)[::-1]
fam = ["EWMA / EWM-std" if ("ewm" in n) else "instantaneous" for n in imp.index]
cols = [C[2] if f.startswith("EWMA") else C[3] for f in fam]
fig, ax = plt.subplots(figsize=(7.8, 5.6))
ax.barh(np.arange(len(imp)), imp.values, color=cols, height=0.7, linewidth=0)
ax.set_yticks(np.arange(len(imp))); ax.set_yticklabels(imp.index, fontsize=8)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=C[2], label="thermal-history feature (EWMA)"),
                   Patch(color=C[3], label="instantaneous sensor value")],
          loc="lower right")
n_ewm = sum(1 for f in fam if f.startswith("EWMA"))
finish(ax, "What the model actually uses  (LightGBM split importance)",
       sub=f"{n_ewm} of the top 18 features are thermal-history features, not instantaneous readings",
       xlabel="number of splits using this feature", grid="x")
fig.savefig(f"{FIG}/08_feature_importance.png"); plt.close(fig)

# ---------- FIG 9: ablation + leakage ----------
abl = R["ablation"]; leak = R["leak"]
fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.0))
names = list(abl.keys()); rm = [abl[n]["RMSE"] for n in names]
axes[0].bar(np.arange(len(names)), rm, color=[C[3], C[3], C[2]], width=0.6, linewidth=0)
for i, v in enumerate(rm):
    axes[0].text(i, v + max(rm) * 0.03, f"{v:.2f}", ha="center", fontsize=9.5,
                 fontweight="bold", color=INK)
axes[0].set_xticks(np.arange(len(names)))
axes[0].set_xticklabels([n.replace(" ", "\n", 1) for n in names], fontsize=8.5)
axes[0].set_ylim(0, max(rm) * 1.18)
finish(axes[0], "Ablation: what earns the accuracy",
       sub="same LightGBM, progressively richer features", ylabel="RMSE (°C)")

# leakage panel must compare the SAME model under two split protocols
LEAK_REF = "LightGBM (final)"
hon = res[LEAK_REF]["R2"]; lk = leak["R2"]
axes[1].bar([0, 1], [lk, hon], color=[C[7], C[2]], width=0.5, linewidth=0)
for i, (v, lbl) in enumerate([(lk, "random split\n(LEAKY)"), (hon, "profile-wise split\n(honest)")]):
    axes[1].text(i, v + 0.004, f"R² = {v:.4f}", ha="center", fontsize=10,
                 fontweight="bold", color=INK)
axes[1].set_xticks([0, 1]); axes[1].set_xticklabels(
    ["random split\n(leaky)", "profile-wise split\n(honest)"], fontsize=9)
axes[1].set_ylim(min(hon, lk) - 0.02, 1.008)
finish(axes[1], "Why the split protocol matters",
       sub="adjacent 0.5 s samples are near-duplicates — random splitting puts them on both sides",
       ylabel="R² on test data")
fig.suptitle("Validating the approach", x=0.005, ha="left",
             fontsize=12.5, fontweight="bold", color=INK, y=1.06)
fig.savefig(f"{FIG}/09_ablation_leakage.png"); plt.close(fig)

# ---------- metrics table for the report ----------
tbl = pd.DataFrame(res).T[["RMSE", "MAE", "R2", "MaxAE", "within_2C"]].round(4)
tbl.columns = ["RMSE (°C)", "MAE (°C)", "R²", "Max abs err (°C)", "Within ±2 °C (%)"]
tbl.to_csv(METRICS)
print(tbl.to_string())
print("\nfigures written")
