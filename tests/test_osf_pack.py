"""Tests for tools/make_osf_pack.py."""
import hashlib
import importlib.util
import json
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
spec = importlib.util.spec_from_file_location("make_osf_pack", os.path.join(ROOT, "tools", "make_osf_pack.py"))
mk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mk)


def test_brackets_are_found_whole_and_links_are_skipped():
    t = "Seed [seed] and [AC-N4: at most [value]; set later] but [a link](http://x) and []"
    assert mk.brackets(t) == ["seed", "AC-N4: at most [value]; set later"]


def test_sections_are_split_by_number():
    s = mk.sections("intro\n## 1. Parts\nA\n## 2. Part A\nB\nC\n")
    assert s["1"].startswith("## 1. Parts") and "C" in s["2"]


def test_pack_records_the_hash_of_the_draft_and_leaves_the_owner_lines_open():
    draft = open(mk.DRAFT, encoding="utf-8").read()
    pack = mk.build(draft, open(mk.RQ, encoding="utf-8").read())
    assert hashlib.sha256(draft.encode()).hexdigest() in pack
    assert "Registration identifier: [to be entered" in pack and "AC-N4 limit per hour: [to be entered" in pack
    assert "Nothing here has been registered" in pack


def test_committed_pack_is_current():
    draft = open(mk.DRAFT, encoding="utf-8").read()
    assert open(mk.OUT, encoding="utf-8").read() == mk.build(draft, open(mk.RQ, encoding="utf-8").read()), "run: python tools/make_osf_pack.py"


def test_zenodo_metadata_is_valid_json_and_has_no_attribution_to_tools():
    z = json.load(open(mk.ZENODO, encoding="utf-8"))
    assert z["creators"] and z["title"] and z["access_right"] == "open"
    assert "claude" not in json.dumps(z).lower()
