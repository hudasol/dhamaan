"""GL3: simulated sun sweep (synthetic camera glare model).

The camera looks along the robot heading, pitched down. Sun direction is set by elevation e and azimuth a
relative to the heading. A reflecting surface (polished floor or glazing, coefficient rho) adds a mirrored
sun below the horizon. Saturation fraction:

  s = clip(g(theta_direct) + rho * g(theta_reflected), 0, 1),  g(theta) = max(0, 1 - theta / halo)

with a seeded per frame flicker. Per frame detection probability within camera range is
p_clean * (1 - s) ** 2. A detection is confirmed by two consecutive positive frames.

Methods: B0 constant nominal speed; B1 constant slow speed; M nominal speed with a saturation monitor that
commands the slow speed when measured saturation exceeds s_g for two frames.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict

import numpy as np

from sim import acceptance, common

EXPERIMENT = "GL3"
ELEVATIONS = (5, 15, 30, 45, 60)
AZIMUTHS = (0, 30, 60, 90, 180)
RHOS = (0.0, 0.5)
METHODS = ("B0", "B1", "M")


@dataclass(frozen=True)
class Config:
    pitch_deg: float = 10.0        # camera pitched down
    halo_deg: float = 40.0
    flicker: float = 0.1           # s multiplied by U(1 - f, 1 + f) each frame
    p_clean: float = 0.95          # per frame detection probability without glare
    camera_range: float = 5.0      # m
    start_distance: float = 6.0    # m, to obstacle surface
    dt: float = 0.1                # s, frame period
    v_nominal: float = 0.8         # m/s
    v_slow: float = 0.3            # m/s
    decel: float = 1.0             # m/s2, used when slowing down
    s_g: float = acceptance.S_G    # saturation threshold of the monitor
    monitor_frames: int = 2
    monitor_noise: float = 0.03    # measurement noise on saturation
    confirm_frames: int = 2


def saturation(cfg: Config, e_deg: float, a_deg: float, rho: float) -> float:
    """Deterministic part of the saturation for one sun condition."""
    e, a, p = (math.radians(x) for x in (e_deg, a_deg, cfg.pitch_deg))
    axis = (math.cos(p), 0.0, -math.sin(p))
    def g(z):
        sun = (math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), z * math.sin(e))
        th = math.degrees(math.acos(max(-1.0, min(1.0, sum(u * w for u, w in zip(axis, sun))))))
        return max(0.0, 1.0 - th / cfg.halo_deg)
    return min(1.0, g(1.0) + rho * g(-1.0))


def run_one(cfg: Config, s0: float, method: str, rng: np.random.Generator, stop: common.Stopping) -> dict:
    v = cfg.v_slow if method == "B1" else cfg.v_nominal
    v_cmd, d, t, pos_run, hi_run, t_exceed, t_cmd = v, cfg.start_distance, 0.0, 0, 0, None, None
    while True:
        if d < stop.required(v):
            return {"outcome": "unsafe", "t_exceed": t_exceed, "t_cmd": t_cmd}
        s = min(1.0, max(0.0, s0 * rng.uniform(1 - cfg.flicker, 1 + cfg.flicker)))
        u, z = rng.random(), rng.standard_normal()
        if t_exceed is None and s > cfg.s_g: t_exceed = t
        hit = d <= cfg.camera_range and u < cfg.p_clean * (1 - s) ** 2
        pos_run = pos_run + 1 if hit else 0
        if pos_run >= cfg.confirm_frames:
            return {"outcome": "detected", "t_exceed": t_exceed, "t_cmd": t_cmd}
        if method == "M" and t_cmd is None:
            hi_run = hi_run + 1 if s + cfg.monitor_noise * z > cfg.s_g else 0
            if hi_run >= cfg.monitor_frames: v_cmd, t_cmd = cfg.v_slow, t
        d -= v * cfg.dt; t += cfg.dt
        if v > v_cmd: v = max(v_cmd, v - cfg.decel * cfg.dt)


def run(seeds: int = common.SEEDS_PER_CONDITION, cfg: Config = Config(), elevations=ELEVATIONS,
        azimuths=AZIMUTHS, rhos=RHOS) -> dict:
    stop = common.Stopping(); conds = {}
    for e in elevations:
        for a in azimuths:
            for rho in rhos:
                cond = f"e={e}|a={a}|rho={rho}"; s0 = saturation(cfg, e, a, rho)
                for m in METHODS:
                    runs = [run_one(cfg, s0, m, common.rng_for(EXPERIMENT, cond, i), stop) for i in range(seeds)]
                    exceeded = [r for r in runs if r["t_exceed"] is not None]
                    conds[f"{m}|{cond}"] = {
                        "method": m, "elevation_deg": e, "azimuth_deg": a, "rho": rho, "saturation_model": s0,
                        "detected_in_time": common.rate([r["outcome"] == "detected" for r in runs]),
                        "unsafe": common.rate([r["outcome"] == "unsafe" for r in runs]),
                        "slow_command": common.rate([r["t_cmd"] is not None for r in runs]),
                        "slow_command_runs_where_s_exceeded": common.rate([r["t_cmd"] is not None for r in exceeded]),
                        "slow_command_delay": common.mean_ci([r["t_cmd"] - r["t_exceed"] for r in exceeded if r["t_cmd"] is not None]),
                        "unsafe_seeds": [i for i, r in enumerate(runs) if r["outcome"] == "unsafe"],
                    }
    summary = {}
    for m in METHODS:
        mine = [c for c in conds.values() if c["method"] == m]
        summary[m] = {"conditions": len(mine),
                      "conditions_below_p_g": sum(c["detected_in_time"]["rate"] < acceptance.P_G for c in mine),
                      "max_unsafe_rate": max(c["unsafe"]["rate"] for c in mine)}
    return common.envelope(EXPERIMENT, ["GL3", "GL5 (software response only)"],
                           asdict(cfg) | {"elevations": list(elevations), "azimuths": list(azimuths), "rhos": list(rhos)},
                           conds, summary)
