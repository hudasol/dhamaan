#!/usr/bin/env python3
"""Render the assurance case YAML to Graphviz DOT (and SVG/PNG if `dot` is installed). Pastel pink theme.
Usage: python3 tools/ac_render.py assurance/library_robot_case.yaml figures/gsn_library_robot"""
from __future__ import annotations
import sys, subprocess, shutil, textwrap
import yaml

PINK = {"goal": "#fde8ef", "strategy": "#f9d5e2", "context": "#fff6f9", "evidence_open": "#ffffff", "evidence_partial": "#fbe3ec","line": "#c2547a", "text": "#4a2433"}

def wrap(s, w=34): return "\\n".join(textwrap.wrap(s, w)) or s
def esc(s): return s.replace('"', "'")

def caption(case: dict) -> str:
    """Diagram title, computed from the case so it cannot drift from the data."""
    def items(status): return [f'{e["id"]} ({e.get("kind", "kind not stated")})' for e in case["evidence"] if e.get("status") == status]
    part, prov = items("partial"), items("provided")
    s = "Illustrative skeleton. Dashed evidence is open."
    if part: s += " Partial: " + ", ".join(part) + "."
    if prov: s += " Provided: " + ", ".join(prov) + "."
    if not part and not prov: s += " No evidence is claimed to exist."
    if any(e.get("kind") == "simulated" for e in case["evidence"] if e.get("status") != "open"):
        s += " Simulated evidence supports no hardware claim."
    return s

def to_dot(case: dict) -> str:
    ev = {e["id"]: e for e in case["evidence"]}
    L = ['digraph GSN {', '  rankdir=TB; nodesep=0.25; ranksep=0.55; bgcolor="white";',
         f'  node [fontname="Helvetica", fontsize=10, style="filled", color="{PINK["line"]}", fontcolor="{PINK["text"]}", margin="0.10,0.06"];',
         f'  edge [color="{PINK["line"]}"];',
         f'  label="{esc(caption(case))}"; labelloc=t; fontname="Helvetica"; fontsize=11;']
    for g in case["goals"]:
        style = "filled,dashed" if g.get("undeveloped") else "filled"
        L.append(f'  {g["id"]} [shape=box, style="{style}", fillcolor="{PINK["goal"]}", label="{g["id"]}\\n{esc(wrap(g["text"]))}"];')
        if g.get("undeveloped"):
            L.append(f'  U_{g["id"]} [shape=diamond, style="filled,dashed", fillcolor="white", label="Undeveloped"]; {g["id"]} -> U_{g["id"]};')
    for s in case["strategies"]:
        L.append(f'  {s["id"]} [shape=parallelogram, fillcolor="{PINK["strategy"]}", label="{s["id"]}\\n{esc(wrap(s["text"], 30))}"];')
    for c in case["contexts"]:
        L.append(f'  {c["id"]} [shape=box, style="rounded,filled,dashed", fillcolor="{PINK["context"]}", label="{c["id"]}\\n{esc(wrap(c["text"], 32))}"];')
    for a in case.get("assumptions", []):
        L.append(f'  {a["id"]} [shape=ellipse, style="filled", fillcolor="{PINK["context"]}", label="{a["id"]} (assumption)\\n{esc(wrap(a["text"], 32))}"];')
    for g in case["goals"]:
        for x in g.get("supported_by") or []: L.append(f'  {g["id"]} -> {x};')
        for c in g.get("context") or []: L.append(f'  {g["id"]} -> {c} [arrowhead=empty, style=dashed];')
        for a in g.get("assumptions") or []: L.append(f'  {g["id"]} -> {a} [arrowhead=empty, style=dotted];')
    for s, tgt in (case.get("strategy_links") or {}).items():
        for t in tgt: L.append(f'  {s} -> {t};')
    for s in case["strategies"]:
        for e in s.get("evidence") or []: L.append(f'  {s["id"]} -> SN_{e.replace("-","")} [style=dashed];')
    used = set()
    for kind in ("goals", "strategies"):
        for it in case[kind]:
            for e in it.get("evidence") or []: used.add(e)
    for e in sorted(used | {x for s in case["strategies"] for x in s.get("evidence") or []}):
        st = ev[e].get("status", "open")
        style = "filled,dashed" if st == "open" else "filled"
        kind = ev[e].get("kind") if st != "open" else None
        label = f"{e}\\n{st}" + (f"\\n{kind}" if kind else "")
        fill = PINK["evidence_open"] if st == "open" else PINK["evidence_partial"]
        L.append(f'  SN_{e.replace("-","")} [shape=circle, style="{style}", fixedsize=true, width=0.8, fontsize=9, fillcolor="{fill}", label="{label}"];')
    for g in case["goals"]:
        for e in g.get("evidence") or []: L.append(f'  {g["id"]} -> SN_{e.replace("-","")} [style=dashed];')
    L.append("}")
    return "\n".join(L)

if __name__ == "__main__":
    src, base = sys.argv[1], sys.argv[2]
    dot = to_dot(yaml.safe_load(open(src, encoding="utf-8")))
    open(base + ".dot", "w", encoding="utf-8", newline="\n").write(dot + "\n")
    if shutil.which("dot"):
        for fmt in ("svg", "png"): subprocess.run(["dot", f"-T{fmt}", base + ".dot", "-o", f"{base}.{fmt}"], check=True)
        print("rendered", base + ".svg", base + ".png")
    else: print("graphviz `dot` not found; wrote DOT only")
