"""Loader for the Jammertest 2024 navigation data (Zenodo 15911589), following docs/ANALYSIS_PLAN_R3_RECORDED.md.

Nothing here reads the network and no recording is stored in the repository. Tests use SYNTHETIC folders made inside the test.
A recording is a scenario folder with nav_pvt.csv, mon_rf.csv and scenario.json; its identifier is the folder path under the
dataset root.
"""
from __future__ import annotations

import csv, json, math, os
from datetime import datetime, timedelta

import numpy as np

EARTH_R = 6371008.8
UTC_OFFSET_H = 2            # attack log times are local time; shifted back to UTC (plan, Windows)
GUARD_S = 120.0
MIN_SEGMENT_S = 60.0
DENIAL_RUN = 5
MIN_SV = 4
FIX_TYPE_MIN = 3
POSITION_SCALE = 1e7        # stored lat/lon are degrees times 1e-7 (plan, Streams)
TYPE_MAP = (("jamming+spoofing", "combined"), ("spoofing + jamming", "combined"), ("jamming", "jamming"),
            ("spoofing", "spoofing"), ("meaconing", "meaconing"))


def discover(root: str) -> list[str]:
    """Relative folder paths that hold a nav_pvt.csv, sorted."""
    out = []
    for dp, _dn, fn in os.walk(root):
        if "nav_pvt.csv" in fn: out.append(os.path.relpath(dp, root).replace(os.sep, "/"))
    return sorted(out)


def attack_type(text: str) -> str:
    t = (text or "").lower()
    for key, name in TYPE_MAP:
        if key in t: return name
    return "unknown"


def _ts(text: str) -> datetime:
    return datetime.fromisoformat(str(text).strip().replace("Z", "").replace(" ", "T"))


def _num(v, default=float("nan")) -> float:
    try: return float(v)
    except (TypeError, ValueError): return default


def _windows(sc: dict, t0: datetime) -> tuple[list[tuple[float, float]], str | None]:
    ev = []
    for e in sc.get("attack_log", []):
        try: ts = _ts(e["timestamp_utc"]) - timedelta(hours=UTC_OFFSET_H)
        except (KeyError, ValueError): return [], "unreadable attack log time"
        ev.append(((ts - t0).total_seconds(), str(e.get("event", "")).lower()))
    starts = [t for t, x in ev if "start" in x]; ends = [t for t, x in ev if "end" in x]
    if not starts or len(starts) != len(ends): return [], "start and end events do not pair"
    win = list(zip(starts, ends))
    if any(b <= a for a, b in win): return [], "an end precedes its start"
    return win, None


def _read(path: str) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f: return list(csv.DictReader(f))


def load(root: str, rel: str) -> dict:
    d = os.path.join(root, rel)
    sc = json.load(open(os.path.join(d, "scenario.json"), encoding="utf-8"))
    rows, seen = [], set()
    for r in _read(os.path.join(d, "nav_pvt.csv")):
        try: t = _ts(r["real_time"])
        except (KeyError, ValueError): continue
        if t in seen: continue
        seen.add(t); rows.append((t, r))
    rows.sort(key=lambda p: p[0])
    if not rows: raise ValueError(f"{rel}: no rows")
    t0 = rows[0][0]
    def valid_row(r):
        lat, lon = _num(r.get("lat")), _num(r.get("lon"))
        return _num(r.get("fixType"), 0) >= FIX_TYPE_MIN and _num(r.get("numSV"), 0) >= MIN_SV and math.isfinite(lat) and math.isfinite(lon)
    ok0 = next((i for i, (_, r) in enumerate(rows) if valid_row(r)), None)
    if ok0 is None: raise ValueError(f"{rel}: no valid fix")
    lat0 = _num(rows[ok0][1]["lat"]) * POSITION_SCALE; lon0 = _num(rows[ok0][1]["lon"]) * POSITION_SCALE
    fixes = []
    for t, r in rows:
        ok = valid_row(r)
        if ok:
            lat = _num(r["lat"]) * POSITION_SCALE; lon = _num(r["lon"]) * POSITION_SCALE
            x = EARTH_R * math.cos(math.radians(lat0)) * math.radians(lon - lon0); y = EARTH_R * math.radians(lat - lat0)
        else: x = y = 0.0
        fixes.append({"t_s": (t - t0).total_seconds(), "x_m": x, "y_m": y, "fix_ok": 1.0 if ok else 0.0, "h_acc": _num(r.get("hAcc"), 1e9),
                      "vel_n": _num(r.get("velN")) if ok else float("nan"), "vel_e": _num(r.get("velE")) if ok else float("nan"),
                      "speed": _num(r.get("gSpeed")) if ok else float("nan")})
    rf = []
    p = os.path.join(d, "mon_rf.csv")
    if os.path.exists(p):
        for r in _read(p):
            try: t = _ts(r["real_time"])
            except (KeyError, ValueError): continue
            vals = [v for v in (_num(r.get("jamInd_01")), _num(r.get("jamInd_02"))) if v == v]
            rf.append({"t_s": (t - t0).total_seconds(), "jam": max(vals) if vals else 0.0})
        rf.sort(key=lambda q: q["t_s"])
    win, err = _windows(sc, t0)
    ap = sc.get("attack_parameters", {})
    return {"id": rel, "scenario_id": sc.get("scenario_id"), "attack_type": attack_type(f'{sc.get("attack_type", "")}'),
            "rover_state_meta": ap.get("rover_states"), "t0": str(t0), "duration_s": fixes[-1]["t_s"], "fixes": fixes, "rf": rf,
            "windows": win, "window_error": err,
            "session": (min(a for a, _ in win), max(b for _, b in win)) if win else None}


def segments(rec: dict) -> dict:
    """Leading and trailing nominal segments, and the run region of the session (guard time included for warm up)."""
    if not rec["session"]: return {"leading": None, "trailing": None, "session_run": None}
    s, e = rec["session"]; end = rec["duration_s"]
    lead = (0.0, s - GUARD_S) if s - GUARD_S - 0.0 >= MIN_SEGMENT_S else None
    trail = (e + GUARD_S, end) if end - (e + GUARD_S) >= MIN_SEGMENT_S else None
    return {"leading": lead, "trailing": trail, "session_run": (max(0.0, s - GUARD_S), min(end, e))}


def odometry(fixes: list[dict], t_start: float, t_end: float, dt: float = 0.1) -> list[dict]:
    """Receiver velocity as an odometry substitute, held between epochs; the last valid value is kept when no fix is valid.
    Heading is atan2(north, east), measured from the east axis as the harness expects; kept when speed is below 0.2 m/s."""
    out, i, v, yaw = [], 0, 0.0, 0.0
    n = int(math.floor((t_end - t_start) / dt + 1e-9))
    for k in range(n + 1):
        t = t_start + k * dt
        while i < len(fixes) and fixes[i]["t_s"] <= t + 1e-9:
            f = fixes[i]; i += 1
            if f["fix_ok"] and f["vel_n"] == f["vel_n"] and f["vel_e"] == f["vel_e"]:
                v = math.hypot(f["vel_n"], f["vel_e"])
                if v >= 0.2: yaw = math.atan2(f["vel_n"], f["vel_e"])
        out.append({"t_s": round(t, 6), "v_mps": v, "yaw_rad": yaw})
    return out


def denial_events(rec: dict) -> list[float]:
    """Start times of runs of at least DENIAL_RUN consecutive invalid epochs that begin inside the session span."""
    if not rec["session"]: return []
    s, e = rec["session"]; out, run, start = [], 0, None
    for f in rec["fixes"]:
        if not f["fix_ok"]:
            if run == 0: start = f["t_s"]
            run += 1
            if run == DENIAL_RUN and s <= start <= e: out.append(start)
        else:
            run = 0
    return out


def nominal_error_rows(rec: dict, max_median_speed: float = 0.3, min_valid: int = 60) -> list[dict] | None:
    """Fix error rows (position minus the segment median) for the leading nominal segment, if the receiver was still and the segment long enough."""
    seg = segments(rec)["leading"]
    if seg is None: return None
    rows = [f for f in rec["fixes"] if seg[0] <= f["t_s"] <= seg[1] and f["fix_ok"]]
    if len(rows) < min_valid: return None
    if float(np.median([f["speed"] for f in rows])) >= max_median_speed: return None
    mx = float(np.median([f["x_m"] for f in rows])); my = float(np.median([f["y_m"] for f in rows]))
    return [{"t_s": f["t_s"], "x_m": f["x_m"], "y_m": f["y_m"], "x_ref_m": mx, "y_ref_m": my, "fix_ok": 1.0, "interference": 0.0} for f in rows]
