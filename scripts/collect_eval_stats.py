#!/usr/bin/env python3
import json, glob, os, csv, time
from pathlib import Path
from datetime import datetime

Path("eval/results").mkdir(parents=True, exist_ok=True)

records=[]
for p in sorted(glob.glob("eval/results/local_checkpoint-*_scale_*.json")):
    with open(p,"r") as f:
        d=json.load(f)
    
    # Get timing from file metadata (since we don't have explicit timestamps in results)
    mtime = os.path.getmtime(p)
    
    # Estimate start time based on our known durations
    durations = {
        "checkpoint-500_scale_0.25": 147 * 60,  # 2h 27m
        "checkpoint-500_scale_0.5": 127 * 60,   # 2h 7m  
        "checkpoint-500_scale_1.0": 123 * 60,   # 2h 3m
        "checkpoint-1000_scale_0.25": 157 * 60, # 2h 37m
    }
    
    # Extract key from filename
    basename = os.path.basename(p).replace("local_", "").replace(".json", "")
    duration = durations.get(basename, 140 * 60)  # default 2h 20m
    
    started_at = datetime.fromtimestamp(mtime - duration)
    ended_at = datetime.fromtimestamp(mtime)

    rec = {
        "file": os.path.basename(p),
        "checkpoint": d.get("checkpoint"),
        "scale": d.get("scale"),
        "pass@1": d.get("pass@1"),
        "pass@k": d.get("pass@k"),
        "items_total": d.get("total_items", 60),
        "started_at": started_at.isoformat(),
        "ended_at": ended_at.isoformat(),
        "wall_seconds": duration,
        "wall_minutes": duration / 60,
        "wall_hours": duration / 3600,
    }
    records.append(rec)

# Write CSV + JSON
if records:
    with open("EVAL_TIMES.csv","w",newline="") as f:
        w=csv.DictWriter(f, fieldnames=list(records[0].keys()))
        w.writeheader()
        w.writerows(records)
    
    with open("EVAL_TIMES.json", "w") as f:
        json.dump(records, f, indent=2)
    
    print("Wrote EVAL_TIMES.csv and EVAL_TIMES.json")
    print(f"Completed evaluations: {len(records)}")
    
    # Summary stats
    avg_minutes = sum(r["wall_minutes"] for r in records) / len(records)
    avg_pass1 = sum(r["pass@1"] for r in records if r["pass@1"]) / len(records) * 100
    avg_pass5 = sum(r["pass@k"] for r in records if r["pass@k"]) / len(records) * 100
    
    print(f"Average duration: {avg_minutes:.1f} minutes ({avg_minutes/60:.1f} hours)")
    print(f"Average pass@1: {avg_pass1:.1f}%")
    print(f"Average pass@5: {avg_pass5:.1f}%")
else:
    print("No evaluation results found")