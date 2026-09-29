import sys, pathlib, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import matplotlib.pyplot as plt
from viz import C, INK, INK2, MUTED, DIVERGING, apply_style, finish
from features import add_physical_features

apply_style()
from paths import FIG, DATA
df = pd.read_csv(DATA)
df = add_physical_features(df)
FS = 2.0

# ---------- FIG 1: thermal lag on one representative profile ----------
pid = df.groupby("profile_id").size().sort_values().index[-1]   # longest session
d = df[df.profile_id == pid].reset_index(drop=True)
t = np.arange(len(d)) / FS / 60.0   # minutes

fig, axes = plt.subplots(3, 1, figsize=(9, 7.2), sharex=True,
                         gridspec_kw={"hspace": 0.35})
axes[0].plot(t, d.motor_speed, color=C[0], lw=1.0)
finish(axes[0], "Motor speed", ylabel="rpm")
axes[1].plot(t, d.i_s, color=C[1], lw=1.0)
finish(axes[1], "Stator current magnitude  $i_s=\\sqrt{i_d^2+i_q^2}$", ylabel="A")
axes[2].plot(t, d.stator_winding, color=C[7], lw=1.6, label="stator winding")
axes[2].plot(t, d.coolant, color=C[2], lw=1.4, label="coolant")
axes[2].plot(t, d.ambient, color=MUTED, lw=1.2, label="ambient")
axes[2].legend(loc="upper left", ncol=3)
finish(axes[2], "Temperatures", xlabel="time (minutes)", ylabel="°C")
fig.suptitle(f"Thermal response lags the electrical excitation  ·  profile {pid}",
             x=0.005, ha="left", fontsize=12, fontweight="bold", color=INK, y=1.0)
fig.text(0.005, 0.965, "Current swings in seconds; winding temperature answers over minutes. "
         "An instantaneous-value model cannot see this.",
         ha="left", fontsize=9, color=MUTED)
fig.savefig(f"{FIG}/01_thermal_lag.png"); plt.close(fig)

# ---------- FIG 2: why EWMA - instantaneous vs smoothed current ----------
sub = df.sample(40000, random_state=0)
ew = df.groupby("profile_id", sort=False)["i_s"].transform(
    lambda x: x.ewm(span=int(600 * FS), adjust=False).mean())
df["_i_ewma600"] = ew
sub = df.sample(40000, random_state=0)

fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.0))
for ax, col, lab, col_c in [
    (axes[0], "i_s", "instantaneous  $i_s$  (A)", C[1]),
    (axes[1], "_i_ewma600", "600 s EWMA of  $i_s$  (A)", C[0]),
]:
    ax.scatter(sub[col], sub.stator_winding, s=2, alpha=0.10,
               color=col_c, edgecolors="none", rasterized=True)
    r = np.corrcoef(df[col], df.stator_winding)[0, 1]
    finish(ax, None, xlabel=lab, ylabel="stator winding temp (°C)", grid="both")
    ax.text(0.97, 0.05, f"r = {r:.2f}", transform=ax.transAxes, ha="right",
            fontsize=11, fontweight="bold", color=INK)
axes[0].set_title("Raw sensor value", loc="left")
axes[1].set_title("Thermally filtered value", loc="left")
fig.suptitle("One feature transform does most of the work",
             x=0.005, ha="left", fontsize=12, fontweight="bold", color=INK, y=1.06)
fig.text(0.005, 1.0, "Smoothing current over a 10-minute window turns a diffuse cloud into a usable predictor.",
         ha="left", fontsize=9, color=MUTED)
fig.savefig(f"{FIG}/02_ewma_motivation.png"); plt.close(fig)
df.drop(columns=["_i_ewma600"], inplace=True)

# ---------- FIG 3: correlation matrix ----------
cols = ["ambient", "coolant", "motor_speed", "torque", "i_d", "i_q", "u_d", "u_q",
        "i_s", "u_s", "S_el", "P_loss", "stator_winding"]
corr = df[cols].corr()
fig, ax = plt.subplots(figsize=(7.4, 6.4))
im = ax.imshow(corr, cmap=DIVERGING, vmin=-1, vmax=1)
ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, rotation=45, ha="right")
ax.set_yticks(range(len(cols))); ax.set_yticklabels(cols)
for i in range(len(cols)):
    for j in range(len(cols)):
        v = corr.iloc[i, j]
        ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7,
                color="#ffffff" if abs(v) > 0.62 else INK2)
ax.set_xticks(np.arange(-.5, len(cols), 1), minor=True)
ax.set_yticks(np.arange(-.5, len(cols), 1), minor=True)
ax.grid(which="minor", color="#ffffff", linewidth=2); ax.tick_params(which="minor", length=0)
cb = fig.colorbar(im, ax=ax, shrink=0.72, pad=0.02); cb.outline.set_visible(False)
cb.set_label("Pearson r", color=INK2)
ax.set_title("Linear correlation of raw signals with winding temperature",
             loc="left", pad=12)
ax.text(0, 1.015, "No raw electrical signal exceeds |r| = 0.6 against the target.",
        transform=ax.transAxes, fontsize=8.5, color=MUTED)
fig.savefig(f"{FIG}/03_correlation.png"); plt.close(fig)

# ---------- FIG 4: dataset structure ----------
sizes = (df.groupby("profile_id").size() / FS / 60).sort_values()
fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.6))
axes[0].hist(df.stator_winding, bins=70, color=C[0], edgecolor="white", linewidth=0.4)
finish(axes[0], "Target distribution", xlabel="stator winding temp (°C)", ylabel="samples")
axes[1].bar(range(len(sizes)), sizes.values, color=C[2], width=0.85, linewidth=0)
finish(axes[1], "Session length by measurement profile",
       xlabel=f"{len(sizes)} profiles (sorted)", ylabel="minutes")
fig.suptitle("Dataset structure", x=0.005, ha="left", fontsize=12,
             fontweight="bold", color=INK, y=1.05)
fig.text(0.005, 0.985, f"{len(df):,} samples at 2 Hz  ·  {df.profile_id.nunique()} independent "
         f"benchmark sessions  ·  {sizes.sum()/60:.0f} hours total  ·  no missing values",
         ha="left", fontsize=9, color=MUTED)
fig.savefig(f"{FIG}/04_dataset_structure.png"); plt.close(fig)

print("EDA figures written")
print("target range: %.1f - %.1f C" % (df.stator_winding.min(), df.stator_winding.max()))
print("hours:", round(len(df)/FS/3600, 1))
print("top |r| vs target:")
print(corr["stator_winding"].drop("stator_winding").abs().sort_values(ascending=False).round(3).to_string())
