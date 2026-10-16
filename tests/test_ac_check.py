import copy, os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import ac_check as ac
import ac_render as ar

ROOT = os.path.join(os.path.dirname(__file__), "..")
ROWS = {"A01": {"access_level": "summary seen"}, "T01": {"access_level": "title only"}}

def case():
    return {
        "assumptions": [{"id": "AS1", "text": "assumed"}],
        "contexts": [{"id": "C1", "text": "ODD", "evidence": ["EV-01"]}],
        "strategies": [{"id": "S1", "text": "argue over hazards", "evidence": ["EV-01"]}],
        "goals": [
            {"id": "G1", "text": "The robot is acceptably safe in the ODD.", "context": ["C1"], "supported_by": ["S1"], "claim_about": "hardware"},
            {"id": "G2", "text": "Contact harm is controlled.", "context": ["C1"], "evidence": ["EV-01"], "claim_about": "hardware"},
        ],
        "strategy_links": {"S1": ["G2"]},
        "evidence": [{"id": "EV-01", "title": "ODD", "status": "open", "rows": ["A01"]}],
    }

def codes(c, rows=ROWS, base="."):
    return {(s, code, i) for s, code, i, m in ac.check(c, rows, base)}

def test_clean_case_has_only_flags():
    res = ac.check(case(), ROWS)
    assert not [r for r in res if r[0] == "ERROR"]

def test_open_evidence_flagged():
    assert ("FLAG", "EVIDENCE_OPEN", "EV-01") in codes(case())

def test_claim_all_open_flagged():
    assert ("FLAG", "CLAIM_ALL_OPEN", "G2") in codes(case())

def test_claim_without_evidence():
    c = case(); c["goals"][1].pop("evidence"); c["strategy_links"] = {"S1": ["G2"]}
    assert ("FLAG", "NO_EVIDENCE", "G2") in codes(c)

def test_undeveloped_goal_flagged_not_error():
    c = case(); c["goals"][1].pop("evidence"); c["goals"][1]["undeveloped"] = True
    k = codes(c); assert ("FLAG", "UNDEVELOPED", "G2") in k and not any(s == "ERROR" for s, _, _ in k)

def test_evidence_untraced_no_rows():
    c = case(); c["evidence"][0]["rows"] = []
    assert ("ERROR", "UNTRACED", "EV-01") in codes(c)

def test_evidence_row_not_in_table():
    c = case(); c["evidence"][0]["rows"] = ["ZZ99"]
    assert ("ERROR", "UNTRACED", "EV-01") in codes(c)

def test_title_only_row_is_weak():
    c = case(); c["evidence"][0]["rows"] = ["T01"]
    assert ("FLAG", "WEAK_SOURCE", "EV-01") in codes(c)

def test_safe_without_context_is_error():
    c = case(); c["goals"][1]["text"] = "The arm is safe."; c["goals"][1].pop("context")
    assert ("ERROR", "UNSUPPORTED_WORD", "G2") in codes(c)

def test_safe_with_context_ok():
    assert ("ERROR", "UNSUPPORTED_WORD", "G1") not in codes(case())

def test_absolute_words_are_errors():
    for w in ["guaranteed", "certified", "always", "never", "compliant", "proven"]:
        c = case(); c["goals"][1]["text"] = f"Contact harm is {w}."
        assert ("ERROR", "UNSUPPORTED_WORD", "G2") in codes(c), w

def test_provided_requires_artefact():
    c = case(); c["evidence"][0]["status"] = "provided"
    assert ("ERROR", "INVENTED_EVIDENCE", "EV-01") in codes(c)
    c["evidence"][0]["artefact"] = "does/not/exist.pdf"
    assert ("ERROR", "INVENTED_EVIDENCE", "EV-01") in codes(c)
    d = tempfile.mkdtemp(); open(os.path.join(d, "report.md"), "w").write("x")
    c["evidence"][0]["artefact"] = "report.md"
    assert ("ERROR", "INVENTED_EVIDENCE", "EV-01") not in codes(c, base=d)

def test_bad_status():
    c = case(); c["evidence"][0]["status"] = "done"
    assert ("ERROR", "BAD_STATUS", "EV-01") in codes(c)

def test_dangling_references():
    c = case(); c["goals"][1]["evidence"] = ["EV-99"]; c["goals"][1]["context"] = ["C9"]
    k = codes(c); assert ("ERROR", "DANGLING", "G2") in k

def test_cycle_and_orphan():
    c = case(); c["goals"].append({"id": "G3", "text": "x", "supported_by": ["G3"]})
    assert any(code == "ORPHAN" or code == "CYCLE" for _, code, _ in codes(c))

def test_duplicate_id():
    c = case(); c["goals"].append({"id": "G1", "text": "dup", "context": ["C1"]})
    assert ("ERROR", "DUPLICATE_ID", "G1") in codes(c)

def test_real_case_has_no_errors_and_all_open():
    case_ = ac.load(os.path.join(ROOT, "assurance", "library_robot_case.yaml"))
    rows = ac.table_rows(os.path.join(ROOT, "data", "evidence_table.csv"))
    res = ac.check(case_, rows, ROOT)
    assert [r for r in res if r[0] == "ERROR"] == []
    assert all(e["status"] == "open" for e in case_["evidence"])   # no invented evidence

def test_cli_exit_codes():
    p = os.path.join(ROOT, "assurance", "library_robot_case.yaml")
    assert ac.main([p, "--table", os.path.join(ROOT, "data", "evidence_table.csv"), "--quiet"]) == 0
    assert ac.main([p, "--table", os.path.join(ROOT, "data", "evidence_table.csv"), "--quiet", "--strict"]) == 1

def test_render_contains_every_node():
    c = case(); dot = ar.to_dot(c)
    for n in ["G1", "G2", "S1", "C1", "AS1", "SN_EV01"]: assert n in dot
    assert "dashed" in dot

def test_goal_without_claim_scope_is_schema_error():
    c = case(); c["goals"][1].pop("claim_about")
    assert ("ERROR", "SCHEMA", "G2") in codes(c)
