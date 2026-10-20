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
