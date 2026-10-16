"""Build the evidence bundles that the assurance case cites (sim/results/EV-08.json and EV-12.json).

A bundle collects, for one evidence item, the result files it rests on (with their SHA-256), the
acceptance criteria and predictions that bear on it, the restrictions and the faults not covered.
It adds no new numbers: every value is copied from sim/results/*.json.
Usage: python -m sim.evidence
"""
from __future__ import annotations

import sys

from sim import acceptance, common, score

ITEMS = {
    "EV-08": {"goal": "G4", "title": "Planning and navigation safety, minimum risk behaviour",
              "results": ["gnss"], "protocol_items": ["N2", "N3", "N4 (synthetic replay only)"],
              "acceptance": ["AC-N1", "AC-N2"], "prefix": "N-"},
    "EV-12": {"goal": "G6", "title": "Building condition evidence (heat, dust, glare)",
              "results": ["du3", "gl3"], "protocol_items": ["DU3", "DU5 (software monitor only)", "GL3", "GL5 (software response only)"],
              "acceptance": ["AC-DU1", "AC-DU2", "AC-GL1", "AC-GL2"], "prefix": ("DU3-", "GL3-")},
}
NOT_SHOWN = [
    "Nothing about a real robot, sensor, receiver or building: the worlds are software models written by the same authors as the methods.",
    "No heat evidence (H1 to H6) and no hardware dust or glare test (DU4, GL2) was run.",
    "No RF level GNSS evidence; fault models are measurement level only and are not checked against real interference.",
    "The stopping model, sensor models and thresholds are proposal values, not measured values.",
]


def restrictions(gl3: dict) -> list[dict]:
    """AC-GL3: every sun condition where M misses P_G becomes a restriction."""
    out = []
    for key, c in sorted(gl3["conditions"].items()):
        if c["method"] == "M" and c["detected_in_time"]["rate"] < acceptance.P_G:
            out.append({"condition": key.split("|", 1)[1], "detected_in_time_rate": c["detected_in_time"]["rate"],
                        "saturation_model": c["saturation_model"]})
    return out


def not_covered(gnss: dict) -> list[dict]:
    """AC-N3: faults below E_N, with the method's detection rate and missed seeds."""
    out = []
    for key, c in sorted(gnss["conditions"].items()):
        if c["method"] != "M" or c["fault"] in ("nominal", "loss"): continue
        if c["size"] < acceptance.E_N[c["fault"]]:
            out.append({"fault": key.split("|", 1)[1], "detected_rate": c["detected"]["rate"],
                        "detected_within_t_n_rate": c["detected_within_t_n"]["rate"], "missed_seeds": c["missed_seeds"]})
    return out


def bundle(item: str, results: dict, scored: dict) -> dict:
    spec = ITEMS[item]
    pfx = spec["prefix"] if isinstance(spec["prefix"], tuple) else (spec["prefix"],)
    b = {"label": common.LABEL, "evidence_kind": common.EVIDENCE_KIND, "evidence_item": item, "goal": spec["goal"],
         "title": spec["title"], "status_supported": "partial", "closes_hardware_claim": False,
         "protocol_items": spec["protocol_items"], "prereg_sha256": scored["prereg_sha256"],
         "result_files": {f"sim/results/{r}.json": common.file_sha256(f"sim/results/{r}.json") for r in spec["results"]},
         "acceptance": [{"id": a["id"], "text": a["text"], "held": a["held"],
                         "failing": [m for c in a["checks"] for m in c["failing"]]}
                        for a in scored["acceptance"] if a["id"] in spec["acceptance"]],
         "predictions": [{"id": p["id"], "verdict": p["verdict"]} for p in scored["predictions"] if p["id"].startswith(pfx)],
         "what_this_does_not_show": NOT_SHOWN}
    if "gl3" in spec["results"]: b["restrictions_ac_gl3"] = restrictions(results["gl3"])
    if "gnss" in spec["results"]: b["not_covered_ac_n3"] = not_covered(results["gnss"])
    return b


def build() -> dict:
    results = score.load_results()
    scored = score.score(results)
    return {item: bundle(item, results, scored) for item in ITEMS}


def main() -> int:
    for item, b in build().items(): print("wrote", common.write_result(f"{item}.json", b))
    return 0


if __name__ == "__main__":
    sys.exit(main())
