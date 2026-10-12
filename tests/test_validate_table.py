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
