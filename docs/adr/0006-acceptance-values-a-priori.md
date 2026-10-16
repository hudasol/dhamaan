# ADR-0006 Acceptance values fixed before the runs

**Context.** The protocol leaves its criteria symbolic (B_D, T_D, P_G, S_G, T_G, E_N, T_N, Q_N, L_N). Nothing in the sources fixes them.

**Decision.** Choose proposal values, write them in `sim/acceptance.py` and `sim/PREREGISTRATION.md`, hash and commit before any evaluation run, and never tune them on the results. Changes go in `sim/DEVIATIONS.md`.

**Consequences.** Some criteria fail and stay failed in the record. Better values need real data, which the pilot would provide.
