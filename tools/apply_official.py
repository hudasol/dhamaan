"""Apply row proposals from the official source checks to the baseline table.

Input : data/evidence_table_v1_baseline.csv, data/official/*_rows.csv
Output: data/verification/input_table_v2.csv, data/official/applied_changes.csv
Rules : proposals that say 'no change' are skipped; access level is only ever lowered here;
        paraphrase proposals that start with Add or Append are appended; special cases are listed in OVERRIDES.
"""
import csv, glob, re, hashlib, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORDER = {"title only": 0, "summary seen": 1, "full text seen": 2}

OVERRIDES = {
    ("A01", "requirement_paraphrase"): None,  # take proposal as is (full replacement)
    ("A02", "requirement_paraphrase"): None,
    ("A05", "requirement_paraphrase"): None,
    ("A17", "requirement_paraphrase"): None,
    ("C62", "requirement_paraphrase"): None,
    ("D43", "requirement_paraphrase"): None,
    ("A15", "requirement_paraphrase"): None,
    ("A14", "requirement_paraphrase"): "A category is included in Annex I Part A if, following the Art. 6(4) assessment, one of four conditions (a) to (d) is met; other categories with serious risk go to Part B. The conditions themselves were not read in detail.",
    ("A18", "requirement_paraphrase"): "Secondary source (MAAK) says 1.2.1 requires safety functions and settings not to be easily modifiable beyond the manufacturer's risk analysis limits, including by user changes and machine learning adjustments. Retention periods were not found in any official text read. One unofficial reproduction places a one year retention of safety related decision data in 1.2.1 (second list, point b, self evolving or autonomous machinery) and a five year tracing log of interventions and safety software versions in 1.2.1 point f. Unverified against the Official Journal.",
    ("B37", "requirement_paraphrase"): "APPEND: Note: the one year retention of safety decision data is not found in Arts 10, 11 or 13 and is not verified in Annex III; an unofficial reproduction places it in 1.2.1 second list point (b). The 10 year technical documentation retention in Art. 10(3) is a different rule.",
}
SKIP_PAT = re.compile(r"^\(?\s*no change", re.I)


def first_url(s):
    m = re.search(r"https?://[^\s)]+", s)
    return m.group(0) if m else None


def main():
    base = list(csv.DictReader(open(ROOT / "data/evidence_table_v1_baseline.csv", encoding="utf-8")))
    cols = list(base[0].keys())
    byid = {r["id"]: r for r in base}
    log = []
    for f in sorted(glob.glob(str(ROOT / "data/official/*_rows.csv"))):
        for p in csv.DictReader(open(f, encoding="utf-8")):
            rid, field, prop = p["row_id"], p["field"], (p["proposed_value"] or "").strip()
            if rid not in byid or field not in cols or not prop or SKIP_PAT.match(prop):
                continue
            row = byid[rid]
            old = row[field]
            new = None
            if field == "access_level":
                if prop in ORDER and ORDER[prop] < ORDER.get(old, 2):
                    new = prop
            elif field == "source_url":
                new = first_url(prop)
            elif field == "binding_status":
                if prop in ("mandatory", "conditional", "voluntary", "guidance"):
                    new = prop
            elif field == "requirement_paraphrase":
                key = (rid, field)
                if key in OVERRIDES:
                    o = OVERRIDES[key]
                    if o is None:
                        new = prop
                    elif o.startswith("APPEND:"):
                        new = (old + " " + o[7:].strip()).strip()
                    else:
                        new = o
                elif re.match(r"^(Add|Append):", prop):
                    new = (old + " " + prop.split(":", 1)[1].strip().strip('"')).strip()
                elif re.match(r"^No change", prop):
                    new = None
                else:
                    sys.exit(f"unhandled paraphrase proposal for {rid}: {prop[:80]}")
            elif field == "notes":
                new = (old + " | " + prop).strip(" |")
            else:
                new = prop
            if new is not None and new != old:
                row[field] = new
                log.append({"row_id": rid, "field": field, "old": old, "new": new, "reason": p["reason"], "source_url": p["source_url"], "locator_seen": p["locator_seen"]})
    out = ROOT / "data/verification/input_table_v2.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(base)
    with open(ROOT / "data/official/applied_changes.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["row_id", "field", "old", "new", "reason", "source_url", "locator_seen"])
        w.writeheader()
        w.writerows(log)
    print(len(log), "changes applied;", hashlib.sha256(out.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
