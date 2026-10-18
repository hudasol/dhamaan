# Plan, phase 3

Session window: about five hours, unattended. The stage budgets in the brief add up to more than five hours, so each stage below has a compressed budget; cuts are recorded in `docs/DECISIONS_PHASE3.md` as they happen. The last 45 minutes are reserved for S7 and S8 whatever happens.

| Stage | Content | Budget (min) | Tag |
|---|---|---|---|
| Start | Pull, fast check, read handoff and ADRs, this plan, decisions log | 15 | |
| S1 | Round 2 simulation: preregistration first; GL3 monitor variant; DU3 threshold and bound set together; heat items H1 to H6; N4 replay harness | 80 | v1.1.0 |
| S2 | `dhamaan` command line tool (check-table, check-case, render, new-case, score-log); binding strength rule | 40 | v1.2.0 |
| S3 | Three unnamed case templates | 25 | v1.3.0 |
| S4 | Static website built by docsgen; Pages workflow | 45 | v1.4.0 |
| S5 | Pilot kit | 25 | v1.5.0 |
| S6 | Proposal pack, generated from data | 20 | v1.6.0 |
| S7 | Independent review by fresh reviewers; fixes; full checks; CI on Linux | 30 | v1.7.0 |
| S8 | Release hygiene; regenerated README and HANDOFF | 15 | v1.8.0 |

Rules carried forward: frozen files stay frozen (`data/frozen_sha256.txt`); every v1.0.0 simulation result stays as it is and new results go in `sim/results_r2/`; a new preregistration is the only way to change a threshold; layers stay tools, then sim, then docs; every number in a generated document comes from a data file.
