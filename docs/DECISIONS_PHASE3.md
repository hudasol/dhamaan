# Decisions, phase 3

Decisions taken during phase 3, with the reason for each. Entries are added in order and not edited afterwards.

- **P3-01 Compressed budgets.** The stage budgets requested add up to more than the session window. Each stage gets a shorter budget (`docs/PLAN_PHASE3.md`); scope is cut inside a stage before a later stage is dropped, and the last 45 minutes stay reserved for review and release hygiene.
- **P3-02 Git workflow unchanged.** Small commits go straight to main with a tag per stage, as in ADR-0010. No pull requests, because no change deletes data or rewrites history.
- **P3-03 Related repositories are linked, not copied.** dhill has no licence selected, so nothing is taken from it except one figure stated in its README, cited by link. marsad is Apache-2.0; no code is taken from it either, only the idea of trust states, cited by link.
- **P3-04 N4 public log not retrieved.** The retrieval method used returns text extractions of web pages, not raw binary flight logs, so a public log cannot be retrieved byte for byte that way. The replay harness is built on a synthetic stand in log, and the retrieval goes to `docs/FETCH_LIST.md`.
- **P3-05 A command layer above docs.** The `dhamaan` command needs the checks (tools), the log scoring (sim) and rendering (docsgen). It lives in a new top layer, `dhamaan/`, that may import every layer below it; the three existing layers keep their order and the import contract test covers the new layer.
- **P3-06 Wording corrected after review.** The introduction and P3-01 and P3-04 were reworded to neutral process language after the review (register entries from R21); the decisions themselves are unchanged.
