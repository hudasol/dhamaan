#!/usr/bin/env python3
"""Credit ledger: how much of a claim each piece of evidence can carry.

Layer: tools. Standard library and PyYAML only. The four conditions are adopted from outside frameworks for the
credibility of simulation evidence (see docs/RELATED_WORK.md: the NASA credibility standard, the ASME V&V 40
risk based approach, and the sources it lists); none of them is new here. Each is decided by a reference that
the checker can open, never by a statement in a field:

  1 context of use   the evidence names context nodes of the case, and they exist
  2 validation       the evidence names measured data in the repository that it was compared with
  3 uncertainty      the evidence names a sensitivity or uncertainty result in the repository
  4 independence     the evidence names the record of a verifier who is not the developer

Ceiling (CREDIT_LEVELS). Bench and field evidence are measurements and get `supporting` unless open; the
conditions below limit simulated evidence:
  none           evidence is open, or its context of use is not stated
  demonstration  context stated, no validation against measured data: it shows the case can take evidence
  indicative     validated against measured data, but uncertainty or independence is missing
  supporting     all four conditions met

What a claim needs from evidence marked provided: a hardware claim needs `supporting` and a bench or field kind
(the existing rule that simulated evidence never closes a hardware claim stays); a software claim needs
`indicative`; process and argument claims need none. Evidence that is only partial is never held to this, but its
ceiling is shown.
"""
from __future__ import annotations

import argparse, csv, os, re, sys

import contracts
import yaml

LEVELS = contracts.CREDIT_LEVELS
CONDITIONS = ("context_of_use", "validation", "uncertainty", "independence")
REQUIRED = {"hardware": "supporting", "software": "indicative", "process": "none", "argument": "none"}
LABEL = {"context_of_use": "context of use stated", "validation": "validated against measured data",
         "uncertainty": "uncertainty or sensitivity reported", "independence": "verifier independent of the developer"}


def _safe(path) -> bool:
    return isinstance(path, str) and bool(path) and not (os.path.isabs(path) or path.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", path)
                                                          or ".." in path.replace("\\", "/").split("/"))


def conditions(e: dict, context_ids: set[str], base_dir: str = ".") -> tuple[dict[str, bool], list[str]]:
    """Which of the four conditions an evidence item meets, and problems with the references it gives."""
    problems, met = [], dict.fromkeys(CONDITIONS, False)
    ctx = e.get("credibility_context") or []
    if ctx:
        bad = [c for c in ctx if c not in context_ids]
        if bad: problems.append(f"credibility_context names unknown context {bad}")
        else: met["context_of_use"] = True
    for cond, key in (("validation", "credibility_physical_data"), ("uncertainty", "credibility_uncertainty"),
                      ("independence", "credibility_verifier_record")):
        path = e.get(key)
        if path is None: continue
        if not _safe(path): problems.append(f"{key} {path!r} must be a relative path inside the repository")
        elif not os.path.isfile(os.path.join(base_dir, path)): problems.append(f"{key} file not found: {path}")
        else: met[cond] = True
    return met, problems


def ceiling(e: dict, met: dict[str, bool]) -> str:
    """Bench and field evidence are measurements, so the four conditions (which govern simulation) do not limit them."""
    if e.get("status") == "open": return "none"
    if e.get("kind") in ("bench", "field"): return "supporting"
    if not met["context_of_use"]: return "none"
    if not met["validation"]: return "demonstration"
    return "supporting" if met["uncertainty"] and met["independence"] else "indicative"


def required_level(goal: dict) -> str:
    return REQUIRED.get(goal.get("claim_about"), "none")


def meets(level: str, needed: str) -> bool:
    return LEVELS.index(level) >= LEVELS.index(needed)


def ledger(case: dict, base_dir: str = ".") -> list[dict]:
    """One row per evidence item that is not open."""
    ctx = {c["id"] for c in case.get("contexts") or []}
    rows = []
    for e in case.get("evidence") or []:
        if e.get("status") == "open": continue
        met, problems = conditions(e, ctx, base_dir)
        lvl = ceiling(e, met)
        rows.append({"evidence": e["id"], "status": e["status"], "kind": e.get("kind", ""), "ceiling": lvl,
                     **{c: met[c] for c in CONDITIONS}, "unmet": "; ".join(LABEL[c] for c in CONDITIONS if not met[c]),
                     "problems": "; ".join(problems)})
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("case", nargs="?", default="assurance/library_robot_case.yaml")
    ap.add_argument("--csv", help="write the ledger to this path")
    a = ap.parse_args(argv)
    case = yaml.safe_load(open(a.case, encoding="utf-8"))
    rows = ledger(case, os.path.dirname(os.path.abspath(a.case)) + "/..")
    for r in rows: print(f"{r['evidence']:7} {r['ceiling']:14} unmet: {r['unmet'] or 'none'}")
    if a.csv:
        os.makedirs(os.path.dirname(a.csv) or ".", exist_ok=True)
        with open(a.csv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["evidence"], lineterminator="\n"); w.writeheader(); w.writerows(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
