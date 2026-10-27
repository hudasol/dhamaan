# Gaps and the plan to close them

Written on 28 October 2026 after reading `docs/LIMITATIONS.md`, `HANDOFF.md`, `docs/PREREG_R3_DRAFT.md`, the simulation code and the checks. Aim: a manuscript that a workshop or conference reviewer can assess, with the monitor compared against real recordings and real baselines.

## What the repository lacks

| Id | Gap | Why a reviewer would object | Can it be closed from here? |
|---|---|---|---|
| G1 | No recorded data for any claim | Every simulation result is written by the authors of the monitor it tests | GNSS part: yes. Dust, glare and heat: no real data found |
| G2 | No baselines beyond the monitor's own gate | A detector is only meaningful against alternatives | Yes for GNSS: receiver quality flags, the receiver's jamming indicator, a position jump gate, an innovation chi square monitor |
| G3 | The study spreads over five topics | The paper has no single claim | Yes: scope the paper to the GNSS question; dust, glare and heat go to an appendix as synthetic and untested |
| G4 | Thresholds are the authors' proposals | Verdicts may follow from the thresholds | Partly: sensitivity audit exists; recorded arm runs the thresholds unchanged and states that |
| G5 | Small samples | Wide intervals | Partly: Wilson intervals, event level counts reported as counts |
| G6 | No Gulf data | The motivation is the Gulf | No. Recorded data come from Norway. Stated as a limit; a Gulf log needs the pilot kit and a person |
| G7 | Registration is not on an independent registry | Preregistration claims are weak | Partly: plan frozen in git before scoring, hash recorded; the owner can still copy it to OSF with the honest label |
| G8 | Evidence table not checked by a human | Error rate comes from one model family | No. Owner item |
| G9 | Related work read at abstract level | Reviewer will find missing papers | Partly: add the recorded data papers and baseline sources actually used |
| G10 | Manuscript is a generated skeleton | Not yet a readable paper | Yes: rewrite the template around the recorded comparison, with figures generated from data |

## Plan

1. Real data: Jammertest 2024 (Zenodo record 15911589), a controlled campaign with jamming, spoofing and meaconing, position fixes at one hertz and the receiver's own radio frequency monitor. Download with a checksum, keep outside the clone, enter the licence as stated on the record.
2. Analysis plan for the recorded arm, frozen in git before any monitor is run on it (`docs/ANALYSIS_PLAN_R3_RECORDED.md`).
3. Code: loader, five detectors (the monitor under test and four baselines), harm rule, scorer, all tested on synthetic fixtures before the freeze.
4. Run once. Report every result, including failures. Deviations go in a log.
5. Regenerate the manuscript around the recorded comparison, with tables and figures from data.
6. Fresh reviewers; fix findings; tag only if every check passes.

## What stays open after this plan

Gulf recordings, a human check of the evidence table, an outside reader, official text reading, enquiries, registry copy, release. These are in `HANDOFF.md`.
