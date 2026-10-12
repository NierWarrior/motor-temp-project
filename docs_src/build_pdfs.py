# -*- coding: utf-8 -*-
"""Render the viva question bank and the terms glossary to PDF via headless Chromium."""
import subprocess, sys, pathlib, io
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import content_viva as CV
import content_terms as CT

OUT = pathlib.Path(__file__).resolve().parents[1] / "reports"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

STUDENT = "Lohhith Thakur &middot; Roll No. 1025220020 &middot; B.E. Electronics (VLSI Design &amp; Technology)"
COURSE  = "UCS321 &mdash; AI for Engineers &middot; MST Mini Project &middot; Problem Statement 6 (GE Power Systems)"
PROJECT = "PMSM Thermal Virtual Sensor &mdash; estimating stator winding temperature from drive-measurable signals"

CSS = r"""
@page { size: A4; margin: 17mm 16mm 20mm 16mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  font-family: "DejaVu Serif", Georgia, "Times New Roman", serif;
  font-size: 9.6pt; line-height: 1.5; color: #1A1A1A; margin: 0;
  overflow-wrap: break-word;
}
code {
  font-family: "DejaVu Sans Mono", Consolas, monospace;
  font-size: 0.87em; background: #F0F2F5; padding: 0.5px 3px;
  border-radius: 2px; color: #11304A;
  overflow-wrap: anywhere; word-break: break-word;
}
b, strong { color: #11304A; }
h1, h2, h3, .sans { font-family: "DejaVu Sans", Helvetica, Arial, sans-serif; }

/* ---------- cover ---------- */
.cover { page-break-after: always; padding-top: 9mm; }
.rule        { height: 3.5px; background: #1F4E79; margin-bottom: 7mm; }
.rule-thin   { height: 1px;   background: #C8CFD6; margin: 5mm 0; }
.kicker { font-family:"DejaVu Sans",Arial,sans-serif; font-size: 8.2pt; letter-spacing: 1.4px;
          text-transform: uppercase; color: #E8833A; font-weight: 700; margin-bottom: 4mm; }
.cover h1 { font-size: 23pt; line-height: 1.14; color: #11304A; margin: 0 0 4mm 0; font-weight: 700; }
.cover .sub { font-size: 10.8pt; color: #3C4A57; line-height: 1.42; margin-bottom: 7mm; }
.meta { font-size: 9pt; color: #4A5560; line-height: 1.75; }
.meta b { color: #11304A; }
.howto { margin-top: 7mm; background: #F6F8FA; border-left: 3.5px solid #E8833A;
         padding: 5mm 6mm; font-size: 9.2pt; line-height: 1.55; }
.howto .t { font-family:"DejaVu Sans",Arial,sans-serif; font-weight:700; color:#11304A;
            font-size: 9.6pt; margin-bottom: 2.5mm; }
.howto ul { margin: 0; padding-left: 5mm; }
.howto li { margin-bottom: 1.6mm; }

/* ---------- numbers strip ---------- */
.nums { display: flex; gap: 3mm; margin-top: 7mm; }
.num  { flex: 1; background: #11304A; color: #fff; padding: 3.1mm 2mm; text-align: center; }
.num .v { font-family:"DejaVu Sans",Arial,sans-serif; font-size: 14.5pt; font-weight: 700;
          color: #FFCFA8; line-height: 1.1; }
.num .l { font-size: 7.4pt; color: #C9D6E2; margin-top: 1.2mm; line-height: 1.3; }

/* ---------- sections ---------- */
.sec { page-break-before: always; }
.sec:first-of-type { page-break-before: avoid; }
.sechead { border-bottom: 2.5px solid #1F4E79; padding-bottom: 2.4mm; margin-bottom: 5.5mm; }
.sechead .k { font-family:"DejaVu Sans",Arial,sans-serif; font-size: 8pt; letter-spacing: 1.3px;
              text-transform: uppercase; color: #E8833A; font-weight: 700; }
.sechead h2 { font-size: 14.5pt; color: #11304A; margin: 1.2mm 0 0 0; font-weight: 700; }
.sechead .d { font-size: 8.8pt; color: #5A6672; margin-top: 1.6mm; font-style: italic; }

/* ---------- Q & A ---------- */
.qa { page-break-inside: avoid; margin-bottom: 5.2mm; }
.q  { display: flex; gap: 3mm; margin-bottom: 1.7mm; }
.qn { font-family:"DejaVu Sans",Arial,sans-serif; font-weight: 700; font-size: 9pt; color: #fff;
      background: #1F4E79; min-width: 7.2mm; height: 7.2mm; border-radius: 50%;
      display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.qt { font-family:"DejaVu Sans",Arial,sans-serif; font-weight: 700; font-size: 10pt;
      color: #11304A; line-height: 1.38; padding-top: 0.7mm; min-width: 0; }
.a  { margin-left: 10.2mm; padding-left: 3.4mm; border-left: 2px solid #E3E8ED; text-align: justify; }

/* ---------- glossary tables ---------- */
table { width: 100%; border-collapse: collapse; margin-bottom: 4mm; }
thead { display: table-header-group; }
th { font-family:"DejaVu Sans",Arial,sans-serif; font-size: 8.1pt; text-transform: uppercase;
     letter-spacing: 0.7px; text-align: left; color: #fff; background: #1F4E79;
     padding: 2.4mm 2.6mm; font-weight: 700; }
td { padding: 2.6mm 2.6mm; border-bottom: 1px solid #DDE3E9; vertical-align: top;
     font-size: 9.1pt; line-height: 1.45; }
tr { page-break-inside: avoid; }
tr:nth-child(even) td { background: #F7F9FB; }
td.term { font-family:"DejaVu Sans",Arial,sans-serif; font-weight: 700; color: #11304A;
          font-size: 9.1pt; width: 21%; }
td.term code { background: none; padding: 0; color: #11304A; font-weight: 700; font-size: 0.95em; }

/* ---------- contents (two columns) ---------- */
.toc { margin-top: 7mm; }
.toc .t { font-family:"DejaVu Sans",Arial,sans-serif; font-weight: 700; color: #11304A;
          font-size: 9.6pt; margin-bottom: 2.5mm; letter-spacing: .3px; }
.toc .cols { column-count: 2; column-gap: 7mm; }
.toc .row { display: flex; align-items: baseline; gap: 2.2mm; break-inside: avoid;
            border-bottom: 1px solid #E6EBF0; padding: 1.35mm 0; font-size: 8.6pt; }
.toc .kk { font-family:"DejaVu Sans",Arial,sans-serif; font-weight: 700; color: #E8833A;
           font-size: 8.2pt; min-width: 4mm; flex-shrink: 0; }
.toc .lb { flex: 1; min-width: 0; color: #2B3742; }
.toc .nn { color: #6A7682; font-size: 8pt; flex-shrink: 0;
           font-family:"DejaVu Sans",Arial,sans-serif; }
td.what { width: 37%; color: #37424E; }
td.work { width: 42%; }
.cols { font-size: 0; }
"""

def shell(txt, title, subtitle):
    return ("<!doctype html><html><head><meta charset='utf-8'><title>" + title +
            "</title><style>" + CSS + "</style></head><body>" + txt + "</body></html>")


def cover(kicker, h1, sub, howto_title, howto_items, nums, toc_title=None, toc_rows=None):
    n = "".join(f"<div class='num'><div class='v'>{v}</div><div class='l'>{l}</div></div>"
                for v, l in nums)
    items = "".join(f"<li>{i}</li>" for i in howto_items)
    toc = ""
    if toc_rows:
        body = "".join(f"<div class='row'><span class='kk'>{k}</span>"
                       f"<span class='lb'>{lab}</span><span class='nn'>{rng}</span></div>"
                       for k, lab, rng in toc_rows)
        toc = (f"<div class='toc'><div class='t'>{toc_title}</div>"
               f"<div class='cols'>{body}</div></div>")
    return f"""
<div class="cover">
  <div class="rule"></div>
  <div class="kicker">{kicker}</div>
  <h1>{h1}</h1>
  <div class="sub">{sub}</div>
  <div class="rule-thin"></div>
  <div class="meta">
    <b>Project</b> &nbsp; {PROJECT}<br>
    <b>Course</b> &nbsp;&nbsp; {COURSE}<br>
    <b>Student</b> &nbsp; {STUDENT}
  </div>
  <div class="nums">{n}</div>
  <div class="howto">
    <div class="t">{howto_title}</div>
    <ul>{items}</ul>
  </div>
  {toc}
</div>"""


def viva_toc():
    rows, n = [], 1
    for key, title, qs in CV.SECTIONS:
        rows.append((key, title, f"Q{n}&ndash;{n+len(qs)-1}"))
        n += len(qs)
    return rows


def terms_toc():
    return [(k, title, f"{len(rows)} terms") for k, title, _, rows in CT.GROUPS]


# ─────────────────────────── document 1: viva Q&A ───────────────────────────
def build_viva():
    parts = [cover(
        "Viva Preparation",
        f"{CV.TOTAL} Viva Questions,<br>With Answers",
        "Every topic in the project, from the physics of the machine to the hyperparameter "
        "search &mdash; phrased the way an examiner would ask it, and answered the way you "
        "should answer it.",
        "How to use this",
        ["Each answer is written to be <i>spoken</i>, not read out &mdash; two to six sentences, "
         "with the number that settles the point.",
         "<b>Bold</b> marks the figure or phrase to land. If you remember nothing else from an "
         "answer, remember the bold part.",
         "Sections A&ndash;J follow the notebook's own order, so you can revise a section and the "
         "corresponding notebook section together.",
         "If you are short of time, the six that decide the viva are "
         "<b>23</b> (how you identified leakage), <b>30</b> (deriving the EWMA from the "
         "thermal ODE), <b>41</b> (quantifying the leakage), <b>49</b> (proving extrapolation), "
         "<b>61</b> (defending R&sup2; = 0.9965) and <b>66</b> (the CV-to-test gap)."],
        [("1.54 °C", "RMSE on unseen sessions"), ("0.9965", "R² on unseen sessions"),
         ("104", "features from 8 channels"), ("3.8×", "error hidden by a random split")],
        "Contents", viva_toc())]

    for key, title, qs in CV.SECTIONS:
        n_from = 1 + sum(len(q) for k, t, q in CV.SECTIONS[:[s[0] for s in CV.SECTIONS].index(key)])
        body = [f"<div class='sec'><div class='sechead'><div class='k'>Section {key} "
                f"&mdash; {len(qs)} questions</div><h2>{title}</h2></div>"]
        for i, (q, a) in enumerate(qs):
            body.append(f"<div class='qa'><div class='q'><div class='qn'>{n_from+i}</div>"
                         f"<div class='qt'>{q}</div></div><div class='a'>{a}</div></div>")
        body.append("</div>")
        parts.append("".join(body))

    return shell("".join(parts), "Viva Questions", "")


# ──────────────────────── document 2: terms glossary ────────────────────────
def build_terms():
    parts = [cover(
        "Terminology Reference",
        f"{CT.TOTAL} Terms,<br>And What Each One Does",
        "Every term used in the project &mdash; what it means, and specifically what job it "
        "performs in this pipeline. Read the third column: knowing a definition is not the same "
        "as knowing why the term is in the project.",
        "How to read the table",
        ["<b>Term</b> is the name as it appears in the code, report and deck.",
         "<b>What it is</b> is the general definition &mdash; the textbook answer.",
         "<b>What work it does here</b> is the part that earns marks: why this project contains "
         "this term at all.",
         "Groups 1&ndash;4 are the physics and the features; 5&ndash;7 are the method and the "
         "metrics; 8 is the tooling."],
        [(str(CT.TOTAL), "terms defined"), (str(len(CT.GROUPS)), "groups"),
         ("90", "of 104 features are thermal history"),
         ("600 s", "the EWMA span that dominates")],
        "Contents", terms_toc())]

    for key, title, blurb, rows in CT.GROUPS:
        body = [f"<div class='sec'><div class='sechead'><div class='k'>Group {key} "
                f"&mdash; {len(rows)} terms</div><h2>{title}</h2>"
                f"<div class='d'>{blurb}</div></div>",
                "<table><thead><tr><th>Term</th><th>What it is</th>"
                "<th>What work it does in this project</th></tr></thead><tbody>"]
        for term, what, work in rows:
            body.append(f"<tr><td class='term'>{term}</td><td class='what'>{what}</td>"
                         f"<td class='work'>{work}</td></tr>")
        body.append("</tbody></table></div>")
        parts.append("".join(body))

    return shell("".join(parts), "Terms Reference", "")


def to_pdf(html, stem):
    h = OUT / f"{stem}.html"
    p = OUT / f"{stem}.pdf"
    h.write_text(html, encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu",
                    "--no-pdf-header-footer", "--virtual-time-budget=10000",
                    f"--print-to-pdf={p}", str(h)],
                   capture_output=True, check=True)
    return p


if __name__ == "__main__":
    for html, stem in [(build_viva(), "UCS321_Viva_Questions"),
                       (build_terms(), "UCS321_Terms_Reference")]:
        p = to_pdf(html, stem)
        print(f"{p.name}  {p.stat().st_size/1024:.0f} KB")
