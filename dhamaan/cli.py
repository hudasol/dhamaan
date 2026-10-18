"""dhamaan command line.

  dhamaan check-table [TABLE] [--reviewed FILE] [--strict]     validate an evidence table
  dhamaan check-case  [CASE] [--table TABLE] [--root DIR] [--strict]   check an assurance case
  dhamaan render      [CASE] [--out BASE]                      write the case diagram (DOT; SVG and PNG if Graphviz is installed)
  dhamaan new-case    TEMPLATE --out FILE [--title TEXT]       start a case from a template and check it
  dhamaan new-case    --list                                   list the templates
  dhamaan score-log   --gnss FILE --odometry FILE [--json]     score a log with the GNSS fault checks

Exit codes: 0 success, 1 check failed or input rejected, 2 usage error.
"""
from __future__ import annotations

import argparse, json, os, shutil, subprocess, sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, ROOT)

import ac_check  # noqa: E402  (tools layer)
import ac_render  # noqa: E402
import validate_table  # noqa: E402
from sim.r2 import replay  # noqa: E402  (sim layer)

TEMPLATES = os.path.join(ROOT, "assurance", "templates")
TABLE = os.path.join(ROOT, "data", "evidence_table.csv")
REVIEWED = os.path.join(ROOT, "data", "validator_warnings_reviewed.csv")
CASE = os.path.join(ROOT, "assurance", "library_robot_case.yaml")
SCORE_NOTE = ("Method parameters are the first round proposal values (assumed, proposal), not values tuned to any robot. "
              "A score is evidence of kind bench or field only for a log recorded on real equipment; it closes no claim by itself.")


def cmd_check_table(a) -> int:
    reviewed = a.reviewed if a.reviewed is not None else (REVIEWED if os.path.abspath(a.table) == os.path.abspath(TABLE) else None)
    if reviewed: errs, warns, done = validate_table.validate_reviewed(a.table, reviewed, a.strict)
    else: (errs, warns), done = validate_table.validate(a.table, a.strict), []
    for w in warns: print("WARN", w)
    for e in errs: print("ERROR", e)
    print(f"{len(errs)} errors, {len(warns)} warnings" + (f", {len(done)} reviewed warnings" if reviewed else ""))
    return 1 if errs else 0


def cmd_check_case(a) -> int:
    argv = [a.case, "--table", a.table] + (["--root", a.root] if a.root else []) + (["--strict"] if a.strict else []) + (["--quiet"] if a.quiet else [])
    return ac_check.main(argv)


def cmd_render(a) -> int:
    dot = ac_render.to_dot(ac_check.load(a.case))
    with open(a.out + ".dot", "w", encoding="utf-8", newline="\n") as f: f.write(dot + "\n")
    print("wrote", a.out + ".dot")
    if shutil.which("dot"):
        for fmt in ("svg", "png"): subprocess.run(["dot", f"-T{fmt}", a.out + ".dot", "-o", f"{a.out}.{fmt}"], check=True)
        print("wrote", a.out + ".svg", a.out + ".png")
    else: print("Graphviz is not installed; wrote DOT only")
    return 0


def templates(directory: str = TEMPLATES) -> dict[str, str]:
    if not os.path.isdir(directory): return {}
    return {f[:-5]: os.path.join(directory, f) for f in sorted(os.listdir(directory)) if f.endswith(".yaml")}


def cmd_new_case(a) -> int:
    t = templates(a.templates)
    if a.list or not a.template:
        for name in t: print(name)
        return 0 if a.list else 2
    if a.template not in t:
        print(f"unknown template {a.template!r}; known: {', '.join(t) or 'none'}"); return 1
    if os.path.exists(a.out) and not a.force:
        print(f"{a.out} exists; use --force to overwrite"); return 1
    text = open(t[a.template], encoding="utf-8").read()
    if a.title:
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("  title: "): lines[i] = "  title: " + json.dumps(a.title); break
        text = "\n".join(lines)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f: f.write(text)
    print("wrote", a.out)
    return ac_check.main([a.out, "--table", a.table, "--root", ROOT, "--quiet"])


def cmd_score_log(a) -> int:
    try:
        g = replay.read_csv(open(a.gnss, encoding="utf-8").read(), replay.GNSS_COLUMNS)
        o = replay.read_csv(open(a.odometry, encoding="utf-8").read(), replay.ODO_COLUMNS)
    except (OSError, replay.LogError) as e:
        print(f"log rejected: {e}"); return 1
    res = replay.score_log(g, o) | {"note": SCORE_NOTE}
    if a.json: print(json.dumps(res, indent=1, sort_keys=True))
    else:
        print(f"fixes {res['fixes']}, odometry rows {res['odometry_rows']}")
        print("no fault declared" if res["t_alarm"] is None else f"fault declared at t = {res['t_alarm']:.1f} s ({res['reason']})")
        if res["max_error_m"] is not None: print(f"largest navigation error against the reference: {res['max_error_m']:.2f} m")
        print(SCORE_NOTE)
    return 0


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="dhamaan", description="Checks, rendering, templates and log scoring for the dhamaan evidence base.")
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("check-table", help="validate an evidence table")
    p.add_argument("table", nargs="?", default=TABLE); p.add_argument("--reviewed"); p.add_argument("--strict", action="store_true")
    p.set_defaults(fn=cmd_check_table)
    p = sub.add_parser("check-case", help="check an assurance case")
    p.add_argument("case", nargs="?", default=CASE); p.add_argument("--table", default=TABLE); p.add_argument("--root")
    p.add_argument("--strict", action="store_true"); p.add_argument("--quiet", action="store_true"); p.set_defaults(fn=cmd_check_case)
    p = sub.add_parser("render", help="write the case diagram")
    p.add_argument("case", nargs="?", default=CASE); p.add_argument("--out", default="case_diagram"); p.set_defaults(fn=cmd_render)
    p = sub.add_parser("new-case", help="start a case from a template")
    p.add_argument("template", nargs="?"); p.add_argument("--out", default="new_case.yaml"); p.add_argument("--title")
    p.add_argument("--list", action="store_true"); p.add_argument("--force", action="store_true")
    p.add_argument("--templates", default=TEMPLATES, help=argparse.SUPPRESS); p.add_argument("--table", default=TABLE, help=argparse.SUPPRESS)
    p.set_defaults(fn=cmd_new_case)
    p = sub.add_parser("score-log", help="score a log with the GNSS fault checks")
    p.add_argument("--gnss", required=True); p.add_argument("--odometry", required=True); p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_score_log)
    return ap


def main(argv: list[str] | None = None) -> int:
    a = parser().parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
