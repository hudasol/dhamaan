"""Part C harness: synthetic against recorded GNSS logs (docs/PREREG_R3_DRAFT.md section 4).

Everything here is exercised in the tests on SYNTHETIC fixtures only. No recorded log has been replayed. The runner
(sim/r3/run_recorded.py) refuses to run until a registration identifier and a licensed data set are entered.

A recording is a pair (gnss rows, odometry rows) in the pilot kit format (sim/r2/replay.py) with reference columns,
and optionally an `interference` column on the fix rows (1.0 inside a labelled interference interval, else 0.0).
Arms: S0 the synthetic generator of rounds 1 and 2; S1 the same model recalibrated on calibration recordings
(time correlated, heavy tailed fix error); R recorded nominal segments with faults injected at measurement level
(semi synthetic) and, where labelled, natural interference intervals.
"""
from __future__ import annotations

import math, random

import numpy as np

from sim import acceptance as A, common, gnss_n2n4 as G
from sim.r2 import replay

COVERED = ["loss=0", "noise=5", "noise=10", "jump=5", "jump=10", "jump=20", "drift=0.2", "drift=0.5", "replay=5", "replay=10"]


def split_recordings(ids: list[str], seed: int, n_calibration: int) -> tuple[list[str], list[str]]:
    """Seeded draw before any metric is computed. A recording is never split across the two sets."""
    ids = sorted(ids)
    if not 0 < n_calibration < len(ids): raise ValueError("need at least one recording on each side")
    cal = sorted(random.Random(seed).sample(ids, n_calibration))
    return cal, [i for i in ids if i not in cal]


def nominal_errors(gnss: list[dict]) -> np.ndarray:
    """Fix error against the reference on rows that are not labelled as interference."""
    rows = [r for r in gnss if r.get("x_ref_m") is not None and not (r.get("interference") or 0.0) and r.get("fix_ok", 1.0)]
    return np.array([[r["x_m"] - r["x_ref_m"], r["y_m"] - r["y_ref_m"]] for r in rows])


def calibrate(recordings: list[tuple[list[dict], list[dict]]]) -> dict:
    """Standard deviation, lag 1 correlation and excess kurtosis of the nominal fix error, from calibration recordings only."""
    errs = [nominal_errors(g) for g, _ in recordings]
    errs = [e for e in errs if len(e) > 3]
    if not errs: raise ValueError("no nominal fix error in the calibration recordings")
    allv = np.concatenate([e.ravel() for e in errs])
    sd = float(allv.std())
    num = sum(float(((e[1:] - e[1:].mean(0)) * (e[:-1] - e[:-1].mean(0))).sum()) for e in errs)
    den = sum(float(((e[:-1] - e[:-1].mean(0)) ** 2).sum()) for e in errs)
    rho = max(-0.99, min(0.99, num / den if den else 0.0))
    kurt = float(((allv - allv.mean()) ** 4).mean() / (allv.var() ** 2) - 3.0) if allv.var() > 0 else 0.0
    return {"sigma_m": sd, "lag1_correlation": rho, "excess_kurtosis": kurt, "fixes_used": int(len(allv) // 2)}


def s1_standin(rng: np.random.Generator, cal: dict, cfg: G.Config = G.Config()) -> tuple[list[dict], list[dict]]:
    """Round 1 stand in log with the fix error replaced by an AR(1) process of the calibrated sigma and correlation, heavy tailed if the
    calibration shows excess kurtosis (Student t with degrees of freedom from kurtosis = 6 / (df - 4))."""
    g, o = replay.standin(rng, cfg)
    k = cal["excess_kurtosis"]; df = (6.0 / k + 4.0) if k > 0.1 else None
    rho, sd = cal["lag1_correlation"], cal["sigma_m"]
    e = np.zeros(2)
    for r in g:
        z = rng.standard_normal(2) if df is None else rng.standard_t(df, 2) * math.sqrt((df - 2) / df if df > 2 else 1.0)
        e = rho * e + math.sqrt(1 - rho * rho) * z
        r["x_m"] = r["x_ref_m"] + sd * e[0]; r["y_m"] = r["y_ref_m"] + sd * e[1]
    return g, o


def measure(logs: list[tuple[list[dict], list[dict]]], kind: str, size: float, rng_for, cfg: G.Config = G.Config()) -> dict:
    """Run the monitor over logs with one fault injected (or none for kind nominal); same measures as round 2, plus exposure for false alarms."""
    res, exposure = [], 0.0
    for i, (g, o) in enumerate(logs):
        gi = replay.inject(g, kind, size, cfg.t_onset, rng_for(kind, size, i)) if kind != "nominal" else g
        r = replay.score_log(gi, o, cfg); res.append(r)
        if kind == "nominal": exposure += (r["t_alarm"] if r["t_alarm"] is not None else o[-1]["t_s"]) / 3600.0
    on = cfg.t_onset
    delays = [r["t_alarm"] - on if r["t_alarm"] is not None and r["t_alarm"] >= on else None for r in res]
    out = {"n": len(res), "detected_within_t_n": common.rate([d is not None and d <= A.T_N for d in delays]) if kind != "nominal" else None,
           "mean_delay_s": common.mean_ci(delays)["mean"], "error_at_alarm_max_m": common.mean_ci([r["error_at_alarm_m"] for r in res])["max"]}
    if kind == "nominal":
        alarms = sum(r["t_alarm"] is not None for r in res)
        out |= {"false_alarms": alarms, "exposure_hours": exposure, "false_alarms_per_hour": alarms / exposure if exposure else None}
    return out


def verdicts(arm: dict, fa_limit_per_hour: float) -> dict:
    """AC-N1 (covered faults found within T_N in at least Q_N of runs), AC-N2 (error at alarm within L_N), AC-N4 (false alarm rate)."""
    c = arm["conditions"]
    n1 = all(c[k]["detected_within_t_n"]["rate"] >= A.Q_N for k in COVERED)
    n2 = all((c[k]["error_at_alarm_max_m"] or 0.0) <= A.L_N for k in c if k != "nominal=0")
    fa = c["nominal=0"]["false_alarms_per_hour"]
    return {"AC-N1": n1, "AC-N2": n2, "AC-N4": fa is not None and fa <= fa_limit_per_hour}


def score_predictions(res: dict) -> dict:
    """R3-P1 to R3-P6 from the result structure, by script. res has arms S0 and S1 and R on calibration (cal) and held out (held) recordings."""
    v = {k: verdicts(res[k], res["fa_limit_per_hour"]) for k in ("S0_held", "S1_held", "R_held", "S0_cal", "R_cal")}
    crit = ("AC-N1", "AC-N2", "AC-N4")
    differ = [c for c in crit if v["S0_held"][c] != v["R_held"][c]]
    fa = lambda k: res[k]["conditions"]["nominal=0"]["false_alarms_per_hour"]
    dl = lambda k: res[k]["conditions"]["drift=0.2"]["mean_delay_s"]
    out = {"R3-P1": bool(differ),
           "R3-P2": fa("R_held") is not None and fa("S0_held") is not None and fa("R_held") > fa("S0_held"),
           "R3-P3": dl("R_held") is not None and dl("S0_held") is not None and dl("R_held") > dl("S0_held"),
           "R3-P4": all(v["S1_held"][c] == v["R_held"][c] for c in differ),
           "R3-P5": all(v["S1_held"][c] == v["R_held"][c] for c in crit),
           "R3-P6": all(v["S0_cal"][c] == v["S0_held"][c] for c in crit)}
    return {"verdicts": v, "criteria_that_differ_between_S0_and_R": differ, "predictions_held": out}
