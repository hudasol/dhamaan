"""Part C runner. Refuses to run until the preconditions of docs/PREREG_R3_DRAFT.md are met.

    python -m sim.r3.run_recorded

Superseded for the Jammertest 2024 data by sim/r3/run_real.py, which is guarded by the git frozen plan (data/r3_recorded/PLAN_FREEZE.json).
This older runner keeps its stricter guard for any later registered run. Preconditions, checked here: (1) docs/OSF_REGISTRATION.md carries a registration identifier, (2) data/third_party_manifest.csv lists at
least one licensed recording, (3) the AC-N4 limit is entered in the preregistration. No recording has been replayed to date.
"""
from __future__ import annotations

import csv, os, re, sys

from sim import common

REG = os.path.join(common.ROOT, "docs", "OSF_REGISTRATION.md")
MANIFEST = os.path.join(common.ROOT, "data", "third_party_manifest.csv")


def preconditions(reg_path: str = REG, manifest_path: str = MANIFEST) -> list[str]:
    missing = []
    text = open(reg_path, encoding="utf-8").read() if os.path.exists(reg_path) else ""
    m = re.search(r"^Registration identifier:\s*(\S.*)$", text, re.M)
    if not m or m.group(1).strip().startswith("["): missing.append("registration identifier not entered in docs/OSF_REGISTRATION.md")
    rows = list(csv.DictReader(open(manifest_path, encoding="utf-8"))) if os.path.exists(manifest_path) else []
    if not any(r.get("licence", "").strip() and r.get("path", "").strip() for r in rows): missing.append("no licensed recording in data/third_party_manifest.csv")
    m = re.search(r"^AC-N4 limit per hour:\s*(\S.*)$", text, re.M)
    if not m or m.group(1).strip().startswith("["): missing.append("AC-N4 limit not entered in docs/OSF_REGISTRATION.md")
    return missing


def main() -> int:
    missing = preconditions()
    if missing:
        print("not run:", "; ".join(missing)); return 2
    print("preconditions met; the replay itself is run by the session that holds the registered text"); return 0


if __name__ == "__main__":
    sys.exit(main())
