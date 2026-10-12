// ---------------------------------------------------------------------------
// UCS321 MST mini project - 10-slide presentation deck.
// Structured deck: one theme, five layouts, named placeholders, sections.
// Every figure in figures/ appears exactly once. Every number is taken from
// outputs/results.json and outputs/tuning.json.
//   node docs_src/build_deck10.js   ->  reports/UCS321_Presentation_10slide.pptx
// ---------------------------------------------------------------------------
const pptxgen = require("pptxgenjs");
const path = require("path");
const fs = require("fs");

const ROOT = path.resolve(__dirname, "..");
const FIG = path.join(ROOT, "figures") + path.sep;
const OUT = path.join(ROOT, "reports", "UCS321_Presentation_10slide.pptx");
const { applyTheme } = require("/mnt/skills/public/pptx/scripts/apply_theme.js");

const W = 13.333, H = 7.5, M = 0.62;

// ---- theme: iron / heat / coolant -----------------------------------------
const THEME = {
  name: "PMSM Thermal",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1C2127",   // ink
    lt1: "FFFFFF",   // paper
    dk2: "6B7280",   // muted
    lt2: "F1F3F5",   // tint
    accent1: "E8833A",   // heat - the thing we predict
    accent2: "2E9E8F",   // coolant - measurement, "good"
    accent3: "1F4E79",   // deep blue - structure
    accent4: "C0504D",
    accent5: "8064A2",
    accent6: "4BACC6",
    hlink: "1F4E79", folHlink: "6B7280",
  },
};
const HEAT = THEME.colors.accent1, COOL = THEME.colors.accent2;
const IRON = THEME.colors.dk1, MUTED = THEME.colors.dk2;
const PAPER = THEME.colors.lt1, TINT = THEME.colors.lt2, DEEP = THEME.colors.accent3;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = "Lohhith Thakur";
pres.title = "PMSM Thermal Virtual Sensor";
pres.subject = "UCS321 AI for Engineers - MST Mini Project";
const C = pres.SchemeColor;

const FOOT = "UCS321 AI for Engineers  |  PMSM Thermal Virtual Sensor  |  Lohhith Thakur (1025220020)";

// ---- layouts ---------------------------------------------------------------
pres.defineSlideMaster({
  title: "TITLE", background: { color: IRON },
  objects: [
    { rect: { x: 0, y: 0, w: W, h: 0.11, fill: { color: HEAT } } },
    { placeholder: { options: { name: "kicker", type: "body", x: M, y: 1.55, w: W - 2 * M, h: 0.3,
        fontSize: 12.5, bold: true, charSpacing: 2.4, color: HEAT, valign: "middle" }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 1.95, w: W - 2 * M, h: 1.52,
        fontSize: 42, bold: true, color: PAPER, align: "left", valign: "top" }, text: "" } },
    { placeholder: { options: { name: "subtitle", type: "body", x: M, y: 3.42, w: W - 2 * M - 2.4, h: 0.84,
        fontSize: 14.5, color: "C9CFD6", valign: "top", lineSpacing: 21 }, text: "" } },
    { placeholder: { options: { name: "meta", type: "body", x: M, y: 5.88, w: W - 2 * M, h: 1.2,
        fontSize: 12.5, color: "9AA4B0", valign: "top", lineSpacing: 19 }, text: "" } },
  ],
});

pres.defineSlideMaster({
  title: "CONTENT", background: { color: PAPER },
  objects: [
    { rect: { x: 0, y: 0, w: 0.085, h: H, fill: { color: HEAT } } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.38, w: W - 2 * M - 1.1, h: 0.56,
        fontSize: 26, bold: true, color: C.text1, align: "left", valign: "middle" }, text: "" } },
    { placeholder: { options: { name: "sub", type: "body", x: M, y: 0.96, w: W - 2 * M - 1.1, h: 0.40,
        fontSize: 13, italic: true, color: C.text2, valign: "middle" }, text: "" } },
    { text: { text: FOOT, options: { x: M, y: H - 0.42, w: W - 2 * M - 0.9, h: 0.26,
        fontSize: 8.5, color: "AAB2BC", isTextBox: true, margin: 0 } } },
    { placeholder: { options: { name: "num", type: "body", x: W - M - 0.9, y: H - 0.44, w: 0.9, h: 0.28,
        fontSize: 10, bold: true, align: "right", color: DEEP, valign: "middle" }, text: "" } },
  ],
});

pres.defineSlideMaster({
  title: "DARK", background: { color: IRON },
  objects: [
    { rect: { x: 0, y: 0, w: 0.085, h: H, fill: { color: HEAT } } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.38, w: W - 2 * M - 1.1, h: 0.56,
        fontSize: 26, bold: true, color: PAPER, align: "left", valign: "middle" }, text: "" } },
    { placeholder: { options: { name: "sub", type: "body", x: M, y: 0.96, w: W - 2 * M - 1.1, h: 0.40,
        fontSize: 13, italic: true, color: "9AA4B0", valign: "middle" }, text: "" } },
    { text: { text: FOOT, options: { x: M, y: H - 0.42, w: W - 2 * M - 0.9, h: 0.26,
        fontSize: 8.5, color: "5A6472", isTextBox: true, margin: 0 } } },
    { placeholder: { options: { name: "num", type: "body", x: W - M - 0.9, y: H - 0.44, w: 0.9, h: 0.28,
        fontSize: 10, bold: true, align: "right", color: HEAT, valign: "middle" }, text: "" } },
  ],
});

// ---- helpers ---------------------------------------------------------------
let pageNo = 0;
function slide(masterName, sectionTitle, titleText, subText) {
  const s = pres.addSlide({ masterName, sectionTitle });
  pageNo += 1;
  if (titleText) s.addText(titleText, { placeholder: "title" });
  if (subText) s.addText(subText, { placeholder: "sub" });
  s.addText(`${pageNo} / 10`, { placeholder: "num" });
  return s;
}
function img(s, file, o) { s.addImage({ path: FIG + file, ...o, objectName: file.replace(".png", "") }); }

// fit an image inside a box, preserving aspect ratio, centred
const ASPECT = {
  "00_flow_diagram.png": 0.979, "01_thermal_lag.png": 1.158, "02_ewma_motivation.png": 1.734,
  "03_correlation.png": 1.118, "04_dataset_structure.png": 1.863, "05_model_comparison.png": 1.967,
  "06_predicted_vs_actual.png": 1.385, "07_residuals.png": 1.813, "08_feature_importance.png": 1.512,
  "09_ablation_leakage.png": 2.140, "10_split_protocol.png": 1.449, "11_tuning_results.png": 2.160,
  "12_error_analysis.png": 2.081,
};
function fit(s, file, bx, by, bw, bh) {
  const a = ASPECT[file];
  let w = bw, h = bw / a;
  if (h > bh) { h = bh; w = bh * a; }
  img(s, file, { x: bx + (bw - w) / 2, y: by + (bh - h) / 2, w, h });
}
function card(s, x, y, w, h, fill, name) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.07,
    fill: { color: fill }, line: { color: fill, width: 0 }, objectName: name });
}
function statTile(s, x, y, w, value, label, vcolor, dark) {
  card(s, x, y, w, 1.26, dark ? "262D36" : TINT, `tile-${label}`);
  s.addText(value, { x, y: y + 0.13, w, h: 0.58, isTextBox: true, margin: 0, align: "center",
    fontSize: 30, bold: true, color: vcolor, fontFace: THEME.bodyFontFace });
  s.addText(label, { x: x + 0.1, y: y + 0.73, w: w - 0.2, h: 0.44, isTextBox: true, margin: 0,
    align: "center", valign: "top", fontSize: 10, color: dark ? "9AA4B0" : MUTED });
}
function bullets(s, items, o) {
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: { indent: 16 }, breakLine: i < items.length - 1 } })),
    { x: o.x, y: o.y, w: o.w, h: o.h, isTextBox: true, margin: 0, valign: "top",
      fontSize: o.size ?? 13, color: o.color ?? C.text1, paraSpaceAfter: o.gap ?? 7, lineSpacing: o.ls ?? 17 });
}
function caption(s, text, x, y, w) {
  s.addText(text, { x, y, w, h: 0.3, isTextBox: true, margin: 0, align: "center",
    fontSize: 9.5, italic: true, color: MUTED });
}
function note(s, text, x, y, w, h, accent) {
  card(s, x, y, w, h, TINT, "note");
  s.addShape(pres.ShapeType.rect, { x, y, w: 0.055, h, fill: { color: accent || HEAT } });
  s.addText(text, { x: x + 0.22, y: y + 0.08, w: w - 0.42, h: h - 0.16, isTextBox: true, margin: 0,
    valign: "middle", fontSize: 11.5, color: C.text1, lineSpacing: 16 });
}
const TBL = {
  border: { type: "solid", color: "DDE3E9", pt: 0.5 },
  fontSize: 11, color: IRON, valign: "middle", fontFace: THEME.bodyFontFace,
};
function head(t) { return { text: t, options: { bold: true, color: PAPER, fill: { color: DEEP }, fontSize: 10.5 } }; }

// ===========================================================================
// 1 - TITLE
// ===========================================================================
pres.addSection({ title: "Opening" });
{
  const s = pres.addSlide({ masterName: "TITLE", sectionTitle: "Opening" });
  pageNo = 1;
  s.addText("UCS321 - AI FOR ENGINEERS  |  MST MINI PROJECT", { placeholder: "kicker" });
  s.addText("Predicting Electric Motor\nWinding Temperature", { placeholder: "title" });
  s.addText("A physics-driven virtual sensor that estimates PMSM stator winding temperature "
    + "from signals the drive already measures - replacing a thermocouple with software.",
    { placeholder: "subtitle" });
  s.addText([
    { text: "Problem Statement 6", options: { bold: true, color: "C9CFD6", breakLine: true } },
    { text: "GE Power Systems - supervised regression for motor temperature", options: { breakLine: true } },
    { text: "Lohhith Thakur  -  Roll No. 1025220020  -  B.E. Electronics (VLSI Design & Technology)", options: { breakLine: true } },
    { text: "Thapar Institute of Engineering & Technology, Patiala", options: {} },
  ], { placeholder: "meta" });

  // headline stat strip
  const tiles = [["1.54 °C", "RMSE on unseen\nmotor sessions", HEAT],
                 ["0.9965", "coefficient of\ndetermination R2", COOL],
                 ["104", "features engineered\nfrom 8 raw channels", PAPER],
                 ["84.2 %", "of samples within\n±2 °C of truth", PAPER]];
  const tw = 2.56, gap = 0.22, x0 = W - M - (4 * tw + 3 * gap);
  tiles.forEach(([v, l, c], i) => statTile(s, x0 + i * (tw + gap), 4.42, tw, v, l, c, true));
  s.addNotes("Virtual sensor for PMSM winding temperature. Headline: 1.54 degrees C RMSE on two "
    + "entire motor sessions never seen in training. The whole result comes from feature "
    + "engineering grounded in the thermal physics, not from model selection.");
}

// ===========================================================================
// 2 - PROBLEM & OBJECTIVE
// ===========================================================================
pres.addSection({ title: "Problem" });
{
  const s = slide("CONTENT", "Problem", "The problem: you cannot measure what matters",
    "Winding temperature bounds how hard a motor may be driven - and it is the one you cannot cheaply measure");
  bullets(s, [
    "A PMSM fails when its stator winding insulation cooks. Class-H insulation is rated to ~180 °C; insulation life halves for every ~10 °C of sustained overtemperature.",
    "Fitting a thermocouple to a varnished, high-voltage winding means extra wiring through a sealed housing, an extra failure mode, and a cost that does not survive a volume BOM.",
    "Test benches have these sensors. Shipped motors do not - so drives must derate conservatively and give up torque the machine could physically deliver.",
    "Every drive already measures, for free, the eight quantities it needs for field-oriented control.",
  ], { x: M, y: 1.60, w: 6.55, h: 3.30, size: 14, gap: 12, ls: 19 });

  note(s, "Objective  -  estimate stator winding temperature from drive-measurable signals only, "
    + "accurately enough that a controller can use it as a thermal limit instead of a thermocouple.",
    M, 5.02, 6.55, 1.08, HEAT);

  card(s, 7.52, 1.60, W - M - 7.52, 4.50, TINT, "inputs-card");
  s.addText("What the drive already measures", { x: 7.78, y: 1.80, w: 4.6, h: 0.3, isTextBox: true,
    margin: 0, fontSize: 13, bold: true, color: DEEP });
  const rows = [["ambient", "ambient air temperature (°C)"], ["coolant", "coolant outlet temp (°C)"],
                ["u_d , u_q", "terminal voltage, dq frame (V)"], ["i_d , i_q", "phase current, dq frame (A)"],
                ["motor_speed", "rotor speed (rpm)"], ["torque", "shaft torque (N·m)"]];
  rows.forEach(([a, b], i) => {
    const y = 2.28 + i * 0.44;
    s.addText(a, { x: 7.78, y, w: 1.55, h: 0.34, isTextBox: true, margin: 0, fontSize: 11,
      bold: true, color: HEAT, fontFace: "Consolas", valign: "middle" });
    s.addText(b, { x: 9.33, y, w: 3.2, h: 0.34, isTextBox: true, margin: 0, fontSize: 10.5,
      color: C.text2, valign: "middle" });
  });
  s.addShape(pres.ShapeType.line, { x: 7.78, y: 5.14, w: 4.75, h: 0, line: { color: "D5DCE3", width: 1 } });
  s.addText([{ text: "TARGET   ", options: { fontSize: 9.5, bold: true, charSpacing: 1.5, color: MUTED } },
             { text: "stator_winding", options: { fontSize: 12.5, bold: true, color: DEEP, fontFace: "Consolas" } }],
    { x: 7.78, y: 5.32, w: 4.75, h: 0.44, isTextBox: true, margin: 0, valign: "middle" });
  s.addNotes("Average error is the wrong headline for a safety limit: 1 degree mean error with a "
    + "20 degree spike still destroys a motor. That is why we also report max error and the "
    + "fraction of samples within plus-minus 2 degrees.");
}

// ===========================================================================
// 3 - DATASET & EDA
// ===========================================================================
pres.addSection({ title: "Data" });
{
  const s = slide("CONTENT", "Data", "Dataset and exploratory analysis",
    "Electric Motor Temperature (Paderborn University, LEA) - PMSM test-bench telemetry from a dynamometer");

  const tiles = [["1,330,816", "samples", DEEP], ["69", "independent sessions", DEEP],
                 ["2 Hz", "sampling rate", DEEP], ["185 h", "total running time", DEEP],
                 ["0", "missing values", COOL]];
  const tw = 2.33, gap = 0.19;
  tiles.forEach(([v, l, c], i) => statTile(s, M + i * (tw + gap), 1.52, tw, v, l, c, false));

  fit(s, "04_dataset_structure.png", M, 3.00, 6.1, 3.00);
  caption(s, "Target distribution (18.6 - 141.4 °C) and session lengths (18 - 366 min)", M, 6.02, 6.1);

  fit(s, "03_correlation.png", 7.00, 3.00, 5.0, 3.00);
  caption(s, "Correlation of every raw channel with the target", 7.00, 6.02, 5.0);

  note(s, "No raw electrical channel exceeds |r| = 0.63 against the target. That ceiling is a property of "
    + "the representation, not of the information - the physical relationship is not instantaneous.",
    M, 6.42, W - 2 * M, 0.60, COOL);
  s.addNotes("The naive reading of the correlation plot is 'weak signal, hard problem'. The correct "
    + "reading is that the relationship is not instantaneous - which is what the next slide shows.");
}

// ===========================================================================
// 4 - THE CORE INSIGHT
// ===========================================================================
{
  const s = slide("DARK", "Data", "The core insight: thermal inertia",
    "Current changes in seconds, temperature in minutes - the target is a function of history, not of the present sample");

  fit(s, "01_thermal_lag.png", M, 1.52, 5.55, 3.55);
  caption(s, "Electrical excitation and thermal response, same time axis, one session", M, 5.12, 5.55);

  fit(s, "02_ewma_motivation.png", 6.45, 1.52, 6.25, 3.05);
  caption(s, "One transform lifts i_s from r = 0.57 to r = 0.70", 6.45, 4.62, 6.25);

  card(s, 6.45, 5.08, 6.25, 1.72, "262D36", "ode-card");
  s.addShape(pres.ShapeType.rect, { x: 6.45, y: 5.08, w: 0.055, h: 1.72, fill: { color: HEAT } });
  s.addText("A lumped-parameter thermal model is a first-order system:", { x: 6.72, y: 5.18, w: 5.85,
    h: 0.28, isTextBox: true, margin: 0, fontSize: 11, color: "9AA4B0" });
  s.addText("C_th · dϑ/dt  =  P_loss(t)  −  (ϑ − ϑ_amb) / R_th", { x: 6.72, y: 5.46,
    w: 5.85, h: 0.32, isTextBox: true, margin: 0, fontSize: 13, bold: true, color: PAPER, fontFace: "Consolas" });
  s.addText("ϑ(t)  =  (1/τ) ∫ exp(−(t−s)/τ) · P_loss(s) ds", { x: 6.72, y: 5.82,
    w: 5.85, h: 0.32, isTextBox: true, margin: 0, fontSize: 13, bold: true, color: HEAT, fontFace: "Consolas" });
  s.addText("That integral is an exponentially weighted moving average. Computing EWMAs does not "
    + "smooth the data - it hands the model the exact functional form the physics produces.",
    { x: 6.72, y: 6.18, w: 5.85, h: 0.54, isTextBox: true, margin: 0, fontSize: 11, color: "C9CFD6", lineSpacing: 14 });

  bullets(s, [
    "Winding responds in tens of seconds, iron in minutes, housing and coolant in tens of minutes.",
    "So EWMAs are computed at five spans - 30, 120, 600, 1800 and 3600 s - and the model weights them.",
    "Exponentially weighted std at each span encodes how volatile the recent duty cycle has been.",
  ], { x: M, y: 5.50, w: 5.55, h: 1.40, size: 11.5, color: "C9CFD6", gap: 5, ls: 15 });
  s.addNotes("This is the single most important slide. The thermal ODE's solution IS an EWMA, so the "
    + "feature is not a heuristic - it is the analytical form of the physics. This is why even a "
    + "linear model reaches R-squared 0.99 once the features exist.");
}

// ===========================================================================
// 5 - PIPELINE & PROTOCOL
// ===========================================================================
pres.addSection({ title: "Method" });
{
  const s = slide("CONTENT", "Method", "Pipeline and evaluation protocol",
    "Eight raw channels become 104 features; entire measurement sessions are held out for test");

  fit(s, "00_flow_diagram.png", M, 1.50, 4.35, 4.45);
  caption(s, "End-to-end pipeline: pre-processing, feature construction, modelling", M, 5.98, 4.35);

  fit(s, "10_split_protocol.png", 5.30, 1.50, 4.30, 4.45);
  caption(s, "Profile-wise split - whole sessions held out", 5.30, 5.98, 4.30);

  card(s, 9.95, 1.50, W - M - 9.95, 4.45, TINT, "protocol-card");
  s.addText("Why not a random split?", { x: 10.18, y: 1.68, w: 2.5, h: 0.3, isTextBox: true,
    margin: 0, fontSize: 13, bold: true, color: DEEP });
  s.addText("At 2 Hz, rows are 0.5 s apart and near-identical. A random split scatters "
    + "near-duplicates across train and test, so the test set is effectively already inside "
    + "the training set.", { x: 10.18, y: 2.02, w: 2.52, h: 1.3, isTextBox: true, margin: 0,
    fontSize: 10.5, color: C.text1, lineSpacing: 14 });
  const sp = [["Train", "1,211,517", "64 profiles"], ["Validation", "63,904", "profiles 60, 62, 74"],
              ["Test", "55,395", "profiles 65, 72"]];
  sp.forEach(([a, b, c], i) => {
    const y = 3.40 + i * 0.80;
    s.addText(a.toUpperCase(), { x: 10.18, y, w: 2.5, h: 0.22, isTextBox: true, margin: 0,
      fontSize: 8.5, bold: true, charSpacing: 1.2, color: MUTED });
    s.addText(b, { x: 10.18, y: y + 0.20, w: 2.5, h: 0.30, isTextBox: true, margin: 0,
      fontSize: 15, bold: true, color: i === 2 ? HEAT : DEEP });
    s.addText(c, { x: 10.18, y: y + 0.48, w: 2.5, h: 0.24, isTextBox: true, margin: 0,
      fontSize: 9.5, color: C.text2 });
  });
  note(s, "Profiles 65 and 72 are the benchmark sessions used in the published literature on this bench, "
    + "chosen in advance - so the test set cannot have been picked to flatter the result.",
    M, 6.42, W - 2 * M, 0.60, DEEP);
  s.addNotes("Every EWMA is computed within a profile_id group. Letting a recursive filter run across "
    + "a session boundary would import the thermal state of an unrelated recording - silent leakage.");
}

// ===========================================================================
// 6 - FEATURE ENGINEERING: ABLATION + LEAKAGE
// ===========================================================================
{
  const s = slide("CONTENT", "Method", "Where the accuracy actually comes from",
    "Two controlled studies: an ablation over feature families, and a leakage study over split protocols");

  fit(s, "09_ablation_leakage.png", M, 1.48, W - 2 * M, 2.95);

  // ablation table
  s.addText("Ablation - identical LightGBM, progressively richer features", { x: M, y: 4.58,
    w: 6.0, h: 0.26, isTextBox: true, margin: 0, fontSize: 11.5, bold: true, color: DEEP });
  s.addTable([
    [head("Feature set"), head("RMSE (°C)"), head("R2")],
    ["Raw inputs only (8 channels)", "14.39", "0.6942"],
    ["+ instantaneous physical derivations", "14.58", "0.6860"],
    [{ text: "+ EWMA thermal-history features", options: { bold: true } },
     { text: "2.43", options: { bold: true, color: HEAT } },
     { text: "0.9913", options: { bold: true, color: HEAT } }],
  ], { x: M, y: 4.90, w: 6.0, colW: [3.5, 1.3, 1.2], rowH: 0.30, ...TBL });

  // leakage table
  s.addText("Leakage - same model, same features, only the split changes", { x: 6.95, y: 4.58,
    w: 5.8, h: 0.26, isTextBox: true, margin: 0, fontSize: 11.5, bold: true, color: DEEP });
  s.addTable([
    [head("Split protocol"), head("RMSE (°C)"), head("R2")],
    [{ text: "Random 80/20 over rows  (leaky)", options: { color: "B03A2E" } },
     { text: "0.66", options: { color: "B03A2E" } }, { text: "0.9995", options: { color: "B03A2E" } }],
    [{ text: "Profile-wise, whole sessions  (honest)", options: { bold: true } },
     { text: "2.50", options: { bold: true } }, { text: "0.9908", options: { bold: true } }],
    [{ text: "Random splitting understates error by 3.8x", options: { colspan: 3, bold: true, color: PAPER, fill: { color: "B03A2E" }, align: "center", fontSize: 10.5 } }],
  ], { x: 6.95, y: 4.90, w: 5.8, colW: [3.4, 1.25, 1.15], rowH: 0.30, ...TBL });

  note(s, "Instantaneous derivations buy nothing on their own - the entire gain is thermal history. "
    + "8 raw channels become 104 features: 8 raw + 6 physical + (9 channels x 2 statistics x 5 spans = 90).",
    M, 6.46, W - 2 * M, 0.58, COOL);
  s.addNotes("The leakage study is deliberate: 0.9995 is the number most projects on this dataset "
    + "report. We show what it looks like and then report the honest one instead.");
}

// ===========================================================================
// 7 - MODEL COMPARISON
// ===========================================================================
pres.addSection({ title: "Results" });
{
  const s = slide("CONTENT", "Results", "Model development: a ladder of five",
    "From the simplest thing that could work upward - the comparison is the point, not any single number");

  fit(s, "05_model_comparison.png", M, 1.46, 7.05, 3.55);
  caption(s, "RMSE, R2 and max absolute error across the ladder", M, 5.08, 7.05);

  s.addTable([
    [head("Model"), head("RMSE"), head("MAE"), head("R2"), head("MaxAE"), head("±2 °C")],
    ["Linear regression, raw inputs", "17.79", "14.37", "0.5324", "69.27", "8.1 %"],
    ["Ridge regression, + EWMA", "2.08", "1.54", "0.9936", "26.19", "71.7 %"],
    ["Random Forest (80 trees)", "3.60", "2.49", "0.9808", "15.56", "56.8 %"],
    ["MLP (2 x 128), untuned", "1.67", "1.26", "0.9959", "9.84", "81.3 %"],
    ["LightGBM (743 trees)", "2.50", "1.85", "0.9908", "11.05", "65.8 %"],
    [{ text: "MLP tuned  - SELECTED", options: { bold: true, color: PAPER, fill: { color: HEAT } } },
     { text: "1.54", options: { bold: true, color: PAPER, fill: { color: HEAT } } },
     { text: "1.10", options: { bold: true, color: PAPER, fill: { color: HEAT } } },
     { text: "0.9965", options: { bold: true, color: PAPER, fill: { color: HEAT } } },
     { text: "11.32", options: { bold: true, color: PAPER, fill: { color: HEAT } } },
     { text: "84.2 %", options: { bold: true, color: PAPER, fill: { color: HEAT } } }],
    ["HistGradientBoosting, tuned", "2.39", "1.75", "0.9915",
     { text: "9.53", options: { bold: true, color: COOL } }, "65.0 %"],
  ], { x: 7.90, y: 1.46, w: 4.82, colW: [1.66, 0.58, 0.56, 0.66, 0.72, 0.64], rowH: 0.335, ...TBL, fontSize: 9.5 });
  caption(s, "Test set = profiles 65 and 72 (55,395 samples), held out entirely", 7.90, 4.26, 4.82);

  bullets(s, [
    "Linear regression goes from R2 0.53 to 0.99 with no change of algorithm - only features. Feature engineering beat model sophistication.",
    "The MLP beats both tree ensembles. Trees are piecewise-constant and cannot extrapolate past the training envelope; a smooth model continues the trend.",
    "RMSE and max error do not rank the models identically - tuned HistGradientBoosting has the best worst case at 9.53 °C.",
  ], { x: M, y: 5.48, w: W - 2 * M, h: 1.50, size: 12.5, gap: 8 });
  s.addNotes("If worst-case error were the selection criterion - and for a protection function it "
    + "arguably should be - tuned HistGradientBoosting would be the better choice. Selecting on "
    + "RMSE and then disclosing max error is the honest order.");
}

// ===========================================================================
// 8 - FINAL RESULT
// ===========================================================================
{
  const s = slide("DARK", "Results", "Final result on unseen motor sessions",
    "Tuned MLP - two hidden layers of 128, StandardScaler pipeline, early stopping, 104 inputs");

  const tiles = [["1.54 °C", "RMSE", HEAT], ["1.10 °C", "MAE", PAPER], ["0.9965", "R2", COOL],
                 ["11.32 °C", "max abs error", PAPER], ["84.2 %", "within ±2 °C", HEAT]];
  const tw = 2.33, gap = 0.19;
  tiles.forEach(([v, l, c], i) => statTile(s, M + i * (tw + gap), 1.50, tw, v, l, c, true));

  fit(s, "06_predicted_vs_actual.png", M, 2.98, 7.15, 3.55);
  caption(s, "Predicted vs measured on profiles 65 and 72 - sessions the model has never seen", M, 6.56, 7.15);

  fit(s, "07_residuals.png", 8.00, 2.98, 4.72, 2.60);
  caption(s, "Residual distribution and bias check vs temperature", 8.00, 5.60, 4.72);

  s.addText("Residuals are approximately zero-mean and symmetric, with no systematic trend against "
    + "measured temperature - the error is dispersion, not bias.", { x: 8.00, y: 5.94, w: 4.72, h: 0.78,
    isTextBox: true, margin: 0, fontSize: 10.5, color: "9AA4B0", lineSpacing: 14 });
  s.addNotes("7.7 hours of running, 55,395 samples, two complete sessions. The estimate tracks every "
    + "ramp, plateau and cool-down, with visible divergence only in the opening minutes of profile "
    + "72 - the warm-up effect.");
}

// ===========================================================================
// 9 - INTERPRETATION & DIAGNOSTICS
// ===========================================================================
{
  const s = slide("CONTENT", "Results", "Interpretation: what the model learned, and where it errs",
    "Feature importance, the tuning search, and an error breakdown by regime");

  fit(s, "08_feature_importance.png", M, 1.46, 4.05, 2.72);
  caption(s, "LightGBM split counts - top features", M, 4.20, 4.05);

  fit(s, "11_tuning_results.png", 4.85, 1.46, 3.95, 2.72);
  caption(s, "Grouped randomised search, two families", 4.85, 4.20, 3.95);

  fit(s, "12_error_analysis.png", 9.00, 1.46, 3.72, 2.72);
  caption(s, "Error by temperature, load, and time into session", 9.00, 4.20, 3.72);

  card(s, M, 4.58, 4.05, 2.30, TINT, "c1");
  s.addText("The model learned the physics", { x: M + 0.22, y: 4.72, w: 3.6, h: 0.28, isTextBox: true,
    margin: 0, fontSize: 12, bold: true, color: DEEP });
  s.addText("All top-15 features are EWMA-derived. The two strongest are coolant_ewma_600s (2234 "
    + "splits) and i_s_sq_ewma_600s (1935) - exactly the heat-sink boundary condition and the "
    + "copper-loss term the thermal ODE names as dominant.",
    { x: M + 0.22, y: 5.02, valign: "top", w: 3.6, h: 1.70, isTextBox: true, margin: 0, fontSize: 10.5,
      color: C.text1, lineSpacing: 14 });

  card(s, 4.85, 4.58, 3.95, 2.30, TINT, "c2");
  s.addText("Tuning helped the average, not the tail", { x: 5.07, y: 4.72, w: 3.5, h: 0.28,
    isTextBox: true, margin: 0, fontSize: 12, bold: true, color: DEEP });
  s.addText("RMSE improved 8 % and MAE 13 %, but max error rose from 9.84 to 11.32 °C because the "
    + "search optimised RMSE and nothing constrained the tail. Reported, not hidden. CV RMSE (3.04) "
    + "ranks candidates; it does not estimate deployed accuracy.",
    { x: 5.07, y: 5.02, valign: "top", w: 3.5, h: 1.70, isTextBox: true, margin: 0, fontSize: 10.5,
      color: C.text1, lineSpacing: 14 });

  card(s, 9.00, 4.58, W - M - 9.00, 2.30, TINT, "c3");
  s.addText("Where the error lives", { x: 9.22, y: 4.72, w: 3.3, h: 0.28, isTextBox: true,
    margin: 0, fontSize: 12, bold: true, color: DEEP });
  s.addText("Median error holds near 1 °C in every temperature band and every load band - accuracy "
    + "does not decay when the motor is hot. The largest errors sit in the first minutes of a "
    + "session, while the 1800 s and 3600 s filters are still converging from zero.",
    { x: 9.22, y: 5.02, valign: "top", w: 3.3, h: 1.70, isTextBox: true, margin: 0, fontSize: 10.5,
      color: C.text1, lineSpacing: 14 });
  s.addNotes("The feature-importance result is the strongest available evidence that the result is "
    + "not an artefact: the model's most-used features are the two terms a lumped thermal model "
    + "would name.");
}

// ===========================================================================
// 10 - CONCLUSIONS
// ===========================================================================
pres.addSection({ title: "Closing" });
{
  const s = slide("DARK", "Closing", "Conclusions, deployment and limitations",
    "What was achieved, what it would take to ship it, and what this work does not prove");

  card(s, M, 1.52, 6.22, 3.30, "262D36", "concl");
  s.addShape(pres.ShapeType.rect, { x: M, y: 1.52, w: 0.055, h: 3.30, fill: { color: HEAT } });
  s.addText("Conclusions", { x: M + 0.26, y: 1.66, w: 5.7, h: 0.3, isTextBox: true, margin: 0,
    fontSize: 14, bold: true, color: HEAT });
  bullets(s, [
    "Winding temperature is estimable from drive-measurable signals alone to 1.54 °C RMSE and R2 = 0.9965 on unseen sessions.",
    "Feature engineering, not model selection, produced the result - the ablation traces the gain specifically to the EWMA terms.",
    "Evaluation protocol changes the reported number by 3.8x; a result without its protocol is not a result.",
    "A smooth model generalises better than tree ensembles here, because held-out sessions demand extrapolation.",
    "The model learned the intended physics - its dominant features are the coolant boundary condition and the copper-loss term.",
  ], { x: M + 0.26, y: 2.02, w: 5.7, h: 2.70, size: 10.5, color: "D5DCE3", gap: 5, ls: 14 });

  card(s, 7.08, 1.52, W - M - 7.08, 1.56, "262D36", "deploy");
  s.addShape(pres.ShapeType.rect, { x: 7.08, y: 1.52, w: 0.055, h: 1.56, fill: { color: COOL } });
  s.addText("Deployment", { x: 7.34, y: 1.66, w: 5.3, h: 0.3, isTextBox: true, margin: 0,
    fontSize: 14, bold: true, color: COOL });
  s.addText("~30k multiply-accumulates per inference at 2 Hz - negligible for a motor-control MCU. "
    + "Each EWMA is one multiply-add and one register, so all 90 cost 90 registers. A "
    + "hardware-friendly feature extractor is what makes this a thermocouple replacement rather "
    + "than an offline analysis.", { x: 7.34, y: 1.98, w: 5.3, h: 1.0, isTextBox: true, margin: 0,
    fontSize: 10.5, color: "D5DCE3", lineSpacing: 14 });

  card(s, 7.08, 3.26, W - M - 7.08, 1.56, "262D36", "limits");
  s.addShape(pres.ShapeType.rect, { x: 7.08, y: 3.26, w: 0.055, h: 1.56, fill: { color: "C0504D" } });
  s.addText("Limitations", { x: 7.34, y: 3.40, w: 5.3, h: 0.3, isTextBox: true, margin: 0,
    fontSize: 14, bold: true, color: "D98880" });
  s.addText("Worst case is 11.32 °C, so a deployed limit still needs a safety margin. One machine, "
    + "one bench - transfer to other geometries is unproven. Warm-up error while the long filters "
    + "converge. No uncertainty estimate, which a protection function would want.",
    { x: 7.34, y: 3.72, w: 5.3, h: 1.0, isTextBox: true, margin: 0, fontSize: 10.5,
      color: "D5DCE3", lineSpacing: 14 });

  s.addText("Next, in order of value", { x: M, y: 5.08, w: 5.0, h: 0.3, isTextBox: true, margin: 0,
    fontSize: 13, bold: true, color: PAPER });
  const nx = [["Seed EWMA state from the first sample", "removes most of the warm-up error - cheapest win"],
              ["Physics-informed loss on the thermal ODE", "attacks worst-case error specifically"],
              ["Quantile / conformal prediction", "gives the upper bound a protection limit wants"],
              ["Sequence model (temporal CNN / LSTM)", "learns time constants instead of fixing five spans"]];
  const cg = 0.21, cw = (W - 2 * M - 3 * cg) / 4;
  nx.forEach(([a, b], i) => {
    const x = M + i * (cw + cg);
    card(s, x, 5.46, cw, 1.30, "262D36", `nx${i}`);
    s.addText(String(i + 1), { x: x + 0.16, y: 5.58, w: 0.3, h: 0.26, isTextBox: true, margin: 0,
      fontSize: 11, bold: true, color: HEAT });
    s.addText(a, { x: x + 0.16, y: 5.84, w: cw - 0.32, h: 0.46, isTextBox: true, margin: 0,
      fontSize: 10, bold: true, color: PAPER, lineSpacing: 12.5 });
    s.addText(b, { x: x + 0.16, y: 6.30, w: cw - 0.32, h: 0.38, isTextBox: true, margin: 0,
      fontSize: 9, color: "9AA4B0", lineSpacing: 11.5 });
  });
  s.addNotes("Close on the two sentences worth remembering: the result came from understanding the "
    + "physics rather than trying models, and the evaluation protocol changes the headline by 3.8x.");
}

(async () => {
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("deck written:", OUT, (fs.statSync(OUT).size / 1024 / 1024).toFixed(1), "MB");
})();
