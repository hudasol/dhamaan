"""POST HOC analysis of the recorded arm, written after the frozen run and after an independent review. Not preregistered.

It does not replace or change the frozen results. It answers three questions the review raised: how the false alarm rate depends on receiver
motion, how much of it comes from one recording whose trailing nominal segment contains real interference, and how wide the interval is when
recordings, and not alarms, are the unit of resampling. The M variant with larger process noise is a sensitivity probe, not a new monitor.

    python -m sim.r3.post_hoc --data PATH_TO_EXTRACTED_DATASET
"""
from __future__ import annotations

import argparse, dataclasses, json, os, sys

import numpy as np

from sim import common, gnss_n2n4 as G
from sim.r2 import replay
from sim.r3 import detectors as D, jammertest as J

OUT = os.path.join("sim", "results_r3", "recorded", "post_hoc.json")
LABEL = ("POST HOC and not preregistered. Computed after the frozen recorded run and an independent review, on the same recorded data "
         "(Jammertest campaign, Andoya, Norway). Does not replace the frozen results.")
CONTAMINATED = "1.11.7"          # trailing nominal segment overlaps real interference (receiver state: satellites lost, jamming indicator high)
STILL_MPS = 0.3
BOOT = 2000


def alarm_m(q_step):
    cfg = dataclasses.replace(G.Config(), q_step=q_step)
    def f(fixes, rf, a, b, params):
        fx = [x for x in fixes if a - 1e-9 <= x["t_s"] <= b + 1e-9]
        k = next((i for i, x in enumerate(fx) if x["fix_ok"]), None)
        if k is None: return None
        fx = fx[k:]
        if fx[-1]["t_s"] - fx[0]["t_s"] < 2 * cfg.dt: return None
        odo = J.odometry(fixes, fx[0]["t_s"], fx[-1]["t_s"], cfg.dt)
        g = [{"t_s": x["t_s"], "x_m": x["x_m"], "y_m": x["y_m"], "fix_ok": x["fix_ok"]} for x in fx]
        return replay.score_log(g, odo, cfg)["t_alarm"]
    return f


def run(data: str, out: str = OUT) -> dict:
    D.FIRST_ALARM["M-q1"] = alarm_m(1.0)
    names = ("M", "M-q1", "D-RX", "D-JUMP", "D-NIS")
    rows = []
    for rel in J.discover(data):
        rec = J.load(data, rel)
        if not rec["session"]: continue
        seg = J.segments(rec)
        for key in ("leading", "trailing"):
            if not seg[key]: continue
            a, b = seg[key]
            sp = [x["speed"] for x in rec["fixes"] if a <= x["t_s"] <= b and x["fix_ok"]]
            if len(sp) < 10: continue
            reg = "still" if float(np.median(sp)) < STILL_MPS else "moving"
            r = {"id": rec["id"], "segment": key, "seconds": b - a, "regime": reg, "contaminated": rec["id"].endswith("/" + CONTAMINATED) and key == "trailing", "alarms": {}}
            for n in names: r["alarms"][n] = len(D.run_episodes(n, rec["fixes"], rec["rf"], a, b, {}))
            rows.append(r)
    def rate(sel, n):
        k = sum(r["alarms"][n] for r in sel); h = sum(max(0.0, r["seconds"] - D.REARM_S * r["alarms"][n]) for r in sel) / 3600.0
        return {"alarms": k, "exposure_hours": h, "per_hour": (k / h) if h > 0 else None, "segments": len(sel), "recordings": len({r["id"] for r in sel})}
    def boot(sel, n):
        ids = sorted({r["id"] for r in sel}); rng = common.rng_for("R3POSTHOC", n, len(ids)); vals = []
        if not ids: return [None, None]
        for _ in range(BOOT):
            pick = rng.choice(len(ids), len(ids)); s = [r for i in pick for r in sel if r["id"] == ids[i]]
            v = rate(s, n)["per_hour"]
            if v is not None: vals.append(v)
        return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))] if vals else [None, None]
    sets = {"all_segments": rows, "excluding_contaminated_segment": [r for r in rows if not r["contaminated"]],
            "still_only": [r for r in rows if r["regime"] == "still" and not r["contaminated"]],
            "moving_only": [r for r in rows if r["regime"] == "moving" and not r["contaminated"]]}
    res = {"label": LABEL, "still_threshold_mps": STILL_MPS, "contaminated_recording": CONTAMINATED, "bootstrap": f"{BOOT} resamples of recordings",
           "sets": {s: {n: rate(sel, n) | {"ci95_recording_bootstrap": boot(sel, n)} for n in names} for s, sel in sets.items()},
           "segments": rows}
    open(os.path.join(common.ROOT, out), "w", encoding="utf-8", newline="\n").write(common.dump(res))
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); a = ap.parse_args(argv)
    r = run(a.data)
    for s, d in r["sets"].items():
        print(s, {n: (v["alarms"], round(v["exposure_hours"], 3), None if v["per_hour"] is None else round(v["per_hour"], 2)) for n, v in d.items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
