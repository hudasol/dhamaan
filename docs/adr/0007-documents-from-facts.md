# ADR-0007 Documents generated from facts, no hand typed numbers

**Context.** Every number in a document must come from a file produced by code, and documents must not drift from results.

**Decision.** Documents with numbers are rendered from templates by `docsgen/build.py`, with values computed in `docsgen/facts.py`. A test rejects any digit in a template outside identifiers, code spans, links, dates and placeholders, and another fails when a generated file is stale.

**Consequences.** Editing a number means editing data or code, not prose. Interpretive sentences in templates still need review when results change; the staleness test shows when that is due.
