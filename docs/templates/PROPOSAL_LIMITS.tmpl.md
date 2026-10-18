# dhamaan: limits note (one page)

> {{SIM_LABEL}}

This note goes with every brief in `docs/PROPOSAL/`. It states plainly what the work does not show.

- **No hardware.** No robot, sensor, receiver or building was measured. {{N_PARTIAL}} assurance case items are partial with simulated evidence only, and every hardware claim they touch stays open ({{SIM_ONLY_GOALS}}).
- **Shared authorship.** The simulated worlds and the methods tested in them were written by the same people. A HIT shows that a model behaved as predicted, nothing more.
- **Assumed values.** Thresholds and all heat parameters are assumed, proposal values; nothing in the sources fixes them.
- **Failures.** First round criteria that failed: {{AC_FAILED_LIST}}. Second round criteria that failed: {{R2_AC_FAILED_LIST}}. Predictions that missed: first round {{PRED_MISS_LIST}}; second round {{R2_PRED_MISS_LIST}}.
- **Source quality.** Before correction, an independent check flagged a key column problem in {{ROW_ERR_EITHER}} of rows (95 percent interval {{ROW_ERR_CI}}); after correction the final check still flagged {{PASSC_CHANGED}} of changed rows. Rows are leads, not citations to rely on.
- **Retrieval gaps.** Some official documents and any public flight log could not be retrieved by the automated retrieval; they are listed in `docs/FETCH_LIST.md`.
- **Regime.** No rule specific to indoor or off road service robots in the UAE was found in the sources retrieved; an enquiry was drafted and not sent.
- **Status.** A student proposal seed. No contact, request, review or endorsement by any body. Licences are proposed until the owner confirms them.
