"""N4 round 2: the replay harness exercised on synthetic stand in logs (held out seed set)."""
from __future__ import annotations

from dataclasses import asdict

from sim import acceptance as A, common, gnss_n2n4 as G
from sim.r2 import base, replay

EXPERIMENT = "N4R2"


def score(seeds: int = base.SEEDS) -> dict:
    cfg = G.Config(); conds = {}
    logs = [replay.standin(base.rng(base.HELDOUT_SEED, "N4LOG", "standin", i), cfg) for i in range(seeds)]
    # the harness reads what it writes: every stand in log goes through the CSV format and back
    logs = [(replay.read_csv(replay.to_csv(g, replay.GNSS_COLUMNS + replay.REF_COLUMNS), replay.GNSS_COLUMNS),
             replay.read_csv(replay.to_csv(o, replay.ODO_COLUMNS), replay.ODO_COLUMNS)) for g, o in logs]
    for kind, size in G.CONDITIONS:
        cond = f"{kind}={size:g}"
        res = []
        for i, (g, o) in enumerate(logs):
            gi = replay.inject(g, kind, size, cfg.t_onset, base.rng(base.HELDOUT_SEED, EXPERIMENT, cond, i))
            res.append(replay.score_log(gi, o, cfg))
        on = cfg.t_onset
        pre = [r["t_alarm"] is not None and (kind == "nominal" or r["t_alarm"] < on) for r in res]
        delays = [r["t_alarm"] - on if r["t_alarm"] is not None and r["t_alarm"] >= on else None for r in res]
        conds[f"H|{cond}"] = {
            "method": "H", "fault": kind, "size": size,
            "false_alarm": common.rate(pre),
            "detected": common.rate([d is not None for d in delays]) if kind != "nominal" else None,
            "detected_within_t_n": common.rate([d is not None and d <= A.T_N for d in delays]) if kind != "nominal" else None,
            "detection_delay": common.mean_ci(delays),
            "error_at_alarm": common.mean_ci([r["error_at_alarm_m"] for r in res]),
            "missed_seeds": [i for i, (d, p) in enumerate(zip(delays, pre)) if d is None and not p] if kind != "nominal" else []}
    return base.envelope(EXPERIMENT, ["N4 (synthetic stand in logs only)"], "held out",
                         asdict(cfg) | {"log_format": {"gnss": list(replay.GNSS_COLUMNS + replay.REF_COLUMNS), "odometry": list(replay.ODO_COLUMNS)}},
                         conds, {"logs": seeds})


def example_log() -> tuple[str, str]:
    """One stand in log for the pilot kit walk through (development seed set, labelled synthetic by its folder)."""
    g, o = replay.standin(base.rng(base.DEV_SEED, "N4LOG", "example", 0))
    return replay.to_csv(g, replay.GNSS_COLUMNS + replay.REF_COLUMNS), replay.to_csv(o, replay.ODO_COLUMNS)
