import csv, os, sys
import yaml
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import contracts as ct
import ac_check as ac

ROOT = os.path.join(os.path.dirname(__file__), "..")


def test_evidence_table_header_matches_contract():
    with open(os.path.join(ROOT, "data/evidence_table.csv"), newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))
    assert header == [c.name for c in ct.EVIDENCE_TABLE]


def test_case_file_conforms():
    case = yaml.safe_load(open(os.path.join(ROOT, "assurance/library_robot_case.yaml"), encoding="utf-8"))
    assert ct.case_conformance(case) == []


def test_unknown_field_rejected():
    case = {"evidence": [{"id": "EV-01", "title": "t", "status": "open", "rows": ["A01"], "colour": "red"}]}
    assert any("unknown field 'colour'" in e for e in ct.case_conformance(case))


def test_bad_status_and_type_rejected():
    case = {"evidence": [{"id": "EV-01", "title": "t", "status": "done", "rows": "A01"}]}
    errs = ct.case_conformance(case)
    assert any("'status'" in e for e in errs) and any("'rows' must be ids" in e for e in errs)


def test_missing_required_and_bad_id():
    errs = ct.case_conformance({"goals": [{"id": "X1"}]})
    assert any("missing required field 'text'" in e for e in errs)
    assert any("does not match" in e for e in errs)


def test_unknown_top_level_key():
    assert ct.case_conformance({"extras": []}) == ["unknown top level key 'extras'"]


def test_checker_reports_schema_errors():
    res = ac.check({"evidence": [{"id": "EV-01", "title": "t", "status": "open", "rows": ["A01"], "x": 1}]},
                   {"A01": {"access_level": "summary seen"}})
    assert any(r[0] == "ERROR" and r[1] == "SCHEMA" for r in res)
