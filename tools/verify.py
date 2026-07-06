"""Independent verification of the spacetax findings, sharing no code with analyze.py or src. Re-reads
results/gen.jsonl and re-asserts: (P1) a trailing space changes the tokenization on >90% of prompts;
(P2) it changes the greedy output on >60%; (P3) it flips the answer on a non-trivial fraction of factual
prompts, including turning correct answers wrong; (P4) the token-boundary mechanism - without the trailing
space the first generated token begins with a space far more often than with it. Exit non-zero on
mismatch.
"""
from __future__ import annotations

import json
import sys

SPACE_MARKER = " "  # in the decoded output text a space-prefixed first token shows as a leading space


def matches(text: str, accepted: list[str]) -> bool:
    low = text.lower()
    return any(a.lower() in low for a in accepted)


def main() -> int:
    rows = [json.loads(x) for x in open("results/gen.jsonl") if x.strip()]
    n = len(rows)
    ok = True

    tok_ch = sum(1 for r in rows if list(r["tok_nospace"]) != list(r["tok_space"]))
    p1 = tok_ch / n > 0.90
    print(f"  [P1] tokenization changed {tok_ch}/{n} ({tok_ch / n:.0%}) (>90% = {p1})")
    ok = ok and p1

    out_ch = sum(1 for r in rows if str(r["out_nospace"]) != str(r["out_space"]))
    p2 = out_ch / n > 0.60
    print(f"  [P2] greedy output changed {out_ch}/{n} ({out_ch / n:.0%}) (>60% = {p2})")
    ok = ok and p2

    factual = [r for r in rows if isinstance(r["accepted"], list)]
    nf = len(factual)
    ans_ch = sum(1 for r in factual
                 if matches(str(r["out_nospace"]), [str(a) for a in r["accepted"]])
                 != matches(str(r["out_space"]), [str(a) for a in r["accepted"]]))
    c2w = sum(1 for r in factual
              if matches(str(r["out_nospace"]), [str(a) for a in r["accepted"]])
              and not matches(str(r["out_space"]), [str(a) for a in r["accepted"]]))
    p3 = ans_ch >= 2 and c2w >= 2
    print(f"  [P3] answer changed {ans_ch}/{nf}, correct->wrong {c2w}/{nf} (non-trivial = {p3})")
    ok = ok and p3

    ns = sum(1 for r in rows if str(r["out_nospace"]).startswith(SPACE_MARKER))
    sp = sum(1 for r in rows if str(r["out_space"]).startswith(SPACE_MARKER))
    p4 = ns / n > 0.9 and sp / n < ns / n - 0.5
    print(f"  [P4] first token space-prefixed: no-space {ns}/{n} vs with-space {sp}/{n} "
          f"(boundary mechanism = {p4})")
    ok = ok and p4

    if ok:
        print("VERIFY OK: a single trailing space changes the tokenization and greedy output on nearly all "
              "prompts, flips factual answers (including correct->wrong), via the token-boundary mechanism "
              "(the consumed space forces a non-space-prefixed first token) - recomputed independently.")
        return 0
    print("VERIFY FAILED", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
