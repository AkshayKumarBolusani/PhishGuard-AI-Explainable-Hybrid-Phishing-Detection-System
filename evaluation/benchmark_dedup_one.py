"""Dedup-sensitivity benchmark driver for one or more corpora.

Usage: ./venv/bin/python benchmark_dedup_one.py CEAS_08 [Nazario_5 ...]

Runs the identical dedup-before-split protocol from benchmark_dedup.py
for each named corpus and writes evaluation/benchmark_results_dedup_<name>.json
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from benchmark_dedup import RuleEngine, evaluate_corpus  # noqa: E402

OUT = HERE
OUT.mkdir(exist_ok=True)


def main():
    rule_engine = RuleEngine()
    print(f"Rule engine loaded: {len(rule_engine.rules)} rules", flush=True)
    for name in sys.argv[1:]:
        t0 = time.time()
        res = evaluate_corpus(name, rule_engine)
        out = OUT / f"benchmark_results_dedup_{name}.json"
        out.write_text(json.dumps(res, indent=2))
        print(f"[{name}] DONE in {time.time()-t0:.0f}s -> {out}", flush=True)


if __name__ == "__main__":
    main()
