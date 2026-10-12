---
title: "Executive brief: what evidence do robots and drones need before deployment?"
author: "For non specialists. Research draft, second edition, 12 October 2026. Not legal or certification advice."
---

**The question.** Before a company or university puts an autonomous robot or drone to work around people, what must it be able to show, who says so, and what is left unsettled? We read {{N_ROWS}} provisions from robot, drone, AI and autonomy standards and regulations (EU, US, UAE, international), each traced to a source we retrieved.

**What we found**

1. **Little is legally required, and what is required is mostly paperwork.** Binding rules cover things like a technical file, a declaration of conformity, registration, operator permits and accident reporting. The detailed engineering standards for robots (risk assessment, safe design, testing) are mostly voluntary in law. They matter because regulators, customers and insurers rely on them. In the table: {{COUNTS_BINDING}}.
2. **The same evidence kit appears everywhere.** Define where and how the machine will operate; document the hazards and how they are reduced; show test and validation results; keep a technical file; get a declaration or independent review; write operating procedures; keep logs; and report incidents.
3. **Learning based (AI) systems are the weakest point.** Laws ask developers to show an AI based safety function is robust and well tested, but the standards that would say how were still being drafted in mid 2026. The most practical guidance (for example AMLAS and SACE) is voluntary.
4. **Hot, dusty, sunny regions with GNSS interference are handled by delegation.** None of the documents we could read tells a developer to test at Gulf temperatures, in sandstorms, in strong glare, or against GPS jamming or spoofing. They ask developers to define their own conditions and qualify against them. A proposal for such tests, clearly labelled as a proposal, is in `docs/GULF_TEST_PROTOCOL.md`.
5. **UAE drones are well covered; UAE ground robots are not, as far as we found.** The UAE has drone rules (operator authorisation, product conformity, accident reporting). We found no UAE rule specific to indoor service robots or delivery robots; Dubai's rules cover autonomous vehicles on roads. A draft enquiry to ask the authorities is in `docs/UAE_ENQUIRY_PACK.md`.
6. **Simulation counts, but only as part of a mix.** Several sources accept simulation as evidence if the simulator itself is shown to be credible. None gives a rule for how much testing can be replaced by simulation.

**What a team should do with this.** Use the evidence kit as a checklist; pick and defend a method for AI components; state the temperature, dust and lighting envelope explicitly and test to it; and ask the relevant UAE authority which rules apply to the specific robot and location. The full report includes a worked example for a library assistant robot, with every evidence item marked as open.

**How far to trust this.** {{BRIEF_VERIFICATION}} Many standards are paywalled and were read only through free catalogue pages, so no detailed clause content is claimed from them. Key facts should be confirmed against the official texts before being cited externally; the report lists which ones.

**Full materials:** `docs/REPORT.md`, `data/evidence_table.csv`, `data/coverage_matrix.csv`, `docs/NEXT_STEPS.md`.
