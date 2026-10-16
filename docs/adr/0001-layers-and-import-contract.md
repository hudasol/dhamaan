# ADR-0001 Layers and a static import contract

**Context.** The repository mixes research data, checks, a simulation and generated documents. A check that quietly depends on simulation code, or a document builder that feeds back into data, would make results hard to trust.

**Decision.** Four layers: data, tools, sim, docsgen. A layer may import only the standard library, its listed third party packages and lower layers. `tests/test_import_contract.py` parses imports statically and also rejects dynamic imports and any network or LLM client.

**Consequences.** Tools cannot read simulation code, only its output files. The docs layer may read everything. Adding a dependency means editing the contract test, which makes the change visible in review.
