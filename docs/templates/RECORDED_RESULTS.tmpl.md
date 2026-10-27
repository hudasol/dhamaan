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

## Post hoc analysis after review

> {{REC_POST_LABEL}}

An independent review of the frozen run found that the headline false alarm rate of M is not a clean property of the monitor. The frozen tables above stand unchanged. The table below separates the causes. The detector M-q1 is M with the filter process noise raised to one metre; it is a sensitivity probe to show that the result depends on that setting, and it is not a new monitor.

{{REC_POST_TABLE}}

What the review found, in words:

- **One mislabelled recording.** In one recording the trailing nominal segment overlaps real jamming: the receiver loses satellites, the jamming indicator rises and position residuals reach hundreds of metres, while the attack log says the jamming had ended. Session spans in the labels are loose and the plan treats everything outside them as clean. That segment supplies about half of the false alarms of M and all of the false alarms of D-RX and D-JUMP.
- **Receiver motion.** On still receivers M raised no alarm. All its remaining alarms occur while the receiver travels in a vehicle at several metres per second, far above the walking pace its settings were chosen for, with a velocity held between one hertz epochs standing in for wheel odometry. The synthetic arm (a slow robot) and the recorded arm (a fast vehicle) therefore differ in speed as well as in realism, and the false alarm verdict cannot be assigned to the synthetic error model alone.
- **Session detection by M is largely the same mechanism.** With larger process noise M alarms in very few sessions that have no loss of fix event, so the high share of sessions alarmed in the frozen run mostly reflects its false alarm behaviour and is weak evidence of detecting spoofing or meaconing.
- **Loss of fix events.** An alarm up to the re-arm time before the onset counts as a detection, as frozen; events cluster in a few recordings, so the intervals that treat them as independent are too narrow. D-RX alarms on an invalid fix, so its score on events defined by invalid fixes holds by construction.
- **Low nominal exposure.** Only half of the recordings contribute any nominal data, and a rate of zero alarms in this exposure cannot show a rate below the limit with confidence. The AC-N4 verdicts marked True for the baselines are point estimates only.
- **Prediction R3-P6** rests on held out segments where the antenna was moved during the segment; the heavy tail and autocorrelation describe a relocation and not receiver noise. S1 is recalibrated on two still segments with noise far below the monitor's assumed value.
- **Prediction scoring set.** R3-P3, R3-P7, R3-P8 and R3-P9 were scored on all recordings; the plan names the held out set only for some predictions. On the held out set R3-P3 changes outcome.
- **Time base.** The receiver time stamp is GPS time, not UTC; the offset is far below the rounding of the attack log.
- **Freeze evidence.** The freeze is a hash file and a git history written by one author; it is self attested.

## Reading

M raised {{REC_M_FA}} false alarms per nominal hour on the recordings (interval {{REC_M_FA_CI}}), against {{REC_M_SYN_FA}} on the synthetic arm built from the developer's parameters. It alarmed in {{REC_M_SESS}} sessions and for {{REC_M_LOSS}} loss of fix events. At its own nominal rate, M would be expected to alarm {{REC_M_CHANCE}} times per session by chance, so session detection alone is weak evidence for M. The lowest false alarm rate in the frozen run belongs to {{REC_BEST_BASELINE}}, a detector that rarely alarms at all, so the comparison says little.

Limits. One campaign in Norway, one receiver type, no Gulf data and no robot. Labels are session spans, so a missed session may be a session in which the attack had no effect on the receiver. The vehicle speed regime, the loose labels and the post hoc findings above apply. The odometry substitute is derived from the same receiver, so the monitor never sees an independent motion estimate, which is the situation it was designed for; the false alarm result therefore shows how M behaves with this substitute and does not show how it would behave on a robot with wheel odometry. Dust, glare and heat have no recorded counterpart and remain synthetic.
