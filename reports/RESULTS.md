# Results Summary — Motor Winding Temperature Estimation
**UCS321 MST Mini Project · Problem Statement 6 (GE Power Systems)**

Copy these numbers straight into the report. Everything below was produced on
`measures_v2.csv` (1,330,816 samples, 69 sessions, 185 h) and is reproducible from
`motor_temperature_prediction.ipynb`.

---

## Headline result

Stator winding temperature estimated from **drive-measurable signals only**
(ambient, coolant, u_d, u_q, i_d, i_q, speed, torque) on **motor sessions never seen
during training**:

| Metric | Value |
|---|---|
| RMSE | **1.67 °C** |
| MAE | **1.26 °C** |
| R² | **0.9959** |
| Max absolute error | **9.84 °C** |
| Samples within ±2 °C | **81.3 %** |

Selected model: **MLP, 2 hidden layers of 128 units**, early stopping.
Test set: profiles **65 and 72** (55,395 samples, 462 min), held out entirely.

---

## Model comparison (test = profiles 65 & 72)

| Model | RMSE (°C) | MAE (°C) | R² | Max abs err (°C) | Within ±2 °C (%) |
|---|---|---|---|---|---|
| Linear regression, raw inputs | 17.79 | 14.37 | 0.5324 | 69.27 | 8.1 |
| Ridge regression, + EWMA features | 2.08 | 1.54 | 0.9936 | 26.19 | 71.7 |
| Random Forest (80 trees, depth 16) | 3.60 | 2.49 | 0.9808 | 15.56 | 56.8 |
| **MLP (2 × 128)** | **1.67** | **1.26** | **0.9959** | **9.84** | **81.3** |
| LightGBM (743 trees, early-stopped) | 2.50 | 1.85 | 0.9908 | 11.05 | 65.8 |

**Three things to say about this table in the viva:**

1. Linear regression goes from R² 0.53 → 0.99 with *no change of algorithm* — only
   features. Feature engineering beat model sophistication.
2. The MLP beats both tree ensembles. Trees are piecewise-constant and cannot
   extrapolate past the training envelope; held-out sessions contain operating
   points the training profiles never visit. A smooth model continues the trend.
3. RMSE and max error do not rank the models identically. For a thermal limit, the
   max-error column is the one that decides deployability.

---

## Ablation — where the accuracy comes from

Identical LightGBM, progressively richer features:

| Feature set | RMSE (°C) | R² |
|---|---|---|
| Raw inputs only (8 channels) | 14.39 | 0.6942 |
| + instantaneous physical derivations (i_s, u_s, S_el, i_s², P_mech, P_loss) | 14.58 | 0.6860 |
| + EWMA thermal-history features | **2.43** | **0.9913** |

Instantaneous derived quantities buy **nothing** (the small regression is within noise).
The entire gain comes from EWMA terms — i.e. from giving the model *thermal history*,
not from giving it more columns.

---

## Leakage study — why the split protocol matters

Same model, same features, only the split changes:

| Split | RMSE (°C) | R² |
|---|---|---|
| Random 80/20 over rows (**leaky**) | 0.66 | 0.9995 |
| Profile-wise, whole sessions held out (**honest**) | 2.50 | 0.9908 |

Random splitting understates RMSE by **~3.8×**. At 2 Hz, consecutive rows are
near-duplicates — a random split puts near-identical samples on both sides, so the
test set is effectively inside the training set. Most teams will report the 0.9995.

---

## Feature importance (LightGBM split counts)

All top-15 features are EWMA-derived. The strongest:

| Rank | Feature | Splits |
|---|---|---|
| 1 | `coolant_ewma_600s` | 2234 |
| 2 | `i_s_sq_ewma_600s` | 1935 |
| 3 | `i_s_ewma_600s` | 1841 |
| 4 | `S_el_ewma_600s` | 1659 |
| 5 | `coolant_ewms_120s` | 1346 |

The two dominant terms are the 600 s average of coolant temperature (the heat-sink
boundary condition) and the 600 s average of **i_s²** (the copper-loss term, P = I²R).
These are exactly the terms a lumped-parameter thermal model would name — strong
evidence the model learned the intended physics rather than an artefact.

---

## Method, in one paragraph (for the abstract)

Winding temperature was modelled as a supervised regression from eight
drive-measurable channels. Three co-located thermocouple channels
(`stator_tooth`, `stator_yoke`, `pm`) were dropped as target leakage, since they are
the very sensors the virtual sensor is meant to replace. Because a motor's
lumped-parameter thermal response is a first-order system whose solution is an
exponentially weighted integral of past losses, the eight raw channels were expanded
to 104 features comprising physical derivations (i_s, u_s, S_el, i_s², P_mech, P_loss)
and exponentially weighted moving averages and standard deviations at five thermal
time constants (30 s to 3600 s), computed per session so that no thermal state crosses
a session boundary. Five models were compared under a profile-wise split holding out
entire measurement sessions. The selected MLP achieves 1.67 °C RMSE and R² = 0.996 on
unseen sessions, with 81 % of samples within ±2 °C.

---

## Rubric mapping

| Criterion | Marks | Where it is evidenced |
|---|---|---|
| Problem Understanding & Objective Clarity | 5 | §1 — virtual-sensor framing, insulation limits, why max error is the right metric |
| Data Collection & Pre-processing | 10 | §2–§5 — 1.33 M samples, leakage-channel removal with justification, session-integrity checks, 8 → 104 features |
| Model Development & Implementation | 12 | §7 — five-model ladder, early stopping on a validation split |
| Performance Evaluation & Interpretation | 8 | §8 — five metrics, time-series overlays, residual analysis, *interpretation* of why MLP > trees |
| Innovation / Creativity | 5 | §5 physics-derived EWMA features; §6 + §9.2 leakage study; §9.1 ablation; §10 embedded deployment analysis |

---

## Figures

| File | Use it for |
|---|---|
| `00_flow_diagram.png` | **required** flow diagram — pre-processing + visualisation steps |
| `01_thermal_lag.png` | motivation: thermal inertia, the core insight |
| `02_ewma_motivation.png` | r 0.57 → 0.70 from one transform |
| `03_correlation.png` | EDA — no raw signal exceeds \|r\| 0.63 |
| `04_dataset_structure.png` | EDA — target distribution and session lengths |
| `05_model_comparison.png` | results — three metrics side by side |
| `06_predicted_vs_actual.png` | **the money figure** — tracking on unseen sessions |
| `07_residuals.png` | error distribution and bias check vs temperature |
| `08_feature_importance.png` | interpretation — thermal history dominates |
| `09_ablation_leakage.png` | innovation — ablation + leakage study |

---

## Running it

```bash
pip install pandas numpy scikit-learn lightgbm matplotlib pyarrow
jupyter notebook motor_temperature_prediction.ipynb
```

Set `PATH = "measures_v2.csv"` in the second code cell. Full run is roughly
20–30 minutes on a laptop; the notebook subsamples the training set for the slower
learners, which costs nothing because 2 Hz data is heavily autocorrelated.

`src/` holds the same pipeline as standalone modules if you prefer scripts to a
notebook: `build_features.py` → `train.py` → `results_figs.py`.
