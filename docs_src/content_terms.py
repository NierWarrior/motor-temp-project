# -*- coding: utf-8 -*-
"""Glossary: every term in the project, what it is, and what work it does here."""

# (term, what it is, what work it does in THIS project)
GROUPS = [

("1", "The Machine and Its Physics",
 "The vocabulary of the motor itself. If you cannot say what these are, the feature engineering "
 "later has no justification.", [

("PMSM", "Permanent-Magnet Synchronous Motor &mdash; an AC motor whose rotor field comes from "
 "permanent magnets rather than from excitation current.",
 "The machine under study. Its efficiency and power density are why it is used in traction and "
 "industrial drives, and its thermal fragility is why this project exists."),

("Stator", "The stationary outer part of the motor, carrying the windings and the iron core.",
 "Three of the four temperature channels in the dataset are stator measurements. The stator is where "
 "copper loss is deposited."),

("Stator winding", "The copper coils in the stator slots that carry the phase currents.",
 "<b>The target.</b> Its insulation is the first thing to fail from overheating, so its temperature is "
 "the binding constraint on how hard the motor may be driven."),

("Stator tooth / stator yoke", "Parts of the stator iron core &mdash; the teeth project between the "
 "slots, the yoke is the outer ring joining them.",
 "<b>Dropped as target leakage.</b> They are separate thermocouple readings inside the same machine "
 "&mdash; the very sensors this project replaces."),

("PM (<code>pm</code>)", "The permanent-magnet (rotor) temperature channel.",
 "<b>Dropped as target leakage</b>, for the same reason. Magnet temperature also matters in practice "
 "because excessive heat demagnetises the rotor, but it is not predictable from the drive without its "
 "own sensor."),

("Class-H insulation", "An insulation thermal class rated to roughly 180&nbsp;&deg;C continuous "
 "operation.",
 "Defines the number the protection function defends. It is why maximum error, not mean error, is the "
 "deployability metric."),

("Derating", "Deliberately limiting a machine below its nameplate capability to stay within a safe "
 "margin.",
 "The cost of <i>not</i> knowing winding temperature. A drive without an estimate must derate "
 "conservatively; an accurate estimate converts that lost margin into usable torque."),

("Thermocouple", "A two-metal junction that produces a voltage proportional to temperature.",
 "The hardware this project replaces. Present on the test bench, absent on shipped motors."),

("Virtual sensor / soft sensor", "A model that outputs a quantity you do not measure, from "
 "quantities you do.",
 "<b>The framing of the whole project.</b> It is what makes dropping the three thermocouple channels "
 "the correct decision rather than a sacrifice."),

("Dynamometer", "A test rig that loads a motor with a controlled, measurable torque.",
 "How the dataset was produced: 69 controlled excitation programmes on a bench, which is why the data "
 "is clean and why sessions are independent experiments."),

("Field-oriented control (FOC)", "The standard high-performance control scheme for AC machines, "
 "working in the rotor-aligned dq frame.",
 "The reason the eight input channels are available for free &mdash; the drive already measures them "
 "to close its control loops."),

("dq frame", "A reference frame rotating with the rotor. The Park transform maps three sinusoidal "
 "phase quantities onto two slowly-varying components, direct (d) and quadrature (q).",
 "The native format of the dataset&rsquo;s electrical channels. Convenient for control, "
 "<i>inconvenient</i> for thermal modelling &mdash; which motivates computing magnitudes in "
 "Section&nbsp;5.1."),

("<code>i_d</code>, <code>i_q</code>", "Direct- and quadrature-axis current components (A).",
 "Raw inputs. Roughly, <code>i_q</code> produces torque and <code>i_d</code> controls flux. Neither is "
 "thermally meaningful alone."),

("<code>u_d</code>, <code>u_q</code>", "Direct- and quadrature-axis terminal voltage components (V).",
 "Raw inputs, used to form apparent electrical power."),

("<code>motor_speed</code>", "Rotor speed (rpm).",
 "Raw input. Drives mechanical power, and affects both iron loss and the effectiveness of cooling."),

("<code>torque</code>", "Shaft torque (N&middot;m).",
 "Raw input. With speed, gives mechanical output power, which separates useful work from heat."),

("<code>ambient</code>", "Ambient air temperature (&deg;C).",
 "Raw input. The far-field boundary condition of the heat-flow problem."),

("<code>coolant</code>", "Coolant outlet temperature (&deg;C).",
 "Raw input, and the <b>single most important one</b>: its 600&nbsp;s EWMA is the most-used feature of "
 "all 104, because it is the heat-sink boundary condition."),

("Copper loss", "Resistive heating in the windings, <code>P = 3&nbsp;I&sup2;R</code>.",
 "The dominant heat source. Because it goes as <i>I&sup2;</i>, the project computes "
 "<code>i_s&sup2;</code> explicitly rather than hoping a model discovers the square law."),

("Iron loss", "Hysteresis and eddy-current losses in the core, rising with speed and flux.",
 "A secondary heat source, captured indirectly through speed and voltage EWMAs rather than modelled "
 "explicitly."),

("Lumped-parameter thermal model", "An approximation treating the machine as a few discrete thermal "
 "masses connected by thermal resistances, rather than solving a continuous heat equation.",
 "<b>The theoretical backbone of the project.</b> It is a first-order system, and its solution is what "
 "tells us an EWMA is the right feature."),

("<code>R_th</code> (thermal resistance)", "Opposition to heat flow, &deg;C per watt.",
 "Appears in the ODE; with <code>C_th</code> it sets the thermal time constant."),

("<code>C_th</code> (thermal capacitance)", "Heat energy needed to raise a mass by 1&nbsp;&deg;C, "
 "joules per &deg;C.",
 "Appears in the ODE; the source of thermal inertia."),

("&tau; (thermal time constant)", "<code>&tau; = R_th &middot; C_th</code> &mdash; the "
 "characteristic time over which a thermal mass responds.",
 "<b>Sets the EWMA spans.</b> A motor has several (winding tens of seconds, iron minutes, housing and "
 "coolant tens of minutes), which is why five spans are used instead of one."),

("Thermal inertia", "The lag between heat generation and temperature rise, caused by thermal mass.",
 "The central observed fact: current changes in seconds, temperature in minutes. It is why an "
 "instantaneous model cannot work."),
]),

("2", "Dataset and Channels", "What the data is and how it is organised.", [

("<code>measures_v2.csv</code>", "The <i>Electric Motor Temperature</i> dataset from Paderborn "
 "University (LEA), via Kaggle: 1,330,816 rows &times; 13 columns, about 300&nbsp;MB.",
 "The sole data source. Git-ignored because of its size; fetched from Kaggle or Drive at run time."),

("<code>profile_id</code>", "An integer labelling the measurement session &mdash; one continuous "
 "recording under one excitation programme. 69 of them.",
 "<b>The most load-bearing column in the project, and not a feature.</b> It groups the EWMA "
 "computation, the train/test split, and the cross-validation folds."),

("Sampling rate (2&nbsp;Hz)", "One sample every 0.5&nbsp;s.",
 "Implies consecutive rows are near-duplicates &mdash; which invalidates random splitting and makes "
 "training-set subsampling nearly free."),

("Session (profile)", "An independent experiment, 18&ndash;366 minutes long, usually with the machine "
 "cooled between runs.",
 "The unit of held-out evaluation. Holding out whole sessions is what makes the reported numbers "
 "honest."),

("Autocorrelation", "The correlation of a signal with a time-shifted copy of itself.",
 "High here by physical necessity. It is the mechanism behind the 3.8&times; leakage inflation under a "
 "random split."),
]),

("3", "Derived Physical Features (Section 5.1)", "Six instantaneous quantities computed from the "
 "eight raw channels, each a term in the machine's heat balance.", [

("<code>i_s</code>", "Current magnitude, "
 "<code>sqrt(i_d&sup2;&nbsp;+&nbsp;i_q&sup2;)</code> (A).",
 "What actually heats the copper, independent of how the current splits between axes. Raised the "
 "single-feature correlation with the target from the raw channels&rsquo; ceiling."),

("<code>u_s</code>", "Voltage magnitude, "
 "<code>sqrt(u_d&sup2;&nbsp;+&nbsp;u_q&sup2;)</code> (V).",
 "Combines with <code>i_s</code> to give electrical power."),

("<code>S_el</code>", "Apparent electrical power, "
 "<code>1.5&nbsp;&middot;&nbsp;i_s&nbsp;&middot;&nbsp;u_s</code> (VA). The 1.5 is the "
 "three-phase dq scaling.",
 "Total power entering the machine &mdash; the top of the energy balance. Its 600&nbsp;s EWMA is the "
 "4th most-used feature."),

("<code>i_s_sq</code>", "<code>i_s&sup2;</code> (A&sup2;).",
 "<b>The copper-loss proxy.</b> Encodes <code>P = I&sup2;R</code> directly, so even a linear model can "
 "represent the dominant heat source. Its 600&nbsp;s EWMA is the 2nd most-used feature of all 104."),

("<code>P_mech</code>", "Mechanical output power, "
 "<code>&tau;&nbsp;&middot;&nbsp;n&nbsp;&middot;&nbsp;2&pi;/60</code> (W).",
 "The part of the input power that leaves as useful work rather than heat."),

("<code>P_loss</code>", "<code>S_el &minus; |P_mech|</code> (W) &mdash; an approximation of power "
 "converted to heat.",
 "The forcing term of the thermal ODE. This is the signal the physics says to integrate "
 "exponentially."),
]),

("4", "Thermal-History Features (Section 5.2)", "Where the project is won: 90 of the 104 features, "
 "and every one of the top 15 by importance.", [

("EWMA", "Exponentially Weighted Moving Average &mdash; a one-pole recursive low-pass filter, "
 "<code>y_k = &alpha;&nbsp;x_k + (1&minus;&alpha;)&nbsp;y_(k&minus;1)</code>.",
 "<b>The core idea.</b> The thermal ODE&rsquo;s solution is an exponentially weighted integral of past "
 "losses &mdash; which <i>is</i> an EWMA. So these features do not smooth the data; they supply the "
 "exact functional form the physics produces."),

("EWM-std (<code>_ewms_</code>)", "Exponentially weighted moving standard deviation at the same span.",
 "Encodes how <i>volatile</i> the recent duty cycle has been. Two motors with the same average load "
 "but different cycling have different thermal states. <code>coolant_ewms_120s</code> is the 5th "
 "most-used feature."),

("Span (<i>s</i>)", "pandas&rsquo; parameterisation of the filter, related to the decay factor by "
 "<code>&alpha; = 2/(s+1)</code>.",
 "Specified in <i>seconds</i> and converted to samples via the 2&nbsp;Hz rate, so the parameter stays "
 "physically meaningful as a thermal time constant."),

("&alpha; (decay factor)", "The weight given to the newest sample, between 0 and 1.",
 "Small &alpha; means long memory. At a 3600&nbsp;s span, &alpha;&nbsp;&asymp;&nbsp;2.8&times;10&#8315;&#8308; "
 "&mdash; which is also why fixed-point accumulators need headroom."),

("The five spans", "30&nbsp;s, 120&nbsp;s, 600&nbsp;s, 1800&nbsp;s, 3600&nbsp;s.",
 "Bracket the machine&rsquo;s physical time constants and let the model weight them. The "
 "<b>600&nbsp;s</b> family empirically dominates."),

("<code>adjust=False</code>", "pandas option selecting the true recursive form instead of a "
 "finite-sample renormalised one.",
 "Keeps the feature identical to what hardware would compute and to the ODE solution. "
 "<code>adjust=True</code> would be statistically tidier but no longer the physical filter."),

("<code>groupby(&quot;profile_id&quot;).transform(...)</code>", "pandas idiom applying a function "
 "within each group and returning a result aligned to the original index.",
 "<b>Prevents silent leakage.</b> Without it, a filter would carry thermal state across a session "
 "boundary, importing the state of an unrelated recording."),

("Feature count: 104", "8 raw + 6 physical + (9 channels &times; 2 statistics &times; 5 spans = 90).",
 "The input dimension of the final model. 90 of the 104 are thermal history, and they carry essentially "
 "all of the accuracy."),

("Warm-up transient", "The period at the start of a session during which recursive filter states are "
 "still converging from their zero initial value.",
 "The largest remaining error source. The cheapest fix is to seed each filter from the first sample "
 "instead of zero."),
]),

("5", "Machine-Learning Method", "The protocol terms &mdash; where most of the marks and most of the "
 "viva risk live.", [

("Supervised regression", "Learning a mapping from inputs to a continuous target using labelled "
 "examples.",
 "The problem class: 104 features in, one temperature in &deg;C out."),

("Target leakage", "A feature carrying information unavailable at prediction time, usually because it "
 "is downstream of or a proxy for the target.",
 "<b>The most consequential concept in the project.</b> Drove the removal of <code>stator_tooth</code>, "
 "<code>stator_yoke</code> and <code>pm</code>, each r&nbsp;&gt;&nbsp;0.95 with the target."),

("Profile-wise split", "Holding out entire sessions rather than random rows.",
 "The honest evaluation protocol. Test = profiles 65 and 72 (55,395 samples); validation = 60, 62, 74; "
 "training = the other 64 profiles (1,211,517 samples)."),

("Leakage study", "Deliberately running the invalid protocol to measure how much it would have "
 "flattered the result.",
 "Quantifies the stakes: random split gives RMSE 0.66&nbsp;&deg;C / R&sup2;&nbsp;0.9995 against the "
 "honest 2.50&nbsp;&deg;C / 0.9908 &mdash; <b>3.8&times;</b> understated."),

("Ablation study", "Removing or adding one component at a time to attribute the result.",
 "Proves the accuracy comes specifically from the EWMA terms: 14.39&nbsp;&rarr;&nbsp;14.58&nbsp;&rarr;"
 "&nbsp;<b>2.43</b>&nbsp;&deg;C RMSE across raw, +physical, +EWMA."),

("Validation set", "Data held out from training but used for stopping and selection decisions.",
 "Profiles 60, 62 and 74. Drove LightGBM&rsquo;s early stopping to 743 trees. Keeps the test set "
 "untouched until the very end."),

("<code>GroupKFold</code>", "Cross-validation that keeps all rows sharing a group label inside the "
 "same fold.",
 "<b>Mandatory here.</b> Grouped on <code>profile_id</code>, it stops the hyperparameter search from "
 "reintroducing the leakage the split protocol removes."),

("<code>RandomizedSearchCV</code>", "Hyperparameter search sampling configurations at random instead "
 "of exhausting a grid.",
 "Tuned the MLP (8 candidates) and HistGradientBoosting (10 candidates) over 3 grouped folds each, in "
 "6.9 and 11.8 minutes."),

("Early stopping", "Halting training when validation performance stops improving.",
 "Used by both LightGBM (743 of 900 trees) and the MLP. Prevents overfitting without needing to guess "
 "the right capacity."),

("<code>StandardScaler</code>", "Standardises each feature to zero mean and unit variance.",
 "Essential for the MLP, whose features span volts, amperes, rpm, watts and &deg;C. Placed "
 "<i>inside</i> the pipeline so it fits on training folds only."),

("<code>Pipeline</code>", "A scikit-learn object chaining transforms and a final estimator into one "
 "fit/predict interface.",
 "<b>Prevents a scaling leak.</b> Because the scaler is a pipeline step, cross-validation refits it per "
 "fold instead of letting test statistics into the transform."),

("<code>clone()</code>", "Produces an unfitted copy of an estimator with identical hyperparameters.",
 "Used to refit the search winner on the full training set. Necessary because naively reinstantiating a "
 "<code>Pipeline</code> from its params loses its nested steps."),

("Extrapolation", "Predicting outside the region of feature space covered by training data.",
 "<b>Why the MLP wins.</b> Test points sit roughly 5.6&times; farther from their nearest training "
 "neighbour than training points sit from each other, in standardised 104-D space."),

("Piecewise-constant", "A function that is flat within regions and jumps between them &mdash; the form "
 "of any decision-tree prediction.",
 "Explains the tree ensembles&rsquo; weakness: a tree&rsquo;s output is a leaf mean, so it can never "
 "exceed the range it was trained on. Under extrapolation it can only clamp."),

("Feature importance (split count)", "How many times a feature was chosen as a split point across all "
 "trees in a boosted ensemble.",
 "The interpretability evidence: all top 15 are EWMA features, led by <code>coolant_ewma_600s</code> "
 "(2234) and <code>i_s_sq_ewma_600s</code> (1935) &mdash; exactly the two terms the thermal ODE names."),

("<code>random_state=42</code>", "A fixed seed for every stochastic component.",
 "Makes the reported numbers reproducible. Residual variation from BLAS threading in the MLP is "
 "disclosed rather than denied."),
]),

("6", "Models in the Ladder", "Five models, ordered from the simplest thing that could work upward. "
 "The point is the comparison, not any single number.", [

("Linear regression", "Fits a linear combination of features by least squares.",
 "The baseline, and the project&rsquo;s headline finding: <b>17.79&nbsp;&deg;C / R&sup2;&nbsp;0.5324</b> "
 "on raw inputs, <b>2.08&nbsp;&deg;C / 0.9936</b> on engineered features. Same algorithm, different "
 "features."),

("Ridge regression", "Linear regression with an L2 penalty on the coefficients.",
 "Handles the 104 features&rsquo; intentional collinearity, where ordinary least squares would give "
 "unstable coefficients."),

("Random Forest", "An average over many decision trees, each fitted on a bootstrap sample.",
 "Rung three: 80 trees at depth 16, RMSE <b>3.60&nbsp;&deg;C</b>. Worst of the engineered-feature "
 "models &mdash; the clearest demonstration of the extrapolation problem."),

("MLP", "Multi-Layer Perceptron &mdash; a feed-forward neural network of fully-connected layers with "
 "nonlinear activations.",
 "<b>The selected model.</b> Two hidden layers of 128, ReLU, Adam. Smooth, so it extrapolates. Tuned: "
 "RMSE <b>1.54&nbsp;&deg;C</b>, R&sup2;&nbsp;<b>0.9965</b>, <b>84.2&nbsp;%</b> within &plusmn;2&nbsp;&deg;C."),

("LightGBM", "A fast histogram-based gradient-boosting framework using leaf-wise tree growth.",
 "Rung five: 900-tree budget early-stopped to <b>743</b>, RMSE <b>2.50&nbsp;&deg;C</b>. Also the "
 "workhorse for the ablation, leakage and feature-importance studies, because it is fast and gives "
 "importances."),

("HistGradientBoosting", "scikit-learn&rsquo;s histogram-based gradient-boosting regressor.",
 "The second tuned family. RMSE 2.39&nbsp;&deg;C &mdash; worse than the MLP &mdash; but the "
 "<b>best worst-case error at 9.53&nbsp;&deg;C</b>. If max error were the selection criterion, this "
 "would be the deployed model."),

("Gradient boosting", "Fitting an additive sequence of weak learners, each correcting the previous "
 "ensemble&rsquo;s residuals.",
 "The mechanism behind both LightGBM and HistGradientBoosting."),

("Hidden layer / ReLU / Adam", "The layer width, the activation "
 "<code>max(0,&nbsp;x)</code>, and an adaptive-learning-rate optimiser.",
 "The MLP&rsquo;s internals: <code>(128, 128)</code> chosen by the search, with "
 "<code>alpha=0.01</code> and <code>learning_rate_init=0.001</code>."),

("<code>alpha</code> (L2 penalty)", "Weight-decay strength in the MLP.",
 "The search raised it to <b>0.01</b> &mdash; more regularisation than the hand-picked default, "
 "consistent with a problem that demands extrapolation."),

("<code>num_leaves</code> / <code>max_leaf_nodes</code>", "The complexity cap on each boosted tree.",
 "96 for LightGBM; the search chose 31 for HistGradientBoosting &mdash; i.e. simpler trees generalised "
 "better across sessions."),
]),

("7", "Metrics", "Four regression metrics plus one coverage figure. The last two are the ones that "
 "decide deployability.", [

("RMSE", "<code>sqrt(mean((y &minus; &#375;)&sup2;))</code>, in &deg;C.",
 "The headline metric and the tuning objective. Penalises large misses quadratically. Final: "
 "<b>1.54&nbsp;&deg;C</b>."),

("MAE", "<code>mean(|y &minus; &#375;|)</code>, in &deg;C.",
 "Typical error with all misses weighted equally; less sensitive to the tail than RMSE. Final: "
 "<b>1.10&nbsp;&deg;C</b>."),

("R&sup2;", "<code>1 &minus; SS_res/SS_tot</code> &mdash; fraction of target variance explained. "
 "Dimensionless.",
 "Reported for comparability, but deliberately <i>not</i> led with: the target&rsquo;s 18&ndash;141&nbsp;&deg;C "
 "spread inflates it. Final: <b>0.9965</b>."),

("MaxAE", "<code>max(|y &minus; &#375;|)</code> &mdash; the single worst prediction.",
 "<b>The deployability metric.</b> A 1&nbsp;&deg;C mean error with a 20&nbsp;&deg;C spike still destroys "
 "a motor. Final: <b>11.32&nbsp;&deg;C</b>, which sets the required safety margin below 180&nbsp;&deg;C."),

("Within &plusmn;2&nbsp;&deg;C", "The percentage of test samples whose absolute error is under "
 "2&nbsp;&deg;C.",
 "Answers the engineer&rsquo;s real question &mdash; how often is this good enough to act on? A "
 "coverage fraction cannot hide a bimodal error distribution the way a single RMSE can. Final: "
 "<b>84.2&nbsp;%</b>."),

("CV RMSE", "Mean RMSE across cross-validation folds.",
 "Used to <b>rank</b> candidates, not to estimate deployed accuracy. MLP 3.04 against HGB 4.02 &mdash; "
 "the ordering held on test, which is all that was asked of it. The gap to the 1.54 test figure is "
 "expected: each fold trains on far fewer sessions."),
]),

("8", "Tooling and Artefacts", "What was used to build it, and what the repository ships.", [

("pandas", "DataFrame library for tabular data.",
 "Loads the CSV and performs the grouped EWMA construction &mdash; the single most important line of "
 "code in the project."),

("NumPy", "Numerical array library.",
 "Vectorised arithmetic for the physical derivations and all metric computation."),

("scikit-learn", "General machine-learning library (version 1.8.0 here).",
 "Supplies the pipeline, scaler, linear models, Random Forest, MLP, HistGradientBoosting, "
 "<code>GroupKFold</code> and <code>RandomizedSearchCV</code> &mdash; most of the method."),

("LightGBM", "Gradient-boosting framework (4.7.0).",
 "The ladder&rsquo;s fifth rung, and the engine for the ablation, leakage and importance studies."),

("matplotlib", "Plotting library.",
 "All 13 figures, at 300&nbsp;dpi."),

("PyArrow / Parquet", "Columnar binary storage format and its library.",
 "Caches the 104-feature matrix so the ~10-minute feature build is not repeated on every run."),

("joblib", "Serialisation library optimised for NumPy arrays.",
 "Exports <code>final_temperature_model.joblib</code> (344&nbsp;KB) carrying the fitted pipeline, the "
 "feature list <i>and its order</i>, the target name, the test metrics and the scikit-learn version."),

("Jupyter / nbformat", "Notebook environment and the library for building notebooks programmatically.",
 "The notebook is <i>generated</i> by <code>docs_src/make_notebook.py</code> rather than hand-edited, "
 "so it cannot drift from the report."),

("Google Colab", "Hosted notebook service with a free CPU runtime.",
 "<code>motor_temperature_prediction_colab.ipynb</code> runs the whole analysis in a browser with "
 "nothing installed, resolving the dataset from Kaggle, Drive or an upload."),

("<code>run.py</code>", "A single entry point with seven resumable stages.",
 "<code>eda &rarr; flow &rarr; features &rarr; train &rarr; tune &rarr; figures &rarr; extra</code>. "
 "Each stage writes a known artefact and is skipped on re-run unless <code>--force</code> is given."),

("<code>predict.py</code>", "A standalone inference script.",
 "Loads the joblib bundle and scores new data, demonstrating that the deliverable is a usable sensor "
 "and not just a notebook."),
]),
]

TOTAL = sum(len(rows) for _, _, _, rows in GROUPS)
