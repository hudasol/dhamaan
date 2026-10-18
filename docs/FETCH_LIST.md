# Fetch list

Items that could not be retrieved during the work on this repository, with where to look and what to look for. Nothing here was worked around. The owner can fetch these by hand; texts of standards or paywalled material are never committed.

| Item | Where to look | What to look for | Why it is needed |
|---|---|---|---|
| A public flight or vehicle log with GNSS fixes and a clear licence | https://github.com/PX4/pyulog (sample logs in the repository, check the licence file); https://review.px4.io (check the terms for reuse) | A log file with GNSS position and a stated licence that allows reuse; the licence text and its URL for `data/third_party_manifest.csv` | Protocol item N4: replay of recorded public logs through the GNSS fault checks (deviation D1 in `sim/DEVIATIONS.md`) |
| Official documents still open from the research phase | `docs/REPORT.md` Appendix C | The exact locators listed there | Settle the open official items |
| Full text of locators recorded as unverified | `docs/VALIDATOR_WARNINGS.md` | Whether the mentioned clause exists and says what the paraphrase states | Confirm rows before quoting them |
