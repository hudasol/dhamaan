# ADR-0010 Git workflow for this phase

**Context.** Two instructions differed on branching: one asked for direct commits to main, another for feature branches and pull requests per milestone where possible.

**Decision.** Published history is never rewritten and nothing is force pushed. Work goes straight to main in small commits, each passing the fast check, with a tag per phase. Pull requests were not opened, because no change in this phase deleted data or rewrote published history.

**Consequences.** Linear history on main with phase tags. If the owner prefers milestone pull requests from now on, the next phase can start on a branch.
