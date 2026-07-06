"""For each prompt and the same prompt with a single trailing space, query the real tokenizer
(/tokenize) and the greedy (temperature 0) continuation (/completion) of a llama.cpp server, and record
both. Factual prompts carry a list of accepted answers so a later step can check whether the trailing
space changes the answer. The tokenizer and greedy output are deterministic, so all comparisons are exact.
Writes one JSON line per prompt to results/gen.jsonl.

The server URL is an argument, so no private host or port is embedded.

Usage: python tools/run_gen.py [URL]   (default a generic localhost placeholder)
"""
from __future__ import annotations

import json
import sys
import urllib.request

N_PREDICT = 64

# (prompt, accepted_answers_or_None). A non-None answer list marks a factual prompt.
CORPUS: list[tuple[str, list[str] | None]] = [
    ("The capital of France is", ["paris"]),
    ("The capital of Japan is", ["tokyo"]),
    ("The capital of Italy is", ["rome"]),
    ("The largest planet in the solar system is", ["jupiter"]),
    ("The chemical symbol for gold is", ["au"]),
    ("The opposite of hot is", ["cold"]),
    ("The opposite of up is", ["down"]),
    ("Two plus two equals", ["4", "four"]),
    ("Ten minus three equals", ["7", "seven"]),
    ("The first president of the United States was", ["washington"]),
    ("The author of Romeo and Juliet is", ["shakespeare"]),
    ("The speed of light is approximately", ["300", "3", "186", "299"]),
    ("Water is made of hydrogen and", ["oxygen"]),
    ("The number of days in a week is", ["7", "seven"]),
    ("The freezing point of water in Celsius is", ["0", "zero"]),
    ("Once upon a time there was a", None),
    ("My favorite color is", None),
    ("The best way to learn programming is", None),
    ("In the morning I like to", None),
    ("The weather today is", None),
    ("She opened the door and saw", None),
    ("The most important thing in life is", None),
    ("A good recipe for dinner is", None),
    ("The future of technology will", None),
    ("Write a short poem about", None),
    ("The meaning of the word serendipity is", None),
    ("To make a paper airplane, first", None),
    ("The history of the Roman Empire began", None),
    ("Explain why the sky is", None),
    ("My plan for the weekend is to", None),
]


def tokenize(url: str, text: str) -> list[int]:
    u = url.rsplit("/", 1)[0] + "/tokenize"
    req = urllib.request.Request(u, data=json.dumps({"content": text}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        toks = json.loads(r.read())["tokens"]
    return [int(t) for t in toks]


def generate(url: str, prompt: str) -> str:
    body = {"prompt": prompt, "n_predict": N_PREDICT, "temperature": 0.0, "seed": 1,
            "cache_prompt": False}
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        obj = json.loads(r.read())
    content = obj["content"]
    assert isinstance(content, str)
    return content


def main(argv: list[str]) -> int:
    url = argv[1] if len(argv) > 1 else "http://127.0.0.1:8001/completion"
    rows = []
    for i, (prompt, accepted) in enumerate(CORPUS):
        sp = prompt + " "
        row = {
            "id": i, "prompt": prompt, "accepted": accepted,
            "tok_nospace": tokenize(url, prompt), "tok_space": tokenize(url, sp),
            "out_nospace": generate(url, prompt), "out_space": generate(url, sp),
        }
        rows.append(row)
        print(f"  {i}: done")
    with open("results/gen.jsonl", "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    print(f"wrote results/gen.jsonl ({len(rows)} prompts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
