#!/usr/bin/env python3
"""Checker for the structured assurance case (YAML). Free tools only: Python and PyYAML.

Findings have a severity:
  ERROR  structural or integrity problem (dangling id, untraced evidence, unsupported word, invented evidence,
         schema violation, missing evidence kind, missing or mismatched artefact hash, simulated evidence
         marked provided under a hardware claim). Exit code 1.
  FLAG   an honest gap that the case is expected to show while work is open (claim without evidence, evidence still open,
         undeveloped goal, weak source row, partial evidence, hardware claim backed only by simulation).
         Exit code 0 unless --strict.
"""
from __future__ import annotations
import argparse, csv, hashlib, os, re, sys
import yaml
import contracts

STATUSES = set(contracts.EVIDENCE_STATUS)
SAFE_WORDS = re.compile(r"\b(safe|safely|safer|safest)\b", re.I)
OBLIGATION_WORDS = re.compile(r"\b(must|shall|is required|are required|required to|mandatory|obligatory|is obliged|are obliged)\b", re.I)
BINDING_STATUSES = {"mandatory", "conditional"}   # statuses that can carry an obligation (conditional: under its condition)
ABSOLUTE_WORDS = re.compile(r"\b(guarantee[sd]?|certified|compliant|proven|always|never|risk[- ]free|fully secure|zero risk)\b", re.I)

def load(path: str) -> dict:
    with open(path, encoding="utf-8") as f: return yaml.safe_load(f)

def sha256_file(path: str) -> str:
    with open(path, "rb") as f: return hashlib.sha256(f.read()).hexdigest()

def table_rows(path: str) -> dict[str, dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f: return {r["id"]: r for r in csv.DictReader(f)}

def check(case: dict, rows: dict, base_dir: str = ".") -> list[tuple[str, str, str, str]]:
    """Return findings as (severity, code, id, message); severity is ERROR or FLAG."""
    out = []  # (severity, code, id, message)
    add = lambda s, c, i, m: out.append((s, c, i, m))
    for msg in contracts.case_conformance(case): add("ERROR", "SCHEMA", msg.split(":")[0], msg)
    ids = {}
    for kind in ("assumptions", "contexts", "strategies", "goals", "evidence"):
        for it in case.get(kind) or []:
            if it["id"] in ids: add("ERROR", "DUPLICATE_ID", it["id"], f"id used in {ids[it['id']]} and {kind}")
            ids[it["id"]] = kind
    ev = {e["id"]: e for e in case.get("evidence") or []}
    goals = {g["id"]: g for g in case.get("goals") or []}
    strategies = {s["id"]: s for s in case.get("strategies") or []}
    contexts = {c["id"] for c in case.get("contexts") or []}
    assumptions = {a["id"] for a in case.get("assumptions") or []}
    links = case.get("strategy_links") or {}

    # references
    for kind in ("goals", "strategies", "contexts"):
        for it in case.get(kind) or []:
            for e in it.get("evidence") or []:
                if e not in ev: add("ERROR", "DANGLING", it["id"], f"unknown evidence id {e}")
            for c in it.get("context") or []:
                if c not in contexts: add("ERROR", "DANGLING", it["id"], f"unknown context {c}")
            for a in it.get("assumptions") or []:
                if a not in assumptions: add("ERROR", "DANGLING", it["id"], f"unknown assumption {a}")
    children = {g: [] for g in goals}
    for g in goals.values():
        for s in g.get("supported_by") or []:
            if s not in goals and s not in strategies: add("ERROR", "DANGLING", g["id"], f"unknown supported_by {s}")
            children[g["id"]].append(s)
    for s, tgt in links.items():
        if s not in strategies: add("ERROR", "DANGLING", s, "strategy_links key is not a strategy")
        for t in tgt:
            if t not in goals: add("ERROR", "DANGLING", s, f"strategy link to unknown goal {t}")
    # reachability and cycles
    def walk(n, seen, stack):
        if n in stack: add("ERROR", "CYCLE", n, "cycle in supported_by"); return
        if n in seen: return
        seen.add(n); stack.append(n)
        for c in (children.get(n) or []) + (links.get(n) or []): walk(c, seen, stack)
        stack.pop()
    roots = [g for g in goals if not any(g in (x.get("supported_by") or []) or g in links.get(s, []) for x in goals.values() for s in strategies)] or list(goals)
    seen = set()
    for r in roots: walk(r, seen, [])
    for g in goals:
        if g not in seen: add("ERROR", "ORPHAN", g, "goal not reachable from a top goal")

    # evidence items
    for e in ev.values():
        i = e["id"]
        if e.get("status") not in STATUSES: add("ERROR", "BAD_STATUS", i, f"status {e.get('status')!r}")
        if e.get("status") == "open": add("FLAG", "EVIDENCE_OPEN", i, f"evidence still open: {e.get('title','')}")
        if e.get("status") in ("partial", "provided"):
            art = e.get("artefact")
            if e.get("status") == "partial":
                add("FLAG", "EVIDENCE_PARTIAL", i, f"evidence partial ({e.get('kind', 'kind not stated')}): {e.get('title','')}")
            if not e.get("kind"): add("ERROR", "MISSING_KIND", i, f"status {e['status']} without an evidence kind (simulated, bench, field)")
            if not art: add("ERROR", "INVENTED_EVIDENCE", i, f"status {e['status']} without an artefact path")
            elif not os.path.isfile(os.path.join(base_dir, art)): add("ERROR", "INVENTED_EVIDENCE", i, f"artefact not found: {art}")
            elif not e.get("sha256"): add("ERROR", "MISSING_HASH", i, f"status {e['status']} without the artefact sha256")
            elif sha256_file(os.path.join(base_dir, art)) != e["sha256"]:
                add("ERROR", "HASH_MISMATCH", i, f"artefact {art} does not match the recorded sha256")
        rs = e.get("rows") or []
        if not rs: add("ERROR", "UNTRACED", i, "evidence item has no evidence table rows")
        for r in rs:
            if r not in rows: add("ERROR", "UNTRACED", i, f"row {r} not in evidence table")
            elif rows[r]["access_level"] == "title only":
                add("FLAG", "WEAK_SOURCE", i, f"row {r} is title and scope only, so it motivates but does not support")
        if e.get("decision_needed"): add("FLAG", "DECISION_NEEDED", i, e.get("note", "a decision is needed"))

    # claim coverage: goals
    def ev_of(n, seen=None):
        seen = seen or set()
        if n in seen: return set()
        seen.add(n)
        if n in goals:
            s = set(goals[n].get("evidence") or [])
            for c in children[n] + links.get(n, []): s |= ev_of(c, seen)
            return s
        if n in strategies:
            s = set(strategies[n].get("evidence") or [])
            for c in links.get(n, []): s |= ev_of(c, seen)
            return s
        return set()
    for g in goals.values():
        es = ev_of(g["id"])
        done = [ev[e] for e in es if e in ev and ev[e].get("status") != "open"]
        if g.get("claim_about") == "hardware":   # checked for every goal, undeveloped or not
            for x in done:
                if x.get("kind") == "simulated" and x.get("status") == "provided":
                    add("ERROR", "SIM_CLOSES_HARDWARE", x["id"], f"simulated evidence marked provided supports hardware claim {g['id']}")
        if g.get("undeveloped"):
            add("FLAG", "UNDEVELOPED", g["id"], g.get("undeveloped_reason", "goal marked undeveloped"))
            continue
        if not es: add("FLAG", "NO_EVIDENCE", g["id"], "claim has no evidence item anywhere in its support tree")
        elif all(ev[e].get("status") == "open" for e in es if e in ev):
            add("FLAG", "CLAIM_ALL_OPEN", g["id"], "every evidence item supporting this claim is open, so the claim is unsupported today")
        elif g.get("claim_about") == "hardware" and all(x.get("kind") == "simulated" for x in done):
            add("FLAG", "CLAIM_SIM_ONLY", g["id"], "only simulated evidence supports this hardware claim, so it stays open")
    for s in strategies.values():
        if not (s.get("evidence") or links.get(s["id"])): add("FLAG", "NO_EVIDENCE", s["id"], "strategy has no evidence and supports no goal")

    # wording
    for kind in ("goals", "strategies", "contexts"):
        for it in case.get(kind) or []:
            t = it.get("text", "")
            if SAFE_WORDS.search(t) and not (it.get("context") or kind == "contexts"):
                add("ERROR", "UNSUPPORTED_WORD", it["id"], "uses 'safe' without a stated context")
            m = ABSOLUTE_WORDS.search(t)
            if m: add("ERROR", "UNSUPPORTED_WORD", it["id"], f"absolute or certification word {m.group(0)!r}")
    for e in ev.values():
        m = ABSOLUTE_WORDS.search(e.get("title", "") + " " + e.get("note", ""))
        if m: add("ERROR", "UNSUPPORTED_WORD", e["id"], f"absolute or certification word {m.group(0)!r}")

    # obligation strength: a goal worded as an obligation needs a cited row whose binding status is binding
    for g in goals.values():
        m = OBLIGATION_WORDS.search(g.get("text", ""))
        if not m: continue
        cited = [r for e in ev_of(g["id"]) if e in ev for r in ev[e].get("rows") or [] if r in rows]
        strengths = {rows[r].get("binding_status", "") for r in cited}
        if not strengths & BINDING_STATUSES:
            add("ERROR", "OVERSTATED_OBLIGATION", g["id"],
                f"worded as an obligation ({m.group(0)!r}) but its cited rows are only {sorted(strengths) or 'none'}")
    return out

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("case", nargs="?", default="assurance/library_robot_case.yaml")
    ap.add_argument("--table", default="data/evidence_table.csv")
    ap.add_argument("--strict", action="store_true", help="exit 1 on FLAG findings as well")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--root", help="directory that artefact paths are relative to (default: the case file's parent's parent)")
    a = ap.parse_args(argv)
    res = check(load(a.case), table_rows(a.table), a.root or os.path.dirname(os.path.abspath(a.case)) + "/..")
    from collections import Counter
    c = Counter(code for s, code, i, m in res)
    if not a.quiet:
        for s, code, i, m in res: print(f"{s:5} {code:17} {i:7} {m}")
    errs = sum(1 for r in res if r[0] == "ERROR"); flags = sum(1 for r in res if r[0] == "FLAG")
    print(f"{errs} errors, {flags} flags; " + ", ".join(f"{k}={v}" for k, v in sorted(c.items())))
    return 1 if errs or (a.strict and flags) else 0

if __name__ == "__main__":
    sys.exit(main())
