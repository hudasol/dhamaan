# Whose verdict counts? Synthetic and recorded GNSS interference for a robot integrity monitor

Status: generated draft. Simulation numbers are SYNTHETIC. Every number is filled by `docsgen/facts.py` from the data files; text edits go in `docs/templates/MANUSCRIPT.tmpl.md`. The recorded arm was run once on a public jamming and spoofing campaign (see the section on the recorded comparison); it is one campaign, one receiver and not the Gulf. Single author, no human check of the evidence table yet, no outside reader yet.

## Abstract

Where no instrument fixes the conditions a service robot must be shown safe under, the developer's own simulation becomes the evidence. We build a source traced table of {{N_ROWS}} rows over {{N_FAMILIES}} instrument families and measure its extraction error (either pass, {{ROW_ERR_EITHER}}, interval {{ROW_ERR_CI}}). We audit {{MS_SILENCE_SCOPE}} in scope rows for what they leave to the developer: of {{MS_SILENCE_ASK}} that ask for environmental or interference evidence, {{MS_SILENCE_SEV}} fix a severity and {{MS_SILENCE_SEV_GULF}} fix one that applies to a Gulf site. We encode published simulation credibility conditions in a checker for a machine readable assurance case, so that {{N_EVIDENCE_ITEMS}} evidence items each carry a ceiling on the claim they can support. Two preregistered synthetic rounds hit {{PRED_HIT}} of {{PRED_TOTAL}} and {{R2_PRED_HIT}} of {{R2_PRED_TOTAL}} predictions; a mutation audit of the predictions found {{MS_R3_UNINF}} uninformative (round three state: {{MS_R3_STATE}}). On {{REC_N}} recordings from a public campaign, the monitor raised {{REC_M_FA}} false alarms per nominal hour against {{REC_M_SYN_FA}} in the synthetic arm. A post hoc review shows that this figure mixes real interference inside a mislabelled segment with a speed regime (a vehicle, not a slow robot) that the monitor's settings do not fit, and that on still receivers it raised no alarm; the nominal exposure is under one hour. All simulated evidence is synthetic, written by the authors of the monitors it tests, and supports no claim about a real robot.

## Introduction

A team that builds a safety monitor also builds the simulation that tests it. If the regulation is silent on which conditions count, that simulation is the evidence. The question is whether such evidence agrees with what happens on recorded data, and whether credibility conditions that already exist in other fields would have warned us. The study makes four contributions: the evidence table, the silence audit, a checker that applies credibility conditions to an assurance case and keeps hardware claims open, and a preregistered design for comparing synthetic with recorded interference. It does not propose a new credibility framework, a safety case for a real robot or any legal conclusion.

## Related work

Credibility of simulation as evidence is treated by risk based frameworks, a ladder of simulator admissibility, the NASA credibility scale and guidance on independence of verification. These are listed with their status in `docs/RELATED_WORK.md` and `data/related_work.csv`; abstracts and page summaries were read, not all originals, and paywalled standards were not read. We adopt their conditions and encode them. The open piece is a verdict comparison on one monitor with thresholds fixed in advance.

## Evidence table

The table has {{N_ROWS}} rows. Access level: full text seen {{ACC_FULL}}, summary seen {{ACC_SUMMARY}}, title only {{ACC_TITLE}}. Binding status: mandatory {{BIND_MANDATORY}}, conditional {{BIND_CONDITIONAL}}, voluntary {{BIND_VOLUNTARY}}, guidance {{BIND_GUIDANCE}}. A second and third pass measured the error rate in a sample: {{ROW_ERR_EITHER}} of rows had an error in either pass, 95 percent interval {{ROW_ERR_CI}}. Rows changed by the final check had {{PASSC_CHANGED}} further errors, and unchanged rows {{PASSC_UNCHANGED}}. A human check of a stratified sample of sixty rows is designed (`data/human_check/DESIGN.md`) and has not been done; until it is, the error rates come from automated passes of one model family.

## Silence audit

Two automated coders, instances of one model family, coded {{MS_CODED_ROWS}} candidate rows with a written codebook (`data/silence_audit/CODEBOOK.md`). Cohen's kappa by field ranged from {{MS_KAPPA_MIN}} to {{MS_KAPPA_MAX}}. After resolving disagreements, {{MS_SILENCE_SCOPE}} rows were in scope and {{MS_SILENCE_OUT}} out of scope. Of the in scope rows, {{MS_SILENCE_ASK}} ask for evidence, {{MS_SILENCE_NOASK}} do not, and {{MS_SILENCE_UNCLEAR}} are unclear. Among those that ask, {{MS_SILENCE_METHOD}} fix a test method, {{MS_SILENCE_SEV}} fix a severity, {{MS_SILENCE_SEV_GULF}} fix a severity that applies to a Gulf site, and {{MS_SILENCE_DELEG}} leave the conditions to the developer. Restricting to the {{MS_SILENCE_FULL_ROWS}} rows seen as full text, {{MS_SILENCE_FULL_DELEG}} leave conditions to the developer. Limit: {{MS_SILENCE_LIMIT}}

## Assurance case and credit ledger

The library robot case has {{N_GOALS}} goals and {{N_EVIDENCE_ITEMS}} evidence items: {{N_OPEN}} open, {{N_PARTIAL}} partial and {{N_PROVIDED}} provided. The checker gives each item a ceiling (none, demonstration, indicative, supporting) from four conditions it can verify by opening a referenced file: stated context of use, validation against measured data, reported sensitivity or uncertainty, and a verifier record showing independence. A hardware claim also needs bench or field evidence. Today the partial items are {{PARTIAL_LIST}}; goals resting on simulation alone are {{SIM_ONLY_GOALS}}. The checker reports {{CASE_ERRORS}} errors and {{CASE_FLAGS}} flags.

{{CASE_FLAG_TABLE}}

## Simulation rounds one and two

Round one (preregistration SHA-256 `{{PREREG_SHA}}`): {{PRED_HIT}} of {{PRED_TOTAL}} predictions hit; missed {{PRED_MISS_LIST}}. Criteria held {{AC_HELD_LIST}}; failed {{AC_FAILED_LIST}}. Round two (SHA-256 `{{R2_PREREG_SHA}}`): {{R2_PRED_HIT}} of {{R2_PRED_TOTAL}} predictions hit; missed {{R2_PRED_MISS_LIST}}; criteria failed {{R2_AC_FAILED_LIST}}. The detail is in `docs/EVALUATION.md` and `docs/EVALUATION_R2.md`.

## Round three

Informativeness audit (state: {{MS_R3_STATE}}). A prediction is informative if its verdict changes under any of four classes of mutant: a monitor that never alarms, one that alarms at once, each assumed parameter scaled by one half and by one and a half, and a shifted fault onset. Across {{MS_R3_MUTANTS}} mutant runs, {{MS_R3_INF}} of {{MS_R3_PREDS}} predictions were informative, and {{MS_R3_INF_HIT}} of those hit, against {{MS_R3_HIT}} hits overall. Uninformative predictions: {{MS_R3_UNINF_IDS}}.

Second author generator. A second generator was written in a fresh context from a written specification (`docs/INDEPENDENT_GENERATOR_SPEC.md`). Across {{MS_IND_N}} compared verdicts, {{MS_IND_DIFF}} differ. Limit: {{MS_IND_LIMIT}}

## Recorded comparison

Data: the {{REC_DATASET}} navigation recordings (Zenodo record, {{REC_N}} recordings, {{REC_CAL}} for calibration and {{REC_HELD}} held out). The plan was frozen by hash before the one scoring run (`docs/ANALYSIS_PLAN_R3_RECORDED.md`). Five detectors were scored: the monitor M, receiver flags (D-RX), the jamming indicator (D-JAM), position jump (D-JUMP) and a Kalman gate (D-NIS).

{{REC_DET_TABLE}}

{{REC_SYN_TABLE}}

{{REC_NOMINAL}}

Predictions hit: {{REC_P_HIT}} of {{REC_P_TOTAL}} scored (all recordings; see the post hoc section for the held out reading).

Post hoc ({{REC_POST_LABEL}})

{{REC_POST_TABLE}}
 The detail, held out results and the limits are in `docs/RECORDED_RESULTS.md`.

## Discussion

What can be said is narrow. The checker keeps hardware claims open for every item whose evidence is simulated, and the mutation audit shows how much of the earlier hit rate could not have failed. On recorded interference the monitor's false alarm rate was far above the developer's synthetic value, but the post hoc analysis attributes it to a mislabelled segment and to vehicle speed, not to the synthetic error model alone. This holds for one campaign, with under one hour of nominal exposure, and for a receiver velocity standing in for wheel odometry, and it is not a claim about a robot or about the Gulf.

## Threats to validity

Single author. Checkers and coders share a model family with the author, so errors can repeat. Parameters are assumed, not measured. Standards were read at summary level where only summaries were available. The recordings come from Norway and a single receiver type, not from the Gulf or a robot. See `docs/LIMITATIONS.md`. Official items: {{MS_OFFICIAL_N}} checked against official texts by an automated service, of which {{MS_OFFICIAL_OPEN}} are not confirmed and need hand reading (`docs/FETCH_LIST_R3.md`).

## Data and code availability

Repository: https://github.com/hudasol/dhamaan. Licences are proposed until the owner confirms them (`LICENSES.md`). A DOI exists only after the owner makes an archive release. Reproduction on a clean machine takes three commands, given in `README.md` and tested in `tests/test_reproduction.py`.
