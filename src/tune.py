"""
Hyperparameter search for the two strongest models from the ladder, then
export the winner as a deployable pipeline.

The search is grouped by profile_id (GroupKFold), so a candidate is never
scored on a session it was fitted on — the same leakage discipline as the
train/test split itself. A plain KFold here would silently undo it.
"""
import sys, pathlib, json, time, warnings
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
warnings.filterwarnings("ignore")

import numpy as np, pandas as pd, joblib
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.base import clone
from sklearn.model_selection import GroupKFold, RandomizedSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from features import TARGET
from paths import OUT, MODELS

RNG = 42
TEST_P, VAL_P = [65, 72], [60, 62, 74]

df = pd.read_parquet(OUT / "features.parquet")
FEATS = [c for c in df.columns if c not in (TARGET, "profile_id")]

te = df.profile_id.isin(TEST_P)
tr = ~(te | df.profile_id.isin(VAL_P))

# The search is cross-validated, so it uses train+val; the test profiles stay
# untouched until the final evaluation at the bottom of this file.
search_mask = ~te
# 2 Hz data is heavily autocorrelated - every 10th sample keeps the structure
# and makes a real search affordable.
sub = df.loc[search_mask].iloc[::10]
Xs, ys, gs = sub[FEATS], sub[TARGET], sub["profile_id"]
Xtr, ytr = df.loc[tr, FEATS], df.loc[tr, TARGET]
Xte, yte = df.loc[te, FEATS], df.loc[te, TARGET]

print(f"search set: {len(sub):,} samples across {gs.nunique()} profiles")
print(f"test set:   {len(Xte):,} samples (profiles {TEST_P}) - held out\n")

cv = GroupKFold(n_splits=3)


def scores(y, p):
    e = np.abs(y - p)
    return dict(RMSE=float(np.sqrt(mean_squared_error(y, p))),
                MAE=float(mean_absolute_error(y, p)),
                R2=float(r2_score(y, p)),
                MaxAE=float(e.max()),
                within_2C=float((e <= 2).mean() * 100))


SPACES = {
    "MLP": (
        Pipeline([("scale", StandardScaler()),
                  ("model", MLPRegressor(early_stopping=True, n_iter_no_change=6,
                                         max_iter=80, random_state=RNG))]),
        {"model__hidden_layer_sizes": [(64, 64), (128, 128), (256, 128), (128, 128, 64)],
         "model__alpha": [1e-5, 1e-4, 1e-3, 1e-2],
         "model__learning_rate_init": [5e-4, 1e-3, 3e-3]},
        8,
    ),
    "HistGradientBoosting": (
        HistGradientBoostingRegressor(early_stopping=True, n_iter_no_change=20,
                                      random_state=RNG),
        {"max_iter": [300, 500, 800],
         "learning_rate": [0.03, 0.06, 0.1],
         "max_leaf_nodes": [31, 63, 127],
         "min_samples_leaf": [20, 50, 100],
         "l2_regularization": [0.0, 0.1, 1.0]},
        10,
    ),
}

tuned, report = {}, {}
for name, (est, space, n_iter) in SPACES.items():
    print(f"--- tuning {name} ({n_iter} candidates x 3 grouped folds) ---")
    t0 = time.time()
    rs = RandomizedSearchCV(est, space, n_iter=n_iter, cv=cv,
                            scoring="neg_root_mean_squared_error",
                            random_state=RNG, n_jobs=1, refit=True, verbose=0)
    rs.fit(Xs, ys, groups=gs)
    dt = time.time() - t0
    best = {k: (list(v) if isinstance(v, tuple) else v) for k, v in rs.best_params_.items()}
    print(f"    best CV RMSE {-rs.best_score_:.3f} °C   [{dt/60:.1f} min]")
    print(f"    params: {best}")

    # refit the winning configuration on the FULL training partition
    t0 = time.time()
    final = clone(rs.best_estimator_)   # clone handles Pipelines; re-constructing does not
    final.fit(Xtr, ytr)
    s = scores(yte.values, final.predict(Xte))
    print(f"    test: RMSE {s['RMSE']:.3f}  MAE {s['MAE']:.3f}  R2 {s['R2']:.4f}  "
          f"MaxAE {s['MaxAE']:.2f}  ±2°C {s['within_2C']:.1f}%   "
          f"[refit {(time.time()-t0)/60:.1f} min]\n")
    tuned[name] = final
    report[name] = {"cv_rmse": float(-rs.best_score_), "params": best, "test": s,
                    "search_minutes": round(dt / 60, 1)}

winner = min(report, key=lambda k: report[k]["test"]["RMSE"])
print(f"selected: {winner}  (test RMSE {report[winner]['test']['RMSE']:.3f} °C)")

joblib.dump({"model": tuned[winner],
             "features": FEATS,
             "target": TARGET,
             "model_name": winner,
             "params": report[winner]["params"],
             "test_metrics": report[winner]["test"],
             "test_profiles": TEST_P,
             "sklearn_version": __import__("sklearn").__version__},
            MODELS / "final_temperature_model.joblib", compress=3)

json.dump({"winner": winner, "models": report},
          open(OUT / "tuning.json", "w"), indent=2)
size = (MODELS / "final_temperature_model.joblib").stat().st_size / 1e6
print(f"saved -> models/final_temperature_model.joblib ({size:.1f} MB)")
print("saved -> outputs/tuning.json")
