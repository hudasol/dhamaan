"""Register of assumed parameters, read from the code by introspection (not typed by hand).

A parameter is a field of a Config class, a module constant of the acceptance files, a heat model constant or a
heat component entry. Names in EXCLUDED are structural (time steps, run length, grids the design rule searches,
the onset time which mutant M3 shifts) or duplicates; each carries its reason, and the list is written to the
results so a reader can disagree with it.
"""
from __future__ import annotations

import dataclasses, math

from sim import acceptance as A, common, du3_lidar, gl3_glare, gnss_n2n4
from sim.r2 import acceptance_r2 as A2, heat

CONFIGS = {"du3": du3_lidar.Config, "gl3": gl3_glare.Config, "gnss": gnss_n2n4.Config}
STOPPING = common.Stopping

EXCLUDED = {
    "du3.dt": "scan period, structural", "du3.step_deg": "beam spacing, structural", "du3.t_onset": "shifted by mutant M3",
    "gl3.dt": "frame period, structural", "gl3.s_g": "same value as acc.S_G, which is the parameter listed",
    "gnss.duration": "run length, structural", "gnss.dt": "odometry step, structural",
    "gnss.fix_period_steps": "fix rate, structural", "gnss.t_onset": "shifted by mutant M3",
    "acc2.DU_THRESHOLDS": "grid searched by the design rule", "acc2.DU_SCANS": "grid searched by the design rule",
    "acc2.DU_BOUNDS": "grid searched by the design rule",
    "heat.RATED_AMBIENT_EXAMPLE": "cited figure, not assumed", "heat.DT": "time step, structural",
    "heat.MISSION": "mission length, structural", "heat.HORIZON": "controller look ahead, structural",
    "heat.DECIDE": "decision period, structural",
}
MONITOR = {"du3.vrr_threshold", "du3.vrr_scans", "gl3.monitor_frames", "gl3.monitor_noise", "gnss.gate", "gnss.reject_run",
           "gnss.cusum_bias", "gnss.cusum_limit", "gnss.timeout", "heat.RULE_AMBIENT", "acc2.M_H"}
UNIT_INTERVAL = {"gl3.p_clean", "du3.range_loss", "du3.drop", "acc.P_G", "acc.Q_N", "acc2.Q_H"}
COMPONENT_FIELDS = ("p0_w", "p1_w", "exponent", "r_k_per_w", "tau_s", "solar_gain_k", "limit_degc")


def _kind(pid: str) -> str:
    if pid in MONITOR: return "monitor"
    if pid.startswith(("acc.", "acc2.")): return "acceptance"
    return "model"


def list_parameters() -> list[dict]:
    """Every assumed parameter with its base value, kind and the reason it is in or out of the sweep."""
    out, skipped = [], []
    def add(pid, value):
        if pid in EXCLUDED: skipped.append({"id": pid, "reason": EXCLUDED[pid]}); return
        out.append({"id": pid, "base": value, "kind": _kind(pid), "integer": isinstance(value, int) and not isinstance(value, bool),
                    "unit_interval": pid in UNIT_INTERVAL})
    for tag, cls in CONFIGS.items():
        for f in dataclasses.fields(cls):
            add(f"{tag}.{f.name}", getattr(cls, f.name))
    for f in dataclasses.fields(STOPPING): add(f"stopping.{f.name}", getattr(STOPPING, f.name))
    for tag, mod in (("acc", A), ("acc2", A2)):
        for name in sorted(n for n in vars(mod) if n.isupper()):
            v = getattr(mod, name)
            if isinstance(v, dict): add(f"{tag}.{name}", dict(v))     # E_N: scaled as one parameter
            else: add(f"{tag}.{name}", v)
    for name in ("LIDAR_BIAS", "RULE_AMBIENT", "SD_PARAM", "SD_SOLAR", "SD_AMB", "SD_MEAS", "RATED_AMBIENT_EXAMPLE", "DT", "MISSION", "HORIZON", "DECIDE"):
        add(f"heat.{name}", getattr(heat, name))
    for comp, vals in heat.COMPONENTS.items():
        for field, v in zip(COMPONENT_FIELDS, vals): add(f"heat.{comp}.{field}", v)
    list_parameters.skipped = skipped
    return [p for p in out if not isinstance(p["base"], (tuple, list))]


def changed_value(p: dict, factor: float):
    """Value after multiplying by factor: integers are rounded half up and kept at least 1, unit interval values are capped at 1."""
    b = p["base"]
    if isinstance(b, dict): return {k: v * factor for k, v in b.items()}
    if p["integer"]: return max(1, int(math.floor(b * factor + 0.5)))
    v = b * factor
    return min(v, 1.0) if p["unit_interval"] else v
