#!/usr/bin/env bash
# Regenerate the spacetax analysis. results/gen.jsonl is committed, so this reproduces without a server.
# To regenerate raw outputs: python tools/run_gen.py URL  (a llama.cpp /completion endpoint).
set -euo pipefail
cd "$(dirname "$0")"
. .venv/bin/activate
python tools/analyze.py
python tools/verify.py
echo "regenerated; see bench_results/frontier.md"
