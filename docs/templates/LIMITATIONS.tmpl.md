# Limitations

> {{SIM_LABEL}}

We list what the work does not show, where it would break on real data, and findings from review that were not fixed, each with a reason.

## Simulated evidence

- **Same authors.** The worlds and the methods under test share an author. A model can only fail in ways its author thought to include, so HIT verdicts are weak evidence of anything beyond the model.
- **No measurement.** No sensor, robot, receiver or building was measured. The dust model (range loss, dropout, haze, noise), the glare model (angular halo and reflection) and the GNSS error model (white noise, constant odometry bias) are simple stand ins. Real dust is clumped and time varying; real glare depends on optics, exposure control and the detector; real GNSS error is correlated in time and multipath dominated near buildings.
- **Thresholds are proposals.** B_D, T_D, P_G, S_G, T_G, E_N, T_N, Q_N and L_N in the first round, and the guard, the DU3 grid, T_H, Q_H, F_H and M_H in the second, were chosen by us for this study. Nothing in the evidence table fixes them.
- **Resolution.** GNSS detection delays are measured at the fix period, so a delay of zero means detection at the first fix after onset. Rates come from {{SEEDS}} seeds per condition; the Wilson intervals in the result files are wide.
- **Failures stand.** Acceptance criteria that failed: {{AC_FAILED_LIST}}. {{N_RESTRICTIONS}} sun conditions are recorded as restrictions. The monitor in DU3 also stops the robot below the degradation bound in {{DU3_M_EARLY_STOP}} of runs at k = {{DU3_EARLY_STOP_K}}, a cost the preregistration did not measure as a criterion.
- **Recorded replay is one campaign.** N4 in round one used the synthetic receiver's own fixes. The recorded comparison (`docs/RECORDED_RESULTS.md`) replays {{REC_N}} recordings of one controlled campaign in Norway with one receiver type; there is no Gulf site and no robot, odometry is replaced by receiver velocity, the receiver travels in a vehicle at speeds far above a library robot, labels are loose session spans and one recording was found post hoc to have interference outside its labelled span, and nominal exposure is under one hour per detector, so false alarm intervals are wide. Dust, glare and heat have no recorded counterpart.
- **Heat is a model with assumed parameters.** Items H1 to H6 were simulated in the second round with assumed, proposal values; no component was measured and no heat item was run on hardware.
- **Second round failures stand.** Acceptance criteria that failed in the second round: {{R2_AC_FAILED_LIST}} (`docs/EVALUATION_R2.md`).

## Assurance case

- The robot, the library and the ODD are assumed. The case is a structure to fill, not a safety case.
- {{N_OPEN}} of {{N_EVIDENCE_ITEMS}} evidence items are open; {{N_PARTIAL}} are partial with simulated evidence only, and the checker keeps their hardware claims open.
- The checker tests structure, traceability, wording and evidence integrity. It cannot judge whether an argument is sound.

## Evidence table

- The verification of this phase found problems in about a third of rows before correction, and the final check still flagged a similar share after correction (`docs/REPORT.md` section 2.3). Rows are leads to confirm in the source, not citations to rely on.
- The validator reports warnings where a paraphrase mentions a clause style reference while the access level is not full text seen. They are reviewed and explained in `docs/VALIDATOR_WARNINGS.md`.
- Paywalled standards were seen at catalogue or summary level only.

## Review findings not fixed

An independent adversarial review produced {{N_REVIEW}} findings; {{N_REVIEW_FIXED}} were fixed. The others are documented, rejected or left as they are, each with a reason (full register: `docs/data/review_findings.csv`):

{{REVIEW_NOT_FIXED}}
