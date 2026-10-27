"""Recorded arm of round three: loader, detectors, scoring and runner, on SYNTHETIC folders made inside the tests.
No recording is read here and nothing in this file is a result."""
import csv, json, math, os

import numpy as np
import pytest

from sim.r3 import detectors as D, jammertest as J, real_score as S, run_real

LAT0, LON0 = 69.2124, 15.8583


def _write_recording(root, name, kind="spoofing", seed=0, duration=900, session=(300, 560), local_offset_h=2, sigma=0.8):
    """A parked receiver. spoofing: 40 m position jump with no velocity change; jamming: no fix for 40 s; meaconing: nothing visible."""
    rng = np.random.default_rng(seed); d = os.path.join(root, name); os.makedirs(d)
    from datetime import datetime, timedelta
    t0 = datetime(2024, 9, 12, 8, 0, 0)
    with open(os.path.join(d, "nav_pvt.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["real_time", "fixType", "numSV", "lat", "lon", "velN", "velE", "gSpeed", "hAcc"])
        for i in range(duration):
            t = i; fix, sv = 3, 30; dn, de = rng.normal(0, sigma, 2)
            if kind == "spoofing" and t >= session[0] + 20: dn += 40.0
            if kind == "jamming" and session[0] + 30 <= t < session[0] + 70: fix, sv = 0, 0
            lat = LAT0 + dn / 111320.0; lon = LON0 + de / (111320.0 * math.cos(math.radians(LAT0)))
            w.writerow([(t0 + timedelta(seconds=i)).strftime("%Y-%m-%d %H:%M:%S.000000"), fix, sv, lat / 1e7, lon / 1e7, 0.0, 0.0, 0.01, 0.3 if fix == 3 else 1500.0])
    with open(os.path.join(d, "mon_rf.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["real_time", "jamInd_01", "jamInd_02"])
        for i in range(duration):
            jam = 200 if (kind == "jamming" and session[0] + 30 <= i < session[0] + 70) else int(rng.integers(0, 10))
            w.writerow([(t0 + timedelta(seconds=i)).strftime("%Y-%m-%d %H:%M:%S.000000"), jam, 3])
    loc = lambda s: (t0 + timedelta(seconds=s, hours=local_offset_h)).strftime("%Y-%m-%dT%H:%M:%SZ")
    json.dump({"scenario_id": name, "attack_type": {"spoofing": "Spoofing", "jamming": "Jamming", "meaconing": "Meaconing"}[kind],
               "attack_parameters": {"rover_states": "stationary"},
               "attack_log": [{"timestamp_utc": loc(session[0]), "event": "Initial jamming started"}, {"timestamp_utc": loc(session[1]), "event": "Initial jamming ended"}]},
              open(os.path.join(d, "scenario.json"), "w"))


@pytest.fixture
def one(tmp_path):
    _write_recording(str(tmp_path), "r0", "spoofing")
    return str(tmp_path)


def test_loader_scales_positions_and_shifts_local_time(one):
    rec = J.load(one, "r0")
    assert rec["attack_type"] == "spoofing" and rec["window_error"] is None
    assert rec["session"] == (300.0, 560.0)                                    # local time minus two hours
    xs = [f["x_m"] for f in rec["fixes"][:200]]
    assert abs(np.std(xs) - 0.8) < 0.25 and abs(np.mean(xs)) < 0.5            # metres, not degrees
    seg = J.segments(rec)
    assert seg["leading"] == (0.0, 180.0) and seg["trailing"] == (680.0, 899.0) and seg["session_run"] == (180.0, 560.0)


def test_unpaired_attack_log_excludes_the_recording(tmp_path):
    _write_recording(str(tmp_path), "r0")
    p = os.path.join(str(tmp_path), "r0", "scenario.json"); sc = json.load(open(p)); sc["attack_log"].pop()
    json.dump(sc, open(p, "w"))
    rec = J.load(str(tmp_path), "r0")
    assert rec["session"] is None and "pair" in rec["window_error"] and J.segments(rec)["session_run"] is None


def test_denial_events_need_a_run_inside_the_session(tmp_path):
    _write_recording(str(tmp_path), "j", "jamming")
    rec = J.load(str(tmp_path), "j")
    assert J.denial_events(rec) == [330.0]
    assert all(f["fix_ok"] == 1.0 for f in rec["fixes"][:300])


def test_odometry_substitute_is_a_held_velocity_at_ten_hertz(one):
    rec = J.load(one, "r0"); odo = J.odometry(rec["fixes"], 10.0, 12.0)
    assert len(odo) == 21 and abs(odo[1]["t_s"] - odo[0]["t_s"] - 0.1) < 1e-9 and all(o["v_mps"] < 0.2 for o in odo)


def test_nominal_error_rows_need_a_still_receiver_and_enough_epochs(one):
    rec = J.load(one, "r0"); rows = J.nominal_error_rows(rec)
    assert rows and len(rows) >= 150 and abs(np.median([r["x_m"] - r["x_ref_m"] for r in rows])) < 0.2
    rec["fixes"] = [dict(f, speed=2.0) for f in rec["fixes"]]
    assert J.nominal_error_rows(rec) is None


def test_every_detector_is_quiet_on_nominal_noise_and_finds_a_jump(one):
    rec = J.load(one, "r0"); fx, rf = rec["fixes"], rec["rf"]; params = {"jam_threshold": 50.0}
    for n in ("D-RX", "D-JUMP", "D-NIS", "M", "D-JAM"):
        assert D.run_episodes(n, fx, rf, 0.0, 280.0, params) == [], n          # nominal part, before the jump
    for n in ("D-JUMP", "D-NIS", "M"):
        al = D.run_episodes(n, fx, rf, 180.0, 560.0, params)
        assert al and 320.0 <= al[0] <= 330.0, (n, al)                         # jump at 320 s
    assert D.run_episodes("D-RX", fx, rf, 180.0, 560.0, params) == []          # the receiver reports a healthy fix throughout
    assert D.run_episodes("D-JAM", fx, rf, 180.0, 560.0, params) == []


def test_denial_is_seen_by_the_receiver_flags_the_timeout_and_the_rf_indicator(tmp_path):
    _write_recording(str(tmp_path), "j", "jamming"); rec = J.load(str(tmp_path), "j"); fx, rf = rec["fixes"], rec["rf"]
    rx = D.run_episodes("D-RX", fx, rf, 180.0, 560.0)
    m = D.run_episodes("M", fx, rf, 180.0, 560.0)
    jam = D.run_episodes("D-JAM", fx, rf, 180.0, 560.0, {"jam_threshold": 50.0})
    assert rx[0] == 330.0 and 330.0 <= m[0] <= 335.0 and 330.0 <= jam[0] <= 334.0


def test_restart_gives_several_alarms_spaced_by_the_rearm_time(tmp_path):
    _write_recording(str(tmp_path), "j", "jamming"); rec = J.load(str(tmp_path), "j")
    al = D.run_episodes("D-RX", rec["fixes"], rec["rf"], 180.0, 560.0)
    assert len(al) >= 2 and all(b - a >= D.REARM_S for a, b in zip(al, al[1:]))   # 40 s of denial gives alarms at 330 and 360


def test_poisson_interval_matches_known_values():
    lo, hi = S.poisson_ci(0, 1.0)
    assert lo == 0.0 and abs(hi - 3.689) < 0.01
    lo, hi = S.poisson_ci(10, 2.0)
    assert abs(lo * 2 - 4.795) < 0.01 and abs(hi * 2 - 18.39) < 0.02
    assert S.poisson_ci(3, 0.0) == [None, None]


def _scores(tmp_path, kinds, names=("M", "D-RX")):
    for i, k in enumerate(kinds): _write_recording(str(tmp_path), f"r{i}", k, seed=i)
    recs = [J.load(str(tmp_path), f"r{i}") for i in range(len(kinds))]
    return recs, [S.record_scores(r, {"jam_threshold": 50.0}, names) for r in recs]


def test_scoring_counts_exposure_alarms_sessions_and_events(tmp_path):
    recs, sc = _scores(tmp_path, ["spoofing", "jamming", "meaconing"])
    g = S.aggregate(sc, "M")
    assert g["sessions"] == 3 and g["false_alarms"]["alarms"] == 0
    assert abs(g["false_alarms"]["exposure_hours"] - 3 * (180.0 + 219.0) / 3600.0) < 1e-6
    assert g["session_detection"]["spoofing"]["k"] == 1 and g["session_detection"]["meaconing"]["k"] == 0
    assert g["session_detection"]["all"]["k"] == 2 and g["session_detection"]["all"]["n"] == 3
    assert g["loss_of_fix_events"]["n"] == 1 and g["loss_of_fix_events"]["k"] == 1
    assert g["verdicts"]["AC-N4"] is True and g["verdicts"]["AC-N1r"] is False        # the meaconing session was missed
    assert g["verdicts"]["AC-N2r"].startswith("not evaluable")
    rx = S.aggregate(sc, "D-RX")
    assert rx["session_detection"]["spoofing"]["k"] == 0 and rx["session_detection"]["jamming"]["k"] == 1


def test_false_alarms_in_the_nominal_part_are_counted_per_hour(tmp_path):
    _write_recording(str(tmp_path), "r0", "spoofing", session=(300, 560))
    rec = J.load(str(tmp_path), "r0")
    for f in rec["fixes"][50:60]: f["fix_ok"] = 0.0                      # a nominal outage of 10 epochs
    g = S.aggregate([S.record_scores(rec, {"jam_threshold": 50.0}, ("D-RX",))], "D-RX")
    assert g["false_alarms"]["alarms"] >= 1 and g["false_alarms"]["per_hour"] > S.FA_LIMIT_PER_HOUR
    assert g["verdicts"]["AC-N4"] is False


def test_jam_threshold_comes_from_nominal_rows_only(tmp_path):
    recs, _ = _scores(tmp_path, ["jamming", "spoofing"], ("D-JAM",))
    thr = S.calibrate_jam_threshold(recs)
    assert thr <= 10 and thr < 200                                       # the 200 values sit inside the session


def test_synthetic_arms_run_through_the_unchanged_harness():
    a = S.synthetic_arm(None, n_logs=4)
    assert set(a["verdicts"]) == {"AC-N1", "AC-N4"} and a["logs"] == 4 and "nominal=0" in a["conditions"]


def test_runner_refuses_without_a_valid_freeze(tmp_path, monkeypatch):
    monkeypatch.setattr(run_real, "FREEZE", "data/r3_recorded/does_not_exist.json")
    with pytest.raises(SystemExit) as e: run_real.run(str(tmp_path))
    assert "freeze" in str(e.value)


def test_freeze_detects_a_changed_plan_or_code(tmp_path, monkeypatch):
    p = tmp_path / "freeze.json"
    rec = run_real.freeze_record(); p.write_text(json.dumps(rec))
    monkeypatch.setattr(run_real, "FREEZE", os.path.relpath(str(p), run_real.ROOT))
    assert run_real.verify_freeze() == []
    rec["plan_sha256"] = "0" * 64; p.write_text(json.dumps(rec))
    assert "analysis plan differs" in " ".join(run_real.verify_freeze())
    rec = run_real.freeze_record(); rec["code_sha256"]["sim/r3/detectors.py"] = "1" * 64; p.write_text(json.dumps(rec))
    assert "sim/r3/detectors.py" in " ".join(run_real.verify_freeze())


def test_committed_freeze_matches_the_committed_plan_and_code():
    if not os.path.exists(os.path.join(run_real.ROOT, run_real.FREEZE)): pytest.skip("not frozen yet")
    assert run_real.verify_freeze() == []


def test_end_to_end_on_a_synthetic_dataset(tmp_path, monkeypatch):
    data = tmp_path / "data"; data.mkdir()
    kinds = ["spoofing", "jamming", "meaconing"] * 5
    for i, k in enumerate(kinds): _write_recording(str(data), f"rec{i:02d}", k, seed=i)
    monkeypatch.setattr(run_real, "verify_freeze", lambda root=run_real.ROOT: [])
    monkeypatch.setattr(S, "synthetic_arm", lambda cal, n_logs=100: {"conditions": {}, "verdicts": {"AC-N1": False, "AC-N4": True},
                                                                      "false_alarms_per_hour": 0.0, "logs": 0})
    out = str(tmp_path / "out"); res = run_real.run(str(data), out)
    h = res["header"]
    assert h["evidence_kind"] == "recorded" and h["label"].startswith("RECORDED") and h["recordings"] == 15
    assert len(h["calibration"]) == 12 and len(h["held_out"]) == 3 and not set(h["calibration"]) & set(h["held_out"])
    for f in ("recorded_results.json", "synthetic_arms.json", "predictions.json", "detectors.csv"):
        assert os.path.exists(os.path.join(out, f)), f
    assert json.load(open(os.path.join(out, "synthetic_arms.json")))["label"].startswith("SYNTHETIC")
    assert set(res["R_all"]) == set(D.NAMES)
    assert set(res["predictions"]["held"]) == {f"R3-P{i}" for i in range(1, 10)}
