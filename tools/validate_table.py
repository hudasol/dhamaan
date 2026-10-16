#!/usr/bin/env python3
"""Validate the evidence table. Exit code 1 on any error. Free tools only (standard library)."""
from __future__ import annotations
import csv, re, sys, argparse
from urllib.parse import urlparse

import contracts

# Column names and value sets come from the typed contract (tools/contracts.py).
REQUIRED = [c.name for c in contracts.EVIDENCE_TABLE]
BINDING = set(contracts.BINDING)
ACCESS = set(contracts.ACCESS)
BINDING_CHECKED = set(contracts.BINDING_CHECKED)
STATUS = set(contracts.VERIFICATION_STATUS)
CODE = re.compile(r"^E(0\d|1[0-5])$")
ID = re.compile(r"^[A-D]\d{2}$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# Source classes (host suffixes). Catalogue pages show title, scope and price only.
CATALOGUE = ("iso.org","webstore.iec.ch","iec.ch","webstore.ansi.org","ul.com","boss.cen.eu",
             "standards.globalspec.com","knowledge.bsigroup.com","ulstandards.ul.com","standards.ieee.org")
SECONDARY = ("bennettjones.com","dlapiper.com","maak-law.com","droneranker.com","suasnews.com",
             "therobotreport.com","evsint.com","ibf-solutions.com","gulfnews.com","gulftoday.ae",
             "economymiddleeast.com","perforce.com","federal-regs.com","blog.ansi.org","holmessafety.org",
             "rics.org","artificialintelligenceact.eu","ca-times.brightspotcdn.com")
CLAUSE_IN_TEXT = re.compile(r"\b(Art\.|Articles?|Clause|Annex|Section|Sec\.|§)\s*[\dIVX]")

def host(url: str) -> str: return (urlparse(url).netloc or "").lower()
def in_class(h, cls): return any(h == c or h.endswith("." + c) for c in cls)

def validate(path: str, strict: bool = False) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for the evidence table at path."""
    errors, warnings = [], []
    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        missing = [c for c in REQUIRED if c not in (rd.fieldnames or [])]
        if missing: return [f"missing columns: {missing}"], []
        rows = list(rd)
    seen = set()
    for r in rows:
        i = r["id"]; e = lambda m: errors.append(f"{i}: {m}")
        if not ID.match(i): e("id format")
        if i in seen: e("duplicate id")
        seen.add(i)
        for c in ("instrument","requirement_paraphrase","family","source_url","retrieval_date","last_checked"):
            if not r[c].strip(): e(f"empty {c}")
        if r["binding_status"] not in BINDING: e(f"binding_status {r['binding_status']!r}")
        if r["access_level"] not in ACCESS: e(f"access_level {r['access_level']!r}")
        if r["binding_checked"] not in BINDING_CHECKED: e(f"binding_checked {r['binding_checked']!r}")
        if r["verification_status"] not in STATUS: e(f"verification_status {r['verification_status']!r}")
        u = r["source_url"].strip()
        if not re.match(r"^https?://[^\s;]+$", u): e("source_url missing or not a single http(s) URL")
        for c in ("retrieval_date","last_checked"):
            if r[c] and not DATE.match(r[c]): e(f"{c} not ISO date")
        toks = re.findall(r"\bE\d{2}\b", r["evidence_codes"])
        if not toks: e("evidence_codes has no E-code")
        for t in toks:
            if not CODE.match(t): e(f"evidence code {t!r} outside E00 to E15")
        h = host(u)
        if r["clause_or_section_seen"].strip() and r["access_level"] != "full text seen":
            e("clause or section locator present without 'full text seen'")
        if in_class(h, CATALOGUE) and r["access_level"] == "full text seen":
            e(f"'full text seen' not allowed for catalogue source {h}")
        if in_class(h, SECONDARY) and r["access_level"] == "full text seen":
            e(f"'full text seen' not allowed for secondary or unofficial source {h}")
        if r["access_level"] == "title only" and r["clause_or_section_seen"].strip(): e("title only with locator")
        if r["access_level"] != "full text seen" and CLAUSE_IN_TEXT.search(r["requirement_paraphrase"]):
            warnings.append(f"{i}: clause style reference in paraphrase while access is {r['access_level']}")
    if strict: errors += warnings; warnings = []
    return errors, warnings

def clause_mentions(text: str) -> str:
    """The clause style references in a paraphrase, as one '; ' separated string."""
    return "; ".join(m.group(0) for m in CLAUSE_IN_TEXT.finditer(text))

def load_reviewed(path: str) -> dict[str, dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f: return {r["id"]: r for r in csv.DictReader(f)}

def validate_reviewed(path: str, reviewed_path: str, strict: bool = False) -> tuple[list[str], list[str], list[str]]:
    """Like validate, but a clause style warning counts as reviewed when the reviewed file lists the row with the
    same mentions and the row records its locator in clause_reported_unverified. Returns (errors, warnings, reviewed)."""
    errors, warnings = validate(path)
    rev = load_reviewed(reviewed_path)
    with open(path, newline="", encoding="utf-8") as f: rows = {r["id"]: r for r in csv.DictReader(f)}
    still, done = [], []
    for w in warnings:
        i = w.split(":", 1)[0]; r = rows.get(i); x = rev.get(i)
        ok = (r is not None and x is not None and "clause style reference" in w
              and x["mentions"] == clause_mentions(r["requirement_paraphrase"]) and r["clause_reported_unverified"].strip())
        (done if ok else still).append(w)
    for i in rev:
        if i not in rows or not any(w.startswith(i + ":") for w in warnings):
            errors.append(f"{i}: listed in {reviewed_path} but no longer warns (stale review)")
    if strict: errors += still; still = []
    return errors, still, done

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("path", nargs="?", default="data/evidence_table.csv")
    ap.add_argument("--strict", action="store_true", help="treat warnings (unreviewed ones, with --reviewed) as errors")
    ap.add_argument("--reviewed", help="CSV of reviewed clause style warnings (id, mentions, ...)")
    a = ap.parse_args()
    if a.reviewed: errs, warns, done = validate_reviewed(a.path, a.reviewed, a.strict)
    else: (errs, warns), done = validate(a.path, a.strict), []
    for w in warns: print("WARN", w)
    for x in errs: print("ERROR", x)
    print(f"{len(errs)} errors, {len(warns)} warnings" + (f", {len(done)} reviewed warnings" if a.reviewed else ""))
    sys.exit(1 if errs else 0)
