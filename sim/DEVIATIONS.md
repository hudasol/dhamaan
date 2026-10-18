# Deviation log

Dated record of every difference between the preregistered plan (`sim/PREREGISTRATION.md`) or the
protocol (`docs/GULF_TEST_PROTOCOL.md`) and what was run. Entries are only added, never edited.

## 2026-10-16, before the first evaluation run

- **D1. N4 uses no public log.** The protocol item N4 names replay of recorded public logs (for example
  open PX4 flight logs). No log was downloaded or used. The replay fault replays the synthetic receiver's
  own earlier fixes, so the result is labelled `simulated`, not `replayed`. Reason: the brief for this
  phase allows software only fault injection, and no public log licence was checked.

## 2026-10-16, after the first evaluation run (found by the review)

None of these entries changes a model, a method, a threshold, a seed or a scored value. The scored file
is byte identical before and after them.

- **D2. AC-N2 metric differs from the protocol wording.** Protocol section 7.4 asks that the safe state
  be reached before the position error exceeds L_n. `sim/predictions.py` (frozen) scores the error at the
  stop instant. A reporting field, `max_error_before_stop_detected`, now gives the largest error between
  onset and the stop in detected runs, so both readings are visible. The criterion is scored as frozen.
- **D3. Pre onset false alarms were listed as missed seeds.** A run in which the method raised an alarm
  before fault onset was counted among the missed detections. Such runs are now listed separately in
  `pre_onset_alarm_seeds`; the detection rates are unchanged.
- **D4. Loss timeout is checked at fix times.** The method declares loss at the first expected fix time
  more than the timeout after the last fix, so with one fix per second the declaration falls a little
  later than the timeout itself. Documents describe it this way; the code is unchanged.
- **D5. AC-GL2 starts its clock on a single true frame above S_G.** The monitor needs two measured frames
  above S_G, so for conditions whose modelled saturation sits just under S_G the criterion is hard to meet
  by construction. The criterion is scored as frozen and its failure stands.
- **D6. Replay delay is converted from seconds to fixes.** The code counted the delay in fixes, which is
  only correct at one fix per second. It now divides by the fix period; at the configured period the
  results are identical.

## 2026-10-18, round 2 (`sim/PREREGISTRATION_R2.md`)

- **D7. The replay harness did not inject noise growth.** In the first held out run of round 2 (commit
  796003f), `sim/r2/replay.py` handled loss, jump, drift and replay but not noise growth, so the noise
  conditions of the N4 stand in logs ran without any fault. This was a defect, not a design choice: the
  preregistration lists noise growth among the faults. The harness now adds the extra noise that makes the
  total grow to the stated size over the round 1 ramp, a test checks that every fault kind changes the fix
  stream, and round 2 scoring was rerun once. No threshold, seed or prediction changed; the first results stay
  in the history at commit 796003f.
- **D8. A helper was added to the replay harness after round 2 scoring.** `sim/r2/replay.py` gained
  `faulty_copy()`, used only by the pilot kit walk through to write a practice log with one injected fault. It
  calls the same `inject()` with a fixed seed and changes no round 2 result; the CI rerun of round 2 checks this.
