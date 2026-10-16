# Security

## Scope

This repository holds research data, a checker and a software simulation. It runs no service, stores no personal data and holds no credentials.

## What is checked on every push

- `tools/secrets_scan.py`: a regular expression scan for private keys, cloud and repository tokens, credentials in URLs and personal email addresses.
- `detect-secrets` in CI, ignoring only exact SHA-256 digests, which the case records on purpose.
- `tools/check_repo.py`: no PDFs, archives, web pages, raw download folders, standard copyright notices, preview watermarks or long quotations.
- `tests/test_import_contract.py`: no network client and no LLM client in any layer.
- The CI workflow has read only repository permissions.

## GNSS safety boundary

The simulation injects faults into a stream of position fixes in software. It does not generate, simulate at signal level, record or transmit any RF signal, and it contains no jamming or spoofing method. It attributes interference to no actor. Any RF level test needs an authorised, shielded range and is out of scope.

## Reporting a problem

Open an issue on the repository, or contact the owner through the repository profile. Please do not post a secret in an issue; describe where it is instead.
