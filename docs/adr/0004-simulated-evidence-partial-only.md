# ADR-0004 Simulated evidence may only make an item partial

**Context.** The first evidence for goals G4 and G6 is simulated. A reader could mistake a simulated result for proof about the robot.

**Decision.** Every goal states `claim_about` (hardware, software, process, argument). Every non open evidence item states `kind` (simulated, bench, field), an artefact path and its SHA-256. The checker reports an error if simulated evidence is marked provided under a hardware claim, and flags hardware claims backed only by simulation. EV-08 and EV-12 are partial, kind simulated.

**Consequences.** The rule is enforced by code and tested. Hardware claims stay open until bench or field evidence with a matching hash exists.
