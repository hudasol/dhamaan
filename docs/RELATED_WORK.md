# Related work and prior art check

Status: first pass, 20 Oct 2026. The list is in `data/related_work.csv` (43 sources). Most pages were read through page summaries or abstracts, not as full original text, and paywalled standards could not be read. Every claim below must be checked against the original source before it is cited in a paper. Absence of a work here means absence from our searches only.

## Question tested

Our first formulation asked how much of a safety claim simulated evidence can carry where regulation is silent on environmental conditions, and what must be shown about the simulator before a case may count it. The search was run to find out how much of that is already done.

## Verdicts by hypothesis

| Hypothesis | Verdict | Closest sources | What remains |
|---|---|---|---|
| Regulation delegates environmental conditions to the developer (silence by delegation) | Partly known | S24 (a technical report on testing under a robot safety standard: the manufacturer selects tests and parameters), S23 (SORA Annex A: the applicant states limits), S27 (an ODD specification standard: the developer writes the ODD) | A stated finding across robot standards, for Gulf heat, dust, glare and GNSS. This is an audit task. Climatic classes and test severity standards may fix values; that check is still needed. |
| Admissibility conditions for simulation can be written as checkable conditions | Largely done | S05 (risk based credibility framework, 2026), S06 (admissibility ladder for learned simulators, 2026), S01 and S03 (NASA credibility scale; a risk based framework for computational models), S12 (independent verification and validation) | Writing them as binary checks inside an assurance case, for robots. Two recent papers with similar vocabulary is a risk of overlap. |
| Applying such conditions to the author's own simulation | New as a move, thin as a result | S12, S01, S15 | The outcome is predictable from the frameworks and is circular unless the conditions come from outside and a second person scores. Reported as a limitation, not a hypothesis. |
| Replay of recorded logs changes verdicts compared with synthetic faults | Partly known | S32 (real versus simulated sensor anomalies differ, glare among the worst), S38 (detection evaluated on real attack traces and on lab emulated data), S04 | No study found that shows an assurance verdict flipping between recorded and synthetic faults for a robot, and none specific to the Gulf. |

## Consequence for the research question

The general framework question is taken. The question in `docs/RESEARCH_QUESTION.md` therefore adopts external conditions (S01, S03, S05, S06, S12) and tests one empirical claim: whether the verdicts agree between synthetic and recorded GNSS interference for the same monitor.

## Closest works

| Id | Work | Why close |
|---|---|---|
| S05 | Risk based credibility framework for virtual testing of automated driving, 2026 | Assumptions, verification and validation, sensitivity, thresholds that depend on use |
| S06 | Admissibility ladder for learned simulators, 2026 | Uses the term admissibility; the abstract does not state rung criteria |
| S07 | Statistical foundation for scenario based testing, 2025 | Statistical fidelity metric |
| S01, S03 | NASA credibility scale; risk based credibility for computational models | Origin of the conditions we adopt |
| S32 | Sim to real benchmark for autonomous driving | Real versus simulated sensor anomalies differ |
| S37 | Open GNSS dataset with interference and spoofing | A free source of recorded interference, from outside the Gulf |
| S40 | Trade press report on GNSS interference in the Gulf, 2026 | Context that Gulf interference is reported; no logs published |

## Limits of this check

- Page summaries can misstate details. Quote nothing from this list without opening the source.
- Some years are inferred from page text and are marked in the table.
- Two sources could not be read (bot protection) and one preprint hit a rate limit; its abstract came from a third party page.
- Standards behind paywalls (the robot safety family, UL 4600, the SORA main body, IEC climatic classes) were seen through abstracts, previews and secondary summaries only.
