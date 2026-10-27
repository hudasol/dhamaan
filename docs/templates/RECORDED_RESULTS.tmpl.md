# Recorded comparison on the {{REC_DATASET}} data

> {{REC_LABEL}}

Generated from `sim/results_r3/recorded/` by `docsgen/facts.py`. The design, detectors, split and criteria were fixed in `docs/ANALYSIS_PLAN_R3_RECORDED.md` and frozen by hash (`data/r3_recorded/PLAN_FREEZE.json`) before the scorer was run. The scorer was run once (state: {{REC_STATE}}). Nothing was tuned afterwards.

## What was run

{{REC_N}} recordings, {{REC_CAL}} used for calibration and {{REC_HELD}} held out. The monitor under test (M) is the round one and two code, unchanged. Four baselines read the same data: D-RX (receiver flags), D-JAM (the receiver jamming indicator against a threshold of {{REC_THRESHOLD}} set on calibration recordings), D-JUMP (position jump against receiver velocity) and D-NIS (a constant velocity Kalman filter with a chi square gate). The odometry stream that M needs is the receiver velocity held at ten hertz, not a wheel encoder.

## All recordings

Nominal data are the parts of each recording outside the labelled session and its guard time. Total nominal exposure for M was {{REC_HOURS}} hours.

{{REC_DET_TABLE}}

## Held out recordings only

{{REC_HELD_TABLE}}

## Sessions alarmed by attack type

{{REC_TYPE_TABLE}}

## Synthetic against recorded

{{REC_SYN_TABLE}}

{{REC_NOMINAL}}

## Preregistered predictions

{{REC_PRED_TABLE}}

## Reading

M raised {{REC_M_FA}} false alarms per nominal hour on the recordings (interval {{REC_M_FA_CI}}), against {{REC_M_SYN_FA}} on the synthetic arm built from the developer's parameters. It alarmed in {{REC_M_SESS}} sessions and for {{REC_M_LOSS}} loss of fix events. At its own nominal rate, M would be expected to alarm {{REC_M_CHANCE}} times per session by chance, so session detection alone is weak evidence for M. Of the baselines, {{REC_BEST_BASELINE}} had the lowest false alarm rate.

Limits. One campaign in Norway, one receiver type, no Gulf data and no robot. Labels are session spans, so a missed session may be a session in which the attack had no effect on the receiver. The odometry substitute is derived from the same receiver, so the monitor never sees an independent motion estimate, which is the situation it was designed for; the false alarm result therefore shows how M behaves with this substitute and does not show how it would behave on a robot with wheel odometry. Dust, glare and heat have no recorded counterpart and remain synthetic.
