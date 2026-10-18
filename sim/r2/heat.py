"""Heat items H1 to H6: a simple thermal derating model (compute, battery, sensor drift).

Every parameter below is "assumed, proposal" unless marked otherwise: nothing was measured, and no row of the
evidence table fixes a heat severity or a component limit (protocol section 4). The only externally sourced
figure is the rated ambient of an example platform, 45 degC, as stated in the README of the related dhill
repository (https://github.com/hudasol/dhill, read, not copied; no licence selected there). It is used only to
place the hottest condition above a rated ambient; the model itself is not taken from dhill.

Each component follows a first order thermal model,
  dT/dt = (T_amb + solar * g + P(scale) * R - T) / tau,
for a two hour mission starting near the daily peak. A run's true parameters are the nominal ones perturbed by
seeded lognormal factors; the ambient carries a seeded forecast error.

Methods: B0 full scale throughout; B1 a fixed rule (park the whole mission when the forecast peak reaches
40 degC); M a predictive derating controller that every minute picks the largest scale whose predicted
temperatures over the next 30 minutes stay at least M_H below every limit, otherwise parks (scale 0, in place,
no shade assumed).
H1 envelope: the condition grid. H2 limit register: LIMITS. H3 prediction before test: AC-H1. H4 safety
function at heat: AC-H2. H5 limit response: AC-H3. H6 restart after a sun soak: first move time.
"""
from __future__ import annotations

import math

import numpy as np

from sim import common
from sim.r2 import acceptance_r2 as A2, base

EXPERIMENT = "HEAT"
RATED_AMBIENT_EXAMPLE = 45.0   # degC, example platform rating stated in the dhill README (cited by link)

# component: (power at scale 0, power at full scale, exponent, R K/W, tau s, solar gain K, hard limit degC)
COMPONENTS = {
    "compute": (15.0, 50.0, 1.0, 0.9, 600.0, 8.0, 85.0),
    "battery": (2.0, 20.0, 2.0, 1.2, 2400.0, 12.0, 60.0),
    "lidar":   (8.0, 8.0, 1.0, 1.5, 900.0, 15.0, 65.0),
}
ASSUMED_NOTE = {"components": base.ASSUMED, "lidar_bias_m_per_k": base.ASSUMED, "ambient_profile": base.ASSUMED,
                "uncertainty": base.ASSUMED, "rated_ambient_example": "dhill README, cited by link"}
LIDAR_BIAS = 0.002          # m per K above 25 degC (assumed, proposal)
DT, MISSION, HORIZON, DECIDE = 10.0, 7200.0, 1800.0, 60.0
SCALES = (1.0, 0.8, 0.6, 0.4, 0.2, 0.0)
PEAKS = (35, 40, 45, 50)
SUN = ("shade", "sun")
START = ("normal", "soak")
METHODS = ("B0", "B1", "M")
RULE_AMBIENT = 40.0          # degC, fixed rule of B1 (assumed, proposal)
SD_PARAM, SD_SOLAR, SD_AMB, SD_MEAS = 0.15, 0.2, 1.5, 0.5


def power(c, scale):
    p0, p1, e, *_ = COMPONENTS[c]
    return p0 + (p1 - p0) * scale ** e


def ambient(peak: float, t: float) -> float:
    return peak - 2.0 + 2.0 * min(t, MISSION) / MISSION


def draw(rng) -> dict:
    """True parameter factors for one run; the same draws for every method."""
    f = {c: (math.exp(SD_PARAM * rng.standard_normal()), math.exp(SD_PARAM * rng.standard_normal()),
             math.exp(SD_SOLAR * rng.standard_normal())) for c in COMPONENTS}
    return {"f": f, "amb_err": SD_AMB * rng.standard_normal(), "meas": rng.standard_normal((int(MISSION / DT) + 1, len(COMPONENTS)))}


def equilibrium(c, amb, sun, scale, fR=1.0, fG=1.0):
    *_, R, tau, g, lim = COMPONENTS[c]
    return amb + (g * fG if sun else 0.0) + power(c, scale) * R * fR


def initial(c, amb, sun, start, fR=1.0, fG=1.0):
    if start == "soak": return equilibrium(c, amb, True, 0.0, fR, fG) + 5.0   # parked in sun before the mission
    return equilibrium(c, amb, False, 0.0, fR, fG)


def predict_max(c, T0, amb, sun, scale, horizon=HORIZON):
    """Nominal model, constant inputs over the horizon: first order response, maximum over the horizon."""
    *_, R, tau, g, lim = COMPONENTS[c]
    teq = equilibrium(c, amb, sun, scale)
    return max(T0, teq + (T0 - teq) * math.exp(-horizon / tau))


def controller(method, temps, t, peak, sun):
    if method == "B0": return 1.0
    if method == "B1": return 0.0 if ambient(peak, MISSION) >= RULE_AMBIENT else 1.0
    amb = ambient(peak, t + HORIZON)
    for s in SCALES:
        if all(predict_max(c, temps[i], amb, sun, s) <= COMPONENTS[c][6] - A2.M_H for i, c in enumerate(COMPONENTS)):
            return s
    return 0.0


def run_one(peak, sun_s, start, method, p) -> dict:
    sun = sun_s == "sun"
    T = np.array([initial(c, ambient(peak, 0) + p["amb_err"], sun, start, p["f"][c][0], p["f"][c][2]) for c in COMPONENTS])
    scale, scales, first_move, exceed, tmax = 0.0, [], None, False, T.copy()
    for k in range(int(MISSION / DT)):
        t = k * DT
        if k % int(DECIDE / DT) == 0:
            meas = T + SD_MEAS * p["meas"][k]
            scale = controller(method, meas, t, peak, sun)
        if scale > 0 and first_move is None: first_move = t / 60.0
        scales.append(scale)
        amb = ambient(peak, t) + p["amb_err"]
        for i, c in enumerate(COMPONENTS):
            fR, ftau, fG = p["f"][c]
            *_, R, tau, g, lim = COMPONENTS[c]
            teq = amb + (g * fG if sun else 0.0) + power(c, scale) * R * fR
            T[i] = teq + (T[i] - teq) * math.exp(-DT / (tau * ftau))
            exceed = exceed or T[i] > lim
        tmax = np.maximum(tmax, T)
    return {"exceed": bool(exceed), "productivity": float(np.mean(scales)), "first_move_min": first_move,
            "tmax": {c: float(tmax[i]) for i, c in enumerate(COMPONENTS)}}


def open_loop_error(peak, sun_s, start, p) -> dict:
    """H3 / AC-H1: nominal prediction of the full scale mission maximum versus the true maximum."""
    sun = sun_s == "sun"; out = {}
    truth = run_one(peak, sun_s, start, "B0", p)["tmax"]
    for c in COMPONENTS:
        T0 = initial(c, ambient(peak, 0), sun, start)
        out[c] = predict_max(c, T0, ambient(peak, MISSION), sun, 1.0, MISSION) - truth[c]
    return out


def required_factor(lidar_max: float) -> float:
    """H4 / AC-H2: factor on the required stopping distance from LiDAR range bias at the run's peak temperature."""
    st = common.Stopping(); req = st.required(0.8)
    return (req + LIDAR_BIAS * max(0.0, lidar_max - 25.0)) / req


def score(seeds: int = base.SEEDS) -> dict:
    conds = {}
    for peak in PEAKS:
        for sun in SUN:
            for start in START:
                cond = f"peak={peak}|{sun}|{start}"
                params = [draw(base.rng(base.HELDOUT_SEED, EXPERIMENT, cond, i)) for i in range(seeds)]
                errs = [open_loop_error(peak, sun, start, p) for p in params]
                conds[f"model|{cond}"] = {"method": "model", "peak": peak, "sun": sun, "start": start} | {
                    f"within_t_h_{c}": common.rate([abs(e[c]) <= A2.T_H for e in errs]) for c in COMPONENTS} | {
                    f"abs_error_{c}": common.mean_ci([abs(e[c]) for e in errs]) for c in COMPONENTS}
                for m in METHODS:
                    runs = [run_one(peak, sun, start, m, p) for p in params]
                    conds[f"{m}|{cond}"] = {
                        "method": m, "peak": peak, "sun": sun, "start": start,
                        "exceed": common.rate([r["exceed"] for r in runs]),
                        "productivity": common.mean_ci([r["productivity"] for r in runs]),
                        "first_move_min": common.mean_ci([r["first_move_min"] for r in runs]),
                        "never_moved": common.rate([r["first_move_min"] is None for r in runs]),
                        "stop_factor": common.mean_ci([required_factor(r["tmax"]["lidar"]) for r in runs])} | {
                        f"tmax_{c}": common.mean_ci([r["tmax"][c] for r in runs]) for c in COMPONENTS}
    summary = {m: {"conditions_with_exceedance": sum(c["exceed"]["k"] > 0 for c in conds.values() if c["method"] == m)}
               for m in METHODS}
    cfg = {"components": {c: dict(zip(("p0_w", "p1_w", "exponent", "r_k_per_w", "tau_s", "solar_gain_k", "limit_degc"), v))
                          for c, v in COMPONENTS.items()},
           "lidar_bias_m_per_k": LIDAR_BIAS, "mission_s": MISSION, "dt_s": DT, "horizon_s": HORIZON, "decide_s": DECIDE,
           "scales": list(SCALES), "rule_ambient_degc": RULE_AMBIENT, "rated_ambient_example_degc": RATED_AMBIENT_EXAMPLE,
           "sd": {"param": SD_PARAM, "solar": SD_SOLAR, "ambient": SD_AMB, "measurement": SD_MEAS},
           "provenance": ASSUMED_NOTE}
    return base.envelope(EXPERIMENT, ["H1", "H2", "H3", "H4", "H5", "H6"], "held out", cfg, conds, summary)
