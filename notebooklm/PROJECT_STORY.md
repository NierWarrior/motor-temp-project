# Teaching a Motor to Feel Its Own Temperature
## The complete story of a machine-learning virtual sensor

**UCS321 — Artificial Intelligence for Engineers · Mid-Semester Mini Project**
**Problem Statement 6 — General Electric (GE) Power Systems**
Thapar Institute of Engineering & Technology, Patiala

> **Note to the narrator:** This document is the complete record of the project — the problem, the reasoning, every decision and why it was made, the dead ends, the results, and the honest limitations. It is written as prose rather than slides so that it can be read aloud as a continuous story. Every number in it is real and was measured. Where a figure is referenced, the document describes in words what that figure shows, so the explanation stands on its own without the image.

---

# PART ONE — THE PROBLEM

## 1.1 A machine that cannot tell you it is dying

Inside every electric motor is a coil of copper wire called the **stator winding**. When current flows through it, the motor turns. But copper has resistance, and resistance means that some of the electrical energy does not become motion — it becomes heat, right there in the wire.

That copper wire is not bare. It is coated in a thin layer of enamel insulation, a few hundredths of a millimetre thick, which keeps adjacent turns of the coil from touching each other. If that enamel fails anywhere along the winding, two turns short together, and the motor is destroyed — not degraded, destroyed.

The enamel is the weak link, and what kills it is heat. Industrial motors typically use what is called **Class H insulation**, rated to roughly **180 degrees Celsius**. Above that rating the enamel does not fail instantly; it degrades chemically. The accepted engineering rule of thumb is that **insulation life roughly halves for every 10 degrees Celsius of sustained overtemperature.** A motor run 20 degrees too hot does not last 80 percent as long — it lasts about a quarter as long.

This makes winding temperature the single most important number in the operation of the machine. It is the constraint that sets how hard the motor is allowed to work.

## 1.2 Why this is worth money, not just worth knowing

Consider two motor controllers driving identical machines.

The first controller knows the winding temperature accurately, in real time. When the winding is cool it can push the motor into its short-term overload capability — pulling far more current than the continuous rating for seconds or minutes — because it can see exactly how much thermal headroom remains, and back off precisely when the margin closes.

The second controller does not know. It has to assume the worst case at all times, so it applies a fixed conservative derating: never exceed some safe current, regardless of how cold the machine actually is. That controller gives up torque the motor could physically have delivered. The hardware is capable; the controller simply cannot prove it is safe.

So accurate winding temperature is not a diagnostic nicety. It converts directly into usable power density from hardware you already own.

## 1.3 The catch: you cannot measure it in a real product

The obvious answer is to put a sensor on the winding. On a laboratory test bench, that is exactly what engineers do — a thermocouple or thermistor bonded directly onto the copper, giving a continuous ground-truth reading.

In a motor you actually ship, it is impractical, for reasons that stack up:

- The sensor must survive sitting on a conductor at high electrical potential.
- It must survive constant vibration and thousands of thermal cycles between ambient and 150 degrees.
- Its wires must be routed out through a sealed housing without compromising the seal — adding a new path for contamination and a new thing that can break.
- And all of that has to cost almost nothing, because volume manufacturing does not tolerate parts that do not earn their place.

Put together, the cost and the reliability penalty do not survive contact with a real bill of materials. This is why test benches have winding thermocouples and the motors in your washing machine, your lift, your factory conveyor and your electric car do not.

## 1.4 What the motor *does* already know

Here is the opening. A modern motor drive performs something called **field-oriented control**, and to do that it must already measure, continuously and for free:

- **Phase currents**, expressed in the rotor reference frame as two numbers, `i_d` and `i_q`
- **Terminal voltages**, likewise as `u_d` and `u_q`
- **Rotor speed**, in revolutions per minute
- **Shaft torque**, measured or estimated from current
- **Coolant temperature** and **ambient temperature**, from cheap external sensors that any liquid-cooled drive already has

Eight signals. All present. All already being sampled many times per second. None of them costing a single extra rupee.

## 1.5 The objective

> **Estimate stator winding temperature from the eight signals a motor drive already measures, accurately enough that a controller can use the estimate as a thermal protection limit in place of a physical sensor.**

In industry this is called a **virtual sensor**, or sometimes a soft sensor: a piece of software that stands in for a piece of hardware. The physical thermocouple exists on the test bench, long enough to teach the model what the relationship looks like. After that the model carries the knowledge, and the sensor is not needed again.

## 1.6 An engineering decision hiding inside the metric

Most machine-learning projects report average error and stop. For this problem, that would be a mistake, and recognising why is part of the engineering.

Imagine a model with a mean absolute error of 1 degree — excellent by any normal standard — that once, under some unusual load pattern, underestimates by 20 degrees. The average says the model is superb. The motor is destroyed anyway, because thermal failure happens at the worst moment, not the average moment.

So this project reports, alongside the conventional metrics, two that are specific to the job:

- **Maximum absolute error** — the single worst deviation across the entire held-out dataset. This is the number a protection engineer uses to size the safety margin below the insulation rating.
- **Percentage of samples within ±2 degrees Celsius** — the fraction of operating time for which the estimate is good enough to act on directly.

As will become clear later, these two metrics do *not* rank the candidate models in the same order as RMSE does. That disagreement turns out to be one of the more interesting findings in the project.

---

# PART TWO — THE DATA

## 2.1 Where it came from

The dataset is the **Electric Motor Temperature** collection recorded by the Department of Power Electronics and Electrical Drives — abbreviated LEA — at **Paderborn University** in Germany, published on Kaggle as the file `measures_v2.csv`.

It is telemetry from a real three-phase permanent-magnet synchronous motor — a PMSM — mounted on a dynamometer test bench and driven through a wide range of speeds and loads under deliberately varied excitation patterns. The motor on that bench is fully instrumented, including the winding thermocouple that a production motor would not have.

The scale:

- **1,330,816 samples**
- Recorded at **2 Hertz** — one reading every half-second
- Across **69 independent measurement sessions**, each identified by a `profile_id`
- Totalling approximately **185 hours** of running
- With the target, winding temperature, ranging from **18.6 to 141.4 degrees Celsius**

Each session is a separate experiment: the bench was started, driven through some schedule of speeds and loads for anywhere from eighteen minutes to six hours, and stopped. Sessions are not continuations of one another. This fact becomes extremely important later.

## 2.2 The data quality audit

Before trusting any of it, the dataset was audited systematically. The results:

- **Zero missing values.** Not a single empty cell in 17.3 million data points.
- **Zero infinite values.**
- **Zero duplicate rows.**
- **No non-numeric columns**, so no parsing surprises.
- **No constant or near-constant columns** — every channel carries information.
- **All 69 sessions are stored contiguously** in the file, with no interleaving.

That last point is not cosmetic. The entire feature engineering strategy, described shortly, depends on processing each session as an unbroken block. Had rows from different sessions been scattered through the file, the method would have silently mixed unrelated recordings together.

Three things did get flagged by the automated checks, and each was investigated rather than assumed:

**First flag: 69,386 rows — 5.2 percent of the data — where winding temperature sits *below* ambient temperature.** That looks thermodynamically impossible. It is not. In 99.9 percent of those rows the coolant is also below ambient — a median of 18.5 degrees against an ambient of 23 — and the current is near zero, a median of 2.3 amperes against 110 overall. This is a liquid-cooled motor sitting idle with chilled coolant running through it. The machine is being actively refrigerated below room temperature. Entirely physical.

**Second flag: nine rows with negative rotor speed.** Eight of them form one contiguous four-second stretch in session 51, in which speed sweeps down through zero and back, with torque crossing zero alongside it. That is a genuine direction reversal captured mid-manoeuvre, not sensor noise.

**Third flag: 85 samples where winding temperature changes by more than one degree in a single half-second step.** All of them sit between 106 and 109 degrees with roughly 194 amperes flowing. That is real, rapid heating under heavy load. None of them occur at a session boundary, which rules out a stitching artefact.

So: the dataset is clean, nothing required repair, and — importantly — nothing was quietly wrong in a way that would have poisoned the results.

---

# PART THREE — THE DECISIONS

Three decisions shaped this project more than any choice of algorithm. Each one involved deliberately doing something that made the headline numbers *worse* in exchange for the result actually meaning something.

## 3.1 Decision one: deleting the three best features

The dataset does not contain only the winding thermocouple. It contains three more temperature channels:

- `stator_tooth` — a thermocouple in the stator tooth
- `stator_yoke` — one in the stator yoke
- `pm` — one measuring the permanent magnet

All three correlate with the winding temperature at above **r = 0.95**. Feed them to any model and it will produce a spectacular coefficient of determination almost immediately.

**All three were discarded.** For two reasons, and both matter.

**The first reason is that keeping them defeats the entire point.** Those three channels are physical thermocouples bolted into the machine — exactly the hardware the virtual sensor exists to eliminate. A model that needs `stator_tooth` as an input cannot run on a motor that has neither `stator_tooth` nor a winding sensor. Its accuracy would be perfect and completely useless.

**The second reason is that it constitutes target leakage.** The tooth and yoke thermocouples sit millimetres from the winding inside the same block of laminated iron, sharing its thermal mass. A model using them is not learning how electrical excitation becomes heat — it is interpolating between three thermometers that are all measuring nearly the same lump of metal. Nothing it learned would transfer to any machine other than this one instrumented bench motor.

The coolant and ambient channels were **kept**, because those are cheap external sensors that any liquid-cooled drive already carries. That leaves the eight drive-measurable inputs.

This is the decision that an examiner is most likely to probe, and the answer is worth stating crisply: *yes, accuracy would be higher with them, and the result would be worthless.*

## 3.2 The observation that changed everything

With the inputs settled, the next step was to look at the data — and one picture reframed the whole problem.

Plot, on a shared time axis for a single long session, three things: motor speed, current magnitude, and the temperatures.

Speed and current are **step functions**. The bench commands a new operating point and the current is there within one sample — half a second. The traces look almost square.

The winding temperature does nothing of the sort. When current steps up, temperature begins a slow exponential climb that takes **minutes** to settle. And when the current steps back down, the temperature *keeps rising for a while* before it turns around and begins an equally slow decay.

This is thermal inertia, and it has a hard consequence:

> **The winding temperature is not a function of the current flowing right now. It is a function of all the heat that has accumulated over the recent past.**

A model given only instantaneous readings is being asked to infer the value of a stored quantity from the rate at which it is being filled. For a system with memory, this is not merely difficult — it is impossible in principle. You cannot know how full a bathtub is by looking only at the tap.

The numbers confirm it. Across the whole dataset, **no raw electrical channel reaches a correlation of 0.63 with the target.** The strongest single predictor, `i_d`, manages 0.624. Apparent power reaches 0.599. That ceiling is not a data quality problem; it is thermal inertia expressed arithmetically.

This established, very early, that the project would be won or lost on **feature engineering**, not on model selection.

## 3.3 Decision two: deriving the features from physics instead of guessing

Here is the step that makes this project more than a standard regression exercise.

Rather than trying smoothing windows until something worked, the feature set was derived from the **lumped-parameter thermal model** of an electrical machine — the standard first-principles description used in motor design.

Treat the winding as a single thermal mass with heat capacity `C_th`, losing heat to its surroundings through a thermal resistance `R_th`. Energy conservation gives a first-order differential equation: the rate of change of temperature equals the heat going in, minus the heat escaping, divided by the heat capacity.

Solving that differential equation gives the temperature at any moment as an **integral over all past losses, with each moment in the past weighted by an exponential decay** — recent heat counts fully, heat from long ago has mostly leaked away.

And here is the key realisation. That exponentially-weighted integral, written in discrete time for data sampled at fixed intervals, **is exactly an Exponentially Weighted Moving Average** — an EWMA. The recursive form is strikingly simple:

> new average = α × (this sample) + (1 − α) × (previous average)

So computing EWMAs of the loss-related signals is not a smoothing trick someone tried. **It is the analytical solution of the thermal physics, written down as a feature.** That is why it works so dramatically, and it is the single strongest thing to say about this project.

### What was actually computed

**Physically-motivated derived quantities.** The dq-frame components are convenient for control but not individually meaningful thermally. What heats a winding is ohmic loss, which is proportional to *the square of current*. So the model is handed the magnitude and its square directly, rather than being asked to rediscover the square law from two orthogonal components:

- Current magnitude `i_s`, the root of `i_d` squared plus `i_q` squared
- Voltage magnitude `u_s`, likewise from `u_d` and `u_q`
- Apparent electrical power `S_el`, one-and-a-half times `i_s` times `u_s`
- **`i_s` squared** — the copper-loss term, the single most physically important derived quantity
- Mechanical power out, from torque and speed
- A loss proxy: electrical power in, minus mechanical power out

**Thermal history features.** A real machine is not one thermal mass. The copper responds in tens of seconds. The laminated iron takes minutes. The housing and coolant circuit take tens of minutes. Rather than trying to identify these time constants precisely — which would require per-machine calibration and defeat the purpose — the approach was to **bracket the plausible range and let the model choose**: EWMAs at **five spans of 30, 120, 600, 1800 and 3600 seconds**, plus an exponentially weighted *standard deviation* at each span, which encodes how volatile the recent duty cycle has been.

Nine signals were filtered this way, at five spans, with two statistics each: 90 thermal features.

**Eight raw channels became 104 engineered features.**

### The detail that is easy to get wrong

Every single EWMA is computed **within a `profile_id` group**, never across the whole file.

Sessions are separate experiments run at different times. If the recursive filter were allowed to run across a session boundary, the first minutes of each session would inherit the thermal state of a completely unrelated recording. It would be a subtle, invisible form of leakage — and the reported accuracy would look slightly better for it.

### Does one transform actually help?

Before fitting any model at all, a single feature was examined in isolation. Instantaneous current magnitude correlates with winding temperature at **r = 0.57** — a diffuse, nearly structureless cloud when plotted. The same signal, passed through a single ten-minute exponential filter, correlates at **r = 0.70**, and the scatter resolves into a coherent band.

One transform. No model yet.

## 3.4 Decision three: never splitting randomly

The third decision is the one most likely to separate this project from others working on time-series data.

The standard move in every tutorial is `train_test_split(X, y, test_size=0.2)`. On this dataset, that produces a meaningless number, and the reason is worth stating precisely.

Samples are half a second apart. A motor's winding temperature physically cannot change appreciably in half a second — the audit confirmed the largest observed jump in the entire dataset is 1.39 degrees, and the 99.99th percentile is under one degree. Consecutive rows are therefore **near-duplicates of one another**.

A random split scatters these near-identical twins across both sides of the partition. For almost every row in the test set, a virtually identical row sits in the training set. The test set is effectively *inside* the training set. The model is rewarded for memorisation, and the reported score measures nothing about generalisation.

The protocol adopted instead holds out **entire measurement sessions**:

- **Training: 64 sessions, 1,211,517 samples**
- **Validation: 3 sessions (profiles 60, 62 and 74), 63,904 samples**
- **Test: 2 sessions (profiles 65 and 72), 55,395 samples** — roughly 7.7 hours of running

Profiles 65 and 72 are the benchmark sessions used in the published academic literature on this test bench, so the results are comparable with prior work.

Under this protocol the model is evaluated the way it would actually be used: **on a motor run it has never seen.**

The cost of getting this wrong was measured directly, and appears in Part Five.

---

# PART FOUR — BUILDING AND COMPARING THE MODELS

## 4.1 The ladder

Five models were trained, deliberately arranged from the simplest thing that could possibly work to the most flexible, so that each increase in complexity had to justify itself against the rung below:

1. **Linear regression on the eight raw inputs** — the honest floor. What you get with no feature engineering at all.
2. **Ridge regression on all 104 engineered features** — isolates exactly what the feature work bought.
3. **Random Forest** — 80 trees, depth 16. A non-parametric reference point.
4. **Multilayer Perceptron (MLP)** — a neural network, two hidden layers of 128 units, with early stopping.
5. **LightGBM** — gradient-boosted trees, early-stopped on the validation sessions at 743 trees.

Every model saw the identical training partition and was scored on the identical held-out sessions, so the comparison isolates the model and nothing else.

A practical note: the Random Forest and MLP were fitted on every tenth training sample. Because 2 Hz data is so heavily autocorrelated, this discards almost no information while cutting computation by an order of magnitude.

## 4.2 The central result

Before the full table, one pair of rows deserves to be read on its own, because it is the main finding of the entire project:

| Model | RMSE | R² | Within ±2 °C |
|---|---|---|---|
| Linear regression, 8 raw inputs | **17.79 °C** | **0.5324** | 8.1 % |
| Linear regression, + EWMA features | **2.08 °C** | **0.9936** | 71.7 % |

The algorithm is identical. The data is identical. The training procedure is identical. The *only* thing that changed is that the inputs now encode thermal history.

**Root-mean-square error fell from 17.79 degrees to 2.08 degrees. R-squared rose from 0.53 to 0.99.**

Stated plainly: **domain-informed feature engineering outperformed every increase in model sophistication attempted in this project.** A simple linear model with physics-derived inputs beats sophisticated models with naive inputs, and it is not close.

## 4.3 The full comparison

| Model | RMSE (°C) | MAE (°C) | R² | Max error (°C) | Within ±2 °C |
|---|---|---|---|---|---|
| Linear (raw inputs) | 17.79 | 14.37 | 0.5324 | 69.27 | 8.1 % |
| Ridge (+ EWMA features) | 2.08 | 1.54 | 0.9936 | 26.19 | 71.7 % |
| Random Forest (80 trees) | 3.60 | 2.49 | 0.9808 | 15.56 | 56.8 % |
| **MLP (2 × 128)** | **1.67** | **1.26** | **0.9959** | **9.84** | **81.3 %** |
| LightGBM (743 trees) | 2.50 | 1.85 | 0.9908 | 11.05 | 65.8 % |

Three things in this table are more interesting than the winner.

### Finding one: the neural network beats both tree ensembles

This runs against the common wisdom that gradient-boosted trees dominate tabular problems. The reason is structural, not accidental.

**A tree ensemble is a piecewise-constant function.** Its prediction for any input is the average of the training samples that landed in the same leaf. It therefore *cannot produce a value outside the range it saw during training* — it has no mechanism for continuing a trend beyond its data.

The held-out sessions contain operating conditions the 64 training sessions never visited, and at those points a tree can only clamp to its nearest leaf. An MLP is a smooth function and extrapolates gracefully.

**This claim was tested, not assumed.** Measuring distance in the standardised 104-dimensional feature space: training points sit a median of **0.16** from their nearest training neighbour. Test points sit a median of **3.85** — **24 times further away**. Fully **75.6 percent of test points lie beyond the 99th percentile** of normal training-to-training distance.

There is a subtlety worth stating, because it is the kind of thing an examiner probes: *every individual feature's range overlaps* between train and test. Not one of the 104 features has more than one percent of test rows outside its training minimum and maximum. But marginal coverage is not joint coverage. The test sessions live in a genuinely distant region of the combined feature space, even though no single feature looks unusual. That is precisely the regime where smoothness wins.

### Finding two: ridge regression beats LightGBM

Once the features encode the physics, the remaining relationship between features and target is close to linear. A low-variance estimator then generalises across unseen sessions better than a high-capacity one, which fits session-specific structure that does not transfer.

### Finding three: the metrics disagree, and the disagreement matters

Ridge regression achieves RMSE of 2.08 — better than LightGBM's 2.50. But Ridge's **worst-case error is 26.19 degrees**, against LightGBM's **11.05**.

For a thermal protection function, that second column is the one that governs. **A model selected on RMSE alone would have been the wrong choice.** This is exactly the scenario sketched back in section 1.6, appearing for real in the results.

## 4.4 Tuning — without quietly undoing the split discipline

The ladder used fixed, sensible configurations. The two strongest families were then tuned properly: the MLP, and a HistGradientBoosting model included because it is the model a well-regarded public project on this same dataset selected.

The search was a randomised search over hyperparameters, but with **one constraint that matters more than the search itself**: cross-validation used **GroupKFold grouped on `profile_id`**.

This means a candidate configuration is **never scored on a session it was fitted on**. A plain K-fold inside the search would have reintroduced exactly the leakage the outer split was designed to remove — and it would have done so invisibly, because the cross-validation score would simply have looked better. It is a trap that is easy to fall into after getting the outer split right.

Eighteen candidate configurations across three grouped folds, about nineteen minutes of search. The winning configuration was then refitted on the full training partition.

**Selected hyperparameters for the winning MLP:** two hidden layers of 128 units, L2 regularisation `alpha = 0.01`, initial learning rate 0.001, with early stopping.

## 4.5 The final result

| Model | RMSE (°C) | MAE (°C) | R² | Max error (°C) | Within ±2 °C |
|---|---|---|---|---|---|
| **MLP, tuned — SELECTED** | **1.54** | **1.10** | **0.9965** | 11.32 | **84.2 %** |
| HistGradientBoosting, tuned | 2.39 | 1.75 | 0.9915 | **9.53** | 65.0 % |
| MLP, untuned baseline | 1.67 | 1.26 | 0.9959 | 9.84 | 81.3 % |

**The headline: winding temperature estimated to 1.54 degrees RMSE, R-squared of 0.9965, with 84.2 percent of all samples within two degrees — on motor sessions the model had never seen.**

And an honest footnote that is deliberately not buried: **tuning did not improve worst-case error. It got slightly worse**, from 9.84 to 11.32 degrees, because the search optimised RMSE and nothing in the objective constrained the tail. If worst-case error were the selection criterion, the tuned HistGradientBoosting model at 9.53 degrees would win instead. Selecting on RMSE and then disclosing max error is the honest order; retrofitting the criterion to whichever model happened to win is not.

One more number worth explaining before anyone asks: the cross-validated RMSE during tuning was 3.04 degrees, far worse than the 1.54 achieved on test. That is expected, not alarming. Each grouped fold trains on only about two-thirds of the sessions, so every candidate is fitted on far less thermal diversity than the final model receives. Grouped CV is useful for *ranking* candidates, not for estimating deployed accuracy.

---

# PART FIVE — PROVING IT IS REAL

A good result is not the same as a trustworthy one. Three studies were run to test whether this one holds up.

## 5.1 The ablation: where does the accuracy actually come from?

An identical LightGBM model was fitted three times against progressively richer feature sets, holding everything else constant.

| Feature set | RMSE | R² |
|---|---|---|
| 8 raw input channels | 14.39 °C | 0.6942 |
| + instantaneous physical derivations | 14.58 °C | 0.6860 |
| **+ EWMA thermal history** | **2.43 °C** | **0.9913** |

Read the middle row carefully. Adding current magnitude, apparent power and the loss proxy — all physically meaningful quantities — bought **nothing**. The tiny regression from 0.6942 to 0.6860 is within run-to-run variation.

Only the thermal history moves the result, and it moves it by a factor of six.

**This establishes something a simple before-and-after could not: the gain comes specifically from supplying memory of the past, not merely from having more columns in the table.**

## 5.2 The leakage study: what the wrong split would have told us

The same model and the same features were evaluated twice, varying only the partitioning scheme.

| Split protocol | RMSE | R² |
|---|---|---|
| Random 80/20 over individual rows | **0.66 °C** | **0.9995** |
| Profile-wise, whole sessions held out | **2.50 °C** | **0.9908** |

Random splitting understates the error by a factor of approximately **3.8**.

The randomly-split model reports an R-squared of 0.9995 — a figure that describes its ability to reproduce samples it has already effectively seen. The profile-wise figure of 0.9908 describes what the model would actually do on a new motor run.

**Methodological conclusion:** for time-series data sampled faster than the dynamics of the system being measured, grouped splitting is not a refinement — it is a correctness requirement. Any result obtained under random splitting on such data should be treated as uninformative.

## 5.3 Interpretability: did the model learn the physics, or a coincidence?

The third check asks what the trained model actually relies on. Ranking features by how often the gradient-boosted model used them to make a decision:

1. `coolant_ewma_600s` — the 600-second average of coolant temperature
2. `i_s_sq_ewma_600s` — the 600-second average of **current squared**
3. `i_s_ewma_600s`
4. `S_el_ewma_600s`
5. `coolant_ewms_120s`

**Every single one of the top fifteen features is thermal-history derived.** Not one instantaneous sensor reading makes the list.

And the top two are the most telling result in the project. Go back to the lumped-parameter thermal model from section 3.3. That equation has essentially two driving terms: **the heat going in**, which is copper loss, proportional to current squared; and **the boundary condition the heat escapes to**, which for a liquid-cooled machine is the coolant temperature.

The model was given no information about motor thermodynamics beyond a choice of which signals to filter and over what spans. It independently concentrated on **exactly the two terms a first-principles thermal model names as dominant.**

That closes the loop: the features were derived from physics, and the trained model rediscovered the same physics from the data. It is the strongest available evidence that the result is grounded rather than an artefact of the dataset.

## 5.4 Where the error actually lives

Breaking the error down three ways on the held-out sessions:

**By operating temperature.** Median absolute error stays near one degree across every band from 18 to 145 degrees. Accuracy does not decay when the machine is hot — which matters enormously, because the hot regime is the *only* one in which a thermal protection estimate is ever consulted. A model that were accurate when cool and poor when hot would be useless.

**By load.** Grouping by current magnitude from idle through to peak, the median error again holds near one degree. The tail widens moderately under heavy load, but the centre does not move.

**By time into the session.** This is where the real structure appears. **The largest errors are concentrated in the first minutes of every session.** The reason is mechanical: the 1800-second and 3600-second EWMAs begin each session from a zero initial state and take their full span to converge. During that warm-up the longest-memory features are reporting a partially-formed average.

That is the intrinsic cost of a recursive feature set, and it is the single most addressable weakness in the model.

---

# PART SIX — IT HAS TO RUN ON THE MOTOR

A virtual sensor that only works in a notebook is an analysis, not a product. The deployment arithmetic was checked.

**Computation.** The selected network is two hidden layers of 128 units over 104 inputs — roughly **30,000 multiply-accumulate operations per inference**. The thermal dynamics need updating only at 2 Hz, so that is about **60,000 operations per second**. For any modern motor-control microcontroller this is negligible. For an FPGA it is trivial.

**The feature extractor is unusually hardware-friendly, and this is the part worth dwelling on.** Each EWMA is a single-pole infinite-impulse-response filter: one multiply, one add, one register holding the previous value. The entire 104-feature extractor costs roughly **90 registers and 90 multiply-accumulates per sample**, with **no windowing buffer and no stored history whatsoever**.

Compare that with the obvious alternative. A conventional sliding-window average over one hour at 2 Hz would require **7,200 buffered samples per signal**. The recursive formulation requires **one**. That is the difference between a feature set that fits on a microcontroller and one that does not — and it is a direct consequence of having derived the features from the differential equation rather than reaching for a moving window.

**Numerical precision.** Temperatures span 18 to 141 degrees and need about 0.1 degree resolution, so 16-bit fixed point suffices at the output. The accumulators need more headroom: at a 3600-second span the per-sample update coefficient is approximately 0.00014, so accumulator precision rather than output precision is the binding constraint. A Q16.16 format would be a sensible starting point, with the quantised model re-characterised against the same held-out sessions before deployment.

---

# PART SEVEN — HONEST LIMITATIONS

Stated plainly, because a project that claims no weaknesses has not been examined properly.

1. **Worst-case error is 11.32 degrees.** A deployed thermal limit still needs a safety margin below the insulation rating. The model shrinks that margin relative to a fixed conservative derating; it does not remove it.

2. **One machine, one test bench.** Transferring to a different motor design would require retraining, or a transfer-learning approach using limited data from the new machine. Nothing here proves the relationship generalises across motor geometries.

3. **Warm-up.** The first minutes of any session are predicted from partially-converged filter states.

4. **Tuning improved average error but not worst-case error**, because nothing in the objective constrained the tail.

5. **Five training sessions are shorter than the longest EWMA span.** Profiles 47, 46, 52, 64 and 51 run between 18 and 52 minutes, while the 3600-second filter needs a full hour to converge. About 1.5 percent of training rows therefore carry a partially-converged feature. None of these sessions are in the validation or test set, so this cannot inflate the reported results — but strictly, not every feature means precisely the same thing in every training row.

6. **The gap between cross-validated and test performance is large** — 3.04 against 1.54 degrees — because grouped folds train on far fewer sessions. The CV number ranks candidates; it does not estimate deployed accuracy.

7. **Session identity must be supplied at inference time.** The model is not a pure function of an instantaneous sample; it needs correctly-segmented chronological history, because the features are averages over that history.

8. **No uncertainty estimate.** A protection function would benefit from a prediction interval rather than a point estimate, and none of these models provides one.

---

# PART EIGHT — WHAT WE WOULD DO NEXT

- **Sequence models.** A temporal convolutional network or an LSTM that *learns* the thermal time constants from data, rather than having them fixed as five chosen EWMA spans.
- **Multi-output prediction** of all four temperature channels under one model, exploiting the shared thermal structure between winding, tooth, yoke and magnet.
- **A physics-informed loss term** that penalises violations of the first-order thermal differential equation, constraining the model to physically realisable trajectories. This is the most promising route to reducing worst-case error specifically.
- **Quantile regression or conformal prediction**, to produce a defensible upper bound rather than a point estimate — which is what a protection limit actually wants.
- **Fixed-point quantisation and a register-transfer-level implementation** of the EWMA feature extractor, with hardware-in-the-loop validation against the same held-out sessions.

---

# PART NINE — THE PROJECT AS A SEQUENCE OF ACTIONS

For a narrator who wants to walk through what was actually done, in order:

**Step 1 — Read the problem statement and reframe it.** The statement asked for a regression model predicting motor temperature. We reframed it as a virtual sensor replacing a thermocouple, which gave us a real engineering motivation and told us which metrics mattered.

**Step 2 — Obtain and audit the data.** 1.33 million rows, 69 sessions, 185 hours. Checked for missing values, duplicates, constant columns, session contiguity and physical plausibility. Investigated three apparent anomalies and established all three were real physics.

**Step 3 — Decide what goes in and what comes out.** Dropped three thermocouple channels as target leakage despite their 0.95-plus correlations. Kept eight drive-measurable inputs.

**Step 4 — Explore, and find the thermal lag.** Plotted excitation against response on a shared time axis. Discovered that no raw channel exceeds 0.63 correlation, and understood why.

**Step 5 — Derive features from the thermal differential equation.** Solved the lumped-parameter model, recognised that its solution is an EWMA, and built 104 features at five thermal time constants — computed strictly within sessions.

**Step 6 — Verify the transform in isolation.** Confirmed a single 600-second filter lifts one feature's correlation from 0.57 to 0.70, before fitting any model.

**Step 7 — Design the split protocol.** Rejected random splitting on the grounds that half-second-apart samples are near-duplicates. Held out whole sessions: 64 train, 3 validation, 2 test.

**Step 8 — Build the model ladder.** Five models, simplest to most flexible, identical data and evaluation.

**Step 9 — Read the result properly.** Found the linear-regression pair that proves feature engineering dominated. Found the MLP beating tree ensembles, and worked out that extrapolation explains it. Found that RMSE and worst-case error disagree on model ranking.

**Step 10 — Tune, under grouped cross-validation.** Eighteen candidates, GroupKFold on session ID so no candidate is scored on a session it saw. Refit the winner on the full training set.

**Step 11 — Run the validation studies.** Ablation to isolate the EWMA contribution. Leakage study to quantify the cost of random splitting. Feature importance to check whether the model found the physics.

**Step 12 — Analyse the remaining error.** Broke it down by temperature, by load, and by time into session; identified warm-up as the dominant remaining weakness.

**Step 13 — Check it would actually deploy.** Counted operations and registers; confirmed it fits on a motor-control microcontroller.

**Step 14 — Document honestly.** Wrote up the limitations, including the ones that make the result look less impressive.

---

# GLOSSARY

- **PMSM** — Permanent-Magnet Synchronous Motor. An efficient AC motor with magnets on the rotor.
- **Stator winding** — the stationary copper coil that carries current and generates the magnetic field. The thing that overheats.
- **Class H insulation** — an insulation rating standard, approximately 180 °C.
- **Field-oriented control** — the standard control scheme for AC motors; it is the reason the drive already measures the eight input signals.
- **dq frame** — a rotating reference frame that turns the three-phase AC quantities into two steady values, `d` and `q`, far easier to control.
- **Thermocouple** — a temperature sensor made from two dissimilar metals.
- **EWMA** — Exponentially Weighted Moving Average. A running average that weights recent values more heavily, computed recursively with one multiply and one add.
- **Lumped-parameter thermal model** — treating a complex object as a small number of uniform thermal masses connected by thermal resistances.
- **Target leakage** — accidentally giving a model information that would not be available at prediction time, producing accuracy that does not transfer.
- **RMSE** — Root Mean Squared Error. Average error, penalising large misses more heavily.
- **MAE** — Mean Absolute Error. Plain average error.
- **R²** — the fraction of variance in the target the model explains. 1.0 is perfect.
- **GroupKFold** — cross-validation that keeps all rows from one group (here, one session) together in the same fold.
- **Extrapolation** — predicting outside the range of the training data. Tree models cannot do it; neural networks can.
- **MAC** — multiply-accumulate, the basic arithmetic operation of neural network inference.
- **IIR filter** — Infinite Impulse Response filter. A recursive filter that needs no history buffer.

---

# THE ONE-PARAGRAPH SUMMARY

A motor's stator winding fails when it overheats, but the thermocouple that would measure it is impractical in a production machine. This project built a software replacement — a virtual sensor — that estimates winding temperature from eight signals a motor drive already measures for free. Three thermocouple channels that would have made the task trivial were deliberately discarded as target leakage. The feature set was derived from the lumped-parameter thermal differential equation, whose solution is an exponentially weighted integral of past losses — which is to say, an EWMA — expanding eight raw channels into 104 physics-grounded features. Evaluation held out entire measurement sessions rather than random rows, because at 2 Hz adjacent samples are near-duplicates and random splitting inflates the reported accuracy by a factor of 3.8. The selected model, a tuned two-layer neural network, achieves 1.54 °C RMSE and an R² of 0.9965 on motor sessions it has never seen, with 84.2 % of samples within two degrees. An ablation proves the accuracy comes specifically from the thermal-history features, and the trained model's most-used inputs turn out to be the coolant boundary condition and the copper-loss term — exactly the two terms the original physics names as dominant. The whole estimator costs about 60,000 operations per second and 90 registers, which is why it is a thermocouple replacement rather than an offline analysis.
