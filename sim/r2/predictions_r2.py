"""Round 2 predictions and acceptance criteria, written before any round 2 run (sim/PREREGISTRATION_R2.md).

Paths are "<file>:<key>/..." into sim/results_r2/<file>.json. "expect" False means we predict the check fails.
Scored by sim/r2/score_r2.py with the round 1 scoring functions. Nothing here may change after a round 2 run.
"""
from __future__ import annotations

from sim import acceptance as A
from sim import gl3_glare as G3
from sim.r2 import acceptance_r2 as A2, heat as H
from sim.predictions import C, P

GL3_CONDS = [f"e={e}|a={a}|rho={r}" for e in G3.ELEVATIONS for a in G3.AZIMUTHS for r in G3.RHOS]
LOW_SAT = [c for (c, s) in ((f"e={e}|a={a}|rho={r}", G3.saturation(G3.Config(), e, a, r))
                            for e in G3.ELEVATIONS for a in G3.AZIMUTHS for r in G3.RHOS) if s < A2.GL_GUARD]


def hc(m, conds, metric):
    return [f"heat:conditions/{m}|{c}/{metric}" for c in conds]


def heat_conds(pred):
    return [f"peak={p}|{s}|{st}" for p in H.PEAKS for s in H.SUN for st in H.START if pred(p, s, st)]


ALL_HEAT = heat_conds(lambda p, s, st: True)
FAULTS_COVERED = ["loss=0", "noise=5", "noise=10", "jump=5", "jump=10", "jump=20", "drift=0.2", "drift=0.5", "replay=5", "replay=10"]
FAULTS_ALL = ["loss=0", "noise=3", "noise=5", "noise=10", "jump=2", "jump=5", "jump=10", "jump=20",
              "drift=0.05", "drift=0.1", "drift=0.2", "drift=0.5", "replay=2", "replay=5", "replay=10"]


def n4(faults, metric):
    return [f"n4r2:conditions/H|{f}/{metric}" for f in faults]


PREDICTIONS = [
    # GL3
    P("GL3R2-P1", "The design rule picks two frames and a margin from 0.03 to 0.05.",
      [C(["design_gl3:chosen/frames"], "between", [2, 2]), C(["design_gl3:chosen/margin"], "between", [0.03, 0.05])]),
    P("GL3R2-P2", "On held out seeds the chosen monitor (M2) has no run that breaks AC-GL2.", [C(["gl3r2:summary/M2/ac_gl2_violating_runs"], "all<=", 0)]),
    P("GL3R2-P3", "On held out seeds the round 1 monitor (M) still has at least one run that breaks AC-GL2.", [C(["gl3r2:summary/M/ac_gl2_violating_runs"], "all>=", 1)]),
    P("GL3R2-P4", "M2 misses P_G in exactly 3 sun conditions, the same low sun cases as round 1.", [C(["gl3r2:summary/M2/conditions_below_p_g"], "between", [3, 3])]),
    P("GL3R2-P5", "M2 issues no slow command where modelled saturation is below the guard.", [C(["gl3r2:summary/M2/false_slow_runs_below_guard"], "all<=", 0)]),
    # DU3
    P("DU3R2-P1", "No threshold, scan count and bound in the grid meets both DU3 criteria on the development seeds.", [C(["design_du3:feasible_count"], "all<=", 0)]),
    P("DU3R2-P2", "The chosen bound lies from 0.3 to 0.5.", [C(["design_du3:chosen/bound"], "between", [0.3, 0.5])]),
    P("DU3R2-P3", "On held out seeds the chosen pair has at most 30 violating runs.", [C(["du3r2:summary/M2/total"], "all<=", 30)]),
    P("DU3R2-P4", "On held out seeds the round 1 pair, judged by the round 2 criteria, has at least 30 violating runs.", [C(["du3r2:summary/M/total"], "all>=", 30)]),
    # Heat
    P("H-P1", "Full scale (B0) exceeds a limit in at least 90 percent of runs in every sun condition and every shade condition from 45 degC.",
      [C(hc("B0", heat_conds(lambda p, s, st: s == "sun" or p >= 45), "exceed/rate"), "all>=", 0.9)]),
    P("H-P2", "The controller (M) never exceeds a limit in shade, nor in sun at 35 and 40 degC from a normal start.",
      [C(hc("M", heat_conds(lambda p, s, st: s == "shade" or (p <= 40 and st == "normal")), "exceed/rate"), "all<=", 0.0)]),
    P("H-P3", "M exceeds a limit in at least half the runs in sun at 50 degC, where parking in place cannot keep the battery below its limit.",
      [C(hc("M", heat_conds(lambda p, s, st: s == "sun" and p == 50), "exceed/rate"), "all>=", 0.5)]),
    P("H-P4", "After a sun soak at 45 degC or more, M never starts moving in at least 90 percent of runs.",
      [C(hc("M", heat_conds(lambda p, s, st: s == "sun" and st == "soak" and p >= 45), "never_moved/rate"), "all>=", 0.9)]),
    P("H-P5", "In shade at 40 and 45 degC from a normal start, M keeps a mean scale of at least 0.2 while the fixed rule parks.",
      [C(hc("M", heat_conds(lambda p, s, st: s == "shade" and st == "normal" and p in (40, 45)), "productivity/mean"), "all>=", 0.2)]),
    P("H-P6", "After a soak in shade at 45 degC, M waits at least 10 minutes on average before moving.",
      [C(hc("M", ["peak=45|shade|soak"], "first_move_min/mean"), "all>=", A2.SOAK_WAIT_MIN)]),
    # N4
    P("N4-P1", "The harness raises at most 1 false alarm in 30 nominal stand in logs.", [C(n4(["nominal=0"], "false_alarm/rate"), "all<=", 1 / 30)]),
    P("N4-P2", "The harness detects loss and jumps of 5 m or more within T_N in every stand in log.",
      [C(n4(["loss=0", "jump=5", "jump=10", "jump=20"], "detected_within_t_n/rate"), "all>=", 1.0)]),
    P("N4-P3", "Drift of 0.2 m/s is detected within T_N in at most half the stand in logs.", [C(n4(["drift=0.2"], "detected_within_t_n/rate"), "all<=", 0.5)]),
    P("N4-P4", "Replay with 5 s and 10 s delay is detected within T_N in at least 90 percent of stand in logs.",
      [C(n4(["replay=5", "replay=10"], "detected_within_t_n/rate"), "all>=", 0.9)]),
]

ACCEPTANCE = [
    P("AC-GL2R2", f"M2 commands the slow speed within T_G = {A.T_G} s of saturation exceeding S_G in every such held out run.",
      [C(["gl3r2:summary/M2/ac_gl2_violating_runs"], "all<=", 0)], expect=True),
    P("AC-GL4R2", f"M2 issues no slow command where modelled saturation is below {A2.GL_GUARD}.",
      [C(["gl3r2:summary/M2/false_slow_runs_below_guard"], "all<=", 0)], expect=True),
    P("AC-GL1R2", f"M2 detects in time at rate at least P_G = {A.P_G} at every sun condition.",
      [C(["gl3r2:summary/M2/conditions_below_p_g"], "all<=", 0)], expect=False),
    P("AC-DU1R2", "Up to the chosen bound, the detector detects in time in every held out run and the chosen monitor never stops the robot.",
      [C(["du3r2:summary/M2/below"], "all<=", 0)], expect=False),
    P("AC-DU2R2", f"Beyond the chosen bound, the chosen monitor stops the robot within T_D = {A.T_D} s of onset in every held out run.",
      [C(["du3r2:summary/M2/above"], "all<=", 0)], expect=False),
    P("AC-H1", f"The open loop model predicts each component's mission maximum within T_H = {A2.T_H} K in at least {A2.Q_H} of runs, in every condition.",
      [C([f"heat:conditions/model|{c}/within_t_h_{k}/rate" for c in ALL_HEAT for k in H.COMPONENTS], "all>=", A2.Q_H)], expect=False),
    P("AC-H2", f"With M, the required stopping distance at heat grows by a factor of at most F_H = {A2.F_H} in every run.",
      [C(hc("M", ALL_HEAT, "stop_factor/max"), "all<=", A2.F_H)], expect=True),
    P("AC-H3", "With M, no component exceeds its hard limit in any run.", [C(hc("M", ALL_HEAT, "exceed/rate"), "all<=", 0.0)], expect=False),
    P("AC-N1R2", f"On stand in logs, faults at or above E_N are detected within T_N = {A.T_N} s in at least Q_N = {A.Q_N} of logs.",
      [C(n4(FAULTS_COVERED, "detected_within_t_n/rate"), "all>=", A.Q_N)], expect=False),
    P("AC-N2R2", f"On stand in logs, the navigation error at the alarm is at most L_N = {A.L_N} m in every detected case.",
      [C(n4(FAULTS_ALL, "error_at_alarm/max"), "all<=", A.L_N)], expect=True),
]
