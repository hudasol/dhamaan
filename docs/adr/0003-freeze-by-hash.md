# ADR-0003 Freeze verification results by hash and store CSV byte for byte

**Context.** The brief forbids altering verification results, error rates and the frozen baseline. `outcome.json` already records hashes of two input tables. During this phase a line ending normalisation briefly changed CSV bytes and would have broken those hashes; it was reverted in a new commit.

**Decision.** `data/frozen_sha256.txt` lists the SHA-256 of every verification input and result, the baseline and the evidence table, and `tests/test_frozen.py` fails on any change. `.gitattributes` stores CSV files without line ending conversion.

**Consequences.** Any later correction to the table must be a new, separately versioned file with its own verification, not an edit in place. Documents that disagree with these files are fixed instead.
