"""DU3 round 2: the monitor threshold and the degradation bound set together.

The world, sensor and detector are the round 1 model (sim/du3_lidar.py, unchanged). Each run is simulated
once at the nominal speed with the detector alone, recording the valid return ratio of every scan. Because the
monitor does not change the world until it stops the robot, any monitor (threshold h, consecutive scans n)
can then be evaluated on the same recorded run: it stops at the first scan that completes n low ratio scans,
if that comes before detection or the unsafe point.
"""
from __future__ import annotations

from dataclasses import asdict

import numpy as np

from sim import acceptance as A, common, du3_lidar as D
from sim.r2 import acceptance_r2 as A2, base

EXPERIMENT = "DU3R2"


def record(cfg: D.Config, k: float, rng, stop: common.Stopping) -> dict:
    th = np.deg2rad(np.arange(-cfg.fov_deg, cfg.fov_deg + 1e-9, cfg.step_deg)); n = th.size
    c, s = np.cos(th), np.sin(th)
    with np.errstate(divide="ignore"):
        r_wall = np.where(np.abs(s) > 1e-9, cfg.half_width / np.abs(s), np.inf)
    expected = r_wall <= cfg.r0
    oy = rng.uniform(-cfg.lateral_offset, cfg.lateral_offset)
    v = cfg.v_nominal; x, t, pos_run, vrr, times = 0.0, 0.0, 0, [], []
    while True:
        d = cfg.start_distance - x - cfg.obstacle_radius
        if d < stop.required(v): return {"end": "unsafe", "vrr": vrr, "t": times}
        ke = k if t >= cfg.t_onset else 0.0
        dx = cfg.start_distance - x
        b = c * dx + s * oy; disc = b * b - (dx * dx + oy * oy - cfg.obstacle_radius ** 2)
        r_obs = np.where((disc >= 0) & (b > 0), b - np.sqrt(np.maximum(disc, 0.0)), np.inf)
        r_true = np.minimum(r_wall, r_obs)
        u1, u2, z = rng.random(n), rng.random(n), rng.standard_normal(n)
        keep = (r_true <= cfg.r0 * (1 - cfg.range_loss * ke)) & (u1 >= cfg.drop * ke) & (u2 >= ke * np.minimum(r_true / cfg.r0, 1.0))
        r = np.where(np.isfinite(r_true), r_true, 0.0) + (cfg.sigma0 + cfg.noise_gain * ke) * z
        cand = keep & (np.abs(r * s) <= cfg.footprint) & (r * c > 0)
        vrr.append(float(keep[expected].mean())); times.append(t - cfg.t_onset)
        pos_run = pos_run + 1 if cand.sum() >= cfg.min_points else 0
        if pos_run >= cfg.confirm_scans: return {"end": "detected", "vrr": vrr, "t": times}
        x += v * cfg.dt; t += cfg.dt


def monitor_stop(run: dict, h: float, n: int) -> float | None:
    """Time after onset at which a monitor (h, n) would stop the robot on this recorded run, or None."""
    low = 0
    for v, t in zip(run["vrr"], run["t"]):
        low = low + 1 if v < h else 0
        if low >= n: return t
    return None


def simulate(seed_set: int, seeds: int = base.SEEDS) -> dict:
    cfg, stop = D.Config(), common.Stopping()
    return {k: [record(cfg, k, base.rng(seed_set, EXPERIMENT, f"k={k:.1f}", i), stop) for i in range(seeds)] for k in D.LEVELS}


def violations(runs: dict, h: float, n: int, bound: float) -> dict:
    """Runs breaking AC-DU1R2 (at or below the bound: detector misses or the monitor stops) or AC-DU2R2
    (above the bound: the monitor does not stop within T_D of onset)."""
    below = above = 0
    for k, rs in runs.items():
        for r in rs:
            st = monitor_stop(r, h, n)
            if k <= bound + 1e-9: below += (r["end"] != "detected") or (st is not None)
            else: above += st is None or st > A.T_D + 1e-9
    return {"below": int(below), "above": int(above), "total": int(below + above)}


def design(seeds: int = base.SEEDS) -> dict:
    """Development seed set only. Largest feasible bound; ties go to fewer scans, then the higher threshold.
    If nothing is feasible, the fewest violating runs, then the largest bound."""
    runs = simulate(base.DEV_SEED, seeds)
    table = [{"threshold": h, "scans": n, "bound": b} | violations(runs, h, n, b)
             for h in A2.DU_THRESHOLDS for n in A2.DU_SCANS for b in A2.DU_BOUNDS]
    ok = [t for t in table if t["total"] == 0]
    if ok: pick = sorted(ok, key=lambda t: (-t["bound"], t["scans"], -t["threshold"]))[0]
    else: pick = sorted(table, key=lambda t: (t["total"], -t["bound"], t["scans"], -t["threshold"]))[0]
    return {"grid_size": len(table), "feasible_count": len(ok),
            "chosen": {"threshold": pick["threshold"], "scans": pick["scans"], "bound": pick["bound"], "feasible": bool(ok),
                       "dev_violations": pick["total"]},
            "best_per_threshold": [min((t for t in table if t["threshold"] == h), key=lambda t: (t["total"], -t["bound"]))
                                   for h in A2.DU_THRESHOLDS]}


def score(chosen: dict, seeds: int = base.SEEDS) -> dict:
    """Held out seed set: the round 1 pair (0.6, 3 scans, bound 0.4) and the chosen pair, on the same runs."""
    runs = simulate(base.HELDOUT_SEED, seeds)
    pairs = {"M": (0.6, D.Config().vrr_scans, A.B_D), "M2": (chosen["threshold"], chosen["scans"], chosen["bound"])}
    conds = {}
    for name, (h, n, b) in pairs.items():
        for k, rs in runs.items():
            stops = [monitor_stop(r, h, n) for r in rs]
            conds[f"{name}|k={k:.1f}"] = {
                "method": name, "k": k, "threshold": h, "scans": n, "bound": b,
                "detector_in_time": common.rate([r["end"] == "detected" for r in rs]),
                "monitor_stop": common.rate([s is not None for s in stops]),
                "stop_within_t_d": common.rate([s is not None and s <= A.T_D + 1e-9 for s in stops]),
                "stop_time_after_onset": common.mean_ci([s for s in stops if s is not None])}
    summary = {name: violations(runs, *pairs[name]) for name in pairs}
    return base.envelope(EXPERIMENT, ["DU3", "DU5 (software monitor only)"], "held out",
                         asdict(D.Config()) | {"chosen": chosen, "t_d": A.T_D}, conds, summary)
