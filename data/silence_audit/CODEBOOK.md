# Codebook: silence audit

Fixed before any row is coded. Hypothesis H1 in `docs/RESEARCH_QUESTION.md`.

## Selection

Candidate rows are all rows of `data/evidence_table.csv` whose requirement paraphrase, evidence type or applies to text matches the keyword rule in `tools/silence_audit.py` (`CANDIDATE_RULE`). The rule is wide on purpose. A coder marks a row `out_of_scope` when it is not about an environmental or interference hazard. The result applies only to retrieved text. A row seen as summary or title only cannot show that an instrument is silent.

## Fields

| Field | Values | Meaning |
|---|---|---|
| hazard | heat, dust, glare, gnss, environment_general, out_of_scope | The hazard the row is about. One value; pick the main one. |
| asks_evidence | yes, no, unclear | The row says a developer must or should produce evidence (test, analysis, declaration) about that hazard. |
| test_method_fixed | yes, no, unclear, na | The instrument names or fixes a test method for the hazard (for example a named test procedure). |
| severity_fixed | yes, no, unclear, na | The instrument fixes a severity or limit value (a temperature range, a particle exposure class, an interference level). |
| severity_gulf_applicable | yes, no, unclear, na | A fixed severity is stated and would apply to a Gulf site without change (for example it covers the temperatures or dust loads a Gulf site meets). `no` if the value is generic, for a different region or class not tied to the site. |
| delegated_to_developer | yes, no, unclear, na | The row says the developer, applicant or operator defines the conditions or values. |
| notes | free text, one line | Why a coding is `unclear`, or what the reader could not see. |

`na` is used only where the question does not arise (for example severity fields when `asks_evidence` is `no`). Use `unclear` when the paraphrase does not let you decide. Do not guess from outside knowledge of the standard; code only what the row and its source show.

## Coders

Two coders work independently from `coder_template.csv`, without seeing each other's file. Coder A and coder B must say who or what they are in the file name. If both coders are automated tools of one kind, state it: agreement between them does not remove shared error. A human coder codes at least a third of the rows, chosen by seed, so agreement with a person can be reported.

## Outputs

- Cohen's kappa per field and raw agreement (`python tools/silence_audit.py agreement coder_A.csv coder_B.csv`).
- Disagreements are resolved by reading the source, and the resolution is recorded with the reason.
- H1 is reported as counts: rows asking for evidence; of those, rows fixing a test method; rows fixing a severity; rows fixing a Gulf applicable severity; rows delegating.
- A row coded from a paraphrase that the human check later finds wrong is flagged and recoded.
