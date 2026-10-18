# Contributing

Thank you for helping. This repository is a student proposal seed; its value depends on every claim staying labelled and traceable. Please keep to the rules below.

## Before a pull request

- Run `python tools/fast_check.py` (or `make check`). Every step must pass.
- If you change data or code that documents depend on, run `python -m docsgen.build` and commit the regenerated files.
- If you change a schema contract, run `python tools/gen_schema.py` and `python tools/gen_log_schema.py`.

## Rules that the checks enforce

- Never edit a frozen file (`data/frozen_sha256.txt`). Corrections to the evidence table go into a new, separately verified version.
- Never change a preregistered threshold, prediction or seed after results exist. Write a new preregistration, and record any deviation in `sim/DEVIATIONS.md` with a date.
- Simulated results carry the SYNTHETIC label and never close a claim about hardware. New evidence items need a kind (simulated, bench or field), an artefact path and its SHA-256.
- Lower layers never import higher ones (tools, then sim, then docsgen, then the command). No network or language model client anywhere.
- Every number in a generated document comes from a data file; do not type numbers into templates.

## Sources

- Cite only sources you retrieved and read, with URL, retrieval date and the access level you actually had.
- Paraphrase; quotations stay under fifteen words and are attributed. Never commit the text of a standard or paywalled material.
- If a source cannot be retrieved, add it to `docs/FETCH_LIST.md` instead of working around the block.

## Voice for public text

Formal and plain, plural or impersonal, no em dashes, no superlatives, no emojis, hyphens only where unavoidable. Do not name institutions outside `docs/CONTEXT.md`, and do not imply contact or endorsement.

## Reporting a problem with a source row

Use the "Source correction" issue template and give the row id, the source URL and what the source actually says.
