# spacetax: a single trailing space changes the tokenization, the output, and the answer

To a human, `"The capital of Italy is"` and `"The capital of Italy is "` (one trailing space) are the same
prompt. To a byte-level BPE tokenizer they are not: the trailing space becomes a separate token, so the
model sees a different sequence and, under greedy decoding, produces different - sometimes wrong - text.
This measures how often and how badly a single trailing space changes the greedy output on a real
llama.cpp server (Qwen2.5-1.5B), including whether it flips factual answers, and why.

## Pre-registration

Four predictions were committed to git (`PREREG.md`) before the analysis: (P1) a trailing space changes
the tokenization on essentially all prompts; (P2) it changes the greedy output on a large majority; (P3)
it is a correctness hazard (flips factual answers); (P4) the mechanism is the token boundary. **All four
held.**

## Results

30 prompts (15 factual), each with and without a trailing space:

```
 tokenization changed    30/30   (100%)   (always +1 token)
 greedy output changed   30/30   (100%)
 answer changed           6/15   (40% of factual prompts)
 correct -> wrong         5/15   (33% of factual prompts)
```

On the 15 factual prompts, the no-space form answers 14/15 correctly; adding a trailing space drops that
to 10/15. For example, `"The capital of Italy is"` greedily continues toward **Rome**, but
`"The capital of Italy is "` derails into `"1000 km away from the capital of Sp..."` - a wrong answer, with
no error and plausible-looking text.

**The mechanism - the token boundary:**

```
 first generated token begins with a space:
   without trailing space:   30/30   (100%)
   with trailing space:        2/30   (7%)
```

1. **A single trailing space changes the tokenization on 100% of prompts** (always adding exactly one
   token) and the greedy output on 100%. The two requests are identical to a person and different to the
   model.

2. **It is a correctness hazard, not a stylistic one.** On factual prompts the trailing space flips the
   answer 6/15 times and turns a correct answer wrong 5/15 times (33%) - dropping accuracy from 14/15 to
   10/15. The failure is silent: no error, plausible output, wrong answer.

3. **The mechanism is the token boundary.** Qwen's byte-level BPE prefixes word tokens with a space marker,
   so normally the first generated token carries its own leading space (100% of the time here). A trailing
   space in the prompt is consumed as a separate token, so the model must emit a token that does *not*
   begin with a space (only 7% do) - a condition it rarely saw in training, which is why the continuation
   derails.

4. **The fix is trivial and worth stating plainly: strip trailing whitespace from prompts.** Because the
   failure is silent and the perturbation is a single invisible character, this is an easy and common way
   to quietly corrupt LLM output in production.

## The one-line finding

A single trailing space - one invisible character - changes a byte-level-BPE model's tokenization and
greedy output on 100% of prompts and turns a correct factual answer wrong a third of the time, because the
consumed space forces the model's first token to be one that does not begin with a space, which it was
rarely trained to produce.

## Reproduce

```
./reproduce.sh                 # analyze + verify from the committed outputs (no server needed)
./scripts/gate.sh              # ruff, mypy --strict, pytest, ASCII, leak scan, independent verify
```

To regenerate the raw outputs, run against a llama.cpp server: `python tools/run_gen.py URL`.
`results/gen.jsonl` is committed, so `tools/analyze.py` and the independent `tools/verify.py` (which
recomputes the rates and the mechanism with its own logic) reproduce without the server.

## Limitations and falsifiers

- One model (Qwen2.5-1.5B), one tokenizer family (byte-level BPE), greedy decoding, a single trailing
  space (a natural, common perturbation), 15 factual prompts with hand-listed accepted answers. The
  finding is that a trailing space changes tokenization and output and can change answers - a prompt-
  hygiene hazard - not a claim about which continuation is better in the open-ended cases.
- The answer check is a case-insensitive substring match against a small accepted-answer list; it is a
  coarse but exact oracle for "did the known answer appear," and the striking cases (correct -> derailed)
  are unambiguous.
- **Falsifier (the informative one):** if a trailing space had left the answer unchanged (as its
  invisibility to a human suggests), the correct-to-wrong rate would be ~0; it is 33%.

MIT licensed. The oracle is the deterministic tokenizer and greedy output; comparisons are exact. No LLM
judgement.
