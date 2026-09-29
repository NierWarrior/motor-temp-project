#!/usr/bin/env python3
"""
predict.py — estimate stator winding temperature with the trained model.

    python predict.py --csv path/to/telemetry.csv            # writes predictions.csv
    python predict.py --csv telemetry.csv --out my_preds.csv
    python predict.py --demo                                 # run on held-out profile 72

The input CSV needs the eight drive-measurable channels plus a session column:

    ambient, coolant, u_d, u_q, motor_speed, i_d, i_q, torque, profile_id

`profile_id` groups rows into continuous recording sessions. It matters because
the features are exponentially weighted moving averages of the signal history —
they must not run across a session boundary, and a session must be fed in
chronological order. If all your rows are one continuous run, set it to a
constant.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from features import build, BASE_INPUTS, TARGET  # noqa: E402
from paths import MODELS, DATA  # noqa: E402

MODEL_PATH = MODELS / "final_temperature_model.joblib"


def load_model():
    if not MODEL_PATH.exists():
        sys.exit(f"No trained model at {MODEL_PATH}.\n"
                 f"Run `python run.py` first — the tune stage writes it.")
    return joblib.load(MODEL_PATH)


def predict(df: pd.DataFrame, bundle: dict) -> np.ndarray:
    missing = [c for c in BASE_INPUTS + ["profile_id"] if c not in df.columns]
    if missing:
        sys.exit(f"Input is missing required column(s): {', '.join(missing)}\n"
                 f"Needed: {', '.join(BASE_INPUTS)}, profile_id")

    for c in BASE_INPUTS:
        df[c] = df[c].astype("float32")
    feats = build(df)                      # same 8 -> 104 transform used in training
    X = feats[bundle["features"]]          # and the same column order
    return bundle["model"].predict(X)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--csv", type=Path, help="telemetry CSV to predict on")
    src.add_argument("--demo", action="store_true",
                     help="demo on held-out profile 72 from the training dataset")
    ap.add_argument("--out", type=Path, default=ROOT / "predictions.csv",
                    help="where to write predictions (default: predictions.csv)")
    args = ap.parse_args()

    bundle = load_model()
    print(f"model: {bundle['model_name']}  "
          f"(test RMSE {bundle['test_metrics']['RMSE']:.2f} °C, "
          f"R² {bundle['test_metrics']['R2']:.4f})")

    if args.demo:
        if not DATA.exists():
            sys.exit(f"Demo needs the dataset at {DATA}.")
        df = pd.read_csv(DATA)
        df = df[df.profile_id == 72].reset_index(drop=True)
        truth = df[TARGET].to_numpy()
        print(f"demo: profile 72 — {len(df):,} samples, "
              f"{len(df)/2/60:.0f} min of running\n")
    else:
        df = pd.read_csv(args.csv)
        truth = df[TARGET].to_numpy() if TARGET in df.columns else None
        print(f"input: {args.csv} — {len(df):,} rows, "
              f"{df.profile_id.nunique()} session(s)\n")

    pred = predict(df, bundle)

    out = pd.DataFrame({"profile_id": df["profile_id"],
                        "predicted_winding_temp_C": np.round(pred, 3)})
    if truth is not None:
        err = np.abs(truth - pred)
        out["measured_winding_temp_C"] = truth
        out["abs_error_C"] = np.round(err, 3)
        print(f"  RMSE        {np.sqrt((err**2).mean()):.3f} °C")
        print(f"  MAE         {err.mean():.3f} °C")
        print(f"  max error   {err.max():.3f} °C")
        print(f"  within ±2°C {(err <= 2).mean()*100:.1f} %\n")
    else:
        print(f"  predicted range: {pred.min():.1f} – {pred.max():.1f} °C\n")

    out.to_csv(args.out, index=False)
    print(f"wrote {len(out):,} predictions -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
