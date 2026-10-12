# Next steps

Ordered by value. Everything here uses free tools, free data and free accounts. Nothing needs a purchase, a subscription, a paid interface or a paid standard.

## Actions for the owner (cannot be done by Claude)

1. **Fetch by hand the documents the fetch tools could not read.** The list with exact URLs is Appendix C of `docs/REPORT.md` (built from `data/official_checks.csv`, column `download_if_blocked`). The highest value ones: EUR-Lex Regulation (EU) 2023/1230 (Art. 54, Art. 10, Annexes I, III, IV), Regulation (EU) 2026/1744 (the article amending Art. 113 of the AI Act), the GCAA CAR-UAC and CAR-UAEX PDFs (current issue and limits), and the GCAA Safety Decision 2026-03.
2. **Unlock fetches by pasting URLs.** The fetch tool's permission layer only reads a URL that appears in one of your messages. Pasting the EUR-Lex, AI Act Service Desk, GCAA and tool licence pages into a message lets the next session read them. No workaround was used.
3. **Send the enquiries** in `docs/UAE_ENQUIRY_PACK.md` after confirming the recipients, then fill `data/uae_enquiry_tracking.csv`.
4. **Confirm licences.** `LICENSE` (MIT for code) and `LICENSE-DOCS.md` (CC BY 4.0 for documents and data) are proposals. Confirm or change them, replace the CC BY notice with the official legal text, and confirm the licences listed as unconfirmed in `data/free_tools_licences.csv`.
5. **Tag a release** (for example `v0.2.0`) once the pull request is merged, and set the repository About text and topics in the GitHub settings.
6. **Read the rows you intend to quote** against their sources. The table is a set of leads, not a settled record (see the verification outcome in `docs/REPORT.md`, section 2.3).

## Research steps

1. **Run a first small experiment from the Gulf protocol** (`docs/GULF_TEST_PROTOCOL.md`): the simulation only items (sensor degradation sweep DU3, glare sun sweep GL3, GNSS fault injection N2 to N4), with criteria and predictions committed before the run. This also gives the first real evidence item for goal G6 and G4 of the assurance case.
2. **Fill the library robot assurance case with real evidence**, item by item, leaving the rest open. `tools/ac_check.py` will stop an item being marked provided without an artefact.
3. **Settle the open official items** (Appendix C) and rerun `tools/build_report.py`.
4. **Ask a second human to verify a sample.** The verification here is machine assisted and shares tool blind spots; a human reader on 30 rows would calibrate the error rates.
5. **Simulation credibility experiment.** For one perception or navigation behaviour, compare simulated and physical outcomes over a scenario set and score the simulator with a credibility scale.
6. **Learning component assurance pilot** with AMLAS stages 2 to 5 on one learned component.
7. **Track what is moving:** harmonised standards for the AI Act and the Machinery Regulation, delegated acts amending Machinery Annex III, the FAA Part 108 final rule, any GCAA U-space rule, and any UAE ground robot regime.
