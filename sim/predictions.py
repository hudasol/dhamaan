"""Predictions and acceptance criteria, written before any evaluation run (see sim/PREREGISTRATION.md).

Each entry names metrics in the result files by path and a comparison every listed metric must satisfy.
Paths are "<file>:<key>/<key>/..." into sim/results/<file>.json. A metric whose value is null (no run
qualified) is reported as not applicable and does not count as a pass or a failure.
Scoring is done by sim/score.py. Nothing here may change after results exist (see DEVIATIONS.md).
"""
from __future__ import annotations

from sim import acceptance as A
from sim import gl3_glare as gl3

K = [round(0.1 * i, 1) for i in range(11)]


def du3(m, ks, metric):
    return [f"du3:conditions/{m}|k={k:.1f}/{metric}" for k in ks]


GL3_CONDS = [(e, a, r) for e in gl3.ELEVATIONS for a in gl3.AZIMUTHS for r in gl3.RHOS]


def glc(m, conds, metric):
    return [f"gl3:conditions/{m}|e={e}|a={a}|rho={r}/{metric}" for e, a, r in conds]


def gn(m, faults, metric):
    return [f"gnss:conditions/{m}|{f}/{metric}" for f in faults]


LOW_SAT = [c for c in GL3_CONDS if gl3.saturation(gl3.Config(), *c) < 0.2]
FAULTS_ALL = ["loss=0", "noise=3", "noise=5", "noise=10", "jump=2", "jump=5", "jump=10", "jump=20",
              "drift=0.05", "drift=0.1", "drift=0.2", "drift=0.5", "replay=2", "replay=5", "replay=10"]
COVERED = ["loss=0", "noise=5", "noise=10", "jump=5", "jump=10", "jump=20", "drift=0.2", "drift=0.5",
           "replay=5", "replay=10"]   # sizes at or above E_N


def P(pid, text, checks, expect=True):
    return {"id": pid, "text": text, "checks": checks, "expect": expect}


def C(metrics, op, value):
    return {"metrics": metrics, "op": op, "value": value}


PREDICTIONS = [
    # DU3
    P("DU3-P1", "Detector alone (B0) is never unsafe for k up to 0.9.", [C(du3("B0", K[:10], "unsafe/rate"), "all<=", 0.0)]),
    P("DU3-P2", "Detector alone (B0) is unsafe in at least 90 percent of runs at k = 1.0.", [C(du3("B0", [1.0], "unsafe/rate"), "all>=", 0.9)]),
    P("DU3-P3", "Monitor (M) never stops the robot for k up to 0.2.", [C(du3("M", K[:3], "monitor_stop/rate"), "all<=", 0.0)]),
    P("DU3-P4", "Monitor (M) stops the robot in at least 90 percent of runs for k from 0.4.", [C(du3("M", K[4:], "monitor_stop/rate"), "all>=", 0.9)]),
    P("DU3-P5", "M is never unsafe at any level.", [C(du3("M", K, "unsafe/rate"), "all<=", 0.0)]),
    P("DU3-P6", "Always slow (B1) is unsafe in at most half the runs at k = 1.0.", [C(du3("B1", [1.0], "unsafe/rate"), "all<=", 0.5)]),
    P("DU3-P7", "Clean median detection distance (B0, k = 0) lies between 6 and 10 m.", [C(du3("B0", [0.0], "detection_distance/median"), "between", [6.0, 10.0])]),
    # GL3
    P("GL3-P1", "B0 misses P_G in 2 to 4 of 50 sun conditions (expected 3: low sun ahead).", [C(["gl3:summary/B0/conditions_below_p_g"], "between", [2, 4])]),
    P("GL3-P2", "M misses P_G in 1 to 3 conditions (expected 2: low sun ahead with a reflecting floor).", [C(["gl3:summary/M/conditions_below_p_g"], "between", [1, 3])]),
    P("GL3-P3", "M meets P_G whenever azimuth is at least 30 degrees or elevation at least 30 degrees.",
      [C(glc("M", [c for c in GL3_CONDS if c[1] >= 30 or c[0] >= 30], "detected_in_time/rate"), "all>=", A.P_G)]),
    P("GL3-P4", "M issues no slow command where modelled saturation is below 0.2.", [C(glc("M", LOW_SAT, "slow_command/rate"), "all<=", 0.0)]),
    # GNSS
    P("N-P1", "M false alarm rate in nominal runs is at most 1 in 30.", [C(gn("M", ["nominal=0"], "false_alarm/rate"), "all<=", 1 / 30)]),
    P("N-P2", "M detects GNSS loss in every run, within 3.5 s.", [C(gn("M", ["loss=0"], "detected/rate"), "all>=", 1.0),
                                                                   C(gn("M", ["loss=0"], "detection_delay/max"), "all<=", 3.5)]),
    P("N-P3", "M detects jumps of 5 m or more in every run, mean delay at most 3 s.",
      [C(gn("M", ["jump=5", "jump=10", "jump=20"], "detected_within_t_n/rate"), "all>=", 1.0),
       C(gn("M", ["jump=5", "jump=10", "jump=20"], "detection_delay/mean"), "all<=", 3.0)]),
    P("N-P4", "M detects a 2 m jump in at least 80 percent of runs (at any time).", [C(gn("M", ["jump=2"], "detected/rate"), "all>=", 0.8)]),
    P("N-P5", "M detects drift of 0.5 m/s within T_N in at least 90 percent of runs.", [C(gn("M", ["drift=0.5"], "detected_within_t_n/rate"), "all>=", 0.9)]),
    P("N-P6", "M detects drift of 0.2 m/s within T_N in at most half the runs (expected AC-N1 failure).", [C(gn("M", ["drift=0.2"], "detected_within_t_n/rate"), "all<=", 0.5)]),
    P("N-P7", "M detects drift of 0.1 m/s in at least 90 percent of runs, mean delay 15 to 30 s.",
      [C(gn("M", ["drift=0.1"], "detected/rate"), "all>=", 0.9), C(gn("M", ["drift=0.1"], "detection_delay/mean"), "between", [15.0, 30.0])]),
    P("N-P8", "M detects noise growth to 5 m and 10 m within T_N in at least 90 percent of runs.", [C(gn("M", ["noise=5", "noise=10"], "detected_within_t_n/rate"), "all>=", 0.9)]),
    P("N-P9", "M detects replay with 5 s and 10 s delay within T_N in at least 90 percent of runs.", [C(gn("M", ["replay=5", "replay=10"], "detected_within_t_n/rate"), "all>=", 0.9)]),
    P("N-P10", "Accept all (B0) exceeds L_N in at least 90 percent of runs for jumps of 5 m or more and drift of 0.1 m/s or more.",
      [C(gn("B0", ["jump=5", "jump=10", "jump=20", "drift=0.1", "drift=0.2", "drift=0.5"], "error_exceeds_l_n/rate"), "all>=", 0.9)]),
    P("N-P11", "Gate only (B1) stays within L_N in at least 90 percent of runs for jumps of 10 m or more.", [C(gn("B1", ["jump=10", "jump=20"], "error_exceeds_l_n/rate"), "all<=", 0.1)]),
    P("N-P12", "Gate only (B1) exceeds L_N in at least half the runs for drift of 0.1 m/s.", [C(gn("B1", ["drift=0.1"], "error_exceeds_l_n/rate"), "all>=", 0.5)]),
]

ACCEPTANCE = [
    P("AC-DU1", f"Up to B_D = {A.B_D}, the detector alone (B0) detects the obstacle in time in every run.",
      [C(du3("B0", [k for k in K if k <= A.B_D], "detected_in_time/rate"), "all>=", 1.0)], expect=True),
    P("AC-DU2", f"Beyond B_D, the monitor (M) stops the robot in every run within T_D = {A.T_D} s of onset.",
      [C(du3("M", [k for k in K if k > A.B_D], "monitor_stop/rate"), "all>=", 1.0),
       C(du3("M", [k for k in K if k > A.B_D], "stop_time_after_onset/max"), "all<=", A.T_D)], expect=True),
    P("AC-GL1", f"M detects in time at rate at least P_G = {A.P_G} at every sun condition (failures become restrictions, AC-GL3).",
      [C(glc("M", GL3_CONDS, "detected_in_time/rate"), "all>=", A.P_G)], expect=False),
    P("AC-GL2", f"M commands the slow speed within T_G = {A.T_G} s of saturation exceeding S_G = {A.S_G}, in every such run.",
      [C(glc("M", GL3_CONDS, "slow_command_runs_where_s_exceeded/rate"), "all>=", 1.0),
       C(glc("M", GL3_CONDS, "slow_command_delay/max"), "all<=", A.T_G)], expect=True),
    P("AC-N1", f"Faults at or above E_N are detected within T_N = {A.T_N} s in at least Q_N = {A.Q_N} of runs.",
      [C(gn("M", COVERED, "detected_within_t_n/rate"), "all>=", A.Q_N)], expect=False),
    P("AC-N2", f"In every detected case the safe state is reached with navigation error at most L_N = {A.L_N} m.",
      [C(gn("M", FAULTS_ALL, "error_at_stop/max"), "all<=", A.L_N)], expect=True),
]
