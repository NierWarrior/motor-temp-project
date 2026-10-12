# Document and notebook builders

Nothing in `reports/` or `notebooks/` is hand-maintained. All of it is
generated, so it stays in step with the figures and the numbers in `outputs/`.

## Report and slide deck

```bash
npm install docx pptxgenjs     # only if the requires fail; usually preinstalled
node docs_src/build_report.js  # -> reports/UCS321_Report.docx
node docs_src/build_deck.js    # -> reports/UCS321_Presentation.pptx
```

Both read PNGs straight from `figures/`, so regenerating the figures and
re-running these two commands refreshes every document.

## Notebooks

`make_notebook.py` is the single source of truth for the analysis notebook.
**Edit it, never the `.ipynb`** — a regeneration overwrites direct edits to the
notebook file.

```bash
python docs_src/make_notebook.py   # -> notebooks/motor_temperature_prediction.ipynb
python docs_src/make_colab.py      # -> notebooks/motor_temperature_prediction_colab.ipynb
```

`make_colab.py` reads the notebook the first command produced and applies only
the changes Colab needs, so the two editions can never drift apart in content:

| Change | Why |
|---|---|
| Dependency cell | Installs `lightgbm`, `pyarrow`, `kaggle` only if missing |
| Dataset cell | Resolves `measures_v2.csv` via local file, Google Drive, or the Kaggle API, into `DATA_PATH` |
| `PATH = DATA_PATH` | The repo-relative path does not exist in Colab |
| `FAST_MODE` switch | Shrinks the ~25-minute Section 9 search to ~5 minutes |
| Model export | Writes to `/content` and offers a browser download, since Colab's disk is discarded with the runtime |
| Colab metadata + badge | "Open in Colab" button, accelerator pinned to None |

Run the notebook builders in that order; `make_colab.py` fails loudly if a cell
it expects to patch has moved or changed, rather than producing a broken notebook.

### The "Open in Colab" badge

`make_colab.py` sets `BADGE_URL` to the hosted copy on Google Drive:

```
https://colab.research.google.com/drive/1T3DjZiorgPdzEpxWozfu8nXM11XAUzZ_?usp=sharing
```

Change that one constant and re-run `python docs_src/make_colab.py` to repoint it. The
two badges in the top-level `README.md` are separate and have to be edited there. If you
would rather serve the notebook straight from GitHub, the github.com form is in a comment
beside `BADGE_URL` — it needs the repository to be public, or Colab asks the viewer to
authenticate.
