"""Part D: score the round 2 harness on logs from an independently written generator and compare verdicts.

The second author wrote the generator from docs/INDEPENDENT_GENERATOR_SPEC.md alone. This module feeds its logs to the
same harness (sim/r2/replay.py) with the same thresholds and scores the round 2 N4 predictions and acceptance
criteria with the same functions, so that any difference in verdict comes from the data, not from the scoring.
All logs are SYNTHETIC.
"""
from __future__ import annotations

from collections import OrderedDict

from sim import acceptance as A, common, gnss_n2n4 as G, score
from sim.r2 import base, replay
from sim.r2.predictions_r2 import ACCEPTANCE, PREDICTIONS

ONSET = G.Config().t_onset


def _n4_items():
    mine = lambda e: all(m.startswith("n4r2:") for c in e["checks"] for m in c["metrics"])
    return [e for e in PREDICTIONS + ACCEPTANCE if mine(e)]


def results_for(generate, seeds: int = base.SEEDS, conditions=G.CONDITIONS) -> dict:
    """The n4r2 result structure, from a generator generate(kind, size, seed) -> (gnss rows, odometry rows)."""
    cfg = G.Config(); conds = OrderedDict()
    for kind, size in conditions:
        cond = f"{kind}={size:g}"; res = []
        for i in range(seeds):
            g, o = generate(kind, size, i)
            g = replay.read_csv(replay.to_csv(g, replay.GNSS_COLUMNS + replay.REF_COLUMNS), replay.GNSS_COLUMNS)
            o = replay.read_csv(replay.to_csv(o, replay.ODO_COLUMNS), replay.ODO_COLUMNS)
            res.append(replay.score_log(g, o, cfg))
        pre = [r["t_alarm"] is not None and (kind == "nominal" or r["t_alarm"] < ONSET) for r in res]
        delays = [r["t_alarm"] - ONSET if r["t_alarm"] is not None and r["t_alarm"] >= ONSET else None for r in res]
        conds[f"H|{cond}"] = {
            "method": "H", "fault": kind, "size": size, "false_alarm": common.rate(pre),
            "detected": common.rate([d is not None for d in delays]) if kind != "nominal" else None,
            "detected_within_t_n": common.rate([d is not None and d <= A.T_N for d in delays]) if kind != "nominal" else None,
            "detection_delay": common.mean_ci(delays), "error_at_alarm": common.mean_ci([r["error_at_alarm_m"] for r in res])}
    return {"conditions": conds}


def verdicts(n4: dict) -> dict:
    out = {}
    for e in _n4_items():
        r = score.evaluate(e, {"n4r2": n4})
        out[e["id"]] = {"held": r["held"], "verdict": r["verdict"], "text": e["text"]}
    return out


def compare(ours: dict, theirs: dict) -> dict:
    """Verdicts side by side, and per condition the measures that decide them."""
    vo, vt = verdicts(ours), verdicts(theirs)
    rows = [{"id": i, "ours_held": vo[i]["held"], "theirs_held": vt[i]["held"], "same": vo[i]["held"] == vt[i]["held"]} for i in vo]
    conds = []
    for k, o in ours["conditions"].items():
        t = theirs["conditions"][k]
        conds.append({"condition": k.split("|", 1)[1],
                      "ours_detected_within_t_n": (o["detected_within_t_n"] or {}).get("rate"), "theirs_detected_within_t_n": (t["detected_within_t_n"] or {}).get("rate"),
                      "ours_false_alarm": o["false_alarm"]["rate"], "theirs_false_alarm": t["false_alarm"]["rate"],
                      "ours_mean_delay_s": o["detection_delay"]["mean"], "theirs_mean_delay_s": t["detection_delay"]["mean"],
                      "ours_max_error_at_alarm_m": o["error_at_alarm"]["max"], "theirs_max_error_at_alarm_m": t["error_at_alarm"]["max"]})
    return {"verdicts": rows, "different": [r["id"] for r in rows if not r["same"]], "conditions": conds}
