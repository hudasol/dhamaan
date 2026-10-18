# Evaluation, second round: GL3 margin, DU3 threshold and bound, heat H1 to H6, N4 replay harness

> {{SIM_LABEL}}

Every number on this page is read from `sim/results_r2/*.json` by `docsgen/facts.py`. The plan, predictions, acceptance values and design rules were committed before any second round run (`sim/PREREGISTRATION_R2.md`, SHA-256 `{{R2_PREREG_SHA}}`). Design used the development seed set (base {{R2_DEV_SEED}}); scoring used the held out seed set (base {{R2_HELDOUT_SEED}}), {{R2_SEEDS}} seeds per condition, {{R2_N_RUNS}} scored method runs. First round results in `sim/results/` are unchanged. One defect found after the first run of the second round is logged as deviation D7 in `sim/DEVIATIONS.md`. Parameters not taken from a cited source are "assumed, proposal".

## Summary

- Predictions: {{R2_PRED_HIT}} of {{R2_PRED_TOTAL}} hit, {{R2_PRED_MISS}} missed ({{R2_PRED_MISS_LIST}}).
- Acceptance criteria: {{R2_AC_HELD}} of {{R2_AC_TOTAL}} held ({{R2_AC_HELD_LIST}}); {{R2_AC_FAILED}} failed ({{R2_AC_FAILED_LIST}}). Outcomes that differed from what we expected: {{R2_AC_EXPECTATION_MISS_LIST}}.
- In the assurance case, the second round adds EV-19, EV-20 and EV-21 as partial with evidence kind `simulated`. They support no claim about a real robot.

## Predictions and results

{{R2_PRED_TABLE}}

## Acceptance criteria

{{R2_AC_TABLE}}

## GL3: monitor with a margin

The design rule tried {{R2_GL_CANDIDATES}} candidates on the development seeds; {{R2_GL_OK}} met both conditions, and the rule chose a margin of {{R2_GL_MARGIN}} below S_G with {{R2_GL_FRAMES}} frame. On the held out seeds the first round monitor still broke AC-GL2 in {{R2_GL_M_VIOL}} runs, while the chosen monitor broke it in {{R2_GL_M2_VIOL}} and raised no false slow down below the guard. Slowing down still does not rescue the low sun conditions: the chosen monitor misses P_G in {{R2_GL_M2_BELOW}} conditions, which stay recorded as restrictions. We predicted two frames; the rule chose one, so GL3R2-P1 is a miss.

## DU3: threshold and bound together

Of {{R2_DU_GRID}} combinations of threshold, scan count and bound, {{R2_DU_FEASIBLE}} met both criteria on the development seeds, as predicted. The fallback rule chose threshold {{R2_DU_THRESHOLD}}, {{R2_DU_SCANS}} scans and bound {{R2_DU_BOUND}}, with {{R2_DU_DEV_VIOL}} violating development runs. On the held out seeds the first round pair, judged by the second round criteria, had {{R2_DU_M_TOTAL}} violating runs ({{R2_DU_M_BELOW}} of them stops below the bound); the chosen pair had {{R2_DU_M2_TOTAL}} ({{R2_DU_M2_BELOW}} below the bound and {{R2_DU_M2_ABOVE}} above it). Both DU3 criteria therefore still fail. Reading: in this model the change in the valid return ratio between adjacent severity levels is too small, relative to its scan to scan spread, for any threshold to separate "never stop" from "always stop within one second".

## Heat, H1 to H6

All parameters are assumed, proposal values (`sim/r2/heat.py`); the only cited figure, a rated ambient of {{R2_HEAT_RATED}} degC for an example platform, comes from the dhill README and only places the hottest condition above a rating.

{{R2_HEAT_TABLE}}

Reading. The full scale baseline exceeds a limit almost everywhere. The fixed rule avoids exceedances only in shade from a normal start, and only by parking the whole mission. The predictive controller keeps every limit from a normal start in shade, at a reduced scale. Two things it cannot fix in this model. First, in sun the sensor heats above its limit even when parked, because its power does not fall with the scale and parking in place gives no shade. Second, a start after a soak can begin above a limit; in {{R2_HEAT_SOAK_EXCEED_CONDS}} of {{R2_HEAT_SOAK_CONDS}} soak conditions the controller had an exceedance, mostly inherited from the starting temperature. We did not foresee the first effect at the lower peaks, so H-P2 is a miss. Both effects point to protocol items that need hardware: shade or cooling as a response, and a limit register with real component limits (H2).

## N4: replay harness on stand in logs

{{R2_N4_TABLE}}

Reading. The harness reads logs in the pilot kit format and reproduces the first round pattern on stand in logs: loss, large jumps, long delay replay and strong noise growth are found within seconds, while slow drift is found late. At the slowest drift the error at the alarm exceeded L_N in the worst log, so AC-N2R2 failed, which we had not expected. No public or field log was replayed (`docs/FETCH_LIST.md`).

## What these results do not show

- Anything about a real robot, sensor, receiver or building.
- That the second round thresholds or the heat parameters are right; they are proposals.
- RF level GNSS behaviour; faults are injected into the position stream only.
