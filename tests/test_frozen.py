"""The phase 2 verification inputs, results and the frozen baseline must never change.

data/frozen_sha256.txt was written once; if this test fails, restore the file from git rather than
regenerating the manifest. Documents that disagree with these files are fixed instead.
"""
import hashlib, json, os

ROOT = os.path.join(os.path.dirname(__file__), "..")


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def manifest():
    for line in open(os.path.join(ROOT, "data/frozen_sha256.txt"), encoding="utf-8"):
        if line.strip() and not line.startswith("#"):
            h, rel = line.split(None, 1)
            yield h, rel.strip()


def test_frozen_files_unchanged():
    changed = [rel for h, rel in manifest() if sha(rel) != h]
    assert changed == []


def test_manifest_covers_outcome_and_baseline():
    rels = {rel for _, rel in manifest()}
    assert {"data/verification/outcome.json", "data/evidence_table_v1_baseline.csv", "data/evidence_table.csv"} <= rels


def test_outcome_hashes_match_frozen_inputs():
    o = json.load(open(os.path.join(ROOT, "data/verification/outcome.json"), encoding="utf-8"))
    assert sha("data/verification/input_table_v2.csv") == o["input_table_v2_sha256"]
    assert sha("data/evidence_table_v1_baseline.csv") == o["baseline_v1_sha256"]
