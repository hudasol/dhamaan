"""Seeds, labels and output for round 2."""
from __future__ import annotations

import os, zlib

import numpy as np

from sim import common

DEV_SEED = 770001          # development seed set: design only
HELDOUT_SEED = 20261018    # held out seed set: scoring only, never read by a design step
SEEDS = 30
RESULTS = os.path.join(common.ROOT, "sim", "results_r2")
PREREG = "sim/PREREGISTRATION_R2.md"
ASSUMED = "assumed, proposal"


def rng(seed_set: int, experiment: str, condition: str, i: int) -> np.random.Generator:
    """Generator keyed by seed set, experiment, condition and seed index (not by method)."""
    key = [seed_set, zlib.crc32(experiment.encode()), zlib.crc32(condition.encode()), i]
    return np.random.default_rng(np.random.SeedSequence(key))


def prereg_sha() -> str | None:
    p = os.path.join(common.ROOT, PREREG)
    return common.file_sha256(PREREG) if os.path.exists(p) else None


def envelope(experiment: str, items: list[str], seed_set: str, config: dict, conditions: dict, summary: dict) -> dict:
    return {"label": common.LABEL, "evidence_kind": common.EVIDENCE_KIND, "round": 2, "experiment": experiment,
            "protocol_items": items, "seed_set": seed_set,
            "seed_base": DEV_SEED if seed_set == "development" else HELDOUT_SEED, "seeds_per_condition": SEEDS,
            "prereg_sha256": prereg_sha(), "config": config, "conditions": conditions, "summary": summary}


def write(name: str, obj: dict) -> str:
    os.makedirs(RESULTS, exist_ok=True)
    path = os.path.join(RESULTS, name)
    with open(path, "w", encoding="utf-8", newline="\n") as f: f.write(common.dump(obj))
    return path
