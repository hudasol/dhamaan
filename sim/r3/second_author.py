# Provenance: written by a second author, a separate automated agent of the same model family as the first author, from docs/INDEPENDENT_GENERATOR_SPEC.md alone.
# The agent was told not to open this repository. That was an instruction and was not enforced. Unchanged below this line.
"""Independent synthetic GNSS fault generator. All output is SYNTHETIC."""
import math
import numpy as np

SPEED = 0.8
ONSET = 30.0
T_END = 120.0
KINDS = ("nominal", "loss", "noise", "jump", "drift", "replay")


def generate(kind, size, seed):
    if kind not in KINDS:
        raise ValueError("unknown kind: %r" % (kind,))
    size = 0.0 if kind in ("nominal", "loss") else float(size)
    root = np.random.SeedSequence(int(seed) % (2 ** 64))
    s_odo, s_fix, s_dir = root.spawn(3)
    r_odo = np.random.default_rng(s_odo)
    r_fix = np.random.default_rng(s_fix)
    r_dir = np.random.default_rng(s_dir)

    # Odometry (identical for every kind at a given seed; faults touch fixes only)
    n_o = 1201
    scale = 1.0 + 0.01 * r_odo.standard_normal()
    v = SPEED * scale + 0.02 * r_odo.standard_normal(n_o)
    steps = 0.001 * math.sqrt(0.1) * r_odo.standard_normal(n_o - 1)
    yaw = np.concatenate(([0.0], np.cumsum(steps)))
    odo = [{"t_s": round(i * 0.1, 1), "v_mps": float(v[i]), "yaw_rad": float(yaw[i])}
           for i in range(n_o)]

    # Fixes
    n_g = 121
    unit = r_fix.standard_normal((n_g, 2))      # base receiver noise, sigma 1
    ang = r_dir.uniform(0.0, 2.0 * math.pi)
    ux, uy = math.cos(ang), math.sin(ang)
    gnss = []
    for i in range(n_g):
        t = float(i)
        tx, ty = SPEED * t, 0.0
        x, y = tx, ty
        active = t >= ONSET
        if kind == "loss" and active:
            continue
        ex, ey = unit[i]
        if kind == "noise" and active:
            sig = 1.0 + (size - 1.0) * min((t - ONSET) / 20.0, 1.0)
            ex, ey = ex * sig, ey * sig
        x, y = x + ex, y + ey
        if kind == "jump" and active:
            x, y = x + size * ux, y + size * uy
        elif kind == "drift" and active:
            d = size * (t - ONSET)
            x, y = x + d * ux, y + d * uy
        elif kind == "replay" and active:
            x, y = SPEED * (t - size) + ex, 0.0 + ey
        gnss.append({"t_s": t, "x_m": float(x), "y_m": float(y), "fix_ok": 1.0,
                     "x_ref_m": tx, "y_ref_m": ty})
    return gnss, odo
