# Analysis plan: recorded arm of round three

Status: frozen when `data/r3_recorded/PLAN_FREEZE.json` exists. That file holds the SHA-256 of this text and is committed before any detector is run on the recordings. The scorer refuses to run if the hash differs. Changes after the freeze go in `sim/DEVIATIONS.md` and in the manuscript; this text is not edited.

This plan is time stamped by git, not by an independent registry. It supports the claim "the rules were fixed before scoring", and no stronger claim.

## Question

Hypotheses H3 to H5 of `docs/RESEARCH_QUESTION.md`, for the GNSS fault monitor of rounds one and two: does a synthetic fault generator written by the monitor's authors give the same verdicts as recorded interference, and do real baseline detectors do better or worse than the monitor?

## Data

Jammertest 2024 navigation data, Zenodo record 15911589 (Sayyaf, Ortiz, Renaudin), archive `GNSS_DATASET_JAMMING_SPOOFING.tar.gz`, MD5 `c7b00c63bb1ee5db80c7692a2b06e169`, checked on download. The record page states the licence GPL-3.0-or-later. Recorded in Andoya, Norway, September 2024, with controlled jamming, spoofing and meaconing. One u-blox receiver. No recording is stored in this repository. It is downloaded by hand from the record and its MD5 is checked.

A recording is one scenario folder containing `nav_pvt.csv`, `mon_rf.csv` and `scenario.json`. The folder path is the recording identifier (two folders share the scenario number 3.2.8, so the number alone is not an identifier).

## Streams

- Fixes: one per row of `nav_pvt.csv`, at about one hertz. A fix is valid when `fixType` is at least 3 and `numSV` is at least 4. Latitude and longitude in the files are degrees times one tenth of a millionth, stored as if already scaled; the degrees are the stored value times ten million (checked against the stated site, about 69.2 N and 15.9 E). Local frame: east and north metres on a sphere of radius 6371008.8 m around the first valid fix of the recording.
- Odometry substitute: the receiver's own velocity (`velN`, `velE`), speed and heading, held between epochs and held at the last valid value when no fix is valid. This is not independent hardware. It tests position against velocity from the same receiver, a mapping assumption stated in the paper.
- Radio frequency monitor: `jamInd_01` and `jamInd_02` from `mon_rf.csv`. The receiver's `jammingState` is zero in nearly every row, so it is not used.
- Time: `real_time` is read as UTC. Times in `scenario.json` attack logs are local time and are shifted back by two hours. Seen before this plan was frozen: with that shift the denial of fix in the scenario 1.11.8 falls inside its window.

## Windows

For each recording, attack events whose text contains "start" are paired in order with events containing "end". The session span is from the first start to the last end. If the counts differ the recording is excluded and listed.

Attack types follow `scenario.json` attack type, mapped to jamming, spoofing, meaconing and combined. The text of the logs for spoofing recordings names jamming times, so a session span brackets the test activity and does not mark exact spoofing times. Detection is therefore scored at session level and nothing here claims a detection delay from a known fault onset, except for loss of fix below.

Nominal data are the part of a recording before the session start minus 120 s and after the session end plus 120 s. Time between the first start and last end is never nominal. Nominal segments shorter than 60 s are dropped and counted.

## Detectors

All detectors run on the same streams. After an alarm a detector is restarted from a fresh state 30 s later; alarms are a list of times, so a recording can have several.

- M: the monitor under test. `sim/r2/replay.score_log` with `Config()` of `sim/gnss_n2n4.py` unchanged (gate, CUSUM, three consecutive rejections, fix timeout of 3 s). The code hash is recorded at scoring.
- D-RX: receiver quality flags, what a robot gets without any monitor. Alarm at the first epoch where the fix is not valid or `hAcc` exceeds 10 m.
- D-JAM: the receiver radio frequency indicator. Alarm when the larger of `jamInd_01` and `jamInd_02` exceeds a threshold for three consecutive rows. The threshold is the 99.9th percentile of that value over the nominal rows of the calibration recordings.
- D-JUMP: plausibility gate. Between consecutive valid fixes at most 2.5 s apart, alarm when the displacement minus the velocity times the interval exceeds 5 m (the jump size E_N of `sim/acceptance.py`).
- D-NIS: innovation chi square monitor of the usual kind, independent of the odometry substitute. Four state constant velocity Kalman filter, measurement noise 1 m, acceleration noise 0.5 m/s squared, first five fixes accepted, gate 13.82 (two degrees of freedom, 0.999), alarm after three consecutive rejections.

Receiver autonomous integrity monitoring on pseudoranges is not run: the files have no ephemerides for it. That is a stated limit, not a result.

## Arms and split

- R: the recordings. A seeded draw with seed 20261028 puts 12 of the recordings in a calibration set and 12 in a held out set before any metric is computed. Detectors are not tuned; only D-JAM takes a threshold from the calibration set and the synthetic arm S1 takes its noise model from it.
- S0: the synthetic stand in logs and faults of rounds one and two (`sim/r2/replay.standin`, `inject`) with the unchanged monitor, 100 logs per condition.
- S1: the same after the fix error is replaced by a process with the standard deviation, lag one correlation and excess kurtosis measured on the calibration nominal data (`sim/r3/recorded.py`).

Nominal error statistics for the calibration come from leading nominal segments with at least 60 valid epochs and a median reported speed below 0.3 m/s: error is the position minus the segment median.

## Measures (per detector)

1. False alarms per hour of nominal data: alarms in nominal segments over nominal seconds minus 30 s after each alarm. Exact Poisson interval.
2. Session detection: the share of sessions with at least one alarm inside the session span, by attack type, with Wilson intervals; the time from session start to the first alarm; alarms per session; and the alarms expected in the session if the nominal false alarm rate held.
3. Loss of fix: an event is a run of at least five consecutive invalid epochs inside a session. It is detected in time if an alarm falls between 30 s before its start and 10 s after (T_N of `sim/acceptance.py`).
4. Nominal error statistics of the fixes (standard deviation, lag one correlation, excess kurtosis) on held out nominal segments.

Navigation error at the alarm (AC-N2) is not evaluable: the recordings carry no reference trajectory. It is reported as not evaluable for the recorded arm.

## Criteria and verdicts

- AC-N1 on S0 and S1: the ten covered faults of `sim/r3/recorded.COVERED`, each detected within T_N in at least 0.9 of logs (Q_N).
- AC-N1r on R: loss of fix events detected in time in at least 0.9 of events, and sessions without a loss event having an alarm in at least 0.9 of sessions. Both parts must hold. The second part is lenient and is read with the chance expectation above.
- AC-N4: false alarms per nominal hour at most 1.0 on every arm. The value is set now, from the synthetic arm showing no false alarm in its nominal exposure; it is a proposal value like the other thresholds.

## Predictions (written before any run on the recordings)

| Id | Prediction |
|---|---|
| R3-P1 | The verdict of at least one of AC-N1 and AC-N4 differs between S0 and R on held out recordings. |
| R3-P2 | The false alarm rate of M per nominal hour on R is higher than on S0. |
| R3-P3 | The share of spoofing sessions in which M alarms is lower than the share of jamming sessions. |
| R3-P4 | The false alarm rate of M on S1 is closer to its rate on R than the rate on S0 is. |
| R3-P5 | S1 reproduces the verdicts of R on AC-N1 and AC-N4 (strict form). |
| R3-P6 | On held out nominal segments the fix error has excess kurtosis above 1 and lag one correlation above 0.3. |
| R3-P7 | D-RX alarms in a smaller share of spoofing and meaconing sessions than M. |
| R3-P8 | D-JAM alarms in a smaller share of meaconing sessions than M. |
| R3-P9 | No detector satisfies both parts of AC-N1r and AC-N4 on all recordings. |

Predictions that cannot be scored because a set is empty are reported as not scored.

## Reading rules

- Every number is reported, including failures. Counts are given beside rates.
- Held out results carry the verdicts; results on all recordings are also shown. Detectors are fixed, so the split matters only for D-JAM and S1.
- One campaign, one receiver, one country. No Gulf claim is made.
- A detector that alarms during every session and never in nominal data is still bounded by the lenient session rule and the small nominal exposure; the manuscript states the exposure.
- Labels are session spans. A missed spoofing session may mean the spoofing had no effect on this receiver at that time.

## What was seen before the freeze

The dataset README; the folder tree; `scenario.json` and `info.txt` of every recording; for every `nav_pvt.csv` the row count, time span, `fixType` counts, `numSV` range, position range, largest speed and median `hAcc`; the set of `jammingState` values and the first `mon_rf` row; and for the recording 2.6.1 a per minute table of displacement from the median of its first two minutes, speed, accuracy, satellite count and fix type. No detector or criterion was computed on these data before this text was frozen.

Also seen before the freeze, while testing the loader: the session span, the segment bounds and the number of denial events of the first three recordings. No detector output was seen.
