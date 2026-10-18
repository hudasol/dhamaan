"""N4: replay of recorded logs through the GNSS fault checks (measurement level, software only).

A log is two CSV tables in the pilot kit format (docs/PILOT_KIT/):
  gnss.csv      t_s, x_m, y_m, fix_ok[, x_ref_m, y_ref_m]   position fixes in a local frame
  odometry.csv  t_s, v_mps, yaw_rad                         wheel speed and heading
score_log() runs the round 1 method (innovation gate, CUSUM, fix timeout; sim/gnss_n2n4.py parameters) over
the logged streams and reports the first fault declaration. When reference columns are present it also
reports the navigation error. Faults can be injected into a logged fix stream with inject().

No public log could be retrieved with the automated retrieval (docs/FETCH_LIST.md), so round 2 exercises the
harness on synthetic stand in logs from standin(); those are labelled SYNTHETIC like every other output here.
"""
from __future__ import annotations

import csv, io, math

import numpy as np

from sim import gnss_n2n4 as G

GNSS_COLUMNS = ("t_s", "x_m", "y_m", "fix_ok")
ODO_COLUMNS = ("t_s", "v_mps", "yaw_rad")
REF_COLUMNS = ("x_ref_m", "y_ref_m")


class LogError(ValueError):
    """The log does not follow the pilot kit format."""


def read_csv(text: str, required: tuple[str, ...]) -> list[dict]:
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows: raise LogError("empty log")
    missing = [c for c in required if c not in rows[0]]
    if missing: raise LogError(f"missing columns {missing}")
    out = []
    for n, r in enumerate(rows, 2):
        try: row = {k: (float(v) if v not in ("", None) else None) for k, v in r.items()}
        except ValueError as e: raise LogError(f"line {n}: {e}") from None
        if any(v is not None and not math.isfinite(v) for v in row.values()): raise LogError(f"line {n}: value is not a finite number")
        if any(row.get(c) is None for c in required): raise LogError(f"line {n}: a required column is empty")
        out.append(row)
    ts = [r["t_s"] for r in out]
    if any(b < a for a, b in zip(ts, ts[1:])): raise LogError("t_s is not increasing")
    return out


def score_log(gnss: list[dict], odo: list[dict], cfg: G.Config = G.Config()) -> dict:
    """Run the fault declaration method over a log. Odometry drives prediction; each fix is tested and fused."""
    R = cfg.sigma_gnss ** 2; Q = cfg.q_step ** 2
    xh = np.array([gnss[0]["x_m"], gnss[0]["y_m"]], dtype=float); P = 0.5
    g, rejects, last_fix_t, t_alarm, reason, gi = 0.0, 0, gnss[0]["t_s"], None, None, 1
    has_ref = all(gnss[0].get(c) is not None for c in REF_COLUMNS)
    max_err, err_alarm, ref = 0.0, None, None
    def err_now():
        return math.hypot(xh[0] - ref[0], xh[1] - ref[1]) if ref is not None else None
    for k in range(1, len(odo)):
        dt = odo[k]["t_s"] - odo[k - 1]["t_s"]
        v, yaw = odo[k - 1]["v_mps"], odo[k - 1]["yaw_rad"]
        xh = xh + v * dt * np.array([math.cos(yaw), math.sin(yaw)]); P += Q * dt / cfg.dt
        t = odo[k]["t_s"]
        while gi < len(gnss) and gnss[gi]["t_s"] <= t + 1e-9:
            f = gnss[gi]; gi += 1
            if has_ref and f.get("x_ref_m") is not None: ref = (f["x_ref_m"], f["y_ref_m"])
            if t_alarm is not None: continue
            if not f["fix_ok"]: continue
            last_fix_t = f["t_s"]
            z = np.array([f["x_m"], f["y_m"]]); nu = z - xh; S = P + R; nis = float(nu @ nu) / S
            if nis <= cfg.gate: K = P / S; xh = xh + K * nu; P = (1 - K) * P; rejects = 0
            else: rejects += 1
            g = max(0.0, g + nis - cfg.cusum_bias)
            if rejects >= cfg.reject_run: t_alarm, reason = f["t_s"], "gate"
            elif g > cfg.cusum_limit: t_alarm, reason = f["t_s"], "cusum"
            if has_ref:
                e = err_now(); max_err = max(max_err, e)
                if t_alarm is not None and err_alarm is None: err_alarm = e
        # fix timeout checked at every odometry step, so a gap with no rows at all is detected too (deviation D10)
        if t_alarm is None and t - last_fix_t > cfg.timeout:
            t_alarm, reason = t, "timeout"
            if has_ref: err_alarm = err_now(); max_err = max(max_err, err_alarm)
    return {"t_alarm": t_alarm, "reason": reason, "max_error_m": max_err if has_ref else None,
            "error_at_alarm_m": err_alarm, "fixes": len(gnss), "odometry_rows": len(odo)}


def standin(rng, cfg: G.Config = G.Config()) -> tuple[list[dict], list[dict]]:
    """A synthetic stand in log with reference positions: the round 1 receiver and odometry models."""
    n = int(round(cfg.duration / cfg.dt)); per = cfg.fix_period_steps
    scale = 1 + cfg.odo_scale_sd * rng.standard_normal()
    vnoise = cfg.odo_speed_sd * rng.standard_normal(n)
    hdg = np.cumsum(cfg.heading_rw * math.sqrt(cfg.dt) * rng.standard_normal(n))
    fix_noise = rng.standard_normal((n // per + 1, 2))
    gnss, odo, x = [], [], 0.0
    for i in range(n + 1):
        t = i * cfg.dt
        odo.append({"t_s": round(t, 3), "v_mps": cfg.speed * scale + (vnoise[i] if i < n else 0.0), "yaw_rad": float(hdg[min(i, n - 1)])})
        if i % per == 0:
            j = i // per
            gnss.append({"t_s": round(t, 3), "x_m": x + cfg.sigma_gnss * fix_noise[j][0], "y_m": cfg.sigma_gnss * fix_noise[j][1],
                         "fix_ok": 1.0, "x_ref_m": x, "y_ref_m": 0.0})
        x += cfg.speed * cfg.dt
    return gnss, odo


def inject(gnss: list[dict], kind: str, size: float, onset: float, rng) -> list[dict]:
    """Measurement level fault on a logged fix stream (no RF of any kind)."""
    phi = rng.uniform(0, 2 * math.pi); u = (math.cos(phi), math.sin(phi))
    out, period = [], (gnss[1]["t_s"] - gnss[0]["t_s"]) if len(gnss) > 1 else 1.0
    for j, f in enumerate(gnss):
        f = dict(f); age = f["t_s"] - onset
        if age >= 0 and kind != "nominal":
            if kind == "loss": f["fix_ok"] = 0.0
            elif kind == "noise":   # extra noise so the total grows to `size` over the round 1 ramp
                base_sd = G.Config().sigma_gnss
                sd = base_sd + (size - base_sd) * min(age / G.Config().noise_ramp, 1.0)
                extra = math.sqrt(max(sd * sd - base_sd * base_sd, 0.0))
                f["x_m"] += extra * rng.standard_normal(); f["y_m"] += extra * rng.standard_normal()
            elif kind == "jump": f["x_m"] += size * u[0]; f["y_m"] += size * u[1]
            elif kind == "drift": f["x_m"] += size * age * u[0]; f["y_m"] += size * age * u[1]
            elif kind == "replay":
                back = int(round(size / period)); src = gnss[max(j - back, 0)]   # never wraps to the end of the log
                f["x_m"], f["y_m"] = src["x_m"], src["y_m"]
        out.append(f)
    return out


def to_csv(rows: list[dict], columns: tuple[str, ...]) -> str:
    buf = io.StringIO(); w = csv.writer(buf, lineterminator="\n"); w.writerow(columns)
    for r in rows: w.writerow([f"{r[c]:.6f}" if isinstance(r[c], float) else r[c] for c in columns])
    return buf.getvalue()


def faulty_copy(text: str, kind: str = "jump", size: float = 20.0, onset: float = 30.0) -> str:
    """A copy of a gnss.csv log with one injected fault and a fixed seed (pilot kit walk through). SYNTHETIC."""
    from sim.r2 import base
    rows = read_csv(text, GNSS_COLUMNS)
    cols = GNSS_COLUMNS + tuple(c for c in REF_COLUMNS if rows[0].get(c) is not None)
    return to_csv(inject(rows, kind, size, onset, base.rng(base.DEV_SEED, "WALK", kind, 0)), cols)
