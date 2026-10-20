"""Turn mutant outcomes into the informativeness table and the sensitivity tables (pure functions, tested on SYNTHETIC fixtures)."""
from __future__ import annotations

import csv, json, os

from sim import common
from sim.r3 import params


def _items() -> dict[str, dict]:
    from sim.predictions import ACCEPTANCE as A1, PREDICTIONS as P1
    from sim.r2.predictions_r2 import ACCEPTANCE as A2, PREDICTIONS as P2
    out = {}
    for rnd, kind, rows in (("round1", "prediction", P1), ("round2", "prediction", P2), ("round1", "acceptance", A1), ("round2", "acceptance", A2)):
        for r in rows: out[(rnd, kind, r["id"])] = {"round": rnd, "kind": kind, "id": r["id"], "text": r["text"]}
    return out


def analyse(specs: list[dict], outs: list[dict], items: dict | None = None) -> dict:
    """Compare each mutant with ORIG. A change is any difference in the verdict (predictions) or in whether the criterion held."""
    items = items or _items()
    by_id = {o["id"]: o for o in outs}; spec_by = {s["id"]: s for s in specs}
    orig = by_id["ORIG"]["result"]
    ok = [s for s in specs if s["class"] != "orig" and "result" in by_id[s["id"]]]
    def val(res, rnd, kind, iid):
        return res[rnd]["predictions" if kind == "prediction" else "acceptance"][iid]
    rows = []
    for (rnd, kind, iid), meta in items.items():
        o = val(orig, rnd, kind, iid); idx = 0 if kind == "prediction" else 1
        changed = {s["id"] for s in ok if val(by_id[s["id"]]["result"], rnd, kind, iid)[idx] != o[idx]}
        cls = {c: sorted(i for i in changed if spec_by[i]["class"] == c) for c in ("M0", "M1", "M2", "M3")}
        rows.append(meta | {"original": o[idx], "changed_under": len(changed), "M0": bool(cls["M0"]), "M1": bool(cls["M1"]),
                            "M2_changes": len(cls["M2"]), "M3": bool(cls["M3"]),
                            "informative": bool(changed), "first_changes": ";".join(sorted(changed)[:3]),
                            "model_params": sorted({spec_by[i]["param"] for i in cls["M2"] if spec_by[i]["kind"] != "acceptance"}),
                            "acceptance_params": sorted({spec_by[i]["param"] for i in cls["M2"] if spec_by[i]["kind"] == "acceptance"})})
    preds = [r for r in rows if r["kind"] == "prediction"]
    inf = [r for r in preds if r["informative"]]
    inf_model = [r for r in preds if r["model_params"] or r["M0"] or r["M1"] or r["M3"]]
    hit = lambda rs: sum(r["original"] == "HIT" for r in rs)
    summary = {"predictions": len(preds), "hit": hit(preds), "informative": len(inf), "informative_hit": hit(inf),
               "uninformative": len(preds) - len(inf),
               "informative_model_changes_only": len(inf_model), "informative_model_changes_only_hit": hit(inf_model),
               "uninformative_ids": sorted(r["id"] for r in preds if not r["informative"]),
               "mutants_run": len(ok), "mutants_failed": sorted(i for i, o in by_id.items() if "error" in o),
               "mutants_skipped_no_change": sorted(i for i, o in by_id.items() if "skipped" in o)}
    # sensitivity: criteria that held in the original, flips under M2 at 0.5 or 1.5
    sens = []
    for r in rows:
        if r["kind"] != "acceptance": continue
        for s in ok:
            if s["class"] != "M2": continue
            nw = val(by_id[s["id"]]["result"], r["round"], "acceptance", r["id"])[1]
            if nw != val(orig, r["round"], "acceptance", r["id"])[1]:
                sens.append({"round": r["round"], "criterion": r["id"], "parameter": s["param"], "kind": s["kind"], "factor": s["factor"],
                             "value": s["value"] if not isinstance(s["value"], dict) else "scaled", "original_held": val(orig, r["round"], "acceptance", r["id"])[1],
                             "mutated_held": nw})
    return {"rows": rows, "summary": summary, "sensitivity": sens}


def _write_csv(path, rows, fields):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n", extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    return path


def write_all(specs, outs, out_dir) -> list[str]:
    a = analyse(specs, outs)
    paths = []
    inf_rows = [{"evidence_kind": "simulated", **{k: r[k] for k in ("round", "kind", "id", "text", "original", "informative", "changed_under", "M0", "M1", "M2_changes", "M3", "first_changes")},
                 "model_parameters_that_change_it": ";".join(r["model_params"]), "acceptance_parameters_that_change_it": ";".join(r["acceptance_params"])} for r in a["rows"]]
    paths.append(_write_csv(os.path.join(out_dir, "informativeness.csv"), inf_rows, list(inf_rows[0])))
    paths.append(_write_csv(os.path.join(out_dir, "sensitivity.csv"), [{"evidence_kind": "simulated", **s} for s in a["sensitivity"]],
                            ["evidence_kind", "round", "criterion", "parameter", "kind", "factor", "value", "original_held", "mutated_held"]))
    plist = [{"id": p["id"], "kind": p["kind"], "base": json.dumps(p["base"]), "integer": p["integer"]} for p in params.list_parameters()]
    paths.append(_write_csv(os.path.join(out_dir, "parameters.csv"), plist, ["id", "kind", "base", "integer"]))
    paths.append(_write_csv(os.path.join(out_dir, "parameters_excluded.csv"), [{"id": k, "reason": r} for k, r in sorted(params.list_parameters.skipped and {s["id"]: s["reason"] for s in params.list_parameters.skipped}.items())], ["id", "reason"]))
    summ = {"label": common.LABEL, "evidence_kind": common.EVIDENCE_KIND, "round": 3, "part": "A and B",
            "factors": [0.5, 1.5], "parameters": len(plist), "mutants": len(specs)} | a["summary"]
    p = os.path.join(out_dir, "summary.json")
    with open(p, "w", encoding="utf-8", newline="\n") as f: f.write(common.dump(summ))
    paths.append(p)
    return paths
