"""Run every preregistered experiment and score it. One command, fixed seeds, no hand editing.

Usage: python -m sim.run_all
Writes sim/results/du3.json, gl3.json, gnss.json, scored.json and the evidence bundles EV-08.json, EV-12.json. Every file carries the SYNTHETIC label.
"""
from __future__ import annotations

import sys

from sim import common, du3_lidar, gl3_glare, gnss_n2n4, evidence, score


def main() -> int:
    results = {"du3": du3_lidar.run(), "gl3": gl3_glare.run(), "gnss": gnss_n2n4.run()}
    for name, obj in results.items(): print("wrote", common.write_result(name + ".json", obj))
    s = score.score(results)
    print("wrote", common.write_result("scored.json", s))
    evidence.main()
    t = s["totals"]
    print(f"predictions: {t['hit']} hit, {t['miss']} miss of {t['predictions']}; "
          f"acceptance criteria held {t['acceptance_held']}, failed {t['acceptance_failed']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
