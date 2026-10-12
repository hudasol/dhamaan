"""Create blind verification batches from the frozen input table.
Pass A: rows ordered by source URL, then id, cut into chunks of 16.
Pass B: rows ordered by instrument then reversed URL, cut into chunks of 15 (different boundaries).
Columns given to verifiers exclude notes, evidence codes and any earlier verdicts."""
import csv, sys, os
COLS=["id","instrument","edition_or_version","status_note","clause_or_section_seen","requirement_paraphrase","binding_status","applies_to","source_url","access_level"]
rows=list(csv.DictReader(open("data/verification/input_table_v2.csv",encoding="utf-8")))
def write(prefix,ordered,size):
    n=0
    for i in range(0,len(ordered),size):
        n+=1
        with open(f"data/verification/batches/{prefix}_{n:02d}.csv","w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=COLS,extrasaction="ignore"); w.writeheader(); w.writerows(ordered[i:i+size])
    return n
a=sorted(rows,key=lambda r:(r["source_url"],r["id"]))
b=sorted(rows,key=lambda r:(r["instrument"],r["source_url"][::-1],r["id"]))
print("A",write("A",a,16),"B",write("B",b,15))
