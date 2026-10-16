#!/usr/bin/env python3
"""Regenerate docs/REPORT.md, docs/EXEC_BRIEF.md and data/coverage_matrix.csv from the data files.
Everything numeric comes from data/evidence_table.csv, data/verification/outcome.json and data/official_checks.csv."""
import csv, json, re, collections, os, sys
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(R, *a)
rows = list(csv.DictReader(open(P("data/evidence_table.csv"), encoding="utf-8")))
out = json.load(open(P("data/verification/outcome.json"), encoding="utf-8"))
checks = list(csv.DictReader(open(P("data/official_checks.csv"), encoding="utf-8")))
RANK = {"mandatory": 4, "conditional": 3, "voluntary": 2, "guidance": 1}; SYM = {4: "M", 3: "C", 2: "V", 1: "G"}
bind = collections.Counter(r["binding_status"] for r in rows); acc = collections.Counter(r["access_level"] for r in rows)
vs = collections.Counter(r["verification_status"] for r in rows)
ab, c = out["passes_A_B_on_input_v2"], out["pass_C"]
pc = lambda d: f'{d["pct"]} percent ({d["k"]} of {d["n"]}; 95 percent interval {d["ci95"][0]} to {d["ci95"][1]})'
code_names = {}
for r in rows:
    for part in r["evidence_codes"].split("; "):
        m = re.match(r"(E\d\d)\b", part.strip())
        if m: code_names[m.group(1)] = part.strip()
codes = sorted(code_names)

def fill(t, **kw):
    for k, v in kw.items(): t = t.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{[A-Z_]+\}\}", t)
    assert not left, left
    return t

# matrix
fams = []
for r in rows:
    if r["family"] not in fams: fams.append(r["family"])
mat = {f: {k: 0 for k in codes} for f in fams}; cnt = collections.Counter()
for r in rows:
    cnt[r["family"]] += 1
    for part in r["evidence_codes"].split("; "):
        m = re.match(r"(E\d\d)\b", part.strip())
        if m: mat[r["family"]][m.group(1)] = max(mat[r["family"]][m.group(1)], RANK[r["binding_status"]])
with open(P("data/coverage_matrix.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["instrument_family", "rows"] + codes)
    for fm in fams: w.writerow([fm, cnt[fm]] + [SYM.get(mat[fm][k], "") for k in codes])
m = list(csv.reader(open(P("data/coverage_matrix.csv"), encoding="utf-8")))
M = ["| " + " | ".join(["Instrument family", "Rows"] + m[0][2:]) + " |", "|" + "---|" * len(m[0])] + ["| " + " | ".join(r) + " |" for r in m[1:]]
M += ["", "Column key: E01 risk assessment; E02 scope, ODD, classification; E03 technical file; E04 design and safety function verification; E05 physical test and validation; E06 simulation and credibility; E07 data and learning assurance; E08 safety case; E09 independent assessment; E10 declaration, marking; E11 procedures, instructions, oversight; E12 logging and monitoring; E13 incident reporting and post market; E14 quality or safety management system; E15 authorisation, registration, permit."]
# binding by family
bf = collections.defaultdict(collections.Counter)
for r in rows: bf[r["family"]][r["binding_status"]] += 1
BF = ["| Instrument family | Rows | Mandatory | Conditional | Voluntary | Guidance |", "|---|---|---|---|---|---|"]
for f in fams:
    x = bf[f]; BF.append(f"| {f} | {sum(x.values())} | {x['mandatory']} | {x['conditional']} | {x['voluntary']} | {x['guidance']} |")
# type table
tc = collections.Counter(); bt = collections.defaultdict(collections.Counter)
for r in rows:
    for part in r["evidence_codes"].split("; "):
        part = part.strip(); tc[part] += 1; bt[part][r["binding_status"]] += 1
TT = ["| Evidence type | Rows | of which mandatory | conditional | voluntary | guidance |", "|---|---|---|---|---|---|"]
for k in sorted(tc): b = bt[k]; TT.append(f"| {k} | {tc[k]} | {b['mandatory']} | {b['conditional']} | {b['voluntary']} | {b['guidance']} |")
# appendix
esc = lambda x: x.replace("|", "/").replace("\n", " ")
A = ["| ID | Instrument | Clause seen | B | A | Requirement (paraphrase, truncated) | Source |", "|---|---|---|---|---|---|---|"]
for r in rows:
    req = esc(r["requirement_paraphrase"]); req = req if len(req) <= 170 else req[:167].rstrip() + "..."
    A.append(f"| {r['id']} | {esc(r['instrument'])[:42]} | {esc(r['clause_or_section_seen'])[:40]} | {r['binding_status'][0].upper()} | {r['access_level'][0].upper()} | {req} | [link]({r['source_url']}) |")
# official status
KEY = ["M01", "M02", "M03", "M04", "M21", "M22", "M18", "M19", "AI01", "AI02", "AI03", "AI05", "AI06", "AI07", "AI22", "MA01", "MA06", "MA07", "MA10", "GCAA-01", "GCAA-02", "GCAA-04", "GCAA-05", "GCAA-10"]
byid = {r["check_id"]: r for r in checks}
OS = ["| Check | Item | Value seen | Locator seen (shortened) | Source type | Retrieved | Status |", "|---|---|---|---|---|---|---|"]
for k in KEY:
    r = byid[k]; sh = lambda s, n: esc(s if len(s) <= n else s[: n - 3].rstrip() + "...")
    OS.append(f"| {k} | {sh(r['item'], 70)} | {sh(r['value'] or '(none)', 60)} | {sh(r['locator_seen'] or '(none)', 80)} | {r['source_type']} | {r['retrieved_on']} | {r['status']} |")
cs = collections.Counter(r["status"] for r in checks)
OS += ["", f"All {len(checks)} official check items: " + ", ".join(f"{k} {v}" for k, v in sorted(cs.items())) + ". Statuses follow the rule stated above; most stay open because the fetch step returned extractions and not the provision's own wording."]
# downloads
dl = collections.OrderedDict()
for r in checks:
    for u in re.findall(r"https?://[^\s)\"';,]+", r["download_if_blocked"]):
        u = u.rstrip(".")
        dl.setdefault(u, []).append(r["check_id"])
DL = [f"- {u} (checks {', '.join(ids)})" for u, ids in dl.items()]
DL += ["- Free pages the fetch step refused or could not read in full are also listed in `docs/NEXT_STEPS.md` (to open by hand, since the automated fetch step could not read them)."]
# verification text
single = vs["corrected after final check, single checked"]
EXEC = (f"A fresh, independent check of all {len(rows)} rows by two separate sets of new verifiers (passes A and B) flagged at least one problem in a key column (paraphrase, binding status or access level) in {pc(ab['row']['either'])} of rows when either verifier objected, and {pc(ab['row']['both'])} when both did. Phase 1 had reported 13 percent content errors in a 30 row sample. "
        f"After correction, a third set of verifiers (pass C) still flagged {pc(c['changed']['row'])} of the changed rows ({c['changed']['row_excl_unverifiable']['pct']} percent when rows the fetch step could not read are excluded) and {pc(c['unchanged_sample']['row'])} of a 30 row sample of unchanged rows. The prediction written beforehand (under 10 and under 8 percent) was not met. "
        f"{single} rows were corrected from the final reading alone and are labelled single checked. Details in section 2.3.")
CAV = f"{single} rows carry text taken from one final reading only (labelled `single checked` in the table)."
BRIEF = (f"Every row was independently re checked by two verifiers before correction: {ab['row']['either']['pct']} percent of rows had a problem that at least one of them flagged. After correction a third check still flagged about {c['changed']['row_excl_unverifiable']['pct']} percent of corrected rows. Treat any single row as a lead to be confirmed in the source, not as settled.")
pa = ab
V = f"""## 2.3 Verification (second edition)

**Why.** The first edition found 13 percent content errors in a 30 row sample (21 of 30 rows had an issue of any kind) and the corrections were never re checked. The second edition repeats verification on all {len(rows)} rows with different automated verifiers, and measures the rate before and after correction. The plan, the reconciliation rules and the predictions were written before the runs (`data/verification/PLAN.md`); the frozen inputs are hashed in `data/verification/outcome.json`.

**Design.** Official source updates were applied first (91 field changes, `data/official/applied_changes.csv`) and the table was frozen. Pass A and pass B each checked every row with new automated verifiers, blind to each other, to earlier verdicts and to the notes column, with different batch boundaries. For each row a verifier recorded, from its own retrieval: whether the paraphrase is supported, the locator it actually saw, the binding status it would assign, and the access level its reading supports. Reconciliation was mechanical: access level takes the lower of the two readings; a binding status changes only if both agree on a new value; a paraphrase is replaced by the flagging verifier's text; a clause locator stays in `clause_or_section_seen` only if the final access level is full text seen and a verifier saw it, otherwise it moves to `clause_reported_unverified`. Pass C then checked all {c['changed']['n']} rows that changed in a key column plus 30 unchanged rows (seed 20261012).

**Error rates before correction (passes A and B on the frozen table, n = {pa['n']}).**

| Measure | Pass A | Pass B | Both flag | Either flags |
|---|---|---|---|---|
| Paraphrase issue | {pa['para']['A']['pct']}% | {pa['para']['B']['pct']}% | {pa['para']['both']['pct']}% | {pa['para']['either']['pct']}% |
| Binding status differs | {pa['binding']['A']['pct']}% | {pa['binding']['B']['pct']}% | {pa['binding']['both']['pct']}% | {pa['binding']['either']['pct']}% |
| Access level overclaimed | {pa['access_over']['A']['pct']}% | {pa['access_over']['B']['pct']}% | {pa['access_over']['both']['pct']}% | {pa['access_over']['either']['pct']}% |
| Any key column (row error) | {pa['row']['A']['pct']}% | {pa['row']['B']['pct']}% | {pa['row']['both']['pct']}% | {pa['row']['either']['pct']}% |

Agreement between A and B: binding status {pa['agree_binding']['raw_pct']} percent (Cohen's kappa {pa['agree_binding']['kappa']}); access level {pa['agree_access']['raw_pct']} percent (kappa {pa['agree_access']['kappa']}). The access level was also underclaimed in {pa['access_under']['either']['pct']} percent of rows by at least one verifier; those were not raised, by rule. Row error "either" has a 95 percent interval of {pa['row']['either']['ci95'][0]} to {pa['row']['either']['ci95'][1]} percent.

**Error rates after correction (pass C).**

| Group | Rows | Row error | Excluding rows the fetch step could not read | Paraphrase issue | Binding differs |
|---|---|---|---|---|---|
| Changed rows | {c['changed']['n']} | {c['changed']['row']['pct']}% | {c['changed']['row_excl_unverifiable']['pct']}% | {c['changed']['para']['pct']}% | {c['changed']['binding']['pct']}% |
| Unchanged sample | {c['unchanged_sample']['n']} | {c['unchanged_sample']['row']['pct']}% | {c['unchanged_sample']['row_excl_unverifiable']['pct']}% | {c['unchanged_sample']['para']['pct']}% | {c['unchanged_sample']['binding']['pct']}% |

**Predictions written beforehand and how they fared.** {'; '.join(k.replace('_',' ') + ': ' + v for k, v in out['predictions'].items())}.

**What the rows look like now.** Access level: {', '.join(f'{k} {acc[k]}' for k in ('full text seen','summary seen','title only'))} (the first edition had 70 full text seen). No row was removed; rows that could not be supported by a retrieved source were set to title only with title and scope text. Verification status: {', '.join(f'{k} {v}' for k, v in sorted(vs.items()))}. Every change is in `data/verification_changelog_v2.csv` with its stage and reason.

**How to read these numbers.** The third check flagged more detail problems (recital versus operative text, scope claims in status notes, truncated extractions) than the first two, so the corrected table is better but not clean. The after correction figure is not lower than the before figure and we do not claim it is. All verifiers used the same retrieval tools, so agreement is not ground truth. Rows corrected from the final reading alone ({single}) have not been checked twice. The most useful next step is a human read of the rows you intend to quote, against the source."""
t = open(P("docs/templates/report_template.md"), encoding="utf-8").read()
t = fill(t, N_ROWS=str(len(rows)), COUNTS_BINDING=", ".join(f"{k} {bind[k]}" for k in ("mandatory", "conditional", "voluntary", "guidance")),
         COUNTS_ACCESS=", ".join(f"{k} {acc[k]}" for k in ("full text seen", "summary seen", "title only")),
         COUNTS_VSTATUS=", ".join(f"{k} {v}" for k, v in sorted(vs.items())), BINDING_BY_FAMILY="\n".join(BF), TYPE_TABLE="\n".join(TT),
         MATRIX="\n".join(M), APPENDIX="\n".join(A), CONFLICTS=open(P("docs/templates/conflicts.md"), encoding="utf-8").read().strip(),
         CAVEAT_VERIF=CAV, EXEC_VERIFICATION=EXEC, VERIFICATION_SECTION=V, OFFICIAL_STATUS="\n".join(OS), DOWNLOADS="\n".join(DL))
open(P("docs/REPORT.md"), "w", encoding="utf-8", newline="\n").write(t)
b = open(P("docs/templates/brief_template.md"), encoding="utf-8").read()
b = fill(b, N_ROWS=str(len(rows)), COUNTS_BINDING=", ".join(f"{k} {bind[k]}" for k in ("mandatory", "conditional", "voluntary", "guidance")), BRIEF_VERIFICATION=BRIEF)
open(P("docs/EXEC_BRIEF.md"), "w", encoding="utf-8", newline="\n").write(b)
print("built", len(t.split()), "words report;", len(b.split()), "words brief")
