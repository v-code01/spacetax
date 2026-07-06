#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
fail() { echo "GATE FAIL: $*" >&2; exit 1; }
[ -d .venv ] && . .venv/bin/activate || { python3 -m venv .venv; . .venv/bin/activate; pip install -q -r requirements.txt; }
echo "== 1/6 ruff =="; ruff check src tests tools || fail ruff; echo "   ok"
echo "== 2/6 mypy --strict =="; MYPYPATH=src mypy --strict src tools/run_gen.py tools/analyze.py tools/verify.py || fail mypy; echo "   ok"
echo "== 3/6 pytest =="; python -m pytest -q || fail pytest
echo "== 4/6 pure-ASCII =="; bad=$(LC_ALL=C grep -rlP '[^\x00-\x7F]' src tests tools scripts README.md claims.toml REVIEW.md PREREG.md bench_results docs 2>/dev/null || true); [ -z "$bad" ] || { echo "$bad"; fail ascii; }; echo "   ok"
echo "== 5/6 no environment leak =="; pat='/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+/'; [ -f scripts/.leakpatterns ] && pat="$pat|$(grep -vE '^\s*(#|$)' scripts/.leakpatterns | paste -sd'|' -)"; leak=$(grep -rniIE --exclude-dir=__pycache__ "$pat" src tests tools README.md claims.toml REVIEW.md PREREG.md reproduce.sh docs 2>/dev/null || true); [ -z "$leak" ] || { echo "$leak"; fail "leak"; }; echo "   ok"
echo "== 6/6 independent verify =="; python tools/verify.py || fail verify; echo "   ok"
echo "ALL GATES PASS"
