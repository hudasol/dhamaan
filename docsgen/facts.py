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
    f["NOT_COVERED"] = table(["Fault below E_N", "M detected", "M within T_N", "Missed seeds", "Seeds with an alarm before onset"],
                             [[r["fault"], pct(r["detected_rate"]), pct(r["detected_within_t_n_rate"]),
                               ", ".join(str(s) for s in r["missed_seeds"]) or "none",
                               ", ".join(str(s) for s in gn["conditions"]["M|" + r["fault"]]["pre_onset_alarm_seeds"]) or "none"]
                              for r in b08["not_covered_ac_n3"]])
    mx = [c["max_error_before_stop_detected"]["max"] for c in gn["conditions"].values()
          if c["method"] == "M" and c["max_error_before_stop_detected"]["max"] is not None]
    f["N_MAX_ERR_BEFORE_STOP"] = num(max(mx), 2)
    f["N_DRIFT005_NEVER"] = str(len(c("M|drift=0.05")["missed_seeds"]))
    f["N_RESTRICTIONS"] = str(len(b12["restrictions_ac_gl3"]))
    return f


def warning_facts() -> dict:
    rev = _csv("data/validator_warnings_reviewed.csv")
    decisions = sorted({r["decision"] for r in rev})
    return {"N_REVIEWED": str(len(rev)), "REVIEW_DATE": ", ".join(sorted({r["reviewed_on"] for r in rev})),
            "REVIEW_DECISIONS": "\n".join(f"> {d}" for d in decisions),
            "REVIEWED_TABLE": table(["Row", "Access", "Mentions in the paraphrase", "Locator recorded as unverified"],
                                    [[r["id"], r["access_level"], r["mentions"], "yes" if r["clause_reported_unverified"].strip() else "no"] for r in rev])}


def review_facts() -> dict:
    rows = _csv("docs/data/review_findings.csv")
    open_rows = [r for r in rows if not r["status"].startswith("fixed")]
    return {"N_REVIEW": str(len(rows)), "N_REVIEW_FIXED": str(sum(r["status"].startswith("fixed") for r in rows)),
            "N_REVIEW_OTHER": str(len(open_rows)),
            "REVIEW_TABLE": table(["Id", "Severity", "Finding", "Status", "Resolution"],
                                  [[r["id"], r["severity"], r["finding"], r["status"], r["resolution"]] for r in rows]),
            "REVIEW_NOT_FIXED": table(["Id", "Finding", "Status", "Reason"],
                                      [[r["id"], r["finding"], r["status"], r["resolution"]] for r in open_rows])}


def _observed(e: dict) -> str:
    vals = [v for c in e["checks"] for v in c["values"]]
    bad = [v for v in vals if v["pass"] is False]
    show = bad or vals
    def label(m):
        k = m.split(":", 1)[1]
        return k.split("/")[1].replace("|", " ") if k.startswith("conditions/") else k.replace("summary/", "")
    txt = "; ".join(f'{label(v["metric"])}: {num(v["value"], 2)}' for v in show[:3])
    return txt + (f"; and {len(show) - 3} more" if len(show) > 3 else "")


def r2_facts() -> dict:
    R = {n: _json(f"sim/results_r2/{n}.json") for n in ("design_gl3", "design_du3", "gl3r2", "du3r2", "heat", "n4r2")}
    S = _json("sim/results_r2/scored_r2.json"); t = S["totals"]
    f = {"R2_PREREG_SHA": S["prereg_sha256"], "R2_SEEDS": str(R["heat"]["seeds_per_condition"]),
         "R2_DEV_SEED": str(R["design_gl3"]["seed_base"]), "R2_HELDOUT_SEED": str(R["heat"]["seed_base"]),
         "R2_PRED_TOTAL": str(t["predictions"]), "R2_PRED_HIT": str(t["hit"]), "R2_PRED_MISS": str(t["miss"]),
         "R2_PRED_MISS_LIST": ", ".join(p["id"] for p in S["predictions"] if p["verdict"] == "MISS") or "none",
         "R2_AC_TOTAL": str(len(S["acceptance"])), "R2_AC_HELD": str(t["acceptance_held"]), "R2_AC_FAILED": str(t["acceptance_failed"]),
         "R2_AC_HELD_LIST": ", ".join(a["id"] for a in S["acceptance"] if a["held"]) or "none",
         "R2_AC_FAILED_LIST": ", ".join(a["id"] for a in S["acceptance"] if a["held"] is False) or "none",
         "R2_AC_EXPECTATION_MISS_LIST": ", ".join(a["id"] for a in S["acceptance"] if a["verdict"] == "MISS") or "none",
         "R2_N_RUNS": str(sum((c.get("unsafe") or c.get("detector_in_time") or c.get("exceed") or c.get("false_alarm") or c.get("within_t_h_battery"))["n"]
                              for n in ("gl3r2", "du3r2", "heat", "n4r2") for c in R[n]["conditions"].values()))}
    f["R2_PRED_TABLE"] = table(["Id", "Prediction", "Observed (failing values first)", "Verdict"],
                               [[p["id"], p["text"], _observed(p), p["verdict"]] for p in S["predictions"]])
    f["R2_AC_TABLE"] = table(["Criterion", "Statement", "Held", "Expected to hold", "Failing metrics"],
                             [[a["id"], a["text"], "yes" if a["held"] else "no", "yes" if a["expected_to_hold"] else "no",
                               _observed(a) if a["held"] is False else "none"] for a in S["acceptance"]])
    g = R["design_gl3"]["chosen"]; gs = R["gl3r2"]["summary"]
    f.update({"R2_GL_MARGIN": num(g["margin"], 2), "R2_GL_FRAMES": str(g["frames"]),
              "R2_GL_CANDIDATES": str(len(R["design_gl3"]["candidates"])),
              "R2_GL_OK": str(sum(c["ok"] for c in R["design_gl3"]["candidates"])),
              "R2_GL_M_VIOL": str(gs["M"]["ac_gl2_violating_runs"]), "R2_GL_M2_VIOL": str(gs["M2"]["ac_gl2_violating_runs"]),
              "R2_GL_M2_BELOW": str(gs["M2"]["conditions_below_p_g"])})
    d = R["design_du3"]; ds = R["du3r2"]["summary"]
    f.update({"R2_DU_THRESHOLD": num(d["chosen"]["threshold"], 2), "R2_DU_SCANS": str(d["chosen"]["scans"]),
              "R2_DU_BOUND": num(d["chosen"]["bound"], 1), "R2_DU_FEASIBLE": str(d["feasible_count"]),
              "R2_DU_GRID": str(d["grid_size"]), "R2_DU_DEV_VIOL": str(d["chosen"]["dev_violations"]),
              "R2_DU_M_TOTAL": str(ds["M"]["total"]), "R2_DU_M_BELOW": str(ds["M"]["below"]),
              "R2_DU_M2_TOTAL": str(ds["M2"]["total"]), "R2_DU_M2_BELOW": str(ds["M2"]["below"]), "R2_DU_M2_ABOVE": str(ds["M2"]["above"])})
    H = R["heat"]["conditions"]; rows = []
    for key, c in H.items():
        if c["method"] != "M": continue
        cond = key.split("|", 1)[1]
        b0, b1 = H[f"B0|{cond}"], H[f"B1|{cond}"]
        rows.append([cond.replace("|", ", ").replace("peak=", "peak "), pct(b0["exceed"]["rate"]), pct(b1["exceed"]["rate"]), num(b1["productivity"]["mean"], 2),
                     pct(c["exceed"]["rate"]), num(c["productivity"]["mean"], 2), pct(c["never_moved"]["rate"])])
    f["R2_HEAT_TABLE"] = table(["Condition", "B0 exceeds", "B1 exceeds", "B1 mean scale", "M exceeds", "M mean scale", "M never moved"], rows)
    f["R2_HEAT_RATED"] = num(R["heat"]["config"]["rated_ambient_example_degc"], 0)
    f["R2_HEAT_MARGIN"] = num(_json("sim/results_r2/heat.json")["config"]["components"]["battery"]["limit_degc"], 0)
    soakx = [c for k, c in H.items() if c["method"] == "M" and c["start"] == "soak"]
    f["R2_HEAT_SOAK_EXCEED_CONDS"] = str(sum(c["exceed"]["k"] > 0 for c in soakx)); f["R2_HEAT_SOAK_CONDS"] = str(len(soakx))
    N = R["n4r2"]["conditions"]; rows = []
    for key, c in N.items():
        rows.append([c["fault"] + "=" + num(c["size"], 2).rstrip("0").rstrip("."), pct(c["detected"]["rate"]) if c["detected"] else "n/a",
                     pct(c["detected_within_t_n"]["rate"]) if c["detected_within_t_n"] else "n/a", num(c["detection_delay"]["mean"], 1),
                     num(c["error_at_alarm"]["max"], 2), pct(c["false_alarm"]["rate"])])
    f["R2_N4_TABLE"] = table(["Fault", "Detected", "Within T_N", "Mean delay (s)", "Max error at alarm (m)", "False alarm"], rows)
    return f


def kit_facts() -> dict:
    from sim.r2 import replay
    streams, cols = _csv("data/pilot_streams.csv"), _csv("data/pilot_log_spec.csv")
    f = {"KIT_STREAMS_TABLE": table(["Stream", "File", "Minimum rate (Hz)", "Purpose", "Protocol items", "Provenance"],
                                    [[s["stream"], f'`{s["file"]}`', num(float(s["min_rate_hz"]), 0) if float(s["min_rate_hz"]) else "on event",
                                      s["purpose"], s["protocol_items"], s["provenance"]] for s in streams])}
    f["KIT_COLUMNS_TABLES"] = "\n\n".join(
        f'### `{s["file"]}`\n\n' + table(["Column", "Type", "Unit", "Required", "Meaning"],
                                         [[f'`{c["column"]}`', c["type"], c["unit"], c["required"], c["description"]]
                                          for c in cols if c["stream"] == s["stream"]]) for s in streams)
    g_text = open(_p("sim/results_r2/standin_log/gnss.csv"), encoding="utf-8").read()
    o_text = open(_p("sim/results_r2/standin_log/odometry.csv"), encoding="utf-8").read()
    g, o = replay.read_csv(g_text, replay.GNSS_COLUMNS), replay.read_csv(o_text, replay.ODO_COLUMNS)
    clean = replay.score_log(g, o)
    faulty = replay.score_log(replay.read_csv(replay.faulty_copy(g_text), replay.GNSS_COLUMNS), o)
    f.update({"KIT_FIXES": str(clean["fixes"]), "KIT_ODO_ROWS": str(clean["odometry_rows"]),
              "KIT_CLEAN_RESULT": "no fault declared" if clean["t_alarm"] is None else f'fault declared at t = {clean["t_alarm"]:.1f} s ({clean["reason"]})',
              "KIT_CLEAN_MAXERR": num(clean["max_error_m"], 2),
              "KIT_FAULT_RESULT": "no fault declared" if faulty["t_alarm"] is None else f'fault declared at t = {faulty["t_alarm"]:.1f} s ({faulty["reason"]})',
              "KIT_FAULT_MAXERR": num(faulty["max_error_m"], 2)})
    return f


def review_fix_facts() -> dict:
    """Facts added after the phase 3 review: readings computed from data instead of typed as prose."""
    import glob
    H = _json("sim/results_r2/heat.json")["conditions"]; S2 = _json("sim/results_r2/scored_r2.json"); S1 = _json("sim/results/scored.json")
    peaks = sorted({c["peak"] for c in H.values()})
    sn = [c for c in H.values() if c["method"] == "M" and c["sun"] == "shade" and c["start"] == "normal"]
    lo, hi = peaks[0], peaks[-1]
    hi_m = H[f"M|peak={hi}|shade|normal"]
    hp2 = next(p for p in S2["predictions"] if p["id"] == "H-P2")
    failing = [m.split("/")[1] for c in hp2["checks"] for m in c["failing"]]
    v = {p["id"]: p["verdict"] for p in S2["predictions"]}
    def verdicts(S): return ", ".join(f'{p["id"]} {p["verdict"]}' for p in S["predictions"])
    return {
        "R2_HEAT_LOW_PEAK": num(lo, 0), "R2_HEAT_HIGH_PEAK": num(hi, 0),
        "R2_HEAT_B1_LOW_SHADE_EXCEED": pct(H[f"B1|peak={lo}|shade|normal"]["exceed"]["rate"]),
        "R2_HEAT_M_SHADE_NORMAL_OK": str(sum(c["exceed"]["k"] == 0 for c in sn)), "R2_HEAT_M_SHADE_NORMAL_N": str(len(sn)),
        "R2_HEAT_M_HIGH_SHADE_SCALE": num(hi_m["productivity"]["mean"], 2), "R2_HEAT_M_HIGH_SHADE_NEVER": pct(hi_m["never_moved"]["rate"]),
        "R2_HP2_FAIL_TOTAL": str(len(failing)), "R2_HP2_FAIL_SOAK": str(sum("|soak" in f for f in failing)),
        "R2_HP2_FAIL_SUN_NORMAL": str(sum("|sun|normal" in f for f in failing)),
        "R2_V_GL3R2_P1": v["GL3R2-P1"], "R2_V_DU3R2_P1": v["DU3R2-P1"],
        "PRED_VERDICTS": f"- First round: {verdicts(S1)}.\n- Second round: {verdicts(S2)}.",
        "PARTIAL_IDS": ", ".join(e.split(" ")[0] for e in F_partial_ids()),
        "N_TEMPLATES": str(len(glob.glob(_p("assurance/templates/*.yaml")))),
        "R2_HEAT_SAME_FACTOR": str(sum(H[f"B0|{k.split('|', 1)[1]}"]["stop_factor"]["max"] == c["stop_factor"]["max"]
                                       for k, c in H.items() if c["method"] == "M")),
        "R2_HEAT_CONDS": str(sum(c["method"] == "M" for c in H.values())),
    }


def F_partial_ids() -> list[str]:
    case = ac_check.load(_p("assurance/library_robot_case.yaml"))
    return [e["id"] for e in case["evidence"] if e["status"] == "partial"]


def check_facts() -> dict:
    p = _p("docs/data/check_summary.json")
    if not os.path.exists(p): return {"TESTS_PASSED": "n/a", "CHECK_LINES": "not recorded"}
    d = json.load(open(p, encoding="utf-8"))
    return {"TESTS_PASSED": str(d["tests_passed"]),
            "CHECK_LINES": "\n".join(f"- {s['name']}: {s['summary']}" for s in d["steps"])}


def manuscript_facts() -> dict:
    """Numbers for docs/paper/manuscript.md. Missing round 3 results are stated as not yet run, never filled in."""
    h = _json("data/silence_audit/h1_result.json"); ag = _json("data/silence_audit/agreement.json")
    ins = h["in_scope"]; full = h["in_scope_full_text_only"]
    kappas = [v["kappa"] for k, v in ag.items() if isinstance(v, dict) and "kappa" in v]
    ind = _json("sim/results_r3/independent_generator.json")
    n_diff = len(ind["different"]); n_ind = len(ind["verdicts"])
    off = _csv("data/official_r3_status.csv")
    n_off_open = sum(r["status_after"] != "confirmed" for r in off)
    f = {
        "MS_SILENCE_CAND": str(h["candidates"]), "MS_SILENCE_SCOPE": str(ins["rows"]), "MS_SILENCE_OUT": str(h["out_of_scope"]),
        "MS_SILENCE_ASK": str(ins["ask_for_evidence"]), "MS_SILENCE_NOASK": str(ins["do_not_ask"]), "MS_SILENCE_UNCLEAR": str(ins["unclear_whether_they_ask"]),
        "MS_SILENCE_DELEG": str(ins["of_those_leave_conditions_to_the_developer"]), "MS_SILENCE_SEV": str(ins["of_those_fix_a_severity"]),
        "MS_SILENCE_SEV_GULF": str(ins["of_those_fix_a_severity_that_applies_to_a_gulf_site"]), "MS_SILENCE_METHOD": str(ins["of_those_fix_a_test_method"]),
        "MS_SILENCE_FULL_ROWS": str(full["rows"]), "MS_SILENCE_FULL_DELEG": str(full["of_those_leave_conditions_to_the_developer"]),
        "MS_SILENCE_LIMIT": h["limit"],
        "MS_KAPPA_MIN": num(min(kappas), 2), "MS_KAPPA_MAX": num(max(kappas), 2), "MS_CODED_ROWS": str(ag["n_rows"]),
        "MS_IND_N": str(n_ind), "MS_IND_DIFF": str(n_diff), "MS_IND_LIMIT": ind["limit"],
        "MS_OFFICIAL_N": str(len(off)), "MS_OFFICIAL_OPEN": str(n_off_open),
    }
    sp = _p("sim/results_r3/summary.json")
    if os.path.exists(sp):
        s = json.load(open(sp, encoding="utf-8")); s = s.get("summary", s)
        f.update({"MS_R3_STATE": "complete", "MS_R3_PREDS": str(s["predictions"]), "MS_R3_HIT": str(s["hit"]),
                  "MS_R3_INF": str(s["informative"]), "MS_R3_INF_HIT": str(s["informative_hit"]),
                  "MS_R3_UNINF": str(s["uninformative"]), "MS_R3_UNINF_IDS": ", ".join(s["uninformative_ids"]) or "none",
                  "MS_R3_MUTANTS": str(s["mutants_run"])})
    else:
        f.update({"MS_R3_STATE": "not yet run", "MS_R3_PREDS": "n/a", "MS_R3_HIT": "n/a", "MS_R3_INF": "n/a", "MS_R3_INF_HIT": "n/a",
                  "MS_R3_UNINF": "n/a", "MS_R3_UNINF_IDS": "n/a", "MS_R3_MUTANTS": "n/a"})
    return f


def r3_facts() -> dict:
    sp = _p("sim/results_r3/summary.json")
    if not os.path.exists(sp):
        return {k: "not yet run" for k in ("R3_SUMMARY", "R3_INFO_TABLE", "R3_SENS_TABLE", "R3_LABEL")}
    S = json.load(open(sp, encoding="utf-8"))
    info = _csv("sim/results_r3/informativeness.csv"); sens = _csv("sim/results_r3/sensitivity.csv")
    preds = [r for r in info if r["kind"] == "prediction"]
    unin = [r for r in preds if r["informative"] != "True"]
    summ = (f"{S['informative']} of {S['predictions']} predictions are informative (their verdict changes under at least one mutant); "
            f"{S['informative_hit']} of those {S['informative']} hit, against {S['hit']} of {S['predictions']} overall. "
            f"Uninformative: {', '.join(S['uninformative_ids']) or 'none'}. {S['mutants_run']} mutants were run over {S['parameters']} assumed parameters at the factors {', '.join(str(x) for x in S['factors'])}.")
    it = table(["Round", "Prediction", "Verdict", "Mutants changing it", "M0", "M1", "M3", "Informative"],
               [[r["round"], r["id"], r["original"], r["changed_under"], r["M0"], r["M1"], r["M3"], r["informative"]] for r in preds])
    held = collections.defaultdict(list)
    for r in sens: held[(r["round"], r["criterion"], r["original_held"], r["mutated_held"])].append(f'{r["parameter"]} x{r["factor"]}')
    st = table(["Round", "Criterion", "Held in original", "Held after change", "Flips", "Parameters (first five)"],
               [[k[0], k[1], k[2], k[3], len(v), "; ".join(v[:5])] for k, v in sorted(held.items())])
    return {"R3_SUMMARY": summ, "R3_INFO_TABLE": it, "R3_SENS_TABLE": st, "R3_LABEL": S["label"]}


def rec_facts() -> dict:
    keys = ("REC_LABEL", "REC_STATE", "REC_N", "REC_CAL", "REC_HELD", "REC_THRESHOLD", "REC_DET_TABLE", "REC_HELD_TABLE", "REC_TYPE_TABLE",
            "REC_PRED_TABLE", "REC_SYN_TABLE", "REC_NOMINAL", "REC_M_FA", "REC_M_FA_CI", "REC_M_SYN_FA", "REC_M_SESS", "REC_M_LOSS", "REC_M_CHANCE",
            "REC_DATASET", "REC_HOURS", "REC_BEST_BASELINE", "REC_P_HIT", "REC_P_TOTAL")
    rp = _p("sim/results_r3/recorded/recorded_results.json")
    if not os.path.exists(rp):
        return {k: "not yet run" for k in keys}
    R = json.load(open(rp, encoding="utf-8")); P = json.load(open(_p("sim/results_r3/recorded/predictions.json"), encoding="utf-8"))
    Y = json.load(open(_p("sim/results_r3/recorded/synthetic_arms.json"), encoding="utf-8"))
    names = list(R["R_all"]); f3 = lambda x: "n/a" if x is None else f"{x:.2f}"
    def det_rows(tab):
        out = []
        for n in names:
            g = tab[n]; fa = g["false_alarms"]; sd = g["session_detection"]["all"]; le = g["loss_of_fix_events"]
            out.append([n, g["sessions"], f'{fa["alarms"]} in {fa["exposure_hours"]:.2f} h', f3(fa["per_hour"]),
                        f'{f3(fa["ci95_per_hour"][0])} to {f3(fa["ci95_per_hour"][1])}', f'{sd["k"]} of {sd["n"]}', f'{le["k"]} of {le["n"]}',
                        g["verdicts"]["AC-N1r"], g["verdicts"]["AC-N4"]])
        return out
    hdr = ["Detector", "Recordings", "Nominal alarms", "Per nominal hour", "95 percent interval", "Sessions alarmed", "Loss of fix events alarmed", "AC-N1r", "AC-N4"]
    types = sorted(t for t in R["R_all"]["M"]["session_detection"] if t != "all")
    tt = table(["Detector"] + [f"{t} sessions" for t in types],
               [[n] + [f'{R["R_all"][n]["session_detection"][t]["k"]} of {R["R_all"][n]["session_detection"][t]["n"]}' for t in types] for n in names])
    desc = {"R3-P1": "Verdicts of AC-N1 or AC-N4 differ between S0 and R", "R3-P2": "False alarm rate of M is higher on R than on S0",
            "R3-P3": "Spoofing sessions are alarmed less often than jamming sessions", "R3-P4": "S1 is closer to R than S0 on false alarms",
            "R3-P5": "S1 reproduces the verdicts of R", "R3-P6": "Held out nominal fix error is heavy tailed and autocorrelated",
            "R3-P7": "D-RX alarms in fewer spoofing and meaconing sessions than M", "R3-P8": "D-JAM alarms in fewer meaconing sessions than M",
            "R3-P9": "No detector satisfies both AC-N1r and AC-N4 on all recordings"}
    pr = P["predictions"]
    pt = table(["Prediction", "Statement", "Outcome"], [[k, desc[k], "not scored" if v is None else ("hit" if v else "miss")] for k, v in sorted(pr.items())])
    st = table(["Arm", "Nominal false alarms per hour", "AC-N1", "AC-N4"],
               [["S0 (synthetic, developer parameters)", f3(Y["S0"]["false_alarms_per_hour"]), Y["S0"]["verdicts"]["AC-N1"], Y["S0"]["verdicts"]["AC-N4"]],
                ["S1 (synthetic, recalibrated on recordings)", f3(Y["S1"]["false_alarms_per_hour"]) if Y["S1"] else "n/a", Y["S1"]["verdicts"]["AC-N1"] if Y["S1"] else "n/a", Y["S1"]["verdicts"]["AC-N4"] if Y["S1"] else "n/a"],
                ["R (recorded, all recordings)", f3(R["R_all"]["M"]["false_alarms"]["per_hour"]), R["R_all"]["M"]["verdicts"]["AC-N1r"], R["R_all"]["M"]["verdicts"]["AC-N4"]]])
    ne = R["nominal_error_held_out"] or {}
    nom = (f'On {ne["segments"]} held out still nominal segments ({ne["fixes_used"]} fixes), sigma {f3(ne["sigma_m"])} m, lag one correlation {f3(ne["lag1_correlation"])}, excess kurtosis {f3(ne["excess_kurtosis"])}.' if ne else "No held out still nominal segment.")
    M = R["R_all"]["M"]; others = [n for n in names if n != "M"]
    best = min(others, key=lambda n: (R["R_all"][n]["false_alarms"]["per_hour"] if R["R_all"][n]["false_alarms"]["per_hour"] is not None else 1e9))
    hit = sum(1 for v in pr.values() if v is True); tot = sum(1 for v in pr.values() if v is not None)
    out = {"REC_LABEL": R["label"], "REC_STATE": "run once", "REC_N": R["recordings"], "REC_CAL": len(R["calibration"]), "REC_HELD": len(R["held_out"]),
            "REC_THRESHOLD": f3(R["jam_threshold"]), "REC_DET_TABLE": table(hdr, det_rows(R["R_all"])), "REC_HELD_TABLE": table(hdr, det_rows(R["R_held"])),
            "REC_TYPE_TABLE": tt, "REC_PRED_TABLE": pt, "REC_SYN_TABLE": st, "REC_NOMINAL": nom,
            "REC_M_FA": f3(M["false_alarms"]["per_hour"]), "REC_M_FA_CI": f'{f3(M["false_alarms"]["ci95_per_hour"][0])} to {f3(M["false_alarms"]["ci95_per_hour"][1])}',
            "REC_M_SYN_FA": f3(Y["S0"]["false_alarms_per_hour"]), "REC_M_SESS": f'{M["session_detection"]["all"]["k"]} of {M["session_detection"]["all"]["n"]}',
            "REC_M_LOSS": f'{M["loss_of_fix_events"]["k"]} of {M["loss_of_fix_events"]["n"]}', "REC_M_CHANCE": f3(M["chance_alarms_per_session"]),
            "REC_HOURS": f3(M["false_alarms"]["exposure_hours"]), "REC_BEST_BASELINE": best, "REC_P_HIT": hit, "REC_P_TOTAL": tot}
    out["REC_DATASET"] = "Jammertest 2024"
    return {k: str(v) for k, v in out.items()}


def all_facts() -> dict:
    f = {}
    for part in (evidence_table_facts(), case_facts(), context_facts(), warning_facts(), review_facts(), sim_facts(), r2_facts(), kit_facts(), review_fix_facts(), check_facts(), manuscript_facts(), r3_facts(), rec_facts()):
        assert not set(part) & set(f), set(part) & set(f)
        f.update(part)
    return f
