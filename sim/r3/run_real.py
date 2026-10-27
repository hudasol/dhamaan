"""Runner for the recorded arm of round three.

    python -m sim.r3.run_real --data PATH_TO_EXTRACTED_DATASET            score (refuses unless the plan freeze is valid)
    python -m sim.r3.run_real --freeze                                    write data/r3_recorded/PLAN_FREEZE.json (before the first run)
    python -m sim.r3.run_real --verify                                    check the freeze and exit

The freeze file holds the SHA-256 of docs/ANALYSIS_PLAN_R3_RECORDED.md and of the code that scores the recordings. If either
differs at scoring time the run is refused; a change after the freeze is a deviation (sim/DEVIATIONS.md) and the freeze is
rewritten with a new hash and the old one kept in the file.
"""
from __future__ import annotations

import argparse, csv, hashlib, json, os, subprocess, sys
from datetime import datetime, timezone

from sim import common
from sim.r3 import detectors as D, jammertest as J, real_score as S, recorded

ROOT = common.ROOT
PLAN = "docs/ANALYSIS_PLAN_R3_RECORDED.md"
FREEZE = "data/r3_recorded/PLAN_FREEZE.json"
OUT = os.path.join("sim", "results_r3", "recorded")
CODE_FILES = ["sim/r3/jammertest.py", "sim/r3/detectors.py", "sim/r3/real_score.py", "sim/r3/recorded.py", "sim/r3/run_real.py",
              "sim/gnss_n2n4.py", "sim/acceptance.py", "sim/r2/replay.py", "sim/common.py"]
SPLIT_SEED = 20261028
N_CALIBRATION = 12
DATASET = {"zenodo_record": "15911589", "archive": "GNSS_DATASET_JAMMING_SPOOFING.tar.gz", "md5": "c7b00c63bb1ee5db80c7692a2b06e169",
           "licence_stated": "GPL-3.0-or-later (as stated on the record page)", "site": "Andoya, Norway, September 2024"}
RECORDED_LABEL = ("RECORDED: receiver output of the Jammertest 2024 campaign (Andoya, Norway), controlled jamming, spoofing and meaconing. "
                  "One u-blox receiver. Not from the Gulf and not from a robot. Evidence kind: recorded. Session level labels only.")


def _sha(path: str) -> str:
    return hashlib.sha256(open(os.path.join(ROOT, path), "rb").read()).hexdigest()


def _git_head() -> str | None:
    try: return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except Exception: return None


def freeze_record() -> dict:
    return {"plan": PLAN, "plan_sha256": _sha(PLAN), "code_sha256": {f: _sha(f) for f in CODE_FILES},
            "git_head_at_freeze": _git_head(), "frozen_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "dataset": DATASET, "split_seed": SPLIT_SEED, "n_calibration": N_CALIBRATION, "fa_limit_per_hour": S.FA_LIMIT_PER_HOUR}


def write_freeze() -> str:
    p = os.path.join(ROOT, FREEZE); old = None
    if os.path.exists(p): old = json.load(open(p, encoding="utf-8"))
    rec = freeze_record()
    if old: rec["earlier_freezes"] = old.get("earlier_freezes", []) + [{k: old[k] for k in ("plan_sha256", "code_sha256", "frozen_utc")}]
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    return p


def verify_freeze(root: str = ROOT) -> list[str]:
    p = os.path.join(root, FREEZE)
    if not os.path.exists(p): return ["no plan freeze file; run --freeze before scoring"]
    fr = json.load(open(p, encoding="utf-8")); bad = []
    if _sha(PLAN) != fr["plan_sha256"]: bad.append("the analysis plan differs from the frozen text")
    for f, h in fr["code_sha256"].items():
        if _sha(f) != h: bad.append(f"code changed since the freeze: {f}")
    return bad


def run(data: str, out: str = OUT) -> dict:
    problems = verify_freeze()
    if problems: raise SystemExit("refused: " + "; ".join(problems))
    rels = J.discover(data)
    recs = [J.load(data, r) for r in rels]
    excluded = [{"id": r["id"], "reason": r["window_error"]} for r in recs if not r["session"]]
    recs = [r for r in recs if r["session"]]
    cal_ids, held_ids = recorded.split_recordings([r["id"] for r in recs], SPLIT_SEED, N_CALIBRATION)
    by = {r["id"]: r for r in recs}; cal = [by[i] for i in cal_ids]; held = [by[i] for i in held_ids]
    params = {"jam_threshold": S.calibrate_jam_threshold(cal)}
    scores = [S.record_scores(r, params) for r in recs]
    sc_by = {s["id"]: s for s in scores}
    agg = lambda ids, n: S.aggregate([sc_by[i] for i in ids], n)
    R_all = {n: agg([r["id"] for r in recs], n) for n in D.NAMES}
    R_held = {n: agg(held_ids, n) for n in D.NAMES}
    R_cal = {n: agg(cal_ids, n) for n in D.NAMES}
    cal_stats = S.nominal_stats(cal); held_stats = S.nominal_stats(held)
    S0 = S.synthetic_arm(None)
    S1 = S.synthetic_arm(cal_stats) if cal_stats else None
    preds = S.predictions({"S0": S0, "S1": S1 or S0, "R_held": R_held, "R_all": R_all, "nominal_held": held_stats}) if S1 else {"held": {}, "notes": {"all": "no calibration nominal segment"}}
    header = {"label": RECORDED_LABEL, "evidence_kind": "recorded", "dataset": DATASET, "plan_sha256": _sha(PLAN),
              "code_sha256": {f: _sha(f) for f in CODE_FILES}, "git_head": _git_head(), "split_seed": SPLIT_SEED,
              "calibration": cal_ids, "held_out": held_ids, "excluded": excluded, "jam_threshold": params["jam_threshold"],
              "recordings": len(recs), "nav_sha256": {r["id"]: hashlib.sha256(open(os.path.join(data, r["id"], "nav_pvt.csv"), "rb").read()).hexdigest() for r in recs}}
    os.makedirs(os.path.join(ROOT, out), exist_ok=True)
    def w(name, obj): open(os.path.join(ROOT, out, name), "w", encoding="utf-8", newline="\n").write(common.dump(obj))
    w("recorded_results.json", header | {"R_all": R_all, "R_held": R_held, "R_cal": R_cal, "nominal_error_calibration": cal_stats,
                                       "nominal_error_held_out": held_stats, "per_recording": scores})
    w("synthetic_arms.json", {"label": common.LABEL, "evidence_kind": common.EVIDENCE_KIND, "S0": S0, "S1": S1, "calibration_used_for_S1": cal_stats})
    w("predictions.json", {"label": RECORDED_LABEL, "predictions": preds["held"], "notes": preds["notes"], "plan_sha256": _sha(PLAN)})
    with open(os.path.join(ROOT, out, "detectors.csv"), "w", encoding="utf-8", newline="") as f:
        cw = csv.writer(f, lineterminator="\n")
        cw.writerow(["set", "detector", "sessions", "false_alarms", "exposure_hours", "false_alarms_per_hour", "session_detected", "session_n", "loss_events_detected", "loss_events", "AC-N1r", "AC-N4"])
        for label, table in (("all", R_all), ("held_out", R_held), ("calibration", R_cal)):
            for n, g in table.items():
                sd = g["session_detection"]["all"]; le = g["loss_of_fix_events"]
                cw.writerow([label, n, g["sessions"], g["false_alarms"]["alarms"], round(g["false_alarms"]["exposure_hours"], 4),
                             None if g["false_alarms"]["per_hour"] is None else round(g["false_alarms"]["per_hour"], 4), sd["k"], sd["n"], le["k"], le["n"],
                             g["verdicts"]["AC-N1r"], g["verdicts"]["AC-N4"]])
    return {"header": header, "R_all": R_all, "R_held": R_held, "S0": S0, "S1": S1, "predictions": preds}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data"); ap.add_argument("--freeze", action="store_true"); ap.add_argument("--verify", action="store_true")
    a = ap.parse_args(argv)
    if a.freeze: print("wrote", write_freeze()); return 0
    if a.verify:
        p = verify_freeze(); print("freeze ok" if not p else "; ".join(p)); return 1 if p else 0
    if not a.data: ap.error("--data is required to score")
    res = run(a.data); print("wrote", OUT, "; held out predictions:", res["predictions"]["held"]); return 0


if __name__ == "__main__":
    sys.exit(main())
