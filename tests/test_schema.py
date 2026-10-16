import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import gen_schema as gs


def test_committed_schemas_are_not_stale():
    assert gs.stale() == [], "run: python tools/gen_schema.py"


def test_generation_is_deterministic_across_processes():
    # a fresh interpreter (different hash seed) must produce the same bytes
    import subprocess
    code = "import sys; sys.path.insert(0, 'tools'); import gen_schema as g; sys.stdout.write(g.render(g.case_schema))"
    root = os.path.join(os.path.dirname(__file__), "..")
    out = subprocess.run([sys.executable, "-c", code], cwd=root, capture_output=True, text=True, encoding="utf-8",
                         env={**os.environ, "PYTHONHASHSEED": "12345"}).stdout
    assert out == gs.render(gs.case_schema)


def test_schema_lists_every_contract_column():
    s = json.loads(gs.render(gs.evidence_table_schema))
    assert s["x-column-order"] == s["required"] and len(s["required"]) == 20


def test_case_schema_closes_evidence_fields():
    s = json.loads(gs.render(gs.case_schema))
    assert s["$defs"]["evidence"]["additionalProperties"] is False
    assert s["$defs"]["evidence"]["properties"]["status"]["enum"] == ["open", "partial", "provided"]
