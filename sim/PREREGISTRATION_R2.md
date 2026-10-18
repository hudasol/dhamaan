# Preregistration, round 2: GL3 monitor margin, DU3 threshold and bound, heat H1 to H6, N4 replay harness

Written 2026-10-18 (Asia/Dubai) before any round 2 design or scoring run. Committed and hashed before the first
run; the hashes are in `sim/PREREGISTRATION_R2.sha256.txt`, and `tests/test_prereg_r2.py` fails if this file,
`sim/r2/predictions_r2.py` or `sim/r2/acceptance_r2.py` changes afterwards. Round 1 (`sim/PREREGISTRATION.md`,
`sim/results/`) is frozen and is not rerun, retuned or rescored here. Deviations go in `sim/DEVIATIONS.md`.

**Label.** Everything produced under this plan is SYNTHETIC, evidence kind `simulated`. The worlds and the
methods were written by the same authors. Parameters not taken from a cited source are "assumed, proposal".
Results support no claim about a real robot, sensor, receiver or building, and cannot close a hardware claim.

## Seed sets

- Development seed set, base 770001: design only (choosing the GL3 margin and frames, and the DU3 threshold,
  scan count and bound). Design writes `sim/results_r2/design_gl3.json` and `design_du3.json`, which are
  committed before scoring.
- Held out seed set, base 20261018: scoring only. No design step reads it (checked by `tests/test_sim_r2.py`).
- 30 seeds per condition in both sets. Commands: `python -m sim.r2.run_r2 design`, then
  `python -m sim.r2.run_r2 score`.

## a. GL3: a monitor with a margin (closes nothing, tests a variant)

Round 1 AC-GL2 failed partly because its clock starts on one true frame above S_G while the monitor needed two
measured frames above S_G (deviation D5). Round 2 adds a latched monitor M2 that triggers when measured
saturation exceeds S_G minus a margin for a number of consecutive frames. Candidates: margin 0, 0.03, 0.05,
0.08 and frames 1 or 2. Design rule on the development seeds: among candidates with no AC-GL2 violation and no
slow command where modelled saturation is below the guard (0.2), take the smallest margin, then the larger
frame count; if none qualifies, take the fewest violations. Scoring runs the round 1 monitor (M) and M2 on the
held out seeds. AC-GL2 keeps its round 1 definition.

## b. DU3: threshold and bound together

Round 1 set the bound (0.4) and the monitor threshold (0.6, three scans) separately, and the monitor stopped
the robot below the bound. Round 2 chooses threshold (0.40 to 0.65 in steps of 0.05), scan count (3 or 5) and
bound (0.1 to 0.8) together. New criteria: up to the bound, the detector detects in time and the monitor never
stops the robot (AC-DU1R2); beyond it, the monitor stops the robot within T_D = 1.0 s of onset (AC-DU2R2).
Design rule on the development seeds: the largest bound with no violation, ties to fewer scans then the higher
threshold; if nothing is feasible, the fewest violating runs, then the largest bound. Each run is simulated
once with the detector alone and the scan by scan valid return ratio is recorded, so every candidate is judged
on the same world.

## c. Heat, H1 to H6

A first order thermal model of three components (compute, battery, sensor with range drift) over a two hour
mission near the daily peak; peaks 35, 40, 45 and 50 degC, shade or sun, normal start or start after a sun
soak. All parameters are "assumed, proposal" (`sim/r2/heat.py`), except the 45 degC rated ambient of an example
platform, stated in the dhill README and cited by link. Methods: B0 full scale; B1 a fixed rule that parks the
whole mission when the forecast peak reaches 40 degC; M a predictive controller with margin M_H = 5 K that
parks in place (no shade assumed) when nothing else keeps the prediction below the limits. True parameters
differ from the nominal ones by seeded factors.

## d. N4: replay harness

No public log could be retrieved with the automated retrieval (`docs/FETCH_LIST.md`, decision P3-04). The
harness (`sim/r2/replay.py`) reads logs in the pilot kit CSV format, injects measurement level faults and runs
the round 1 method. Round 2 exercises it on 30 synthetic stand in logs from the round 1 receiver model, written
to CSV and read back. No RF signal is generated, simulated at signal level or described.

## Acceptance values

`sim/r2/acceptance_r2.py`: guard 0.2; DU3 grid as above; T_H = 5 K with Q_H = 0.9; F_H = 1.2; M_H = 5 K;
soak wait threshold 10 minutes. Round 1 values (P_G, S_G, T_G, T_D, E_N, T_N, Q_N, L_N) are reused unchanged.

| Criterion | Statement | Expected |
|---|---|---|
| AC-GL2R2 | M2 commands the slow speed within T_G = 0.5 s of saturation exceeding S_G in every such held out run. | hold |
| AC-GL4R2 | M2 issues no slow command where modelled saturation is below 0.2. | hold |
| AC-GL1R2 | M2 detects in time at rate at least P_G = 0.95 at every sun condition. | fail |
| AC-DU1R2 | Up to the chosen bound, the detector detects in time in every held out run and the chosen monitor never stops the robot. | fail |
| AC-DU2R2 | Beyond the chosen bound, the chosen monitor stops the robot within T_D = 1.0 s of onset in every held out run. | fail |
| AC-H1 | The open loop model predicts each component's mission maximum within T_H = 5.0 K in at least 0.9 of runs, in every condition. | fail |
| AC-H2 | With M, the required stopping distance at heat grows by a factor of at most F_H = 1.2 in every run. | hold |
| AC-H3 | With M, no component exceeds its hard limit in any run. | fail |
| AC-N1R2 | On stand in logs, faults at or above E_N are detected within T_N = 10.0 s in at least Q_N = 0.9 of logs. | fail |
| AC-N2R2 | On stand in logs, the navigation error at the alarm is at most L_N = 3.0 m in every detected case. | hold |

## Predictions

| Id | Prediction |
|---|---|
| GL3R2-P1 | The design rule picks two frames and a margin from 0.03 to 0.05. |
| GL3R2-P2 | On held out seeds the chosen monitor (M2) has no run that breaks AC-GL2. |
| GL3R2-P3 | On held out seeds the round 1 monitor (M) still has at least one run that breaks AC-GL2. |
| GL3R2-P4 | M2 misses P_G in exactly 3 sun conditions, the same low sun cases as round 1. |
| GL3R2-P5 | M2 issues no slow command where modelled saturation is below the guard. |
| DU3R2-P1 | No threshold, scan count and bound in the grid meets both DU3 criteria on the development seeds. |
| DU3R2-P2 | The chosen bound lies from 0.3 to 0.5. |
| DU3R2-P3 | On held out seeds the chosen pair has at most 30 violating runs. |
| DU3R2-P4 | On held out seeds the round 1 pair, judged by the round 2 criteria, has at least 30 violating runs. |
| H-P1 | Full scale (B0) exceeds a limit in at least 90 percent of runs in every sun condition and every shade condition from 45 degC. |
| H-P2 | The controller (M) never exceeds a limit in shade, nor in sun at 35 and 40 degC from a normal start. |
| H-P3 | M exceeds a limit in at least half the runs in sun at 50 degC, where parking in place cannot keep the battery below its limit. |
| H-P4 | After a sun soak at 45 degC or more, M never starts moving in at least 90 percent of runs. |
| H-P5 | In shade at 40 and 45 degC from a normal start, M keeps a mean scale of at least 0.2 while the fixed rule parks. |
| H-P6 | After a soak in shade at 45 degC, M waits at least 10 minutes on average before moving. |
| N4-P1 | The harness raises at most 1 false alarm in 30 nominal stand in logs. |
| N4-P2 | The harness detects loss and jumps of 5 m or more within T_N in every stand in log. |
| N4-P3 | Drift of 0.2 m/s is detected within T_N in at most half the stand in logs. |
| N4-P4 | Replay with 5 s and 10 s delay is detected within T_N in at least 90 percent of stand in logs. |

## Assurance case

Round 2 results enter the case as new evidence items with status `partial`, kind `simulated`, an artefact and
its SHA-256. The checker keeps every hardware claim open while only simulated evidence supports it.
