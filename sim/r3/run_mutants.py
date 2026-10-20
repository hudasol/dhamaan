"""Run every mutant of parts A and B and write sim/results_r3/.

    python -m sim.r3.run_mutants [--cache DIR] [--jobs 2]

Mutants: ORIG (no change, must reproduce the committed scores), M0 (monitor never alarms), M1 (monitor alarms at
the first chance), M2 (each assumed parameter times 0.5 and times 1.5, one at a time) and M3 (fault onset
shifted). Each mutant runs in a fresh interpreter (sim/r3/worker.py). Results are cached per mutant so an
interrupted run resumes; the cache is not a result.
"""
from __future__ import annotations

import argparse, concurrent.futures as cf, json, os, subprocess, sys

from sim import common
from sim.r3 import params, report

OUT = os.path.join(common.ROOT, "sim", "results_r3")
FACTORS = (0.5, 1.5)
M0 = {"set": {"gnss.reject_run": 10 ** 9, "gnss.cusum_limit": 1e9, "gnss.timeout": 1e9, "du3.vrr_threshold": -1.0,
              "gl3.monitor_frames": 10 ** 9}, "monitor": "M0"}
M1 = {"set": {"gnss.cusum_limit": -1.0, "du3.vrr_threshold": 2.0, "gl3.monitor_frames": 0}, "monitor": "M1"}
M3 = {"set": {"gnss.t_onset": 40.0, "du3.t_onset": 1.5}}


def build_specs() -> list[dict]:
    specs = [{"id": "ORIG", "class": "orig", "set": {}}, {"id": "M0", "class": "M0"} | M0,
             {"id": "M1", "class": "M1"} | M1, {"id": "M3", "class": "M3"} | M3]
    for p in params.list_parameters():
        for f in FACTORS:
            v = params.changed_value(p, f)
            specs.append({"id": f"M2|{p['id']}|x{f:g}", "class": "M2", "param": p["id"], "kind": p["kind"], "factor": f,
                          "base": p["base"], "set": {p["id"]: v}, "value": v, "no_change": v == p["base"]})
    return specs


def run_spec(spec: dict, cache: str) -> dict:
    key = os.path.join(cache, spec["id"].replace("|", "_") + ".json")
    if os.path.exists(key): return json.load(open(key, encoding="utf-8"))
    if spec.get("no_change"): out = {"id": spec["id"], "skipped": "the changed value equals the base value"}
    else:
        send = {k: spec[k] for k in ("id", "set", "monitor") if k in spec}
        p = subprocess.run([sys.executable, "-m", "sim.r3.worker", json.dumps(send)], capture_output=True, text=True, cwd=common.ROOT)
        try: out = json.loads(p.stdout.strip().splitlines()[-1])
        except Exception: out = {"id": spec["id"], "error": f"no output; exit {p.returncode}; {p.stderr.strip()[-300:]}"}
    os.makedirs(cache, exist_ok=True)
    with open(key, "w", encoding="utf-8", newline="\n") as f: json.dump(out, f, sort_keys=True)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--cache", default="/tmp/dhamaan_r3_cache"); ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args(argv)
    specs = build_specs()
    print(f"{len(specs)} mutants, {a.jobs} at a time")
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        outs = []
        for i, o in enumerate(ex.map(lambda s: run_spec(s, a.cache), specs), 1):
            outs.append(o)
            if i % 10 == 0: print(i, "done", flush=True)
    paths = report.write_all(specs, outs, OUT)
    for p in paths: print("wrote", os.path.relpath(p, common.ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
