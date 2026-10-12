# Dhamaan

Research on the safety evidence that robot and drone standards and regulations ask a developer to produce before deployment, which of those asks are mandatory, and where they are silent (learning based autonomy, and Gulf conditions: heat, dust, glare, GNSS degradation).

This is research. It is not certification, legal advice or an endorsement by any authority. Draft status: second edition, 12 October 2026. Licences are proposals until the owner confirms them (see `LICENSES.md`).

## What is documented

Statements below are things retrieved sources say, recorded as short paraphrases with a source URL, a retrieval date and an access level.

- `data/evidence_table.csv`: 222 rows. Each row has the instrument, edition, binding status (mandatory, conditional, voluntary, guidance), a paraphrased requirement, the source URL and the access level (full text seen, summary seen, title only). A clause locator is kept only where full text was seen and a verifier saw it; otherwise it sits in `clause_reported_unverified`.
- `data/coverage_matrix.csv`: instrument families against 15 evidence types (E01 to E15).
- `data/official_checks.csv` and `data/official/`: 71 official source check items (Machinery Regulation dates, Articles and Annexes; AI Act dates; GCAA drone rules) with the exact locator seen, retrieval date and conflicts.
- `data/verification/`: the pre registered plan (`PLAN.md`), blind verification results of three independent passes, and `outcome.json` with error rates before and after correction. `data/verification_changelog_v2.csv` lists every change and why.
- `docs/REPORT.md`, `docs/EXEC_BRIEF.md`, `docs/READING_LIST.md`: generated or written from those files (`python tools/build_report.py`).

## What is interpreted

Interpretation is always labelled "Reading (interpretation)" in the report and kept apart from what documents say.

- The binding status scheme, the evidence type taxonomy and the instrument families are my own scheme.
- Gap statements ("no instrument found requires X") are absence findings within the sources searched, not proof of absence.
- `docs/GULF_TEST_PROTOCOL.md` is a proposal, not a result. Every item is labelled "proposal" or "idea", and it states what no source currently requires.
- `assurance/library_robot_case.yaml` is an illustrative assurance case skeleton for an assumed university library robot. Every evidence item is open. It is a structure to fill, not a safety case.
- `docs/COMPETITION_SAFETY_ANNEX_TEMPLATE.md` is an unofficial template with no certification claims.

## What is still open

- Verification: an independent check of all 222 rows found problems in about a third of rows (at least one verifier flagging a key column) before correction, and a final check after correction still flagged a similar share. The figures and their limits are in `docs/REPORT.md` section 2.3 and `data/verification/outcome.json`. Rows corrected from the final reading alone are labelled single checked. Treat each row as a lead to confirm in the source.
- Official items still open or not accessible through the fetch tools: Machinery Regulation Annex I Part A, Annex III and Annex IV text; the article of Regulation (EU) 2026/1744 that sets the AI Act high risk dates (the dates come from a recital and a Commission page); AI Act Articles 9, 12 to 15, 26, 73 in the Official Journal text; the current issue and limits of GCAA CAR-UAC and CAR-UAEX; GCAA Safety Decision 2026-03. The exact URLs are in `docs/REPORT.md` Appendix C.
- Which UAE regime covers an indoor service robot is unresolved. A draft enquiry and a tracking sheet are in `docs/UAE_ENQUIRY_PACK.md` and `data/uae_enquiry_tracking.csv`. Nothing has been sent.
- Licences: the proposals in `LICENSES.md` need the owner's confirmation. Several tool licences are unconfirmed (`data/free_tools_licences.csv`).

## What this repository does not contain

No text of any standard, no paywalled PDF and no raw downloads. `tools/check_repo.py` fails the CI job if such material is committed.

## Checks

```
python tools/check_repo.py .                       # no standard text, PDFs or unlicensed raw downloads
python tools/validate_table.py data/evidence_table.csv
python tools/ac_check.py assurance/library_robot_case.yaml   # flags open evidence, unsupported claims
python tools/ac_render.py assurance/library_robot_case.yaml figures/gsn_library_robot   # needs Graphviz
python -m pytest -q tests
python tools/secrets_scan.py .
```

CI (`.github/workflows/checks.yml`) runs these on every push and pull request. Tools used are free: Python, PyYAML, pytest, detect-secrets, Graphviz.

## Related projects

Heat and dust modelling: https://github.com/hudasol/dhill. GNSS trust and interference simulation: https://github.com/hudasol/marsad. The Gulf protocol links to both and does not copy them.
