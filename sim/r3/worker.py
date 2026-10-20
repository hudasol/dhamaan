"""Apply one mutant to the model and rerun rounds 1 and 2 in memory, then score the committed predictions.

Run in a fresh interpreter, so a patch can never leak into another mutant or into a committed result:

    python -m sim.r3.worker '{"id": "M0", "set": {}, "monitor": "M0"}'

Nothing is written to disk. The scored verdicts are printed as one JSON line. The predictions and acceptance
criteria are the committed ones (sim/predictions.py and sim/r2/predictions_r2.py), read after the patch, so a
changed acceptance value changes the criterion as it was written, with the new number.
"""
from __future__ import annotations

import dataclasses, json, sys

SPEC_KEYS = ("id", "set", "monitor", "onset")


def _patch_config(cls, name, value):
    setattr(cls, name, value)
    names = [f.name for f in dataclasses.fields(cls)]
    cls.__init__.__defaults__ = tuple(getattr(cls, n) for n in names)


def apply(spec: dict) -> None:
    """Patch constants first, then import the experiment modules, so nothing captures an unpatched default."""
    from sim import acceptance as A, common
    from sim.r2 import acceptance_r2 as A2
    sets = dict(spec.get("set", {}))
    sets.update(spec.get("monitor_set", {}))
    for pid, value in sets.items():
        tag, name = pid.split(".", 1)
        if tag == "acc":
            if isinstance(value, dict): getattr(A, name).update(value)
            else: setattr(A, name, value)
        elif tag == "acc2": setattr(A2, name, value)
    from sim import du3_lidar, gl3_glare, gnss_n2n4
    cfgs = {"du3": du3_lidar.Config, "gl3": gl3_glare.Config, "gnss": gnss_n2n4.Config, "stopping": common.Stopping}
    for pid, value in sets.items():
        tag, name = pid.split(".", 1)
        if tag in cfgs: _patch_config(cfgs[tag], name, value)
    from sim.r2 import heat
    for pid, value in sets.items():
        tag, name = pid.split(".", 1)
        if tag != "heat": continue
        if "." in name:
            comp, field = name.split(".")
            from sim.r3.params import COMPONENT_FIELDS
            vals = list(heat.COMPONENTS[comp]); vals[COMPONENT_FIELDS.index(field)] = value
            heat.COMPONENTS[comp] = tuple(vals)
        else: setattr(heat, name, value)


def apply_monitor_wrappers(mode: str | None) -> None:
    """M0: the monitor never raises an alarm. M1: it raises an alarm at the first chance. Baselines are untouched."""
    if mode not in ("M0", "M1"): return
    from sim.r2 import du3_r2, gl3_r2, heat
    if mode == "M0":
        du3_r2.monitor_stop = lambda run, h, n: None
        orig = gl3_r2.run_one; gl3_r2.run_one = lambda cfg, s0, th, fr, rng, stop: orig(cfg, s0, th, 10 ** 9, rng, stop)
        oc = heat.controller; heat.controller = lambda m, temps, t, peak, sun: 1.0 if m == "M" else oc(m, temps, t, peak, sun)
    else:
        du3_r2.monitor_stop = lambda run, h, n: run["t"][n - 1] if len(run["t"]) >= n else None
        orig = gl3_r2.run_one; gl3_r2.run_one = lambda cfg, s0, th, fr, rng, stop: orig(cfg, s0, th, 0, rng, stop)
        oc = heat.controller; heat.controller = lambda m, temps, t, peak, sun: 0.0 if m == "M" else oc(m, temps, t, peak, sun)


def run_and_score() -> dict:
    from sim import du3_lidar, gl3_glare, gnss_n2n4, score
    from sim.r2 import base, du3_r2, gl3_r2, heat, n4_r2, score_r2
    r1 = {"du3": du3_lidar.run(cfg=du3_lidar.Config()), "gl3": gl3_glare.run(cfg=gl3_glare.Config()),
          "gnss": gnss_n2n4.run(cfg=gnss_n2n4.Config())}
    s1 = score.score(r1)
    d = {"design_gl3": gl3_r2.design(), "design_du3": du3_r2.design()}
    r2 = dict(d)
    r2["gl3r2"] = gl3_r2.score(d["design_gl3"]["chosen"])
    r2["du3r2"] = du3_r2.score(d["design_du3"]["chosen"])
    r2["heat"] = heat.score()
    r2["n4r2"] = n4_r2.score()
    s2 = score_r2.score_r2(r2)
    def pack(s):
        return {"predictions": {p["id"]: [p["verdict"], p["held"]] for p in s["predictions"]},
                "acceptance": {a["id"]: [a["verdict"], a["held"]] for a in s["acceptance"]}, "totals": s["totals"]}
    return {"round1": pack(s1), "round2": pack(s2),
            "design_r2": {"gl3": d["design_gl3"]["chosen"], "du3": d["design_du3"]["chosen"]}}


def main(argv: list[str]) -> int:
    spec = json.loads(argv[1])
    try:
        # onset shift mutant M3 is a set of ordinary parameters, applied through the same path
        apply(spec)
        apply_monitor_wrappers(spec.get("monitor"))
        out = {"id": spec["id"], "result": run_and_score()}
    except Exception as e:                       # a mutant that breaks the model is reported, not hidden
        out = {"id": spec["id"], "error": f"{type(e).__name__}: {e}"}
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
