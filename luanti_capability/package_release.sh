#!/usr/bin/env bash
set -euo pipefail
cd ~/luanti_capability
OUT=artifacts/release_$(date +%Y%m%d_%H%M%S)
mkdir -p "$OUT"
# promote best (bakes winning scale)
TORCHDYNAMO_DISABLE=1 /home/tdeshane/miniconda3/envs/gptoss/bin/python -u scripts/promote_best.py | tee "$OUT/promote_best.log"
# manifest
python - <<'PY' > "$OUT/manifest.json"
import json, os, hashlib, pathlib, platform, torch
root = pathlib.Path.home()/"luanti_capability"
out  = root/"outputs_luanti_best"
def sha(p): 
    h = hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20), b""): h.update(b)
    return h.hexdigest()
files = []
for p in out.rglob("*"):
    if p.is_file(): files.append({"path": str(p.relative_to(root)), "sha256": sha(p)})
env = {
 "python": platform.python_version(),
 "torch": torch.__version__,
 "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES",""),
}
print(json.dumps({"artifact":"outputs_luanti_best","files":files,"env":env}, indent=2))
PY
# tarball
tar czf "$OUT/outputs_luanti_best.tgz" outputs_luanti_best
sha256sum "$OUT/outputs_luanti_best.tgz" > "$OUT/outputs_luanti_best.tgz.sha256"
echo "Release staged at $OUT"
