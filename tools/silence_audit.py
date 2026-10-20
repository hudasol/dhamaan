#!/usr/bin/env python3
"""Silence audit of the evidence table (hypothesis H1 in docs/RESEARCH_QUESTION.md).

Layer: tools. Standard library only.

    python tools/silence_audit.py draw       writes data/silence_audit/candidates.csv and coder_template.csv
    python tools/silence_audit.py agreement coder_A.csv coder_B.csv    reports Cohen's kappa per coded field
    python tools/silence_audit.py summarise resolved.csv               H1 counts from the resolved coding

Candidate rows are chosen by a fixed keyword rule (recorded in data/silence_audit/CODEBOOK.md) before any row is coded.
The rule is deliberately wide; coders mark rows that are not about an environmental or interference hazard as `out_of_scope`.
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TABLE = os.path.join(ROOT, "data", "evidence_table.csv")
OUT = os.path.join(ROOT, "data", "silence_audit")

HAZARDS = {
    "heat": r"temperature|thermal|heat|climat|humid|ambient",
    "dust": r"dust|ingress|\bIP\d|particulate|sand",
    "glare": r"glare|\bsun|illumination|lighting|daylight",
    "gnss": r"GNSS|GPS|jamming|spoof|interference",
    "environment_general": r"environment|weather",
}
CANDIDATE_RULE = re.compile("|".join(HAZARDS.values()), re.I)
SEARCH_COLUMNS = ("requirement_paraphrase", "evidence_type", "applies_to")
SHOW = ("id", "instrument", "binding_status", "access_level", "clause_or_section_seen", "requirement_paraphrase", "source_url")
CODED = ("hazard", "asks_evidence", "test_method_fixed", "severity_fixed", "severity_gulf_applicable", "delegated_to_developer", "notes")
CHOICES = {
    "hazard": ("heat", "dust", "glare", "gnss", "environment_general", "out_of_scope"),
    "asks_evidence": ("yes", "no", "unclear"),
    "test_method_fixed": ("yes", "no", "unclear", "na"),
    "severity_fixed": ("yes", "no", "unclear", "na"),
    "severity_gulf_applicable": ("yes", "no", "unclear", "na"),
    "delegated_to_developer": ("yes", "no", "unclear", "na"),
}


def read_csv(path: str) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def candidates(table: list[dict]) -> list[dict]:
    """Rows whose text matches the fixed keyword rule, in table order, with the hazards each keyword group hit."""
    out = []
    for r in table:
        text = " ".join(r[c] for c in SEARCH_COLUMNS)
        if CANDIDATE_RULE.search(text):
            hit = [h for h, pat in HAZARDS.items() if re.search(pat, text, re.I)]
            out.append({**{k: r[k] for k in SHOW}, "keyword_hazards": "; ".join(hit)})
    return out


def kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    if n == 0:
        return float("nan")
    cats = sorted(set(a) | set(b))
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def agreement(rows_a: list[dict], rows_b: list[dict]) -> dict:
    """Cohen's kappa per coded field on the ids both coders coded, with raw agreement."""
    b = {r["id"]: r for r in rows_b}
    ids = [r["id"] for r in rows_a if r["id"] in b and r.get("hazard") and b[r["id"]].get("hazard")]
    res = {"n_rows": len(ids)}
    for field in CHOICES:
        xs = [next(r for r in rows_a if r["id"] == i)[field] for i in ids]
        ys = [b[i][field] for i in ids]
        res[field] = {"kappa": kappa(xs, ys), "raw": (sum(x == y for x, y in zip(xs, ys)) / len(ids)) if ids else None}
    return res


def summarise(rows: list[dict]) -> dict:
    """H1 counts from the resolved coding. Rows seen as summary or title only are counted apart, because they cannot show silence."""
    inscope = [r for r in rows if r["hazard"] != "out_of_scope"]
    def block(rs):
        asking = [r for r in rs if r["asks_evidence"] == "yes"]
        return {"rows": len(rs), "ask_for_evidence": len(asking),
                "of_those_fix_a_test_method": sum(r["test_method_fixed"] == "yes" for r in asking),
                "of_those_fix_a_severity": sum(r["severity_fixed"] == "yes" for r in asking),
                "of_those_fix_a_severity_that_applies_to_a_gulf_site": sum(r["severity_gulf_applicable"] == "yes" for r in asking),
                "of_those_leave_conditions_to_the_developer": sum(r["delegated_to_developer"] == "yes" for r in asking),
                "of_those_with_severity_unclear": sum(r["severity_fixed"] == "unclear" for r in asking),
                "do_not_ask": sum(r["asks_evidence"] == "no" for r in rs), "unclear_whether_they_ask": sum(r["asks_evidence"] == "unclear" for r in rs)}
    return {"candidates": len(rows), "out_of_scope": len(rows) - len(inscope), "in_scope": block(inscope),
            "in_scope_full_text_only": block([r for r in inscope if r["access_level"] == "full text seen"]),
            "by_hazard": {h: block([r for r in inscope if r["hazard"] == h]) for h in sorted({r["hazard"] for r in inscope})},
            "limit": "Applies to retrieved text only. Two automated coders of one model family; agreement does not remove shared error. Rows seen as summary or title only cannot show that an instrument is silent."}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("draw")
    g = sub.add_parser("agreement")
    g.add_argument("coder_a")
    g.add_argument("coder_b")
    m = sub.add_parser("summarise")
    m.add_argument("resolved")
    args = ap.parse_args(argv)
    if args.cmd == "draw":
        rows = candidates(read_csv(TABLE))
        os.makedirs(OUT, exist_ok=True)
        fields = [*SHOW, "keyword_hazards"]
        with open(os.path.join(OUT, "candidates.csv"), "w", encoding="utf-8", newline="\n") as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
            w.writeheader(); w.writerows(rows)
        with open(os.path.join(OUT, "coder_template.csv"), "w", encoding="utf-8", newline="\n") as f:
            w = csv.DictWriter(f, fieldnames=[*SHOW, *CODED], lineterminator="\n")
            w.writeheader()
            for r in rows:
                w.writerow({**{k: r[k] for k in SHOW}, **{c: "" for c in CODED}})
        print(f"{len(rows)} candidate rows written to data/silence_audit/")
        return 0
    import json
    if args.cmd == "summarise":
        print(json.dumps(summarise(read_csv(args.resolved)), indent=1, sort_keys=True))
        return 0
    print(json.dumps(agreement(read_csv(args.coder_a), read_csv(args.coder_b)), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
