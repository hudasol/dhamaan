"""Tests for tools/apply_official_r3.py on SYNTHETIC rows made inside the test."""
import importlib.util
import os

import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
spec = importlib.util.spec_from_file_location("apply_official_r3", os.path.join(ROOT, "tools", "apply_official_r3.py"))
ao = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ao)


def base_row(i, status):
    return {"area": "a", "check_id": i, "item": "x", "instrument": "y", "locator_seen": "old", "what_the_source_says": "", "value": "old value",
            "source_url": "http://old", "source_type": "s", "access_seen": "summary seen", "retrieved_on": "2026-10-12", "conflicts": "",
            "status": status, "table_rows_checked": "", "download_if_blocked": "hand url"}


def upd(i, status, **kw):
    return {"check_id": i, "item": "x", "new_status": status, "value": "new value", "locator": "Art. 1", "source_url": "http://new",
            "source_type": "official", "access": "extraction", "retrieved_on": "2026-10-20", "conflicts": "", "hand_fetch_url_and_page": "page 3", **kw}


def test_update_replaces_status_and_marks_the_basis():
    out = ao.merge([base_row("M01", "open"), base_row("M02", "open")], [upd("M01", "confirmed")])
    a, b = out
    assert a["status_before"] == "open" and a["status_after"] == "confirmed" and a["value"] == "new value"
    assert a["basis"] == ao.BASIS and a["hand_check_needed"] == "yes" and a["hand_fetch_url_and_page"] == "page 3"
    assert b["status_after"] == "open" and b["value"] == "old value" and b["basis"] == "round 2 checks, unchanged"


def test_items_that_stay_open_stay_open_and_confirmed_ones_need_no_hand_check():
    out = ao.merge([base_row("M01", "open"), base_row("M02", "confirmed")], [upd("M01", "open")])
    assert out[0]["status_after"] == "open" and out[0]["hand_check_needed"] == "yes"
    assert out[1]["hand_check_needed"] == "no"


def test_bad_status_unknown_id_and_duplicate_rows_are_refused():
    with pytest.raises(ValueError): ao.merge([base_row("M01", "open")], [upd("M01", "done")])
    with pytest.raises(ValueError): ao.merge([base_row("M01", "open")], [upd("ZZ", "open")])
    with pytest.raises(ValueError): ao.merge([base_row("M01", "open")], [upd("M01", "open"), upd("M01", "open")])


def test_committed_status_file_keeps_all_original_checks():
    base = ao.read(ao.BASE)
    out = ao.read(ao.OUT)
    assert [r["check_id"] for r in out] == [r["check_id"] for r in base]
    assert all(o["status_before"] == b["status"] for o, b in zip(out, base))
