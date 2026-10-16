"""Score predictions and acceptance criteria against sim/results/*.json and write sim/results/scored.json."""
from __future__ import annotations

import json, os

from sim import common
from sim.predictions import ACCEPTANCE, PREDICTIONS

OPS = {
    "all<=": lambda x, v: x <= v + 1e-12,
    "all>=": lambda x, v: x >= v - 1e-12,
    "between": lambda x, v: v[0] - 1e-12 <= x <= v[1] + 1e-12,
}


def lookup(results: dict, path: str):
    f, keys = path.split(":", 1)
    node = results[f]
    for k in keys.split("/"):
        if node is None: return None
        node = node[k]
    return node


def evaluate(entry: dict, results: dict) -> dict:
    checks, ok_all, applicable = [], True, 0
    for c in entry["checks"]:
        vals = []
        for m in c["metrics"]:
            x = lookup(results, m)
            ok = None if x is None else OPS[c["op"]](x, c["value"])
            vals.append({"metric": m, "value": x, "pass": ok})
            if ok is not None:
                applicable += 1; ok_all = ok_all and ok
        checks.append({"op": c["op"], "value": c["value"], "values": vals,
                       "failing": [v["metric"] for v in vals if v["pass"] is False]})
    held = ok_all if applicable else None
    return {"id": entry["id"], "text": entry["text"], "held": held, "expected_to_hold": entry["expect"],
            "verdict": None if held is None else ("HIT" if held == entry["expect"] else "MISS"), "checks": checks}


def score(results: dict) -> dict:
    preds = [evaluate(p, results) for p in PREDICTIONS]
    acs = [evaluate(a, results) for a in ACCEPTANCE]
    return {"label": common.LABEL, "evidence_kind": common.EVIDENCE_KIND,
            "prereg_sha256": results["du3"].get("prereg_sha256"),
            "predictions": preds, "acceptance": acs,
            "totals": {"predictions": len(preds), "hit": sum(p["verdict"] == "HIT" for p in preds),
                       "miss": sum(p["verdict"] == "MISS" for p in preds),
                       "acceptance_held": sum(a["held"] is True for a in acs),
                       "acceptance_failed": sum(a["held"] is False for a in acs)}}


def load_results(d: str = common.RESULTS) -> dict:
    return {n: json.load(open(os.path.join(d, n + ".json"), encoding="utf-8")) for n in ("du3", "gl3", "gnss")}
