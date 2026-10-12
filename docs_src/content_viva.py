# -*- coding: utf-8 -*-
"""Viva question bank content. (question, answer) grouped by section."""

SECTIONS = [

("A", "Problem Understanding and Objective", [

("State the problem your project solves, in one sentence.",
 "Estimate the stator winding temperature of a permanent-magnet synchronous motor (PMSM) from "
 "signals the drive already measures &mdash; ambient and coolant temperature, dq-frame voltages and "
 "currents, rotor speed and torque &mdash; accurately enough that a controller can use the estimate "
 "as a thermal limit instead of a physical thermocouple."),

("Why can you not simply put a thermocouple on the winding?",
 "Three reasons, and cost is only one. The winding is varnished, rotating-adjacent and at high "
 "voltage, so bonding a sensor to it means extra wiring routed out through a sealed housing. That "
 "wiring is an additional failure mode in the part of the machine you least want to compromise. And "
 "the bill-of-materials cost does not survive volume production. Test benches have these sensors; "
 "shipped motors do not. That gap is exactly the gap this project fills."),

("What is a virtual sensor, or soft sensor?",
 "A software component that outputs a quantity you cannot or will not measure directly, computed "
 "from quantities you already measure. The &lsquo;sensor&rsquo; is a model, not hardware. Here the "
 "model replaces a winding thermocouple, using the eight channels a field-oriented-control drive "
 "already acquires for free."),

("Which temperature are you predicting, and why that one?",
 "<b>stator_winding</b>. It is the binding thermal constraint on the machine: the winding insulation "
 "is the first thing to fail from overheating, and insulation life halves roughly every 10&nbsp;&deg;C "
 "of sustained overtemperature. The magnet and iron temperatures matter, but the winding is what sets "
 "how hard you are allowed to push the motor."),

("What is Class-H insulation, and why does 180&nbsp;&deg;C matter?",
 "Class H is an insulation thermal class rated to about 180&nbsp;&deg;C continuous. Past that the "
 "varnish degrades and the failure mode is a turn-to-turn short. So 180&nbsp;&deg;C is the number the "
 "protection function is defending, and every design decision in this project &mdash; including which "
 "error metric I report &mdash; traces back to defending it."),

("What is the engineering benefit if the estimate is accurate?",
 "Torque and power density. A drive that does not know the winding temperature must derate "
 "conservatively &mdash; assume the worst case and give up performance the machine could physically "
 "deliver. An accurate estimate lets the controller run closer to the true thermal limit and use the "
 "motor&rsquo;s short-term overload capability. The payoff is not &lsquo;a nicer number&rsquo;; it is "
 "usable torque."),

("Why is mean error the wrong headline metric here?",
 "Because this is a safety limit, not an average-case forecast. A model with 1&nbsp;&deg;C mean error "
 "and a 20&nbsp;&deg;C worst-case spike will still cook a motor. So alongside RMSE, MAE and R&sup2; I "
 "report <b>maximum absolute error</b> and <b>the fraction of samples within &plusmn;2&nbsp;&deg;C</b> "
 "&mdash; the two numbers a protection engineer would actually ask for."),

("Who is the stated customer, and what did they ask for?",
 "Problem Statement 6, GE Power Systems: improve operational reliability of electric motors by "
 "predicting winding temperature under diverse working conditions, using a supervised regression "
 "model on ambient temperature, motor speed, load torque, supply voltage and current. The virtual-sensor "
 "framing is my interpretation of <i>why</i> they would want it, and it is what makes the leakage "
 "decision in Section&nbsp;4 obvious rather than arbitrary."),
]),

("B", "Dataset", [

("Describe your dataset.",
 "The <i>Electric Motor Temperature</i> dataset from Paderborn University&rsquo;s LEA department "
 "(<code>measures_v2.csv</code>, via Kaggle). Test-bench telemetry from a three-phase PMSM on a "
 "dynamometer: <b>1,330,816 samples</b> at <b>2&nbsp;Hz</b> across <b>69 independent sessions</b>, "
 "about <b>185 hours</b> of running, 13 columns, <b>zero missing values</b>. The target spans "
 "18.6&ndash;141.4&nbsp;&deg;C and sessions run 18&ndash;366 minutes."),

("What is <code>profile_id</code> and why does it matter so much?",
 "It labels the measurement session &mdash; one continuous recording of the bench under one excitation "
 "programme. It matters twice. First, every EWMA feature must be computed <i>within</i> a session, or "
 "the filter imports thermal state from an unrelated recording. Second, it is the grouping variable "
 "for the train/test split and for cross-validation. Essentially every correctness decision in this "
 "project is a <code>profile_id</code> decision."),

("What does the 2&nbsp;Hz sampling rate imply?",
 "Samples are 0.5&nbsp;s apart, and a motor&rsquo;s temperature cannot change appreciably in 0.5&nbsp;s. "
 "So consecutive rows are near-duplicates. That single fact is why a random train/test split is invalid "
 "here, and it is also why subsampling the training set for the slower learners costs almost nothing "
 "&mdash; the data is heavily autocorrelated."),

("Which columns are inputs, and which are not?",
 "Eight inputs, all drive-measurable: <code>ambient</code>, <code>coolant</code>, <code>u_d</code>, "
 "<code>u_q</code>, <code>i_d</code>, <code>i_q</code>, <code>motor_speed</code>, <code>torque</code>. "
 "One target: <code>stator_winding</code>. Three columns dropped as leakage: <code>stator_tooth</code>, "
 "<code>stator_yoke</code>, <code>pm</code>. Plus <code>profile_id</code>, which is metadata, not a feature."),

("What is the dq frame, and why are voltage and current given as d and q?",
 "The dq (direct&ndash;quadrature) frame is a rotating reference frame locked to the rotor. Applying "
 "the Park transform to the three phase quantities turns sinusoidally-varying AC values into two "
 "slowly-varying DC-like components, which is what makes field-oriented control tractable: roughly, "
 "<code>i_q</code> produces torque and <code>i_d</code> controls flux. The dataset ships dq because "
 "that is what the controller works in."),

("Is dq convenient for <i>thermal</i> modelling too?",
 "No, and that is the point of Section&nbsp;5.1. What heats a winding is copper loss, which depends on "
 "the <i>magnitude</i> of the current, not its decomposition. Handing a model <code>i_d</code> and "
 "<code>i_q</code> and expecting it to discover "
 "<code>i_s&nbsp;=&nbsp;sqrt(i_d&sup2;&nbsp;+&nbsp;i_q&sup2;)</code> and then square it is asking the "
 "model to rediscover physics I already know. I compute it instead."),

("Is the data clean? How do you know, rather than assume?",
 "I ran a systematic audit, not just a null check. Completeness: <b>0</b> NaN cells, <b>0</b> infinite "
 "cells, <b>0</b> duplicate rows, no constant columns. Structure: all <b>69</b> sessions are contiguous "
 "in file order, which is what makes the per-session EWMA safe. Plausibility: 0 rows above "
 "200&nbsp;&deg;C, 0 above 6500&nbsp;rpm, 0 above 400&nbsp;A, 0 with ambient outside 0&ndash;50&nbsp;&deg;C. "
 "One check did fire, and I chased it down &mdash; see the next question."),

("Your audit flagged 69,386 rows (5.2&nbsp;%) with winding temperature below ambient. Is that a sensor fault?",
 "No &mdash; it is a liquid-cooled machine, and that is the correct physical behaviour. In 99.9&nbsp;% of "
 "those rows the <i>coolant</i> is also below ambient (median coolant 18.5&nbsp;&deg;C against median "
 "ambient 23.0&nbsp;&deg;C), and median current in those rows is 2.3&nbsp;A against 110.6&nbsp;A overall. "
 "So: a near-idle motor with chilled coolant running through it sits below room temperature. The flag was "
 "right to fire and the data is right to contain it. I kept the rows."),
]),

("C", "Exploratory Data Analysis", [

("What was the single most important thing EDA told you?",
 "That the problem is not instantaneous. Plotting excitation and thermal response on one time axis for "
 "the longest session shows current changing in <i>seconds</i> while winding temperature moves over "
 "<i>minutes</i>. The target at time <i>t</i> is not a function of the inputs at time <i>t</i> &mdash; it "
 "is a function of their recent history. Every design decision downstream follows from that one plot."),

("What is thermal inertia, in your own words?",
 "The motor has thermal mass. Electrical loss deposits energy into copper and iron, and that energy takes "
 "time to raise the temperature and time to escape to the coolant. The result is a low-pass relationship "
 "between loss and temperature, with time constants from tens of seconds (winding) through minutes (iron) "
 "to tens of minutes (housing and coolant)."),

("What was the strongest raw correlation with the target, and what did you conclude?",
 "No raw electrical channel exceeded <b>|r| = 0.63</b>. The naive reading is &lsquo;weak signal, hard "
 "problem&rsquo;. The correct reading is that the <i>instantaneous</i> relationship is weak because the "
 "physical relationship is not instantaneous. The ceiling is a property of the representation, not of the "
 "information content &mdash; and one transform lifted <code>i_s</code> from r&nbsp;&asymp;&nbsp;0.57 to "
 "r&nbsp;&asymp;&nbsp;0.70."),

("Why did you not use correlation to select features?",
 "Because correlation measures a linear, same-instant association, and the whole structure of this problem "
 "lives in the time domain. A correlation filter would have discarded exactly the channels that become "
 "predictive once you average them, and kept nothing useful. Feature <i>construction</i> was the task here, "
 "not feature selection."),
]),

("D", "Pre-processing and Target Leakage", [

("What is target leakage?",
 "When a feature carries information that would not be available at prediction time, usually because it is "
 "downstream of the target or is a proxy for it. The model scores brilliantly in validation and is useless "
 "in deployment, because the feature it leaned on does not exist in the real setting."),

("Which columns did you drop, and why?",
 "<code>stator_tooth</code>, <code>stator_yoke</code> and <code>pm</code>. Each correlates with the target "
 "above <b>r = 0.95</b>, but the reason for dropping them is not the correlation &mdash; it is that they are "
 "readings from <i>other thermocouples inside the same machine</i>. They are the very hardware the virtual "
 "sensor exists to replace. A model that uses them is not a virtual sensor; it is an interpolator between "
 "sensors you already said you cannot afford."),

("How did you know those three were leaking, rather than just useful?",
 "By asking the deployment question, not the statistical one: <i>would this signal exist on a shipped "
 "motor?</i> It would not, because installing those thermocouples is precisely the cost the project is "
 "avoiding. The r&nbsp;&gt;&nbsp;0.95 correlation is corroboration, not the argument. This is the single "
 "most consequential decision in the project &mdash; keeping them would have produced a far better number "
 "describing nothing."),

("Is dropping features correlated with the target not throwing away information?",
 "Yes, deliberately. The question is never &lsquo;does this feature help the score&rsquo; but "
 "&lsquo;will this feature be present when the model runs&rsquo;. Here the answer is no, so the "
 "information is not mine to use. Honest framing of the problem comes before accuracy."),

("Did you need to handle missing values, outliers or scaling?",
 "Missing values: none exist, so nothing to impute. Outliers: the audit found none that were physically "
 "implausible, and the one flag that fired was explained rather than removed &mdash; deleting real "
 "low-load data would have biased the model. Scaling: yes, but as a <i>pipeline step</i> rather than a "
 "pre-processing pass, so the scaler fits on training data only. See question 45."),

("Did you need to encode any categorical variables?",
 "No. Every input is continuous and physical. <code>profile_id</code> is categorical but is deliberately "
 "<i>not</i> a feature &mdash; it is grouping metadata. Encoding it would let the model memorise session "
 "identity, which is the opposite of what the split protocol is trying to test."),
]),

("E", "Feature Engineering", [

("How many features do you have, and where do they come from?",
 "8 raw channels become <b>104 features</b>: the 8 raw inputs, plus <b>6</b> physically-derived "
 "instantaneous quantities, plus <b>90</b> thermal-history features &mdash; 9 channels &times; 2 statistics "
 "(exponentially weighted mean and standard deviation) &times; 5 time spans. 8&nbsp;+&nbsp;6&nbsp;+&nbsp;90 "
 "=&nbsp;104."),

("What are the six derived physical quantities, and why those?",
 "<code>i_s = sqrt(i_d&sup2; + i_q&sup2;)</code> (current magnitude), "
 "<code>u_s = sqrt(u_d&sup2; + u_q&sup2;)</code> (voltage magnitude), "
 "<code>S_el = 1.5&nbsp;&middot;&nbsp;i_s&nbsp;&middot;&nbsp;u_s</code> (apparent electrical power), "
 "<code>i_s&sup2;</code> (the copper-loss proxy), "
 "<code>P_mech = &tau;&nbsp;&middot;&nbsp;n&nbsp;&middot;&nbsp;2&pi;/60</code> (mechanical power), and "
 "<code>P_loss &asymp; S_el &minus; |P_mech|</code> (power that became heat). Each one is a term that "
 "appears in the heat balance of the machine."),

("Why <code>i_s&sup2;</code> specifically?",
 "Copper loss is <code>P = 3&nbsp;I&sup2;R</code> &mdash; the heating is proportional to the <i>square</i> "
 "of the current. Giving the model <code>i_s&sup2;</code> hands it the correct functional form directly. "
 "A tree can approximate a square law with enough splits and a linear model cannot approximate it at all, "
 "so this is a free accuracy gain for anything linear and a free efficiency gain for anything else."),

("Derive the EWMA from the physics. This is the core of your project.",
 "A lumped-parameter thermal model of the motor is a first-order system: "
 "<code>C_th&nbsp;&middot;&nbsp;d&thetasym;/dt = P_loss(t) &minus; (&thetasym; &minus; &thetasym;_amb)/R_th</code>. "
 "Solving it gives "
 "<code>&thetasym;(t) = (1/&tau;)&nbsp;&int;&nbsp;exp(&minus;(t&minus;s)/&tau;)&nbsp;P_loss(s)&nbsp;ds</code> "
 "with <code>&tau; = R_th&nbsp;&middot;&nbsp;C_th</code>. That integral &mdash; an exponentially weighted "
 "average of past losses &mdash; <b>is</b> an EWMA. So computing EWMAs of the loss-related signals does not "
 "merely smooth the data: it supplies the exact functional form the physics produces. That is why even a "
 "linear model works once the features exist."),

("What is an EWMA, mathematically?",
 "A one-pole recursive low-pass filter: <code>y_k = &alpha;&nbsp;x_k + (1&minus;&alpha)&nbsp;y_(k&minus;1)</code>. "
 "Each output is a weighted average of all past inputs with weights decaying geometrically into the past. "
 "It needs one multiply&ndash;add and one stored value per sample, which is why it is as attractive for "
 "hardware as it is for the physics."),

("What is &lsquo;span&rsquo;, and how does it relate to &alpha;?",
 "pandas parameterises the filter by span <i>s</i>, with <code>&alpha; = 2/(s+1)</code>. I specify spans in "
 "<i>seconds</i> and convert to samples by multiplying by the 2&nbsp;Hz sampling rate, so a 600&nbsp;s span "
 "is 1200 samples. Working in seconds keeps the parameter physically meaningful &mdash; it is a thermal time "
 "constant, not a window length."),

("Why five spans, and why 30, 120, 600, 1800 and 3600&nbsp;s?",
 "Because the machine is not one thermal mass but several, with different time constants: winding tens of "
 "seconds, iron minutes, housing and coolant tens of minutes. A single span would have to compromise. Five "
 "spans spanning 30&nbsp;s to one hour bracket the physical range, and the model is left to weight them. "
 "The empirical answer agrees: the most-used features are the <b>600&nbsp;s</b> ones, which sits right in "
 "the middle of that range."),

("Why also compute the exponentially weighted <i>standard deviation</i>?",
 "The mean tells you how much loss has recently been deposited; the standard deviation tells you how "
 "<i>volatile</i> the recent duty cycle has been. A motor held at a steady 100&nbsp;A and one cycling "
 "violently around a 100&nbsp;A mean have the same EWMA and different thermal states. The ewms terms earn "
 "their place &mdash; <code>coolant_ewms_120s</code> is the 5th most-used feature of all 104."),

("Why compute every EWMA within a <code>profile_id</code> group?",
 "Sessions are separate experiments, often with the machine cooled down in between. Letting a recursive "
 "filter run across a session boundary would carry the thermal state of an unrelated recording into the "
 "first minutes of the next one. That is leakage, and it is silent &mdash; it would quietly improve the "
 "score while corrupting the physics. I use <code>groupby(&quot;profile_id&quot;).transform(...)</code> so "
 "each session&rsquo;s filter starts fresh."),

("Why <code>adjust=False</code>?",
 "<code>adjust=False</code> gives the true recursive form "
 "<code>y_k = &alpha;x_k + (1&minus;&alpha;)y_(k&minus;1)</code>, which is exactly what a hardware "
 "implementation would compute and exactly what the thermal ODE solution looks like. "
 "<code>adjust=True</code> applies a finite-sample renormalisation that is statistically tidier but no "
 "longer the physical filter, and could not be reproduced on a controller with one register per channel."),

("Did the instantaneous physical features actually help? Be honest.",
 "Measured, with an ablation on identical LightGBM models. Raw inputs only: RMSE <b>14.39&nbsp;&deg;C</b>, "
 "R&sup2;&nbsp;0.6942. Adding the six instantaneous derivations: <b>14.58&nbsp;&deg;C</b>, R&sup2;&nbsp;0.6860 "
 "&mdash; very slightly <i>worse</i>, inside noise. Adding the EWMAs: <b>2.43&nbsp;&deg;C</b>, "
 "R&sup2;&nbsp;0.9913. So the instantaneous derivations buy essentially nothing on their own; the entire "
 "gain is thermal history. I keep them because they are the <i>channels</i> the useful EWMAs are computed "
 "<i>of</i>, and because they help the linear models."),

("Which features does the model actually rely on?",
 "All of the top 15 by LightGBM split count are EWMA-derived. The top three are "
 "<code>coolant_ewma_600s</code> (2234 splits), <code>i_s_sq_ewma_600s</code> (1935) and "
 "<code>i_s_ewma_600s</code> (1841). Read that physically: the 600&nbsp;s average of coolant temperature is "
 "the <b>heat-sink boundary condition</b>, and the 600&nbsp;s average of <code>i_s&sup2;</code> is the "
 "<b>copper-loss term</b>. Those are precisely the two terms the lumped thermal ODE names as dominant. The "
 "model learned the physics the features were designed around, which is the strongest evidence available "
 "that the result is not an artefact."),
]),

("F", "Train / Test Split Protocol", [

("How did you split the data, and why that way?",
 "Profile-wise: entire measurement sessions are held out. Test is profiles <b>65 and 72</b> "
 "(<b>55,395</b> samples), validation is profiles 60, 62 and 74 (<b>63,904</b> samples), training is the "
 "remaining <b>64</b> profiles (<b>1,211,517</b> samples). The model is evaluated the way it would be used: "
 "on a motor run it has never seen."),

("What exactly goes wrong with <code>train_test_split(X, y, test_size=0.2)</code> here?",
 "Rows are 0.5&nbsp;s apart and near-identical. A random split scatters near-duplicate rows across both "
 "sides, so the test set is effectively already inside the training set. The model is rewarded for "
 "memorising rather than generalising, and the reported score describes nothing you could deploy."),

("Quantify it. How wrong is a random split?",
 "Same model, same features, only the split changes. Random 80/20 over rows: RMSE <b>0.66&nbsp;&deg;C</b>, "
 "R&sup2;&nbsp;<b>0.9995</b>. Profile-wise: RMSE <b>2.50&nbsp;&deg;C</b>, R&sup2;&nbsp;<b>0.9908</b>. Random "
 "splitting understates error by <b>3.8&times;</b>. I ran this deliberately, as a study, because the "
 "0.9995 is the number most projects on this dataset report."),

("How did you choose profiles 65 and 72 specifically?",
 "They are the benchmark test sessions used in the published literature on this bench, so my numbers are "
 "comparable to other people&rsquo;s. Choosing them in advance also removes any suspicion that the test "
 "set was selected to flatter the result."),

("What did the validation set do, if the test set is what you report?",
 "Early stopping and model selection. LightGBM&rsquo;s early stopping watched profiles 60, 62 and 74 and "
 "settled at <b>743</b> trees out of a 900 budget; the MLP used scikit-learn&rsquo;s internal early "
 "stopping. The test profiles were touched exactly once, at the end. Using the test set to choose a "
 "stopping point is a subtler form of the same leakage the split protocol exists to prevent."),

("You subsampled the training set for some models. Does that not throw away data?",
 "For the Random Forest and MLP I trained on every 10th row &mdash; <b>121,152</b> samples. At 2&nbsp;Hz, "
 "consecutive rows are near-duplicates, so the information lost is small while the training time saved is "
 "large. Crucially, subsampling is applied <i>within</i> the training set only; the test profiles are "
 "evaluated at full rate, and the EWMA features were computed at full rate before any subsampling, so no "
 "thermal history is lost."),
]),

("G", "Model Development", [

("Which models did you try, and why that ladder?",
 "Five, deliberately ordered from the simplest thing that could work upward: linear regression on raw "
 "inputs, Ridge on the full feature set, Random Forest (80 trees, depth 16), an MLP (two hidden layers of "
 "128), and LightGBM (900-tree budget, early-stopped to 743). The point of a ladder is the <i>comparison</i> "
 "&mdash; it isolates how much each addition is worth. The first two rungs alone carry the project&rsquo;s "
 "main finding."),

("What is the main finding from the ladder?",
 "Linear regression on raw inputs: RMSE <b>17.79&nbsp;&deg;C</b>, R&sup2;&nbsp;<b>0.5324</b>. The same "
 "algorithm on the engineered features: RMSE <b>2.08&nbsp;&deg;C</b>, R&sup2;&nbsp;<b>0.9936</b>. No change "
 "of model &mdash; only features. <b>Feature engineering beat model sophistication</b>, and by a margin no "
 "amount of tuning could have recovered. That is the sentence I would want remembered."),

("Why Ridge rather than plain least squares on 104 features?",
 "The 104 features are heavily collinear by construction &mdash; a 30&nbsp;s and a 120&nbsp;s EWMA of the "
 "same channel are nearly the same signal. Ordinary least squares on collinear inputs gives unstable, "
 "wildly-scaled coefficients. The L2 penalty keeps the solution well-conditioned without discarding any "
 "feature, which suits a feature set whose redundancy is intentional."),

("Your final model is an MLP. Why did it beat both tree ensembles?",
 "Extrapolation. Tree ensembles are <b>piecewise-constant</b>: a prediction is the mean of the training "
 "samples in a leaf, so a tree can never output a value outside the range it was trained on. The held-out "
 "sessions contain operating points the 64 training profiles never visit, and at those points a tree can "
 "only clamp to its nearest leaf. An MLP is a smooth function and continues the trend. Under genuine "
 "extrapolation, smoothness is the decisive property &mdash; which is why the usual "
 "&lsquo;trees-win-on-tabular-data&rsquo; expectation fails here."),

("Can you prove the test set actually requires extrapolation, rather than asserting it?",
 "Yes. Marginally, every feature&rsquo;s range overlaps between train and test, so a per-feature check "
 "says nothing. The question is joint. Measuring nearest-neighbour distances in the standardised "
 "104-dimensional feature space, the median distance from a test point to its nearest training point is "
 "about <b>5.6&times;</b> the median distance between training points themselves, and roughly <b>9&nbsp;%</b> "
 "of test points lie beyond the 99th percentile of intra-training distances. The exact ratio depends on how "
 "densely you sample the training reference set, but the direction is robust: the held-out sessions sit in a "
 "part of joint feature space the training data does not populate."),

("Describe your final model precisely.",
 "A scikit-learn <code>Pipeline</code> of <code>StandardScaler</code> followed by "
 "<code>MLPRegressor(hidden_layer_sizes=(128, 128), alpha=0.01, learning_rate_init=0.001, "
 "early_stopping=True, n_iter_no_change=6, max_iter=80, random_state=42)</code>. ReLU activations, Adam "
 "optimiser, 104 inputs, one output. Serialised with the feature list, the target name, the test metrics "
 "and the scikit-learn version into a <b>344&nbsp;KB</b> joblib bundle."),

("Why <code>StandardScaler</code>, and why inside a <code>Pipeline</code> rather than before the split?",
 "The MLP needs it: features span volts, amperes, rpm, watts and degrees Celsius, and gradient descent on "
 "unscaled inputs of wildly different magnitudes converges badly. Putting it <i>inside</i> the pipeline "
 "means the scaler&rsquo;s mean and variance are fitted on training folds only. Scaling the whole dataset "
 "first would let test-set statistics influence the transform &mdash; a textbook, easily-missed leak, and "
 "one that cross-validation would not catch because every fold would already be contaminated."),

("Why did you not use an LSTM or a temporal CNN, given this is time-series data?",
 "Two reasons, one principled and one practical. Principled: the physics tells me the exact functional form "
 "&mdash; an exponentially weighted integral of past losses &mdash; so I can <i>construct</i> that "
 "representation rather than asking a network to learn it from data. That is cheaper, interpretable, and it "
 "worked. Practical: the resulting model is 90 registers and ~30k multiply-accumulates, which runs on a "
 "motor-control MCU; a sequence model does not. I list sequence models in Section&nbsp;12 as the natural "
 "next step, specifically to learn the time constants instead of fixing five spans."),

("Why <code>random_state=42</code> everywhere?",
 "Reproducibility. The MLP&rsquo;s weight initialisation, the Random Forest&rsquo;s bootstrap, LightGBM&rsquo;s "
 "subsampling and the randomised search&rsquo;s candidate draws are all stochastic. Fixing the seed means the "
 "reported numbers can be regenerated exactly. Small differences across machines are still possible from "
 "BLAS threading in the MLP, and I say so rather than claiming bit-exactness."),
]),

("H", "Performance Evaluation and Interpretation", [

("Define your four regression metrics.",
 "<b>RMSE</b> = sqrt(mean((y &minus; &#375;)&sup2;)) &mdash; typical error in &deg;C, penalising large misses "
 "quadratically. <b>MAE</b> = mean(|y &minus; &#375;|) &mdash; typical error, all misses weighted equally. "
 "<b>R&sup2;</b> = 1 &minus; SS_res/SS_tot &mdash; the fraction of variance explained, dimensionless. "
 "<b>MaxAE</b> = max(|y &minus; &#375;|) &mdash; the single worst prediction in the test set."),

("Why report &lsquo;within &plusmn;2&nbsp;&deg;C&rsquo; at all?",
 "Because it is the question an engineer actually asks: <i>how often is this estimate good enough to act "
 "on?</i> RMSE is a single summary statistic that can hide a bimodal error distribution; a coverage "
 "fraction cannot. For the final model, <b>84.2&nbsp;%</b> of samples fall within &plusmn;2&nbsp;&deg;C."),

("State your final results.",
 "Tuned MLP, on profiles 65 and 72 &mdash; 55,395 samples, 7.7 hours, never seen in training: "
 "RMSE <b>1.54&nbsp;&deg;C</b>, MAE <b>1.10&nbsp;&deg;C</b>, R&sup2;&nbsp;<b>0.9965</b>, "
 "max absolute error <b>11.32&nbsp;&deg;C</b>, <b>84.2&nbsp;%</b> within &plusmn;2&nbsp;&deg;C."),

("Walk through the model-comparison table.",
 "Linear raw 17.79&nbsp;&deg;C / R&sup2;&nbsp;0.5324. Ridge + EWMA 2.08 / 0.9936. Random Forest 3.60 / "
 "0.9808. MLP untuned 1.67 / 0.9959. LightGBM 2.50 / 0.9908. Tuned MLP <b>1.54 / 0.9965</b>. Tuned "
 "HistGradientBoosting 2.39 / 0.9915. Three readings: features matter more than the model; the neural net "
 "beats the ensembles because of extrapolation; and <b>RMSE and max error do not rank the models "
 "identically</b> &mdash; tuned HGB has the best worst case at <b>9.53&nbsp;&deg;C</b> despite worse RMSE."),

("So which model would you actually deploy?",
 "It depends on the selection criterion, and I would say so explicitly rather than pretend there is one "
 "answer. I selected on RMSE, which gives the MLP. If worst-case error were the criterion &mdash; and for a "
 "protection function it arguably should be &mdash; tuned HistGradientBoosting at <b>9.53&nbsp;&deg;C</b> "
 "MaxAE is the better choice, at the cost of RMSE rising from 1.54 to 2.39. Selecting on RMSE and then "
 "disclosing max error is the honest order of operations."),

("Where does the remaining error actually live? Average error hides structure.",
 "I broke it down three ways. By operating temperature: median error stays near 1&nbsp;&deg;C in every band "
 "from 18&nbsp;&deg;C to 145&nbsp;&deg;C &mdash; accuracy does not decay when the motor is hot, which is the "
 "property that matters since a thermal limit is only consulted in the hot regime. By load: likewise flat, "
 "with a moderately wider tail under heavy load. By time into the session: <b>this is where the structure "
 "is</b> &mdash; the largest errors are concentrated in the first minutes, while the 1800&nbsp;s and "
 "3600&nbsp;s filters are still converging from their zero initial state."),

("Is the model biased?",
 "The residual distribution is approximately zero-mean and symmetric, and residuals plotted against "
 "measured temperature show no systematic trend &mdash; so no consistent over- or under-prediction across "
 "the operating range. The error is dispersion, not bias. For a thermal limit that is the preferable "
 "failure mode, but it is also why the max-error number still has to be reported separately."),

("R&sup2; = 0.9965 sounds too good. Why should I believe it?",
 "You should be suspicious, and I built two studies specifically to answer that. First, the leakage study: "
 "I show what the inflated number looks like (R&sup2;&nbsp;0.9995 under a random split) and report the "
 "honest one instead. Second, the ablation: the accuracy is traceable to a specific, physically-justified "
 "feature family rather than appearing from nowhere. And the headline R&sup2; is computed on two entire "
 "sessions that no training sample came from. The high R&sup2; is partly just the target&rsquo;s wide "
 "variance &mdash; 18 to 141&nbsp;&deg;C &mdash; which is why I lead with RMSE in &deg;C, not R&sup2;."),

("What does the predicted-versus-measured plot show?",
 "The two held-out sessions overlaid as time series, prediction against measurement. The estimate tracks "
 "every ramp, plateau and cool-down, with visible divergence only in the opening minutes of profile 72 "
 "&mdash; the warm-up effect. It is the most informative figure in the project because it shows error "
 "<i>in time</i>, which a scatter plot or a single metric cannot."),
]),

("I", "Hyperparameter Tuning and Cross-Validation", [

("How did you tune, and what did you tune?",
 "<code>RandomizedSearchCV</code> over the two strongest families. For the MLP: hidden layer sizes, L2 "
 "penalty <code>alpha</code>, and initial learning rate &mdash; 8 candidates. For "
 "HistGradientBoosting: <code>max_iter</code>, learning rate, <code>max_leaf_nodes</code>, "
 "<code>min_samples_leaf</code> and L2 regularisation &mdash; 10 candidates. Three grouped folds each, "
 "scored on negative RMSE, on a 1-in-10 subsample of the non-test data."),

("Why randomised search rather than an exhaustive grid?",
 "The MLP grid alone is 4&times;4&times;3 = 48 combinations and each fit takes minutes; the full grid "
 "across both families is hundreds of fits. Randomised search samples the space, and with most "
 "hyperparameters mattering far less than a few, random sampling finds a near-optimal configuration for a "
 "fraction of the compute. The MLP search took <b>6.9</b> minutes and the HGB search <b>11.8</b>."),

("Why <code>GroupKFold</code> and not plain <code>KFold</code>?",
 "Because a plain <code>KFold</code> would split <i>within</i> sessions and silently reintroduce exactly "
 "the leakage the whole split protocol exists to prevent &mdash; near-duplicate rows on both sides of each "
 "fold boundary. Every candidate would be scored on a contaminated fold, so the search would rank them by "
 "how well they memorise. <code>GroupKFold</code> grouped on <code>profile_id</code> keeps whole sessions "
 "together. This is not optional here."),

("Your CV RMSE is about 3&nbsp;&deg;C but your test RMSE is 1.54&nbsp;&deg;C. That looks wrong. Explain.",
 "It is expected, and it is a point worth making. Each grouped fold trains on only about two-thirds of the "
 "available sessions, so every candidate sees far less thermal diversity than the final model does when it "
 "is refitted on all 64 training profiles. Grouped CV here is for <b>ranking candidates</b>, not for "
 "estimating deployed accuracy. The MLP scored CV RMSE <b>3.04</b> against HGB&rsquo;s <b>4.02</b>, and that "
 "ordering held on the test set &mdash; which is all I asked of it."),

("What were the winning hyperparameters?",
 "MLP: <code>hidden_layer_sizes=(128, 128)</code>, <code>alpha=0.01</code>, "
 "<code>learning_rate_init=0.001</code>. Notably the search chose the <i>same</i> architecture as my initial "
 "hand-picked guess and changed only the regularisation and learning rate &mdash; so most of the gain came "
 "from <code>alpha</code> rising to 0.01, i.e. more regularisation, which is consistent with the "
 "extrapolation story."),

("Did tuning help?",
 "Partly, and I report both halves. RMSE improved <b>8&nbsp;%</b> (1.67&nbsp;&rarr;&nbsp;1.54&nbsp;&deg;C) "
 "and MAE <b>13&nbsp;%</b> (1.26&nbsp;&rarr;&nbsp;1.10&nbsp;&deg;C). But maximum absolute error got "
 "<i>worse</i>, 9.84&nbsp;&rarr;&nbsp;<b>11.32&nbsp;&deg;C</b>, because the search objective was RMSE and "
 "nothing in it constrained the tail. That is a real cost for a safety-limit application, and hiding it "
 "would have been the easy thing to do."),

("Why <code>clone(rs.best_estimator_)</code> before the final refit?",
 "Because <code>best_estimator_.__class__(**get_params())</code> does not reconstruct a "
 "<code>Pipeline</code> correctly &mdash; a pipeline&rsquo;s parameters include its nested steps, and "
 "naively reinstantiating it loses them. <code>clone</code> produces an unfitted copy with identical "
 "hyperparameters, which is exactly what you want before refitting on the full training set."),
]),

("J", "Deployment, Limitations and Extensions", [

("Could this actually run on a real motor controller?",
 "Yes, and that is what makes it a thermocouple replacement rather than an offline analysis. The MLP is "
 "two layers of 128 over ~104 inputs &mdash; roughly <b>30,000 multiply-accumulates</b> per inference, at "
 "the 2&nbsp;Hz rate the thermal model needs. That is negligible for any modern motor-control MCU and "
 "trivial on an FPGA."),

("What does the feature extraction cost in hardware?",
 "Almost nothing, which is the elegant part. Each EWMA is "
 "<code>y_k = &alpha;x_k + (1&minus;&alpha;)y_(k&minus;1)</code> &mdash; one multiply-add and one register. "
 "All <b>90</b> EWMA features cost 90 registers and 90 MACs per sample. A hardware-friendly feature "
 "extractor is unusual, and it is a large part of why this formulation is attractive for deployment rather "
 "than just for a report."),

("What numeric precision would you need?",
 "Temperatures span 18&ndash;141&nbsp;&deg;C and need about 0.1&nbsp;&deg;C resolution, so 16-bit fixed "
 "point suffices at the output. The EWMA accumulators need more headroom because of the long time constants "
 "&mdash; a 3600&nbsp;s span means <code>&alpha; &asymp; 2.8&times;10&#8315;&#8308;</code>, so small "
 "increments accumulate over thousands of samples. Q16.16 accumulators are a safe starting point."),

("What is the warm-up problem, and how would you fix it?",
 "The EWMA states initialise at zero, so for the first minutes of a session the 1800&nbsp;s and "
 "3600&nbsp;s features are only partly converged and the predictions built on them are correspondingly "
 "worse. It is the largest single remaining error source and it is intrinsic to a recursive feature set. "
 "The cheapest fix is to seed each filter from the first sample instead of zero, which costs nothing and "
 "removes most of the transient; that is first on my improvement list."),

("What are the real limitations of this work?",
 "Eight, and I would rather state them than be asked. Worst-case error is ~11&nbsp;&deg;C, so a deployed "
 "limit still needs a safety margin. One machine, one test bench &mdash; nothing proves transfer to other "
 "motor geometries. Warm-up, as above. Tuning improved the average but not the tail. Five training "
 "sessions (profiles 47, 46, 52, 64, 51) are shorter than the 3600&nbsp;s span, so ~1.5&nbsp;% of training "
 "rows carry a partly-formed feature &mdash; none are in validation or test, so the results stand, but "
 "strictly not every feature means the same thing in every row. The CV-to-test gap is large. Session "
 "identity is required at inference. And there is no uncertainty estimate."),

("Why does &lsquo;session identity is required at inference&rsquo; matter?",
 "Because the model is not a pure function of an instantaneous sample &mdash; it needs correctly segmented, "
 "chronologically ordered history, since the features are averages over that history. In deployment that "
 "means the drive has to know when a run begins so it can reset the filters, and it cannot feed samples out "
 "of order. That is a real integration requirement, not a detail."),

("A protection function wants a bound, not a point estimate. What would you do?",
 "Quantile regression or conformal prediction, to produce a defensible upper bound rather than a mean "
 "estimate. None of my five models provides one, and for a safety limit that is arguably a more valuable "
 "improvement than shaving RMSE. It is on the improvement list for exactly that reason."),

("What would you do next, in priority order?",
 "Seed the EWMA states from the first sample &mdash; cheapest fix for the largest remaining error. A "
 "physics-informed loss enforcing the thermal ODE, which would constrain trajectories to physically "
 "realisable ones and should attack the worst case specifically. Quantile or conformal prediction for an "
 "upper bound. A sequence model to learn the time constants instead of fixing five spans. Multi-output "
 "prediction of all four temperatures, to exploit the shared thermal structure between winding, tooth, yoke "
 "and magnet."),

("If I only remember one thing from your project, what should it be?",
 "That the result came from understanding the physics, not from trying models. The same linear regression "
 "goes from R&sup2;&nbsp;0.53 to 0.99 with no change of algorithm, because the features now encode the "
 "exponentially weighted integral that the thermal ODE actually produces. And the second thing: the "
 "evaluation protocol changes the headline by 3.8&times;, so a number without its protocol is not a result."),

("What was the hardest decision you made?",
 "Dropping <code>stator_tooth</code>, <code>stator_yoke</code> and <code>pm</code>. They correlate above "
 "0.95 with the target and keeping them would have produced a far prettier number. Dropping them is what "
 "makes the project a virtual sensor instead of a curve fit, and it cost most of the accuracy I then had to "
 "earn back through feature engineering."),
]),
]

TOTAL = sum(len(qs) for _, _, qs in SECTIONS)
