# Adversarial review: spacetax

A skeptic's pass over the claims, and why each survives.

## "Everyone knows trailing whitespace matters for tokenizers - this is a known gotcha."
That it exists is known folklore; the magnitude is not. Measuring that a single trailing space changes the
output on 100% of prompts and turns a correct factual answer wrong 33% of the time - with a clean
token-boundary mechanism - turns a vague "be careful with whitespace" into a quantified, reproducible
hazard with a named cause. "Known gotcha" is not "breaks a third of factual answers."

## "The answer check is a crude substring match - maybe the 'wrong' answers are actually fine."
The check is coarse but exact and conservative, and the load-bearing cases are unambiguous: the no-space
form contains the accepted answer and the with-space form contains a plainly different, wrong continuation
(e.g. Rome vs "1000 km away from the capital of Spain"). A crude oracle can produce false "unchanged"
(missing a paraphrase) but rarely a false "correct-to-wrong" - and the effect is a 4-point accuracy drop
(14/15 to 10/15) across 15 prompts, not one cherry-picked case.

## "15 factual prompts is tiny."
The tokenization and output effects are 30/30 - not a rate that needs a large sample. For the answer
hazard, 5 of 15 going correct-to-wrong is a large effect with an obvious mechanism, offered as a hazard
demonstration (this happens, and here is why), not a precise population estimate. The README scopes it that
way.

## "Greedy decoding is a corner case; sampling would differ anyway."
Greedy at temperature 0 is exactly the setting where the comparison is exact and where a user expects a
stable answer to a factual question. It is the strict test: even the deterministic path is corrupted by an
invisible character. Under sampling the outputs differ for unrelated reasons, so nothing could be
attributed to the space.

## "The 'first token begins with a space' mechanism is just a proxy, read off the output text."
It is a faithful proxy: in a byte-level BPE decode, a leading space in the output text is exactly a
space-prefixed first token. The 100%-vs-7% split is a direct, exact reading of the recorded outputs and it
matches the causal story (the consumed trailing space removes the leading-space slot the model expects).

## "Maybe it is the extra token length, not the boundary, that derails it."
The extra token IS the boundary change - the trailing space is tokenized as its own token, shifting where
the next word starts. The mechanism section attributes the effect to that specific shift (the first
generated token can no longer carry a leading space), and the 100%-vs-7% first-token split is the direct
evidence for that specific mechanism, not just "one more token."

## "verify.py just echoes analyze.py."
verify.py re-reads results/gen.jsonl and recomputes the tokenization-change, output-change, and
answer-change rates and the first-token space mechanism with its own logic, sharing no code with
analyze.py or src.

## Pre-registration honesty
All four predictions were committed before the analysis and held. PREREG.md flags P3 (a trailing space can
silently make a correct answer wrong) as the headline hazard up front.
