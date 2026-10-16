# Deviation log

Dated record of every difference between the preregistered plan (`sim/PREREGISTRATION.md`) or the
protocol (`docs/GULF_TEST_PROTOCOL.md`) and what was run. Entries are only added, never edited.

## 2026-10-16, before the first evaluation run

- **D1. N4 uses no public log.** The protocol item N4 names replay of recorded public logs (for example
  open PX4 flight logs). No log was downloaded or used. The replay fault replays the synthetic receiver's
  own earlier fixes, so the result is labelled `simulated`, not `replayed`. Reason: the brief for this
  phase allows software only fault injection, and no public log licence was checked.
