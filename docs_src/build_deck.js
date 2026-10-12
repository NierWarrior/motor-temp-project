const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.layout = "LAYOUT_WIDE";              // 13.3 x 7.5 in
const W = 13.3, H = 7.5;
const path = require("path");
const fs = require("fs");
const ROOT = path.resolve(__dirname, "..");
const FIG = path.join(ROOT, "figures") + path.sep;
const OUT = path.join(ROOT, "reports", "UCS321_Presentation.pptx");

// ---- palette: iron / heat / coolant -------------------------------------
const IRON   = "1C2127";   // dark ground — the machine
const IRON2  = "2A313A";
const HEAT   = "E8833A";   // accent — temperature, the thing we predict
const COOL   = "2E9E8F";   // secondary — measurement, coolant, "good"
const PAPER  = "FFFFFF";
const TINT   = "F1F3F5";
const INK    = "1C2127";
const MUTED  = "6B7280";
const LIGHT  = "C9CFD6";

const HFONT = "Cambria", BFONT = "Calibri";
const M = 0.72;                        // side margin

// ---------------- slide builders ----------------
function darkSlide() { const s = p.addSlide(); s.background = { color: IRON }; return s; }
function lightSlide() { const s = p.addSlide(); s.background = { color: PAPER }; return s; }

// motif: a numbered circle badge, repeated on every content slide
function badge(s, n, color = HEAT) {
  s.addShape(p.ShapeType.ellipse, { x: M, y: 0.44, w: 0.52, h: 0.52, fill: { color } });
  s.addText(String(n), { x: M, y: 0.44, w: 0.52, h: 0.52, isTextBox: true, margin: 0,
    align: "center", valign: "middle", fontSize: 18, bold: true, color: PAPER, fontFace: BFONT });
}

function title(s, text, opts = {}) {
  s.addText(text, { x: opts.x ?? (M + 0.74), y: opts.y ?? 0.40, w: opts.w ?? (W - 2 * M - 0.74),
    h: 0.62, isTextBox: true, margin: 0, valign: "middle",
    fontSize: opts.size ?? 30, bold: true, color: opts.color ?? INK, fontFace: HFONT });
}
function sub(s, text, opts = {}) {
  s.addText(text, { x: opts.x ?? (M + 0.74), y: opts.y ?? 1.04, w: opts.w ?? (W - 2 * M - 0.74),
    h: 0.38, isTextBox: true, margin: 0, valign: "top",
    fontSize: opts.size ?? 14, color: opts.color ?? MUTED, fontFace: BFONT, italic: true });
}
function img(s, file, o) { s.addImage({ path: FIG + file, ...o }); }

function card(s, x, y, w, h, fill = TINT) {
  s.addShape(p.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.08, fill: { color: fill } });
}
function stat(s, x, y, w, value, label, color = HEAT, vsize = 44) {
  s.addText(value, { x, y, w, h: 0.72, isTextBox: true, margin: 0, align: "center",
    fontSize: vsize, bold: true, color, fontFace: BFONT });
  s.addText(label, { x, y: y + 0.74, w, h: 0.52, isTextBox: true, margin: 0, align: "center",
    fontSize: 11.5, color: MUTED, fontFace: BFONT });
}
function bullets(s, items, o) {
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
    { x: o.x, y: o.y, w: o.w, h: o.h, isTextBox: true, margin: 0,
      fontSize: o.size ?? 14, color: o.color ?? INK, fontFace: BFONT,
      paraSpaceAfter: o.gap ?? 9, lineSpacing: o.line ?? 20 });
}
function body(s, text, o) {
  s.addText(text, { x: o.x, y: o.y, w: o.w, h: o.h, isTextBox: true, margin: 0,
    fontSize: o.size ?? 14, color: o.color ?? INK, fontFace: BFONT, lineSpacing: o.line ?? 20,
    bold: o.bold, italic: o.italic, align: o.align, valign: o.valign });
}

// ================== 1. TITLE ==================
let s = darkSlide();
s.addShape(p.ShapeType.ellipse, { x: 10.6, y: -1.5, w: 5.2, h: 5.2, fill: { color: IRON2 } });
s.addShape(p.ShapeType.ellipse, { x: 11.9, y: -0.2, w: 2.6, h: 2.6, fill: { color: HEAT } });
s.addText("UCS321 · AI FOR ENGINEERS · MINI PROJECT", { x: M, y: 1.55, w: 9.6, h: 0.3,
  isTextBox: true, margin: 0, fontSize: 12, bold: true, color: HEAT, charSpacing: 2, fontFace: BFONT });
s.addText("Predicting Electric Motor", { x: M, y: 2.05, w: 10.2, h: 0.78, isTextBox: true,
  margin: 0, fontSize: 42, bold: true, color: PAPER, fontFace: HFONT });
s.addText("Winding Temperature", { x: M, y: 2.80, w: 10.2, h: 0.78, isTextBox: true,
  margin: 0, fontSize: 42, bold: true, color: PAPER, fontFace: HFONT });
s.addText("A machine-learning virtual sensor that replaces a thermocouple", { x: M, y: 3.72,
  w: 9.6, h: 0.4, isTextBox: true, margin: 0, fontSize: 15, color: LIGHT, fontFace: BFONT, italic: true });
s.addShape(p.ShapeType.rect, { x: M, y: 4.42, w: 1.5, h: 0.028, fill: { color: HEAT } });
s.addText("Problem Statement 6 — General Electric (GE) Power Systems", { x: M, y: 4.72, w: 9.6,
  h: 0.32, isTextBox: true, margin: 0, fontSize: 13, color: LIGHT, fontFace: BFONT });
s.addText("Lohhith Thakur · 1025220020    |    [ group members ]", { x: M, y: 5.16, w: 9.6,
  h: 0.32, isTextBox: true, margin: 0, fontSize: 13, color: MUTED, fontFace: BFONT });
s.addNotes("Opening line: we picked the problem statement that sits closest to what we already study — electrical machines and sensor data. The framing we chose is a virtual sensor: replace a physical thermocouple with software.");

// ================== 2. WHY IT MATTERS ==================
s = lightSlide(); badge(s, 1);
title(s, "Why winding temperature is the number that matters");
sub(s, "It is the binding constraint on how hard a motor may be driven");
body(s, "A PMSM converts electrical power to mechanical power efficiently, but the loss appears as heat in the stator copper. The winding's enamel insulation has a finite thermal rating. Exceed it and the enamel degrades chemically until adjacent turns short and the machine is destroyed.",
  { x: M, y: 1.78, w: 6.4, h: 1.9, size: 15, line: 23 });
[["180 °C", "Class H insulation rating", HEAT],
 ["÷ 2", "insulation life per +10 °C", HEAT],
 ["0", "production motors with a\nwinding thermocouple", COOL]].forEach(([v, l, c], i) => {
  card(s, M + i * 2.27, 3.94, 2.05, 2.30);
  stat(s, M + i * 2.27, 4.32, 2.05, v, l, c, 36);
});
card(s, 7.5, 1.78, W - 7.5 - M, 4.46, IRON);
body(s, "The engineering consequence", { x: 7.85, y: 2.14, w: 4.4, h: 0.3, size: 13.5, bold: true, color: HEAT });
body(s, "A controller that knows this temperature accurately can use the machine's full short-term overload capability.\n\nA controller that does not must apply a fixed conservative derating — and give up torque the motor could physically have delivered.\n\nSo the estimate is worth real power density, not just a number on a dashboard.",
  { x: 7.85, y: 2.64, w: 4.4, h: 3.3, size: 14.5, color: PAPER, line: 24 });
s.addNotes("Key point to land: this is not an academic regression target. Insulation life halving every 10 degrees is the standard engineering rule of thumb, and it is why the limit is enforced conservatively today.");

// ================== 3. WHY YOU CAN'T MEASURE IT ==================
s = lightSlide(); badge(s, 2);
title(s, "So why not just measure it?");
sub(s, "The sensor is practical on a test bench and impractical in a product");
card(s, M, 1.80, 5.85, 4.58, TINT);
body(s, "ON A TEST BENCH", { x: M + 0.36, y: 2.12, w: 5.1, h: 0.3, size: 12, bold: true, color: COOL, });
bullets(s, ["Thermocouples bonded directly to the winding",
  "Cost and fragility are acceptable — it is one machine",
  "Gives us ground truth to learn from"],
  { x: M + 0.36, y: 2.64, w: 5.1, h: 2.1, size: 15, gap: 13, line: 22 });
body(s, "This dataset comes from exactly such a bench.", { x: M + 0.36, y: 5.62, w: 5.1, h: 0.4,
  size: 13.5, italic: true, color: MUTED });

card(s, 6.95, 1.80, 5.85, 4.58, IRON);
body(s, "IN A PRODUCTION MOTOR", { x: 7.31, y: 2.12, w: 5.1, h: 0.3, size: 12, bold: true, color: HEAT });
bullets(s, ["Sensor must survive winding potential, vibration, thermal cycling",
  "Leads must exit a sealed housing — a new failure mode",
  "Cost does not survive a volume bill of materials"],
  { x: 7.31, y: 2.64, w: 5.1, h: 2.3, size: 15, color: PAPER, gap: 13, line: 22 });
body(s, "So production motors simply do not have one.", { x: 7.31, y: 5.62, w: 5.1, h: 0.4,
  size: 13.5, italic: true, color: LIGHT });
s.addNotes("The gap between these two columns is the entire business case for the project. Examiner may ask: why not a thermal model instead of ML? Answer — lumped-parameter models exist and need per-machine parameter identification; we get comparable accuracy straight from logged data.");

// ================== 4. OBJECTIVE ==================
s = darkSlide();
s.addShape(p.ShapeType.rect, { x: M, y: 1.62, w: 0.05, h: 3.0, fill: { color: HEAT } });
s.addText("OBJECTIVE", { x: M + 0.42, y: 1.62, w: 8, h: 0.3, isTextBox: true, margin: 0,
  fontSize: 12, bold: true, color: HEAT, charSpacing: 2, fontFace: BFONT });
s.addText("Estimate stator winding temperature from the signals a motor drive already measures — accurately enough to use as a thermal protection limit in place of a physical sensor.",
  { x: M + 0.42, y: 2.10, w: 8.6, h: 1.9, isTextBox: true, margin: 0, fontSize: 25,
    bold: true, color: PAPER, fontFace: HFONT, lineSpacing: 34 });
s.addText("Every one of these is already measured for field-oriented control — at zero marginal cost.",
  { x: M + 0.42, y: 4.12, w: 8.6, h: 0.34, isTextBox: true, margin: 0, fontSize: 13,
    color: LIGHT, fontFace: BFONT, italic: true });
["i_d , i_q", "u_d , u_q", "speed", "torque", "coolant", "ambient"].forEach((t, i) => {
  const x = M + 0.42 + (i % 3) * 2.0, y = 4.62 + Math.floor(i / 3) * 0.62;
  s.addShape(p.ShapeType.roundRect, { x, y, w: 1.82, h: 0.48, rectRadius: 0.06, fill: { color: IRON2 } });
  s.addText(t, { x, y, w: 1.82, h: 0.48, isTextBox: true, margin: 0, align: "center",
    valign: "middle", fontSize: 13, color: PAPER, fontFace: BFONT });
});
card(s, 9.55, 1.62, 3.03, 4.3, IRON2);
body(s, "Success is defined by\ndeployment, not by a\nleaderboard.", { x: 9.9, y: 2.0, w: 2.4, h: 1.1,
  size: 15, bold: true, color: PAPER, line: 22 });
body(s, "A model with 1 °C mean error and one 20 °C underestimate still destroys the motor.\n\nSo we report max absolute error and % within ±2 °C, not just RMSE.",
  { x: 9.9, y: 3.26, w: 2.4, h: 2.3, size: 12.5, color: LIGHT, line: 19 });
s.addNotes("This slide is where the marks for problem understanding are won. The last box is the one to emphasise: choosing the right success metric is itself an engineering decision.");

// ================== 5. DATASET ==================
s = lightSlide(); badge(s, 3, COOL);
title(s, "The dataset");
sub(s, "PMSM dynamometer telemetry — Paderborn University (LEA), via Kaggle");
[["1.33 M", "samples", HEAT], ["2 Hz", "sampling rate", COOL],
 ["69", "independent sessions", COOL], ["185 h", "total recording", COOL],
 ["0", "missing values", COOL]].forEach(([v, l, c], i) => {
  const x = M + i * 2.44;
  card(s, x, 1.76, 2.22, 1.5);
  stat(s, x, 1.92, 2.22, v, l, c, 27);
});
img(s, "04_dataset_structure.png", { x: M, y: 3.46, w: 7.4, h: 3.49 });
card(s, 8.5, 3.46, W - 8.5 - M, 3.3, IRON);
body(s, "Eight inputs retained", { x: 8.85, y: 3.72, w: 3.4, h: 0.3, size: 13, bold: true, color: HEAT });
body(s, "i_d, i_q  ·  u_d, u_q  ·  motor speed  ·  torque  ·  coolant  ·  ambient",
  { x: 8.85, y: 4.10, w: 3.4, h: 0.85, size: 12.5, color: PAPER, line: 19 });
body(s, "Three channels discarded", { x: 8.85, y: 5.02, w: 3.4, h: 0.3, size: 13, bold: true, color: HEAT });
body(s, "stator_tooth · stator_yoke · pm\n\nCorrelated r > 0.95 with the target — and dropped anyway. Next slide explains why.",
  { x: 8.85, y: 5.40, w: 3.4, h: 1.2, size: 12.5, color: LIGHT, line: 19 });
s.addNotes("69 sessions, each a continuous recording with its own excitation schedule. The session is the natural unit for splitting — that becomes important three slides from now.");

// ================== 6. THE LEAKAGE DECISION ==================
s = lightSlide(); badge(s, 4);
title(s, "The most important decision we made");
sub(s, "Throwing away the three features that would have scored best");
card(s, M, 1.78, 5.7, 1.2, IRON);
body(s, "stator_tooth   ·   stator_yoke   ·   pm", { x: M + 0.3, y: 1.96, w: 5.1, h: 0.35,
  size: 15, bold: true, color: PAPER });
body(s, "correlate with the target at r > 0.95", { x: M + 0.3, y: 2.38, w: 5.1, h: 0.35,
  size: 13, color: HEAT, italic: true });
body(s, "Including them yields a spectacular R². We dropped all three.",
  { x: M, y: 3.14, w: 5.7, h: 0.4, size: 14, bold: true });
bullets(s, [
  "It defeats the objective. Those sensors are exactly the hardware we are trying to remove. A model that needs stator_tooth cannot run on a motor that has neither.",
  "It is target leakage. Tooth and yoke sit millimetres from the winding in the same iron. The model would be interpolating between adjacent thermocouples — not learning thermodynamics."],
  { x: M, y: 3.66, w: 5.7, h: 2.4, size: 13, gap: 14 });

card(s, 7.05, 1.78, W - 7.05 - M, 4.28, TINT);
body(s, "What the numbers look like without them", { x: 7.4, y: 2.06, w: 4.9, h: 0.3,
  size: 13, bold: true, color: COOL });
img(s, "03_correlation.png", { x: 7.55, y: 2.46, w: 3.35, h: 2.95 });
body(s, "No raw electrical channel exceeds |r| = 0.63.\nThat ceiling is thermal inertia showing up numerically — and it is what the next slide is about.",
  { x: 11.1, y: 2.9, w: 1.55, h: 2.2, size: 11.5, color: MUTED, line: 17 });
s.addNotes("Expect a question here: 'wouldn't your accuracy be higher if you kept them?' Yes — and the result would be worthless, because the deployment target has none of those sensors. This is the slide that shows we understood the problem rather than the dataset.");

// ================== 7. THE KEY OBSERVATION ==================
s = lightSlide(); badge(s, 5);
title(s, "The observation the whole project rests on");
sub(s, "Current changes in seconds. Temperature answers in minutes.");
img(s, "01_thermal_lag.png", { x: M, y: 1.72, w: 7.55, h: 6.41 * 7.55 / 8.0 });
card(s, 8.55, 1.72, W - 8.55 - M, 4.34, IRON);
body(s, "Why this breaks a naive model", { x: 8.9, y: 2.02, w: 3.4, h: 0.3, size: 13,
  bold: true, color: HEAT });
body(s, "Winding temperature is not a function of the present current. It is a function of the accumulated loss over the recent past.\n\nA model given only instantaneous values is being asked to infer a state variable from its input — which for a system with memory is impossible in principle, not merely hard in practice.",
  { x: 8.9, y: 2.46, w: 3.4, h: 3.2, size: 12.5, color: PAPER, line: 20 });
s.addNotes("Point at the bottom panel against the middle one. Temperature keeps rising after current has already stepped down. Everything that follows is a response to this one picture.");

// ================== 8. FEATURE ENGINEERING ==================
s = lightSlide(); badge(s, 6);
title(s, "From physics to features");
sub(s, "The thermal model tells us exactly what transform to apply");
card(s, M, 1.76, 5.75, 2.65, IRON);
body(s, "LUMPED-PARAMETER THERMAL MODEL", { x: M + 0.32, y: 1.98, w: 5.1, h: 0.28,
  size: 10.5, bold: true, color: HEAT, });
body(s, "C_th · dϑ/dt  =  P_loss(t)  −  (ϑ − ϑ_amb) / R_th", { x: M + 0.32, y: 2.34,
  w: 5.1, h: 0.36, size: 14.5, color: PAPER, italic: true });
body(s, "solving gives", { x: M + 0.32, y: 2.78, w: 5.1, h: 0.26, size: 11, color: MUTED });
body(s, "ϑ(t) = (1/τ) ∫ exp(−(t−s)/τ) · P_loss(s) ds", { x: M + 0.32, y: 3.06, w: 5.1,
  h: 0.36, size: 14.5, color: PAPER, italic: true });
body(s, "— an exponentially weighted integral of past losses.", { x: M + 0.32, y: 3.50,
  w: 5.1, h: 0.3, size: 12, color: LIGHT, italic: true });
body(s, "which in discrete time is exactly an EWMA:   y[k] = α·x[k] + (1−α)·y[k−1]",
  { x: M + 0.32, y: 3.86, w: 5.1, h: 0.4, size: 12.5, bold: true, color: HEAT, line: 17 });

body(s, "So we compute EWMAs of the loss-related signals at five thermal time constants — 30 s, 120 s, 600 s, 1800 s, 3600 s — because copper, iron and housing respond on different scales.",
  { x: M, y: 4.66, w: 5.75, h: 1.0, size: 13.5, line: 20 });
[["8", "raw channels", MUTED], ["→", "", MUTED], ["104", "engineered features", HEAT]]
  .forEach(([v, l, c], i) => {
    stat(s, M + i * 1.95, 5.86, 1.8, v, l, c, i === 1 ? 28 : 36);
  });

card(s, 7.1, 1.76, W - 7.1 - M, 5.12, TINT);
body(s, "Does one transform actually help?", { x: 7.45, y: 2.02, w: 4.9, h: 0.3, size: 13,
  bold: true, color: COOL });
img(s, "02_ewma_motivation.png", { x: 7.45, y: 2.44, w: 4.85, h: 4.85 * 881 / 1686 });
body(s, "Same signal. One 10-minute exponential filter. A diffuse cloud becomes a structured relationship — before any model has been fitted.",
  { x: 7.45, y: 5.06, w: 4.85, h: 0.8, size: 12.5, color: MUTED, line: 18 });
s.addNotes("This is the innovation slide. The claim to make explicitly: we did not pick EWMA by trial and error — the analytical solution of the thermal ODE IS an exponentially weighted integral, so the feature is the physics written down.");

// ================== 9. SPLIT PROTOCOL ==================
s = lightSlide(); badge(s, 7);
title(s, "Why we did not use train_test_split");
sub(s, "On 2 Hz data, a random split measures memorisation");
card(s, M, 1.82, 5.75, 2.05, TINT);
body(s, "THE TRAP", { x: M + 0.32, y: 2.04, w: 5.1, h: 0.28, size: 10.5, bold: true, color: HEAT });
body(s, "Samples are 0.5 s apart. A motor's temperature cannot change in half a second, so consecutive rows are near-duplicates. A random split scatters near-identical samples across both sides — the test set is effectively inside the training set.",
  { x: M + 0.32, y: 2.38, w: 5.1, h: 1.4, size: 13, line: 19 });
card(s, M, 4.10, 5.75, 2.35, IRON);
body(s, "WHAT WE DID INSTEAD", { x: M + 0.32, y: 4.32, w: 5.1, h: 0.28, size: 10.5,
  bold: true, color: HEAT });
body(s, "Hold out entire measurement sessions. The model is evaluated the way it would be used: on a motor run it has never seen.",
  { x: M + 0.32, y: 4.66, w: 5.1, h: 0.7, size: 13, color: PAPER, line: 19 });
[["Train", "64 profiles", "1,211,517"], ["Validation", "3 profiles", "63,904"],
 ["Test", "profiles 65 & 72", "55,395"]].forEach(([a, b, c], i) => {
  const y = 5.42 + i * 0.32;
  body(s, a, { x: M + 0.32, y, w: 1.3, h: 0.28, size: 12, bold: true, color: i === 2 ? HEAT : PAPER });
  body(s, b, { x: M + 1.62, y, w: 1.8, h: 0.28, size: 12, color: LIGHT });
  body(s, c + " samples", { x: M + 3.42, y, w: 2.0, h: 0.28, size: 12, color: LIGHT });
});
card(s, 7.1, 1.82, W - 7.1 - M, 4.63, TINT);
img(s, "10_split_protocol.png", { x: 7.3, y: 1.98, w: 5.1, h: 5.1 * 2347 / 3401 });
body(s, "The cost of getting this wrong", { x: 7.45, y: 5.52, w: 4.9, h: 0.3, size: 13,
  bold: true, color: COOL });
body(s, "Random split:  R² = 0.9995, RMSE 0.66 °C   ·   whole sessions held out:  R² = 0.9908, RMSE 2.50 °C",
  { x: 7.45, y: 5.88, w: 4.9, h: 0.5, size: 12, color: MUTED, line: 16 });
body(s, "Random splitting understates RMSE by ~3.8×.",
  { x: 7.45, y: 6.42, w: 4.9, h: 0.3, size: 12.5, bold: true, color: HEAT });
s.addNotes("Strongest viva moment in the deck. Most teams working on time-series data will report the 0.9995 figure. Being able to say why it is wrong, and quantify it, is the differentiator.");

// ================== 10. MODEL LADDER ==================
s = lightSlide(); badge(s, 8, COOL);
title(s, "The model ladder");
sub(s, "Every increase in complexity has to justify itself against the rung below");
const rungs = [
  ["Linear regression", "8 raw inputs, OLS", "the honest floor", MUTED],
  ["Ridge regression", "104 engineered features", "isolates the feature work", COOL],
  ["Random Forest", "80 trees, depth 16", "non-parametric reference", COOL],
  ["MLP", "2 × 128, early stopping", "smooth approximator", HEAT],
  ["LightGBM", "743 trees, early-stopped", "strong tabular baseline", COOL],
];
rungs.forEach(([n, cfg, why, col], i) => {
  const y = 1.86 + i * 0.86;
  card(s, M, y, 8.4, 0.72, i === 3 ? IRON : TINT);
  s.addShape(p.ShapeType.ellipse, { x: M + 0.22, y: y + 0.19, w: 0.34, h: 0.34, fill: { color: col } });
  body(s, String(i + 1), { x: M + 0.22, y: y + 0.19, w: 0.34, h: 0.34, size: 11, bold: true,
    color: PAPER, align: "center", valign: "middle" });
  body(s, n, { x: M + 0.74, y: y + 0.1, w: 2.5, h: 0.52, size: 14.5, bold: true,
    color: i === 3 ? PAPER : INK, valign: "middle" });
  body(s, cfg, { x: M + 3.3, y: y + 0.1, w: 2.6, h: 0.52, size: 12.5,
    color: i === 3 ? LIGHT : MUTED, valign: "middle" });
  body(s, why, { x: M + 5.95, y: y + 0.1, w: 2.3, h: 0.52, size: 12.5, italic: true,
    color: i === 3 ? HEAT : MUTED, valign: "middle" });
});
card(s, 9.5, 1.86, W - 9.5 - M, 4.32, IRON);
body(s, "Same data.\nSame split.\nSame metrics.", { x: 9.85, y: 2.16, w: 2.4, h: 1.0,
  size: 16, bold: true, color: PAPER, line: 24 });
body(s, "All five fitted on the identical training partition and scored on the identical held-out sessions, so the comparison isolates the model and nothing else.",
  { x: 9.85, y: 3.3, w: 2.4, h: 1.8, size: 12.5, color: LIGHT, line: 19 });
body(s, "Highlighted rung wins →", { x: 9.85, y: 5.36, w: 2.4, h: 0.4, size: 12,
  bold: true, color: HEAT });
s.addNotes("Mention the subsampling: RF and MLP were fitted on every 10th training sample. At 2 Hz the data is so autocorrelated that this costs essentially no information and saves an order of magnitude of compute.");

// ================== 11. THE CENTRAL RESULT ==================
s = darkSlide();
s.addText("THE CENTRAL FINDING", { x: M, y: 0.86, w: 9, h: 0.3, isTextBox: true, margin: 0,
  fontSize: 12, bold: true, color: HEAT, charSpacing: 2, fontFace: BFONT });
s.addText("Feature engineering beat every model we tried", { x: M, y: 1.26, w: 11.4, h: 0.7,
  isTextBox: true, margin: 0, fontSize: 34, bold: true, color: PAPER, fontFace: HFONT });
s.addText("Same algorithm. Same data. Same training procedure. Only the inputs changed.",
  { x: M, y: 2.06, w: 11.4, h: 0.34, isTextBox: true, margin: 0, fontSize: 14,
    color: LIGHT, fontFace: BFONT, italic: true });
[["Linear regression\non 8 raw inputs", "0.5324", "R²", "17.79 °C", "RMSE", MUTED],
 ["Linear regression\n+ EWMA features", "0.9936", "R²", "2.08 °C", "RMSE", HEAT]]
 .forEach(([lab, r2, r2l, rm, rml, col], i) => {
  const x = M + i * 5.9;
  s.addShape(p.ShapeType.roundRect, { x, y: 2.82, w: 5.4, h: 3.1, rectRadius: 0.08,
    fill: { color: i ? IRON2 : IRON }, line: { color: i ? HEAT : IRON2, width: i ? 1.6 : 1 } });
  body(s, lab, { x: x + 0.42, y: 3.08, w: 4.6, h: 0.62, size: 14, bold: true, color: PAPER, line: 19 });
  body(s, r2, { x: x + 0.42, y: 3.82, w: 2.3, h: 0.7, size: 40, bold: true, color: col });
  body(s, r2l, { x: x + 0.42, y: 4.56, w: 2.3, h: 0.3, size: 12, color: MUTED });
  body(s, rm, { x: x + 2.9, y: 3.94, w: 2.1, h: 0.56, size: 26, bold: true, color: PAPER });
  body(s, rml, { x: x + 2.9, y: 4.56, w: 2.1, h: 0.3, size: 12, color: MUTED });
  body(s, i ? "81.3 % of samples within ±2 °C" : "8.1 % of samples within ±2 °C",
    { x: x + 0.42, y: 5.16, w: 4.6, h: 0.34, size: 12.5, color: i ? HEAT : MUTED });
});
s.addShape(p.ShapeType.ellipse, { x: 6.28, y: 4.02, w: 0.74, h: 0.74, fill: { color: HEAT } });
s.addText("→", { x: 6.28, y: 4.02, w: 0.74, h: 0.74, isTextBox: true, margin: 0, align: "center",
  valign: "middle", fontSize: 22, bold: true, color: IRON, fontFace: BFONT });
s.addText("Domain-informed feature engineering outperformed every increase in model sophistication attempted in this project.",
  { x: M, y: 6.26, w: 11.4, h: 0.4, isTextBox: true, margin: 0, fontSize: 14.5, bold: true,
    color: PAPER, fontFace: BFONT, align: "center" });
s.addNotes("Pause on this slide. If the examiner remembers one thing, it should be this pair of numbers. It also answers 'did you just throw XGBoost at it' — no, the physics did the work.");

// ================== 12. FULL COMPARISON ==================
s = lightSlide(); badge(s, 9, COOL);
title(s, "Full model comparison");
sub(s, "Held-out sessions only — profiles 65 and 72, 55,395 samples");
const rows = [
  ["Model", "RMSE", "MAE", "R²", "Max err", "±2 °C"],
  ["Linear (raw inputs)", "17.79", "14.37", "0.5324", "69.27", "8.1 %"],
  ["Ridge (+ EWMA)", "2.08", "1.54", "0.9936", "26.19", "71.7 %"],
  ["Random Forest", "3.60", "2.49", "0.9808", "15.56", "56.8 %"],
  ["MLP (2 × 128)", "1.67", "1.26", "0.9959", "9.84", "81.3 %"],
  ["LightGBM", "2.50", "1.85", "0.9908", "11.05", "65.8 %"],
  ["MLP — tuned", "1.54", "1.10", "0.9965", "11.32", "84.2 %"],
];
s.addTable(rows.map((r, ri) => r.map((c, ci) => ({
  text: c,
  options: {
    fontSize: ri === 0 ? 12 : 12.5, bold: ri === 0 || ri === 6,
    color: ri === 0 ? PAPER : (ri === 6 ? PAPER : INK),
    fill: { color: ri === 0 ? IRON : (ri === 6 ? COOL : (ri % 2 ? TINT : PAPER)) },
    align: ci === 0 ? "left" : "center", valign: "middle", fontFace: BFONT,
  },
}))), { x: M, y: 1.78, w: 7.6, colW: [2.5, 1.02, 1.02, 1.02, 1.02, 1.02], rowH: 0.375,
  border: { type: "solid", color: "E3E6E9", pt: 1 }, margin: 6 });
body(s, "The three metrics do not rank the models identically — see the next slide.",
  { x: M, y: 4.52, w: 7.6, h: 0.34, size: 12, italic: true, color: MUTED });
card(s, M, 4.98, 7.6, 1.76, TINT);
[["Tuning gained", "RMSE 1.67 → 1.54 °C,  MAE 1.26 → 1.10 °C", COOL],
 ["Tuning cost", "worst case 9.84 → 11.32 °C — the search optimised RMSE", HEAT]]
 .forEach(([h, b, col], i) => {
  const y = 5.16 + i * 0.80;
  body(s, h, { x: M + 0.3, y, w: 1.9, h: 0.3, size: 12.5, bold: true, color: col });
  body(s, b, { x: M + 2.25, y, w: 5.2, h: 0.5, size: 12.3, color: INK, line: 16 });
});
card(s, 8.6, 1.78, W - 8.6 - M, 4.92, IRON);
body(s, "Selected model", { x: 8.95, y: 2.04, w: 3.4, h: 0.3, size: 12, color: HEAT, bold: true });
body(s, "MLP 2 × 128", { x: 8.95, y: 2.40, w: 3.4, h: 0.44, size: 21, bold: true, color: PAPER });
body(s, "tuned", { x: 8.95, y: 2.80, w: 3.4, h: 0.26, size: 12, color: HEAT });
[["1.54 °C", "RMSE"], ["0.9965", "R²"], ["11.32 °C", "worst-case error"],
 ["84.2 %", "within ±2 °C"]].forEach(([v, l], i) => {
  const y = 3.22 + i * 0.76;
  body(s, v, { x: 8.95, y, w: 3.4, h: 0.38, size: 19, bold: true, color: i === 2 ? HEAT : PAPER });
  body(s, l, { x: 8.95, y: y + 0.38, w: 3.4, h: 0.28, size: 11.5, color: MUTED });
});
s.addNotes("Worth flagging: Ridge beats LightGBM on RMSE but has a 26 degree worst case versus LightGBM's 11. Selecting on RMSE alone would have picked the wrong model for a protection function.");

// ================== 13. INTERPRETATION ==================
s = lightSlide(); badge(s, 10);
title(s, "Three results worth explaining");
sub(s, "The interpretation matters more than the table");
[["The neural net beat both tree ensembles.",
  "Tree ensembles are piecewise-constant — a prediction is the mean of the training samples in a leaf, so they cannot produce a value outside the range they saw. Held-out sessions contain operating points the 64 training profiles never visit. An MLP is smooth and continues the trend. Under genuine extrapolation, smoothness is the decisive property.", HEAT],
 ["Ridge regression beat LightGBM.",
  "Once the features encode the thermal physics, the residual relationship is close to linear. A low-variance estimator then generalises across sessions better than a high-capacity one, which fits session-specific structure that does not transfer.", COOL],
 ["RMSE and worst-case error disagree.",
  "Ridge attains RMSE 2.08 °C — better than LightGBM's 2.50 °C — yet its worst case is 26.19 °C against 11.05 °C. For a thermal limit the second column governs. A model chosen on RMSE alone would have been the wrong choice.", COOL],
].forEach(([h, b, col], i) => {
  const y = 1.78 + i * 1.62;
  card(s, M, y, 8.3, 1.42, TINT);
  s.addShape(p.ShapeType.ellipse, { x: M + 0.26, y: y + 0.24, w: 0.4, h: 0.4, fill: { color: col } });
  body(s, String(i + 1), { x: M + 0.26, y: y + 0.24, w: 0.4, h: 0.4, size: 12, bold: true,
    color: PAPER, align: "center", valign: "middle" });
  body(s, h, { x: M + 0.84, y: y + 0.18, w: 7.2, h: 0.32, size: 14, bold: true, color: INK });
  body(s, b, { x: M + 0.84, y: y + 0.54, w: 7.2, h: 0.8, size: 11.8, color: MUTED, line: 16 });
});
card(s, 9.35, 1.78, W - 9.35 - M, 4.86, IRON);
body(s, "Residual check", { x: 9.7, y: 2.04, w: 2.9, h: 0.3, size: 13, bold: true, color: HEAT });
img(s, "07_residuals.png", { x: 9.7, y: 2.44, w: 2.85, h: 2.85 * 840 / 1722 });
body(s, "Error does not grow with operating temperature.\n\nThat is the check that matters: a model accurate when cool and poor when hot would be useless, because the hot regime is the only one where the estimate is consulted.",
  { x: 9.7, y: 3.94, w: 2.9, h: 2.4, size: 11.8, color: LIGHT, line: 17 });
s.addNotes("Result 1 is the one examiners find most interesting — it is counter to the usual assumption that gradient boosting always wins on tabular data. Be ready to explain leaf-wise constant prediction.");

// ================== 14. TRACKING ==================
s = lightSlide(); badge(s, 11, COOL);
title(s, "Tracking on motors the model has never seen");
sub(s, "Neither session appeared in training in any form");
img(s, "06_predicted_vs_actual.png", { x: M, y: 1.70, w: 8.05, h: 8.05 * 1283 / 1849 });
card(s, 9.05, 1.70, W - 9.05 - M, 5.55, IRON);
body(s, "What to look at", { x: 9.4, y: 2.0, w: 3.1, h: 0.3, size: 13.5, bold: true, color: HEAT });
bullets(s, ["Rapid transients under aggressive load cycling are tracked",
  "Slow exponential cool-down is tracked",
  "Largest deviations sit at sharp transitions"],
  { x: 9.4, y: 2.46, w: 3.1, h: 2.4, size: 13.5, color: PAPER, gap: 13, line: 19 });
body(s, "That lag at step changes is the expected signature of a filter-based feature set meeting a change faster than its shortest time constant.",
  { x: 9.4, y: 5.18, w: 3.1, h: 1.7, size: 12.8, color: LIGHT, italic: true, line: 19 });
s.addNotes("If asked how to fix the transition lag: add a shorter EWMA span, or move to a sequence model that learns the time constants rather than having them fixed.");

// ================== 15. VALIDATION ==================
s = lightSlide(); badge(s, 12);
title(s, "Two studies that test whether the result is real");
sub(s, "Ablation and leakage — both with everything else held constant");
card(s, M, 1.76, 5.85, 4.6, TINT);
body(s, "ABLATION — where does the accuracy come from?", { x: M + 0.32, y: 2.0, w: 5.2,
  h: 0.3, size: 12, bold: true, color: COOL });
[["8 raw input channels", "14.39", "0.6942", MUTED],
 ["+ instantaneous physical terms", "14.58", "0.6860", MUTED],
 ["+ EWMA thermal history", "2.43", "0.9913", HEAT]].forEach(([a, b, c, col], i) => {
  const y = 2.44 + i * 0.72;
  card(s, M + 0.32, y, 5.2, 0.62, PAPER);
  body(s, a, { x: M + 0.52, y: y + 0.02, w: 2.9, h: 0.58, size: 12.2, valign: "middle",
    bold: i === 2, color: i === 2 ? INK : MUTED });
  body(s, b, { x: M + 3.42, y: y + 0.02, w: 0.95, h: 0.58, size: 14, bold: true,
    color: col, align: "center", valign: "middle" });
  body(s, c, { x: M + 4.37, y: y + 0.02, w: 1.05, h: 0.58, size: 14, bold: true,
    color: col, align: "center", valign: "middle" });
});
body(s, "RMSE          R²", { x: M + 3.42, y: 2.18, w: 2.0, h: 0.24, size: 10, color: MUTED, align: "center" });
body(s, "Instantaneous physical terms buy nothing on their own — the small regression is within run-to-run variation. Only thermal history moves the result. The gain is not from having more columns.",
  { x: M + 0.32, y: 4.74, w: 5.2, h: 1.3, size: 12.5, line: 18 });

card(s, 7.05, 1.76, W - 7.05 - M, 4.6, IRON);
body(s, "LEAKAGE — the cost of the wrong split", { x: 7.4, y: 2.0, w: 5.0, h: 0.3,
  size: 12, bold: true, color: HEAT });
img(s, "09_ablation_leakage.png", { x: 7.4, y: 2.5, w: 5.0, h: 5.0 * 871 / 2140 });
body(s, "Same model, same features, only the partitioning changes. Random splitting reports R² = 0.9995 — a figure describing the model's ability to reproduce samples it has already seen in near-identical form.",
  { x: 7.4, y: 4.6, w: 5.0, h: 1.1, size: 12.2, color: PAPER, line: 18 });
body(s, "For time-series sampled faster than the system's dynamics, grouped splitting is a correctness requirement, not a refinement.",
  { x: 7.4, y: 5.72, w: 5.0, h: 0.56, size: 12, bold: true, color: HEAT, line: 17 });
s.addNotes("These two studies are what turn a result into evidence. Without the ablation we could not claim the EWMAs specifically caused the gain rather than the feature count.");

// ================== 15b. TUNING ==================
s = lightSlide(); badge(s, 13);
title(s, "Tuning, without undoing the split discipline");
sub(s, "RandomizedSearchCV under GroupKFold grouped on profile_id");
card(s, M, 1.78, 5.1, 2.5, IRON);
body(s, "THE CONSTRAINT THAT MATTERS", { x: M + 0.3, y: 2.0, w: 4.5, h: 0.28,
  size: 10.5, bold: true, color: HEAT });
body(s, "A candidate is never scored on a session it was fitted on.\n\nA plain KFold inside the search would reintroduce exactly the leakage the outer split removes — and invisibly, because the CV score would simply look better.",
  { x: M + 0.3, y: 2.36, w: 4.5, h: 1.8, size: 12.5, color: PAPER, line: 19 });
[["18", "candidates", HEAT], ["3", "grouped folds", COOL], ["19", "minutes of search", COOL]]
  .forEach(([v, l, c], i) => {
    const x = M + i * 1.72;
    card(s, x, 4.46, 1.55, 1.5);
    stat(s, x, 4.62, 1.55, v, l, c, 26);
  });
body(s, "Selected:  hidden (128, 128) · alpha 0.01 · lr 0.001", { x: M, y: 6.12, w: 5.1,
  h: 0.4, size: 11.5, color: MUTED, line: 15 });
img(s, "11_tuning_results.png", { x: 6.1, y: 1.9, w: 6.5, h: 6.5 * 1741 / 3760 });
card(s, 6.1, 5.0, W - 6.1 - M, 1.62, TINT);
body(s, "Tuning improved RMSE by ~8 % and MAE by ~13 %. It did not improve worst-case error — that moved from 9.84 °C to 11.32 °C, because the search optimised RMSE and nothing constrained the tail.",
  { x: 6.42, y: 5.22, w: 6.0, h: 1.2, size: 12.5, line: 18 });
s.addNotes("The honest framing: we selected on RMSE and then disclosed max error, rather than retrofitting the criterion. If worst case were the selection criterion, tuned HistGradientBoosting at 9.53 would win instead.");

// ================== 15c. ERROR ANALYSIS ==================
s = lightSlide(); badge(s, 14, COOL);
title(s, "Where the error actually lives");
sub(s, "Broken down three ways on the held-out sessions");
img(s, "12_error_analysis.png", { x: 1.15, y: 1.58, w: 11.0, h: 11.0 * 1789 / 3723 });
card(s, M, 6.76, W - 2 * M, 0.56, IRON);
body(s, "Median error holds near 1 °C across every temperature and load band — accuracy does not decay when the motor is hot or working hard. The real weakness is the third panel: the worst errors sit in the first minutes, while the 1800 s and 3600 s filters are still converging.",
  { x: M + 0.3, y: 6.84, w: W - 2 * M - 0.6, h: 0.42, size: 11, color: PAPER, line: 14 });
s.addNotes("If asked how to fix the warm-up penalty: seed the EWMA state from the first sample instead of zero, add a shorter span, or move to a sequence model that learns the time constants.");

// ================== 16. PHYSICS VALIDATION ==================
s = lightSlide(); badge(s, 15, COOL);
title(s, "The model learned the physics we designed for");
sub(s, "Strongest evidence that the result is not an artefact");
img(s, "08_feature_importance.png", { x: M, y: 1.74, w: 6.5, h: 6.5 * 1041 / 1556 });
card(s, 7.6, 1.74, W - 7.6 - M, 4.62, IRON);
body(s, "All top-15 features are thermal history", { x: 7.95, y: 2.02, w: 4.4, h: 0.32,
  size: 14, bold: true, color: PAPER });
[["coolant_ewma_600s", "the heat-sink boundary condition"],
 ["i_s²_ewma_600s", "the copper-loss term,  P = I²R"]].forEach(([f, m], i) => {
  const y = 2.56 + i * 1.06;
  card(s, 7.95, y, 4.4, 0.9, IRON2);
  body(s, f, { x: 8.2, y: y + 0.1, w: 4.0, h: 0.32, size: 13, bold: true, color: HEAT });
  body(s, m, { x: 8.2, y: y + 0.46, w: 4.0, h: 0.32, size: 11.8, color: LIGHT });
});
body(s, "These are exactly the two terms the lumped-parameter thermal model on slide 8 identifies as dominant.\n\nGiven no information about motor thermodynamics beyond which signals to filter, the model independently concentrated on them.",
  { x: 7.95, y: 4.76, w: 4.4, h: 1.5, size: 12.5, color: PAPER, line: 19 });
s.addNotes("This is the interpretability slide. It closes the loop: we derived the features from physics, and the trained model independently ranked the physically dominant terms highest.");

// ================== 17. DEPLOYMENT ==================
s = lightSlide(); badge(s, 16);
title(s, "It is cheap enough to run on the drive");
sub(s, "Which is what makes it a replacement for a thermocouple, not an offline analysis");
[["~60 k", "MAC/s at the 2 Hz\nupdate rate", HEAT],
 ["90", "state registers for the\nentire feature extractor", COOL],
 ["1", "multiply-add per\nEWMA feature", COOL],
 ["16-bit", "sufficient output precision\n(Q16.16 accumulators)", COOL]]
 .forEach(([v, l, c], i) => {
  const x = M + i * 3.0;
  card(s, x, 1.78, 2.8, 1.86);
  stat(s, x, 1.96, 2.8, v, l, c, 30);
});
card(s, M, 3.92, 5.85, 2.5, IRON);
body(s, "WHY THE FEATURE EXTRACTOR IS HARDWARE-FRIENDLY", { x: M + 0.32, y: 4.14, w: 5.2,
  h: 0.28, size: 10.5, bold: true, color: HEAT });
body(s, "Each EWMA is a single-pole IIR filter: one multiply, one add, one register. No windowing buffer, no stored history.\n\nA conventional one-hour sliding-window statistic at 2 Hz would need 7,200 buffered samples per signal. The recursive form needs one.",
  { x: M + 0.32, y: 4.50, w: 5.2, h: 1.8, size: 12.5, color: PAPER, line: 19 });
card(s, 7.05, 3.92, W - 7.05 - M, 2.5, TINT);
body(s, "HONEST LIMITATIONS", { x: 7.4, y: 4.14, w: 5.0, h: 0.28, size: 10.5, bold: true, color: COOL });
bullets(s, ["Worst case is still 9.84 °C — a deployed limit needs a margin, just a smaller one than a fixed derating",
  "Trained on one machine on one bench; a different design needs retraining or transfer learning",
  "Error is largest at sharp load transitions"],
  { x: 7.4, y: 4.50, w: 5.0, h: 1.8, size: 12, gap: 8, line: 16 });
s.addNotes("Tie this back to our own background — this is the slide where the VLSI angle pays off. The EWMA recurrence maps directly to a small fixed-point datapath; an RTL implementation is listed as future work.");

// ================== 18. CONCLUSIONS ==================
s = darkSlide();
s.addText("CONCLUSIONS", { x: M, y: 0.72, w: 9, h: 0.3, isTextBox: true, margin: 0,
  fontSize: 12, bold: true, color: HEAT, charSpacing: 2, fontFace: BFONT });
s.addText("What we take away", { x: M, y: 1.10, w: 11.4, h: 0.6, isTextBox: true, margin: 0,
  fontSize: 32, bold: true, color: PAPER, fontFace: HFONT });
[["The objective was met.", "RMSE 1.54 °C, R² 0.9965, 84.2 % within ±2 °C on motor sessions never seen during training."],
 ["Feature engineering, not model selection, produced the result.", "An unchanged linear regression improves from R² 0.53 to 0.99 once its inputs encode thermal history."],
 ["The evaluation protocol changes the answer by 4×.", "Profile-wise splitting is a correctness requirement on data of this kind, not a refinement."],
 ["A smooth model generalises better than tree ensembles here.", "Held-out sessions demand extrapolation, and piecewise-constant models cannot extrapolate."],
 ["The model learned the intended physics.", "Its dominant features are the coolant boundary condition and the copper-loss term."],
].forEach(([h, b], i) => {
  const y = 2.02 + i * 0.86;
  s.addShape(p.ShapeType.ellipse, { x: M, y: y + 0.08, w: 0.38, h: 0.38, fill: { color: HEAT } });
  s.addText(String(i + 1), { x: M, y: y + 0.08, w: 0.38, h: 0.38, isTextBox: true, margin: 0,
    align: "center", valign: "middle", fontSize: 11.5, bold: true, color: IRON, fontFace: BFONT });
  s.addText(h, { x: M + 0.58, y, w: 11.0, h: 0.32, isTextBox: true, margin: 0, fontSize: 15,
    bold: true, color: PAPER, fontFace: BFONT });
  s.addText(b, { x: M + 0.58, y: y + 0.34, w: 11.0, h: 0.34, isTextBox: true, margin: 0,
    fontSize: 12.5, color: LIGHT, fontFace: BFONT });
});
s.addText("Future work:  sequence models that learn the time constants  ·  multi-output prediction of all four temperatures  ·  physics-informed loss  ·  fixed-point RTL implementation of the EWMA extractor",
  { x: M, y: 6.5, w: 11.9, h: 0.5, isTextBox: true, margin: 0, fontSize: 12,
    color: MUTED, fontFace: BFONT, italic: true, lineSpacing: 17 });
s.addNotes("Close on point 2 — it is the transferable lesson, not just a result about motors.");

// ================== 19. BACKUP: VIVA Q&A ==================
s = lightSlide(); badge(s, "?", IRON);
title(s, "Anticipated questions");
sub(s, "Backup slide — not presented unless asked");
const qa = [
  ["Why not just use a lumped-parameter thermal model?",
   "They exist and work, but need per-machine parameter identification on a bench. We reach comparable accuracy directly from logged data, and our features are that model's analytical solution anyway."],
  ["Wouldn't keeping stator_tooth give better accuracy?",
   "Yes — and the result would be worthless. Those sensors are the hardware we are replacing; a production motor has none of them."],
  ["Why does the MLP beat gradient boosting?",
   "Trees predict the mean of a leaf, so they cannot output values beyond the training range. Held-out sessions require extrapolation; a smooth model handles it."],
  ["Is R² = 0.996 not suspiciously high?",
   "It would be under a random split — we show that gives 0.9995 and is meaningless. Ours is on entirely held-out sessions, and we report the 9.84 °C worst case alongside it."],
  ["How did you choose the five EWMA spans?",
   "From the physical time constants: copper responds in tens of seconds, iron in minutes, housing and coolant in tens of minutes. We bracketed that range and let the model weight them."],
  ["What would you do with more time?",
   "A temporal CNN or LSTM that learns the time constants instead of having them fixed, and a physics-informed loss enforcing the thermal ODE."],
];
qa.forEach(([q, a], i) => {
  const col = i % 2, row = Math.floor(i / 2);
  const x = M + col * 6.1, y = 1.76 + row * 1.62;
  card(s, x, y, 5.75, 1.46, TINT);
  body(s, q, { x: x + 0.28, y: y + 0.16, w: 5.2, h: 0.34, size: 12.8, bold: true, color: HEAT });
  body(s, a, { x: x + 0.28, y: y + 0.54, w: 5.2, h: 0.84, size: 11.5, color: INK, line: 15.5 });
});
s.addNotes("Keep this slide hidden during the talk; jump to it only if one of these comes up.");

fs.mkdirSync(path.dirname(OUT), { recursive: true });
p.writeFile({ fileName: OUT })
  .then(f => console.log("deck written:", f));
