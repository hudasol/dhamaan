"""Acceptance criteria parameters, fixed before any evaluation run (see sim/PREREGISTRATION.md).

These values name the symbols left open in docs/GULF_TEST_PROTOCOL.md sections 5.4, 6.4 and 7.4.
They are proposal values chosen by the authors for a synthetic study, not values from any source.
Changing a value after results exist is a deviation and goes in sim/DEVIATIONS.md.
"""
# DU3 / AC-DU1, AC-DU2
B_D = 0.4        # degradation bound up to which the detector alone must detect in time
T_D = 1.0        # s, beyond B_D the monitor must stop the robot within this time of onset

# GL3 / AC-GL1, AC-GL2, AC-GL3
P_G = 0.95       # in time detection rate required at each sun condition
S_G = 0.3        # saturation threshold (also the monitor threshold)
T_G = 0.5        # s, slow command must follow the first frame above S_G within this time

# N2 to N4 / AC-N1, AC-N2, AC-N3 (sizes at or above E_N must be covered)
E_N = {"jump": 5.0, "drift": 0.2, "noise": 5.0, "replay": 5.0, "loss": 0.0}
T_N = 10.0       # s, detection time after fault onset
Q_N = 0.9        # fraction of seeded runs that must detect within T_N
L_N = 3.0        # m, navigation error limit before the safe state is reached
