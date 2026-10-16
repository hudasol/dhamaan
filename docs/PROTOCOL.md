# Research Protocol (written before research began, 2026-10-11)

**Question.** Across robot and drone safety standards and regulations, what evidence must a developer produce before deploying autonomous or semi-autonomous machines in workplaces and public spaces; what is mandatory vs voluntary; where are the gaps (learning-based autonomy; Gulf conditions: heat, dust, glare, GNSS interference)?

## Inclusion criteria
- Instruments: standards, regulations, regulator guidance, and published assurance methods in the scope list (ISO 12100, 10218, 13482, 3691-4, IEC 61508, ISO 13849, EU Machinery Regulation, UL 3300, ISO 21448, UL 4600, EU AI Act, learning-enabled component assurance literature, EASA specific category, JARUS SORA, FAA, UAE GCAA/emirate rules, safety-case/GSN/ODD/simulation-credit/runtime-monitoring/incident-reporting practice).
- A row enters the evidence table only if it is a testable requirement or evidence expectation, visible in a source the researcher actually retrieved.
- Sources acceptable: official regulator/standards-body pages (catalogue entries, previews, abstracts), EUR-Lex, EASA/JARUS/FAA/GCAA documents, open academic papers, public summaries by reputable bodies. Blogs/vendor pages are allowed only as "summary seen" and are flagged as secondary.

## Search strategy
Four independent streams (A machinery/robots, B autonomy/AI, C drones/UAE, D assurance practice). Per instrument: (1) find official catalogue/status page for current edition and status; (2) find regulator or open-access text; (3) find public summaries; (4) record what was and was not accessible. UAE: search GCAA, UAE legislation portal, emirate authorities (Dubai, Abu Dhabi), in English and Arabic; if nothing is found, record "not findable".

## How "required" is decided
- **mandatory**: legal text binding on the developer/operator (regulation, directly applicable law), seen in the legal text or an official regulator page.
- **conditional**: binding only if a trigger holds (e.g. risk class, category, harmonised-standard route to presumption of conformity, contractual/market requirement).
- **voluntary**: standards not referenced by law in the relevant jurisdiction; use is by choice or contract.
- **guidance**: regulator or body guidance, non-binding.
Where a standard is "voluntary" in law but gives presumption of conformity under a regulation, it is recorded as conditional with the route stated. Conflicts between sources are flagged, not resolved silently.

## Access levels (per row)
- `full text seen`: the cited passage itself was read.
- `summary seen`: only an official/public summary, abstract, or secondary description was read.
- `title only`: catalogue entry/title and scope only; text not accessed. No clause numbers or requirement detail may be asserted.

## Paywall handling
Paywalled standards are never reproduced or reconstructed from memory. Their rows carry `title only` or `summary seen`, clause = blank, and requirement text limited to what the catalogue/scope statement says. Clause numbers are recorded only if seen in a retrieved source.

## Integrity rules
Cite only retrieved sources; no invented clause numbers, dates, editions, quotes; quotes under 15 words and attributed; documents-say vs interpretation visibly separated; research, not certification or legal advice.

## Verification
After merge, an independent verifier re-fetches sources for a random sample of >= 25 rows (seeded random), classifies each as correct / partly wrong / unsupported, reports error rate; errors are fixed and the rate reported honestly.

## Table schema (CSV)
id, instrument, edition_or_version, status_note, clause_or_section_seen, requirement_paraphrase, binding_status, applies_to, evidence_type, who_verifies, source_url, retrieval_date, access_level, notes

Wording note (2026-10-16): one tool specific word in the verification step was replaced by "verifier". The procedure is unchanged.
