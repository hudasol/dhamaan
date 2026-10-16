import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import gen_schema as gs


def test_committed_schemas_are_not_stale():
    assert gs.stale() == [], "run: python tools/gen_schema.py"


def test_generation_is_deterministic():
    for fn in gs.OUTPUTS.values():
        assert gs.render(fn) == gs.render(fn)


def test_schema_lists_every_contract_column():
    s = json.loads(gs.render(gs.evidence_table_schema))
    assert s["x-column-order"] == s["required"] and len(s["required"]) == 20


def test_case_schema_closes_evidence_fields():
    s = json.loads(gs.render(gs.case_schema))
    assert s["$defs"]["evidence"]["additionalProperties"] is False
    assert s["$defs"]["evidence"]["properties"]["status"]["enum"] == ["open", "partial", "provided"]
