"""Apply PLAN.md reconciliation rules mechanically. Reads input_table_v2 + results A_*, B_*; writes
data/verification/table_v3.csv, data/removed_rows.csv, data/verification/reconcile_log.csv"""
import csv, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from vstats import load, ORDER
INV={v:k for k,v in ORDER.items()}
T=list(csv.DictReader(open("data/verification/input_table_v2.csv",encoding="utf-8")))
A=load("A"); B=load("B")
fields=list(T[0].keys())
for extra in ["clause_reported_unverified","binding_checked","verification_status","last_checked"]:
    if extra not in fields: fields.append(extra)
out=[]; log=[]; removed=[]
TODAY="2026-10-12"
def para_flag(v): return v["para_verdict"]!="supported" or v["recommendation"] in ("revise","downgrade","remove")
for r in T:
    i=r["id"]; a=A[i]; b=B[i]; n=dict(r)
    n["clause_reported_unverified"]=""; n["binding_checked"]="agreed"; n["verification_status"]="verified twice"; n["last_checked"]=TODAY
    ch=[]
    # access: lower of the two
    new_acc=INV[min(ORDER[a["access_value"]],ORDER[b["access_value"]])]
    if new_acc!=r["access_level"]: ch.append(("access_level",r["access_level"],new_acc)); n["access_level"]=new_acc
    # binding
    cur=r["binding_status"]
    if a["binding_value"]==b["binding_value"]:
        if a["binding_value"]!=cur:
            ch.append(("binding_status",cur,a["binding_value"])); n["binding_status"]=a["binding_value"]
    elif cur in (a["binding_value"],b["binding_value"]): n["binding_checked"]="split"
    else: n["binding_checked"]="disputed"
    # remove
    if a["recommendation"]=="remove" and b["recommendation"]=="remove":
        removed.append({**r,"removal_reason":(a["evidence_note"]+" | "+b["evidence_note"])[:500]}); log.append((i,"row","removed",r["requirement_paraphrase"][:80],"")); continue
    # paraphrase
    fa,fb=para_flag(a),para_flag(b)
    txt=None; downgrade=False
    flaggers=[v for v,f in ((a,fa),(b,fb)) if f]
    dg=[v for v in flaggers if v["para_verdict"] in ("unsupported","unverifiable") and v["recommendation"]=="downgrade" or v["recommendation"]=="downgrade"]
    if dg:
        downgrade=True
        cands=[v["corrected_paraphrase"].strip() for v in dg if v["corrected_paraphrase"].strip()]
        txt=min(cands,key=len) if len(cands)>1 else (cands[0] if cands else None)
        n["access_level"]="title only"
        if r["access_level"]!="title only": ch.append(("access_level",r["access_level"],"title only (downgrade)"))
    elif flaggers:
        cands=[(v["corrected_paraphrase"].strip(),k) for k,v in (("A",a),("B",b)) if (v in flaggers) and v["corrected_paraphrase"].strip()]
        if cands:
            cands.sort(key=lambda x:(len(x[0]), x[1])); txt=cands[0][0]
    if txt and txt!=r["requirement_paraphrase"]:
        ch.append(("requirement_paraphrase",r["requirement_paraphrase"],txt)); n["requirement_paraphrase"]=txt
    elif flaggers and not txt:
        n["verification_status"]="flagged, no replacement text"
    if any(v["para_verdict"]=="unverifiable" for v in (a,b)) and not downgrade:
        n["verification_status"]="source not fully retrieved by verifier"
    # clause rule
    clause=r["clause_or_section_seen"]
    seen=bool(a["locator_seen"].strip() or b["locator_seen"].strip())
    clause_bad=a["clause_ok"]=="no" or b["clause_ok"]=="no"
    if clause and (n["access_level"]!="full text seen" or not seen or clause_bad):
        n["clause_or_section_seen"]=""; n["clause_reported_unverified"]=clause
        ch.append(("clause_or_section_seen",clause,"(moved to clause_reported_unverified)"))
    for col,o,nv in ch: log.append((i,col,"changed",o,nv))
    if ch: n["verification_status"]+="; corrected after A/B" if n["verification_status"]=="verified twice" else ""
    out.append(n)
w=csv.DictWriter(open("data/verification/table_v3.csv","w",newline="",encoding="utf-8"),fieldnames=fields); w.writeheader(); w.writerows(out)
rf=fields+["removal_reason"]
w=csv.DictWriter(open("data/removed_rows.csv","w",newline="",encoding="utf-8"),fieldnames=rf,extrasaction="ignore"); w.writeheader(); w.writerows(removed)
w=csv.writer(open("data/verification/reconcile_log.csv","w",newline="",encoding="utf-8")); w.writerow(["id","field","action","old","new"]); w.writerows(log)
from collections import Counter
print(len(out),"kept",len(removed),"removed", Counter(l[1] for l in log))
print(Counter(r["binding_checked"] for r in out), Counter(r["verification_status"] for r in out))
