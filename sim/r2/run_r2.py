"""Round 2 runner. Two separate steps, so the design record is committed before any held out run.

  python -m sim.r2.run_r2 design   development seed set only; writes design_gl3.json and design_du3.json
  python -m sim.r2.run_r2 score    held out seed set; reads the design files; writes the results and scored_r2.json
"""
from __future__ import annotations

import json, os, sys

from sim.r2 import base, du3_r2, evidence_r2, gl3_r2, heat, n4_r2, score_r2


def design() -> int:
    for name, fn, items in (("design_gl3", gl3_r2.design, ["GL3"]), ("design_du3", du3_r2.design, ["DU3"])):
        obj = base.envelope(name.upper(), items, "development", {}, {}, {}) | fn()
        print("wrote", base.write(name + ".json", obj))
    return 0


def score() -> int:
    d = {n: json.load(open(os.path.join(base.RESULTS, n + ".json"), encoding="utf-8")) for n in ("design_gl3", "design_du3")}
    results = dict(d)
    results["gl3r2"] = gl3_r2.score(d["design_gl3"]["chosen"])
    results["du3r2"] = du3_r2.score(d["design_du3"]["chosen"])
    results["heat"] = heat.score()
    results["n4r2"] = n4_r2.score()
    for n in ("gl3r2", "du3r2", "heat", "n4r2"): print("wrote", base.write(n + ".json", results[n]))
    s = score_r2.score_r2(results)
    print("wrote", base.write("scored_r2.json", s))
    evidence_r2.main()
    g, o = n4_r2.example_log()
    os.makedirs(os.path.join(base.RESULTS, "standin_log"), exist_ok=True)
    for name, text in (("gnss.csv", g), ("odometry.csv", o)):
        with open(os.path.join(base.RESULTS, "standin_log", name), "w", encoding="utf-8", newline="\n") as f: f.write(text)
    t = s["totals"]
    print(f"round 2: {t['hit']} hit, {t['miss']} miss of {t['predictions']}; acceptance held {t['acceptance_held']}, failed {t['acceptance_failed']}")
    return 0


if __name__ == "__main__":
    sys.exit({"design": design, "score": score}[sys.argv[1]]())
