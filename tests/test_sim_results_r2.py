"""Committed round 2 results must be labelled, tied to the round 2 preregistration and reproducible from code."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sim import common
from sim.r2 import base, du3_r2, evidence_r2, gl3_r2, heat, n4_r2, score_r2

ROOT = os.path.join(os.path.dirname(__file__), "..")
RES = score_r2.load()


def prereg_hash():
    for line in open(os.path.join(ROOT, "sim/PREREGISTRATION_R2.sha256.txt"), encoding="utf-8"):
        if line.rstrip().endswith("sim/PREREGISTRATION_R2.md"): return line.split()[0]


def test_round2_files_labelled_and_tied_to_prereg():
    for name in list(score_r2.FILES) + ["scored_r2", "EV-19", "EV-20", "EV-21"]:
        r = json.load(open(os.path.join(base.RESULTS, name + ".json"), encoding="utf-8"))
        assert r["label"] == common.LABEL and r["evidence_kind"] == "simulated" and r["prereg_sha256"] == prereg_hash(), name


def test_design_used_development_seeds_and_scoring_held_out_seeds():
    for n in ("design_gl3", "design_du3"): assert RES[n]["seed_set"] == "development" and RES[n]["seed_base"] == base.DEV_SEED
    for n in ("gl3r2", "du3r2", "heat", "n4r2"): assert RES[n]["seed_set"] == "held out" and RES[n]["seed_base"] == base.HELDOUT_SEED


def test_scoring_uses_the_committed_design():
    assert RES["gl3r2"]["config"]["chosen"] == RES["design_gl3"]["chosen"]
    assert RES["du3r2"]["config"]["chosen"] == RES["design_du3"]["chosen"]


def subset(stored, fresh):
    for k, v in fresh["conditions"].items(): assert common.dump(v) == common.dump(stored["conditions"][k]), k


def test_heat_reproducible_subset(monkeypatch):
    monkeypatch.setattr(heat, "PEAKS", (45,)); monkeypatch.setattr(heat, "SUN", ("sun",))
    subset(RES["heat"], heat.score())


def test_gl3_reproducible_subset(monkeypatch):
    monkeypatch.setattr(gl3_r2, "CONDS", [(5, 30, 0.5)])
    subset(RES["gl3r2"], gl3_r2.score(RES["design_gl3"]["chosen"]))


def test_n4_reproducible_subset(monkeypatch):
    from sim import gnss_n2n4 as G
    monkeypatch.setattr(G, "CONDITIONS", [("nominal", 0.0), ("noise", 5.0), ("drift", 0.05)])
    subset(RES["n4r2"], n4_r2.score())


def test_scored_and_bundles_are_current():
    stored = json.load(open(os.path.join(base.RESULTS, "scored_r2.json"), encoding="utf-8"))
    assert common.dump(score_r2.score_r2(RES)) == common.dump(stored)
    for item, b in evidence_r2.build().items():
        assert common.dump(b) == common.dump(json.load(open(os.path.join(base.RESULTS, item + ".json"), encoding="utf-8"))), item


def test_every_round2_prediction_metric_exists():
    from sim.r2.predictions_r2 import ACCEPTANCE, PREDICTIONS
    for e in PREDICTIONS + ACCEPTANCE:
        for c in e["checks"]:
            for m in c["metrics"]:
                f, keys = m.split(":", 1); node = RES[f]
                for k in keys.split("/"):
                    if node is None: break
                    assert k in node, m
                    node = node[k]
