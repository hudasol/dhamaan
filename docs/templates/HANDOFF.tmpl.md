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

These steps need a person and cannot be done from inside the repository. Nothing has been sent to anyone.

- **Fetch documents.** Everything in `docs/FETCH_LIST.md`: a public GNSS log with a clear licence for N4, the official items in `docs/REPORT.md` Appendix C, and the locators in `docs/VALIDATOR_WARNINGS.md`. Fetch by hand; never commit standard text.
- **Confirm licences.** The proposed licences in `LICENSES.md` (MIT for code, CC BY 4.0 for documents and data), the unconfirmed tool and data licences in `data/free_tools_licences.csv`, and the licence of any public log before it enters `data/third_party_manifest.csv`. dhill has no licence selected; nothing is copied from it.
- **Create the release.** No GitHub release was created. Suggested release from tag v1.8.0, titled "dhamaan v1.8.0, third phase":

  > Student proposal seed. This release adds a second preregistered simulation round ({{R2_PRED_HIT}} of {{R2_PRED_TOTAL}} predictions hit; failed criteria {{R2_AC_FAILED_LIST}}), the dhamaan command, three case templates, a static site, a pilot kit and a proposal pack. Simulated results are SYNTHETIC and close no hardware claim. Not certification and not endorsed by any body. Licences are proposed until confirmed.

- **Set About and topics.** Suggested About text:

  > Student proposal seed: source traced safety evidence for robots and drones in Gulf conditions, a checkable assurance case, preregistered simulations, a local command and a pilot kit. Not certification.

  Suggested topics: assurance-case, safety-case, robotics, drones, gnss, simulation, preregistration, evidence, gulf.
- **Turn on Pages.** In the repository settings, under Pages, set the source to GitHub Actions, then start the "pages" workflow from the Actions tab. Until then nothing is published.
- **Review the Arabic summary.** The page `ar.html` (source in `docsgen/site.py`, function `arabic_page`) is a draft for owner review; correct it before sharing the site.
- **Decide on milestone pull requests.** This phase committed to main (`docs/adr/0010-git-workflow.md`, decision `P3-02`).

## Open items

- Hardware evidence for every goal; the pilot kit (`docs/PILOT_KIT/`) describes the path.
- N4 with a public or field log; the harness ran on stand in logs only.
- DU3: no threshold and bound in the grid met both criteria; a finer severity grid or a different monitor statistic needs a new preregistration.
- Heat: real component limits and a site envelope are needed before any heat result means anything for a robot.
- The regulatory question for indoor and off road service robots in the UAE is unanswered; the enquiry pack is drafted and unsent.

## Review register

{{N_REVIEW}} findings across the two reviews, {{N_REVIEW_FIXED}} fixed, {{N_REVIEW_OTHER}} documented, rejected or left with a reason (`docs/data/review_findings.csv`).

{{REVIEW_TABLE}}
