# Validator warnings: review

`tools/validate_table.py` warns when a paraphrase contains a clause style reference (Article, Annex, Section and similar) while the row's access level is below full text seen. The evidence table produced {{N_REVIEWED}} such warnings. The table and its verification are frozen by hash (`data/frozen_sha256.txt`), so the rows were not edited. Each warning was reviewed instead, and the review is stored as data in `data/validator_warnings_reviewed.csv` (reviewed on {{REVIEW_DATE}}).

## Decision applied to every row

{{REVIEW_DECISIONS}}

## How the review is enforced

- `python tools/validate_table.py data/evidence_table.csv --reviewed data/validator_warnings_reviewed.csv --strict` runs in the fast check and in CI.
- A warning counts as reviewed only if the reviewed file lists the row with exactly the same mentions and the row records a locator in `clause_reported_unverified`. Any new warning, any change to a reviewed paraphrase, and any review entry that no longer matches a warning fails the build.
- A separate test (`tests/test_validate_table.py`) checks that every locator in `clause_or_section_seen` belongs to a row whose access level is full text seen.

## Reviewed rows

{{REVIEWED_TABLE}}

## What this does not settle

The review confirms that no row claims a verified clause it did not see. It does not confirm that the mentioned locator is right; that needs the full text, as listed in `HANDOFF.md`.
