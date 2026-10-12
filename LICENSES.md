# Licence proposals and third party licences

## Proposals for the owner to confirm

| Part | Proposal | Short reason |
|---|---|---|
| Code (`tools/`, `tests/`, `.github/`) | MIT | Short, permissive, and the same as most of the owner's other repositories. Apache-2.0 is the alternative (marsad uses it); it adds an explicit patent grant. dhill has no licence yet. |
| Documents and data (`docs/`, `data/`, `assurance/`, `README.md`) | CC BY 4.0 | Allows reuse with credit, which suits research notes. Carries no warranty. Does not cover third party standards text, which is never included. |

Nothing is final until the owner confirms. Files `LICENSE` and `LICENSE-DOCS.md` carry a "proposed" notice that should be removed on confirmation.

## Libraries and tools used (free only)

See `data/free_tools_licences.csv`. A licence is recorded only when it was read from a local package file or an official page in the session; others are marked unconfirmed.

## Datasets

No third party dataset is committed. `data/third_party_manifest.csv` is the register; `tools/check_repo.py` fails if a file appears under `third_party/` without a confirmed licence there.

## Sources

The evidence table cites public web pages and documents by URL and retrieval date. It holds short paraphrases and short attributed quotes only. Copyright in those sources stays with their publishers.
