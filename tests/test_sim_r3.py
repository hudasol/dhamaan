"""Round 3 parts A and B: the register of assumed parameters, the mutant list and the informativeness analysis.
The analysis tests use SYNTHETIC outcomes made inside the test; they are not results."""
from sim.r3 import params, report, run_mutants


def test_parameters_are_read_from_the_code_and_cover_every_layer():
    ps = {p["id"]: p for p in params.list_parameters()}
    assert len(ps) >= 80
    for pid in ("du3.vrr_threshold", "gl3.p_clean", "gnss.cusum_limit", "acc.T_N", "acc2.T_H", "heat.LIDAR_BIAS", "heat.battery.limit_degc", "stopping.decel"):
        assert pid in ps, pid
    assert {p["kind"] for p in ps.values()} == {"model", "monitor", "acceptance"}


def test_every_exclusion_has_a_reason_and_is_not_swept():
    params.list_parameters()
    skipped = {s["id"]: s["reason"] for s in params.list_parameters.skipped}
    assert skipped and all(r for r in skipped.values())
    ids = {p["id"] for p in params.list_parameters()}
    assert not (ids & set(skipped))
    assert "gnss.t_onset" in skipped and "du3.t_onset" in skipped      # shifted by mutant M3 instead


def test_changed_values_are_valid():
    ps = {p["id"]: p for p in params.list_parameters()}
    assert params.changed_value(ps["gl3.p_clean"], 1.5) == 1.0                     # capped at 1
    assert params.changed_value(ps["gnss.reject_run"], 0.5) == 2                   # integers rounded half up
    assert params.changed_value(ps["du3.min_points"], 0.5) == 1                    # and never below 1
    assert abs(params.changed_value(ps["gnss.gate"], 0.5) - 6.91) < 1e-9
    e = params.changed_value(ps["acc.E_N"], 0.5)
    assert e["jump"] == 2.5 and e["loss"] == 0.0


def test_mutant_list_has_the_four_classes():
    specs = run_mutants.build_specs()
    classes = [s["class"] for s in specs]
    assert classes.count("orig") == 1 and classes.count("M0") == 1 and classes.count("M1") == 1 and classes.count("M3") == 1
    assert classes.count("M2") == 2 * len(params.list_parameters())
    assert len({s["id"] for s in specs}) == len(specs)


def _fixture():
    specs = [{"id": "ORIG", "class": "orig"}, {"id": "M0", "class": "M0"}, {"id": "M1", "class": "M1"},
             {"id": "M2|a.x|x0.5", "class": "M2", "param": "a.x", "kind": "model", "factor": 0.5, "value": 1},
             {"id": "M2|acc.T|x1.5", "class": "M2", "param": "acc.T", "kind": "acceptance", "factor": 1.5, "value": 2},
             {"id": "M3", "class": "M3"}]
    def res(p1, p2, a1):
        return {"round1": {"predictions": {"P1": [p1, True], "P2": [p2, True]}, "acceptance": {"A1": [None, a1]}}}
    outs = [{"id": "ORIG", "result": res("HIT", "HIT", True)}, {"id": "M0", "result": res("MISS", "HIT", True)},
            {"id": "M1", "result": res("HIT", "HIT", True)}, {"id": "M2|a.x|x0.5", "result": res("HIT", "HIT", False)},
            {"id": "M2|acc.T|x1.5", "result": res("HIT", "HIT", True)}, {"id": "M3", "result": res("HIT", "HIT", True)}]
    items = {("round1", "prediction", "P1"): {"round": "round1", "kind": "prediction", "id": "P1", "text": ""},
             ("round1", "prediction", "P2"): {"round": "round1", "kind": "prediction", "id": "P2", "text": ""},
             ("round1", "acceptance", "A1"): {"round": "round1", "kind": "acceptance", "id": "A1", "text": ""}}
    return specs, outs, items


def test_informative_means_the_verdict_changes_under_some_mutant():
    specs, outs, items = _fixture()
    a = report.analyse(specs, outs, items)
    rows = {r["id"]: r for r in a["rows"]}
    assert rows["P1"]["informative"] and rows["P1"]["M0"] and not rows["P1"]["M1"]
    assert not rows["P2"]["informative"]                                  # restates the model: nothing changes it
    s = a["summary"]
    assert s["predictions"] == 2 and s["informative"] == 1 and s["informative_hit"] == 1 and s["uninformative_ids"] == ["P2"]


def test_sensitivity_lists_only_flips():
    specs, outs, items = _fixture()
    flips = report.analyse(specs, outs, items)["sensitivity"]
    assert len(flips) == 1 and flips[0]["parameter"] == "a.x" and flips[0]["original_held"] is True and flips[0]["mutated_held"] is False


def test_failed_mutants_are_reported_not_hidden():
    specs, outs, items = _fixture()
    outs[3] = {"id": "M2|a.x|x0.5", "error": "ValueError: x"}
    a = report.analyse(specs, outs, items)
    assert a["summary"]["mutants_failed"] == ["M2|a.x|x0.5"]
    assert a["sensitivity"] == []


def test_independent_comparison_reproduces_round_2_when_given_our_own_generator():
    """Harness check on SYNTHETIC logs: our own generator, rebuilt as generate(kind, size, seed), must give the committed n4r2 conditions."""
    import json, os
    from sim import common, gnss_n2n4 as G
    from sim.r2 import base, replay
    from sim.r3 import indep
    cfg = G.Config()
    def ours(kind, size, seed):
        g, o = replay.standin(base.rng(base.HELDOUT_SEED, "N4LOG", "standin", seed), cfg)
        g = replay.read_csv(replay.to_csv(g, replay.GNSS_COLUMNS + replay.REF_COLUMNS), replay.GNSS_COLUMNS)
        gi = replay.inject(g, kind, size, cfg.t_onset, base.rng(base.HELDOUT_SEED, "N4R2", f"{kind}={size:g}", seed))
        return gi, o
    res = indep.results_for(ours)
    stored = json.load(open(os.path.join(common.ROOT, "sim", "results_r2", "n4r2.json"), encoding="utf-8"))
    for k, v in stored["conditions"].items():
        for field in ("false_alarm", "detected", "detected_within_t_n"):
            assert common.dump(res["conditions"][k][field]) == common.dump(v[field]), (k, field)
        for field in ("detection_delay", "error_at_alarm"):               # the log is written to CSV once more here, so allow rounding
            for stat in ("mean", "median", "max"):
                a, b = res["conditions"][k][field][stat], v[field][stat]
                assert (a is None and b is None) or abs(a - b) < 2e-3, (k, field, stat)
    cmp = indep.compare(res, res)
    assert cmp["different"] == [] and len(cmp["conditions"]) == 16 and len(cmp["verdicts"]) >= 6


# ---- Part C harness, SYNTHETIC fixtures only ----

def _fixture_logs(n, seed0=500, rho=0.0):
    import numpy as np
    from sim import gnss_n2n4 as G
    from sim.r2 import replay
    cfg = G.Config(); out = []
    for i in range(n):
        g, o = replay.standin(np.random.default_rng(seed0 + i), cfg)
        out.append((g, o))
    return out


def test_split_is_seeded_and_never_splits_a_recording():
    from sim.r3 import recorded
    ids = [f"rec{i:02d}" for i in range(10)]
    a = recorded.split_recordings(ids, 7, 4); b = recorded.split_recordings(list(reversed(ids)), 7, 4)
    assert a == b and len(a[0]) == 4 and len(a[1]) == 6 and not set(a[0]) & set(a[1]) and set(a[0]) | set(a[1]) == set(ids)
    assert recorded.split_recordings(ids, 8, 4) != a


def test_calibration_recovers_known_error_structure():
    import numpy as np
    from sim.r3 import recorded
    rng = np.random.default_rng(1); rows = []
    e = np.zeros(2)
    for t in range(4000):
        e = 0.7 * e + np.sqrt(1 - 0.49) * rng.standard_normal(2)
        rows.append({"t_s": float(t), "x_m": 2.0 * e[0], "y_m": 2.0 * e[1], "x_ref_m": 0.0, "y_ref_m": 0.0, "fix_ok": 1.0})
    cal = recorded.calibrate([(rows, [])])
    assert abs(cal["sigma_m"] - 2.0) < 0.1 and abs(cal["lag1_correlation"] - 0.7) < 0.05 and abs(cal["excess_kurtosis"]) < 0.3


def test_calibration_ignores_labelled_interference_rows():
    from sim.r3 import recorded
    rows = [{"t_s": float(t), "x_m": 1.0, "y_m": 1.0, "x_ref_m": 0.0, "y_ref_m": 0.0, "fix_ok": 1.0, "interference": 0.0} for t in range(10)]
    rows += [{"t_s": 10.0 + t, "x_m": 99.0, "y_m": 99.0, "x_ref_m": 0.0, "y_ref_m": 0.0, "fix_ok": 1.0, "interference": 1.0} for t in range(10)]
    assert len(recorded.nominal_errors(rows)) == 10


def test_recalibrated_standin_has_the_calibrated_correlation():
    import numpy as np
    from sim.r3 import recorded
    cal = {"sigma_m": 1.0, "lag1_correlation": 0.8, "excess_kurtosis": 0.0, "fixes_used": 1}
    g, o = recorded.s1_standin(np.random.default_rng(3), cal)
    got = recorded.calibrate([(g, o)])
    assert 0.55 < got["lag1_correlation"] < 0.95 and len(g) == 121 and len(o) == 1201


def test_measure_nominal_reports_exposure_and_faults_report_detection():
    import numpy as np
    from sim.r3 import recorded
    logs = _fixture_logs(6)
    f = lambda kind, size, i: np.random.default_rng(900 + i)
    nom = recorded.measure(logs, "nominal", 0.0, f)
    assert nom["exposure_hours"] > 0 and nom["false_alarms"] >= 0
    jump = recorded.measure(logs, "jump", 20.0, f)
    assert jump["detected_within_t_n"]["rate"] == 1.0 and jump["n"] == 6


def _arm(fa, delay, detect=1.0, err=1.0):
    conds = {k: {"detected_within_t_n": {"rate": detect}, "mean_delay_s": delay, "error_at_alarm_max_m": err} for k in recorded_covered()}
    conds["drift=0.2"] = {"detected_within_t_n": {"rate": detect}, "mean_delay_s": delay, "error_at_alarm_max_m": err}
    conds["nominal=0"] = {"false_alarms_per_hour": fa, "detected_within_t_n": None, "mean_delay_s": None, "error_at_alarm_max_m": None}
    return {"conditions": conds}


def recorded_covered():
    from sim.r3 import recorded
    return recorded.COVERED


def test_prediction_scoring_by_script_on_synthetic_arms():
    from sim.r3 import recorded
    res = {"fa_limit_per_hour": 1.0, "S0_held": _arm(0.1, 5.0), "S0_cal": _arm(0.1, 5.0), "R_cal": _arm(2.0, 9.0, detect=0.5),
           "R_held": _arm(2.0, 9.0, detect=0.5), "S1_held": _arm(2.0, 9.0, detect=0.5)}
    out = recorded.score_predictions(res)
    p = out["predictions_held"]
    assert p["R3-P1"] and p["R3-P2"] and p["R3-P3"] and p["R3-P4"] and p["R3-P5"] and p["R3-P6"]
    assert set(out["criteria_that_differ_between_S0_and_R"]) == {"AC-N1", "AC-N4"}
    res["S1_held"] = _arm(0.1, 5.0)                                          # recalibration does not help
    p = recorded.score_predictions(res)["predictions_held"]
    assert not p["R3-P4"] and not p["R3-P5"]


def test_runner_refuses_until_registration_and_licensed_data_exist(tmp_path):
    from sim.r3 import run_recorded
    assert len(run_recorded.preconditions()) == 2                            # the repository today: nothing registered; the licensed recording is listed in the manifest
    reg = tmp_path / "reg.md"; man = tmp_path / "m.csv"
    reg.write_text("Registration identifier: [to be entered]\nAC-N4 limit per hour: [to be entered]\n"); man.write_text("path,licence,source_url,note\n")
    assert len(run_recorded.preconditions(str(reg), str(man))) == 3
    reg.write_text("Registration identifier: osf.io/abcde\nAC-N4 limit per hour: 1.0\n"); man.write_text("path,licence,source_url,note\nx.csv,CC BY 4.0,http://u,n\n")
    assert run_recorded.preconditions(str(reg), str(man)) == []
