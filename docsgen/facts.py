"""Every number that appears in a generated document is computed here from a file in the repository.

Sources: data/evidence_table.csv, data/official_checks.csv, data/verification/outcome.json,
assurance/library_robot_case.yaml (through tools/ac_check.py), sim/results/*.json, sim/acceptance.py,
sim/predictions.py and docs/data/check_summary.json (written by tools/fast_check.py --record).
"""
from __future__ import annotations

import collections, csv, json, os, sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, ROOT)

import ac_check  # noqa: E402  (tools layer)
from sim import acceptance as A  # noqa: E402  (sim layer)
from sim import common as SC  # noqa: E402
from sim.predictions import ACCEPTANCE, PREDICTIONS  # noqa: E402


def _p(*a): return os.path.join(ROOT, *a)
def _json(rel): return json.load(open(_p(rel), encoding="utf-8"))
def _csv(rel): return list(csv.DictReader(open(_p(rel), encoding="utf-8", newline="")))


def pct(x, nd=0) -> str:
    """A rate in [0, 1] as a percent string."""
    if x is None: return "n/a"
    v = round(100 * x, nd)
    return f"{v:.{nd}f} percent"


def num(x, nd=2) -> str:
    if x is None: return "n/a"
    if isinstance(x, int) or float(x).is_integer() and nd == 0: return str(int(round(x)))
    return f"{x:.{nd}f}"


def table(header: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def evidence_table_facts() -> dict:
    rows = _csv("data/evidence_table.csv")
    acc = collections.Counter(r["access_level"] for r in rows)
    bind = collections.Counter(r["binding_status"] for r in rows)
    out = _json("data/verification/outcome.json")
    ab, c = out["passes_A_B_on_input_v2"]["row"]["either"], out["pass_C"]
    vs = out["final_table"]["verification_status"]
    return {
        "N_ROWS": str(len(rows)), "N_FAMILIES": str(len({r["family"] for r in rows})),
        "ACC_FULL": str(acc["full text seen"]), "ACC_SUMMARY": str(acc["summary seen"]), "ACC_TITLE": str(acc["title only"]),
        "BIND_MANDATORY": str(bind["mandatory"]), "BIND_CONDITIONAL": str(bind["conditional"]),
        "BIND_VOLUNTARY": str(bind["voluntary"]), "BIND_GUIDANCE": str(bind["guidance"]),
        "N_OFFICIAL": str(len(_csv("data/official_checks.csv"))),
        "ROW_ERR_EITHER": f'{ab["pct"]} percent', "ROW_ERR_CI": f'{ab["ci95"][0]} to {ab["ci95"][1]} percent',
        "PASSC_CHANGED": f'{c["changed"]["row"]["pct"]} percent', "PASSC_UNCHANGED": f'{c["unchanged_sample"]["row"]["pct"]} percent',
        "N_SINGLE_CHECKED": str(vs["corrected after final check, single checked"]),
    }


CONTEXT_ROWS = {
    "UAE drone regime": ["C47", "C48", "C49", "C52", "C60"],
    "UAE ground autonomy (roads)": ["C64", "C65", "D50", "C66"],
    "GNSS interference in the UAE region": ["D57", "D58", "D59", "D52"],
    "Instruments that apply if a product is placed on the EU market": ["A01", "B17", "C01"],
}


def context_facts() -> dict:
    rows = {r["id"]: r for r in _csv("data/evidence_table.csv")}
    out = []
    for group, ids in CONTEXT_ROWS.items():
        out.append(f"### {group}\n")
        out.append(table(["Row", "Instrument or source", "What the source says (paraphrase)", "Binding", "Access", "Source"],
                         [[i, rows[i]["instrument"], rows[i]["requirement_paraphrase"].replace("|", "/"), rows[i]["binding_status"],
                           rows[i]["access_level"], rows[i]["source_url"]] for i in ids]))
        out.append("")
    return {"CONTEXT_TABLES": "\n".join(out).strip(),
            "CONTEXT_N_ROWS": str(sum(len(v) for v in CONTEXT_ROWS.values()))}


def case_facts() -> dict:
    case = ac_check.load(_p("assurance/library_robot_case.yaml"))
    res = ac_check.check(case, ac_check.table_rows(_p("data/evidence_table.csv")), ROOT)
    codes = collections.Counter(code for s, code, i, m in res if s == "FLAG")
    ev = case["evidence"]
    partial = [e for e in ev if e["status"] == "partial"]
    return {
        "N_GOALS": str(len(case["goals"])), "N_EVIDENCE_ITEMS": str(len(ev)),
        "N_OPEN": str(sum(e["status"] == "open" for e in ev)), "N_PARTIAL": str(len(partial)),
        "N_PROVIDED": str(sum(e["status"] == "provided" for e in ev)),
        "PARTIAL_LIST": ", ".join(f'{e["id"]} ({e["kind"]}, `{e["artefact"]}`)' for e in partial),
        "CASE_ERRORS": str(sum(s == "ERROR" for s, *_ in res)), "CASE_FLAGS": str(sum(s == "FLAG" for s, *_ in res)),
        "CASE_FLAG_TABLE": table(["Flag", "Count"], [[k, str(v)] for k, v in sorted(codes.items())]),
        "SIM_ONLY_GOALS": ", ".join(i for s, code, i, m in res if code == "CLAIM_SIM_ONLY"),
    }


def _metric(results, path):
    f, keys = path.split(":", 1)
    node = results[f]
    for k in keys.split("/"):
        if node is None: return None
        node = node[k]
    return node


def sim_facts() -> dict:
    R = {n: _json(f"sim/results/{n}.json") for n in ("du3", "gl3", "gnss")}
    S = _json("sim/results/scored.json")
    du3, gl3, gn = R["du3"], R["gl3"], R["gnss"]
    t = S["totals"]
    f = {
        "SEEDS": str(du3["seeds_per_condition"]), "BASE_SEED": str(du3["base_seed"]),
        "PREREG_SHA": S["prereg_sha256"], "SIM_LABEL": du3["label"],
        "N_DU3_LEVELS": str(len(du3["config"]["levels"])), "N_GL3_CONDITIONS": str(len(gl3["conditions"]) // 3),
        "N_GNSS_CONDITIONS": str(len(gn["config"]["conditions"])),
        "N_RUNS": str(sum(c.get("unsafe", c.get("false_alarm"))["n"] for r in R.values() for c in r["conditions"].values())),
        "PRED_TOTAL": str(t["predictions"]), "PRED_HIT": str(t["hit"]), "PRED_MISS": str(t["miss"]),
        "AC_TOTAL": str(len(S["acceptance"])), "AC_HELD": str(t["acceptance_held"]), "AC_FAILED": str(t["acceptance_failed"]),
        "AC_HELD_LIST": ", ".join(a["id"] for a in S["acceptance"] if a["held"]),
        "AC_FAILED_LIST": ", ".join(a["id"] for a in S["acceptance"] if a["held"] is False),
        "PRED_MISS_LIST": ", ".join(p["id"] for p in S["predictions"] if p["verdict"] == "MISS"),
        "AC_EXPECTATION_MISS_LIST": ", ".join(a["id"] for a in S["acceptance"] if a["verdict"] == "MISS"),
    }
    # acceptance values
    f.update({"B_D": num(A.B_D, 1), "T_D": num(A.T_D, 1), "P_G": num(A.P_G), "S_G": num(A.S_G, 1), "T_G": num(A.T_G, 1),
              "T_N": num(A.T_N, 0), "Q_N": num(A.Q_N, 1), "L_N": num(A.L_N, 1),
              "E_N_JUMP": num(A.E_N["jump"], 0), "E_N_DRIFT": num(A.E_N["drift"], 1),
              "E_N_NOISE": num(A.E_N["noise"], 0), "E_N_REPLAY": num(A.E_N["replay"], 0)})
    # configs for METHOD
    for name, r in (("DU3", du3), ("GL3", gl3), ("GN", gn)):
        for k, v in r["config"].items():
            if isinstance(v, (int, float)) and not isinstance(v, bool): f[f"{name}_{k.upper()}"] = num(v, 0) if float(v).is_integer() else str(v)
    st = SC.Stopping()
    f.update({"STOP_T_REACT": num(st.t_react, 1), "STOP_DECEL": num(st.decel, 1), "STOP_MARGIN": num(st.margin, 1),
              "STOP_REQ_NOMINAL": num(st.required(du3["config"]["v_nominal"]), 2)})
    f["DU3_LEVELS"] = ", ".join(num(x, 1) for x in du3["config"]["levels"])
    f["GL3_ELEVATIONS"] = ", ".join(str(x) for x in gl3["config"]["elevations"])
    f["GL3_AZIMUTHS"] = ", ".join(str(x) for x in gl3["config"]["azimuths"])
    f["GL3_RHOS"] = ", ".join(num(x, 1) for x in gl3["config"]["rhos"])
    f["GN_CONDITIONS"] = ", ".join(gn["config"]["conditions"])
    # prediction and acceptance tables
    def observed(e):
        vals = [v for c in e["checks"] for v in c["values"]]
        bad = [v for v in vals if v["pass"] is False]
        show = bad or vals
        txt = "; ".join(f'{v["metric"].split("/", 1)[1].rsplit("/", 2)[0].replace("|", " ")}: {num(v["value"], 2)}' for v in show[:3])
        return txt + (f"; and {len(show) - 3} more" if len(show) > 3 else "")
    f["PRED_TABLE"] = table(["Id", "Prediction", "Observed (failing values first)", "Verdict"],
                            [[p["id"], p["text"], observed(p), p["verdict"]] for p in S["predictions"]])
    f["AC_TABLE"] = table(["Criterion", "Statement", "Held", "Expected to hold", "Failing metrics"],
                          [[a["id"], a["text"], "yes" if a["held"] else "no", "yes" if a["expected_to_hold"] else "no",
                            observed(a) if a["held"] is False else "none"] for a in S["acceptance"]])
    # DU3 table
    rows = []
    for k in du3["config"]["levels"]:
        c = {m: du3["conditions"][f"{m}|k={k:.1f}"] for m in ("B0", "B1", "M")}
        rows.append([num(k, 1), pct(c["B0"]["unsafe"]["rate"]), pct(c["B1"]["unsafe"]["rate"]), pct(c["M"]["unsafe"]["rate"]),
                     pct(c["M"]["monitor_stop"]["rate"]), num(c["B0"]["detection_distance"]["median"], 2)])
    f["DU3_TABLE"] = table(["k", "B0 unsafe", "B1 unsafe", "M unsafe", "M monitor stop", "B0 median detection distance (m)"], rows)
    early = [k for k in du3["config"]["levels"] if k <= A.B_D and du3["conditions"][f"M|k={k:.1f}"]["monitor_stop"]["rate"]
             and du3["conditions"][f"B0|k={k:.1f}"]["unsafe"]["rate"] == 0 and k < A.B_D]
    k_early = early[-1] if early else None
    f["DU3_EARLY_STOP_K"] = num(k_early, 1)
    f["DU3_M_EARLY_STOP"] = pct(du3["conditions"][f"M|k={k_early:.1f}"]["monitor_stop"]["rate"]) if early else "n/a"
    f["DU3_B0_UNSAFE_AT_1"] = pct(du3["conditions"]["B0|k=1.0"]["unsafe"]["rate"])
    # GL3 tables
    fail_rows = []
    for key, c in sorted(gl3["conditions"].items()):
        if c["detected_in_time"]["rate"] < A.P_G:
            fail_rows.append([c["method"], num(c["elevation_deg"], 0), num(c["azimuth_deg"], 0), num(c["rho"], 1),
                              num(c["saturation_model"], 2), pct(c["detected_in_time"]["rate"])])
    f["GL3_FAIL_TABLE"] = table(["Method", "Elevation (deg)", "Azimuth (deg)", "rho", "Model saturation", "In time detection"], fail_rows)
    for m in ("B0", "B1", "M"): f[f"GL3_{m}_FAILS"] = str(gl3["summary"][m]["conditions_below_p_g"])
    ac2 = next(a for a in S["acceptance"] if a["id"] == "AC-GL2")
    fails = sorted({m.split("/")[1] for c in ac2["checks"] for m in c["failing"]})
    g2 = gl3["conditions"][fails[0]] if fails else None
    f["GL3_AC2_COND"] = (f'elevation {num(g2["elevation_deg"], 0)}, azimuth {num(g2["azimuth_deg"], 0)}, reflection {num(g2["rho"], 1)}'
                         + (f" and {len(fails) - 1} more" if len(fails) > 1 else "")) if g2 else "none"
    g2 = g2 or {"saturation_model": None, "slow_command_runs_where_s_exceeded": {"rate": None}, "slow_command_delay": {"max": None}}
    f["GL3_AC2_COND_SAT"] = num(g2["saturation_model"], 2)
    f["GL3_AC2_COND_CMD"] = pct(g2["slow_command_runs_where_s_exceeded"]["rate"])
    f["GL3_AC2_COND_DELAY_MAX"] = num(g2["slow_command_delay"]["max"], 1)
    # GNSS table
    grows = []
    for cond in gn["config"]["conditions"]:
        c = {m: gn["conditions"][f"{m}|{cond}"] for m in ("B0", "B1", "M")}
        M = c["M"]
        grows.append([cond, pct(M["detected"]["rate"]) if M["detected"] else "n/a",
                      pct(M["detected_within_t_n"]["rate"]) if M["detected_within_t_n"] else "n/a",
                      num(M["detection_delay"]["mean"], 1), num(M["error_at_stop"]["max"], 2),
                      pct(c["B0"]["error_exceeds_l_n"]["rate"]), pct(c["B1"]["error_exceeds_l_n"]["rate"]),
                      pct(M["error_exceeds_l_n"]["rate"]), pct(M["false_alarm"]["rate"])])
    f["GNSS_TABLE"] = table(["Fault", "M detected", "M within T_N", "M mean delay (s)", "M max error at stop (m)",
                             "B0 error above L_N", "B1 error above L_N", "M error above L_N", "M false alarm"], grows)
    c = lambda k: gn["conditions"][k]
    f["N_JUMP2_DET"] = pct(c("M|jump=2")["detected"]["rate"])
    f["N_NOISE5_TN"] = pct(c("M|noise=5")["detected_within_t_n"]["rate"])
    f["N_NOISE5_DELAY"] = num(c("M|noise=5")["detection_delay"]["mean"], 1)
    f["N_DRIFT02_DELAY"] = num(c("M|drift=0.2")["detection_delay"]["mean"], 1)
    f["N_DRIFT01_DELAY"] = num(c("M|drift=0.1")["detection_delay"]["mean"], 1)
    f["N_DRIFT005_EXCEED"] = pct(c("M|drift=0.05")["error_exceeds_l_n"]["rate"])
    f["N_REPLAY2_DET"] = pct(c("M|replay=2")["detected"]["rate"])
    f["N_B0_NOISE10_EXCEED"] = pct(c("B0|noise=10")["error_exceeds_l_n"]["rate"])
    f["N_B1_DRIFT01_EXCEED"] = pct(c("B1|drift=0.1")["error_exceeds_l_n"]["rate"])
    f["N_M_NOMINAL_FA"] = pct(c("M|nominal=0")["false_alarm"]["rate"])
    fa = [v["false_alarm"] for k, v in gn["conditions"].items() if v["method"] == "M"]
    f["N_M_ALL_FA_K"] = str(sum(x["k"] for x in fa)); f["N_M_ALL_FA_N"] = str(sum(x["n"] for x in fa))
    # prediction thresholds quoted in prose
    pv = {p["id"]: p["checks"][0]["value"] for p in PREDICTIONS}
    f["PV_N_P4"] = pct(pv["N-P4"]); f["PV_N_P8"] = pct(pv["N-P8"])
    # restrictions and not covered from the bundles
    b12, b08 = _json("sim/results/EV-12.json"), _json("sim/results/EV-08.json")
    f["RESTRICTIONS"] = table(["Sun condition", "Model saturation", "M in time detection"],
                              [[r["condition"].replace("|", ", "), num(r["saturation_model"], 2), pct(r["detected_in_time_rate"])] for r in b12["restrictions_ac_gl3"]])
    f["NOT_COVERED"] = table(["Fault below E_N", "M detected", "M within T_N", "Missed seeds"],
                             [[r["fault"], pct(r["detected_rate"]), pct(r["detected_within_t_n_rate"]),
                               ", ".join(str(s) for s in r["missed_seeds"]) or "none"] for r in b08["not_covered_ac_n3"]])
    f["N_RESTRICTIONS"] = str(len(b12["restrictions_ac_gl3"]))
    return f


def check_facts() -> dict:
    p = _p("docs/data/check_summary.json")
    if not os.path.exists(p): return {"TESTS_PASSED": "n/a", "CHECK_LINES": "not recorded"}
    d = json.load(open(p, encoding="utf-8"))
    return {"TESTS_PASSED": str(d["tests_passed"]),
            "CHECK_LINES": "\n".join(f"- {s['name']}: {s['summary']}" for s in d["steps"])}


def all_facts() -> dict:
    f = {}
    for part in (evidence_table_facts(), case_facts(), context_facts(), sim_facts(), check_facts()):
        assert not set(part) & set(f), set(part) & set(f)
        f.update(part)
    return f
