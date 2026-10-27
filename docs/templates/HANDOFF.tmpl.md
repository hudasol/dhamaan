# Handoff, third phase

> {{SIM_LABEL}}

This note closes the third phase, which turned the repository into a toolkit a small team can use without help. Numbers here are filled from files by `docsgen/build.py`. Decisions taken during the phase, with reasons, are in `docs/DECISIONS_PHASE3.md`; the plan and budgets in `docs/PLAN_PHASE3.md`.

## What changed

| Tag | Stage | Main result |
|---|---|---|
| v1.1.0 | Second simulation round | Preregistered before any run; GL3 monitor margin, DU3 threshold and bound together, heat H1 to H6, N4 replay harness; EV-19 to EV-21 partial and simulated |
| v1.2.0 | Command | `dhamaan` (check-table, check-case, render, new-case, score-log); a checker rule against goals worded more strongly than their sources bind |
| v1.3.0 | Templates | Indoor campus delivery robot, small survey drone, outdoor ground rover |
| v1.4.0 | Site | Static site built from data, self contained, Arabic summary marked as a draft; manual Pages workflow |
| v1.5.0 | Pilot kit | Logging specification and schemas from data, walk through, bench sheets, partner brief, stop list |
| v1.6.0 | Proposal pack | Three neutral audience briefs and a limits note, generated from data |
| v1.7.0 | Review | Fresh reviewers; findings fixed or recorded in the review register |
| v1.8.0 | Release hygiene | Changelog, citation file, contributing guide, issue templates, regenerated README and this note |

Frozen files, the verification results and every first round simulation result are unchanged (`data/frozen_sha256.txt`, `tests/test_frozen.py`, CI rerun of `sim/results/`).

## Test results

Recorded by `python tools/fast_check.py --record` into `docs/data/check_summary.json`:

{{CHECK_LINES}}

Tests passed: {{TESTS_PASSED}}. CI also reruns both simulation rounds and fails on any changed byte, installs and runs the `dhamaan` command, runs `detect-secrets` and renders the diagram.

## Predictions

{{PRED_VERDICTS}}

Failed acceptance criteria: first round {{AC_FAILED_LIST}}; second round {{R2_AC_FAILED_LIST}}. Outcomes that differed from what was expected in the second round: {{R2_AC_EXPECTATION_MISS_LIST}}. One defect found after the first second round run is logged as deviation D7 (`sim/DEVIATIONS.md`).

## State of the assurance case

{{N_EVIDENCE_ITEMS}} evidence items: {{N_OPEN}} open, {{N_PARTIAL}} partial ({{PARTIAL_LIST}}), {{N_PROVIDED}} provided. Checker: {{CASE_ERRORS}} errors, {{CASE_FLAGS}} flags. Hardware claims supported only by simulation, and therefore still open: {{SIM_ONLY_GOALS}}.

## What the owner must do

These steps need a person and cannot be done from inside the repository. Nothing has been sent to anyone, no account was created and nothing was registered. Each item is open until the owner records it as done here.

1. **Human check of sixty rows.** Read `data/human_check/INSTRUCTIONS.md`, fill `data/human_check/worksheet.csv` from the printed sources, then run the scorer. Until then the error rates come from automated passes of one model family. Status: open.
2. **Hand fetch of official texts.** Read the items in `docs/FETCH_LIST_R3.md` from the printed Official Journal and the GCAA pages; automated extraction did not confirm them. Never commit standard text. Status: open.
3. **Send enquiries A to D.** Drafts are in `docs/UAE_ENQUIRY_PACK.md`. Review each, choose the sender and send. Status: open, nothing sent.
4. **Register the design on OSF.** Use `docs/OSF_REGISTRATION.md` (it carries the hash of the design file). Enter the registration identifier in that file and in `docs/PREREG_R3_DRAFT.md`, and record the AC-N4 limit as written there. The recorded arm has already been run once, frozen by git hash and not by OSF (`docs/ANALYSIS_PLAN_R3_RECORDED.md`); register a copy of that plan with this stated honestly, as a plan frozen in git before the run and not an OSF registration made before it. Status: open.
5. **Find an outside reader.** One person who did not write the work reads the manuscript and the case, and signs a verifier record if they are willing. Status: open.
6. **Confirm licences.** The proposed licences in `LICENSES.md`, the tool and data licences in `data/free_tools_licences.csv`, and the licence of any recording before it enters `data/third_party_manifest.csv`; see `data/gnss_data_options.csv`. Status: open.
7. **Release, Pages and archive.** Create the GitHub release from the tag, set About text and topics, turn on Pages (source GitHub Actions, then start the pages workflow), and enable the Zenodo link so `.zenodo.json` produces a DOI. Add the DOI to `CITATION.cff` afterwards. Status: open.
8. **Review the Arabic summary.** The page `ar.html` (function `arabic_page` in `docsgen/site.py`) is a draft; correct it before sharing the site. Status: open.
9. **Gulf recordings.** The recorded comparison used the public {{REC_DATASET}} data from Norway (`docs/RECORDED_RESULTS.md`). No Gulf recording was used. Obtaining a licensed receiver log from a Gulf site, or a robot log with wheel odometry, would close the largest remaining gap; the same scorer reads any folder in the same layout. Status: open.

Suggested About text, as one line: student proposal seed, source traced safety evidence for robots and drones in Gulf conditions, a checkable assurance case, preregistered simulations, a local command and a pilot kit; not certification. Suggested topics: assurance-case, safety-case, robotics, drones, gnss, simulation, preregistration, evidence, gulf.

Decision taken earlier: work is committed to main (`docs/adr/0010-git-workflow.md`, decision `P3-02`).

## Open items

- Hardware evidence for every goal; the pilot kit (`docs/PILOT_KIT/`) describes the path.
- N4 with a public or field log; the harness ran on stand in logs only.
- DU3: no threshold and bound in the grid met both criteria; a finer severity grid or a different monitor statistic needs a new preregistration.
- Heat: real component limits and a site envelope are needed before any heat result means anything for a robot.
- The regulatory question for indoor and off road service robots in the UAE is unanswered; the enquiry pack is drafted and unsent.

## Review register

{{N_REVIEW}} findings across the two reviews, {{N_REVIEW_FIXED}} fixed, {{N_REVIEW_OTHER}} documented, rejected or left with a reason (`docs/data/review_findings.csv`).

{{REVIEW_TABLE}}
