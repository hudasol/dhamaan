# Pilot kit: replay and scoring walk through

> {{SIM_LABEL}} The logs used on this page are synthetic stand in logs, not recordings; the scoring method is the one preregistered for the second round (SHA-256 `{{R2_PREREG_SHA}}`).

This walk through runs on the stand in log committed in `sim/results_r2/standin_log/`. With a real log in the format of `docs/PILOT_KIT/LOGGING_SPEC.md`, the same commands apply. Every output shown here is produced by the code when the documents are built.

## Install the command (local only)

```
python -m pip install -e .
```

## Score a log without a fault

```
dhamaan score-log --gnss sim/results_r2/standin_log/gnss.csv --odometry sim/results_r2/standin_log/odometry.csv
```

The log has {{KIT_FIXES}} fixes and {{KIT_ODO_ROWS}} odometry rows. Result: {{KIT_CLEAN_RESULT}}. Largest navigation error against the reference columns: {{KIT_CLEAN_MAXERR}} m.

## Make a copy with one injected fault and score it

```
python docs/PILOT_KIT/make_faulty_copy.py sim/results_r2/standin_log/gnss.csv gnss_jump.csv
dhamaan score-log --gnss gnss_jump.csv --odometry sim/results_r2/standin_log/odometry.csv
```

The copy carries a jump injected at the measurement level (software only). Result: {{KIT_FAULT_RESULT}}. Largest navigation error before the declaration: {{KIT_FAULT_MAXERR}} m.

## Check a log of your own

- `dhamaan score-log` rejects a log whose columns or time order do not follow the specification, and says why.
- Add `--json` for a machine readable result to store beside the run.

## Turn a score into evidence

- A score from a stand in log is simulated evidence and closes nothing.
- A score from a log recorded on real equipment can become an evidence item with kind `bench` or `field`: store the result file, record its SHA-256 in the case, and run `dhamaan check-case`. The checker verifies the hash and keeps a hardware claim open while only simulated evidence supports it.
- The scoring parameters are the first round proposal values (assumed, proposal). A partner who wants different thresholds writes a new preregistration before scoring any real log.
