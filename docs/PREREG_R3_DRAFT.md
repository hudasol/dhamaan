# Round 3 preregistration (DRAFT, not registered)

Status: draft. Nothing in this document has been run. Items in square brackets are fixed after the recorded data are chosen and before any recorded log is replayed. When complete, the text is committed, its SHA 256 is recorded, and the same text is registered on a public registry that issues its own timestamp (the OSF preregistration form uses the headings in the last section). Only then does any run begin.

Hypotheses H3 to H5 are in `docs/RESEARCH_QUESTION.md`. Rounds 1 and 2 are frozen and are not rerun with changed settings; round 3 adds new conditions beside them.

## 1. Parts

| Part | Question | New runs |
|---|---|---|
| A | How many of the 42 predictions in rounds 1 and 2 could have failed? | Rerun of rounds 1 and 2 under mutated models |
| B | Which acceptance verdicts flip when an assumed parameter changes? | Rerun under parameter changes |
| C | Do verdicts for the GNSS monitor agree between synthetic and recorded arms? (H3 to H5) | Replay of recorded logs |
| D | Does a generator written by someone else give the same verdicts as ours? | One independently written generator |

Part C is the core. Parts A, B and D limit what the other parts can be taken to show.

## 2. Part A: informativeness of predictions

A prediction is informative if its verdict changes under at least one mutant. Mutants, each applied to the whole model and rerun on the same seeds:

- M0: a monitor that never alarms.
- M1: a monitor that alarms at every fix.
- M2: each assumed parameter multiplied by 0.5 and by 1.5, one at a time (parameters listed from the code by a script, not by hand).
- M3: the fault onset time shifted by a fixed offset.

Output: for every prediction, the verdict under the original model and under each mutant; the count of predictions whose verdict never changes; the hit rate among informative predictions only. Reported next to the headline hit rates, which stay as published.

Prediction (written now): at least a quarter of the 42 predictions are unchanged under every mutant.

## 3. Part B: sensitivity

For each acceptance criterion of both rounds, the verdict under each parameter change in M2. Output: a table of criteria against parameters, marking each flip, and a list of the criteria that never flip and the ones that flip under a change of 50 percent or less.

Prediction (written now): at least one criterion that held in rounds 1 or 2 flips under a change of 50 percent or less in one assumed parameter.

## 4. Part C: synthetic against recorded

### Arms

- S0: the existing synthetic generator and the faults of rounds 1 and 2, unchanged.
- S1: the synthetic generator after recalibration on the calibration recordings (adds what the calibration data show, for example time correlation and heavy tails of the position error). Calibration uses only the calibration recordings.
- R: recorded receiver output. Nominal segments of recordings with faults injected at measurement level by the same fault functions as S0 (semi synthetic, labelled as such), and, where the recording has labelled natural interference intervals, those intervals as they are (recorded, labelled).

### Data

[Source, licence, format and recording identifiers, chosen from the options in `data/gnss_data_options.csv` (20 options, retrieved 20 October 2026). At that date no option was clean for replay: no licensed fix level log under real interference was found, and no Gulf data set was found. Candidates are the ADS B track archives under the Open Database Licence (interference inferred from reported accuracy fields, not labelled), and the Andoya jammer test (real interference, raw samples only, licence to be confirmed by reading the data page). Only recordings with a stated licence that allows reuse are used. The licence text and URL are entered in `data/third_party_manifest.csv` before any replay.] Recordings made outside the Gulf are used as such and no Gulf claim is drawn from them.

### Split

Recordings are assigned to calibration or held out by a seeded draw [seed] before any metric is computed. [Number] recordings calibrate and [number] are held out. A recording is never split across the two sets. No setting of the monitor is changed in this round.

### Monitor and thresholds

The monitor of round 1 and 2 with the thresholds in `sim/` at the commit [hash]. The code hash is recorded at scoring, as in round 2.

### Measures (per fault class and arm)

- detection rate within the time limit T_N;
- mean detection delay;
- false alarms per hour of nominal data [definition: an alarm raised when no fault is injected and no labelled interference interval is active];
- navigation error at the stop.

### Verdicts

The acceptance criteria of round 1 that concern the GNSS monitor (AC-N1 and AC-N2) are scored on each arm with their original values, plus the criterion [AC-N4: false alarms per hour of nominal data at most [value]; the value is set from the synthetic arm's rate before any recorded data are seen].

### Predictions (direction fixed now; numbers fixed with the data)

| Id | Prediction |
|---|---|
| R3-P1 | At least one verdict among AC-N1, AC-N2 and AC-N4 differs between S0 and R on held out recordings (H3). |
| R3-P2 | On R the false alarm rate per hour of nominal data is higher than on S0 (H4). |
| R3-P3 | On R the mean detection delay for drift is longer than on S0 (H4). |
| R3-P4 | On held out recordings S1 reproduces the verdict of R for every criterion where S0 differs from R (H5). |
| R3-P5 | On held out recordings S1 reproduces the verdict of R for every criterion (H5, strict form). |
| R3-P6 | The verdict of S0 on calibration recordings differs from its verdict on held out recordings in no criterion (no hidden dependence on the split). |

### Reading rules

- A prediction is scored HIT or MISS from the result files by script. Misses are reported with the same prominence as hits.
- If R3-P1 is a MISS, the synthetic arm is adequate for this monitor and the credit ledger may credit it as such, with the recorded evidence listed beside it.
- If R3-P4 is a MISS, synthetic faults cannot stand in for the recorded claim, and the ledger says so.
- No hardware claim is closed by any outcome of this round.

## 5. Part D: independently written generator

A written specification of the fault classes and the data format is given to a second author who has not seen the monitor code or the results of rounds 1 and 2. The second author writes a generator from the specification. Its verdicts are compared with those of S0 on the same monitor and thresholds. The identity of the second author is stated (a person, or a separate automated reviewer; in the second case the shared origin of the two authors is stated as a limit). Prediction: at least one verdict differs.

## 6. Analysis, exclusions and stopping

- All runs listed are carried out; none is dropped after seeing results. A run that fails for a technical reason is rerun once with the same seed, and both outcomes are logged.
- Wilson intervals for rates; bootstrap intervals for delays; no significance tests are used to decide verdicts, only the criteria above.
- Deviations from this text are logged in `sim/DEVIATIONS.md` with the date and the reason, as in earlier rounds.
- The round stops when all parts are run. No part is added after seeing results.

## 7. Registry form (headings for the public registration)

Study information: title, authors, description, hypotheses (H3 to H5). Design plan: study type (computational, replay of existing data), blinding (none; scripts score), study design (arms and parts above), randomisation (seeded split). Sampling plan: existing data (recorded logs, listed), data collection procedures, sample size, rationale, stopping rule. Variables: manipulated (arm), measured (measures above), indices. Analysis plan: models and criteria, inference criteria, data exclusion, missing data, exploratory analyses (marked as such). Other: the unchanged monitor and thresholds, the commit hashes, and the deviations log.
