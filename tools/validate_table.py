#!/usr/bin/env python3
"""Validate the evidence table. Exit code 1 on any error. Free tools only (standard library)."""
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

def host(url): return (urlparse(url).netloc or "").lower()
def in_class(h, cls): return any(h == c or h.endswith("." + c) for c in cls)

def validate(path, strict=False):
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

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("path", nargs="?", default="data/evidence_table.csv")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    a = ap.parse_args(); errs, warns = validate(a.path, a.strict)
    for w in warns: print("WARN", w)
    for x in errs: print("ERROR", x)
    print(f"{len(errs)} errors, {len(warns)} warnings")
    sys.exit(1 if errs else 0)
