# Reading order for the documents

Start with the first four. The rest is reference. Generated files carry a header saying which template builds them; edit the template, not the file.

## Read in this order

1. `paper/manuscript.md`: the single paper, generated from the data files. Numbers are filled by script.
2. `RESEARCH_QUESTION.md`: the question, hypotheses H1 to H5 and what would falsify each.
3. `REPORT.md`: the evidence table, how it was built and what it found.
4. `LIMITATIONS.md`: what none of this shows.

## Method and results

- `METHOD.md`, `PROTOCOL.md`: how rows were collected and checked.
- `INFORMATIVENESS.md`: mutation audit and parameter sensitivity of the predictions (SYNTHETIC).
- `EVALUATION.md`, `EVALUATION_R2.md`: preregistered simulation rounds one and two (SYNTHETIC).
- `PREREG_R3_DRAFT.md`, `OSF_REGISTRATION.md`, `INDEPENDENT_GENERATOR_SPEC.md`: round three design, registration text and the second generator spec.
- `RELATED_WORK.md`, `paper/OUTLINE.md`: literature positioning and the outline the manuscript follows.
- `ARCHITECTURE.md`, `CONTEXT.md`, `DATA_STATEMENT.md`, `SECURITY.md`, `VALIDATOR_WARNINGS.md`: reference.

## For people acting on the work

- `FETCH_LIST_R3.md`: official texts to read by hand (current).
- `UAE_ENQUIRY_PACK.md`, `PILOT.md`, `PILOT_KIT/`, `GULF_TEST_PROTOCOL.md`, `PROPOSAL/`, `COMPETITION_SAFETY_ANNEX_TEMPLATE.md`, `EXEC_BRIEF.md`, `READING_LIST.md`.
- `../HANDOFF.md`: what only the owner can do.

## Superseded or historical

These are kept because earlier commits and hashes refer to them. Do not use them as current.

- `FETCH_LIST.md`: superseded by `FETCH_LIST_R3.md`.
- `NEXT_STEPS.md`: superseded by `../HANDOFF.md`.
- `PLAN_PHASE3.md`, `DECISIONS_PHASE3.md`: record of an earlier phase.
- `PROTOCOL.md`: written before research began; historical record of the first protocol.

Other folders: `adr/` holds decision records; `templates/` holds document templates; `data/` holds recorded check results.
