import time, json, os, subprocess, pathlib
ROOT = pathlib.Path.home()/"luanti_capability"
ADIR = ROOT/"outputs_luanti_safe"
SEEN = ROOT/"artifacts/.seen_ckpts.txt"
SEEN.parent.mkdir(parents=True, exist_ok=True)
seen = set(SEEN.read_text().splitlines()) if SEEN.exists() else set()

def run(cmd):
    print(">>", cmd); return subprocess.call(cmd, shell=True)

while True:
    ckpts = sorted(p.name for p in ADIR.glob("checkpoint-*") if p.is_dir())
    new = [c for c in ckpts if c not in seen]
    if new:
        ck = new[-1]
        print(f"[auto] detected {ck} → running Gate D/E")
        # Gate D
        cmdD = (
          'TORCHDYNAMO_DISABLE=1 TOKENIZERS_PARALLELISM=false HF_HUB_OFFLINE= '
          '/home/tdeshane/miniconda3/envs/gptoss/bin/python -u -m eval.test_adapter '
          '--base unsloth/gpt-oss-20b-unsloth-bnb-4bit '
          f'--adapters_dir {ADIR} '
          '--eval data/eval/luanti_eval.jsonl '
          '--template prompts/iir_template.txt '
          '--k 5 --temperature 0.2 --top_p 0.9 --max_new_tokens 300 '
          '--scales 0.25 0.5 1.0 --seed 3407 '
          '--out_dir eval/results/ | tee -a eval/results/test_adapter.log'
        )
        if run(cmdD)!=0: print("[auto] Gate D failed")
        # Gate E
        cmdE = (
          '/home/tdeshane/miniconda3/envs/gptoss/bin/python -u -m eval.compare '
          '--baseline eval/results/baseline.json '
          '--results_dir eval/results/ | tee eval/results/deltas.txt'
        )
        run(cmdE)
        seen.add(ck); SEEN.write_text("\n".join(sorted(seen)))
    time.sleep(30)
