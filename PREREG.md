# Pre-registration: spacetax

Committed to git BEFORE the final analysis. Not edited afterward.

## What is measured

For 30 prompts (15 of them factual with a known short answer), each compared with and without a single
trailing space, on a real llama.cpp server (Qwen2.5-1.5B): the tokenization (/tokenize), the greedy
(temperature 0, fixed seed) 64-token continuation, and - for factual prompts - whether the answer is
correct. Everything is deterministic, so the comparisons are exact.

## Predictions

**P1 - a trailing space changes the tokenization on essentially all prompts.** The space forms or alters a
token, changing the token sequence on more than 90% of prompts (typically adding one token). *Falsifier:*
tokenization unchanged on more than 10% of prompts.

**P2 - a trailing space changes the greedy output on a large majority of prompts.** Because the token
sequence differs, the greedy continuation differs on more than 60% of prompts. *Falsifier:* output changed
on 60% or fewer.

**P3 - it is a correctness hazard, not just stylistic.** On factual prompts a trailing space flips the
answer on a non-trivial fraction, including turning correct answers wrong. *Falsifier:* no factual answer
changes, or none go from correct to wrong.

**P4 - the mechanism is the token boundary.** Qwen's byte-level BPE prefixes word tokens with a space
marker, so without a trailing space the first generated token almost always begins with a space; with the
trailing space consumed, the first generated token must NOT begin with a space, an off-distribution
condition. Predict the "first token begins with a space" rate is near-universal without the trailing space
and much lower with it. *Falsifier:* the two rates are similar.

## Commitment

P3 (a stray trailing space can silently make a correct answer wrong) is the headline hazard. Results are
reported as-is.
