const fs = require("fs");
const d = require("docx");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, PageBreak,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, ImageRun,
  TableOfContents, Header, Footer, PageNumber, LevelFormat, convertInchesToTwip
} = d;

const path = require("path");
const ROOT = path.resolve(__dirname, "..");
const FIG = path.join(ROOT, "figures");
const OUT = path.join(ROOT, "reports", "UCS321_Report.docx");
const ACCENT = "1F4E79", INK = "1A1A1A", MUTED = "595959", RULE = "BFBFBF";
const PAGE_W = 12240, MARGIN = 1080;          // US Letter, 0.75in margins
const CONTENT_W = PAGE_W - 2 * MARGIN;        // 10080 dxa = 7in

// ---------- helpers ----------
const P = (text, o = {}) => new Paragraph({
  alignment: o.align, spacing: { before: o.before ?? 0, after: o.after ?? 140, line: o.line ?? 276 },
  indent: o.indent, border: o.border, shading: o.shading,
  children: [new TextRun({ text, size: o.size ?? 21, color: o.color ?? INK,
    bold: o.bold, italics: o.italics, font: o.font ?? "Calibri" })],
});

// rich paragraph: array of [text, opts]
const RP = (runs, o = {}) => new Paragraph({
  alignment: o.align, spacing: { before: o.before ?? 0, after: o.after ?? 140, line: o.line ?? 276 },
  indent: o.indent, shading: o.shading, border: o.border,
  children: runs.map(([t, ro = {}]) => new TextRun({
    text: t, size: ro.size ?? o.size ?? 21, color: ro.color ?? o.color ?? INK,
    bold: ro.bold, italics: ro.italics, font: ro.font ?? "Calibri" })),
});

const H1 = (t) => new Paragraph({
  heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 160 },
  children: [new TextRun({ text: t, size: 30, bold: true, color: ACCENT, font: "Calibri" })],
});
const H2 = (t) => new Paragraph({
  heading: HeadingLevel.HEADING_2, spacing: { before: 260, after: 120 },
  children: [new TextRun({ text: t, size: 24, bold: true, color: INK, font: "Calibri" })],
});

const BULLET = (t, lvl = 0) => new Paragraph({
  numbering: { reference: "bullets", level: lvl },
  spacing: { after: 90, line: 276 },
  children: [new TextRun({ text: t, size: 21, font: "Calibri" })],
});
const BULLETR = (runs, lvl = 0) => new Paragraph({
  numbering: { reference: "bullets", level: lvl },
  spacing: { after: 90, line: 276 },
  children: runs.map(([t, ro = {}]) => new TextRun({ text: t, size: 21, font: "Calibri", ...ro })),
});
// `instance` restarts the numbering — each distinct list needs its own.
const NUM = (t, instance = 0) => new Paragraph({
  numbering: { reference: "nums", level: 0, instance }, spacing: { after: 90, line: 276 },
  children: [new TextRun({ text: t, size: 21, font: "Calibri" })],
});
const NUMR = (runs, instance = 0) => new Paragraph({
  numbering: { reference: "nums", level: 0, instance }, spacing: { after: 90, line: 276 },
  children: runs.map(([t, ro = {}]) => new TextRun({ text: t, size: 21, font: "Calibri", ...ro })),
});

// figure with caption; widthIn inches
function figure(file, widthIn, caption) {
  const sizeOf = require("child_process").execSync(
    `python3 -c "from PIL import Image;im=Image.open('${FIG}/${file}');print(im.size[0],im.size[1])"`
  ).toString().trim().split(" ").map(Number);
  const w = widthIn * 96, h = Math.round(w * sizeOf[1] / sizeOf[0]);
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { before: 160, after: 60 },
      children: [new ImageRun({ type: "png", data: fs.readFileSync(`${FIG}/${file}`),
        transformation: { width: w, height: h } })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 220 },
      children: [new TextRun({ text: caption, size: 18, italics: true, color: MUTED, font: "Calibri" })],
    }),
  ];
}

// table: header row + body rows; widths array must sum to CONTENT_W
function table(widths, header, rows, opts = {}) {
  const cell = (txt, o = {}) => new TableCell({
    width: { size: o.w, type: WidthType.DXA },
    shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: "auto" } : undefined,
    margins: { top: 70, bottom: 70, left: 110, right: 110 },
    children: [new Paragraph({
      alignment: o.align, spacing: { after: 0, line: 250 },
      children: [new TextRun({ text: String(txt), size: o.size ?? 19, bold: o.bold,
        color: o.color ?? INK, font: "Calibri" })],
    })],
  });
  const headRow = new TableRow({
    tableHeader: true,
    children: header.map((h, i) => cell(h, { w: widths[i], bold: true, fill: ACCENT,
      color: "FFFFFF", align: i === 0 ? undefined : AlignmentType.CENTER })),
  });
  const bodyRows = rows.map((r, ri) => new TableRow({
    children: r.map((c, i) => {
      const isBoldRow = opts.boldRows && opts.boldRows.includes(ri);
      return cell(c, { w: widths[i], bold: isBoldRow,
        fill: isBoldRow ? "E8F0F8" : (ri % 2 ? "F5F7FA" : undefined),
        align: i === 0 ? undefined : AlignmentType.CENTER });
    }),
  }));
  return new Table({
    columnWidths: widths, width: { size: CONTENT_W, type: WidthType.DXA },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: RULE },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: RULE },
      left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: "E3E3E3" },
      insideVertical: { style: BorderStyle.NONE },
    },
    rows: [headRow, ...bodyRows],
  });
}
const TCAP = (t) => new Paragraph({
  spacing: { before: 70, after: 240 },
  children: [new TextRun({ text: t, size: 18, italics: true, color: MUTED, font: "Calibri" })],
});

const CALLOUT = (title, body) => [
  new Paragraph({
    spacing: { before: 180, after: 0 }, indent: { left: 170, right: 170 },
    shading: { type: ShadingType.CLEAR, fill: "EAF1F8", color: "auto" },
    border: { left: { style: BorderStyle.SINGLE, size: 18, color: ACCENT, space: 8 } },
    children: [new TextRun({ text: title, size: 20, bold: true, color: ACCENT, font: "Calibri" })],
  }),
  new Paragraph({
    spacing: { before: 40, after: 200, line: 276 }, indent: { left: 170, right: 170 },
    shading: { type: ShadingType.CLEAR, fill: "EAF1F8", color: "auto" },
    border: { left: { style: BorderStyle.SINGLE, size: 18, color: ACCENT, space: 8 } },
    children: [new TextRun({ text: body, size: 20, color: INK, font: "Calibri" })],
  }),
];

const EQ = (t) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 120, after: 160 },
  children: [new TextRun({ text: t, size: 22, italics: true, font: "Cambria", color: INK })],
});

// ================= DOCUMENT =================
const children = [];

// ---------- TITLE PAGE ----------
children.push(
  new Paragraph({ spacing: { before: 1400, after: 0 }, alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "THAPAR INSTITUTE OF ENGINEERING & TECHNOLOGY, PATIALA",
      size: 22, bold: true, color: MUTED, font: "Calibri" })] }),
  new Paragraph({ spacing: { before: 60, after: 700 }, alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Department of Electronics & Communication Engineering",
      size: 20, color: MUTED, font: "Calibri" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 },
    children: [new TextRun({ text: "UCS321 — Artificial Intelligence for Engineers",
      size: 24, color: ACCENT, bold: true, font: "Calibri" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 420 },
    children: [new TextRun({ text: "Mid-Semester Mini Project", size: 21, color: MUTED, font: "Calibri" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 90 },
    children: [new TextRun({ text: "Machine Learning Estimation of Stator Winding",
      size: 40, bold: true, color: INK, font: "Calibri" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 },
    children: [new TextRun({ text: "Temperature in Permanent-Magnet Synchronous Motors",
      size: 40, bold: true, color: INK, font: "Calibri" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 700 },
    border: { top: { style: BorderStyle.SINGLE, size: 8, color: ACCENT, space: 14 } },
    children: [new TextRun({ text: "Problem Statement 6 — General Electric (GE) Power Systems",
      size: 22, italics: true, color: MUTED, font: "Calibri" })] }),
);

children.push(
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
    children: [new TextRun({ text: "Submitted by", size: 20, color: MUTED, font: "Calibri" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 },
    children: [new TextRun({ text: "Lohhith Thakur — 1025220020", size: 22, bold: true, font: "Calibri" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 },
    children: [new TextRun({ text: "[ Group member 2 — Roll No. ]", size: 22, color: "A6A6A6", font: "Calibri" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 },
    children: [new TextRun({ text: "[ Group member 3 — Roll No. ]", size: 22, color: "A6A6A6", font: "Calibri" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 },
    children: [new TextRun({ text: "[ Group member 4 — Roll No. ]", size: 22, color: "A6A6A6", font: "Calibri" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 },
    children: [new TextRun({ text: "[ Group member 5 — Roll No. ]", size: 22, color: "A6A6A6", font: "Calibri" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "B.E. Electronics Engineering (VLSI Design & Technology)",
      size: 20, color: MUTED, font: "Calibri" }), new PageBreak()] }),
);

// ---------- ABSTRACT + TOC ----------
children.push(H1("Abstract"));
children.push(P("The stator winding is the thermally limiting component of a permanent-magnet synchronous motor (PMSM): sustained operation above the insulation class rating degrades the winding varnish and ends in a turn-to-turn short. Direct measurement requires a thermocouple bonded to a high-voltage winding inside a sealed housing, which is practical on a test bench but not on a volume production motor. This project develops a supervised regression model that estimates stator winding temperature from signals a motor drive already measures for field-oriented control, thereby replacing the sensor with a software estimator.", { after: 160 }));
children.push(P("A 1,330,816-sample telemetry dataset from a PMSM dynamometer test bench (69 independent sessions, 185 hours, 2 Hz) was used. Three co-located thermocouple channels were deliberately discarded as target leakage, leaving eight drive-measurable inputs. Because a motor's lumped-parameter thermal response is a first-order system whose analytical solution is an exponentially weighted integral of past losses, the eight raw channels were expanded to 104 features comprising physically-motivated derivations and exponentially weighted moving averages at five thermal time constants. Five models were compared under a profile-wise split that holds out entire measurement sessions, and the two strongest were then tuned by randomised search under grouped cross-validation.", { after: 160 }));
children.push(RP([
  ["The selected multilayer perceptron achieves ", {}],
  ["RMSE 1.54 °C, R² = 0.9965, and a maximum absolute error of 11.32 °C", { bold: true }],
  [" on motor sessions never seen during training, with 84.2 % of samples within ±2 °C. Two controlled studies support the result: an ablation showing the accuracy originates specifically from the thermal-history features rather than from feature count, and a leakage study showing that the conventional random train-test split overstates accuracy by a factor of approximately four on data of this kind.", {}],
], { after: 300 }));

children.push(H1("Table of Contents"));
children.push(P("In Word, right-click the field below and choose \u201cUpdate Field\u201d to populate the contents.", { italics: true, color: MUTED, size: 18, after: 120 }));
children.push(new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-2" }));
children.push(new Paragraph({ children: [new PageBreak()] }));

// ---------- 1. PROBLEM ----------
children.push(H1("1. Problem Understanding and Objectives"));
children.push(H2("1.1 Engineering context"));
children.push(P("A permanent-magnet synchronous motor converts electrical power to mechanical power with high efficiency, but the fraction that is not converted appears as heat, predominantly as ohmic loss in the stator copper. That heat raises the winding temperature, and the winding's enamel insulation has a finite thermal rating — Class H insulation, common in industrial machines, is rated to approximately 180 °C. Operation above that limit does not cause immediate failure; it accelerates chemical degradation of the enamel, and the accepted engineering rule of thumb is that insulation life roughly halves for every 10 °C of sustained overtemperature. Eventually the enamel fails between adjacent turns and the machine is destroyed."));
children.push(P("Winding temperature is therefore the binding constraint on how hard a drive may push a motor. A controller that knows this temperature accurately can exploit the machine's full short-term overload capability; a controller that does not must apply a fixed conservative derating and give up torque that the machine could physically have delivered."));

children.push(H2("1.2 The problem: the measurement is impractical in production"));
children.push(P("The obvious solution — instrument the winding — is available on a test bench and unavailable in a product. A thermocouple or thermistor bonded to the winding must survive the winding's potential, its vibration, and its thermal cycling; its leads must be routed out through the housing without compromising the seal; and it introduces an additional failure mode into an otherwise robust machine. The combined cost and reliability penalty does not survive contact with a volume bill of materials."));
children.push(P("What a drive does have, at no marginal cost, is the set of quantities it already measures to perform field-oriented control:"));
children.push(BULLET("Phase currents, resolved in the rotor reference frame as i_d and i_q"));
children.push(BULLET("Terminal voltages, resolved as u_d and u_q"));
children.push(BULLET("Rotor speed, from the position sensor or an observer"));
children.push(BULLET("Shaft torque, either measured or estimated from current"));
children.push(BULLET("Coolant and ambient temperature, from inexpensive external sensors"));

children.push(H2("1.3 Objective"));
children.push(...CALLOUT("Project objective",
  "Estimate stator winding temperature from signals the motor drive already measures, with sufficient accuracy that a controller can use the estimate as a thermal protection limit in place of a physical winding sensor."));
children.push(P("This is a virtual sensor, or soft sensor, problem. Its defining characteristic — and the reason it is more interesting than a generic regression exercise — is that the definition of success is set by the deployment context rather than by a leaderboard metric."));

children.push(H2("1.4 Choosing the right success criterion"));
children.push(P("Mean-error metrics are the wrong headline for a safety limit. A model with 1 °C mean absolute error and an occasional 20 °C underestimate will still destroy a motor, because the failure occurs at the worst case, not at the average. Accordingly this project reports, alongside the conventional regression metrics:"));
children.push(BULLETR([["Maximum absolute error", { bold: true }], [" — the largest single-sample deviation over the entire held-out set. This is the quantity a protection engineer would use to size the safety margin below the insulation rating.", {}]]));
children.push(BULLETR([["Percentage of samples within ±2 °C", { bold: true }], [" — a deployability measure: the fraction of operating time for which the estimate is good enough to act on directly.", {}]]));
children.push(P("These two metrics do not rank the candidate models identically to RMSE, which is itself an instructive result and is discussed in Section 6.3."));

children.push(new Paragraph({ children: [new PageBreak()] }));

// ---------- 2. DATASET ----------
children.push(H1("2. Dataset"));
children.push(H2("2.1 Source and structure"));
children.push(P("The dataset is the Electric Motor Temperature collection recorded by the Department of Power Electronics and Electrical Drives (LEA) at Paderborn University, obtained from Kaggle as the file measures_v2.csv. It consists of telemetry from a three-phase permanent-magnet synchronous motor mounted on a dynamometer test bench and driven through a wide range of speed and load conditions under controlled excitation profiles."));
children.push(table([3400, 3340, 3340],
  ["Property", "Value", "Implication"],
  [
    ["Total samples", "1,330,816", "Ample for high-capacity models"],
    ["Sampling rate", "2 Hz (0.5 s)", "Adjacent samples nearly identical"],
    ["Independent sessions", "69", "The natural unit for splitting"],
    ["Total duration", "≈ 185 hours", "Covers many thermal cycles"],
    ["Raw channels", "13", "8 usable as inputs (Section 3.1)"],
    ["Missing values", "0", "No imputation required"],
    ["Target range", "18.6 – 141.4 °C", "Spans ambient to near-rated"],
  ]));
children.push(TCAP("Table 1 — Dataset summary. Each session (profile_id) is one continuous recording with its own excitation schedule."));

children.push(H2("2.2 Channel description"));
children.push(table([2300, 4500, 3280],
  ["Channel", "Physical meaning", "Role"],
  [
    ["ambient", "Ambient air temperature (°C)", "Input"],
    ["coolant", "Coolant outlet temperature (°C)", "Input"],
    ["u_d, u_q", "Terminal voltage, rotor dq frame (V)", "Input"],
    ["i_d, i_q", "Phase current, rotor dq frame (A)", "Input"],
    ["motor_speed", "Rotor speed (rpm)", "Input"],
    ["torque", "Shaft torque (N·m)", "Input"],
    ["stator_winding", "Winding temperature (°C)", "TARGET"],
    ["stator_tooth", "Stator tooth temperature (°C)", "Discarded — leakage"],
    ["stator_yoke", "Stator yoke temperature (°C)", "Discarded — leakage"],
    ["pm", "Permanent magnet temperature (°C)", "Discarded — leakage"],
    ["profile_id", "Measurement session identifier", "Grouping key"],
  ], { boldRows: [6] }));
children.push(TCAP("Table 2 — Channel inventory and the role assigned to each in this project."));

children.push(...figure("04_dataset_structure.png", 6.6,
  "Figure 1 — Dataset structure. Left: the target spans the full range from ambient to near-rated temperature, with no degenerate concentration. Right: session lengths vary from 18 to 366 minutes, which motivates grouping by session rather than by sample."));



// ---------- 3. METHODOLOGY ----------
children.push(H1("3. Methodology"));
children.push(P("The complete processing pipeline is given in Figure 2. Each stage is described in the subsections that follow."));
children.push(...figure("00_flow_diagram.png", 5.7,
  "Figure 2 — Processing pipeline, with the visualisation produced at each stage noted alongside."));



children.push(H2("3.1 Pre-processing: removing the leaking channels"));
children.push(P("The dataset contains three additional thermocouple readings — stator_tooth, stator_yoke, and pm — that correlate with the target at r > 0.95. Including them as inputs yields a spectacular coefficient of determination. All three were nevertheless discarded, for two distinct reasons, both of which matter."));
children.push(NUMR([["It defeats the stated objective. ", { bold: true }], ["Those sensors are precisely the hardware the virtual sensor is intended to replace. A model that requires stator_tooth in order to predict stator_winding cannot be deployed on a motor that has neither, so its accuracy is irrelevant to the problem being solved.", {}]], 1));
children.push(NUMR([["It constitutes target leakage. ", { bold: true }], ["The tooth and yoke thermocouples sit millimetres from the winding within the same laminated iron structure and share its thermal mass. A model using them is interpolating between adjacent thermocouples, not learning the relationship between electrical excitation and thermal response. The apparent accuracy would not transfer to any machine other than this instrumented one.", {}]], 1));
children.push(P("The coolant and ambient channels were retained. These are inexpensive external sensors already fitted to any liquid-cooled industrial drive, so including them is consistent with the deployment constraint. After this step, eight input channels remain."));

children.push(H2("3.2 Data quality verification"));
children.push(P("The dataset contains no missing values and no duplicated rows, so pre-processing is concerned with structure rather than repair. The one property that must be verified is that each profile_id corresponds to a single contiguous recording session, because every feature constructed in Section 3.3 is computed within session boundaries and would be invalid otherwise. All 69 sessions were confirmed continuous. All channels were downcast to 32-bit floating point, which halves memory consumption to approximately 570 MB for the full engineered matrix and permits the entire dataset to be held in memory."));

children.push(H2("3.3 Feature engineering"));
children.push(P("This stage is where the project's accuracy is determined, and it is derived from the physics rather than from trial and error."));

children.push(new Paragraph({ spacing: { before: 180, after: 100 },
  children: [new TextRun({ text: "3.3.1  Physically-motivated derived quantities", size: 21, bold: true, font: "Calibri" })] }));
children.push(P("The dq-frame components are convenient for control but are not individually thermally meaningful. What heats a winding is ohmic loss, P_cu = 3 I² R, which depends on current magnitude and does so quadratically. The model is therefore given the magnitude and its square directly rather than being asked to discover the square law from the orthogonal components:"));
children.push(EQ("i_s = √(i_d² + i_q²)        u_s = √(u_d² + u_q²)        S_el = 1.5 · i_s · u_s"));
children.push(EQ("P_mech = (2π/60) · τ · n        P_loss ≈ S_el − |P_mech|"));
children.push(P("where τ is shaft torque and n is rotor speed. The quantity P_loss is a coarse proxy for total loss: apparent electrical power in, less mechanical power out."));

children.push(new Paragraph({ spacing: { before: 200, after: 100 },
  children: [new TextRun({ text: "3.3.2  Exponentially weighted moving averages: the thermal memory", size: 21, bold: true, font: "Calibri" })] }));
children.push(P("The central modelling insight comes from the lumped-parameter thermal model of the machine. Treating the winding as a single thermal mass with capacitance C_th coupled to ambient through resistance R_th, the governing equation is a first-order ordinary differential equation:"));
children.push(EQ("C_th · dϑ/dt = P_loss(t) − (ϑ − ϑ_amb) / R_th"));
children.push(P("whose solution, with thermal time constant τ_th = R_th · C_th, is"));
children.push(EQ("ϑ(t) = (1/τ_th) ∫ exp(−(t − s)/τ_th) · P_loss(s) ds"));
children.push(P("The winding temperature is an exponentially weighted integral of past losses. The discrete-time realisation of exactly that integral is an exponentially weighted moving average:"));
children.push(EQ("y[k] = α · x[k] + (1 − α) · y[k−1]"));
children.push(...CALLOUT("Why this matters",
  "Computing EWMAs of the loss-related signals is not merely smoothing the data. It supplies the model with the exact functional form the physics produces, which is why even an ordinary linear regression becomes accurate once these features are present (Section 5.2)."));
children.push(P("A real machine is not a single thermal mass. The copper winding responds in tens of seconds, the laminated iron in minutes, and the housing and coolant circuit over tens of minutes. Rather than identifying these time constants explicitly, EWMAs were computed at five spans spanning the plausible range — 30 s, 120 s, 600 s, 1800 s and 3600 s — and the model was left to weight them. The exponentially weighted standard deviation was computed at each span as well, encoding how volatile the recent duty cycle has been."));
children.push(P("Nine signals were filtered in this way: i_s, u_s, S_el, i_s², P_loss, motor_speed, torque, coolant and ambient. With five spans and two statistics each, this yields 90 thermal features; with the six physical derivations and the eight raw channels, the final matrix contains 104 features."));
children.push(...CALLOUT("Implementation detail that is easy to get wrong",
  "Every EWMA is computed within a profile_id group. Sessions are separate experiments performed at different times; allowing the recursive filter to run across a session boundary would import the thermal state of an unrelated recording into the first minutes of the next, which is a subtle but genuine form of leakage."));

children.push(H2("3.4 Train–test split protocol"));
children.push(P("The conventional approach — a random split of rows into 80 % training and 20 % test — produces a meaningless result on this dataset, and the reason is worth stating explicitly."));
children.push(P("Samples are spaced 0.5 seconds apart. A motor's winding temperature cannot change appreciably in half a second, so consecutive rows are near-duplicates of one another. A random split therefore distributes near-identical samples across both sides of the partition, and the test set is effectively contained within the training set. The model is rewarded for memorisation, and the reported metric measures nothing about generalisation."));
children.push(P("The protocol adopted here holds out entire measurement sessions. The model is evaluated the way it would actually be used: on a motor run it has never observed. Profiles 65 and 72 form the test set, following the benchmark convention used in the published literature on this test bench; three further profiles (60, 62, 74) form a validation set used for early stopping; the remaining 64 profiles are used for training."));
children.push(table([4000, 2500, 3580],
  ["Partition", "Profiles", "Samples"],
  [["Training", "64", "1,211,517"], ["Validation", "60, 62, 74", "63,904"], ["Test (held out)", "65, 72", "55,395"]]));
children.push(TCAP("Table 3 — Profile-wise partition. No sample from a test session appears in training in any form."));
children.push(...figure("10_split_protocol.png", 6.6,
  "Figure 3 — The partition made concrete. Each bar is one recording session, spanning the winding temperatures it reached; the three validation and two test sessions are held out whole."));
children.push(P("The magnitude of the difference this makes is quantified experimentally in Section 7.2."));



// ---------- 4. EDA ----------
children.push(H1("4. Exploratory Data Analysis"));
children.push(H2("4.1 Thermal inertia: the dominant physical fact"));
children.push(P("Figure 4 plots the electrical excitation and the thermal response of a single session on a common time axis. Reading the lower panel against the middle one establishes the entire character of the problem."));
children.push(...figure("01_thermal_lag.png", 6.5,
  "Figure 4 — Electrical excitation versus thermal response, profile 20. Motor speed and current change in seconds; winding temperature responds over minutes and continues to rise after the current has stepped down."));
children.push(P("Current steps change within a single sample interval. Winding temperature takes several minutes to reach its new equilibrium, and continues rising for some time after the excitation has already been reduced. A model presented only with instantaneous values is being asked to infer the value of a state variable from its input — which, for a system with memory, is not possible in principle rather than merely difficult in practice."));

children.push(H2("4.2 Correlation of raw signals with the target"));
children.push(...figure("03_correlation.png", 5.4,
  "Figure 5 — Pearson correlation between raw and instantaneously-derived signals and the target."));
children.push(P("No raw electrical channel exceeds |r| = 0.63 against the target; the strongest is i_d at 0.624, followed by apparent power at 0.599. This ceiling is not a data quality problem. It is the thermal inertia of Figure 4 expressed numerically, and it establishes that feature engineering rather than model selection is the lever that will move the result."));

children.push(H2("4.3 Evidence that the EWMA transform works"));
children.push(...figure("02_ewma_motivation.png", 6.6,
  "Figure 6 — Instantaneous current magnitude (left) and its 600-second exponentially weighted average (right), each plotted against winding temperature. A single transform raises the correlation from 0.57 to 0.70 and converts a diffuse cloud into a structured relationship."));
children.push(P("The left panel shows why the raw signal is a weak predictor: at any given instantaneous current the winding may be at almost any temperature, because the temperature depends on how long that current has been flowing. The right panel shows the same data after the current has been passed through a ten-minute exponential filter. The scatter resolves into a coherent band. This is a single feature, examined in isolation, before any model has been fitted."));



// ---------- 5. MODELS ----------
children.push(H1("5. Model Development"));
children.push(H2("5.1 Design of the comparison"));
children.push(P("Five models were trained, arranged as a ladder from the simplest arrangement that could plausibly work to the most flexible, so that every increase in complexity is required to justify itself against the preceding rung."));
children.push(table([2900, 4200, 2980],
  ["Model", "Configuration", "Purpose in the ladder"],
  [
    ["Linear regression", "Ordinary least squares, 8 raw inputs", "Honest floor — no feature engineering"],
    ["Ridge regression", "α = 1.0, 104 engineered features", "Isolates the value of Section 3.3"],
    ["Random Forest", "80 trees, depth 16, leaf ≥ 20", "Non-parametric reference"],
    ["MLP", "2 × 128 units, early stopping", "Smooth function approximator"],
    ["LightGBM", "743 trees, lr 0.06, 96 leaves", "Strong tabular baseline"],
  ]));
children.push(TCAP("Table 4 — The model ladder. All inputs were standardised for the linear and neural models; tree models are scale-invariant and were fitted on raw feature values."));
children.push(P("All models were fitted on the same training partition and evaluated on the same held-out sessions. LightGBM was early-stopped against the validation profiles, terminating at 743 of a maximum 900 trees. The Random Forest and MLP were fitted on every tenth training sample; because the data is heavily autocorrelated at 2 Hz, this subsampling reduces computation by an order of magnitude at negligible information cost."));

children.push(H2("5.2 The central result of the project"));
children.push(P("Before the full comparison, one pair of rows deserves separate attention, because it constitutes the project's main finding:"));
children.push(table([5000, 1700, 1700, 1680],
  ["Model", "RMSE (°C)", "R²", "Within ±2 °C"],
  [
    ["Linear regression, 8 raw inputs", "17.79", "0.5324", "8.1 %"],
    ["Linear regression, + engineered features", "2.08", "0.9936", "71.7 %"],
  ], { boldRows: [1] }));
children.push(TCAP("Table 5 — The effect of feature engineering in isolation."));
children.push(...CALLOUT("Main finding",
  "The algorithm is identical. The data is identical. The training procedure is identical. RMSE falls from 17.79 °C to 2.08 °C and R² rises from 0.53 to 0.99 solely because the inputs now encode thermal history. Domain-informed feature engineering outperformed every increase in model sophistication attempted in this project."));



// ---------- 6. RESULTS ----------
children.push(H1("6. Results and Performance Evaluation"));
children.push(H2("6.1 Quantitative comparison"));
children.push(table([3500, 1500, 1400, 1300, 1300, 1080],
  ["Model", "RMSE (°C)", "MAE (°C)", "R²", "Max err", "±2 °C"],
  [
    ["Linear (raw inputs only)", "17.79", "14.37", "0.5324", "69.27", "8.1 %"],
    ["Ridge (+ engineered features)", "2.08", "1.54", "0.9936", "26.19", "71.7 %"],
    ["Random Forest (80 trees)", "3.60", "2.49", "0.9808", "15.56", "56.8 %"],
    ["MLP (2 × 128)", "1.67", "1.26", "0.9959", "9.84", "81.3 %"],
    ["LightGBM (743 trees)", "2.50", "1.85", "0.9908", "11.05", "65.8 %"],
  ], { boldRows: [3] }));
children.push(TCAP("Table 6 — Full model comparison on the held-out sessions (profiles 65 and 72, 55,395 samples). Best values in bold."));
children.push(...figure("05_model_comparison.png", 6.8,
  "Figure 7 — Model comparison across three metrics. Note that the three panels do not order the models identically."));

children.push(H2("6.2 Tracking performance on unseen sessions"));
children.push(...figure("06_predicted_vs_actual.png", 6.5,
  "Figure 8 — Selected model (MLP) predicted against measured winding temperature on the two held-out sessions. Neither session was seen in any form during training."));
children.push(P("The estimate tracks both the rapid transients during aggressive load cycling and the slow exponential decay during cool-down. The largest deviations occur at sharp transitions, where the estimate lags the measurement by a few seconds — the expected signature of a filter-based feature set encountering a step change faster than its shortest time constant."));

children.push(H2("6.3 Interpretation: three results worth explaining"));
children.push(NUMR([["The neural network outperforms both tree ensembles. ", { bold: true }], ["This is not an artefact. Tree ensembles are piecewise-constant functions: a prediction is the mean of the training samples in a leaf, so the model cannot produce a value outside the range it observed during training. The held-out sessions contain operating points the 64 training profiles never visit, and at those points a tree ensemble can only clamp to the nearest leaf it has. A multilayer perceptron is a smooth function and continues the trend. For a continuous physical system evaluated under genuine extrapolation, smoothness is the decisive property.", {}]], 2));
children.push(NUMR([["Ridge regression outperforms LightGBM. ", { bold: true }], ["Once the features encode the thermal physics, the residual relationship between features and target is close to linear. A low-variance estimator then generalises across sessions better than a high-capacity one, which fits session-specific structure that does not transfer.", {}]], 2));
children.push(NUMR([["RMSE and maximum error do not rank the models identically. ", { bold: true }], ["Ridge regression attains an RMSE of 2.08 °C — better than LightGBM's 2.50 °C — yet its worst-case error is 26.19 °C against LightGBM's 11.05 °C. For a thermal protection function the second column is the one that governs, and a model selected on RMSE alone would have been the wrong choice.", {}]], 2));

children.push(H2("6.4 Residual analysis"));
children.push(...figure("07_residuals.png", 6.6,
  "Figure 9 — Residual distribution (left) and residual against measured temperature (right) for the selected model."));
children.push(...figure("12_error_analysis.png", 6.8,
  "Figure 10 — Error broken down by operating temperature, by load, and by time into the session."));
children.push(P("Median error stays near 1 °C in every temperature band and every load band, so accuracy does not collapse when the machine is hot or heavily loaded. The clearest structure is in the third panel: the largest errors sit in the first minutes of a session, while the 1800 s and 3600 s filters are still converging from their initial state. That warm-up cost is intrinsic to a recursive feature set and is the model's most addressable remaining weakness."));
children.push(P("The residual distribution is approximately symmetric about a small, indicating no systematic bias in either direction. The right panel is the more important check: it confirms that error does not grow with operating temperature. A model that were accurate when cool and inaccurate when hot would be useless for thermal protection, since the hot regime is the only one in which the estimate is consulted. No such degradation is present."));



// ---------- 7. VALIDATION ----------
children.push(H1("7. Hyperparameter Tuning"));
children.push(P("The ladder in Section 5 used fixed, sensible configurations. The two strongest families were then tuned properly, with one methodological constraint that matters more than the search itself."));
children.push(...CALLOUT("Grouped cross-validation is not optional here",
  "The search uses GroupKFold with profile_id as the grouping key, so a candidate configuration is never scored on a session it was fitted on. A plain KFold inside the search would reintroduce exactly the leakage that Section 3.4 removes from the outer split — and it would do so invisibly, because the reported CV score would simply look better."));
children.push(P("Each search ran on every tenth training sample; the winning configuration was then refitted on the full training partition before being scored on the held-out sessions."));
children.push(table([3100, 2300, 1700, 1500, 1480],
  ["Model", "Search space", "Candidates", "Best CV RMSE", "Search time"],
  [
    ["MLP", "hidden sizes, alpha, learning rate", "8", "3.04 °C", "6.9 min"],
    ["HistGradientBoosting", "iterations, learning rate, leaves, leaf size, L2", "10", "4.02 °C", "11.8 min"],
  ]));
children.push(TCAP("Table 7 — Search configuration. Both searches used 3 grouped folds."));
children.push(P("The selected parameters were hidden_layer_sizes = (128, 128), alpha = 0.01 and learning_rate_init = 0.001 for the MLP; and max_iter = 500, learning_rate = 0.03, max_leaf_nodes = 31, min_samples_leaf = 20 and l2_regularization = 0 for HistGradientBoosting."));

children.push(H2("7.1 Final test evaluation"));
children.push(table([3400, 1500, 1400, 1300, 1300, 1180],
  ["Model", "RMSE (°C)", "MAE (°C)", "R²", "Max err", "±2 °C"],
  [
    ["MLP (tuned) — selected", "1.54", "1.10", "0.9965", "11.32", "84.2 %"],
    ["HistGradientBoosting (tuned)", "2.39", "1.75", "0.9915", "9.53", "65.0 %"],
    ["MLP (untuned baseline)", "1.67", "1.26", "0.9959", "9.84", "81.3 %"],
  ], { boldRows: [0] }));
children.push(TCAP("Table 8 — Tuned models refitted on the full training partition and scored on profiles 65 and 72."));
children.push(...figure("11_tuning_results.png", 6.8,
  "Figure 11 — What tuning bought, across three metrics. Colour identifies the model and is held constant across panels."));
children.push(P("Tuning improved RMSE by roughly 8 % and MAE by 13 %. It did not improve worst-case error, which moved the wrong way from 9.84 °C to 11.32 °C, because the search optimised RMSE and nothing in the objective constrained the tail. This is reported rather than hidden: selecting on RMSE and then disclosing max error is the honest order, and if worst case were the selection criterion, tuned HistGradientBoosting at 9.53 °C would be the better choice."));

children.push(H1("8. Validation Studies"));
children.push(P("Two controlled experiments were performed to test whether the result is genuine rather than an artefact of the experimental setup."));

children.push(H2("8.1 Ablation: where does the accuracy originate?"));
children.push(P("An identical LightGBM model was fitted three times against progressively richer feature sets, holding every other factor constant."));
children.push(table([5400, 2340, 2340],
  ["Feature set", "RMSE (°C)", "R²"],
  [
    ["8 raw input channels only", "14.39", "0.6942"],
    ["+ instantaneous physical derivations", "14.58", "0.6860"],
    ["+ EWMA thermal-history features", "2.43", "0.9913"],
  ], { boldRows: [2] }));
children.push(TCAP("Table 9 — Feature ablation. All three rows use the same model configuration and the same split."));
children.push(P("The instantaneous physical derivations — current magnitude, apparent power, loss proxy — buy essentially nothing on their own; the small regression from 0.6942 to 0.6860 is within run-to-run variation. Only the addition of the exponentially weighted features moves the result, and it moves it decisively. This establishes that the gain arises specifically from supplying thermal history, not merely from increasing the number of columns available to the model."));

children.push(H2("8.2 Leakage study: the cost of the wrong split"));
children.push(P("The same model and feature set were evaluated twice, varying only the partitioning scheme."));
children.push(table([5400, 2340, 2340],
  ["Split protocol", "RMSE (°C)", "R²"],
  [
    ["Random 80/20 over individual rows", "0.66", "0.9995"],
    ["Profile-wise, whole sessions held out", "2.50", "0.9908"],
  ], { boldRows: [1] }));
children.push(TCAP("Table 10 — The effect of the split protocol on reported accuracy."));
children.push(P("Random splitting understates RMSE by a factor of approximately 3.8. The randomly-split model reports R² = 0.9995, a figure that describes its ability to reproduce samples it has already seen in near-identical form. The profile-wise figure of 0.9908 describes what the model would actually do on a new motor run."));
children.push(...figure("09_ablation_leakage.png", 6.8,
  "Figure 12 — Left: feature ablation. Right: the effect of split protocol on reported accuracy."));
children.push(...CALLOUT("Methodological conclusion",
  "For time-series data sampled faster than the dynamics of the system being measured, grouped splitting is not a refinement — it is a correctness requirement. Any result obtained under random splitting on such data should be treated as uninformative."));

children.push(H2("8.3 What the model relies on"));
children.push(...figure("08_feature_importance.png", 6.0,
  "Figure 13 — The eighteen most-used features in the gradient-boosted model, coloured by family."));
children.push(P("Every one of the top fifteen features is thermal-history derived. The two strongest are the 600-second average of coolant temperature and the 600-second average of i_s². These are, respectively, the heat-sink boundary condition and the copper-loss term of the lumped-parameter thermal model set out in Section 3.3.2."));
children.push(P("This constitutes the strongest available evidence that the result is physically grounded. The model, given no information about motor thermodynamics beyond the choice of which signals to filter, independently concentrated on the two terms that a first-principles thermal model would identify as dominant."));



// ---------- 8. DEPLOYMENT ----------
children.push(H1("9. Deployment Considerations"));
children.push(P("The purpose of a virtual sensor is that it executes on the drive rather than in an analysis environment. The following observations bear on that transition."));
children.push(H2("9.1 Computational cost"));
children.push(P("The selected network comprises two hidden layers of 128 units over approximately 104 inputs, requiring roughly 30,000 multiply-accumulate operations per inference. The thermal dynamics require an update rate of only 2 Hz, so this represents approximately 60,000 MAC/s — negligible for any modern motor-control microcontroller, and trivially small for an FPGA implementation where the same computation could be pipelined at a fraction of the fabric."));
children.push(H2("8.2 The feature extractor is hardware-friendly"));
children.push(P("This is the property that makes the formulation attractive for embedded deployment and is not shared by most feature engineering schemes. Each exponentially weighted moving average is a single-pole IIR filter requiring one multiply, one add, and one state register per feature. The 90 thermal features therefore cost 90 registers and 90 MACs per sample, with no windowing buffer and no history storage of any kind. A conventional sliding-window statistic over a one-hour span at 2 Hz would require 7,200 samples of buffered history per signal; the recursive formulation requires one."));
children.push(H2("9.3 Fixed-point feasibility"));
children.push(P("Temperatures span 18–141 °C and require approximately 0.1 °C resolution, so 16-bit fixed point is sufficient at the output. The EWMA accumulators require greater headroom because of the long time constants: with a 3600-second span the per-sample update coefficient α is approximately 1.4 × 10⁻⁴, so accumulator precision rather than output precision is the binding constraint. A Q16.16 accumulator would be a reasonable starting point, with the quantised model's worst-case error re-characterised against the same held-out sessions before deployment."));
children.push(H2("9.4 Residual limitations"));
children.push(BULLET("The worst-case error of the selected model is 9.84 °C. A deployed thermal limit would require a corresponding margin below the insulation rating. The model reduces the necessary derating relative to a fixed conservative margin, but does not eliminate the need for one."));
children.push(BULLET("The model was trained on a single machine on a single test bench. Transfer to a different motor design would require retraining, or a transfer-learning approach with limited data from the new machine."));
children.push(BULLET("Errors are largest at sharp load transitions, where the shortest EWMA span limits how quickly the feature set can respond."));



// ---------- 9. CONCLUSIONS ----------
children.push(H1("10. Conclusions"));
children.push(NUMR([["The objective was met. ", { bold: true }], ["Stator winding temperature can be estimated from drive-measurable signals alone to RMSE 1.67 °C and R² = 0.9959 on motor sessions never seen during training, with 81.3 % of samples within ±2 °C and a worst-case error of 9.84 °C.", {}]], 3));
children.push(NUMR([["Feature engineering, not model selection, produced the result. ", { bold: true }], ["An unchanged linear regression improves from R² 0.53 to 0.99 when its inputs encode thermal history. The ablation in Section 8.1 confirms that the gain comes specifically from the exponentially weighted terms and not from feature count.", {}]], 3));
children.push(NUMR([["The evaluation protocol changes the reported result by a factor of four. ", { bold: true }], ["Profile-wise splitting is a correctness requirement on data of this kind; random splitting reports a figure that measures memorisation.", {}]], 3));
children.push(NUMR([["A smooth model generalises better than tree ensembles here, ", { bold: true }], ["because held-out sessions require extrapolation beyond the training envelope and piecewise-constant models cannot extrapolate.", {}]], 3));
children.push(NUMR([["The model learned the intended physics. ", { bold: true }], ["The dominant features are the coolant boundary condition and the copper-loss term — precisely the terms of the first-order thermal model from which the feature set was derived.", {}]], 3));
children.push(NUMR([["The result is deployable. ", { bold: true }], ["Approximately 60,000 MAC/s and 90 state registers is within the budget of a standard motor-control microcontroller, which is what makes this a replacement for a thermocouple rather than an offline analysis.", {}]], 3));

children.push(H2("10.1 Future work"));
children.push(BULLET("Sequence models — a temporal convolutional network or LSTM — that learn the thermal time constants from data rather than having them specified as fixed EWMA spans."));
children.push(BULLET("Multi-output prediction of all four temperature channels under a single model, exploiting the shared thermal structure between winding, tooth, yoke and magnet."));
children.push(BULLET("A physics-informed loss term penalising violations of the first-order thermal ordinary differential equation, which would constrain the model to physically realisable trajectories and may reduce worst-case error."));
children.push(BULLET("Fixed-point quantisation and a register-transfer-level implementation of the EWMA feature extractor, with hardware-in-the-loop validation against the same held-out sessions."));

children.push(H1("References"));
const refs = [
  "W. Kirchgässner, O. Wallscheid, and J. Böcker, \"Electric Motor Temperature\" dataset, Department of Power Electronics and Electrical Drives (LEA), Paderborn University. Available via Kaggle.",
  "W. Kirchgässner, O. Wallscheid, and J. Böcker, \"Estimating Electric Motor Temperatures With Deep Recurrent Neural Networks,\" IEEE Open Journal of the Industrial Electronics Society, 2021.",
  "O. Wallscheid and J. Böcker, \"Global Identification of a Low-Order Lumped-Parameter Thermal Network for Permanent Magnet Synchronous Motors,\" IEEE Transactions on Energy Conversion, vol. 31, no. 1, 2016.",
  "G. Ke et al., \"LightGBM: A Highly Efficient Gradient Boosting Decision Tree,\" Advances in Neural Information Processing Systems 30, 2017.",
  "F. Pedregosa et al., \"Scikit-learn: Machine Learning in Python,\" Journal of Machine Learning Research, vol. 12, 2011.",
  "IEC 60034-1, Rotating electrical machines — Part 1: Rating and performance, International Electrotechnical Commission.",
];
refs.forEach((r, i) => children.push(new Paragraph({
  spacing: { after: 120, line: 276 }, indent: { left: 420, hanging: 420 },
  children: [new TextRun({ text: `[${i + 1}]  ${r}`, size: 20, font: "Calibri" })],
})));

children.push(H1("Appendix A — Reproducing the Results"));
children.push(P("The complete analysis is provided as a Jupyter notebook, motor_temperature_prediction.ipynb, which reproduces every figure and table in this report from the raw CSV. The same pipeline is also supplied as standalone Python modules."));
children.push(table([3200, 6880],
  ["File", "Contents"],
  [
    ["motor_temperature_prediction.ipynb", "Complete analysis, executed end to end"],
    ["src/features.py", "Physical derivations and EWMA feature construction"],
    ["src/build_features.py", "Builds the 104-feature matrix from the raw CSV"],
    ["src/train.py", "Model ladder, ablation and leakage studies"],
    ["src/results_figs.py", "Result figures and the metrics table"],
    ["src/eda.py, src/flow_diagram.py", "Exploratory figures and the pipeline diagram"],
  ]));
children.push(TCAP("Table 11 — Supplied code artefacts."));
children.push(P("Dependencies: pandas, numpy, scikit-learn, lightgbm, matplotlib, pyarrow. A full run takes approximately 20–30 minutes on a standard laptop. Set the PATH variable in the second code cell to the location of measures_v2.csv."));

// ---------- BUILD ----------
const doc = new Document({
  creator: "Lohhith Thakur",
  title: "ML Estimation of Stator Winding Temperature in PMSMs",
  description: "UCS321 MST Mini Project — Problem Statement 6",
  numbering: {
    config: [
      { reference: "bullets", levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 460, hanging: 240 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "◦", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 900, hanging: 240 } } } },
      ] },
      { reference: "nums", levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 460, hanging: 300 } } } },
      ] },
    ],
  },
  styles: { default: { document: { run: { font: "Calibri", size: 21 } } } },
  sections: [{
    properties: {
      page: { size: { width: 12240, height: 15840 },
        margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } },
    },
    headers: { default: new Header({ children: [new Paragraph({
      alignment: AlignmentType.RIGHT, spacing: { after: 0 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: RULE, space: 6 } },
      children: [new TextRun({ text: "UCS321 — Mini Project — Problem Statement 6",
        size: 16, color: MUTED, font: "Calibri" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], size: 16, color: MUTED, font: "Calibri" })] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((b) => {
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, b);
  console.log("report written:", OUT, b.length, "bytes");
});
