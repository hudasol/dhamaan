"""DU3: sensor degradation sweep (synthetic 2D LiDAR in a corridor, dust modelled in software).

World: a straight corridor (walls at +/- half_width), a standard test cylinder ahead of the robot with a
seeded lateral offset. The robot drives at constant speed until it confirms the obstacle, its monitor
stops it, or it passes the required stopping distance (unsafe).

Degradation of severity k in [0, 1], applied from t_onset (software only):
  range loss    usable range R0 * (1 - range_loss * k)
  dropped       each return dropped with probability drop * k
  haze          extra loss growing with range: probability k * min(r / R0, 1)
  noise         range noise sigma0 + noise_gain * k

Methods: B0 detector only; B1 detector only at a fixed low speed; M detector plus a map based
valid return ratio monitor that stops the robot when the ratio stays below a threshold.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np

from sim import common

EXPERIMENT = "DU3"
LEVELS = [round(0.1 * i, 1) for i in range(11)]
METHODS = ("B0", "B1", "M")


@dataclass(frozen=True)
class Config:
    fov_deg: float = 30.0          # beams from -fov to +fov
    step_deg: float = 1.0
    r0: float = 10.0               # m, clean maximum range
    half_width: float = 1.2        # m, corridor half width
    obstacle_radius: float = 0.15  # m, standard test cylinder (synthetic)
    lateral_offset: float = 0.2    # m, obstacle offset drawn from U(-x, x)
    start_distance: float = 12.0   # m, robot to obstacle centre at t = 0
    footprint: float = 0.4         # m, half width of the swept path checked for obstacles
    sigma0: float = 0.01           # m
    range_loss: float = 0.95
    drop: float = 0.6
    noise_gain: float = 0.08
    dt: float = 0.1                # s, scan period
    t_onset: float = 0.5           # s, degradation starts
    v_nominal: float = 0.8         # m/s
    v_slow: float = 0.4            # m/s, method B1
    min_points: int = 2            # obstacle points in one scan
    confirm_scans: int = 2         # consecutive positive scans to confirm
    vrr_threshold: float = 0.6     # method M
    vrr_scans: int = 3             # consecutive low ratio scans to stop


def run_one(cfg: Config, k: float, method: str, rng: np.random.Generator, stop: common.Stopping) -> dict:
    th = np.deg2rad(np.arange(-cfg.fov_deg, cfg.fov_deg + 1e-9, cfg.step_deg)); n = th.size
    c, s = np.cos(th), np.sin(th)
    with np.errstate(divide="ignore"):
        r_wall = np.where(np.abs(s) > 1e-9, cfg.half_width / np.abs(s), np.inf)
    expected = r_wall <= cfg.r0
    oy = rng.uniform(-cfg.lateral_offset, cfg.lateral_offset)
    v = cfg.v_slow if method == "B1" else cfg.v_nominal
    x, t, pos_run, low_run = 0.0, 0.0, 0, 0
    while True:
        d = cfg.start_distance - x - cfg.obstacle_radius
        if d < stop.required(v):
            return {"outcome": "unsafe", "distance": d, "t_after_onset": t - cfg.t_onset}
        ke = k if t >= cfg.t_onset else 0.0
        dx = cfg.start_distance - x
        b = c * dx + s * oy; disc = b * b - (dx * dx + oy * oy - cfg.obstacle_radius ** 2)
        r_obs = np.where((disc >= 0) & (b > 0), b - np.sqrt(np.maximum(disc, 0.0)), np.inf)
        r_true = np.minimum(r_wall, r_obs)
        u1, u2, z = rng.random(n), rng.random(n), rng.standard_normal(n)
        keep = (r_true <= cfg.r0 * (1 - cfg.range_loss * ke)) & (u1 >= cfg.drop * ke) \
            & (u2 >= ke * np.minimum(r_true / cfg.r0, 1.0))
        r = np.where(np.isfinite(r_true), r_true, 0.0) + (cfg.sigma0 + cfg.noise_gain * ke) * z  # no return: 0, masked by keep
        cand = keep & (np.abs(r * s) <= cfg.footprint) & (r * c > 0)
        pos_run = pos_run + 1 if cand.sum() >= cfg.min_points else 0
        if pos_run >= cfg.confirm_scans:
            return {"outcome": "detected", "distance": d, "t_after_onset": t - cfg.t_onset}
        if method == "M":
            vrr = keep[expected].mean()
            low_run = low_run + 1 if vrr < cfg.vrr_threshold else 0
            if low_run >= cfg.vrr_scans:
                return {"outcome": "monitor_stop", "distance": d, "t_after_onset": t - cfg.t_onset}
        x += v * cfg.dt; t += cfg.dt


def run(seeds: int = common.SEEDS_PER_CONDITION, levels=LEVELS, cfg: Config = Config()) -> dict:
    stop = common.Stopping(); conds = {}
    for k in levels:
        for m in METHODS:
            runs = [run_one(cfg, k, m, common.rng_for(EXPERIMENT, f"k={k:.1f}", i), stop) for i in range(seeds)]
            v = cfg.v_slow if m == "B1" else cfg.v_nominal
            det_in_time = [r["outcome"] == "detected" for r in runs]
            stops = [r for r in runs if r["outcome"] == "monitor_stop"]
            conds[f"{m}|k={k:.1f}"] = {
                "method": m, "k": k, "speed": v, "required_distance": stop.required(v),
                "unsafe": common.rate([r["outcome"] == "unsafe" for r in runs]),
                "detected_in_time": common.rate(det_in_time),
                "monitor_stop": common.rate([r["outcome"] == "monitor_stop" for r in runs]),
                "detection_distance": common.mean_ci([r["distance"] for r in runs if r["outcome"] == "detected"]),
                "stop_time_after_onset": common.mean_ci([r["t_after_onset"] for r in stops]),
                "unsafe_seeds": [i for i, r in enumerate(runs) if r["outcome"] == "unsafe"],
            }
    summary = {m: {"max_unsafe_rate": max(conds[f"{m}|k={k:.1f}"]["unsafe"]["rate"] for k in levels)} for m in METHODS}
    return common.envelope(EXPERIMENT, ["DU3", "DU5 (software monitor only)"], asdict(cfg) | {"levels": list(levels)}, conds, summary)
