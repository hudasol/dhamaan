"""Apply pass C (third vote / final check) to table_v3 per PLAN.md. Writes data/evidence_table.csv,
data/verification/final_log.csv and data/verification_changelog_v2.csv."""
import csv, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from vstats import load, ORDER, flags
A,B,C=load("A"),load("B"),load("C")
T=list(csv.DictReader(open("data/verification/table_v3.csv",encoding="utf-8")))
I={r["id"]:r for r in csv.DictReader(open("data/verification/input_table_v2.csv",encoding="utf-8"))}
G={r["id"]:r["group"] for r in csv.DictReader(open("data/verification/passC_sample.csv"))}
key=["requirement_paraphrase","binding_status","access_level","edition_or_version","status_note"]
log=[]; out=[]
for r in T:
    i=r["id"]; n=dict(r); changed=any(r[c]!=I[i][c] for c in key)
    if i not in C:
        n["verification_status"]="verified twice, no change" if not changed else "corrected after A/B, not re-checked"
        out.append(n); continue
    c=C[i]; f=flags(c,r); fl=[]
    # binding: three votes
    votes=[A[i]["binding_value"],B[i]["binding_value"],c["binding_value"]]
    cur=r["binding_status"]
    maj=[v for v in set(votes) if votes.count(v)>=2]
    if maj and maj[0]!=cur:
        log.append((i,"binding_status",cur,maj[0],"2 of 3 verifiers agree")); n["binding_status"]=maj[0]; n["binding_checked"]="majority of 3"
    elif c["binding_value"]!=cur:
        n["binding_checked"]="split" if r["binding_checked"]!="disputed" else "disputed"
        fl.append(f"binding dissent in final check ({c['binding_value']})")
    elif r["binding_checked"]=="agreed": n["binding_checked"]="agreed (3 of 3)" if votes.count(cur)==3 else "agreed"
    # access / paraphrase
    if c["recommendation"]=="downgrade" or (c["para_verdict"]=="unverifiable" and ORDER[c["access_value"]]<ORDER[r["access_level"]]):
        if r["access_level"]!="title only": log.append((i,"access_level",r["access_level"],"title only","final check could not support content"))
        n["access_level"]="title only"
        if c["corrected_paraphrase"].strip() and c["corrected_paraphrase"].strip()!=r["requirement_paraphrase"]:
            log.append((i,"requirement_paraphrase",r["requirement_paraphrase"],c["corrected_paraphrase"].strip(),"final check, title and scope text")); n["requirement_paraphrase"]=c["corrected_paraphrase"].strip()
        n["verification_status"]="corrected after final check, single checked"
    elif c["para_verdict"] in ("partly","unsupported") or c["recommendation"]=="revise":
        t=c["corrected_paraphrase"].strip()
        if t and t!=r["requirement_paraphrase"]:
            log.append((i,"requirement_paraphrase",r["requirement_paraphrase"],t,"final check")); n["requirement_paraphrase"]=t
            n["verification_status"]="corrected after final check, single checked"
        else: n["verification_status"]="flagged by final check, no replacement text"
    else:
        n["verification_status"]="confirmed by final check" if changed else "verified three times"
    if c["edition_ok"]=="no" or c["clause_ok"]=="no":
        fl.append(f"final check: edition_ok={c['edition_ok']}, clause_ok={c['clause_ok']}")
    if f["para"] and c["evidence_note"]: fl.append("final check note: "+c["evidence_note"])
    if fl: n["notes"]=(n["notes"]+" | " if n["notes"] else "")+"; ".join(fl)
    out.append(n)
fields=list(T[0].keys())
w=csv.DictWriter(open("data/evidence_table.csv","w",newline="",encoding="utf-8"),fieldnames=fields); w.writeheader(); w.writerows(out)
w=csv.writer(open("data/verification/final_log.csv","w",newline="",encoding="utf-8")); w.writerow(["id","field","old","new","reason"]); w.writerows(log)
# changelog v2: A/B reconcile log + final log, with source
rl=list(csv.DictReader(open("data/verification/reconcile_log.csv",encoding="utf-8")))
w=csv.writer(open("data/verification_changelog_v2.csv","w",newline="",encoding="utf-8"))
w.writerow(["id","stage","field","old","new","reason"])
for x in rl: w.writerow([x["id"],"A+B reconcile",x["field"],x["old"],x["new"],"rule-based reconciliation of two independent verifiers"])
for x in log: w.writerow([x[0],"C final check",x[1],x[2],x[3],x[4]])
from collections import Counter
print(len(out),Counter(r["verification_status"] for r in out)); print(Counter(l[1] for l in log))
