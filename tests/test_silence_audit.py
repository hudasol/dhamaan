"""Tests for tools/silence_audit.py (synthetic coder files are made inside the tests; they are not results)."""
import importlib.util
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
spec = importlib.util.spec_from_file_location("silence_audit", os.path.join(ROOT, "tools", "silence_audit.py"))
sa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sa)


def test_candidates_are_deterministic_and_nonempty():
    t = sa.read_csv(sa.TABLE)
    a, b = sa.candidates(t), sa.candidates(t)
    assert a == b and len(a) > 20
    assert all(r["keyword_hazards"] for r in a)


def test_committed_candidates_match_the_rule():
    t = sa.read_csv(sa.TABLE)
    committed = sa.read_csv(os.path.join(sa.OUT, "candidates.csv"))
    assert [r["id"] for r in committed] == [r["id"] for r in sa.candidates(t)]


def test_template_has_every_coded_field():
    rows = sa.read_csv(os.path.join(sa.OUT, "coder_template.csv"))
    assert set(sa.CODED) <= set(rows[0].keys())
    assert all(rows[0][c] == "" for c in sa.CODED)


def _coded(ids, **over):
    return [{"id": i, "hazard": "gnss", "asks_evidence": "yes", "test_method_fixed": "no", "severity_fixed": "no",
             "severity_gulf_applicable": "no", "delegated_to_developer": "yes", "notes": "", **over.get(i, {})} for i in ids]


def test_agreement_perfect_and_partial():
    ids = ["A1", "A2", "A3", "A4"]
    a = _coded(ids, A1={"asks_evidence": "no"}, A2={"asks_evidence": "unclear"})
    assert sa.agreement(a, a)["asks_evidence"]["kappa"] == 1.0
    b = _coded(ids)
    res = sa.agreement(a, b)
    assert res["n_rows"] == 4
    assert res["asks_evidence"]["raw"] == 0.5
    assert res["hazard"]["raw"] == 1.0


def test_kappa_chance_level():
    assert abs(sa.kappa(["a", "a", "b", "b"], ["a", "b", "a", "b"])) < 1e-9


def test_summarise_counts_only_in_scope_rows_and_keeps_the_limit():
    rows = [{"id": "X1", "access_level": "full text seen", **c} for c in (
        {"hazard": "heat", "asks_evidence": "yes", "test_method_fixed": "yes", "severity_fixed": "yes", "severity_gulf_applicable": "no", "delegated_to_developer": "yes"},
        {"hazard": "heat", "asks_evidence": "yes", "test_method_fixed": "no", "severity_fixed": "unclear", "severity_gulf_applicable": "unclear", "delegated_to_developer": "no"},
        {"hazard": "gnss", "asks_evidence": "no", "test_method_fixed": "na", "severity_fixed": "na", "severity_gulf_applicable": "na", "delegated_to_developer": "na"},
        {"hazard": "out_of_scope", "asks_evidence": "yes", "test_method_fixed": "yes", "severity_fixed": "yes", "severity_gulf_applicable": "yes", "delegated_to_developer": "yes"})]
    s = sa.summarise(rows)
    assert s["candidates"] == 4 and s["out_of_scope"] == 1
    b = s["in_scope"]
    assert b["rows"] == 3 and b["ask_for_evidence"] == 2 and b["of_those_fix_a_test_method"] == 1
    assert b["of_those_fix_a_severity_that_applies_to_a_gulf_site"] == 0 and b["of_those_with_severity_unclear"] == 1
    assert s["by_hazard"]["heat"]["ask_for_evidence"] == 2 and "retrieved text only" in s["limit"]


def test_committed_resolved_coding_is_complete_and_uses_allowed_values():
    rows = sa.read_csv(os.path.join(sa.OUT, "resolved.csv"))
    ids = [r["id"] for r in sa.read_csv(os.path.join(sa.OUT, "candidates.csv"))]
    assert [r["id"] for r in rows] == ids
    for r in rows:
        for field, ok in sa.CHOICES.items():
            assert r[field] in ok, (r["id"], field)
        if r["resolution"] != "agreed": assert r["resolution_reason"]
