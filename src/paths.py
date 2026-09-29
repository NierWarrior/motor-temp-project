"""Repo-relative paths, so the pipeline runs from any checkout.

Output locations can be redirected with environment variables, which is how
`run.py --quick` keeps a smoke run from overwriting real results:

    PMSM_FIG_DIR   where figures are written      (default: <repo>/figures)
    PMSM_OUT_DIR   where intermediates are written (default: <repo>/outputs)
    PMSM_METRICS   the metrics table path         (default: <repo>/metrics_table.csv)
    PMSM_MODELS    where the exported model goes   (default: <repo>/models)
    PMSM_DATA      the dataset                     (default: data/raw/measures_v2.csv,
                                                    falling back to the repo root)
"""
import os
from pathlib import Path

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent

FIG = Path(os.environ.get("PMSM_FIG_DIR", ROOT / "figures"))
OUT = Path(os.environ.get("PMSM_OUT_DIR", ROOT / "outputs"))
METRICS = Path(os.environ.get("PMSM_METRICS", ROOT / "metrics_table.csv"))
MODELS = Path(os.environ.get("PMSM_MODELS", ROOT / "models"))


def _find_dataset() -> Path:
    """data/raw/ is the conventional home; the repo root is accepted too."""
    if env := os.environ.get("PMSM_DATA"):
        return Path(env)
    preferred = ROOT / "data" / "raw" / "measures_v2.csv"
    legacy = ROOT / "measures_v2.csv"
    return legacy if (legacy.exists() and not preferred.exists()) else preferred


DATA = _find_dataset()

FIG.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
MODELS.mkdir(parents=True, exist_ok=True)

if not DATA.exists():
    import warnings
    warnings.warn(
        f"Dataset not found at {DATA}. Download 'Electric Motor Temperature' "
        "(measures_v2.csv) from Kaggle and place it in data/raw/.",
        stacklevel=2,
    )
