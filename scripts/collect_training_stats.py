#!/usr/bin/env python3
import re, json, os, time
from pathlib import Path
from datetime import datetime

ROOT = Path(".")
log = None
for cand in [
    ROOT/"outputs_luanti_safe"/"training.log",
    ROOT/"training.log", 
    ROOT/"outputs_luanti_safe"/"logs.txt",
]:
    if cand.exists():
        log = cand; break

def ts(dt_str):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%m/%d/%Y %H:%M:%S"):
        try: return datetime.strptime(dt_str, fmt)
        except: pass
    return None

stats = {
    "found_log": bool(log),
    "wall_start": None, "wall_end": None, "wall_seconds": None,
    "steps_total": 1500, "steps_seen": 0,
    "avg_step_seconds": None, "final_loss": None,
    "loss_trace": []
}

if log:
    text = log.read_text(errors="ignore")
    lines = text.splitlines()
    sx = re.compile(r"(?P<t>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*Step\s+(?P<s>\d+)/(?P<T>\d+).*(loss[:=]\s*(?P<loss>[0-9.]+))?", re.I)
    t0 = t1 = None
    steps = []
    for ln in lines:
        m = sx.search(ln)
        if not m: continue
        t = ts(m.group("t"))
        s = int(m.group("s"))
        T = int(m.group("T"))
        stats["steps_total"] = T
        if t:
            if not t0: t0 = t
            t1 = t
        if m.group("loss"):
            stats["loss_trace"].append({"step": s, "loss": float(m.group("loss"))})
        steps.append((s, t.timestamp() if t else None))
    if t0 and t1:
        stats["wall_start"] = t0.isoformat()
        stats["wall_end"] = t1.isoformat()
        stats["wall_seconds"] = (t1 - t0).total_seconds()
    if steps:
        stats["steps_seen"] = max(s for s,_ in steps)
        t_pairs = [(s,t) for s,t in steps if t]
        if len(t_pairs) >= 2:
            t_pairs.sort()
            s0,t0s = t_pairs[0]
            s1,t1s = t_pairs[-1]
            if s1 > s0:
                stats["avg_step_seconds"] = (t1s - t0s) / (s1 - s0)
    if stats["loss_trace"]:
        stats["final_loss"] = stats["loss_trace"][-1]["loss"]

# Fallbacks if log timestamps did not parse
if stats["wall_seconds"] is None:
    outs = ROOT/"outputs_luanti_safe"
    if outs.exists():
        cps = [p for p in outs.iterdir() if p.is_dir() and p.name.startswith("checkpoint-")]
        if cps:
            t0 = min(p.stat().st_mtime for p in cps)
            t1 = max(p.stat().st_mtime for p in cps)
            stats["wall_start"] = datetime.fromtimestamp(t0).isoformat()
            stats["wall_end"] = datetime.fromtimestamp(t1).isoformat()
            stats["wall_seconds"] = t1 - t0

with open("TRAINING_STATS.json", "w") as f:
    json.dump(stats, f, indent=2)

print("Wrote TRAINING_STATS.json")
print(f"Training duration: {stats.get('wall_seconds', 'unknown')} seconds")
if stats.get("avg_step_seconds"):
    print(f"Average step time: {stats['avg_step_seconds']:.2f} seconds")
if stats.get("final_loss"):
    print(f"Final loss: {stats['final_loss']}")