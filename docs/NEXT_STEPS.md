# Next steps

Ordered by value. Everything here uses free tools, free data and free accounts. Nothing needs a purchase, a subscription, a paid interface or a paid standard.

## Actions for the owner (cannot be done from inside this repository)

The current list, with what each step needs, is in `HANDOFF.md` under "What the owner must do". In short: fetch by hand the documents the automated retrieval could not read (Appendix C of `docs/REPORT.md` and `docs/VALIDATOR_WARNINGS.md`), decide on and send the enquiries in `docs/UAE_ENQUIRY_PACK.md`, confirm the licences, tag a release, and set the repository About text and topics. Read the rows you intend to quote against their sources; the table is a set of leads, not a settled record (`docs/REPORT.md`, section 2.3).

## Research steps

1. **Done in this phase:** the simulation only items of the Gulf protocol (DU3, GL3, N2 to N4) were preregistered and run; EV-08 and EV-12 are partial with simulated evidence (`docs/EVALUATION.md`).
2. **Replace the synthetic worlds with logged data** from a real sensor and localisation stack, following `docs/PILOT.md` stage B, under a new preregistration. This is what could move EV-08 and EV-12 towards bench evidence.
3. **Preregister a second round of monitor design:** set the DU3 monitor threshold and the degradation bound together, and give the glare monitor a margin or hysteresis around S_G. Keep the first round's results as they are.
4. **Heat items H1 to H6**, starting with the site envelope from open weather data once its licence is confirmed.
5. **Settle the open official items** (Appendix C) and rerun `tools/build_report.py`.
6. **Ask a second human to verify a sample of rows.** The verification here was machine assisted and shares retrieval blind spots; a human reader would calibrate the error rates.
7. **Simulation credibility experiment.** For one perception or navigation behaviour, compare simulated and physical outcomes over a scenario set and score the simulator with a credibility scale.
8. **Learning component assurance pilot** with AMLAS stages 2 to 5 on one learned component.
9. **Track what is moving:** harmonised standards for the AI Act and the Machinery Regulation, delegated acts amending Machinery Annex III, the FAA Part 108 final rule, any GCAA U-space rule, and any UAE ground robot regime.
