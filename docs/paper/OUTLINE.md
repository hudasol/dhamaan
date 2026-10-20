# Manuscript outline

Status: outline. The manuscript is generated from data files, as the other documents are, so that no number is typed by hand. Target length 8 to 12 pages. Working title and alternatives are listed at the end.

## Contribution statement (draft)

1. A source traced evidence table of robot, drone and autonomy rules, with a measured error rate and a human check of a stratified sample.
2. An audit of what the retrieved instruments leave to the developer for environmental and GNSS interference conditions that matter in the Gulf.
3. A machine checked assurance case whose checker applies published simulation credibility conditions and keeps hardware claims open when only simulated evidence exists.
4. A preregistered comparison, on the same GNSS integrity monitor and thresholds, of synthetic faults against recorded data, with the credit each earns.

What is not claimed: a new credibility framework (adopted from the sources in `docs/RELATED_WORK.md`), a safety case for a real robot, or any legal conclusion.

## Sections

| Section | Content | Source in the repository | Numbers to fill | Status |
|---|---|---|---|---|
| Abstract | Question, method, three results, limits | Generated last | all | not started |
| 1 Introduction | Silence, simulation as evidence, Gulf interference | `docs/RESEARCH_QUESTION.md`, `docs/REPORT.md` section 1 | few | outline |
| 2 Related work | Credibility frameworks, assurance guidance, sim to real gaps, GNSS interference data | `docs/RELATED_WORK.md`, `data/related_work.csv` | source count | first pass done; originals to be read |
| 3 Evidence table | Construction, protocol, verification, error rates, human check | `docs/REPORT.md` section 2, `data/verification/`, `data/human_check/` | error rates before and after, human check result | human check pending |
| 4 Silence audit | Codebook, coding, agreement, counts for H1 | `data/silence_audit/` | counts, kappa | codebook done; coding pending |
| 5 Assurance case and credit ledger | Case structure, checker rules, conditions adopted, ledger per evidence item | `assurance/`, `tools/ac_check.py` | items by credit level | ledger rules pending |
| 6 Simulation rounds 1 and 2 | Models, preregistration, results, failed criteria | `docs/EVALUATION.md`, `docs/EVALUATION_R2.md`, `sim/` | predictions hit and missed, criteria failed | done |
| 7 Round 3 | Informativeness audit, sensitivity, recorded arm, second author generator | `docs/PREREG_R3_DRAFT.md` and results | all | pending |
| 8 Discussion | What each result says about substitution of simulated evidence; where it would break | Round 3 results | none | pending |
| 9 Threats to validity | Single author, shared model family of checkers, non Gulf recordings, assumed parameters, summary level reading of standards | `docs/LIMITATIONS.md` | few | draft from existing text |
| 10 Data and code availability | Repository, release DOI, licences, reproduction in three commands | `README.md`, `LICENSES.md` | DOI | pending |
| Appendices | Evidence table, official checks, codebook, preregistration text and hashes | data files | none | generated |

## Figures and tables (planned)

1. Pipeline from sources to table to case to simulation to recorded replay (one diagram).
2. Silence map: hazards against instruments, coded cells.
3. Credit ledger: evidence items against the four conditions, with the ceiling each earns.
4. Verdict agreement: criteria against arms (S0, S1, R, second author).
5. Informativeness: predictions by number of mutants under which the verdict changes.

## Reproduction

Three commands on a clean machine: install, run the checks, regenerate the documents. The release carries a DOI from a free archive so the version cited is fixed.

## Working titles

- Whose verdict counts? Synthetic and recorded GNSS interference for a robot integrity monitor
- When the standard is silent: simulated evidence, recorded interference and a credit ledger for a service robot
- Self simulated evidence and the missing environment: a Gulf case

## Venue notes

Choose after searching current calls for workshops on safety assurance, robotics safety and trustworthy autonomy. Post a preprint on a free server first. Check each venue's rules on preprints and on use of assistant tools in the work before submitting; disclose such use as the venue requires.
