"""Five detectors for the recorded arm (docs/ANALYSIS_PLAN_R3_RECORDED.md, Detectors). Each takes fixes and returns the time of its first alarm.

M is the monitor under test and is the round 1 and 2 code unchanged (sim/r2/replay.score_log). D-RX, D-JAM, D-JUMP and D-NIS are baselines.
run_episodes() restarts a detector from a fresh state REARM_S seconds after an alarm, so one stretch of data gives a list of alarm times.
"""
from __future__ import annotations

import math

import numpy as np

from sim import gnss_n2n4 as G
from sim.r2 import replay
from sim.r3 import jammertest as J

REARM_S = 30.0
H_ACC_LIMIT = 10.0
JUMP_LIMIT_M = 5.0
JUMP_MAX_GAP_S = 2.5
NIS_SIGMA = 1.0
NIS_ACCEL = 0.5
NIS_GATE = 13.82
NIS_RUN = 3
NIS_WARMUP = 5
JAM_ROWS = 3
NAMES = ("M", "D-RX", "D-JAM", "D-JUMP", "D-NIS")


def _in(rows: list[dict], a: float, b: float) -> list[dict]:
    return [r for r in rows if a - 1e-9 <= r["t_s"] <= b + 1e-9]


def first_alarm_m(fixes: list[dict], rf: list[dict], a: float, b: float, params: dict) -> float | None:
    fx = _in(fixes, a, b)
    k = next((i for i, f in enumerate(fx) if f["fix_ok"]), None)
    if k is None: return None
    fx = fx[k:]
    if fx[-1]["t_s"] - fx[0]["t_s"] < 2 * G.Config().dt: return None
    odo = J.odometry(fixes, fx[0]["t_s"], fx[-1]["t_s"], G.Config().dt)
    gnss = [{"t_s": f["t_s"], "x_m": f["x_m"], "y_m": f["y_m"], "fix_ok": f["fix_ok"]} for f in fx]
    return replay.score_log(gnss, odo, G.Config())["t_alarm"]


def first_alarm_rx(fixes, rf, a, b, params) -> float | None:
    for f in _in(fixes, a, b):
        if not f["fix_ok"] or f["h_acc"] > H_ACC_LIMIT: return f["t_s"]
    return None


def first_alarm_jam(fixes, rf, a, b, params) -> float | None:
    thr = params["jam_threshold"]; run = 0
    for r in _in(rf, a, b):
        run = run + 1 if r["jam"] > thr else 0
        if run >= JAM_ROWS: return r["t_s"]
    return None


def first_alarm_jump(fixes, rf, a, b, params) -> float | None:
    prev = None
    for f in _in(fixes, a, b):
        if not f["fix_ok"]: continue
        if prev is not None and f["t_s"] - prev["t_s"] <= JUMP_MAX_GAP_S:
            dt = f["t_s"] - prev["t_s"]
            vn = 0.5 * (f["vel_n"] + prev["vel_n"]); ve = 0.5 * (f["vel_e"] + prev["vel_e"])
            if math.hypot(f["x_m"] - prev["x_m"] - ve * dt, f["y_m"] - prev["y_m"] - vn * dt) > JUMP_LIMIT_M: return f["t_s"]
        prev = f
    return None


def first_alarm_nis(fixes, rf, a, b, params) -> float | None:
    """Constant velocity Kalman filter on position fixes only; chi square gate on the innovation, alarm after NIS_RUN rejections in a row."""
    x = None; P = None; last_t = None; n = 0; rejects = 0
    R = np.eye(2) * NIS_SIGMA ** 2; H = np.hstack([np.eye(2), np.zeros((2, 2))])
    for f in _in(fixes, a, b):
        if not f["fix_ok"]: continue
        z = np.array([f["x_m"], f["y_m"]])
        if x is None:
            x = np.array([z[0], z[1], 0.0, 0.0]); P = np.diag([NIS_SIGMA ** 2, NIS_SIGMA ** 2, 25.0, 25.0]); last_t = f["t_s"]; n = 1; continue
        dt = f["t_s"] - last_t; last_t = f["t_s"]
        F = np.eye(4); F[0, 2] = F[1, 3] = dt
        q = NIS_ACCEL ** 2
        Q = q * np.array([[dt ** 4 / 4, 0, dt ** 3 / 2, 0], [0, dt ** 4 / 4, 0, dt ** 3 / 2], [dt ** 3 / 2, 0, dt ** 2, 0], [0, dt ** 3 / 2, 0, dt ** 2]])
        x = F @ x; P = F @ P @ F.T + Q
        S = H @ P @ H.T + R; nu = z - H @ x; nis = float(nu @ np.linalg.solve(S, nu)); n += 1
        accept = n <= NIS_WARMUP or nis <= NIS_GATE
        if accept:
            K = P @ H.T @ np.linalg.inv(S); x = x + K @ nu; P = (np.eye(4) - K @ H) @ P; rejects = 0
        else:
            rejects += 1
            if rejects >= NIS_RUN: return f["t_s"]
    return None


FIRST_ALARM = {"M": first_alarm_m, "D-RX": first_alarm_rx, "D-JAM": first_alarm_jam, "D-JUMP": first_alarm_jump, "D-NIS": first_alarm_nis}


def run_episodes(name: str, fixes: list[dict], rf: list[dict], a: float, b: float, params: dict | None = None) -> list[float]:
    """Alarm times over [a, b]. After each alarm the detector restarts REARM_S later with a fresh state."""
    f = FIRST_ALARM[name]; params = params or {}; out = []; start = a
    while start < b:
        t = f(fixes, rf, start, b, params)
        if t is None: break
        out.append(t); start = t + REARM_S
    return out
