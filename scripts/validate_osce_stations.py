#!/usr/bin/env python3
"""Validation gate for generated OSCE stations (Phase 6).

Checks each 25-august-docs/osce_generated/*.osce.json against
OSCE_GENERATION_INSTRUCTIONS.md. Exit 1 if any fail.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / "25-august-docs" / "osce_generated"
STAGING = ROOT / "25-august-docs" / "staging"
STATIONS = {"history_taking","physical_examination","counselling","communication","diagnosis_management","emergency_scenario"}
SPECS = {"gastroenterology","obstetrics_gynaecology","musculoskeletal","neurology","urology","ophthalmology","general_practice"}
DIFF = {"easy","medium","hard"}

# gather valid qdrant ids across all rag_context (citation cross-check)
valid_ids = set()
for f in STAGING.rglob("*.json"):
    if f.name.endswith(".assessed.json"): continue
    try:
        for c in json.loads(f.read_text()).get("rag_context", []):
            valid_ids.add(c["qdrant_point_id"])
    except Exception:
        pass

def check(p):
    errs=[]
    try: o=json.loads(p.read_text())
    except Exception as e: return [f"invalid JSON: {e}"]
    for k in ("osce_id","title","patient_instructions","candidate_instructions","examiner_instructions"):
        if not o.get(k): errs.append(f"missing/empty {k}")
    if o.get("specialty") not in SPECS: errs.append(f"bad specialty {o.get('specialty')}")
    if o.get("station_type") not in STATIONS: errs.append(f"bad station_type {o.get('station_type')}")
    if o.get("difficulty") not in DIFF: errs.append(f"bad difficulty {o.get('difficulty')}")
    r=o.get("rubric") or {}
    doms=r.get("domains") or []
    if not doms: errs.append("no rubric domains")
    else:
        s=sum(d.get("max_marks",0) for d in doms)
        tot=r.get("total_marks")
        if s!=tot: errs.append(f"rubric marks sum {s} != total_marks {tot}")
    if len(o.get("red_flags") or [])<2: errs.append("red_flags <2")
    if len(o.get("australian_guidelines") or [])<2: errs.append("australian_guidelines <2")
    cits=o.get("citations") or []
    if len(cits)<2: errs.append("citations <2")
    for c in cits:
        pid=c.get("qdrant_point_id","")
        if valid_ids and pid and pid not in valid_ids:
            errs.append(f"fabricated qdrant_point_id {pid[:13]}")
    return errs

def main():
    files=sorted(GEN.glob("*.osce.json")) if GEN.exists() else []
    if not files:
        print("No OSCE files found."); sys.exit(1)
    failed=0
    for p in files:
        e=check(p)
        if e:
            failed+=1; print(f"✗ {p.name}")
            for x in e: print("   ", x)
    print(f"\n{len(files)-failed}/{len(files)} passed, {failed} failed")
    sys.exit(1 if failed else 0)

if __name__=="__main__": main()
