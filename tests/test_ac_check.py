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

# The only items allowed out of "open": simulated, partial, with an artefact produced by sim/.
NON_OPEN = {"EV-08": "sim/results/EV-08.json", "EV-12": "sim/results/EV-12.json", "EV-19": "sim/results_r2/EV-19.json",
            "EV-20": "sim/results_r2/EV-20.json", "EV-21": "sim/results_r2/EV-21.json"}

def test_real_case_has_no_errors_and_only_simulated_partials():
    case_ = ac.load(os.path.join(ROOT, "assurance", "library_robot_case.yaml"))
    rows = ac.table_rows(os.path.join(ROOT, "data", "evidence_table.csv"))
    res = ac.check(case_, rows, ROOT)
    assert [r for r in res if r[0] == "ERROR"] == []
    for e in case_["evidence"]:   # no invented evidence
        if e["id"] in NON_OPEN:
            assert (e["status"], e["kind"], e["artefact"]) == ("partial", "simulated", NON_OPEN[e["id"]])
        else:
            assert e["status"] == "open", e["id"]
    assert all(g["claim_about"] == "hardware" for g in case_["goals"] if g["id"] in ("G4", "G6"))
    assert ("FLAG", "CLAIM_SIM_ONLY", "G4") in {r[:3] for r in res}
    assert ("FLAG", "CLAIM_SIM_ONLY", "G6") in {r[:3] for r in res}

def test_cli_exit_codes():
    p = os.path.join(ROOT, "assurance", "library_robot_case.yaml")
    assert ac.main([p, "--table", os.path.join(ROOT, "data", "evidence_table.csv"), "--quiet"]) == 0
    assert ac.main([p, "--table", os.path.join(ROOT, "data", "evidence_table.csv"), "--quiet", "--strict"]) == 1

def test_render_contains_every_node():
    c = case(); dot = ar.to_dot(c)
    for n in ["G1", "G2", "S1", "C1", "AS1", "SN_EV01"]: assert n in dot
    assert "dashed" in dot


def with_artefact(status="partial", kind="simulated", good_hash=True):
    d = tempfile.mkdtemp(); open(os.path.join(d, "a.json"), "w", encoding="utf-8").write("{}")
    c = case(); e = c["evidence"][0]
    e.update({"status": status, "kind": kind, "artefact": "a.json",
              "sha256": ac.sha256_file(os.path.join(d, "a.json")) if good_hash else "0" * 64})
    return c, d

def test_partial_with_artefact_and_hash_is_clean():
    c, d = with_artefact()
    k = codes(c, base=d)
    assert not any(s == "ERROR" for s, _, _ in k) and ("FLAG", "EVIDENCE_PARTIAL", "EV-01") in k

def test_simulated_cannot_close_hardware_claim():
    c, d = with_artefact(status="provided")
    assert ("ERROR", "SIM_CLOSES_HARDWARE", "EV-01") in codes(c, base=d)

def test_simulated_provided_allowed_for_software_claim():
    c, d = with_artefact(status="provided")
    for g in c["goals"]: g["claim_about"] = "software"
    assert not any(code == "SIM_CLOSES_HARDWARE" for _, code, _ in codes(c, base=d))

def test_bench_evidence_may_close_hardware_claim():
    c, d = with_artefact(status="provided", kind="bench")
    k = codes(c, base=d)
    assert not any(s == "ERROR" for s, _, _ in k) and ("FLAG", "CLAIM_SIM_ONLY", "G2") not in k

def test_hardware_claim_with_only_simulation_is_flagged():
    c, d = with_artefact()
    assert ("FLAG", "CLAIM_SIM_ONLY", "G2") in codes(c, base=d)

def test_hash_mismatch_is_error():
    c, d = with_artefact(good_hash=False)
    assert ("ERROR", "HASH_MISMATCH", "EV-01") in codes(c, base=d)

def test_missing_hash_and_kind_are_errors():
    c, d = with_artefact(); e = c["evidence"][0]; e.pop("sha256"); e.pop("kind")
    k = codes(c, base=d)
    assert ("ERROR", "MISSING_HASH", "EV-01") in k and ("ERROR", "MISSING_KIND", "EV-01") in k

def test_goal_without_claim_scope_is_schema_error():
    c = case(); c["goals"][1].pop("claim_about")
    assert ("ERROR", "SCHEMA", "G2") in codes(c)

def test_committed_diagram_source_is_current():
    case_ = ac.load(os.path.join(ROOT, "assurance", "library_robot_case.yaml"))
    dot = open(os.path.join(ROOT, "figures", "gsn_library_robot.dot"), encoding="utf-8").read()
    assert dot == ar.to_dot(case_) + "\n", "run: python tools/ac_render.py assurance/library_robot_case.yaml figures/gsn_library_robot"

def test_caption_follows_the_data():
    c = case(); assert "No evidence is claimed to exist." in ar.caption(c)
    c["evidence"][0].update({"status": "partial", "kind": "simulated"})
    cap = ar.caption(c); assert "Partial: EV-01 (simulated)." in cap and "supports no hardware claim" in cap

def test_undeveloped_goal_does_not_bypass_simulation_rule():
    c, d = with_artefact(status="provided")
    for g in c["goals"]: g["undeveloped"] = True
    assert ("ERROR", "SIM_CLOSES_HARDWARE", "EV-01") in codes(c, base=d)

def test_decision_needed_is_flagged():
    c = case(); c["evidence"][0]["decision_needed"] = True; c["evidence"][0]["note"] = "Decision needed: limits."
    assert ("FLAG", "DECISION_NEEDED", "EV-01") in codes(c)

def obligation_case(binding, text):
    c = case(); c["goals"][1]["text"] = text
    rows = {"A01": {"access_level": "summary seen", "binding_status": binding}}
    return {(s, code, i) for s, code, i, m in ac.check(c, rows)}

def test_voluntary_or_guidance_cannot_be_written_as_mandatory():
    for b in ("voluntary", "guidance"):
        assert ("ERROR", "OVERSTATED_OBLIGATION", "G2") in obligation_case(b, "Contact limits must be met.")
        assert ("ERROR", "OVERSTATED_OBLIGATION", "G2") in obligation_case(b, "A risk assessment is required.")

def test_binding_rows_may_carry_an_obligation():
    for b in ("mandatory", "conditional"):
        assert ("ERROR", "OVERSTATED_OBLIGATION", "G2") not in obligation_case(b, "Contact limits shall be met.")

def test_plain_claims_are_not_obligations():
    assert ("ERROR", "OVERSTATED_OBLIGATION", "G2") not in obligation_case("guidance", "Contact harm is controlled.")

def test_obligation_word_list_and_negation():
    for t in ("The robot has to stop.", "The operator needs to log faults.", "The site requires a permit.", "Testing is mandated."):
        assert ("ERROR", "OVERSTATED_OBLIGATION", "G2") in obligation_case("guidance", t), t
    assert ("ERROR", "OVERSTATED_OBLIGATION", "G2") not in obligation_case("guidance", "The source does not say the robot must stop.")

def test_obligation_uses_the_goals_own_rows_and_covers_strategies():
    c = case(); c["goals"][0]["text"] = "The robot must be acceptably safe in the ODD."    # G1 has no own items
    rows = {"A01": {"access_level": "summary seen", "binding_status": "mandatory"}}
    assert ("ERROR", "OVERSTATED_OBLIGATION", "G1") not in codes(c, rows)                  # support tree is binding
    c = case(); c["strategies"][0]["text"] = "Argue that each hazard shall be removed."
    rows = {"A01": {"access_level": "summary seen", "binding_status": "voluntary"}}
    assert ("ERROR", "OVERSTATED_OBLIGATION", "S1") in codes(c, rows)

def test_artefact_path_must_stay_inside_the_repository():
    for bad in ("/etc/passwd", "../outside.json", "sim/../../x.json"):
        c = case(); c["evidence"][0].update({"status": "partial", "kind": "simulated", "artefact": bad, "sha256": "0" * 64})
        assert ("ERROR", "BAD_ARTEFACT_PATH", "EV-01") in codes(c), bad


# ---- credit ledger (four external conditions, decided by files the checker can open) ----

def credit_case(tmp_path, **ev_extra):
    (tmp_path / "data").mkdir(exist_ok=True); (tmp_path / "data" / "measured.csv").write_text("t,x\n0,1\n")
    (tmp_path / "data" / "sens.csv").write_text("a,b\n1,2\n"); (tmp_path / "data" / "review.md").write_text("review\n")
    c = case(); c["contexts"].append({"id": "C2", "text": "context of use of the simulated evidence"})
    c["evidence"] = [{"id": "EV-01", "title": "ODD", "status": "open", "rows": ["A01"]},
                     {"id": "EV-02", "title": "sim", "status": "partial", "kind": "simulated", "artefact": "data/measured.csv",
                      "sha256": ac.sha256_file(str(tmp_path / "data" / "measured.csv")), "rows": ["A01"]} | ev_extra]
    c["goals"][1]["evidence"] = ["EV-02"]
    return c


def ceiling_of(c, tmp_path):
    return [m for s, code, i, m in ac.check(c, ROWS, str(tmp_path)) if code == "CREDIT_CEILING"][0]


def test_credit_none_without_context_of_use(tmp_path):
    assert "ceiling on the claim it can support: none" in ceiling_of(credit_case(tmp_path), tmp_path)


def test_credit_demonstration_with_context_only(tmp_path):
    m = ceiling_of(credit_case(tmp_path, credibility_context=["C2"]), tmp_path)
    assert "demonstration" in m and "validated against measured data" in m


def test_credit_indicative_needs_measured_data(tmp_path):
    m = ceiling_of(credit_case(tmp_path, credibility_context=["C2"], credibility_physical_data="data/measured.csv"), tmp_path)
    assert ": indicative" in m and "independent" in m


def test_credit_supporting_needs_all_four(tmp_path):
    full = dict(credibility_context=["C2"], credibility_physical_data="data/measured.csv", credibility_uncertainty="data/sens.csv",
                credibility_verifier_record="data/review.md")
    assert ": supporting" in ceiling_of(credit_case(tmp_path, **full), tmp_path)
    for drop in ("credibility_physical_data", "credibility_uncertainty", "credibility_verifier_record"):
        part = {k: v for k, v in full.items() if k != drop}
        assert ": supporting" not in ceiling_of(credit_case(tmp_path, **part), tmp_path), drop


def test_credit_reference_to_a_missing_file_is_an_error(tmp_path):
    c = credit_case(tmp_path, credibility_context=["C2"], credibility_physical_data="data/nothing.csv")
    assert ("ERROR", "CREDIT_REFERENCE", "EV-02") in {(s, code, i) for s, code, i, m in ac.check(c, ROWS, str(tmp_path))}
    c = credit_case(tmp_path, credibility_context=["C9"])
    assert ("ERROR", "CREDIT_REFERENCE", "EV-02") in {(s, code, i) for s, code, i, m in ac.check(c, ROWS, str(tmp_path))}


def test_credit_path_may_not_leave_the_repository(tmp_path):
    c = credit_case(tmp_path, credibility_context=["C2"], credibility_uncertainty="../outside.csv")
    assert ("ERROR", "CREDIT_REFERENCE", "EV-02") in {(s, code, i) for s, code, i, m in ac.check(c, ROWS, str(tmp_path))}


def test_provided_simulated_evidence_cannot_carry_a_software_claim_without_validation(tmp_path):
    c = credit_case(tmp_path, credibility_context=["C2"]); c["evidence"][1]["status"] = "provided"; c["goals"][1]["claim_about"] = "software"
    assert ("ERROR", "CREDIT_BELOW_CLAIM", "EV-02") in {(s, code, i) for s, code, i, m in ac.check(c, ROWS, str(tmp_path))}


def test_partial_evidence_is_flagged_not_rejected_and_hardware_stays_open(tmp_path):
    c = credit_case(tmp_path, credibility_context=["C2"])
    k = {(s, code, i) for s, code, i, m in ac.check(c, ROWS, str(tmp_path))}
    assert ("FLAG", "CLAIM_CEILING", "G2") in k and ("FLAG", "CLAIM_SIM_ONLY", "G2") in k
    assert not [x for x in k if x[0] == "ERROR"]


def test_even_fully_credited_simulation_does_not_close_a_hardware_claim(tmp_path):
    full = dict(credibility_context=["C2"], credibility_physical_data="data/measured.csv", credibility_uncertainty="data/sens.csv",
                credibility_verifier_record="data/review.md")
    c = credit_case(tmp_path, **full); c["evidence"][1]["status"] = "provided"
    assert ("ERROR", "SIM_CLOSES_HARDWARE", "EV-02") in {(s, code, i) for s, code, i, m in ac.check(c, ROWS, str(tmp_path))}
