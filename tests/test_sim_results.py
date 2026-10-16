"""Committed simulation results must be labelled, tied to the preregistration and reproducible from code."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sim import common, du3_lidar, gl3_glare, gnss_n2n4, score

ROOT = os.path.join(os.path.dirname(__file__), "..")
RES = score.load_results()


def prereg_hash():
    for line in open(os.path.join(ROOT, "sim/PREREGISTRATION.sha256.txt"), encoding="utf-8"):
        if line.rstrip().endswith("sim/PREREGISTRATION.md"): return line.split()[0]


def test_results_labelled_and_tied_to_prereg():
    for name in ("du3", "gl3", "gnss", "scored"):
        r = json.load(open(os.path.join(ROOT, "sim/results", name + ".json"), encoding="utf-8"))
        assert r["label"] == common.LABEL and r["evidence_kind"] == "simulated"
        assert r["prereg_sha256"] == prereg_hash()


def test_at_least_30_seeds_per_condition():
    for name in ("du3", "gl3", "gnss"):
        assert RES[name]["seeds_per_condition"] >= 30
        for c in RES[name]["conditions"].values():
            r = c.get("unsafe") or c.get("false_alarm")
            assert r["n"] >= 30


def subset_matches(stored, fresh):
    for k, v in fresh["conditions"].items():
        assert common.dump(v) == common.dump(stored["conditions"][k]), k


def test_du3_reproducible_subset():
    subset_matches(RES["du3"], du3_lidar.run(levels=[0.3]))


def test_gl3_reproducible_subset():
    subset_matches(RES["gl3"], gl3_glare.run(elevations=(5,), azimuths=(30,), rhos=(0.5,)))


def test_gnss_reproducible_subset():
    subset_matches(RES["gnss"], gnss_n2n4.run(conditions=[("nominal", 0.0), ("jump", 2.0)]))


def test_scored_file_is_current():
    stored = json.load(open(os.path.join(ROOT, "sim/results/scored.json"), encoding="utf-8"))
    assert common.dump(score.score(RES)) == common.dump(stored)


def test_every_prediction_metric_exists():
    from sim.predictions import ACCEPTANCE, PREDICTIONS
    for e in PREDICTIONS + ACCEPTANCE:
        for c in e["checks"]:
            for m in c["metrics"]:
                f, keys = m.split(":", 1)
                node = RES[f]
                for k in keys.split("/"):
                    if node is None: break
                    assert k in node, m
                    node = node[k]
