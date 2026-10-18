# Pilot kit

**Status: proposal.** Material for a partner who wants to turn the repository's simulated evidence into bench and field evidence on a robot they already have. Nothing here has been run on hardware. Nothing is sent to anyone.

| File | What it is |
|---|---|
| `LOGGING_SPEC.md` | What to record, units and rates (generated from data) |
| `schemas/*.schema.json` | JSON schema for each log file (generated) |
| `WALKTHROUGH.md` | Replay and scoring walk through on synthetic stand in logs (generated) |
| `make_faulty_copy.py` | Injects one measurement level GNSS fault into a log copy, for practice |
| `BENCH_SHEETS.md` | Printable bench test sheets for dust, glare and heat |
| `PARTNER_BRIEF.md` | One page brief for a pilot partner |
| `STOP_LIST.md` | Conditions under which a test must not proceed |

Related repositories, linked and not copied: dhill (https://github.com/hudasol/dhill) for heat and dust envelopes and its field test kit; marsad (https://github.com/hudasol/marsad) for GNSS trust states and log replay.
