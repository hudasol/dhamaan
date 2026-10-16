# Dhamaan

**Status: student proposal seed. Not a deployment, not certification, not legal advice, and not endorsed by any entity.** Simulation outputs in this repository are SYNTHETIC and labelled as such.

## Problem

Robot and drone standards and regulations ask a developer for safety evidence before deployment, but they rarely say how much of that evidence is mandatory, and they are mostly silent on learning based autonomy and on Gulf conditions: heat, dust, glare and GNSS degradation. A developer in the UAE therefore has no clear list of what to produce, and no worked example of how Gulf condition evidence would enter a safety case.

## What this repository does

- **Evidence table** (`data/evidence_table.csv`): {{N_ROWS}} source traced rows across {{N_FAMILIES}} instrument families, each with a paraphrase, binding status, access level and source URL. Access level: full text seen {{ACC_FULL}}, summary seen {{ACC_SUMMARY}}, title only {{ACC_TITLE}}.
- **Machine checkable assurance case** (`assurance/library_robot_case.yaml`) for an assumed library service robot: {{N_GOALS}} goals and {{N_EVIDENCE_ITEMS}} evidence items, checked by `tools/ac_check.py`. Today {{N_OPEN}} items are open and {{N_PARTIAL}} are partial with simulated evidence only: {{PARTIAL_LIST}}.
- **Gulf conditions test protocol** (`docs/GULF_TEST_PROTOCOL.md`): a proposal for heat, dust, glare and GNSS degradation evidence.
- **Preregistered simulation harness** (`sim/`): seeded synthetic models for protocol items DU3 (dust degradation sweep), GL3 (sun sweep) and N2 to N4 (measurement level GNSS fault injection, software only). {{SEEDS}} seeds per condition, {{N_RUNS}} runs in total. Of {{PRED_TOTAL}} preregistered predictions, {{PRED_HIT}} hit and {{PRED_MISS}} missed ({{PRED_MISS_LIST}}). Acceptance criteria held: {{AC_HELD_LIST}}; failed: {{AC_FAILED_LIST}}. Details in `docs/EVALUATION.md`.

## Run it

```
python -m pip install pyyaml numpy pytest
python -m sim.run_all
python tools/fast_check.py
```

The first command installs the free dependencies, the second reproduces every simulation result byte for byte from fixed seeds, and the third runs every check (repository guard, table validator, case checker, secrets scan and tests). `make check` runs the third. `python -m docsgen.build` regenerates this file and the other generated documents from the data.

## Diagram

![Assurance case diagram](figures/gsn_library_robot.svg)

Goals are boxes, the strategy is a parallelogram, evidence items are circles. Dashed circles are open. The two filled circles (EV-08, EV-12) are partial with simulated evidence; the checker keeps the hardware claims they touch ({{SIM_ONLY_GOALS}}) open.

## What is real, synthetic and proposal

| Label | What | Where |
|---|---|---|
| Real (documented) | Paraphrases of retrieved sources with URL, date and access level; official source checks; verification results | `data/`, `docs/REPORT.md` |
| Real (interpretation) | Binding scheme, evidence taxonomy, gap statements, always marked as interpretation | `docs/REPORT.md` |
| Synthetic | Every number produced by `sim/`; models and methods share an author | `sim/results/`, `docs/EVALUATION.md` |
| Proposal | The assurance case, the Gulf protocol, acceptance values, the pilot path | `assurance/`, `docs/GULF_TEST_PROTOCOL.md`, `sim/acceptance.py`, `docs/PILOT.md` |

## What this is not

- Not a safety case for any real robot. The robot and the library are assumed.
- Not evidence about hardware. Simulated evidence never closes a hardware claim; `tools/ac_check.py` reports an error if it is marked as doing so.
- Not a copy of any standard. No standard text, paywalled PDF or raw download is committed; `tools/check_repo.py` fails the build if one is.
- Not GNSS interference work. No RF signal is generated, simulated at signal level or transmitted.
- Not endorsed, reviewed or requested by any authority or company.

## Verification of the evidence table

An independent check of all {{N_ROWS}} rows found at least one key column problem in {{ROW_ERR_EITHER}} of rows before correction (95 percent interval {{ROW_ERR_CI}}). After correction the final check still flagged {{PASSC_CHANGED}} of changed rows and {{PASSC_UNCHANGED}} of a sample of unchanged rows. {{N_SINGLE_CHECKED}} rows were corrected from the final reading alone and are labelled single checked. Treat each row as a lead to confirm in the source. See `docs/REPORT.md` section 2.3 and `data/verification/outcome.json`; these files are frozen by hash (`data/frozen_sha256.txt`).

## Documents

`docs/ARCHITECTURE.md` (layers and contracts), `docs/METHOD.md`, `docs/EVALUATION.md`, `docs/LIMITATIONS.md`, `docs/CONTEXT.md` (public sources), `docs/PILOT.md` (path to real data and a real robot test), `docs/SECURITY.md`, `docs/DATA_STATEMENT.md`, `docs/adr/` (decisions), `HANDOFF.md`.

## Licences

Proposed: MIT for code, CC BY 4.0 for documents and data (`LICENSES.md`). These are proposals until the owner confirms them.

## Related projects

Heat and dust modelling: https://github.com/hudasol/dhill. GNSS trust and interference simulation: https://github.com/hudasol/marsad. The protocol links to both and does not copy them.
