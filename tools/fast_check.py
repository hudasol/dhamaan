#!/usr/bin/env python3
"""Fast check: run every repository check in order and stop at the first failure.

Usage: python tools/fast_check.py   (or: make check)
Standard library only; the steps themselves need PyYAML, numpy and pytest.
"""
import json, os, re, subprocess, sys, time

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PY = sys.executable
STEPS = [
    ("repository guard", [PY, "tools/check_repo.py", "."]),
    ("evidence table", [PY, "tools/validate_table.py", "data/evidence_table.csv",
                        "--reviewed", "data/validator_warnings_reviewed.csv", "--strict"]),
    ("assurance case", [PY, "tools/ac_check.py", "assurance/library_robot_case.yaml", "--quiet"]),
    ("secrets scan", [PY, "tools/secrets_scan.py", "."]),
    ("tests", [PY, "-m", "pytest", "-q", "tests"]),
]


def main(argv=None):
    """With --record, also write docs/data/check_summary.json (step summaries, no timings) for HANDOFF."""
    record = "--record" in (argv if argv is not None else sys.argv[1:])
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(errors="replace")   # Windows consoles lack some scripts
    t0, steps = time.time(), []
    for name, cmd in STEPS:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        last = (r.stdout.strip().splitlines() or [""])[-1]
        print(f"{'ok  ' if r.returncode == 0 else 'FAIL'} {name:16} {last}")
        if r.returncode:
            print(r.stdout[-4000:], r.stderr[-4000:], sep="\n")
            return 1
        steps.append({"name": name, "summary": re.sub(r" in [\d.]+s$", "", last)})
    print(f"all checks passed in {time.time() - t0:.1f} s")
    if record:
        passed = int(re.search(r"(\d+) passed", steps[-1]["summary"]).group(1))
        os.makedirs(os.path.join(ROOT, "docs", "data"), exist_ok=True)
        with open(os.path.join(ROOT, "docs", "data", "check_summary.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"tests_passed": passed, "steps": steps}, f, indent=1, sort_keys=True); f.write("\n")
        print("wrote docs/data/check_summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
