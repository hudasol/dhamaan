"""Tests for tools/human_check.py. The scoring tests use SYNTHETIC worksheets made inside the test; they are not results."""
import csv
import importlib.util
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
spec = importlib.util.spec_from_file_location("human_check", os.path.join(ROOT, "tools", "human_check.py"))
hc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hc)


def table():
    return hc.read_csv(hc.TABLE)


def test_draw_is_deterministic_and_stratified():
    a = hc.draw_sample(table(), 20261020)
    b = hc.draw_sample(table(), 20261020)
    assert a == b
    assert len(a) == sum(hc.ALLOCATION.values()) == 60
    assert len({s["id"] for s in a}) == 60
    for stratum, n in hc.ALLOCATION.items():
        assert sum(s["stratum"] == stratum for s in a) == n


def test_each_wave_has_the_same_proportions():
    sample = hc.draw_sample(table(), 20261020)
    for wave in (1, 2):
        rows = [s for s in sample if s["wave"] == wave]
        assert len(rows) == 30
        for stratum, n in hc.ALLOCATION.items():
            assert sum(s["stratum"] == stratum for s in rows) == n // 2
    assert [s["wave"] for s in sample[:30]] == [1] * 30


def test_different_seed_gives_a_different_sample():
    assert [s["id"] for s in hc.draw_sample(table(), 1)] != [s["id"] for s in hc.draw_sample(table(), 2)]


def test_worksheet_hides_binding_and_access(tmp_path):
    out = tmp_path / "hc"
    ns = type("A", (), {"seed": 20261020, "outdir": str(out)})()
    ns.outdir = os.path.relpath(out, hc.ROOT)
    assert hc.cmd_draw(ns) == 0
    with open(out / "worksheet.csv", encoding="utf-8", newline="") as f:
        header = next(csv.reader(f))
    assert "binding_status" not in header and "access_level" not in header
    assert "verification_status" not in header and "notes" in header  # response column only
    for col in hc.RESPONSE:
        assert col in header


def _synthetic_sheet(frame, table_rows, bad_ids):
    sheet = []
    for rid, f in frame.items():
        row = table_rows[rid]
        bind = row["binding_status"]
        para = "yes"
        if rid in bad_ids:
            para = "partly"
        sheet.append({"id": rid, "paraphrase_supported": para, "binding_assigned": bind,
                      "access_achieved": {"full text seen": "full text", "summary seen": "summary", "title only": "title only"}[row["access_level"]],
                      "locator_found": "not_applicable", "minutes": "5", "notes": ""})
    return sheet


def test_scoring_synthetic_rates():
    t = {r["id"]: r for r in table()}
    frame = {s["id"]: s for s in hc.draw_sample(list(t.values()), 20261020)}
    bad = {rid for rid, s in frame.items() if s["stratum"] == "mandatory"}   # all 20 mandatory rows flagged
    res = hc.score_rows(_synthetic_sheet(frame, t, bad), t, frame)
    assert res["rows_scored"] == 60
    assert res["per_stratum"]["mandatory"]["rate"] == 1.0
    assert res["per_stratum"]["conditional"]["rate"] == 0.0
    expected = t_weight = sum(1 for r in t.values() if r["binding_status"] == "mandatory") / len(t)
    assert abs(res["content_error_rate_stratified"] - expected) < 1e-9
    lo, hi = res["content_error_ci95_bootstrap"]
    assert lo <= expected <= hi
    assert res["binding_agreement"] == 1.0
    assert res["access_overclaim"]["overclaimed"] == 0


def test_binding_disagreement_and_unreadable_rows_are_counted():
    t = {r["id"]: r for r in table()}
    frame = {s["id"]: s for s in hc.draw_sample(list(t.values()), 20261020)}
    sheet = _synthetic_sheet(frame, t, set())
    ids = list(frame)
    sheet[0]["binding_assigned"] = "voluntary" if t[ids[0]]["binding_status"] != "voluntary" else "guidance"
    sheet[1]["paraphrase_supported"] = "cannot_open_source"
    res = hc.score_rows(sheet, t, frame)
    assert res["could_not_open_source"] == 1
    assert res["rows_scored"] == 59
    assert res["binding_agreement"] < 1.0
    assert sum(v["errors"] for v in res["per_stratum"].values()) == 1


def test_access_overclaim_needs_the_source_to_have_been_opened():
    t = {r["id"]: r for r in table()}
    frame = {s["id"]: s for s in hc.draw_sample(list(t.values()), 20261020)}
    sheet = _synthetic_sheet(frame, t, set())
    full = [r for r in sheet if t[r["id"]]["access_level"] == "full text seen"]
    assert full, "sample should contain a full text row"
    full[0]["access_achieved"] = "summary"
    full[1 if len(full) > 1 else 0]["access_achieved"] = "could_not_open"
    res = hc.score_rows(sheet, t, frame)
    assert res["access_overclaim"]["overclaimed"] >= 1


def test_wilson_and_kappa_known_values():
    lo, hi = hc.wilson(0, 10)
    assert lo == 0.0 and 0.25 < hi < 0.32
    assert hc.cohen_kappa(["a", "b", "a", "b"], ["a", "b", "a", "b"]) == 1.0
    assert abs(hc.cohen_kappa(["a", "a", "b", "b"], ["a", "b", "a", "b"])) < 1e-9
