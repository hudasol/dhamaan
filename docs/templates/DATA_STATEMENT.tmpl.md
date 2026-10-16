# Data statement

> {{SIM_LABEL}} This label applies to `sim/results/` only; the other data below are real records of retrieved sources.

## Real data (documented sources)

| File | What it is | Size |
|---|---|---|
| `data/evidence_table.csv` | Paraphrased requirements from retrieved sources, with binding status, access level, URL and verification status | {{N_ROWS}} rows |
| `data/official_checks.csv` | Official source checks with the locator seen | {{N_OFFICIAL}} items |
| `data/verification/` | Preregistered verification plan, blind pass results, reconciliation and `outcome.json` | frozen by hash |
| `data/evidence_table_v1_baseline.csv` | Frozen phase one baseline | frozen by hash |

Access level in the table: full text seen {{ACC_FULL}}, summary seen {{ACC_SUMMARY}}, title only {{ACC_TITLE}}. Binding status: mandatory {{BIND_MANDATORY}}, conditional {{BIND_CONDITIONAL}}, voluntary {{BIND_VOLUNTARY}}, guidance {{BIND_GUIDANCE}}.

**Collection.** Sources were retrieved with web tools during the research phase; no paywalled text was bought or copied. Each row is a short paraphrase, never source text. Quotations are under fifteen words and attributed. A row's access level records what the reader actually saw.

**Known quality.** The verification error rate is reported in `docs/REPORT.md` section 2.3 and `data/verification/outcome.json`: about a third of rows had a key column problem before correction, and a similar share was flagged after it. Rows are leads to confirm, not citations to rely on.

**Personal data.** None. Rows refer to public instruments and public bodies only.

## Synthetic data

| File | What it is |
|---|---|
| `sim/results/du3.json`, `gl3.json`, `gnss.json` | Outputs of seeded software models: {{N_RUNS}} runs, {{SEEDS}} seeds per condition, base seed {{BASE_SEED}} |
| `sim/results/scored.json` | Predictions and acceptance criteria scored against those outputs |
| `sim/results/EV-08.json`, `EV-12.json` | Evidence bundles cited by the assurance case |

Every synthetic file carries the label above and `evidence_kind: simulated`. The data describe models written by the same authors as the methods; they contain no measurement.

## Proposal data

`assurance/library_robot_case.yaml` (an assumed robot and building) and `sim/acceptance.py` (threshold values chosen by us) are proposals, not facts about any site.

## Licences

Proposed: CC BY 4.0 for documents and data, MIT for code (`LICENSES.md`), pending the owner's confirmation. Third party files require a confirmed licence in `data/third_party_manifest.csv`; there are none at present.
