"""GL3 round 2: a saturation monitor with a margin below S_G, beside the round 1 monitor.

World and detection are the round 1 model (sim/gl3_glare.py, unchanged). The variant M2 commands the slow
speed when measured saturation exceeds S_G minus a margin for a number of consecutive frames, and stays slow
once commanded (latched, so it cannot chatter). Margin and frames are chosen on the development seed set by
the rule in sim/PREREGISTRATION_R2.md; scoring uses the held out seed set.
"""
from __future__ import annotations

from dataclasses import asdict

from sim import acceptance as A, common, gl3_glare as G
from sim.r2 import acceptance_r2 as A2, base

EXPERIMENT = "GL3R2"
CANDIDATES = [(m, f) for m in (0.0, 0.03, 0.05, 0.08) for f in (1, 2)]   # (margin, frames)
CONDS = [(e, a, r) for e in G.ELEVATIONS for a in G.AZIMUTHS for r in G.RHOS]


def run_one(cfg: G.Config, s0: float, threshold: float, frames: int, rng, stop: common.Stopping) -> dict:
    """Nominal speed with a latched monitor (threshold, frames). Same draws per frame as round 1."""
    v = cfg.v_nominal
    v_cmd, d, t, pos_run, hi_run, t_exceed, t_cmd = v, cfg.start_distance, 0.0, 0, 0, None, None
    while True:
        if d < stop.required(v): return {"outcome": "unsafe", "t_exceed": t_exceed, "t_cmd": t_cmd}
        s = min(1.0, max(0.0, s0 * rng.uniform(1 - cfg.flicker, 1 + cfg.flicker)))
        u, z = rng.random(), rng.standard_normal()
        if t_exceed is None and s > A.S_G: t_exceed = t
        hit = d <= cfg.camera_range and u < cfg.p_clean * (1 - s) ** 2
        pos_run = pos_run + 1 if hit else 0
        if pos_run >= cfg.confirm_frames: return {"outcome": "detected", "t_exceed": t_exceed, "t_cmd": t_cmd}
        if t_cmd is None:
            hi_run = hi_run + 1 if s + cfg.monitor_noise * z > threshold else 0
            if hi_run >= frames: v_cmd, t_cmd = cfg.v_slow, t
        d -= v * cfg.dt; t += cfg.dt
        if v > v_cmd: v = max(v_cmd, v - cfg.decel * cfg.dt)


def summarise(runs: list[dict], s0: float) -> dict:
    exceeded = [r for r in runs if r["t_exceed"] is not None]
    in_time = [r["t_cmd"] is not None and r["t_cmd"] - r["t_exceed"] <= A.T_G + 1e-9 for r in exceeded]
    return {"saturation_model": s0,
            "detected_in_time": common.rate([r["outcome"] == "detected" for r in runs]),
            "unsafe": common.rate([r["outcome"] == "unsafe" for r in runs]),
            "slow_command": common.rate([r["t_cmd"] is not None for r in runs]),
            "slow_within_t_g_where_exceeded": common.rate(in_time),
            "slow_command_delay": common.mean_ci([max(0.0, r["t_cmd"] - r["t_exceed"]) for r in exceeded if r["t_cmd"] is not None])}


def evaluate(seed_set: int, monitors: dict[str, tuple[float, int]], cfg: G.Config = G.Config(), seeds: int = base.SEEDS) -> dict:
    stop = common.Stopping(); out = {}
    for e, a, r in CONDS:
        cond = f"e={e}|a={a}|rho={r}"; s0 = G.saturation(cfg, e, a, r)
        for name, (margin, frames) in monitors.items():
            runs = [run_one(cfg, s0, A.S_G - margin, frames, base.rng(seed_set, EXPERIMENT, cond, i), stop) for i in range(seeds)]
            out[f"{name}|{cond}"] = {"method": name, "margin": margin, "frames": frames, "elevation_deg": e,
                                     "azimuth_deg": a, "rho": r} | summarise(runs, s0)
    return out


def ok_on(conds: dict, name: str) -> tuple[bool, int]:
    """Design rule check: AC-GL2 holds and no slow command below the false slow down guard. Returns (ok, violations)."""
    bad = 0
    for c in conds.values():
        if c["method"] != name: continue
        r = c["slow_within_t_g_where_exceeded"]
        if r["rate"] is not None and r["k"] < r["n"]: bad += r["n"] - r["k"]
        if c["saturation_model"] < A2.GL_GUARD: bad += c["slow_command"]["k"]
    return bad == 0, bad


def design(seeds: int = base.SEEDS) -> dict:
    """Development seed set only. Smallest margin first, then more frames, among candidates with no violation."""
    mons = {f"m{m}_f{f}": (m, f) for m, f in CANDIDATES}
    conds = evaluate(base.DEV_SEED, mons, seeds=seeds)
    table = []
    for name, (m, f) in mons.items():
        ok, bad = ok_on(conds, name); table.append({"monitor": name, "margin": m, "frames": f, "ok": ok, "violations": bad})
    ok = [t for t in table if t["ok"]]
    pick = sorted(ok, key=lambda t: (t["margin"], -t["frames"]))[0] if ok else sorted(table, key=lambda t: (t["violations"], t["margin"]))[0]
    return {"candidates": table, "chosen": {"margin": pick["margin"], "frames": pick["frames"], "feasible": bool(ok)}}


def score(chosen: dict, seeds: int = base.SEEDS) -> dict:
    """Held out seed set. M is the round 1 monitor (margin 0, two frames, latched); M2 is the chosen variant."""
    cfg = G.Config()
    conds = evaluate(base.HELDOUT_SEED, {"M": (0.0, cfg.monitor_frames), "M2": (chosen["margin"], chosen["frames"])}, seeds=seeds)
    summary = {}
    for name in ("M", "M2"):
        ok, bad = ok_on(conds, name)
        mine = [c for c in conds.values() if c["method"] == name]
        summary[name] = {"conditions_below_p_g": sum(c["detected_in_time"]["rate"] < A.P_G for c in mine),
                         "ac_gl2_violating_runs": sum(c["slow_within_t_g_where_exceeded"]["n"] - c["slow_within_t_g_where_exceeded"]["k"] for c in mine),
                         "false_slow_runs_below_guard": sum(c["slow_command"]["k"] for c in mine if c["saturation_model"] < A2.GL_GUARD)}
    return base.envelope(EXPERIMENT, ["GL3", "GL5 (software response only)"], "held out",
                         asdict(cfg) | {"chosen": chosen, "guard": A2.GL_GUARD}, conds, summary)
