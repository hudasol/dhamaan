"""Development tests for the simulation harness. They use a separate base seed (not the evaluation
seeds) and assert only structure, labels and determinism, never outcome values."""
import os, sys
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sim import common, du3_lidar, gl3_glare, gnss_n2n4, score

DEV_SEED = 999


@pytest.fixture(autouse=True)
def dev_seed(monkeypatch):
    monkeypatch.setattr(common, "BASE_SEED", DEV_SEED)


def small():
    return {"du3": du3_lidar.run(seeds=2, levels=[0.0, 1.0]),
            "gl3": gl3_glare.run(seeds=2, elevations=(5,), azimuths=(0,), rhos=(0.0,)),
            "gnss": gnss_n2n4.run(seeds=2, conditions=[("nominal", 0.0), ("jump", 5.0), ("replay", 5.0), ("loss", 0.0)])}


def test_same_seed_same_output():
    a, b = small(), small()
    assert {k: common.dump(v) for k, v in a.items()} == {k: common.dump(v) for k, v in b.items()}


def test_every_output_is_labelled_synthetic():
    for r in small().values():
        assert r["label"].startswith("SYNTHETIC") and r["evidence_kind"] == "simulated"


def test_seed_changes_world():
    r1 = common.rng_for("X", "c", 0).random(); r2 = common.rng_for("X", "c", 1).random()
    assert r1 != r2


def test_methods_share_the_world():
    # common random numbers: the generator is keyed without the method, so in a clean world (no degradation,
    # where the monitor cannot act) the detector alone and the method see the same scans and agree exactly.
    import inspect
    assert list(inspect.signature(common.rng_for).parameters) == ["experiment", "condition", "seed_index"]
    cfg, stop = du3_lidar.Config(), common.Stopping()
    for i in range(3):
        a = du3_lidar.run_one(cfg, 0.0, "B0", common.rng_for("DU3", "k=0.0", i), stop)
        b = du3_lidar.run_one(cfg, 0.0, "M", common.rng_for("DU3", "k=0.0", i), stop)
        assert a == b


def test_saturation_is_bounded():
    cfg = gl3_glare.Config()
    for e in gl3_glare.ELEVATIONS:
        for a in gl3_glare.AZIMUTHS:
            for r in gl3_glare.RHOS:
                assert 0.0 <= gl3_glare.saturation(cfg, e, a, r) <= 1.0


def test_stopping_distance_grows_with_speed():
    s = common.Stopping()
    assert s.required(0.3) < s.required(0.8)


def test_score_ops_and_not_applicable():
    res = {"f": {"a": {"x": 0.5, "y": None}}}
    e = score.evaluate({"id": "T", "text": "", "expect": True,
                        "checks": [{"metrics": ["f:a/x", "f:a/y"], "op": "all<=", "value": 0.6}]}, res)
    assert e["held"] is True and e["verdict"] == "HIT"
    e = score.evaluate({"id": "T", "text": "", "expect": True,
                        "checks": [{"metrics": ["f:a/y"], "op": "all<=", "value": 0.6}]}, res)
    assert e["held"] is None and e["verdict"] is None
