"""Score round 2 predictions and acceptance criteria with the round 1 scoring functions."""
from __future__ import annotations

import json, os

from sim import common, score
from sim.r2 import base
from sim.r2.predictions_r2 import ACCEPTANCE, PREDICTIONS

FILES = ("design_gl3", "design_du3", "gl3r2", "du3r2", "heat", "n4r2")


def load(d: str = base.RESULTS) -> dict:
    return {n: json.load(open(os.path.join(d, n + ".json"), encoding="utf-8")) for n in FILES}


def score_r2(results: dict) -> dict:
    preds = [score.evaluate(p, results) for p in PREDICTIONS]
    acs = [score.evaluate(a, results) for a in ACCEPTANCE]
    return {"label": common.LABEL, "evidence_kind": common.EVIDENCE_KIND, "round": 2, "prereg_sha256": base.prereg_sha(),
            "predictions": preds, "acceptance": acs,
            "totals": {"predictions": len(preds), "hit": sum(p["verdict"] == "HIT" for p in preds),
                       "miss": sum(p["verdict"] == "MISS" for p in preds),
                       "acceptance_held": sum(a["held"] is True for a in acs),
                       "acceptance_failed": sum(a["held"] is False for a in acs)}}
