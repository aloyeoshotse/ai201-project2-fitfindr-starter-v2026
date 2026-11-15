"""
Measure what one agent run costs: tokens and seconds, averaged over 10 runs.

    AI201_CACHE=0 python measure_cost.py

Runs 10 queries that the data can match (so each one goes through all three
steps), reads the numbers back out of logs/runs.jsonl, and prints the average.
Cache must be off, or cached answers would cost nothing and read as free.
"""

import sys

import config
import runlog
from agent import run_agent
from utils.data_loader import get_example_wardrobe

QUERIES = [
    "vintage graphic tee under $30",
    "levis jeans",
    "silk slip dress",
    "leather bomber jacket under $80",
    "denim jacket under $50",
] * 2

if config.CACHE_ENABLED:
    sys.exit("Turn the cache off first: AI201_CACHE=0 python measure_cost.py")

for q in QUERIES:
    run_agent(q, get_example_wardrobe())

rows = runlog.tail(len(QUERIES))
ok = [r for r in rows if r["status"] == "ok"]
print(f"{len(ok)} of {len(rows)} runs completed")
for key in ("model_calls", "prompt_tokens", "output_tokens", "duration_s"):
    print(f"avg {key}: {sum(r[key] for r in ok) / len(ok):.2f}")
