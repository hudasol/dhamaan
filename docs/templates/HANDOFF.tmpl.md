# Handoff

> {{SIM_LABEL}}

This note closes the phase that turned the repository into a tested evidence engine and produced the first simulated evidence for goals G4 and G6. Numbers here are filled from files by `docsgen/build.py`.

## What changed

| Tag | Phase | Main result |
|---|---|---|
| v0.3.0 | Baseline | Fast check (`make check`, `python tools/fast_check.py`); a Windows test fixture and report line endings fixed |
| v0.4.0 | Architecture | Typed contracts and generated schemas, layer import contract, frozen hash manifest for verification data |
| v0.5.0 | Simulation | Preregistered, seeded synthetic harness for DU3, GL3 and N2 to N4 with results |
| v0.6.0 | Evidence into the case | Evidence kind, artefact and hash fields; checker rules; EV-08 and EV-12 partial (simulated); diagram re rendered |
| v0.7.0 | Docs from data | Generated README and document set, ADRs, doc agreement tests |
| v0.8.0 | Validation | Clause style warnings reviewed as data; strict validation in CI; locator test |
| v0.9.0 | Review | Adversarial review findings fixed or listed below |
| v1.0.0 | Handoff | This note |

Verification results, error rates and the frozen baseline were not changed (`data/frozen_sha256.txt`).

## Test results

Recorded by `python tools/fast_check.py --record` into `docs/data/check_summary.json`:

{{CHECK_LINES}}

Tests passed: {{TESTS_PASSED}}. CI runs the same checks plus `detect-secrets` and renders the diagram.

## Predictions and acceptance criteria

- {{PRED_HIT}} of {{PRED_TOTAL}} predictions hit; missed: {{PRED_MISS_LIST}}.
- Acceptance criteria held: {{AC_HELD_LIST}}. Failed: {{AC_FAILED_LIST}}. The failure of {{AC_EXPECTATION_MISS_LIST}} was not expected.
- {{N_RESTRICTIONS}} sun conditions are recorded as restrictions. Details: `docs/EVALUATION.md`.

## State of the assurance case

{{N_EVIDENCE_ITEMS}} evidence items: {{N_OPEN}} open, {{N_PARTIAL}} partial ({{PARTIAL_LIST}}), {{N_PROVIDED}} provided. Checker: {{CASE_ERRORS}} errors, {{CASE_FLAGS}} flags. Hardware claims supported only by simulation, and therefore still open: {{SIM_ONLY_GOALS}}.

## What the owner must do

These steps need a person and cannot be done from inside the repository.

- **Fetch documents.** Read the full text of the locators listed in `docs/VALIDATOR_WARNINGS.md` and the official items still open in `docs/REPORT.md` Appendix C, through a library or a free official route. Do not commit the texts.
- **Send enquiries.** Review and, if wished, send the draft in `docs/UAE_ENQUIRY_PACK.md`; record replies in `data/uae_enquiry_tracking.csv`. Nothing has been sent.
- **Confirm licences.** Confirm the proposed licences in `LICENSES.md` and the unconfirmed tool and data licences in `data/free_tools_licences.csv` (open weather data, a public GNSS log source) before any pilot stage uses them.
- **Tag a release.** After reading this note, create a GitHub release from tag v1.0.0 with a short plain description.
- **Set About and topics.** Suggested topics: assurance-case, safety-case, robotics, drones, gnss, simulation, preregistration, evidence. Suggested About text:

  > Student proposal seed: source traced evidence table of robot and drone safety rules, a checkable assurance case and preregistered simulated Gulf condition evidence. Not certification.

- **Decide on milestone pull requests.** This phase committed to main (`docs/adr/0010-git-workflow.md`). Say if later phases should use branches and pull requests.

## Open items

- Hardware evidence for every goal; see `docs/PILOT.md` for the stages.
- Heat items H1 to H6 were not simulated.
- N4 with a public log (deviation D1 in `sim/DEVIATIONS.md`).
- The DU3 monitor threshold stops the robot below the degradation bound; a new preregistration should set threshold and bound together.
- The AC-GL2 failure at a saturation just below S_G suggests a hysteresis or margin in the monitor; this needs a new preregistration, not a retune.

## Adversarial review

{{N_REVIEW}} findings, {{N_REVIEW_FIXED}} fixed, {{N_REVIEW_OTHER}} documented, rejected or left with a reason.

{{REVIEW_TABLE}}
