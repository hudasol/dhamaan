"""Round 2 acceptance values, fixed before any round 2 run (sim/PREREGISTRATION_R2.md).

Round 1 values in sim/acceptance.py are reused where they apply and are not changed. Every value here is an
assumed, proposal value chosen by the authors for a synthetic study, not a value from any source.
"""
# GL3: a slow command where modelled saturation is below this guard counts as a false slow down
GL_GUARD = 0.2

# DU3: the bound is chosen together with the threshold from this grid (development seeds only)
DU_THRESHOLDS = (0.40, 0.45, 0.50, 0.55, 0.60, 0.65)
DU_SCANS = (3, 5)
DU_BOUNDS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)

# Heat (H1 to H6)
T_H = 5.0        # K, open loop prediction error allowed per component (AC-H1)
Q_H = 0.9        # fraction of runs within T_H (AC-H1)
F_H = 1.2        # allowed factor on the required stopping distance at heat soak (AC-H2)
M_H = 5.0        # K, controller margin below each hard limit (used by the method, AC-H3)
SOAK_WAIT_MIN = 10.0   # minutes, prediction threshold for the first move after a sun soak (H6)
