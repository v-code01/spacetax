"""Correctness tests for the trailing-space comparison helpers."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import spacetax as s  # noqa: E402


def test_token_delta() -> None:
    assert s.token_delta([1, 2, 3], [1, 2, 3, 4]) == 1
    assert s.token_delta([1, 2], [1, 2]) == 0
    assert s.token_delta([1, 2, 3], [1, 2]) == -1


def test_differs() -> None:
    assert s.differs([1, 2], [1, 3]) is True
    assert s.differs([1, 2], [1, 2]) is False
    assert s.differs("abc", "abc") is False


def test_starts_with_space_marker() -> None:
    marker = chr(288)  # GPT-2 byte-level remap of the space byte 0x20
    assert s.starts_with_space(marker + "Paris") is True
    assert s.starts_with_space("Paris") is False
    assert s.starts_with_space("") is False


def test_answer_matches() -> None:
    assert s.answer_matches("The answer is Paris.", ["paris"]) is True
    assert s.answer_matches("PARIS!", ["paris"]) is True  # case-insensitive
    assert s.answer_matches("Rome", ["paris"]) is False
    assert s.answer_matches("blue and green", ["red", "green"]) is True
    assert s.answer_matches("x", []) is False
