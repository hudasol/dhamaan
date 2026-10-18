"""Development tests for round 2. They patch both seed sets to a separate test seed and assert structure,
labels, determinism and the log format only, never outcome values."""
import os, sys
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sim import common, gnss_n2n4 as G
from sim.r2 import base, du3_r2, gl3_r2, heat, n4_r2, replay


@pytest.fixture(autouse=True)
def test_seeds(monkeypatch):
    monkeypatch.setattr(base, "DEV_SEED", 4242)
    monkeypatch.setattr(base, "HELDOUT_SEED", 4243)


def test_design_and_scoring_use_separate_seed_sets():
    src = open(os.path.join(os.path.dirname(__file__), "..", "sim", "r2", "base.py"), encoding="utf-8").read()
    dev = int(src.split("DEV_SEED = ")[1].split()[0]); held = int(src.split("HELDOUT_SEED = ")[1].split()[0])
    assert dev != held
    for mod in (gl3_r2, du3_r2):
        code = open(mod.__file__, encoding="utf-8").read()
        design_src = code[code.index("def design"):code.index("def score")]
        assert "HELDOUT_SEED" not in design_src and "DEV_SEED" in design_src


def test_gl3_design_and_score_structure_and_determinism():
    d1, d2 = gl3_r2.design(seeds=2), gl3_r2.design(seeds=2)
    assert common.dump(d1) == common.dump(d2) and set(d1["chosen"]) == {"margin", "frames", "feasible"}
    r = gl3_r2.score(d1["chosen"], seeds=2)
    assert r["label"] == common.LABEL and r["evidence_kind"] == "simulated" and r["seed_set"] == "held out"
    assert {c["method"] for c in r["conditions"].values()} == {"M", "M2"}


def test_du3_monitor_stop_reads_the_recorded_run():
    run = {"vrr": [0.9, 0.5, 0.5, 0.5, 0.9], "t": [0.0, 0.1, 0.2, 0.3, 0.4]}
    assert du3_r2.monitor_stop(run, 0.6, 3) == 0.3
    assert du3_r2.monitor_stop(run, 0.6, 4) is None


def test_du3_design_structure():
    d = du3_r2.design(seeds=1)
    assert set(d["chosen"]) == {"threshold", "scans", "bound", "feasible", "dev_violations"}


def test_heat_model_basics():
    p = heat.draw(base.rng(base.HELDOUT_SEED, "HEAT", "t", 0))
    r = heat.run_one(45, "sun", "normal", "M", p)
    assert 0.0 <= r["productivity"] <= 1.0 and set(r["tmax"]) == set(heat.COMPONENTS)
    assert heat.run_one(45, "sun", "normal", "B1", p)["productivity"] == 0.0     # fixed rule parks at 45 degC
    assert heat.required_factor(25.0) == 1.0


def test_heat_parameters_are_labelled_assumed():
    assert set(heat.ASSUMED_NOTE.values()) <= {base.ASSUMED, "dhill README, cited by link"}


def test_log_round_trip_and_format_errors():
    g, o = replay.standin(base.rng(base.DEV_SEED, "N4LOG", "t", 0))
    gt = replay.to_csv(g, replay.GNSS_COLUMNS + replay.REF_COLUMNS)
    assert replay.read_csv(gt, replay.GNSS_COLUMNS)[3]["x_ref_m"] == pytest.approx(g[3]["x_ref_m"], abs=1e-6)
    with pytest.raises(replay.LogError): replay.read_csv("t_s,x_m\n0,1\n", replay.GNSS_COLUMNS)
    with pytest.raises(replay.LogError): replay.read_csv("t_s,v_mps,yaw_rad\n1,0,0\n0,0,0\n", replay.ODO_COLUMNS)
    with pytest.raises(replay.LogError): replay.read_csv("t_s,v_mps,yaw_rad\n", replay.ODO_COLUMNS)


def test_injected_loss_marks_fixes_without_a_position_change():
    g, _ = replay.standin(base.rng(base.DEV_SEED, "N4LOG", "t", 0))
    lost = replay.inject(g, "loss", 0.0, 30.0, base.rng(base.DEV_SEED, "x", "y", 0))
    assert all(f["fix_ok"] == 0.0 for f in lost if f["t_s"] >= 30.0) and lost[0] == g[0]


def test_n4_score_structure():
    r = n4_r2.score(seeds=2)
    assert {c["fault"] for c in r["conditions"].values()} == {k for k, _ in G.CONDITIONS}


def test_every_fault_kind_changes_the_fix_stream():
    g, _ = replay.standin(base.rng(base.DEV_SEED, "N4LOG", "t", 0))
    for kind, size in [k for k in G.CONDITIONS if k[0] != "nominal"]:
        out = replay.inject(g, kind, size, 30.0, base.rng(base.DEV_SEED, "x", kind, 0))
        assert any(a != b for a, b in zip(out, g) if a["t_s"] >= 40.0), kind
