import csv, os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import validate_table as vt

def good():
    return {c: "" for c in vt.REQUIRED} | {
        "id": "A01", "family": "f", "instrument": "i", "requirement_paraphrase": "p",
        "binding_status": "voluntary", "access_level": "summary seen", "evidence_codes": "E05 Something",
        "source_url": "https://example.org/x", "retrieval_date": "2026-10-12", "last_checked": "2026-10-12",
        "binding_checked": "agreed", "verification_status": "verified twice, no change"}

def run(rows, cols=None):
    d = tempfile.mkdtemp(); p = os.path.join(d, "t.csv")
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols or vt.REQUIRED); w.writeheader(); w.writerows(rows)
    return vt.validate(p)

def test_good_row_passes():
    e, w = run([good()]); assert e == []

def test_missing_column():
    e, _ = run([{c: "" for c in vt.REQUIRED if c != "notes"}], cols=[c for c in vt.REQUIRED if c != "notes"]); assert e and "missing columns" in e[0]

def test_bad_enum_values():
    r = good(); r["binding_status"] = "mandatory-ish"; r["access_level"] = "full"
    e, _ = run([r]); assert any("binding_status" in x for x in e) and any("access_level" in x for x in e)

def test_url_required_and_single():
    r = good(); r["source_url"] = ""; e, _ = run([r]); assert any("source_url" in x for x in e)
    r = good(); r["source_url"] = "https://a.org/x; https://b.org/y"; e, _ = run([r]); assert any("source_url" in x for x in e)

def test_clause_needs_full_text():
    r = good(); r["clause_or_section_seen"] = "Art. 5"; e, _ = run([r]); assert any("locator" in x for x in e)
    r["access_level"] = "full text seen"; r["source_url"] = "https://eur-lex.europa.eu/x"; e, _ = run([r]); assert e == []

def test_catalogue_source_cannot_be_full_text():
    r = good(); r["access_level"] = "full text seen"; r["source_url"] = "https://www.iso.org/standard/1.html"
    e, _ = run([r]); assert any("catalogue" in x for x in e)

def test_secondary_source_cannot_be_full_text():
    r = good(); r["access_level"] = "full text seen"; r["source_url"] = "https://www.dlapiper.com/a"
    e, _ = run([r]); assert any("secondary" in x for x in e)

def test_duplicate_id_and_bad_code_and_date():
    a, b = good(), good(); b["evidence_codes"] = "E99"; b["retrieval_date"] = "11/10/2026"
    e, _ = run([a, b]); assert any("duplicate" in x for x in e) and any("E99" in x for x in e) and any("ISO date" in x for x in e)

def test_paraphrase_clause_reference_is_warning_then_strict_error():
    r = good(); r["requirement_paraphrase"] = "Article 6 applies"
    e, w = run([r]); assert e == [] and w
    d = tempfile.mkdtemp(); p = os.path.join(d, "t.csv")
    with open(p, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=vt.REQUIRED); wr.writeheader(); wr.writerow(r)
    e, _ = vt.validate(p, strict=True); assert e

def test_real_table_is_valid():
    p = os.path.join(os.path.dirname(__file__), "..", "data", "evidence_table.csv")
    e, _ = vt.validate(p); assert e == [], e[:5]

ROOT = os.path.join(os.path.dirname(__file__), "..")
TABLE = os.path.join(ROOT, "data", "evidence_table.csv")
REVIEWED = os.path.join(ROOT, "data", "validator_warnings_reviewed.csv")

def test_every_clause_locator_has_full_text_seen():
    rows = list(csv.DictReader(open(TABLE, encoding="utf-8", newline="")))
    bad = [r["id"] for r in rows if r["clause_or_section_seen"].strip() and r["access_level"] != "full text seen"]
    assert bad == [] and any(r["clause_or_section_seen"].strip() for r in rows)

def test_real_table_has_no_unreviewed_warnings():
    errs, warns, done = vt.validate_reviewed(TABLE, REVIEWED, strict=True)
    assert errs == [] and warns == [] and len(done) == len(vt.load_reviewed(REVIEWED))

def test_review_requires_same_mentions_and_unverified_locator():
    r = good() | {"requirement_paraphrase": "See Art. 5 of the act.", "clause_reported_unverified": "Art. 5"}
    d = tempfile.mkdtemp(); rev = os.path.join(d, "rev.csv")
    def write_rev(m):
        with open(rev, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["id", "mentions"]); w.writerow(["A01", m])
    write_rev("Art. 5")
    errs, warns, done = vt.validate_reviewed(run_path([r]), rev, strict=True)
    assert errs == [] and len(done) == 1
    write_rev("Art. 6")                                   # review no longer matches the text
    errs, warns, done = vt.validate_reviewed(run_path([r]), rev, strict=True)
    assert errs and not done
    write_rev("Art. 5"); r["clause_reported_unverified"] = ""   # locator not recorded as unverified
    errs, warns, done = vt.validate_reviewed(run_path([r]), rev, strict=True)
    assert errs and not done

def test_stale_review_is_an_error():
    d = tempfile.mkdtemp(); rev = os.path.join(d, "rev.csv")
    with open(rev, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["id", "mentions"]); w.writerow(["A01", "Art. 5"])
    errs, _, _ = vt.validate_reviewed(run_path([good()]), rev)
    assert any("stale review" in e for e in errs)

def run_path(rows):
    d = tempfile.mkdtemp(); p = os.path.join(d, "t.csv")
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=vt.REQUIRED); w.writeheader(); w.writerows(rows)
    return p
