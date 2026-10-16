"""N2 to N4: measurement level GNSS fault injection (software only; no RF generation of any kind).

A robot drives a straight outdoor approach at constant speed. A 2D Kalman filter fuses wheel odometry
(10 Hz, with seeded scale bias, speed noise and heading random walk) with GNSS position fixes (1 Hz, white
noise). From t_onset one fault is applied to the fix stream:

  loss     no fixes
  noise    fix noise sigma grows linearly to sigma_end over ramp_s, then stays
  jump     constant offset of size J in a seeded direction
  drift    offset growing at rate r (m/s) in a seeded direction
  replay   each fix is the genuine fix recorded D seconds earlier (a synthetic recorded track, labelled
           simulated; no public log is used, see sim/DEVIATIONS.md)

Methods: B0 accepts every fix; B1 rejects single fixes by an innovation gate (common practice);
M adds fault declaration: three consecutive gate rejections, a CUSUM on the normalised innovation, or a
fix timeout. On declaration M brakes to a stop (the declared safe state) on odometry only.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict

import numpy as np

from sim import acceptance, common

EXPERIMENT = "GNSS"
CONDITIONS = [("nominal", 0.0), ("loss", 0.0), ("noise", 3.0), ("noise", 5.0), ("noise", 10.0),
              ("jump", 2.0), ("jump", 5.0), ("jump", 10.0), ("jump", 20.0),
              ("drift", 0.05), ("drift", 0.1), ("drift", 0.2), ("drift", 0.5),
              ("replay", 2.0), ("replay", 5.0), ("replay", 10.0)]
METHODS = ("B0", "B1", "M")


@dataclass(frozen=True)
class Config:
    duration: float = 120.0     # s
    dt: float = 0.1             # s, odometry step
    fix_period_steps: int = 10  # 1 Hz fixes
    t_onset: float = 30.0       # s
    speed: float = 0.8          # m/s
    sigma_gnss: float = 1.0     # m per axis
    odo_scale_sd: float = 0.01  # per run scale bias
    odo_speed_sd: float = 0.02  # m/s per step
    heading_rw: float = 0.001   # rad per sqrt(s)
    q_step: float = 0.01        # m, filter process noise per step and axis
    gate: float = 13.82         # chi-square, 2 dof, 0.999
    reject_run: int = 3
    cusum_bias: float = 3.0
    cusum_limit: float = 25.0
    timeout: float = 3.0        # s without a fix
    decel: float = 1.0          # m/s2 while stopping
    noise_ramp: float = 20.0    # s


def run_one(cfg: Config, kind: str, size: float, method: str, rng: np.random.Generator) -> dict:
    n = int(round(cfg.duration / cfg.dt)); per = cfg.fix_period_steps
    # all random draws first, so every method sees the same world
    scale = 1 + cfg.odo_scale_sd * rng.standard_normal()
    vnoise = cfg.odo_speed_sd * rng.standard_normal(n)
    hdg = np.cumsum(cfg.heading_rw * math.sqrt(cfg.dt) * rng.standard_normal(n))
    fix_noise = rng.standard_normal((n // per + 1, 2))
    phi = rng.uniform(0, 2 * math.pi); u = np.array([math.cos(phi), math.sin(phi)])
    R = cfg.sigma_gnss ** 2; Q = cfg.q_step ** 2
    xt = np.zeros(2); xh = np.zeros(2); P = 0.5; v = cfg.speed
    truth_at_fix = []
    g = 0.0; rejects = 0; last_fix_t = 0.0; t_alarm = None; stopped_at = None
    max_err = 0.0; err_alarm = None
    for i in range(n):
        t = i * cfg.dt
        if t_alarm is not None:                 # braking to the safe state on odometry only
            v = max(0.0, v - cfg.decel * cfg.dt)
        step_true = v * cfg.dt
        xt = xt + np.array([step_true, 0.0])
        vm = v * scale + (vnoise[i] if v > 0 else 0.0)
        xh = xh + vm * cfg.dt * np.array([math.cos(hdg[i]), math.sin(hdg[i])]); P += Q
        if t >= cfg.t_onset: max_err = max(max_err, float(np.linalg.norm(xh - xt)))
        if t_alarm is not None and v == 0.0:
            stopped_at = t; break
        if (i + 1) % per or t_alarm is not None: continue   # after declaration: odometry only
        j = (i + 1) // per; tf = t + cfg.dt
        truth_at_fix.append(xt.copy())
        genuine = xt + cfg.sigma_gnss * fix_noise[j]
        z = genuine
        if tf >= cfg.t_onset and kind != "nominal":
            age = tf - cfg.t_onset
            if kind == "loss": z = None
            elif kind == "noise":
                sig = cfg.sigma_gnss + (size - cfg.sigma_gnss) * min(age / cfg.noise_ramp, 1.0)
                z = xt + sig * fix_noise[j]
            elif kind == "jump": z = genuine + size * u
            elif kind == "drift": z = genuine + size * age * u
            elif kind == "replay":
                back = int(round(size)); z = truth_at_fix[j - 1 - back] + cfg.sigma_gnss * fix_noise[j - back]
        if z is None:
            if method == "M" and t_alarm is None and tf - last_fix_t > cfg.timeout: t_alarm = tf
        else:
            last_fix_t = tf
            nu = z - xh; S = P + R; nis = float(nu @ nu) / S
            accept = method == "B0" or nis <= cfg.gate
            if accept:
                K = P / S; xh = xh + K * nu; P = (1 - K) * P; rejects = 0
            else:
                rejects += 1
            if method == "M" and t_alarm is None:
                g = max(0.0, g + nis - cfg.cusum_bias)
                if rejects >= cfg.reject_run or g > cfg.cusum_limit: t_alarm = tf
        if t_alarm is not None and err_alarm is None: err_alarm = float(np.linalg.norm(xh - xt))
    err_stop = float(np.linalg.norm(xh - xt)) if stopped_at is not None else None
    return {"t_alarm": t_alarm, "err_alarm": err_alarm, "err_stop": err_stop, "max_err": max_err}


def run(seeds: int = common.SEEDS_PER_CONDITION, cfg: Config = Config(), conditions=CONDITIONS) -> dict:
    conds = {}
    for kind, size in conditions:
        cond = f"{kind}={size:g}"
        for m in METHODS:
            runs = [run_one(cfg, kind, size, m, common.rng_for(EXPERIMENT, cond, i)) for i in range(seeds)]
            on = cfg.t_onset
            false_alarm = [r["t_alarm"] is not None and (kind == "nominal" or r["t_alarm"] < on) for r in runs]
            delays = [r["t_alarm"] - on if r["t_alarm"] is not None and r["t_alarm"] >= on else None for r in runs]
            det_tn = [d is not None and d <= acceptance.T_N for d in delays]
            detected = [r for r, d in zip(runs, delays) if d is not None]
            conds[f"{m}|{cond}"] = {
                "method": m, "fault": kind, "size": size,
                "false_alarm": common.rate(false_alarm),
                "detected": common.rate([d is not None for d in delays]) if kind != "nominal" else None,
                "detected_within_t_n": common.rate(det_tn) if kind != "nominal" else None,
                "detection_delay": common.mean_ci(delays),
                "error_at_detection": common.mean_ci([r["err_alarm"] for r in detected]),
                "error_at_stop": common.mean_ci([r["err_stop"] for r in detected]),
                "max_error_after_onset": common.mean_ci([r["max_err"] for r in runs]),
                "error_exceeds_l_n": common.rate([r["max_err"] > acceptance.L_N for r in runs]),
                "missed_seeds": [i for i, d in enumerate(delays) if d is None] if kind != "nominal" else [],
            }
    summary = {m: {"false_alarm_nominal": conds[f"{m}|nominal=0"]["false_alarm"]["rate"]} for m in METHODS}
    return common.envelope(EXPERIMENT, ["N2", "N3", "N4 (synthetic replay only)"],
                           asdict(cfg) | {"conditions": [f"{k}={s:g}" for k, s in conditions]}, conds, summary)
