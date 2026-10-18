# Dhamaan

**Status: student proposal seed. Not a deployment, not certification, not legal advice, and not endorsed by any entity; no contact has been made.** Simulation outputs in this repository are SYNTHETIC and labelled as such.

## Problem

Robot and drone standards and regulations ask a developer for safety evidence before deployment, but they rarely say how much of that evidence is mandatory, and they are mostly silent on learning based autonomy and on Gulf conditions: heat, dust, glare and GNSS degradation. In the sources reviewed, a developer in the UAE finds no clear list of what to produce, and no worked example of how Gulf condition evidence would enter a safety case.

## What this repository does

- **Evidence table** (`data/evidence_table.csv`): {{N_ROWS}} source traced rows across {{N_FAMILIES}} instrument families, each with a paraphrase, binding status, access level and source URL. Access level: full text seen {{ACC_FULL}}, summary seen {{ACC_SUMMARY}}, title only {{ACC_TITLE}}.
- **Machine checkable assurance case** (`assurance/library_robot_case.yaml`) for an assumed library service robot: {{N_GOALS}} goals and {{N_EVIDENCE_ITEMS}} evidence items, checked by `tools/ac_check.py`. Today {{N_OPEN}} items are open and {{N_PARTIAL}} are partial with simulated evidence only: {{PARTIAL_LIST}}.
- **Case templates** (`assurance/templates/`): {{N_TEMPLATES}} unnamed robot types, every item open.
- **Gulf conditions test protocol** (`docs/GULF_TEST_PROTOCOL.md`): a proposal for heat, dust, glare and GNSS degradation evidence.
- **Preregistered simulation, first round** (`sim/`, preregistration SHA-256 `{{PREREG_SHA}}`, evidence kind simulated): DU3, GL3 and N2 to N4. {{SEEDS}} seeds per condition, {{N_RUNS}} runs. {{PRED_HIT}} of {{PRED_TOTAL}} predictions hit; missed: {{PRED_MISS_LIST}}. Acceptance criteria held: {{AC_HELD_LIST}}; failed: {{AC_FAILED_LIST}}. The second round showed that the first round DU3 monitor, judged by stricter criteria, stops the robot below its bound (`docs/EVALUATION_R2.md`). Details in `docs/EVALUATION.md`.
- **Preregistered simulation, second round** (`sim/r2/`, preregistration SHA-256 `{{R2_PREREG_SHA}}`, evidence kind simulated): GL3 monitor margin, DU3 threshold and bound together, heat H1 to H6 with assumed parameters, and a log replay harness on stand in logs. Design on development seeds, scoring on held out seeds. {{R2_PRED_HIT}} of {{R2_PRED_TOTAL}} predictions hit; missed: {{R2_PRED_MISS_LIST}}. Acceptance criteria failed: {{R2_AC_FAILED_LIST}}. Details in `docs/EVALUATION_R2.md`.
- **The `dhamaan` command** (`dhamaan/`): `check-table`, `check-case`, `render`, `new-case` and `score-log`, local only, no network.
- **Static site** (`docsgen/site.py`): the evidence table, coverage matrix, an interactive case diagram, evaluations, limits and an Arabic summary marked as a draft; published only when the owner turns on Pages.
- **Pilot kit** (`docs/PILOT_KIT/`) and **proposal pack** (`docs/PROPOSAL/`).

## Run it

```
python -m pip install -e .
python -m sim.run_all
python tools/fast_check.py
```

The first command installs the command and its free dependencies from this clone (editable install only), the second reproduces the first round results byte for byte from fixed seeds (`python -m sim.r2.run_r2 design` and `python -m sim.r2.run_r2 score` do the same for the second round), and the third runs every check (repository guard, table validator, case checker, secrets scan and tests). `make check` runs the third. `python -m docsgen.build` regenerates the generated documents and `python -m docsgen.site ../dhamaan_site` builds the site into a folder outside the clone (the repository guard rejects HTML inside it).

## Diagram

![Assurance case diagram](figures/gsn_library_robot.svg)

Goals are boxes, the strategy is a parallelogram, evidence items are circles. Dashed circles are open. The filled circles ({{PARTIAL_IDS}}) are partial with simulated evidence; the checker keeps the hardware claims they touch ({{SIM_ONLY_GOALS}}) open.

## What is real, synthetic and proposal

| Label | What | Where |
|---|---|---|
| Real (documented) | Paraphrases of retrieved sources with URL, date and access level; official source checks; verification results | `data/`, `docs/REPORT.md` |
| Real (interpretation) | Binding scheme, evidence taxonomy, gap statements, always marked as interpretation | `docs/REPORT.md` |
| Synthetic | Every number produced by `sim/`; models and methods share an author | `sim/results/`, `sim/results_r2/`, `docs/EVALUATION.md`, `docs/EVALUATION_R2.md` |
| Proposal | The assurance case and templates, the Gulf protocol, acceptance values, heat parameters, the pilot path | `assurance/`, `docs/GULF_TEST_PROTOCOL.md`, `sim/acceptance.py`, `sim/r2/acceptance_r2.py`, `docs/PILOT.md`, `docs/PILOT_KIT/` |

## What this is not

- Not a safety case for any real robot. The robot and the library are assumed.
- Not evidence about hardware. Simulated evidence never closes a hardware claim; `tools/ac_check.py` reports an error if it is marked as doing so.
- Not a copy of any standard. No standard text, paywalled PDF or raw download is committed; `tools/check_repo.py` fails the build if one is.
- Not GNSS interference work. No RF signal is generated, simulated at signal level or transmitted.
- Not endorsed, reviewed or requested by any authority, company or institution.

## Verification of the evidence table

A separate blind check of all {{N_ROWS}} rows found at least one key column problem in {{ROW_ERR_EITHER}} of rows before correction (95 percent interval {{ROW_ERR_CI}}). After correction the final check still flagged {{PASSC_CHANGED}} of changed rows and {{PASSC_UNCHANGED}} of a sample of unchanged rows. {{N_SINGLE_CHECKED}} rows were corrected from the final reading alone and are labelled single checked. Treat each row as a lead to confirm in the source. See `docs/REPORT.md` section 2.3 and `data/verification/outcome.json`; these files are frozen by hash (`data/frozen_sha256.txt`).

## Documents

`docs/ARCHITECTURE.md` (layers and contracts), `docs/METHOD.md`, `docs/EVALUATION.md`, `docs/EVALUATION_R2.md`, `docs/LIMITATIONS.md`, `docs/CONTEXT.md` (public sources), `docs/PILOT.md` and `docs/PILOT_KIT/`, `docs/PROPOSAL/`, `docs/SECURITY.md`, `docs/DATA_STATEMENT.md`, `docs/FETCH_LIST.md`, `docs/adr/` and `docs/DECISIONS_PHASE3.md` (decisions), `CHANGELOG.md`, `CONTRIBUTING.md`, `HANDOFF.md`.

## Licences

Proposed: MIT for code, CC BY 4.0 for documents and data (`LICENSES.md`). These are proposals until the owner confirms them. How to cite: `CITATION.cff`.

## Related projects

Heat and dust modelling: https://github.com/hudasol/dhill. GNSS trust and interference simulation: https://github.com/hudasol/marsad. The protocol links to both and does not copy them.
