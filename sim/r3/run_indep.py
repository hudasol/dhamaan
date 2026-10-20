"""Part D runner: the round 2 harness on the second author's logs, compared with our own generator's verdicts.

    python -m sim.r3.run_indep

Writes sim/results_r3/independent_generator.json and independent_vs_ours.csv. Our side is the committed round 2 file
sim/results_r2/n4r2.json, read only. All logs are SYNTHETIC.
"""
from __future__ import annotations

import csv, json, os, sys

from sim import common
from sim.r3 import indep, second_author

OUT = os.path.join(common.ROOT, "sim", "results_r3")
FIELDS = ["condition", "ours_detected_within_t_n", "theirs_detected_within_t_n", "ours_false_alarm", "theirs_false_alarm",
          "ours_mean_delay_s", "theirs_mean_delay_s", "ours_max_error_at_alarm_m", "theirs_max_error_at_alarm_m"]


def main() -> int:
    ours = json.load(open(os.path.join(common.ROOT, "sim", "results_r2", "n4r2.json"), encoding="utf-8"))
    theirs = indep.results_for(second_author.generate)
    cmp = indep.compare(ours, theirs)
    os.makedirs(OUT, exist_ok=True)
    obj = {"label": common.LABEL, "evidence_kind": common.EVIDENCE_KIND, "round": 3, "part": "D",
           "author_of_generator": "a separate automated agent of the same model family, from docs/INDEPENDENT_GENERATOR_SPEC.md alone",
           "limit": "Same model family as the first author, so errors can repeat. The spec fixes the central error values, so this tests the "
                    "implementation and its reading of the fault classes, not the choice of those values.",
           "verdicts": cmp["verdicts"], "different": cmp["different"], "conditions": cmp["conditions"]}
    with open(os.path.join(OUT, "independent_generator.json"), "w", encoding="utf-8", newline="\n") as f: f.write(common.dump(obj))
    with open(os.path.join(OUT, "independent_vs_ours.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n"); w.writeheader()
        for r in cmp["conditions"]: w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
    print("verdicts that differ:", cmp["different"] or "none")
    for r in cmp["verdicts"]: print(f"  {r['id']:9} ours held={r['ours_held']} theirs held={r['theirs_held']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
