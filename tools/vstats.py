"""Statistics for verification passes. Usage: python3 -I tools/vstats.py prefixA prefixB  (reads data/verification/results)."""
import csv, glob, math, json, sys
ORDER={"title only":0,"summary seen":1,"full text seen":2}
def load(p, d="data/verification/results"):
    out={}
    for f in sorted(glob.glob(f"{d}/{p}_*.csv")):
        for r in csv.DictReader(open(f,encoding="utf-8")): out[r["id"]]=r
    return out
def wilson(k,n,z=1.96):
    if n==0: return (0.0,0.0)
    p=k/n; d=1+z*z/n; c=p+z*z/(2*n); h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))
    return ((c-h)/d,(c+h)/d)
def kappa(a,b):
    n=len(a); cats=sorted(set(a)|set(b))
    po=sum(x==y for x,y in zip(a,b))/n
    pe=sum((a.count(c)/n)*(b.count(c)/n) for c in cats)
    return (po-pe)/(1-pe) if pe<1 else 1.0
def flags(v,t):
    """v: verifier row, t: table row (the version that was checked)."""
    f={}
    f["para"]=v["para_verdict"]!="supported"
    f["binding"]=v["binding_value"]!=t["binding_status"]
    f["access_over"]=ORDER[v["access_value"]]<ORDER[t["access_level"]]
    f["access_under"]=ORDER[v["access_value"]]>ORDER[t["access_level"]]
    f["row"]=f["para"] or f["binding"] or f["access_over"]
    return f
def rate(k,n):
    lo,hi=wilson(k,n); return {"k":k,"n":n,"pct":round(100*k/n,1) if n else None,"ci95":[round(100*lo,1),round(100*hi,1)]}
def compare(A,B,T,ids=None):
    ids=sorted(ids or set(A)&set(B)); n=len(ids); res={"n":n}
    FA={i:flags(A[i],T[i]) for i in ids}; FB={i:flags(B[i],T[i]) for i in ids}
    for col in ["para","binding","access_over","access_under","row"]:
        a=sum(FA[i][col] for i in ids); b=sum(FB[i][col] for i in ids)
        both=sum(FA[i][col] and FB[i][col] for i in ids); either=sum(FA[i][col] or FB[i][col] for i in ids)
        res[col]={"A":rate(a,n),"B":rate(b,n),"both":rate(both,n),"either":rate(either,n)}
    for fld,key in [("binding","binding_value"),("access","access_value")]:
        xa=[A[i][key] for i in ids]; xb=[B[i][key] for i in ids]
        agree=sum(x==y for x,y in zip(xa,xb))
        res[f"agree_{fld}"]={"raw_pct":round(100*agree/n,1),"kappa":round(kappa(xa,xb),3),"k":agree,"n":n}
    return res
if __name__=="__main__":
    A=load(sys.argv[1]);B=load(sys.argv[2])
    T={r["id"]:r for r in csv.DictReader(open("data/verification/input_table_v2.csv",encoding="utf-8"))}
    print(json.dumps(compare(A,B,T),indent=1))
