---
title: "What evidence must a developer produce before deploying autonomous machines? A standards and regulations evidence study, with gaps for learning based autonomy and Gulf conditions"
author: "Huda Mueen. Research draft, second edition. Not legal or certification advice."
date: "12 October 2026"
---

# 0. Read this first

**What this is.** A structured, source traced study of what robot, drone and autonomy standards and regulations ask a developer to *produce as evidence* before deployment, which of those asks are binding, and where they are silent. It is built from {{N_ROWS}} evidence table rows (`data/evidence_table.csv`), each tied to a URL a research subagent or I retrieved on 11 or 12 October 2026. This second edition adds a fresh verification of every row and official source checks (section 2.3 and section 9).

**What this is not.** It is not certification advice and not legal advice. Several instruments are paywalled; for those the table says "title and scope only" or "summary seen" and no clause content is claimed.

**How to read the two voices.** Statements of what a document says are written plainly and carry row IDs such as (A04) that point to the table. My own interpretation is always set in a block starting **Reading (interpretation):** so you can strip it out and defend only the documented part.

**Three caveats that matter before you share anything.**

1. The web fetch tool used for most retrieval returns *model written extractions* of pages, not raw text. "Full text seen" therefore means the specific passage was returned and read, not that a human read the original PDF. Verifiers downloaded some PDFs directly (SORA 2.5, the EASA annex, GCAA CARs, SACE, the Federal Register NPRM), but the EUR-Lex text of Regulation 2023/1230 and the AI Act articles were read only through extractions or an unofficial reproduction.
2. The AI Act article rows come from artificialintelligenceact.eu, an unofficial reproduction. Rows relying on it were downgraded to "summary seen" and should be checked against the Official Journal.
3. Verification (section 2.3) found real errors, and the final check after correction still flagged a substantial share of rows. {{CAVEAT_VERIF}}

# 1. Executive summary

**Question.** Across robot and drone safety standards and regulations, what evidence must a developer produce before deploying autonomous or semi autonomous machines in workplaces and public spaces; what is mandatory; and where are the gaps, particularly for learning based autonomy and Gulf conditions?

**Headline findings** (each is supported in sections 4 to 7; interpretation is flagged there).

1. **Very little robot specific evidence is mandatory, and what is mandatory is mostly legal process rather than technical acceptance criteria.** The binding rows are mainly the EU Machinery Regulation (technical file, conformity assessment, declaration and marking, retention for 10 years) (A03 to A05), the EU drone regulations (authorisation, declaration, registration) (C01 to C10), and UAE drone rules (product conformity in C48; the GCAA operator rules, C51 to C54, are now recorded as title and scope only because their text could not be re read in the second edition). The robot safety standards themselves (ISO 12100, ISO 10218, ISO 13482, ISO 3691-4, IEC 61508, ISO 13849, UL 3300) are voluntary in law; they become relevant through the harmonised standard route to a presumption of conformity (A07) or through contracts and market expectations.
2. **A single evidence skeleton recurs everywhere:** a defined operating context, a documented hazard and risk assessment, verification and validation records, a technical file, a declaration or independent assessment, operating procedures, logging, and incident reporting. What differs is who checks it and how rigorously.
3. **Learning based autonomy is the least standardised area.** The EU Machinery Regulation makes machine learning safety functions a category needing third party assessment (A16, secondary source for the annex wording), the AI Act sets high level duties on risk management, data governance and robustness (B20, B21, B26), but the technical standards that would make these testable were still being written (A21, B33), and the road vehicle standards (ISO 21448 and relatives) do not by their scope cover robots (B01, B02). The most concrete guidance (AMLAS, SACE, MLEAP) is non binding (B44, B46, D21).
4. **No instrument I could retrieve asks a developer to test against Gulf heat, dust, sun glare or GNSS jamming/spoofing.** The closest hooks are generic: SORA operational safety objectives on environmental qualification (D35, D38), Dubai's autonomous vehicle rules requiring tests under local climatic conditions (secondary source, no numbers) (D50, C65), generic IEC test methods (D62, D63), and GNSS interference operational guidance (D52 and others). This is an absence finding within the scope searched, not proof that nothing exists.
5. **UAE position.** For drones the UAE has a findable, structured regime (Federal Decree-Law 26/2022, Cabinet Resolution 110/2023 on products, GCAA CAR-UAC/CAR-UAEX for operators) (C47 to C56). For ground robots, no UAE rule specific to service or delivery robots was found; Dubai's autonomous vehicle law and RTA resolution cover vehicles on roads (C64, C65). What governs an indoor library robot in the UAE is therefore **unresolved by the sources found** and is the first open item in the worked example.
6. **Simulation is accepted as evidence in several places but never as a free standing credit.** SORA guidance allows it if the target environment is justified (D38), UL 4600 expects a mix of analysis, simulation, closed course and road testing (B07), NASA-STD-7009 offers a credibility scale (D27, secondary), and AMLAS asks for evidence that the simulator represents reality (B45). No source gave a quantitative rule for how much simulation can replace physical testing.

**Verification error rate.** {{EXEC_VERIFICATION}}

# 2. Method

## 2.1 Protocol (written before research; `docs/PROTOCOL.md`)

- **Inclusion.** Instruments named in the brief; a row is admitted only if it is a testable requirement or evidence expectation visible in a retrieved source.
- **Search.** Four independent streams, run in parallel by research subagents: (A) machinery and robot safety, (B) autonomy and AI, (C) drones and the UAE, (D) assurance practice and Gulf conditions. For each instrument: official catalogue or status page first, then regulator or open text, then public summaries; record what could not be accessed. UAE searches were run in English and Arabic.
- **How "required" is decided.** *Mandatory*: binding legal text on the developer or operator, seen in legal text or an official regulator page. *Conditional*: binding only if a trigger holds (risk class, category, harmonised standard route, approval pathway). *Voluntary*: not referenced by law in the relevant jurisdiction. *Guidance*: regulator or body guidance, non binding. A standard that is voluntary in law but gives a presumption of conformity under a regulation is recorded as conditional, with the route stated.
- **Access levels.** *Full text seen* (the cited passage was read), *summary seen* (abstract, official summary, secondary or unofficial reproduction), *title only* (catalogue entry and scope; no requirement content asserted).
- **Paywalls.** Never reproduced or reconstructed. Clause numbers recorded only if seen in a retrieved source.

## 2.2 Resulting table

{{N_ROWS}} rows. Binding status after verification: {{COUNTS_BINDING}}. Access level after verification: {{COUNTS_ACCESS}}. Verification status: {{COUNTS_VSTATUS}}.

The original columns (instrument, edition or version, status note, clause seen, paraphrased requirement, binding status, applies to, evidence type, who verifies, source URL, retrieval date, access level, notes) are in the CSV together with derived columns: `family`, `evidence_codes` (section 5), and from the second edition `clause_reported_unverified` (a locator a source reported but that no verifier could confirm in full text), `binding_checked`, `verification_status` and `last_checked`. A clause locator sits in `clause_or_section_seen` only when the access level is full text seen and a verifier saw it. Appendix A shows a compact version; the CSV is authoritative.

**Row duplication.** Some provisions appear in more than one stream (for example Machinery Regulation rows in streams A, B and D, and EASA's AI concept paper in streams B and C). I did not delete them because the verifiers checked them independently, but counts by instrument overstate the number of distinct requirements.

{{VERIFICATION_SECTION}}

# 3. The landscape: what each instrument is, and how binding it is

Statuses are as seen in retrieved sources on 11 October 2026; "unverified" means I could not retrieve a source that settles it.

| Instrument | Edition / status seen | Binding for a developer | Notes |
|---|---|---|---|
| EU Machinery Regulation (EU) 2023/1230 | Applies from 20 January 2027. The 14 January 2027 on one Parliament page is the uncorrected print date (corrigendum OJ L 169, 4.7.2023, p. 35). Directive 2006/42/EC applies until then (B35). See section 9, items M01 to M04 | Mandatory in the EU (A03 to A06) | Annex I Part A, Annex III and Annex IV text were not reached in an official source; Annex content is from secondary sources (A16 to A19) |
| ISO 12100 | 2010 edition; ISO page shows it due for revision | Voluntary in law; conditional via harmonised standard route (A22, A07) | Harmonised list evidence is the 2021 list under the old Directive; current citation under 2023/1230 not checked |
| ISO 10218-1 / -2 | 2025 editions published (A23, A25) | Conditional (route) or voluntary; EN harmonisation of 2025 editions unverified (A26) | ISO/TS 15066: ISO says it is to be replaced; vendor pages say its content moved into ISO 10218:2025. Sources conflict |
| ISO 13482 | 2014; due for revision (A28) | Voluntary / conditional via the old harmonised list | Abstract notes no recognised impact injury data existed at publication (A29) |
| ISO 3691-4 | 2023 edition; 2020 edition withdrawn (A31) | Voluntary | Scope excludes public zones; clause text not read (D64) |
| IEC 61508; ISO 13849-1/-2 | IEC 61508 (2010 edition) current; ISO 13849-1:2023 current; -2:2012 | Voluntary / conditional (A32 to A36) | Catalogue and abstracts only |
| UL 3300 | Listed as ANSI/CAN/UL 3300:2025 with a 2024 publication date (labels conflict) (D66) | Voluntary; third party evaluation at developer or market request (A37) | Edition not confirmed |
| UL 3115 | Outline of Investigation, not a full standard (B12) | Voluntary | Meant to be used with a product standard such as UL 3300 |
| ISO 21448 (SOTIF) | 2022; under revision (B01) | Voluntary | Road vehicle scope; applicability to robots is interpretation (B02) |
| UL 4600 | Edition 3, March 2023 (B06, D04) | Voluntary | Generic autonomy standard; requires a safety case; catalogue and news text only |
| EU AI Act (2024/1689) as amended by Regulation (EU) 2026/1744 | Amending regulation dated 8 July 2026, in force 27 July 2026 (official service pages); high risk obligations from 2 Dec 2027 (Annex III systems) and 2 Aug 2028 (Annex I systems) per a recital and a Commission page. The amending article itself was not reached (section 9, AI07) (B17, B18) | Conditional (high risk classification) | Text from unofficial reproduction; robots mostly reach the Act through machinery legislation (B19, interpretation) |
| Harmonised standards for the AI Act (CEN-CENELEC JTC 21) | EN 18286 (quality management) approved; risk, data and cybersecurity standards still drafts per mid-2026 pages (B33) | Voluntary; presumption of conformity once cited | Date of citation in the Official Journal disputed between sources |
| EU Reg. 2019/947 and 2019/945 | In force; the retrieved text is the original unamended act (C01 to C14) | Mandatory in the EU | |
| JARUS SORA 2.5 | Main body dated 13 May 2024 (C15 to C26) | Guidance in itself; EASA adopted it as AMC (C28 to C36) | EASA amendment labelled 3 on the PDF and 4 on the web page (conflict) |
| FAA Part 107, Part 89 | Current rules (C39 to C43) | Mandatory in the US | Part 108 BVLOS rule: proposed rule retrieved; final rule status rests on secondary blogs (C44 to C46) |
| UAE drones | Federal Decree-Law 26/2022; Cabinet Resolution 110/2023; GCAA CAR-UAC Issue 02 and CAR-UAEX Issue 02 (titles only in this edition; limits not read again), CAR-UAR Issue 04 (C47 to C58) | Mandatory in the UAE | A GCAA U-space rule is reported only by news (C60) |
| UAE ground autonomy | Dubai Law 9/2023 and RTA Administrative Resolution 939/2025 (autonomous vehicles on roads, including autonomous equipment and machinery categories) (C64, C65); Abu Dhabi permits for L4 vehicles by press release only (C66) | Mandatory in Dubai for covered vehicles | No rule for service or delivery robots found |

**Reading (interpretation).** For a developer in the UAE the legally binding layer is thin and drone heavy. The technical weight sits in voluntary standards and in expectations of buyers, insurers and regulators. Which binding regime applies to a given robot depends on where it operates and whether it is exported: the EU instruments matter if the product is placed on the EU market, not by virtue of being built in the UAE.

# 4. What the evidence table shows

## 4.1 The recurring evidence set

Reading the rows together, the same artefacts recur across instruments:

- **Defined operating context.** SORA's ConOps and SAIL determination (C17, C21), BSI PAS 1883 and ISO 34503 ODD taxonomies (D11, D13), SACE's first stage (B46), UL 4600's safety case tied to the ODD (D05), the Machinery Regulation's requirement to account for the intended operating area of autonomous mobile machinery (A19, secondary).
- **Hazard and risk assessment record.** ISO 12100 as the generic method (A22), ISO 13482 and ISO 3691-4 as type-C style applications (A28, A31), EU AI Act Article 9 for AI systems (B20), SORA's ground risk steps (C18, C19).
- **Technical file and declaration.** Machinery Regulation Article 10: documentation, conformity assessment, EU declaration, CE marking, retention for 10 years, source code or logic on request (A03 to A05).
- **Verification and validation records.** ISO 13849 requires a validation plan and report (A36), IEC 61508 a safety lifecycle with hardware and software records (A32 to A34), AI Act Article 15 accuracy and robustness evidence (B26).
- **Independent assessment.** Notified body routes under the Machinery Regulation (A11, A16), SORA's third party verification at higher assurance levels (C16, C29), EASA design verification reports at SAIL IV and type certificates at SAIL V to VI (C31), UL's optional third party evaluation (A37).
- **Operating procedures, instructions and oversight.** AI Act Articles 13 and 14 (B24, B25), SORA operational safety objectives on procedures and training (C34), UL 3300's user classes and surroundings (A38).
- **Logging and monitoring.** AI Act Article 12 (B23), Machinery Regulation Annex III retention of safety decision data (A18, secondary and with an unverified anchor), AMLAS deployment monitoring (B45), runtime monitor research (D24, D25).
- **Incident reporting and field feedback.** AI Act Articles 72 and 73 (B29, B30), EU occurrence reporting (D44), GCAA CAAP 22 reporting categories and times (D45), FAA Part 107.9 (D48), UL 4600's safety performance indicators with field feedback (B08 to B10).

## 4.2 Mandatory versus voluntary: the shape of the table

{{BINDING_BY_FAMILY}}

**Reading (interpretation).** Mandatory rows cluster where a regulator controls market entry or operation (CE marking, drone authorisation, UAE operator approval). Technical depth lives in rows that are voluntary or guidance. A developer who only does what is mandatory will often have a process file but little technical evidence of safety.

# 5. Taxonomy of assurance evidence types (bottom up)

**How it was built.** Each row's `evidence_type` field was written by the researcher who read the source, in free text (for example "Third party testing/assessment leading to UL Mark", "Contingency volume calculation", "Triggering condition analysis (SOTIF style)"). I grouped those descriptions into 15 types by what the artefact is and what it is used for, merged near duplicates, and kept a separate bucket for rows that describe context rather than an artefact. The grouping used keyword rules, and verifiers then checked and corrected the codes of all {{N_ROWS}} rows. A row can carry several codes. The taxonomy is therefore *derived from the table* but its boundaries are my judgement, not a standard.

{{TYPE_TABLE}}

**Definitions.**

- **E01 Hazard and risk assessment record.** Structured identification and estimation of hazards and risks, and the record of risk reduction (ISO 12100-style, AI Act Art. 9, SORA ground/air risk).
- **E02 Scope, classification and operating context definition.** Documents that fix what the system is, where and how it operates and which regime applies: ODD, ConOps, risk class or category determination, operational volume.
- **E03 Technical documentation or technical file.** The retained, structured dossier that makes the other evidence findable by an authority; may include source code or logic on request.
- **E04 Design and safety function verification.** Evidence that safety functions are specified and designed to a required integrity: performance level or SIL determination, lifecycle records, design standard compliance, system safety assessment.
- **E05 Physical test and validation evidence.** Results from tests on the real system or components: performance, robustness, contact force, environmental, stopping, interference.
- **E06 Simulation and scenario based evidence, with credibility.** Scenario sets, simulation results and the argument that the simulation is credible.
- **E07 Data, learning assurance and ML evidence.** Dataset specification and representativeness, model verification, triggering condition analysis, generalisation and runtime monitor evidence.
- **E08 Safety case or assurance argument.** A structured argument linking claims to evidence, with confidence or defeater analysis (GSN, UL 4600, SORA safety portfolio).
- **E09 Independent or third party assessment.** Notified body certificates, design verification reports, accredited lab test reports, third party evaluation marks.
- **E10 Declaration of conformity, marking and labelling.** The manufacturer's formal declaration, marks and labels.
- **E11 Operating procedures, instructions, training and human oversight.** Manuals, instructions for use, competency, supervision design, human machine interface evidence.
- **E12 Logging, monitoring and data retention.** Event logs, runtime monitoring, retained decision data, tracking.
- **E13 Incident and occurrence reporting, and post market monitoring.** Duties and artefacts for reporting events and feeding field data back.
- **E14 Quality or safety management system.** Organisational management systems (QMS, SMS, AI management system).
- **E15 Authorisation, registration, permit or approval.** Administrative permissions obtained from an authority.
- **E00 No evidence artefact.** Rows that record scope, status or legal context rather than something a developer produces.

# 6. Coverage matrix: instruments versus evidence types

Cell letters give the strongest binding status among the instrument family's rows that mention that evidence type: **M** mandatory, **C** conditional, **V** voluntary, **G** guidance. A blank means no row in that family asks for that type, *not* that the instrument forbids it.

{{MATRIX}}

**How to read it.** The matrix shows what the rows record, not a legal test of what each instrument can require. Families are groupings I created, and a family's letter can be driven by a single row. In particular, "M" in the UAE family comes from drone rules and from Dubai's road vehicle rules; it does not indicate a mandatory evidence requirement for a robot.

**Reading (interpretation).**

- Apart from the UNECE ADS rule as reported by secondary sources (D31), only the EU Machinery Regulation and the AI Act carry a conditional ask for data and learning assurance evidence (E07); nothing is mandatory in the strict sense. Everything else on E07 is guidance.
- Simulation (E06) is asked for conditionally by the UNECE ADS rule as reported (D31, secondary) and recommended elsewhere, but nowhere mandatory for robots.
- E09 (independent assessment) is mandatory or conditional wherever market entry is controlled (machinery, drones, UAE operator approval) and optional in the standards.
- Incident reporting (E13) is the most consistently *binding* evidence type across jurisdictions (EU occurrence reporting, GCAA, FAA, AI Act).

# 7. Gap analysis

Each gap states what documents say, then my interpretation. UAE claims appear only where a retrieved source supports them.

## 7.1 Learning based perception and planning

**What documents say.**

- The Machinery Regulation treats safety components with fully or partially self evolving behaviour using machine learning as a higher scrutiny category needing third party assessment (A16, D43, secondary sources for the annex text; recitals 54 and 55 explain the intent (A15)). It also lets a software driven change count as a "substantial modification" only when it meets the Article 3(16) conditions (A06).
- The AI Act sets lifecycle risk management, data governance, logging, human oversight, and accuracy, robustness and cybersecurity duties (B20, B21, B23, B25, B26). It states what to document, not numerical acceptance thresholds. Application of the high risk obligations was deferred to 2027 and 2028 by the 2026 omnibus regulation (B17, B18).
- The Commission's standardisation request asks CEN-CENELEC for standards on machine learning safety functions, protection against corruption and autonomous mobile machinery, with a first deadline of 20 January 2026 (A21). Whether that deadline was met was not checked. Harmonised AI Act standards were largely drafts in mid-2026 (B33).
- ISO 21448, ISO 26262, ISO/PAS 8800 and ISO/TS 5083 are road vehicle documents by scope (B01, B02, B04, B05). ISO/IEC TR 5469:2024 is an informative report, not requirements (B38); ISO/IEC TS 22440 is still at committee draft (B39).
- The most concrete guidance is non binding: AMLAS gives a staged process with artefacts for ML safety requirements, data management, model learning, verification and deployment (B44, B45); SACE gives a system level eight stage process (B46); EASA's MLEAP report sets out learning assurance concerns on data completeness, generalisation and robustness (D21).
- Research on triggering conditions for perception and on learned runtime monitors exists but is early stage (D22 to D25). One monitor paper reports 92% accuracy on a simple traffic sign case and lists its own limitations (D25).

**Reading (interpretation).** Learning enabled components are the clearest *evidence gap*: legal text says "show it is robust and representative", the testable standard that defines how is mostly missing or in draft, and the usable method (AMLAS, SACE) is voluntary. A developer must therefore *choose and defend a method*, which is also an opportunity: a safety case built on AMLAS style data and verification arguments will be more convincing than one that only cites a standard.

## 7.2 Gulf conditions: heat, dust, glare, GNSS degradation

A proposal (not a result) for what a developer could test, argue and simulate for these four conditions is in `docs/GULF_TEST_PROTOCOL.md`. It cross references the author's dhill (heat and dust) and marsad (GNSS) projects without duplicating them.

**What documents say.**

- *Environmental qualification, generic.* SORA 2.5 operational safety objectives on environmental limits and qualification (#23 and #24); #24 is not required at SAIL I-II, medium at SAIL III and high at SAIL IV-VI (D35). The UK CAA's AMC says simulation may be used if the target environment is justified and gives DO-160 as an example standard (D38). The applicant defines the conditions; heat, dust and glare are not named.
- *ODD vocabulary.* BSI PAS 1883 lets an ODD declare airborne dust and sand and illumination attributes, with temperature only optional; it is a taxonomy, not a test requirement (D11, D12). ISO 34503 is a taxonomy and format for ODDs (D13).
- *Test methods.* IEC 60068-2-2 (dry heat) and IEC 60529 (IP code, referencing a dust and sand test method) are methods whose severities are chosen by a product standard or contract (D62, D63). The safety scanner standard IEC 61496-3:2025 states that it does not address outdoor application (D65). ISO 3691-4's contents list climatic condition and high temperature clauses, but the text was not read (D64).
- *Dubai.* Secondary sources say Dubai's autonomous vehicle rules require operational tests under local climatic conditions, with no numeric limits seen (D50, C65). RTA Resolution 939/2025 Article 3 is reported as requiring local operational test runs with data (C65).
- *GNSS.* EASA's AMC tells drone operators to identify GNSS as an external system and prepare procedures for complete GNSS loss and poor satellite geometry (C34); the text read contains no jamming or spoofing wording. EASA Safety Information Bulletin 2022-02R4 names the Middle East, not specifically the Persian Gulf, and is non mandatory (D52). UAE working papers submitted to ICAO document jamming and suspected spoofing and propose reporting frameworks (D57, D58, D59). GCAA reporting material lists interference affecting aircraft safety among safety critical events (D45, D46). ETSO-C146e (GNSS receivers) includes a spoofing section stated to create no new requirements, though other parts add requirements (D54).
- *UAE drone products.* Cabinet Resolution 110/2023 requires conformity testing of drone products, including a GPS feature test, geographic boundary identification and safe fall and return, with an Annex A standards list including IEC 61508 (C48 to C50).

**What was not found** (recorded as absence within the searched scope): no instrument read requires testing a robot or drone against a stated Gulf ambient temperature, solar loading, sand or dust storms or sun glare; no UAE regulation (GCAA, TDRA, ITC, RTA) was found that requires GNSS jamming or spoofing resilience testing; GCAA CAR-OCR text and a TDRA statement on GNSS interference were not found. IEC 60721 climatic classes, MIL-STD-810 and IEC 60204-1 were not retrieved and remain unverified.

**Reading (interpretation).** The Gulf is handled by *delegation*: standards ask the developer to define the conditions and qualify against them, and leave the choice of severity to the developer. That is a gap with a practical consequence: two products can both be "compliant" while one has been tested at 55 degrees C with dust loading and the other has not. A defensible UAE ready case should state the temperature, dust and glare envelope explicitly and test to it, and treat GNSS denial as a design assumption (with indoor deployment the issue becomes localisation robustness rather than GNSS).

## 7.3 Human robot interaction in public spaces

**What documents say.**

- ISO 3691-4's scope excludes public zones (A31), the 2025 ISO 10218-1 abstract excludes service robots where the public has access (A23), and the IEC 61496-3 safety scanner standard excludes outdoor application (D65).
- ISO 13482 covers personal care robots (mobile servant, physical assistant, person carrier), notes missing impact injury data at publication, and is due for revision (A28, A29).
- UL 3300 covers service, communication, information, education and entertainment robots in settings with people present, with user classes and use surroundings as evaluation inputs (A37, A38, D66). Only catalogue and article text was read.
- AI Act Article 14 requires oversight design so humans can understand limits, detect automation bias, override and stop (B25), and Article 13 requires instructions covering accuracy, oversight and maintenance (B24).
- For UAE ground robots in public spaces, no rule specific to delivery or service robots was found; Dubai pilots appear only in news (C67), and the autonomous vehicle instruments are about vehicles on roads (C64, C65).

**Reading (interpretation).** The standards were written for factories, vehicles and personal care contexts; a robot moving among unsupervised members of the public, including children and people with disabilities, sits on the boundaries of several scopes at once. The least binding but most relevant sources are UL 3300 and ISO 13482 as design references, and AI Act oversight articles as a vocabulary for human oversight evidence. What counts as an acceptable injury risk limit for a service robot is not settled in the sources I could read.

## 7.4 Simulation as evidence

**What documents say.**

- SORA related guidance allows simulation when the target environment is justified (D38). UL 4600 expects the safety case to show a mix of analysis, simulation, closed course and public road testing for the initial release and each software update (B07). SACE describes simulation as helping reviewers (Activity 3), as additional analysis to corroborate hazard validation (Activity 8) and as an option for validation (Note 13) (D20). AMLAS asks for evidence that the simulator represents reality when simulation is used for integration testing (B45).
- NASA-STD-7009 defines eight credibility factors scored 0 to 4 (D27, read through slides describing the 2008 version; voluntary). ISO 34502 is a scenario based evaluation process scoped to ADS on limited access highways (D29). A trade press report says a UNECE regulation for fully driverless systems accepts validated virtual environments as part of a safety case; the primary text was not retrieved (D31).
- A vendor page on ISO 10218 says contact force evidence for power and force limiting may come from measurement or validated simulation (A26); this is secondary.

**Reading (interpretation).** Simulation is accepted *as one leg of a mixed argument*, and always conditional on a credibility argument for the simulator and the scenario set. No retrieved source set a quantitative share of evidence that simulation may supply. For a small team, the defensible position is: simulate to explore and to cover rare scenarios, validate the simulator against physical tests in the ODD, and say so explicitly.

# 8. Worked example: assurance case skeleton for a library assistant service robot

**Scenario (assumed for illustration).** A mobile service robot with learning based perception and an optional arm that fetches and returns books and guides visitors in a university library in the UAE. I made these assumptions; they are not facts about any particular project. **Every evidence item below is OPEN: no evidence is claimed to exist.** A machine checkable version of this case is `assurance/library_robot_case.yaml`; `tools/ac_check.py` flags open evidence, unsupported claims and untraced items, and `tools/ac_render.py` draws the diagram from the file. Items marked "decision needed" depend on choices the team has not recorded here.

![GSN style assurance case skeleton. Rectangle: goal; parallelogram: strategy; rounded box: context; circle: solution (evidence item EV xx, see checklist); diamond: undeveloped. Dashed outlines mean open: no evidence is claimed to exist.](../figures/gsn_library_robot.svg)

**Evidence checklist.** "Motivating sources" are table row IDs that motivate asking for the item; they show *why the item is on the list*, not that any instrument requires it for this robot. Where I add an expectation not found in a source, it is marked "(my addition)".

| ID | Evidence item | Motivating sources | Status |
|---|---|---|---|
| EV-01 | ODD and system definition: library layout, occupancy ranges, user classes (children, elderly, people with disabilities, staff), floors and obstacles, lighting including daylight through glazing (my addition), network and localisation sources, what is out of scope | PAS 1883 and ISO 34503 taxonomies (D11, D13); SACE stage 1 (B46); AMLAS scoping (B44); UL 4600 completeness tied to ODD (D05); SORA ConOps (C17) | OPEN. Decision needed |
| EV-02 | Hazard and risk assessment, identifying hazardous situations for people, objects, and the robot's own failures | ISO 12100 method (A22); ISO 13482 scope for mobile servant robots (A28); ISO 3691-4 hazard annex as an analogue for mobile platforms (A31); UL 3300 scope (A37); AI Act Art. 9 as vocabulary (B20) | OPEN |
| EV-03 | Regime determination: which laws and authorities govern an indoor robot in this university (UAE federal, emirate, university policy, insurer); whether EU rules apply if exported | UAE sources found cover drones and road vehicles only (C47 to C56, C64, C65); Machinery Regulation scope (A01, B35); AI Act dates (B17) | OPEN. Not answerable from the sources found. Ask the relevant UAE authority and the university |
| EV-04 | Safety requirements and safety function specification: speed and force limits, protective stop, emergency stop, safe states, with the integrity level (performance level or SIL) chosen and justified | ISO 13849 performance level evidence (A35); IEC 61508 lifecycle (A32 to A34); ISO 3691-4 control system verification (A31) | OPEN. Decision needed: target integrity level |
| EV-05 | Contact and collision evidence: measured contact forces and pressures for relevant body regions, with limits justified | ISO 10218 and PFL measurement or validated simulation, vendor page (A26); ISO 13482 abstract warns injury data were not available at publication (A29) | OPEN. Decision needed: what limits and from which source |
| EV-06 | Stopping distance and obstacle detection tests at maximum speed and in the worst ODD conditions | ISO 3691-4 verification scope (A31); ISO 13849 validation plan and report (A36) | OPEN |
| EV-07 | Perception evidence: dataset specification, coverage of ODD (people, wheelchairs, strollers, glass, reflective floors, glare), model verification, triggering condition analysis, performance in worst case lighting | AMLAS stages 2 to 5 (B44); dataset coverage argument (D18); triggering condition analysis (D22); MLEAP data completeness (D21); AI Act Art. 10 as vocabulary (B21) | OPEN |
| EV-08 | Planning and navigation safety: independent safety monitor or minimum risk strategy, behaviour on ODD exit, localisation loss handling | SACE out of context stage and minimum risk strategy (B46); UL 4600 ODD violation handling (B09); EASA GNSS loss procedures as a drone analogue only (C34) | OPEN |
| EV-09 | Simulation credibility: scenario library, simulator validation against physical tests, scenario coverage, documented limits | UL 4600 mix of evidence (B07); AMLAS simulator reality evidence (B45); SACE simulation roles (D20); NASA credibility scale (D27, secondary); SORA simulation justification (D38) | OPEN. Decision needed: credibility method |
| EV-10 | Human interaction evidence: signalling, predictability, stopping by staff and users, tests with representative user classes, escalation path | UL 3300 user classes and surroundings (A38); AI Act Art. 14 oversight and Art. 13 instructions as vocabulary (B24, B25) | OPEN |
| EV-11 | Cybersecurity and update control: who can change safety settings, how updates are re argued | ISO 10218-1:2025 cybersecurity to the-extent it affects-safety (A24, secondary); Machinery Regulation annex on protecting safety functions from alteration (A18, secondary); UL 4600 per update reargument (B07) | OPEN |
| EV-12 | Building condition evidence: temperature range of the space including HVAC failure, dust ingress, glare and daylight effects on sensors; enclosure protection level chosen and tested | IEC 60529 and IEC 60068-2-2 test methods (D62, D63); SORA environmental objectives as analogue (D35, D38); PAS 1883 environment attributes (D11, D12) | OPEN. Decision needed: the envelope and severities (nothing in the sources fixes them) |
| EV-13 | Operating procedures, staff training, supervision model, maintenance and instructions for use | AI Act Art. 13 as vocabulary (B24); SORA procedures objective as analogue (C34); UL 3300 evaluation inputs (A38) | OPEN |
| EV-14 | Logging and retention: what the robot records (near misses, stops, detection confidence), how long, privacy implications | AI Act Art. 12 as vocabulary (B23); retention of technical file and decision data (A05, A18); GCAA record keeping for drone operators as an analogue only (C52, title and scope only, not confirmed) | OPEN. Decision needed: retention period; privacy review (my addition) |
| EV-15 | Incident reporting and field monitoring: definitions, safety performance indicators, root cause process, reporting path to the university and to any authority identified in EV-03 | UL 4600 SPIs and field feedback (B08 to B10); AI Act Arts. 72 and 73 (B29, B30); EU occurrence reporting (D44); no UAE ground robot reporting rule found | OPEN |
| EV-16 | The safety case document itself, in GSN or equivalent, with assumptions, confidence arguments and defeater analysis | GSN community standard (D01); UL 4600 safety case (B06); safety case templates (B47); defeaters (D09) | OPEN |
| EV-17 | Independent review: internal safety review at minimum; optional external evaluation (for example against UL 3300) | UL 3300 third party evaluation (A37); SORA third party verification as an analogue (C16) | OPEN. Optional |
| EV-18 | Change management: criteria for when a model, map or software change reopens the case | UL 4600 per update reargument (B07); "substantial modification" concept (A06) | OPEN |

**What is deliberately not in the skeleton.** I did not assert that any listed instrument *requires* these items for this robot. The Machinery Regulation, ISO 10218 and ISO 3691-4 contain exclusions or scope limits that may place such a robot outside them (A23, A31). What the skeleton does is assemble the evidence the different instruments *ask for in neighbouring contexts*, so the team can choose, justify and fill it.

# 9. Limitations

1. **Paywalls and access.** ISO, IEC and UL standards were read only through catalogue abstracts, previews or secondary summaries. No clause level content of these is asserted. Rows with only such access are labelled accordingly.
2. **Extraction, not raw text.** Most retrieval went through a tool that returns model written extractions. Where a verifier downloaded the PDF itself it is noted in the changelog; for EUR-Lex text, extractions were the only route (EUR-Lex blocked direct download). Wording of Machinery Regulation Articles and Annexes should be read again in the Official Journal PDF (Appendix C).
3. **Unofficial AI Act text.** AI Act article content came mainly from an unofficial reproduction that already includes the 2026 amendments. In the second edition the high risk dates were checked against a recital and a Commission page; the operative amending article was not reached (section 9).
4. **What counts as "required".** The mandatory/conditional/voluntary/guidance scheme is mine. A voluntary standard can be effectively required by a customer, a tender or an insurer; a mandatory regulation can leave the choice of method open. Conditional rows carry the trigger in the row, but triggers were sometimes inferred (for example the harmonised standard route rests on a 2021 list under the old Directive, not the current Official Journal).
5. **Language.** UAE sources were reached mostly in English, with Arabic official texts reached through portal pages (Decree-Law 26/2022); no Arabic GCAA CAR pages were found. OCR noise affected some Arabic extractions.
6. **UAE gaps.** Not found or not read: any UAE rule for ground delivery or service robots; GCAA U-space rule text (news only); GCAA CAR-OCR text; Abu Dhabi regulation text beyond a press release; other emirates' drone rules; the official gazette text of Dubai Law 4/2020; whether UAE regulators have adopted a specific SORA version. These are absence of evidence findings within the searches run.
7. **Source conflicts left unresolved.** Machinery Regulation application date (20 versus 14 January 2027); EASA amendment label (3 versus 4); ISO/TS 15066 status; UL 3300 edition and date labels; EN 18286 approval and Official Journal citation timing; NASA-STD-7009B date; GSN and SACM version dates; whether Part 108 final rule status is as reported by blogs. Appendix B lists these.
8. **Verification limits.** Verifiers used the same fetch tools and share their blind spots. Error rates measure disagreement between independent readings, not ground truth. Some rows were corrected from a single final reading and are labelled single checked. Evidence codes and families are my own scheme and affect the matrix.
9. **Currency.** The status of PDRAs under SORA 2.5, any new UAE rules after the retrieval date, and the EU harmonised standards list under Regulation 2023/1230 were not established.
10. **Duplication.** Some provisions appear in more than one row (section 2.2).

**Official source checks (second edition).** Status of the items flagged for double checking, with the exact locator seen and the retrieval date, is in `data/official_checks.csv` and summarised here. "Confirmed" requires an official source whose own wording was returned and no conflict; extraction only readings stay "open".

{{OFFICIAL_STATUS}}

**Before you quote a row externally:** open its source URL and confirm the passage.

# Appendix A. Evidence table (compact view)

Full table with all fields: `docs/data/evidence_table.csv`. Requirements are truncated here to 170 characters; binding: M mandatory, C conditional, V voluntary, G guidance; access: F full text seen, S summary seen, T title only.

{{APPENDIX}}

# Appendix B. Source conflicts and open status questions

{{CONFLICTS}}

# Appendix C. Documents to fetch by hand (free sources only)

These are the documents the fetch tools could not return. Each is a free public page or file. Nothing here needs a purchase, subscription or paid standard: for ISO, IEC and UL standards the free catalogue and preview pages are the level this study records, and no clause content is asserted from them.

{{DOWNLOADS}}
