#!/usr/bin/env python3
import json, glob
from datetime import datetime

# Known durations from completed evaluations
mins = {
    ("1000","0.5"): 127, ("1000","1.0"): 123,
    ("1500","0.25"): 152, ("1500","0.5"): 127, ("1500","1.0"): 123
}

print("=== Evaluation Completion ETA ===")
print("")

# Check what's actually complete
completed = []
for p in glob.glob("eval/results/local_checkpoint-*_scale_*.json"):
    try:
        with open(p) as f:
            d = json.load(f)
        ck = d.get("checkpoint", "").replace("checkpoint-", "")
        sc = str(d.get("scale", ""))
        completed.append((ck, sc))
    except:
        pass

print(f"Completed: {len(completed)}/9 evaluations")
for ck, sc in sorted(completed):
    print(f"  ✅ checkpoint-{ck} @ scale={sc}")

print("")
print("Remaining evaluations:")
total_mins = 0
for (ck, sc), m in mins.items():
    if (ck, sc) not in completed:
        h = m // 60; mm = m % 60
        print(f"  ⏳ checkpoint-{ck} @ scale={sc}: ~{h}h {mm}m")
        total_mins += m

if total_mins > 0:
    h = total_mins // 60; mm = total_mins % 60
    print("")
    print(f"Estimated remaining time: ~{h}h {mm}m")
    
    # Add buffers for overhead
    for buf in [0.05, 0.10]:
        buffered = int(total_mins * (1 + buf))
        bh = buffered // 60; bmm = buffered % 60
        print(f"With {int(buf*100)}% buffer: ~{bh}h {bmm}m")
    
    # Current time + ETA
    now = datetime.now()
    print("")
    print(f"Current time: {now.strftime('%H:%M')}")
    estimated_completion = now.timestamp() + total_mins * 60
    completion_time = datetime.fromtimestamp(now.timestamp() + total_mins * 60 * 1.1)
    print(f"ETA (with buffer): {completion_time.strftime('%H:%M tomorrow' if completion_time.day > now.day else '%H:%M today')}")
else:
    print("🎉 All evaluations complete!")