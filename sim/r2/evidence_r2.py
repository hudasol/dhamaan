"""Evidence bundles for the round 2 items cited by the assurance case (sim/results_r2/EV-19.json to EV-21.json).

Every value is copied from sim/results_r2/*.json; nothing new is computed. Usage: python -m sim.r2.evidence_r2
"""
from __future__ import annotations

import sys

from sim import common
from sim.r2 import base, score_r2

ITEMS = {
    "EV-19": {"goal": "G6", "title": "Round 2 dust and glare monitor evidence", "results": ["design_gl3", "gl3r2", "design_du3", "du3r2"],
              "items": ["DU3", "GL3"], "acceptance": ["AC-GL2R2", "AC-GL4R2", "AC-GL1R2", "AC-DU1R2", "AC-DU2R2"], "prefix": ("GL3R2-", "DU3R2-")},
    "EV-20": {"goal": "G6", "title": "Heat derating evidence (H1 to H6)", "results": ["heat"],
              "items": ["H1", "H2", "H3", "H4", "H5", "H6"], "acceptance": ["AC-H1", "AC-H2", "AC-H3"], "prefix": ("H-",)},
    "EV-21": {"goal": "G4", "title": "GNSS log replay harness (synthetic stand in logs)", "results": ["n4r2"],
              "items": ["N4"], "acceptance": ["AC-N1R2", "AC-N2R2"], "prefix": ("N4-",)},
}
NOT_SHOWN = [
    "Nothing about a real robot, sensor, receiver or building: worlds and methods share an author.",
    "Heat parameters are assumed, proposal values; no component was measured.",
    "The replay harness ran on synthetic stand in logs only; no public or field log was replayed.",
    "No RF level GNSS evidence; faults are injected into the position stream only.",
]


def bundle(item: str, results: dict, scored: dict) -> dict:
    spec = ITEMS[item]
    return {"label": common.LABEL, "evidence_kind": common.EVIDENCE_KIND, "round": 2, "evidence_item": item,
            "goal": spec["goal"], "title": spec["title"], "status_supported": "partial", "closes_hardware_claim": False,
            "protocol_items": spec["items"], "prereg_sha256": scored["prereg_sha256"],
            "result_files": {f"sim/results_r2/{r}.json": common.file_sha256(f"sim/results_r2/{r}.json") for r in spec["results"]},
            "acceptance": [{"id": a["id"], "text": a["text"], "held": a["held"], "failing": [m for c in a["checks"] for m in c["failing"]]}
                           for a in scored["acceptance"] if a["id"] in spec["acceptance"]],
            "predictions": [{"id": p["id"], "verdict": p["verdict"]} for p in scored["predictions"] if p["id"].startswith(spec["prefix"])],
            "what_this_does_not_show": NOT_SHOWN}


def build() -> dict:
    results = score_r2.load()
    scored = score_r2.score_r2(results)
    return {item: bundle(item, results, scored) for item in ITEMS}


def main() -> int:
    for item, b in build().items(): print("wrote", base.write(f"{item}.json", b))
    return 0


if __name__ == "__main__":
    sys.exit(main())
