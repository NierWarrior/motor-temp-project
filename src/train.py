import sys, pathlib, time, json, warnings
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import lightgbm as lgb
from features import TARGET, BASE_INPUTS

RNG = 42
from paths import OUT, DATA

# --- Profile-wise split. Profiles 65 & 72 are the standard held-out benchmark
#     sessions used in the literature for this test bench. ---
TEST_P  = [65, 72]
VAL_P   = [60, 62, 74]

df = pd.read_parquet(f"{OUT}/features.parquet")
FEATS = [c for c in df.columns if c not in (TARGET, "profile_id")]
print(f"{len(df):,} samples  ·  {len(FEATS)} features")

te = df.profile_id.isin(TEST_P)
va = df.profile_id.isin(VAL_P)
tr = ~(te | va)
Xtr, ytr = df.loc[tr, FEATS], df.loc[tr, TARGET]
Xva, yva = df.loc[va, FEATS], df.loc[va, TARGET]
Xte, yte = df.loc[te, FEATS], df.loc[te, TARGET]
print(f"train {tr.sum():,} ({df.loc[tr,'profile_id'].nunique()} profiles) | "
      f"val {va.sum():,} | test {te.sum():,}")

# Subsample for the slow learners. 2 Hz data is massively autocorrelated,
# so every 10th sample (0.2 Hz) loses essentially no information.
sub = slice(None, None, 10)
Xtr_s, ytr_s = Xtr.iloc[sub], ytr.iloc[sub]
print(f"subsampled train for RF/MLP: {len(Xtr_s):,}")


def scores(y, p):
    e = np.abs(y - p)
    return dict(
        RMSE=float(np.sqrt(mean_squared_error(y, p))),
        MAE=float(mean_absolute_error(y, p)),
        R2=float(r2_score(y, p)),
        MaxAE=float(e.max()),
        within_2C=float((e <= 2).mean() * 100),
    )


results, preds, timing = {}, {}, {}


def run(name, model, cols=FEATS, Xt=Xtr, yt=ytr):
    t0 = time.time()
    model.fit(Xt[cols], yt)
    timing[name] = time.time() - t0
    p = model.predict(Xte[cols])
    results[name] = scores(yte.values, p)
    preds[name] = p
    r = results[name]
    print(f"{name:<28} RMSE {r['RMSE']:6.3f}  MAE {r['MAE']:6.3f}  "
          f"R2 {r['R2']:7.4f}  MaxAE {r['MaxAE']:7.3f}  "
          f"±2°C {r['within_2C']:5.1f}%   [{timing[name]:.0f}s]")
    return model


print("\n--- model ladder (evaluated on held-out profiles 65 & 72) ---")
run("Linear (raw inputs only)", make_pipeline(StandardScaler(), LinearRegression()), cols=BASE_INPUTS)
run("Linear (+ EWMA features)", make_pipeline(StandardScaler(), Ridge(alpha=1.0)))
rf = run("Random Forest (80 trees)", RandomForestRegressor(
    n_estimators=80, max_depth=16, min_samples_leaf=20, max_features=0.35,
    n_jobs=-1, random_state=RNG, verbose=0), Xt=Xtr_s, yt=ytr_s)
run("MLP (2 x 128)", make_pipeline(StandardScaler(), MLPRegressor(
    hidden_layer_sizes=(128, 128), max_iter=60, early_stopping=True,
    n_iter_no_change=6, random_state=RNG)), Xt=Xtr_s, yt=ytr_s)
gbm = lgb.LGBMRegressor(
    n_estimators=900, learning_rate=0.06, num_leaves=96, min_child_samples=60,
    subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
    random_state=RNG, n_jobs=-1, verbose=-1)
t0 = time.time()
gbm.fit(Xtr, ytr, eval_set=[(Xva, yva)],
        callbacks=[lgb.early_stopping(60, verbose=False)])
timing["LightGBM (final)"] = time.time() - t0
p = gbm.predict(Xte)
results["LightGBM (final)"] = scores(yte.values, p); preds["LightGBM (final)"] = p
r = results["LightGBM (final)"]
print(f"{'LightGBM (final)':<28} RMSE {r['RMSE']:6.3f}  MAE {r['MAE']:6.3f}  "
      f"R2 {r['R2']:7.4f}  MaxAE {r['MaxAE']:7.3f}  ±2°C {r['within_2C']:5.1f}%   "
      f"[{timing['LightGBM (final)']:.0f}s, {gbm.best_iteration_} trees]")

# --- The leakage demonstration: same model, random split instead ---
print("\n--- leakage check: identical model, RANDOM split ---")
rs = np.random.RandomState(RNG)
mask = rs.rand(len(df)) < 0.80
gbm_leak = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05, num_leaves=96,
                             min_child_samples=60, random_state=RNG, n_jobs=-1, verbose=-1)
gbm_leak.fit(df.loc[mask, FEATS], df.loc[mask, TARGET])
p_leak = gbm_leak.predict(df.loc[~mask, FEATS])
leak = scores(df.loc[~mask, TARGET].values, p_leak)
print(f"{'LightGBM, RANDOM split':<28} RMSE {leak['RMSE']:6.3f}  MAE {leak['MAE']:6.3f}  "
      f"R2 {leak['R2']:7.4f}  MaxAE {leak['MaxAE']:7.3f}")
print(f"   -> R2 inflated from {results['LightGBM (final)']['R2']:.4f} to {leak['R2']:.4f}")

# --- Ablation: how much do the EWMA features actually buy? ---
print("\n--- ablation: EWMA feature contribution (LightGBM) ---")
abl = {}
for label, cols in [("raw inputs only", BASE_INPUTS),
                    ("+ physical derivations", BASE_INPUTS + ["i_s","u_s","S_el","i_s_sq","P_mech","P_loss"]),
                    ("+ EWMA (full)", FEATS)]:
    m = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05, num_leaves=96,
                          min_child_samples=60, random_state=RNG, n_jobs=-1, verbose=-1)
    m.fit(Xtr[cols], ytr)
    s = scores(yte.values, m.predict(Xte[cols]))
    abl[label] = s
    print(f"  {label:<26} RMSE {s['RMSE']:6.3f}   R2 {s['R2']:7.4f}")

imp = pd.Series(gbm.feature_importances_, index=FEATS).sort_values(ascending=False)
print("\ntop 15 features:")
print(imp.head(15).to_string())

np.savez_compressed(f"{OUT}/predictions.npz",
                    yte=yte.values, pid=df.loc[te, "profile_id"].values,
                    **{k.replace(" ", "_"): v for k, v in preds.items()})
json.dump({"results": results, "leak": leak, "ablation": abl, "timing": timing,
           "best_iter": int(gbm.best_iteration_),
           "importance": imp.to_dict(),
           "split": {"test": TEST_P, "val": VAL_P,
                     "n_train": int(tr.sum()), "n_val": int(va.sum()), "n_test": int(te.sum()),
                     "n_train_profiles": int(df.loc[tr,'profile_id'].nunique())}},
          open(f"{OUT}/results.json", "w"), indent=2)
import joblib; joblib.dump(gbm, f"{OUT}/model_lgbm.joblib")
print("\nsaved -> outputs/results.json, predictions.npz, model_lgbm.joblib")
