#!/usr/bin/env python3
"""
run.py — one entry point for the whole pipeline.

    python run.py                 # everything: EDA -> features -> train -> figures
    python run.py --stage train   # just one stage
    python run.py --list          # what the stages are
    python run.py --quick         # fast smoke run on a slice of the data

Stages run in order and each one reuses the previous stage's output, so a
re-run only redoes what is missing (pass --force to rebuild regardless).
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

# stage key -> (script, human label, output it produces)
STAGES: dict[str, tuple[str, str, str | None]] = {
    "eda":      ("eda.py",          "Exploratory figures",        "figures/01_thermal_lag.png"),
    "flow":     ("flow_diagram.py", "Pipeline flow diagram",      "figures/00_flow_diagram.png"),
    "features": ("build_features.py", "Feature matrix (8 -> 104)", "outputs/features.parquet"),
    "train":    ("train.py",        "Model ladder + studies",     "outputs/results.json"),
    "tune":     ("tune.py",         "Hyperparameter search + export", "models/final_temperature_model.joblib"),
    "figures":  ("results_figs.py", "Result figures + metrics",   "figures/05_model_comparison.png"),
}
ORDER = ["eda", "flow", "features", "train", "tune", "figures"]

BOLD, DIM, GREEN, RED, YELLOW, CYAN, OFF = (
    "\033[1m", "\033[2m", "\033[32m", "\033[31m", "\033[33m", "\033[36m", "\033[0m"
)
if not sys.stdout.isatty():
    BOLD = DIM = GREEN = RED = YELLOW = CYAN = OFF = ""


def hr(char: str = "─") -> str:
    return char * min(shutil.get_terminal_size((78, 20)).columns, 78)


def human(sec: float) -> str:
    return f"{sec:.0f}s" if sec < 90 else f"{sec/60:.1f}m"


def check_environment() -> bool:
    """Verify the dataset and the third-party packages are present."""
    ok = True
    print(f"{BOLD}Environment{OFF}")

    data = ROOT / "data" / "raw" / "measures_v2.csv"
    if not data.exists() and (ROOT / "measures_v2.csv").exists():
        data = ROOT / "measures_v2.csv"
    if data.exists():
        mb = data.stat().st_size / 1e6
        print(f"  {GREEN}OK{OFF}  dataset           {data.relative_to(ROOT)} ({mb:,.0f} MB)")
    else:
        print(f"  {RED}--{OFF}  dataset           measures_v2.csv NOT FOUND")
        print(f"      {DIM}Download 'Electric Motor Temperature' (measures_v2.csv) from{OFF}")
        print(f"      {DIM}https://www.kaggle.com/datasets/wkirgsn/electric-motor-temperature{OFF}")
        print(f"      {DIM}and place it in: {ROOT / 'data' / 'raw'}{OFF}")
        ok = False

    for mod, pip_name in [("pandas", "pandas"), ("numpy", "numpy"),
                          ("sklearn", "scikit-learn"), ("lightgbm", "lightgbm"),
                          ("matplotlib", "matplotlib"), ("pyarrow", "pyarrow")]:
        try:
            __import__(mod)
            print(f"  {GREEN}OK{OFF}  package           {pip_name}")
        except ImportError:
            print(f"  {RED}--{OFF}  package           {pip_name} missing")
            ok = False

    if not ok:
        print(f"\n  {YELLOW}Install packages with:{OFF}  pip install -r requirements.txt")
    print()
    return ok


QUICK_ENV = {
    "PMSM_FIG_DIR": "figures_quick",
    "PMSM_OUT_DIR": "outputs_quick",
    "PMSM_METRICS": "metrics_table_quick.csv",
}


def make_quick_dataset(n_rows: int = 320_000) -> Path:
    """Slice the dataset down to a few sessions so a smoke run finishes fast."""
    import pandas as pd

    sys.path.insert(0, str(SRC))
    from paths import DATA as full
    backup = full.with_name("measures_v2.full.csv")
    print(f"{YELLOW}--quick{OFF}  smoke run — NOT the real results.")
    print(f"        A slice of the data means shorter sessions and less thermal")
    print(f"        history, so accuracy will be much worse than the README's.")
    print(f"        Output goes to figures_quick/ and metrics_table_quick.csv,")
    print(f"        so your real figures are left untouched.\n")
    if not backup.exists():
        df = pd.read_csv(full)
        df.to_csv(backup, index=False)
    else:
        df = pd.read_csv(backup)
    # keep the benchmark test/val profiles plus enough others to train on
    keep = [65, 72, 60, 62, 74, 2, 4, 6, 11, 20, 27, 43, 47, 52, 13, 18, 30, 36]
    sub = df[df.profile_id.isin(keep)]
    if len(sub) > n_rows:
        sub = sub.groupby("profile_id", group_keys=False).head(n_rows // len(keep))
    sub.to_csv(full, index=False)
    print(f"  reduced to {len(sub):,} rows across {sub.profile_id.nunique()} sessions\n")
    return backup


def restore_dataset(backup: Path) -> None:
    if backup and backup.exists():
        shutil.move(str(backup), str(backup.with_name("measures_v2.csv")))
        print(f"\n{DIM}Full dataset restored.{OFF}")


def resolve(produces: str) -> Path:
    """Map a stage's declared output onto the active (possibly redirected) dirs."""
    head, _, tail = produces.partition("/")
    if head == "figures":
        return Path(os.environ.get("PMSM_FIG_DIR", ROOT / "figures")) / tail
    if head == "outputs":
        return Path(os.environ.get("PMSM_OUT_DIR", ROOT / "outputs")) / tail
    if head == "models":
        return Path(os.environ.get("PMSM_MODELS", ROOT / "models")) / tail
    return ROOT / produces


def run_stage(key: str, force: bool) -> tuple[bool, float, bool]:
    """Returns (ok, seconds, skipped)."""
    script, label, produces = STAGES[key]
    target = resolve(produces) if produces else None

    if not force and target and target.exists():
        print(f"{DIM}[skip]{OFF} {label:<28} {DIM}{produces} already exists{OFF}")
        return True, 0.0, True

    print(f"{CYAN}[run ]{OFF} {BOLD}{label}{OFF}  {DIM}(src/{script}){OFF}")
    t0 = time.time()
    proc = subprocess.run([sys.executable, str(SRC / script)], cwd=str(ROOT))
    dt = time.time() - t0

    if proc.returncode != 0:
        print(f"{RED}[FAIL]{OFF} {label} exited with code {proc.returncode} after {human(dt)}\n")
        return False, dt, False
    print(f"{GREEN}[done]{OFF} {label} in {human(dt)}\n")
    return True, dt, False


def summary() -> None:
    """Print the headline numbers if training has produced them."""
    import json

    results = Path(os.environ.get("PMSM_OUT_DIR", ROOT / "outputs")) / "results.json"
    if not results.exists():
        return
    R = json.loads(results.read_text())
    res = R["results"]
    best = min(res, key=lambda k: res[k]["RMSE"])

    print(hr("="))
    print(f"{BOLD}Results — held-out sessions (profiles {', '.join(map(str, R['split']['test']))}){OFF}\n")
    print(f"  {'Model':<30}{'RMSE':>8}{'MAE':>8}{'R2':>10}{'MaxAE':>9}{'±2°C':>9}")
    print(f"  {DIM}{'-'*74}{OFF}")
    for name, m in sorted(res.items(), key=lambda kv: kv[1]["RMSE"]):
        mark = f"{GREEN}*{OFF}" if name == best else " "
        print(f" {mark}{name:<30}{m['RMSE']:>8.2f}{m['MAE']:>8.2f}"
              f"{m['R2']:>10.4f}{m['MaxAE']:>9.2f}{m['within_2C']:>8.1f}%")
    print(f"\n  {GREEN}*{OFF} selected: {BOLD}{best}{OFF}")

    if "leak" in R:
        print(f"\n  {DIM}Leakage check — same model, random split instead of profile-wise:{OFF}")
        print(f"  {DIM}  R2 {R['leak']['R2']:.4f} / RMSE {R['leak']['RMSE']:.2f} °C "
              f"— inflated, and the reason the split protocol matters.{OFF}")
    print(hr("="))
    figdir = os.environ.get("PMSM_FIG_DIR", "figures")
    metrics = os.environ.get("PMSM_METRICS", "metrics_table.csv")
    print(f"\nFigures written to {BOLD}{figdir}/{OFF}  ·  metrics to {BOLD}{metrics}{OFF}")
    model = Path(os.environ.get("PMSM_MODELS", ROOT / "models")) / "final_temperature_model.joblib"
    if model.exists():
        print(f"Trained model at {BOLD}models/{model.name}{OFF} — "
              f"try {BOLD}python predict.py --demo{OFF}")
    if os.environ.get("PMSM_FIG_DIR"):
        print(f"{YELLOW}Reminder: this was a --quick smoke run on a slice of the data. "
              f"These are not the project's results.{OFF}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Run the PMSM winding-temperature pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="examples:\n"
               "  python run.py                   run everything\n"
               "  python run.py --quick           fast smoke run on a data slice\n"
               "  python run.py --stage train     re-run training only\n"
               "  python run.py --force           rebuild even if outputs exist\n")
    ap.add_argument("--stage", choices=ORDER, help="run a single stage instead of all")
    ap.add_argument("--from", dest="start", choices=ORDER, help="start at this stage and continue")
    ap.add_argument("--force", action="store_true", help="rebuild stages whose output already exists")
    ap.add_argument("--quick", action="store_true", help="smoke run on a slice of the data (minutes, not tens of minutes)")
    ap.add_argument("--list", action="store_true", help="list the stages and exit")
    ap.add_argument("--check", action="store_true", help="check the environment and exit")
    args = ap.parse_args()

    if args.list:
        print(f"\n{BOLD}Pipeline stages{OFF}  {DIM}(run in this order){OFF}\n")
        for i, k in enumerate(ORDER, 1):
            script, label, produces = STAGES[k]
            print(f"  {i}. {BOLD}{k:<10}{OFF}{label:<30}{DIM}-> {produces}{OFF}")
        print(f"\n{DIM}python run.py --stage <name>   to run just one{OFF}\n")
        return 0

    print(f"\n{BOLD}PMSM Thermal Virtual Sensor{OFF} {DIM}— winding temperature estimation pipeline{OFF}")
    print(hr() + "\n")

    if not check_environment():
        return 1
    if args.check:
        return 0

    backup = None
    if args.quick:
        os.environ.update(QUICK_ENV)
        backup = make_quick_dataset()
    force = args.force or args.quick

    if args.stage:
        todo = [args.stage]
    elif args.start:
        todo = ORDER[ORDER.index(args.start):]
    else:
        todo = ORDER

    print(hr())
    t_all = time.time()
    ran = skipped = 0
    try:
        for key in todo:
            ok, _, was_skipped = run_stage(key, force)
            if not ok:
                print(f"{RED}Pipeline stopped at stage '{key}'.{OFF}")
                return 1
            ran += not was_skipped
            skipped += was_skipped
    finally:
        if backup:
            restore_dataset(backup)

    print(f"{BOLD}Pipeline complete{OFF} — {ran} stage(s) run, {skipped} skipped, "
          f"{human(time.time() - t_all)} total.\n")
    summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
