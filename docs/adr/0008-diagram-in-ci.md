# ADR-0008 Diagram rendered in CI

**Context.** Graphviz is free but was not installed on the authoring machine, and installing it needed administrator rights.

**Decision.** `tools/ac_render.py` writes the DOT source, and a test keeps it current with the case. CI installs Graphviz, renders SVG and PNG and uploads them as a build artefact; the committed figures are those CI files.

**Consequences.** The DOT source is always checked. The SVG and PNG are refreshed by downloading the CI artefact after a case change.
