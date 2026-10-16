# Preregistration: simulated evidence for DU3, GL3 and N2 to N4

Written 2026-10-16 (Asia/Dubai) before any evaluation run. Committed and hashed before the first run;
the hash is in `sim/PREREGISTRATION.sha256.txt` and `tests/test_prereg.py` fails if this file,
`sim/predictions.py` or `sim/acceptance.py` changes afterwards. Any later change of design is recorded in
`sim/DEVIATIONS.md` with a date, and the original text here stays as it is.

**Label.** Everything produced under this plan is SYNTHETIC. The worlds (corridor, obstacle, sensors, sun,
GNSS receiver and odometry) and the methods under test were written by the same authors, in this
repository. A result here says how a software model behaves, not how any robot, sensor or receiver
behaves. Evidence kind is `simulated` and it can never close a hardware claim in the assurance case.

## 1. Scope

Only these items of `docs/GULF_TEST_PROTOCOL.md` are run:

| Protocol item | What is run | File |
|---|---|---|
| DU3 sensor degradation sweep | 2D LiDAR model in a corridor, dust as range loss, dropped returns, haze and noise; severity k from 0.0 to 1.0 in steps of 0.1 | `sim/du3_lidar.py` |
| GL3 simulated sun sweep | camera glare model; sun elevation 5, 15, 30, 45, 60 degrees; azimuth to heading 0, 30, 60, 90, 180 degrees; reflection coefficient 0 and 0.5 | `sim/gl3_glare.py` |
| N2 to N4 GNSS fault injection | position fix stream only: loss, noise growth, jump, slow drift, replay of a recorded track | `sim/gnss_n2n4.py` |

N4 in the protocol names replay of recorded public logs. No public log is used here; the replayed track is
the synthetic receiver's own earlier fixes. This is listed as a deviation from the protocol in
`sim/DEVIATIONS.md` and the evidence is labelled simulated, not replayed. No RF signal of any kind is
generated, simulated at signal level or transmitted.

## 2. Questions and hypotheses

- **DU3.** Does obstacle detection keep the required stopping distance as dust degradation grows, and does a
  map based valid return ratio monitor stop the robot when it does not? Hypothesis: detection alone holds
  up to high degradation and fails only when usable range falls below the stopping distance; the monitor
  stops the robot from about k = 0.4 with no stops at k up to 0.2.
- **GL3.** At which sun conditions does camera detection fall below the required rate, and does a
  saturation monitor that commands a slow speed recover it? Hypothesis: failures occur only with low sun
  ahead of the robot; slowing down recovers some but not all of them, and a reflecting floor makes the
  worst cases unrecoverable, which become restrictions.
- **N2 to N4.** Does an innovation gate plus CUSUM plus timeout detect each fault type quickly enough, and
  does the robot stop before its navigation error exceeds the limit? Hypothesis: loss, large jumps,
  replay with a long delay and strong noise growth are found within seconds; slow drift is found late
  because the filter trusts odometry, but the error at the stop stays small for the same reason.

## 3. Methods and baselines

Each experiment compares a simple baseline, the obvious competitor and the method.

| Experiment | B0 (simple) | B1 (obvious competitor) | M (method) |
|---|---|---|---|
| DU3 | detector only at 0.8 m/s | detector only at a fixed 0.4 m/s | detector plus valid return ratio monitor (stop when below 0.6 for 3 scans) at 0.8 m/s |
| GL3 | 0.8 m/s throughout | 0.3 m/s throughout | 0.8 m/s, slow to 0.3 m/s when measured saturation exceeds S_G for 2 frames |
| GNSS | accept every fix | innovation gate rejects single fixes (chi square, 2 dof, 0.999) | gate plus fault declaration (3 consecutive rejections, CUSUM above 25, or no fix for 3 s), then brake to a stop on odometry |

Model and method parameters are the `Config` defaults in each file at the commit of this document.
Stopping model shared by DU3 and GL3: reaction 0.3 s, deceleration 1.0 m/s2, margin 0.2 m
(`sim/common.py`). These are proposal values, not measured.

## 4. Seeds and runs

Base seed 20261016. Each condition uses 30 seeds (indices 0 to 29). The generator for a run is keyed by
experiment, condition and seed index, not by method, so the three methods see the same world in each
seed. One command runs everything: `python -m sim.run_all`. Development tests use base seed 999 and
assert only structure and determinism. A timing run on base seed 999 was made before this document was
committed; its outcomes were not printed or inspected. No parameter is tuned on the evaluation seeds.

## 5. Metrics

Rates are reported with 95 percent Wilson intervals; continuous metrics with mean, a normal 95 percent
interval, median and maximum across seeds.

- DU3: unsafe rate (neither in time detection nor monitor stop before the required distance), in time
  detection rate, monitor stop rate, detection distance, stop time after onset.
- GL3: in time detection rate, unsafe rate, slow command rate, slow command delay after the first frame
  above S_G.
- GNSS: false alarm rate, detection rate, detection within T_N, detection delay, navigation error at
  detection and at the stop, maximum navigation error after onset, rate of runs whose error exceeds L_N.

## 6. Acceptance criteria (values fixed here, `sim/acceptance.py`)

These fill the open symbols of protocol sections 5.4, 6.4 and 7.4. They are our proposal values for a
synthetic study, not values from any source.

| Criterion | Value | Statement |
|---|---|---|
| AC-DU1 | B_D = 0.4 | Up to B_D, the detector alone detects the obstacle in time in every run. |
| AC-DU2 | T_D = 1.0 s | Beyond B_D, the monitor stops the robot in every run within T_D of onset. |
| AC-GL1 | P_G = 0.95 | M detects in time at rate at least P_G at every sun condition. |
| AC-GL2 | S_G = 0.3, T_G = 0.5 s | M commands the slow speed within T_G of saturation first exceeding S_G, in every such run. |
| AC-GL3 | | Every condition that fails AC-GL1 is listed as a restriction. |
| AC-N1 | E_N: jump 5 m, drift 0.2 m/s, noise 5 m, replay 5 s, any loss; T_N = 10 s; Q_N = 0.9 | Faults at or above E_N are detected within T_N in at least Q_N of runs. |
| AC-N2 | L_N = 3.0 m | In every detected case the safe state is reached with navigation error at most L_N. |
| AC-N3 | | Faults below E_N are listed as not covered; missed detections are reported with seeds. |

We expect AC-DU1, AC-DU2, AC-GL2 and AC-N2 to hold, and AC-GL1 and AC-N1 to fail (see predictions GL3-P2
and N-P6). A failed criterion is reported as a failure and stays in the case.

## 7. Predictions

Machine readable form: `sim/predictions.py`, scored by `sim/score.py` into `sim/results/scored.json`.
Each is marked HIT or MISS after the run; misses are kept.

| Id | Prediction |
|---|---|
| DU3-P1 | Detector alone (B0) is never unsafe for k up to 0.9. |
| DU3-P2 | Detector alone (B0) is unsafe in at least 90 percent of runs at k = 1.0. |
| DU3-P3 | Monitor (M) never stops the robot for k up to 0.2. |
| DU3-P4 | Monitor (M) stops the robot in at least 90 percent of runs for k from 0.4. |
| DU3-P5 | M is never unsafe at any level. |
| DU3-P6 | Always slow (B1) is unsafe in at most half the runs at k = 1.0. |
| DU3-P7 | Clean median detection distance (B0, k = 0) lies between 6 and 10 m. |
| GL3-P1 | B0 misses P_G in 2 to 4 of 50 sun conditions (expected 3: low sun ahead). |
| GL3-P2 | M misses P_G in 1 to 3 conditions (expected 2: low sun ahead with a reflecting floor). |
| GL3-P3 | M meets P_G whenever azimuth is at least 30 degrees or elevation at least 30 degrees. |
| GL3-P4 | M issues no slow command where modelled saturation is below 0.2. |
| N-P1 | M false alarm rate in nominal runs is at most 1 in 30. |
| N-P2 | M detects GNSS loss in every run, within 3.5 s. |
| N-P3 | M detects jumps of 5 m or more in every run, mean delay at most 3 s. |
| N-P4 | M detects a 2 m jump in at least 80 percent of runs (at any time). |
| N-P5 | M detects drift of 0.5 m/s within T_N in at least 90 percent of runs. |
| N-P6 | M detects drift of 0.2 m/s within T_N in at most half the runs (expected AC-N1 failure). |
| N-P7 | M detects drift of 0.1 m/s in at least 90 percent of runs, mean delay 15 to 30 s. |
| N-P8 | M detects noise growth to 5 m and 10 m within T_N in at least 90 percent of runs. |
| N-P9 | M detects replay with 5 s and 10 s delay within T_N in at least 90 percent of runs. |
| N-P10 | Accept all (B0) exceeds L_N in at least 90 percent of runs for jumps of 5 m or more and drift of 0.1 m/s or more. |
| N-P11 | Gate only (B1) stays within L_N in at least 90 percent of runs for jumps of 10 m or more. |
| N-P12 | Gate only (B1) exceeds L_N in at least half the runs for drift of 0.1 m/s. |

## 8. What a result can and cannot support

A HIT shows that the software model behaves as we expected; it does not show that a real sensor or
receiver behaves that way. In the assurance case the results can make EV-08 and EV-12 `partial`
with evidence kind `simulated`; they cannot make any item `provided`, and they cannot support a claim
about hardware (enforced by `tools/ac_check.py`). The fault and degradation models are our own and are
checked against nothing real; DU4, GL2 and a logged localisation stack are the hardware steps that would
test them.
