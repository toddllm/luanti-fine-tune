
stats:
	@echo "== Harvesting training + eval stats =="
	python scripts/collect_training_stats.py
	python scripts/collect_eval_stats.py  
	python scripts/print_eta.py | tee ETA.txt
	@echo "== Wrote TRAINING_STATS.json, EVAL_TIMES.(csv|json), ETA.txt =="
