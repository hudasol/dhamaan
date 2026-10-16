# Method

> {{SIM_LABEL}}

This page explains how each part of the repository produces what it claims. Values below are read from the result files and the code by `docsgen/facts.py`.

## Evidence table

The table was built and verified before this phase; the method is in `docs/PROTOCOL.md`, `data/verification/PLAN.md` and `docs/REPORT.md` section 2. In short: each row is a paraphrase of a retrieved source with its URL, retrieval date and the access level the reader actually had (full text seen, summary seen, title only). A clause locator is kept only where a verifier saw it in full text. Three blind verification passes measured the error rate before and after correction. The inputs and results of that verification are frozen by hash (`data/frozen_sha256.txt`, checked by `tests/test_frozen.py`) and this phase did not change them.

## Assurance case and checker

`assurance/library_robot_case.yaml` follows the shape of Goal Structuring Notation: goals, one strategy, contexts, assumptions and evidence items (solutions). Its fields are defined once in `tools/contracts.py`; `schema/assurance_case.schema.json` is generated from that contract. `tools/ac_check.py` reports two severities.

- ERROR (build fails): schema violation, duplicate or dangling id, cycle, orphan goal, evidence item with no source row, absolute or certification wording, an item marked partial or provided without an evidence kind, without an existing artefact or with an artefact whose SHA-256 differs from the recorded one, and simulated evidence marked provided under a hardware claim.
- FLAG (reported, expected while work is open): open, partial or decision needed evidence, weak source rows, undeveloped goals, claims with all evidence open, and hardware claims supported only by simulation.

Every goal states what it is about (`claim_about`: hardware, software, process or argument). Every non open evidence item states how it was produced (`kind`: simulated, bench or field). The rule that simulated evidence never closes a hardware claim is enforced by the checker, not by convention.

## Simulation harness

Protocol items run: DU3 and the software part of DU5, GL3 and the software part of GL5, N2, N3 and a synthetic form of N4. Everything else in `docs/GULF_TEST_PROTOCOL.md` is still a proposal.

**Preregistration.** Questions, hypotheses, baselines, metrics, acceptance values and numeric predictions were written in `sim/PREREGISTRATION.md`, `sim/predictions.py` and `sim/acceptance.py`, hashed and committed before the first evaluation run. `tests/test_prereg.py` fails if those files change. Deviations go in `sim/DEVIATIONS.md` with a date.

**Determinism.** Each run draws from a generator keyed by base seed {{BASE_SEED}}, experiment, condition and seed index. The method is not part of the key, so the baselines and the method face the same world in each seed. {{SEEDS}} seeds per condition. `tests/test_sim_results.py` reruns a subset of conditions and requires byte identical results.

**Stopping model** (shared by DU3 and GL3, proposal values): reaction {{STOP_T_REACT}} s, deceleration {{STOP_DECEL}} m/s2, margin {{STOP_MARGIN}} m. Required distance to the obstacle surface at the nominal speed: {{STOP_REQ_NOMINAL}} m.

### DU3: dust degradation sweep

A planar range sensor with beams from minus to plus {{DU3_FOV_DEG}} degrees every {{DU3_STEP_DEG}} degree, clean range {{DU3_R0}} m and noise {{DU3_SIGMA0}} m, drives along a corridor of half width {{DU3_HALF_WIDTH}} m towards a test cylinder of radius {{DU3_OBSTACLE_RADIUS}} m that starts {{DU3_START_DISTANCE}} m ahead with a lateral offset drawn up to {{DU3_LATERAL_OFFSET}} m. Scans every {{DU3_DT}} s. From {{DU3_T_ONSET}} s, degradation of severity k is applied in software: usable range shrinks by a factor of {{DU3_RANGE_LOSS}} times k, each return is dropped with probability {{DU3_DROP}} times k, a haze term removes far returns with probability rising with range, and range noise grows by {{DU3_NOISE_GAIN}} m times k.

- Detector: at least {{DU3_MIN_POINTS}} returns inside the swept path (half width {{DU3_FOOTPRINT}} m) in {{DU3_CONFIRM_SCANS}} consecutive scans.
- B0: detector at {{DU3_V_NOMINAL}} m/s. B1: detector at {{DU3_V_SLOW}} m/s. M: detector at {{DU3_V_NOMINAL}} m/s plus a monitor that compares returns with the beams the corridor map says should return, and stops the robot when that valid return ratio stays below {{DU3_VRR_THRESHOLD}} for {{DU3_VRR_SCANS}} scans.
- A run is unsafe when the robot reaches the required stopping distance without a confirmed detection or a monitor stop.

### GL3: sun sweep

A forward camera pitched down {{GL3_PITCH_DEG}} degrees. Saturation is a deterministic function of the angle between the camera axis and the sun, with a halo of {{GL3_HALO_DEG}} degrees, plus a reflected sun below the horizon weighted by the reflection coefficient; each frame multiplies it by a seeded flicker of up to {{GL3_FLICKER}} either way. Within {{GL3_CAMERA_RANGE}} m, a frame detects the obstacle with probability {{GL3_P_CLEAN}} times the square of one minus saturation; {{GL3_CONFIRM_FRAMES}} consecutive detections confirm. The robot starts {{GL3_START_DISTANCE}} m from the obstacle surface; frames every {{GL3_DT}} s.

- B0: {{GL3_V_NOMINAL}} m/s throughout. B1: {{GL3_V_SLOW}} m/s throughout. M: {{GL3_V_NOMINAL}} m/s, and when measured saturation (noise {{GL3_MONITOR_NOISE}}) exceeds {{GL3_S_G}} for {{GL3_MONITOR_FRAMES}} frames it commands {{GL3_V_SLOW}} m/s, braking at {{GL3_DECEL}} m/s2.

### N2 to N4: GNSS fault injection

No RF signal is generated or simulated. A robot drives a straight outdoor approach at {{GN_SPEED}} m/s for {{GN_DURATION}} s. Odometry every {{GN_DT}} s has a per run scale error (standard deviation {{GN_ODO_SCALE_SD}}), speed noise {{GN_ODO_SPEED_SD}} m/s and a heading random walk of {{GN_HEADING_RW}} rad per square root second. A position fix arrives every {{GN_FIX_PERIOD_STEPS}} odometry steps with white noise of {{GN_SIGMA_GNSS}} m per axis. A Kalman filter with process noise {{GN_Q_STEP}} m per step fuses the two. From {{GN_T_ONSET}} s one fault is applied to the fix stream: loss, noise growth over {{GN_NOISE_RAMP}} s, a jump, a drift or a replay of the receiver's own fixes from earlier.

- B0 accepts every fix. B1 rejects a fix whose normalised innovation exceeds {{GN_GATE}} (chi square, two degrees of freedom).
- M adds fault declaration: {{GN_REJECT_RUN}} consecutive rejections, a CUSUM of the normalised innovation minus {{GN_CUSUM_BIAS}} above {{GN_CUSUM_LIMIT}}, or no fix for more than {{GN_TIMEOUT}} s, checked at the expected fix times (`sim/DEVIATIONS.md`, D4). After declaration the robot stops using fixes and brakes at {{GN_DECEL}} m/s2 to a stop, the declared safe state.

### Acceptance values (fixed before the runs)

B_D {{B_D}}, T_D {{T_D}} s; P_G {{P_G}}, S_G {{S_G}}, T_G {{T_G}} s; E_N jump {{E_N_JUMP}} m, drift {{E_N_DRIFT}} m/s, noise {{E_N_NOISE}} m, replay {{E_N_REPLAY}} s, any loss; T_N {{T_N}} s, Q_N {{Q_N}}, L_N {{L_N}} m. These name the open symbols of the protocol and are our proposal values, not values from any source.

## Documents

Generated documents (this one included) are filled from data by `docsgen/build.py`. `tests/test_docs.py` fails when a generated document is stale, when a template contains a number typed by hand, when a document with simulation numbers lacks the SYNTHETIC label, and when public text breaks the voice rules.
