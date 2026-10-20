# Evaluation: preregistered simulation of DU3, GL3 and N2 to N4

> {{SIM_LABEL}}

Every number on this page is read from `sim/results/*.json` by `docsgen/facts.py`. The plan, predictions and acceptance values were committed before the first run (`sim/PREREGISTRATION.md`, SHA-256 `{{PREREG_SHA}}`). Base seed {{BASE_SEED}}, {{SEEDS}} seeds per condition, {{N_RUNS}} runs in total. A second run of `python -m sim.run_all` reproduces every result file byte for byte.

## Summary

- Predictions: {{PRED_HIT}} of {{PRED_TOTAL}} hit, {{PRED_MISS}} missed ({{PRED_MISS_LIST}}).
- Acceptance criteria: {{AC_HELD}} of {{AC_TOTAL}} held ({{AC_HELD_LIST}}); {{AC_FAILED}} failed ({{AC_FAILED_LIST}}). We had expected AC-GL1 and AC-N1 to fail; the failure of {{AC_EXPECTATION_MISS_LIST}} was not expected.
- GL3-P2 is scored HIT because the count of failing conditions fell in the predicted band, but the hypothesis behind it, that slowing down recovers some glare failures, was not supported: the method failed the same conditions as both baselines.
- In the assurance case, these results make EV-08 and EV-12 partial with evidence kind `simulated`. They support no claim about a real robot.

## Predictions and results

{{PRED_TABLE}}

## Acceptance criteria

{{AC_TABLE}}

## DU3: dust degradation sweep

Severity levels: {{DU3_LEVELS}}. B0 is the detector alone, B1 the detector at a fixed slow speed, M the detector plus the valid return ratio monitor.

{{DU3_TABLE}}

Reading. The detector alone kept the stopping distance up to the second highest level and failed at the highest, where usable range falls below the stopping distance ({{DU3_B0_UNSAFE_AT_1}} unsafe). The monitor stopped the robot at every level from the bound upwards, inside the time limit, so AC-DU1 and AC-DU2 held. The cost appears at k = {{DU3_EARLY_STOP_K}}, below the bound: the monitor stopped the robot in {{DU3_M_EARLY_STOP}} of runs although the detector alone would have succeeded. That is an availability loss the preregistration did not ask about, and it suggests the threshold and the bound are not yet consistent.

## GL3: sun sweep

Sun elevations {{GL3_ELEVATIONS}} degrees, azimuths {{GL3_AZIMUTHS}} degrees, reflection coefficients {{GL3_RHOS}}. Conditions below the required rate: B0 {{GL3_B0_FAILS}}, B1 {{GL3_B1_FAILS}}, M {{GL3_M_FAILS}}.

{{GL3_FAIL_TABLE}}

Restrictions recorded under AC-GL3 (conditions where the method stays below the required rate):

{{RESTRICTIONS}}

Reading. All failures are low sun straight ahead, as predicted. Slowing down did not rescue them in this model: B1, which is always slow, failed the same conditions as M. AC-GL2 failed at one condition ({{GL3_AC2_COND}}) whose modelled saturation, {{GL3_AC2_COND_SAT}}, sits just under the threshold; flicker pushed single frames above it, the monitor needs two noisy frames, and the slow command followed in only {{GL3_AC2_COND_CMD}} of those runs, with a worst delay of {{GL3_AC2_COND_DELAY_MAX}} s. A threshold placed at the edge of the operating conditions produces this behaviour, and the criterion starts its clock on one true frame while the monitor needs two measured ones (`sim/DEVIATIONS.md`, D5). The criterion as written is not met, and we report it as a failure.

## N2 to N4: GNSS fault injection

Conditions: {{GN_CONDITIONS}} (sizes in m, m/s, m and s for jump, drift, noise and replay). B0 accepts every fix, B1 gates single fixes, M declares a fault and stops.

{{GNSS_TABLE}}

Faults below the coverage sizes E_N (AC-N3):

{{NOT_COVERED}}

Reading. Loss, large jumps, long delay replay and strong noise growth were found within seconds. Slow drift was found late (mean {{N_DRIFT02_DELAY}} s at the coverage size and {{N_DRIFT01_DELAY}} s below it), which fails AC-N1, as predicted. Because the filter trusts odometry, the navigation error at the stop stayed below L_N in every detected case (AC-N2 held). Read as the protocol words it, with the largest error between onset and the stop, the worst detected run reached {{N_MAX_ERR_BEFORE_STOP}} m, also below L_N (`sim/DEVIATIONS.md`, D2). Two predictions missed. N-P4: the smallest jump was detected in {{N_JUMP2_DET}} of runs against a predicted {{PV_N_P4}} or more; the filter absorbs part of the jump before the CUSUM accumulates. N-P8: noise growth to the coverage size was detected within T_N in {{N_NOISE5_TN}} of runs (mean delay {{N_NOISE5_DELAY}} s) against a predicted {{PV_N_P8}} or more; this miss also makes AC-N1 fail for a second reason. Replay with a short delay was mostly not detected ({{N_REPLAY2_DET}}), but its error stays small. Without a monitor, noise growth to the largest size pushed the error above L_N in {{N_B0_NOISE10_EXCEED}} of runs; the gate alone let slow drift through ({{N_B1_DRIFT01_EXCEED}} above L_N at the smaller drift). The method raised false alarms in {{N_M_NOMINAL_FA}} of nominal runs; counting the fault free period before onset in every condition, it raised {{N_M_ALL_FA_K}} false alarm in {{N_M_ALL_FA_N}} runs. For the slowest drift, {{N_DRIFT005_NEVER}} runs were never detected, and {{N_DRIFT005_EXCEED}} of runs exceeded L_N.

## What these results do not show

- Anything about a real robot, sensor, receiver or building. The models and the methods were written by the same authors, and nothing here was checked against measurement.
- That the thresholds are right. They were fixed before the runs and not tuned; the misses above show where they are weak.
- Heat: no heat item was simulated in this first round. The second round simulated heat with assumed parameters (`docs/EVALUATION_R2.md`).
- RF level GNSS behaviour: faults are injected into the position stream only.

See `docs/LIMITATIONS.md` for the full list and `docs/PILOT.md` for the steps that would test these models on hardware.
