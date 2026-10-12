# Verification plan v2 (written before any phase 2 run)

Written 2026-10-11 late evening (Asia/Dubai), before the official source checks and before verification passes A, B and C were started. Nothing in this file was changed after results came in, except the "Outcome" section at the bottom, which is appended later and clearly marked.

## Why this exists

Phase 1 found a 13 percent content error rate in a random sample of 30 rows (21 of 30 rows had some issue of any kind). Corrections were applied but never independently re checked. Phase 2 repeats verification on all 222 rows with new, independent verifiers, and measures the error rate before and after corrections.

Baseline file (frozen before phase 2): `data/evidence_table_v1_baseline.csv`, sha256 `930413888591f00610233c415ea956047cc99e2ef3ebd49b01a66ec78f0e6232`. The input for passes A and B is the table after the official source updates, frozen and hashed as `data/verification/input_table_v2.csv` (hash recorded in `outcome.json`).

## Design

1. **Official source checks first** (Machinery Regulation, AI Act dates, GCAA limits), using fetch tools only. Results update rows where an official source replaces an unofficial or secondary one. The table is then frozen.
2. **Pass A and pass B.** Two separate sets of new subagents, none of whom took part in phase 1. Each checks every one of the rows. They are blind to each other, to the phase 1 verdicts, to the change log and to the notes column. Rows are split into batches by source URL, with different batch boundaries in A and B.
3. **Per row, each verifier records independently:** whether the paraphrase is supported (supported, partly, unsupported, unverifiable); the locator they actually saw; whether the clause field is right; whether edition and status are right; the binding status they would assign from the protocol definitions; the access level their own retrieval supports; and a recommendation (keep, revise, downgrade to title only, remove) with replacement text where needed.
4. **Reconciliation rules (fixed now, applied mechanically):**
   - *Access level:* the lower of the A and B independent levels (order: title only, summary seen, full text seen). A higher level is never adopted unless both A and B say so.
   - *Binding status:* if A and B agree, adopt their value. If they disagree and one matches the current value, keep the current value and mark the row `binding_checked = split`. If neither matches the current value and they differ from each other, keep the current value and mark it `disputed`. Pass C acts as a third vote on every row it sees.
   - *Paraphrase:* if both say supported, keep. If either flags it, replace with the flagging verifier's corrected text (if both flag, use the shorter text, ties go to A). If either says unsupported or unverifiable and recommends downgrade, set access level to `title only` and replace the paraphrase with the verifier's title and scope text. If both recommend removal, remove the row to `data/removed_rows.csv` with the reason.
   - *Clause field:* a clause or article locator is kept in `clause_or_section_seen` only if the final access level is `full text seen` and at least one verifier recorded seeing it. Otherwise it moves to `clause_reported_unverified`.
5. **Pass C (after correction).** A third, new set of subagents, blind to the earlier passes, checks every row that changed in any field, plus a random sample of 30 unchanged rows (seed 20261012). This is the after correction measurement and the third vote.
6. **After pass C**, any row C still flags is either downgraded or corrected with C's own text and labelled `corrected after final check, single checked`. Those counts are reported as a residual and are never described as verified twice.

## Definitions of an error (per key column)

- **Paraphrase issue:** verdict partly, unsupported or unverifiable.
- **Binding issue:** the verifier's independent value differs from the table value.
- **Access issue:** the verifier's independent level is lower than the table level (overclaim). A higher level is counted separately as an underclaim.
- **Row error:** an issue in any of the three key columns.

Reported for A and for B separately, then as "confirmed" (both flag the same column) and "either". Agreement between A and B on binding and access is reported as raw percentage and Cohen's kappa. Rates are given with Wilson 95 percent intervals.

## Predictions, written before the runs

- Fresh pass row error rate (any key column, either verifier) between 15 and 35 percent.
- Paraphrase issue rate 8 to 20 percent; access overclaim rate 8 to 20 percent; binding disagreement 5 to 15 percent.
- Pass C on changed rows: row error rate under 10 percent. Pass C on the unchanged sample: under 8 percent.
- A and B agree on binding status for at least 85 percent of rows.

If the results fall outside these ranges the report says so.

## Known limits of this method

- Verifiers use the same fetch tools, which often return extractions rather than raw text. Errors can be correlated across verifiers. Error rates measure disagreement between independent readings, not ground truth.
- Paywalled standards can only be verified at catalogue or abstract level, so their rows can only ever reach `summary seen` or `title only`.
- Sources the tools cannot reach are listed for manual download, not worked around.

## Outcome

Appended after the runs (see `outcome.json` and the report).

### Outcome (appended 2026-10-12, after the runs; the text above was not changed)

Figures are in `outcome.json`. Pass A and pass B each checked all 222 rows with new subagents. Pass C checked 76 rows that changed in a key column plus 30 unchanged rows (seed 20261012).

Fresh error rate on the 222 rows before A/B corrections (any key column): 26.1 percent (A), 20.3 percent (B), 32.0 percent flagged by either, 14.4 percent flagged by both. Phase 1 reported 13 percent content errors in its own sample; the fresh independent figure is higher.

After correction (pass C): 32.9 percent of changed rows (22.4 percent when rows the fetch tool could not read are excluded) and 20.0 percent of the unchanged sample were still flagged. The prediction of under 10 percent and under 8 percent was wrong. Reasons are visible in the flags: the final reader examined details such as recitals versus operative text, fine scope claims in status notes, and truncated extractions. Verifiers share the same fetch tools, so agreement is not ground truth.

Predictions scored: fresh row error range met (32.0 percent); paraphrase 20.3 percent, just above the stated range; access overclaim 14.9 percent, inside; binding 5.4 percent, inside; binding agreement 96.4 percent (kappa 0.95), met; access agreement 85.1 percent (kappa 0.67).

Residual: 28 rows were corrected using the pass C text alone and are labelled `corrected after final check, single checked`. They have not been verified twice.
