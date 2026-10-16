# ADR-0002 Contracts in Python, JSON schemas generated

**Context.** The evidence table and the assurance case needed a schema. A JSON schema validator is an extra dependency, and value sets were already duplicated in the validator.

**Decision.** Define the contract once as typed dataclasses in `tools/contracts.py`. The validator and the checker read their value sets from it. `tools/gen_schema.py` generates JSON schemas for other readers, and a test fails when they are stale.

**Consequences.** One source of truth with no new dependency. The generated schemas are for readers outside Python; the repository itself validates through the contract code.
