"""Pure comparison helpers for the trailing-space study. A byte-level BPE tokenizer (GPT-2 / Qwen) remaps
the space byte 0x20 to a printable marker glyph (chr(288)) and prefixes most word tokens with it, so
"whether the next token begins with a space" is "does its decoded string start with that marker". No I/O.
"""
from __future__ import annotations

SPACE_MARKER = chr(288)  # GPT-2 byte-to-unicode remap of the space byte (0x20)


def token_delta(a: list[int], b: list[int]) -> int:
    """Number of extra tokens in b relative to a (can be negative)."""
    return len(b) - len(a)


def differs(a: object, b: object) -> bool:
    """True iff the two sequences (token lists or strings) are not equal."""
    return a != b


def starts_with_space(tok: str) -> bool:
    """Does a decoded token string begin with the byte-level space marker (i.e. it is a space-prefixed
    word token)? Empty string -> False."""
    return bool(tok) and tok[0] == SPACE_MARKER


def answer_matches(text: str, accepted: list[str]) -> bool:
    """True iff any accepted answer occurs (case-insensitive) as a substring of text."""
    low = text.lower()
    return any(a.lower() in low for a in accepted)
