"""Shared pieces of the simulation harness: label, seeding, stopping model, statistics, output."""
from __future__ import annotations

import hashlib, json, math, os, zlib
from dataclasses import dataclass

import numpy as np

LABEL = ("SYNTHETIC: produced by a seeded software model in sim/. Not measured on any robot, sensor or "
         "receiver. The model and the method under test share an author. Evidence kind: simulated.")
EVIDENCE_KIND = "simulated"
BASE_SEED = 20261016
SEEDS_PER_CONDITION = 30
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RESULTS = os.path.join(ROOT, "sim", "results")


def rng_for(experiment: str, condition: str, seed_index: int) -> np.random.Generator:
    """Generator for one run. The method is not part of the key, so every method sees the same world."""
    key = [BASE_SEED, zlib.crc32(experiment.encode()), zlib.crc32(condition.encode()), seed_index]
    return np.random.default_rng(np.random.SeedSequence(key))


@dataclass(frozen=True)
class Stopping:
    """Simple braking model shared by DU3 and GL3 (proposal values, not measured)."""
    t_react: float = 0.3   # s, sensing to braking latency
    decel: float = 1.0     # m/s2
    margin: float = 0.2    # m

    def required(self, v: float) -> float:
        """Distance to the obstacle surface needed to stop with the margin at speed v."""
        return v * self.t_react + v * v / (2 * self.decel) + self.margin


def wilson(k: int, n: int, z: float = 1.959964) -> list[float]:
    """95 percent Wilson interval for a proportion k of n."""
    if n == 0: return [0.0, 1.0]
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0.0, c - h), min(1.0, c + h)]


def rate(flags: list[bool]) -> dict:
    k, n = int(sum(flags)), len(flags)
    return {"k": k, "n": n, "rate": k / n if n else None, "ci95": wilson(k, n)}


def mean_ci(xs: list[float]) -> dict:
    """Mean with a normal approximation 95 percent interval; None when there are no values."""
    a = np.asarray([x for x in xs if x is not None], dtype=float)
    if a.size == 0: return {"n": 0, "mean": None, "ci95": None, "median": None, "max": None}
    m = float(a.mean()); h = 1.959964 * float(a.std(ddof=1)) / math.sqrt(a.size) if a.size > 1 else 0.0
    return {"n": int(a.size), "mean": m, "ci95": [m - h, m + h], "median": float(np.median(a)), "max": float(a.max())}


def _round(o, nd=6):
    if isinstance(o, float): return round(o, nd)
    if isinstance(o, dict): return {k: _round(v, nd) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [_round(v, nd) for v in o]
    return o


def file_sha256(rel: str) -> str:
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def dump(obj: dict) -> str:
    return json.dumps(_round(obj), indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def write_result(name: str, obj: dict) -> str:
    os.makedirs(RESULTS, exist_ok=True)
    path = os.path.join(RESULTS, name)
    with open(path, "w", encoding="utf-8", newline="\n") as f: f.write(dump(obj))
    return path


def envelope(experiment: str, protocol_items: list[str], config: dict, conditions: dict, summary: dict) -> dict:
    """Common header written into every result file."""
    return {"label": LABEL, "evidence_kind": EVIDENCE_KIND, "experiment": experiment,
            "protocol_items": protocol_items, "base_seed": BASE_SEED, "seeds_per_condition": SEEDS_PER_CONDITION,
            "prereg_sha256": file_sha256("sim/PREREGISTRATION.md") if os.path.exists(os.path.join(ROOT, "sim/PREREGISTRATION.md")) else None,
            "config": config, "conditions": conditions, "summary": summary}
