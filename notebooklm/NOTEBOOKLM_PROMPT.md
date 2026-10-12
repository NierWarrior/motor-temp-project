# NotebookLM — how to use this

## Setup

1. Create a new notebook in NotebookLM.
2. Upload **`PROJECT_STORY.md`** as a source. That one file is self-contained — it is the whole project in narrative form.
3. *(Optional but recommended)* Also upload `UCS321_Report.pdf` and the 13 figures from `figures/`. NotebookLM can pull visuals from PDFs into a Video Overview, and the report's figure captions let it describe them correctly.
4. Generate a **Video Overview** (or Audio Overview), and paste one of the prompts below into the **"Customise"** box before you hit generate.

---

## PROMPT A — the full one (use this if the box accepts long text)

```
AUDIENCE: a curious engineering student who knows nothing about electric
motors, nothing about this dataset, and only the basics of machine learning.
Assume zero prior context. By the end they should be able to re-explain this
entire project to someone else from memory.

TELL IT AS A STORY WITH A PROBLEM AT ITS CENTRE. Follow this arc, and do not
skip ahead to the results:

1. THE HOOK — Open with the physical stakes, not with machine learning. There
   is a copper coil inside every electric motor, wrapped in enamel insulation
   a few hundredths of a millimetre thick. Heat destroys that enamel, and
   insulation life halves for every 10 degrees of overheating. Make the
   listener feel why this one number decides whether the motor lives or dies.

2. THE TRAP — Explain the cruel catch: you can measure this temperature
   perfectly on a laboratory test bench, and you cannot measure it at all in a
   motor you actually sell. Walk through exactly why — the voltage, the
   vibration, the sealed housing, the cost. Let the listener feel stuck.

3. THE OPENING — Reveal that the motor's own controller is already measuring
   eight signals, for free, every fraction of a second, for completely
   unrelated reasons. That is the whole opportunity.

4. THE ASSIGNMENT — Now, and only now, state the actual problem statement
   that was set: Problem Statement 6, General Electric Power Systems, build a
   regression model to estimate motor winding temperature. Explain how the
   team reframed a generic coursework task into a real engineering goal: a
   virtual sensor that replaces a physical thermocouple.

5. THE THREE DECISIONS — This is the heart. Spend the most time here. Each
   decision made the headline number WORSE in exchange for the result
   actually meaning something. Build suspense into each one:

   (a) They deleted the three best features. Three extra thermocouples in the
       dataset correlate above 0.95 with the answer. Explain the temptation,
       then explain why keeping them would have made the project worthless.

   (b) They derived the features from physics, not from guesswork. Walk
       slowly through this: a motor heating up obeys a simple differential
       equation; solving it shows temperature is an exponentially weighted
       integral of all past heat; and that integral, in discrete time, IS an
       exponentially weighted moving average. So the feature is not a
       smoothing trick someone tried — it is the physics written down. Use
       the bathtub analogy: you cannot tell how full a bathtub is by looking
       only at the tap.

   (c) They refused to split the data randomly. Explain why: samples are half
       a second apart, a motor cannot change temperature in half a second, so
       neighbouring rows are near-twins, and a random split quietly puts the
       answers in the training set. Then deliver the measured cost — random
       splitting made the error look 3.8 times better than it really was.

6. THE RESULTS — Lead with the single pair of numbers that matters most: the
   SAME linear regression goes from R-squared 0.53 to 0.99 purely because the
   inputs changed. Nothing about the algorithm. Then give the final result:
   1.54 degrees RMSE, R-squared 0.9965, 84.2 percent of readings within two
   degrees, on motor runs the model had never seen.

   Then explain the three surprises honestly: the neural network beat the
   gradient-boosted trees (because trees cannot extrapolate and the test runs
   sat 24 times further from the training data than training points sit from
   each other); plain ridge regression beat LightGBM; and the metrics
   disagreed about which model was best, which is itself the lesson.

7. THE PROOF — Explain how they showed the result was real rather than
   lucky: an ablation proving the gain came specifically from the thermal
   memory and not from simply having more columns; a leakage study measuring
   what the wrong split would have claimed; and the best moment of the whole
   project — the trained model's two most-used inputs turned out to be the
   coolant temperature and the current squared, which are exactly the two
   terms the original physics equation names as dominant. The model
   rediscovered the physics it was built from. Land this as the payoff.

8. THE HONEST ENDING — Do not finish on triumph. Cover the real limitations:
   worst-case error is still 11.3 degrees; tuning improved the average but
   made the worst case slightly worse; the biggest errors sit in the first
   minutes of a run while the long filters are still warming up; and it is
   trained on one motor on one test bench. Then close on why it matters: the
   whole estimator costs about 60,000 operations per second and 90 registers,
   small enough to run on the motor's own controller — which is the
   difference between a thermocouple replacement and a lab exercise.

STYLE RULES:
- Explain every technical term the first time it appears, in one plain
  sentence, then use it freely. Terms to define: PMSM, stator winding,
  thermocouple, EWMA, target leakage, RMSE, R-squared, extrapolation.
- Prefer concrete physical images over jargon. Heat accumulating in copper.
  A bathtub filling. A filter with a memory.
- Every number you state must come from the source document. Do not invent,
  round loosely, or estimate.
- Treat the listener as intelligent but uninformed. Never condescend, never
  assume.
- Emphasise reasoning over outcomes. The question "why did they do that?"
  should be answered before "what happened".
- Do not read out file names, folder paths, code, or installation steps.
- Keep momentum. Each section should make the listener want the next one.
```

---

## PROMPT B — the compact one (if the box is short)

```
Explain this project as a story for a curious student who knows nothing about
motors or ML. Arc: (1) a copper coil inside every motor dies from heat, and
insulation life halves per 10 degrees too hot; (2) you can measure that
temperature on a test bench but never in a motor you sell — explain why;
(3) but the drive already measures eight signals for free; (4) state the
assignment — Problem Statement 6, GE Power Systems — and how the team
reframed it as a virtual sensor replacing a thermocouple; (5) spend the most
time on the three decisions that each made the numbers LOOK worse but made
them MEAN something: deleting the three best features as leakage, deriving
the features from the thermal differential equation (whose solution IS an
exponentially weighted moving average — use the bathtub-and-tap analogy), and
refusing to split the data randomly; (6) results — the same linear regression
going from R-squared 0.53 to 0.99 on features alone, then the final 1.54
degrees RMSE and 84.2 percent within two degrees; (7) the payoff — the
trained model's top two features turned out to be coolant temperature and
current squared, exactly the two terms the original physics equation names;
(8) end honestly with the limitations, then why it fits on a microcontroller.
Define every term on first use. Use only numbers from the source. Explain why
before what. No file paths, no code.
```

---

## Follow-up prompts worth trying in the chat panel

Once the notebook is built, these produce genuinely useful extra material:

- `Generate 15 viva questions an examiner would ask about this project, with model answers drawn only from the source.`
- `Produce a 3-minute version of this explanation for someone with 3 minutes.`
- `Explain the EWMA feature engineering section to a 15-year-old, using only everyday analogies.`
- `What is the single weakest part of this project, and what would an expert criticise first?`
- `Create a study guide: the ten facts someone must memorise to defend this project.`
- `Build a timeline of the project as a sequence of decisions, with the reasoning behind each.`

---

## One tip on length

NotebookLM Video Overviews run longer and stay more faithful when the source
has clear section headings — which `PROJECT_STORY.md` does, nine numbered
parts plus a glossary. If the first generation feels rushed, add this line to
the customise box:

```
Go deep. Do not compress. Spend real time on Part Three (the three decisions)
and Part Five (the proof) — those two sections are the project.
```
