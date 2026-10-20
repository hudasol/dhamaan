# Specification for an independently written GNSS fault generator (round 3, Part D)

Status: written before the second author starts. The second author receives only this page. They do not receive the monitor code, the thresholds, the acceptance criteria, any earlier result or any other file of this repository. All logs are SYNTHETIC.

## Purpose

Our own generator and our own monitor share an author. This page asks a second author to write a generator from a description, so that we can ask whether the monitor gives the same verdicts on data it was not tuned on. The monitor is not described here and must not be inferred.

## Scenario

A ground robot drives in a straight line along the positive x axis at a constant true speed of 0.8 m/s for 120 s. It starts at the origin; true y is 0 throughout. A satellite positioning receiver reports a position fix once per second. Wheel odometry reports speed and heading ten times per second.

## Receiver and odometry errors (central values, nominal case)

- Each fix has independent Gaussian error per axis with standard deviation 1.0 m.
- Odometry speed equals the true speed times a scale factor drawn once per run (mean 1, standard deviation 0.01), plus independent Gaussian noise of standard deviation 0.02 m/s at every sample.
- Odometry heading is a random walk with increments of standard deviation 0.001 rad per square root of a second, starting at 0 rad.

The author may choose any detail not stated here, and should write down what they chose.

## Fault classes (applied to the fix stream only, from onset at t = 30 s)

| Kind | Size | Behaviour from onset |
|---|---|---|
| nominal | none | no fault |
| loss | none | no fix is delivered after onset |
| noise | target standard deviation 3, 5 or 10 m | error standard deviation grows linearly from 1 m to the target over 20 s, then stays |
| jump | 2, 5, 10 or 20 m | a constant offset of that size, in a direction drawn at random once per run |
| drift | 0.05, 0.1, 0.2 or 0.5 m/s | an offset that starts at zero at onset and grows at that rate, in a direction drawn at random once per run |
| replay | delay 2, 5 or 10 s | each fix reports a position that was genuine that many seconds earlier: the true position at the earlier time plus ordinary receiver error |

Faults act at measurement level only. No radio frequency signal of any kind is generated or modelled.

## Output format

Two tables, as lists of dictionaries with these keys, floats unless stated.

GNSS table, one row per second from t = 0 to t = 120 inclusive (121 rows, fewer after onset for kind loss, where rows are omitted):
`t_s`, `x_m`, `y_m` (the reported fix), `fix_ok` (1.0 for a delivered fix), `x_ref_m`, `y_ref_m` (the true position at that time, never faulted).

Odometry table, one row per 0.1 s from t = 0 to t = 120 inclusive (1201 rows):
`t_s`, `v_mps` (reported speed), `yaw_rad` (reported heading).

## Interface

A single Python module using only the standard library and numpy, with:

`generate(kind: str, size: float, seed: int) -> tuple[list[dict], list[dict]]`

returning the GNSS table and the odometry table. `kind` is one of nominal, loss, noise, jump, drift, replay. `size` is ignored for nominal and loss. The result must be a deterministic function of (kind, size, seed). Different seeds must give independent runs.

## What to report back

The path of the module, a short list of every choice made where this page was silent, and any statement on this page that was unclear.
