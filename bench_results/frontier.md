# spacetax: a single trailing space changes the tokenization, the output, and the answer

For 30 prompts, each compared with and without a single trailing space, using the real tokenizer (/tokenize) and greedy (temperature 0) generation on a llama.cpp server (Qwen2.5-1.5B). Everything is deterministic, so the comparisons are exact.

## How often a trailing space changes things

   tokenization changed    30/30   (100%)   (token count delta: [1])
   greedy output changed   30/30   (100%)
   answer changed          6/15   (40% of factual prompts)
   correct -> wrong        5/15   (33% of factual prompts)

On the 15 factual prompts (with a known answer), the no-space form gets 14/15 right; adding a trailing space drops that to 10/15. The space is not a stylistic tweak - it silently breaks the answer on a third of factual prompts.

## The mechanism: the token boundary

   first generated token begins with a space:
     without trailing space:   30/30   (100%)
     with trailing space:      2/30   (7%)

Qwen's byte-level BPE prefixes word tokens with a space marker, so normally the model's first generated token carries its own leading space (100% of the time). A trailing space in the prompt is consumed as a separate token, so the model must now emit a token that does NOT begin with a space (7% do) - an off-distribution condition it was rarely trained on, which is why the continuation derails.

## findings

1. A single trailing space changes the tokenization on 100% of prompts (always +1 token) and the greedy output on 100%.
2. It is a correctness hazard, not just a stylistic one: on factual prompts the trailing space flips the answer 6/15 times and turns a correct answer wrong 5/15 times (33%).
3. The mechanism is the token boundary: without the space the first generated token is space-prefixed 100% of the time; with the space consumed, only 7% are, forcing an off-distribution continuation.
4. The fix is trivial and worth stating: strip trailing whitespace from prompts. The failure is silent (no error, plausible-looking output), which is what makes it dangerous.

