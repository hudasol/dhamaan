"""Scoring of the recorded arm (docs/ANALYSIS_PLAN_R3_RECORDED.md). Pure functions; tests use SYNTHETIC recordings made inside the test.

record_scores()   per recording and detector: nominal alarms and exposure, session alarms, loss of fix events
aggregate()       rates with intervals, by attack type, and the verdicts AC-N1r and AC-N4
synthetic_arm()   the S0 or S1 arm with the unchanged monitor, through sim/r3/recorded.py
predictions()     R3-P1 to R3-P9 by script
"""
from __future__ import annotations

import math

import numpy as np

from sim import acceptance as A, common
from sim.r2 import replay
from sim.r3 import detectors as D, jammertest as J, recorded

FA_LIMIT_PER_HOUR = 1.0     # AC-N4, fixed in the plan
CHANCE_NOTE = "alarms expected in the session if the nominal false alarm rate held"


def poisson_ci(k: int, hours: float, alpha: float = 0.05) -> list[float | None]:
    """Exact (Garwood) 95 percent interval for a rate of k events in `hours`, by bisection on the Poisson distribution."""
    if hours <= 0: return [None, None]
    def cdf(x, lam):             # P(X <= x)
        return sum(math.exp(-lam + i * math.log(lam) - math.lgamma(i + 1)) for i in range(int(x) + 1)) if lam > 0 else 1.0
    def solve(f, lo, hi):
        for _ in range(200):
            mid = (lo + hi) / 2
            if f(mid): hi = mid
            else: lo = mid
        return (lo + hi) / 2
    lo = 0.0 if k == 0 else solve(lambda lam: 1 - cdf(k - 1, lam) >= alpha / 2, 0.0, k + 10 * math.sqrt(k + 1) + 10)
    hi = solve(lambda lam: cdf(k, lam) <= alpha / 2, 0.0, k + 10 * math.sqrt(k + 1) + 10)
    return [lo / hours, hi / hours]


def calibrate_jam_threshold(recs: list[dict], q: float = 99.9) -> float:
    vals = []
    for r in recs:
        seg = J.segments(r)
        for s in (seg["leading"], seg["trailing"]):
            if s: vals += [x["jam"] for x in r["rf"] if s[0] <= x["t_s"] <= s[1]]
    if not vals: raise ValueError("no nominal radio frequency rows in the calibration recordings")
    return float(np.percentile(vals, q))


def record_scores(rec: dict, params: dict, names: tuple[str, ...] = D.NAMES) -> dict:
    seg = J.segments(rec); out = {"id": rec["id"], "attack_type": rec["attack_type"], "session": rec["session"], "detectors": {}}
    if not rec["session"]: return out | {"excluded": rec["window_error"]}
    s, e = rec["session"]; events = J.denial_events(rec)
    out["denial_events"] = events
    for n in names:
        nominal = []
        for key in ("leading", "trailing"):
            if seg[key]:
                a, b = seg[key]; al = D.run_episodes(n, rec["fixes"], rec["rf"], a, b, params)
                nominal.append({"segment": key, "seconds": b - a, "alarms": al})
        exposure = sum(max(0.0, x["seconds"] - D.REARM_S * len(x["alarms"])) for x in nominal)
        ra, rb = seg["session_run"]; al = D.run_episodes(n, rec["fixes"], rec["rf"], ra, rb, params)
        in_session = [t for t in al if s <= t <= e]
        ev = [{"onset": o, "detected": any(o - D.REARM_S <= t <= o + A.T_N for t in al)} for o in events]
        out["detectors"][n] = {"nominal_alarms": sum(len(x["alarms"]) for x in nominal), "nominal_exposure_s": exposure,
                               "session_alarms": len(in_session), "first_alarm_delay_s": (in_session[0] - s) if in_session else None,
                               "session_seconds": e - s, "loss_events": ev}
    return out


def _wil(k: int, n: int) -> dict:
    return {"k": k, "n": n, "rate": (k / n) if n else None, "ci95": common.wilson(k, n)}


def aggregate(scores: list[dict], name: str) -> dict:
    rows = [r["detectors"][name] | {"attack_type": r["attack_type"], "id": r["id"]} for r in scores if name in r["detectors"]]
    alarms = sum(r["nominal_alarms"] for r in rows); hours = sum(r["nominal_exposure_s"] for r in rows) / 3600.0
    fa = {"alarms": alarms, "exposure_hours": hours, "per_hour": (alarms / hours) if hours > 0 else None,
          "ci95_per_hour": poisson_ci(alarms, hours), "recordings_with_nominal": sum(r["nominal_exposure_s"] > 0 for r in rows)}
    by_type = {}
    for t in sorted({r["attack_type"] for r in rows} | {"all"}):
        rs = [r for r in rows if t == "all" or r["attack_type"] == t]
        by_type[t] = _wil(sum(r["session_alarms"] > 0 for r in rs), len(rs))
    chance = None
    if fa["per_hour"] is not None and rows: chance = float(np.mean([fa["per_hour"] * r["session_seconds"] / 3600.0 for r in rows]))
    delays = [r["first_alarm_delay_s"] for r in rows if r["first_alarm_delay_s"] is not None]
    events = [ev for r in rows for ev in r["loss_events"]]
    no_loss = [r for r in rows if not r["loss_events"]]
    loss = _wil(sum(e["detected"] for e in events), len(events))
    nonloss = _wil(sum(r["session_alarms"] > 0 for r in no_loss), len(no_loss))
    n1 = None
    if loss["n"] and nonloss["n"]: n1 = bool(loss["rate"] >= A.Q_N and nonloss["rate"] >= A.Q_N)
    n4 = None if fa["per_hour"] is None else bool(fa["per_hour"] <= FA_LIMIT_PER_HOUR)
    return {"detector": name, "sessions": len(rows), "false_alarms": fa, "session_detection": by_type,
            "alarms_per_session_mean": float(np.mean([r["session_alarms"] for r in rows])) if rows else None,
            "chance_alarms_per_session": chance, "chance_note": CHANCE_NOTE,
            "first_alarm_delay_s": {"median": float(np.median(delays)) if delays else None, "n": len(delays)},
            "loss_of_fix_events": loss, "sessions_without_loss_event": nonloss,
            "verdicts": {"AC-N1r": n1, "AC-N4": n4, "AC-N2r": "not evaluable: no reference trajectory"}}


def nominal_stats(recs: list[dict]) -> dict | None:
    rows = [x for x in (J.nominal_error_rows(r) for r in recs) if x]
    if len(rows) < 1: return None
    return recorded.calibrate([(x, []) for x in rows]) | {"segments": len(rows)}


def synthetic_arm(cal: dict | None, n_logs: int = 100) -> dict:
    """Arm S0 (cal is None) or S1 (cal from calibration recordings): the unchanged monitor on stand in logs with the covered faults and none."""
    def logs():
        out = []
        for i in range(n_logs):
            rng = common.rng_for("R3REC", "S1log" if cal else "S0log", i)
            out.append(recorded.s1_standin(rng, cal) if cal else replay.standin(rng))
        return out
    base = logs(); conds = {}
    for cond in ["nominal=0"] + recorded.COVERED:
        kind, size = cond.split("="); size = float(size)
        conds[cond] = recorded.measure(base, kind, size, lambda k, s, i: common.rng_for("R3REC", f"inj|{k}={s:g}", i))
    arm = {"conditions": conds}
    v = recorded.verdicts(arm, FA_LIMIT_PER_HOUR)
    return {"conditions": conds, "verdicts": {"AC-N1": v["AC-N1"], "AC-N4": v["AC-N4"]},
            "false_alarms_per_hour": conds["nominal=0"]["false_alarms_per_hour"], "logs": n_logs}


def predictions(res: dict) -> dict:
    """R3-P1 to R3-P9. res keys: S0, S1, R_held (detector name -> aggregate), R_all, nominal_held (calibrate output or None)."""
    mh, ma = res["R_held"]["M"], res["R_all"]["M"]
    out, why = {}, {}
    def put(k, v, note=""): out[k] = v; why[k] = note
    crit = ("AC-N1", "AC-N4")
    vr = {"AC-N1": mh["verdicts"]["AC-N1r"], "AC-N4": mh["verdicts"]["AC-N4"]}
    if None in vr.values(): put("R3-P1", None, "a recorded verdict is not defined on the held out set")
    else: put("R3-P1", any(res["S0"]["verdicts"][c] != vr[c] for c in crit))
    fr, f0, f1 = mh["false_alarms"]["per_hour"], res["S0"]["false_alarms_per_hour"], res["S1"]["false_alarms_per_hour"]
    put("R3-P2", None if fr is None or f0 is None else fr > f0)
    sp, ja = ma["session_detection"].get("spoofing"), ma["session_detection"].get("jamming")
    put("R3-P3", None if not sp or not ja or not sp["n"] or not ja["n"] else sp["rate"] < ja["rate"])
    put("R3-P4", None if None in (fr, f0, f1) else abs(f1 - fr) < abs(f0 - fr))
    if None in vr.values(): put("R3-P5", None, "a recorded verdict is not defined on the held out set")
    else: put("R3-P5", all(res["S1"]["verdicts"][c] == vr[c] for c in crit))
    ns = res.get("nominal_held")
    put("R3-P6", None if not ns else bool(ns["excess_kurtosis"] > 1.0 and ns["lag1_correlation"] > 0.3), "" if ns else "no held out still nominal segment")
    def share(name, types):
        k = n = 0
        for t in types:
            d = res["R_all"][name]["session_detection"].get(t)
            if d: k += d["k"]; n += d["n"]
        return (k / n) if n else None
    a, b = share("D-RX", ("spoofing", "meaconing")), share("M", ("spoofing", "meaconing"))
    put("R3-P7", None if a is None or b is None else a < b)
    a, b = share("D-JAM", ("meaconing",)), share("M", ("meaconing",))
    put("R3-P8", None if a is None or b is None else a < b)
    ok = [d for d, g in res["R_all"].items() if g["verdicts"]["AC-N1r"] and g["verdicts"]["AC-N4"]]
    put("R3-P9", len(ok) == 0, "detectors satisfying both: " + (", ".join(ok) or "none"))
    return {"held": out, "notes": {k: v for k, v in why.items() if v}}
