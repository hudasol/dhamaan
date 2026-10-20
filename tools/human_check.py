#!/usr/bin/env python3
"""Human gold check of the evidence table: draw a seeded stratified sample, then score the owner's readings.

Layer: tools. Standard library only.

    python tools/human_check.py draw  [--seed 20261020] [--outdir data/human_check]
    python tools/human_check.py score [--outdir data/human_check] [--worksheet worksheet_completed.csv]

Why this exists. Every earlier check of the table was done by automated verifiers from one model family, so their
errors can repeat. This check puts a person, reading the source themselves, against the table.

Design (fixed before any reading, see data/human_check/DESIGN.md):
- Strata are the four binding statuses. Allocation is 20 mandatory, 20 conditional, 10 guidance, 10 voluntary.
- Rows are drawn without replacement with a seeded generator and split into two waves of 30 that are each
  stratified in the same proportions, so the first 30 rows are a valid sample on their own.
- The worksheet hides the table's binding status and access level, so the reader assigns them from the source.
  Blinding is by omission only: the table is public.
- Headline error: a row has a content error if the reader marks the paraphrase "partly" or "no", or assigns a
  binding status different from the table. Access overclaim is reported separately.
- Estimates are stratified (weights N_h / N) with a seeded percentile bootstrap interval, plus Wilson intervals per stratum.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TABLE = os.path.join(ROOT, "data", "evidence_table.csv")
RESULTS = os.path.join(ROOT, "data", "verification", "results")

ALLOCATION = {"mandatory": 20, "conditional": 20, "guidance": 10, "voluntary": 10}
WAVES = 2
BINDING = ("mandatory", "conditional", "voluntary", "guidance")
ACCESS_RANK = {"title only": 0, "summary seen": 1, "full text seen": 2}
PARA = ("yes", "partly", "no", "cannot_open_source")
BIND_REPLY = BINDING + ("cannot_tell",)
ACCESS_REPLY = ("full text", "summary", "title only", "could_not_open")
ACCESS_TO_TABLE = {"full text": "full text seen", "summary": "summary seen", "title only": "title only"}
SHOW = ("instrument", "edition_or_version", "clause_or_section_seen", "requirement_paraphrase", "applies_to", "source_url")
RESPONSE = ("paraphrase_supported", "binding_assigned", "access_achieved", "locator_found", "minutes", "notes")


def read_csv(path: str) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: str, rows: list[dict], fields: list[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------------------------------------
# draw
# ---------------------------------------------------------------------------------------------

def draw_sample(table: list[dict], seed: int) -> list[dict]:
    """Return sample rows with stratum, wave and position. Deterministic for a given table and seed."""
    rng = random.Random(seed)
    sample: list[dict] = []
    for stratum in BINDING:
        pool = sorted(r["id"] for r in table if r["binding_status"] == stratum)
        n = ALLOCATION[stratum]
        if n > len(pool):
            raise ValueError(f"stratum {stratum} has {len(pool)} rows, allocation is {n}")
        if n % WAVES:
            raise ValueError("allocation must split evenly across waves")
        chosen = rng.sample(pool, n)
        per_wave = n // WAVES
        for i, rid in enumerate(chosen):
            sample.append({"id": rid, "stratum": stratum, "wave": i // per_wave + 1, "stratum_size": len(pool)})
    # reading order: wave 1 first, then wave 2, mixed strata inside a wave, seeded
    order = sorted(sample, key=lambda s: (s["wave"], rng.random()))
    for pos, s in enumerate(order, 1):
        s["position"] = pos
    return order


def cmd_draw(args: argparse.Namespace) -> int:
    table = {r["id"]: r for r in read_csv(TABLE)}
    sample = draw_sample(list(table.values()), args.seed)
    out = os.path.join(ROOT, args.outdir)
    write_csv(os.path.join(out, "sample_frame.csv"), sample, ["position", "wave", "stratum", "stratum_size", "id"])
    sheet = []
    for s in sample:
        row = table[s["id"]]
        item = {"position": s["position"], "wave": s["wave"], "id": s["id"]}
        item.update({k: row[k] for k in SHOW})
        item.update({k: "" for k in RESPONSE})
        sheet.append(item)
    fields = ["position", "wave", "id", *SHOW, *RESPONSE]
    if os.path.exists(os.path.join(out, "worksheet_completed.csv")):
        print("worksheet_completed.csv exists; refusing to redraw over a finished check")
        return 1
    write_csv(os.path.join(out, "worksheet.csv"), sheet, fields)
    print(f"drew {len(sample)} rows with seed {args.seed}: {dict((k, ALLOCATION[k]) for k in BINDING)}")
    print(f"wrote sample_frame.csv, worksheet.csv in {args.outdir}")
    return 0


# ---------------------------------------------------------------------------------------------
# statistics
# ---------------------------------------------------------------------------------------------

def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def cohen_kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    if n == 0:
        return float("nan")
    cats = sorted(set(a) | set(b))
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def stratified_estimate(flags: dict[str, list[int]], sizes: dict[str, int]) -> float:
    total = sum(sizes[h] for h in flags if flags[h])
    if total == 0:
        return float("nan")
    return sum(sizes[h] / total * (sum(v) / len(v)) for h, v in flags.items() if v)


def bootstrap_ci(flags: dict[str, list[int]], sizes: dict[str, int], seed: int, reps: int = 10000) -> tuple[float, float]:
    rng = random.Random(seed)
    est = []
    for _ in range(reps):
        res = {h: [rng.choice(v) for _ in v] for h, v in flags.items() if v}
        est.append(stratified_estimate(res, sizes))
    est.sort()
    return (est[int(0.025 * reps)], est[int(0.975 * reps) - 1])


def agent_flags() -> dict[str, bool]:
    """True where either blind agent pass (A or B) judged the paraphrase partly or unsupported."""
    flagged: dict[str, bool] = {}
    if not os.path.isdir(RESULTS):
        return flagged
    for name in sorted(os.listdir(RESULTS)):
        if not name.startswith(("A_", "B_")):
            continue
        for r in read_csv(os.path.join(RESULTS, name)):
            flagged[r["id"]] = flagged.get(r["id"], False) or r["para_verdict"] in ("partly", "unsupported")
    return flagged


def score_rows(sheet: list[dict], table: dict[str, dict], frame: dict[str, dict], seed: int = 20261020) -> dict:
    """Score completed worksheet rows. Pure function: no file access, so it can be tested on synthetic data."""
    sizes: dict[str, int] = {}
    for r in table.values():
        sizes[r["binding_status"]] = sizes.get(r["binding_status"], 0) + 1
    done = [r for r in sheet if r.get("paraphrase_supported", "").strip()]
    flags: dict[str, list[int]] = {h: [] for h in BINDING}
    para_flags: dict[str, list[int]] = {h: [] for h in BINDING}
    bind_pairs: list[tuple[str, str]] = []
    overclaim, openable, unreadable = 0, 0, 0
    agent = agent_flags()
    two_by_two = {"human_err_agent_flag": 0, "human_err_agent_clean": 0, "human_ok_agent_flag": 0, "human_ok_agent_clean": 0}
    for r in done:
        rid = r["id"].strip()
        stratum = frame[rid]["stratum"]
        row = table[rid]
        para = r["paraphrase_supported"].strip()
        if para == "cannot_open_source":
            unreadable += 1
            continue
        bind = r.get("binding_assigned", "").strip()
        para_bad = int(para in ("partly", "no"))
        bind_bad = int(bind in BINDING and bind != row["binding_status"])
        if bind in BINDING:
            bind_pairs.append((row["binding_status"], bind))
        flags[stratum].append(int(para_bad or bind_bad))
        para_flags[stratum].append(para_bad)
        got = ACCESS_TO_TABLE.get(r.get("access_achieved", "").strip())
        if got:
            openable += 1
            overclaim += int(ACCESS_RANK[got] < ACCESS_RANK[row["access_level"]])
        if rid in agent:
            key = ("human_err" if (para_bad or bind_bad) else "human_ok") + ("_agent_flag" if agent[rid] else "_agent_clean")
            two_by_two[key] += 1
    n_scored = sum(len(v) for v in flags.values())
    per_stratum = {}
    for h in BINDING:
        k, n = sum(flags[h]), len(flags[h])
        lo, hi = wilson(k, n)
        per_stratum[h] = {"n": n, "errors": k, "rate": (k / n if n else None), "wilson95": [lo, hi], "population": sizes.get(h, 0)}
    est = stratified_estimate(flags, sizes)
    ci = bootstrap_ci(flags, sizes, seed) if n_scored else (float("nan"), float("nan"))
    est_para = stratified_estimate(para_flags, sizes)
    return {
        "rows_in_worksheet": len(sheet), "rows_read": len(done), "could_not_open_source": unreadable, "rows_scored": n_scored,
        "content_error_rate_stratified": est, "content_error_ci95_bootstrap": list(ci),
        "paraphrase_issue_rate_stratified": est_para,
        "per_stratum": per_stratum,
        "binding_agreement": (sum(a == b for a, b in bind_pairs) / len(bind_pairs) if bind_pairs else None),
        "binding_kappa": cohen_kappa([a for a, _ in bind_pairs], [b for _, b in bind_pairs]),
        "access_overclaim": {"rows_where_source_opened": openable, "overclaimed": overclaim},
        "agent_flag_vs_human_error": two_by_two,
        "note": "Single reader. Estimates describe the table as of the draw; the interval reflects sampling only, not reader error.",
    }


def cmd_score(args: argparse.Namespace) -> int:
    out = os.path.join(ROOT, args.outdir)
    table = {r["id"]: r for r in read_csv(TABLE)}
    frame = {r["id"]: r for r in read_csv(os.path.join(out, "sample_frame.csv"))}
    sheet = read_csv(os.path.join(out, args.worksheet))
    bad = [r["id"] for r in sheet if r["id"] not in frame]
    if bad:
        print("ids not in the sample frame:", bad)
        return 1
    result = score_rows(sheet, table, frame)
    path = os.path.join(out, "human_check_results.json")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps({k: result[k] for k in ("rows_read", "rows_scored", "content_error_rate_stratified", "content_error_ci95_bootstrap", "binding_kappa")}, indent=1))
    print("wrote", os.path.relpath(path, ROOT))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("draw")
    d.add_argument("--seed", type=int, default=20261020)
    d.add_argument("--outdir", default="data/human_check")
    s = sub.add_parser("score")
    s.add_argument("--outdir", default="data/human_check")
    s.add_argument("--worksheet", default="worksheet_completed.csv")
    args = ap.parse_args(argv)
    return {"draw": cmd_draw, "score": cmd_score}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
