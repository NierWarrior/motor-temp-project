"""
Derive the Google Colab edition of the project notebook.

The local notebook (notebooks/motor_temperature_prediction.ipynb, built by
make_notebook.py) is the single source of truth for all narrative and analysis.
This script reads it and applies only the changes Colab needs:

  1. a dependency cell (installs what Colab is missing, nothing it already has)
  2. a dataset-acquisition cell with three auto-tried routes
  3. PATH -> DATA_PATH, resolved by that cell
  4. a FAST_MODE switch for the ~20-minute hyperparameter search in Section 9
  5. the exported model written to /content and offered as a browser download
  6. Colab notebook metadata

Run after make_notebook.py:
    python docs_src/make_notebook.py && python docs_src/make_colab.py
"""

import pathlib
import nbformat as nbf

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "notebooks" / "motor_temperature_prediction.ipynb"
DST = ROOT / "notebooks" / "motor_temperature_prediction_colab.ipynb"

# The "Open in Colab" badge. Points at the hosted copy on Google Drive, which runs
# whatever the repository is doing without needing the repo to be public.
# A github-hosted alternative, if you ever want it instead:
#   https://colab.research.google.com/github/<user>/<repo>/blob/main/notebooks/motor_temperature_prediction_colab.ipynb
BADGE_URL = "https://colab.research.google.com/drive/1T3DjZiorgPdzEpxWozfu8nXM11XAUzZ_?usp=sharing"

nb = nbf.read(SRC, as_version=4)
cells = nb.cells


def md(s):
    return nbf.v4.new_markdown_cell(s.strip())


def co(s):
    return nbf.v4.new_code_cell(s.strip())


def find(predicate, what):
    hits = [i for i, c in enumerate(cells) if predicate(c)]
    if len(hits) != 1:
        raise SystemExit(f"expected exactly 1 cell for {what!r}, found {len(hits)}")
    return hits[0]


def patch(idx, old, new, label):
    src = cells[idx].source
    if src.count(old) != 1:
        raise SystemExit(f"{label}: {old!r} appears {src.count(old)}x, expected 1")
    cells[idx].source = src.replace(old, new)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Title cell — Colab badge and runtime expectations
# ─────────────────────────────────────────────────────────────────────────────
i_title = find(lambda c: c.source.startswith("# Predicting Electric Motor"), "title")
cells[i_title].source = cells[i_title].source.replace(
    "# Predicting Electric Motor Winding Temperature",
    "# Predicting Electric Motor Winding Temperature\n\n"
    f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]({BADGE_URL})",
    1,
).rstrip() + r"""

---

### Running this in Google Colab

**Runtime > Run all** executes the whole notebook end to end. No GPU is needed — every model
here is CPU-bound, so leave the accelerator set to **None**.

| | |
|---|---|
| Expected wall-clock | **35–50 min** on a free CPU runtime |
| Of which Section 9 (hyperparameter search) | **~20–30 min** — set `FAST_MODE = True` below to cut it to ~5 min |
| Peak RAM | **≈ 6 GB** (104 features x 1.33 M rows, float32). The standard ~12.7 GB runtime is enough; a High-RAM runtime is not required |
| Disk | ≈ 300 MB for the dataset |

Colab recycles idle runtimes, so if you plan to walk away, run it in two sittings
(Sections 1–8, then 9 onward) rather than leaving it unattended for an hour.
"""

# ─────────────────────────────────────────────────────────────────────────────
# 2. Setup cells, inserted after the "## 2. Dataset" narrative and before the
#    cell that loads the CSV
# ─────────────────────────────────────────────────────────────────────────────
i_load = find(lambda c: "PATH = " in c.source and "pd.read_csv(PATH)" in c.source, "data load")

setup_md = md(r"""
### Getting the dataset into Colab

The CSV is ~300 MB, so it is not in the repository. The next cell finds it whichever way you
bring it in and leaves the resolved location in `DATA_PATH`. It tries three routes in order and
stops at the first that works.

| Route | Set | What happens |
|---|---|---|
| **1 — already here** | nothing | Looks in `/content`, the current folder, and `data/raw/` |
| **2 — Google Drive** | `MOUNT_DRIVE = True` | Mounts your Drive and looks for `measures_v2.csv` in `MyDrive` (one folder deep). Best option if you will run this more than once — the file survives runtime restarts |
| **3 — Kaggle API** | `USE_KAGGLE = True` | Downloads [`wkirgsn/electric-motor-temperature`](https://www.kaggle.com/datasets/wkirgsn/electric-motor-temperature) directly. Needs a `kaggle.json` token (Kaggle > *Settings* > *API* > *Create New Token*); you will be prompted to upload it if it is not already present |

Manual upload also works if you prefer: use the folder icon in Colab's left sidebar to drop
`measures_v2.csv` into `/content`, then run the cell — route 1 will pick it up. Browser upload of
a 300 MB file is slow, so Drive or Kaggle is usually less painful.
""")

setup_deps = co(r'''
# ── dependencies ────────────────────────────────────────────────────────────
# Colab already ships numpy / pandas / scikit-learn / matplotlib. Only install
# what is actually missing, so the runtime does not get churned unnecessarily.
import importlib.util, subprocess, sys

for pkg in ["lightgbm", "pyarrow", "kaggle"]:
    if importlib.util.find_spec(pkg) is None:
        print(f"installing {pkg} ...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", pkg], check=False)

import sklearn, numpy, pandas
print(f"python       {sys.version.split()[0]}")
print(f"numpy        {numpy.__version__}")
print(f"pandas       {pandas.__version__}")
print(f"scikit-learn {sklearn.__version__}")
import lightgbm; print(f"lightgbm     {lightgbm.__version__}")
''')

setup_data = co(r'''
# ── configuration ───────────────────────────────────────────────────────────
MOUNT_DRIVE = False   # True  -> mount Google Drive and look for the CSV there
USE_KAGGLE  = True    # True  -> fall back to the Kaggle API (needs kaggle.json)
FAST_MODE   = False   # True  -> shrink the Section 9 search from ~25 min to ~5 min

# ── locate measures_v2.csv ──────────────────────────────────────────────────
import glob, os, sys
from pathlib import Path

IN_COLAB = "google.colab" in sys.modules
KAGGLE_DATASET = "wkirgsn/electric-motor-temperature"

SEARCH = [
    "measures_v2.csv",
    "/content/measures_v2.csv",
    "/content/data/raw/measures_v2.csv",
    "../data/raw/measures_v2.csv",
    "/content/drive/MyDrive/measures_v2.csv",
    "/content/drive/MyDrive/*/measures_v2.csv",
]

def locate():
    """First matching location wins; within a location, the largest file wins -
    a failed download can leave a stub next to the real thing."""
    for pattern in SEARCH:
        hits = [h for h in glob.glob(pattern) if os.path.isfile(h)]
        if hits:
            return max(hits, key=os.path.getsize)
    return None

DATA_PATH = locate()

# Route 2 — Google Drive
if DATA_PATH is None and IN_COLAB and MOUNT_DRIVE:
    from google.colab import drive
    drive.mount("/content/drive")
    DATA_PATH = locate()

# Route 3 — Kaggle API
if DATA_PATH is None and IN_COLAB and USE_KAGGLE:
    token = Path.home() / ".kaggle" / "kaggle.json"
    if not token.exists():
        local = sorted(glob.glob("/content/kaggle.json")) + sorted(glob.glob("kaggle.json"))
        if not local:
            print("Upload kaggle.json  (Kaggle > Settings > API > Create New Token)")
            from google.colab import files
            files.upload()
            local = sorted(glob.glob("kaggle.json")) + sorted(glob.glob("/content/kaggle.json"))
        if local:
            token.parent.mkdir(parents=True, exist_ok=True)
            token.write_bytes(Path(local[0]).read_bytes())
            token.chmod(0o600)
    if token.exists():
        import kaggle                      # authenticates on import
        print(f"downloading {KAGGLE_DATASET} ...")
        kaggle.api.dataset_download_files(KAGGLE_DATASET, path="/content", unzip=True)
        DATA_PATH = locate()

if DATA_PATH is None:
    raise FileNotFoundError(
        "measures_v2.csv not found.\n"
        "  - put it in /content (sidebar folder icon > upload), or\n"
        "  - set MOUNT_DRIVE = True if it is in your Google Drive, or\n"
        "  - set USE_KAGGLE = True and upload a kaggle.json token,\n"
        f"then re-run this cell. Searched: {SEARCH}"
    )

_bytes = os.path.getsize(DATA_PATH)
if _bytes < 200_000_000:
    raise ValueError(
        f"{DATA_PATH} is only {_bytes/1e6:.1f} MB; the real measures_v2.csv is about 300 MB.\\n"
        "That is a stub, a truncated upload, or a failed download rather than the "
        "dataset. Delete it and fetch it again:\\n"
        "  !rm -f /content/measures_v2.csv\\n"
        "then re-run this cell."
    )

print(f"dataset   : {DATA_PATH}")
print(f"size      : {_bytes/1e6:.0f} MB")
print(f"FAST_MODE : {FAST_MODE}")
''')

cells[i_load:i_load] = [setup_md, setup_deps, setup_data]
i_load += 3

# ─────────────────────────────────────────────────────────────────────────────
# 3. Point the loader at the resolved path
# ─────────────────────────────────────────────────────────────────────────────
patch(
    i_load,
    'PATH = "../data/raw/measures_v2.csv"   # <-- point this at your copy of the dataset',
    "PATH = DATA_PATH   # resolved by the setup cell above",
    "data path",
)

# ─────────────────────────────────────────────────────────────────────────────
# 4. FAST_MODE for the Section 9 search
# ─────────────────────────────────────────────────────────────────────────────
i_tune = find(lambda c: "RandomizedSearchCV(est, space" in c.source, "tuning")
patch(
    i_tune,
    "sub = df.loc[~te].iloc[::10]                     # train + val, never the test profiles",
    "STRIDE = 40 if FAST_MODE else 10                 # FAST_MODE thins the search set 4x\n"
    "sub = df.loc[~te].iloc[::STRIDE]                 # train + val, never the test profiles",
    "tuning stride",
)
patch(
    i_tune,
    '"model__learning_rate_init": [5e-4, 1e-3, 3e-3]}, 8),',
    '"model__learning_rate_init": [5e-4, 1e-3, 3e-3]}, 3 if FAST_MODE else 8),',
    "MLP n_iter",
)
patch(
    i_tune,
    '"l2_regularization": [0.0, 0.1, 1.0]}, 10),',
    '"l2_regularization": [0.0, 0.1, 1.0]}, 4 if FAST_MODE else 10),',
    "HGB n_iter",
)

cells.insert(i_tune, md(r"""
> **This is the slow cell — budget 20–30 minutes on a free Colab CPU runtime.**
>
> It fits 18 candidate models, each across 3 grouped folds, then refits the two winners on the
> full training set. If you only want to see the mechanics work, set `FAST_MODE = True` in the
> setup cell at the top and re-run from there: that thins the search set 4x and drops to 7
> candidates, finishing in about 5 minutes.
>
> `FAST_MODE` changes only the *search*, never the train/test split or the final evaluation — but
> the reported best hyperparameters and the final metrics will differ from the numbers discussed
> in the text below, which come from the full search. Leave it `False` to reproduce the report.
"""))
i_tune += 1

# ─────────────────────────────────────────────────────────────────────────────
# 5. Export the model somewhere retrievable, and offer the download
# ─────────────────────────────────────────────────────────────────────────────
i_dump = find(lambda c: 'joblib.dump(bundle' in c.source, "model export")
patch(
    i_dump,
    'joblib.dump(bundle, "final_temperature_model.joblib", compress=3)',
    "joblib.dump(bundle, MODEL_OUT, compress=3)",
    "dump path",
)
patch(
    i_dump,
    '''    print(f"exported -> final_temperature_model.joblib "
          f"({__import__('os').path.getsize('final_temperature_model.joblib')/1e6:.1f} MB)")''',
    '''    print(f"exported -> {MODEL_OUT} "
          f"({os.path.getsize(MODEL_OUT)/1e6:.1f} MB)")''',
    "dump message",
)
cells[i_dump].source = (
    "import os\n"
    "MODEL_OUT = \"/content/final_temperature_model.joblib\" if IN_COLAB \\\n"
    "            else \"final_temperature_model.joblib\"\n\n"
    + cells[i_dump].source
    + '''

# Colab's filesystem disappears with the runtime — pull the bundle down while it exists.
if IN_COLAB and bundle["model"] is not None:
    from google.colab import files
    files.download(MODEL_OUT)          # comment out if you would rather not download'''
)

# ─────────────────────────────────────────────────────────────────────────────
# 6. Colab metadata
# ─────────────────────────────────────────────────────────────────────────────
nb.metadata["colab"] = {
    "name": "motor_temperature_prediction_colab.ipynb",
    "provenance": [],
    "toc_visible": True,
}
nb.metadata["accelerator"] = "None"
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3"}
nb.metadata["language_info"] = {"name": "python"}

nbf.write(nb, DST)
n_md = sum(c.cell_type == "markdown" for c in cells)
n_co = sum(c.cell_type == "code" for c in cells)
print(f"wrote {DST.relative_to(ROOT)}  ({len(cells)} cells: {n_md} markdown, {n_co} code)")
