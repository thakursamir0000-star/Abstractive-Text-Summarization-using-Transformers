"""Split long text into model-sized chunks at sentence boundaries.

BART reads at most 1,024 tokens. Instead of silently cutting the rest off,
long text is packed sentence by sentence into chunks that fit, with a little
overlap so a point that straddles a boundary is not lost. Token counting is
passed in, so this module needs no model and is easy to test.
"""

from __future__ import annotations

import re
from collections.abc import Callable

# Split after . ! ? (optionally followed by a closing quote or bracket) when the
# next sentence starts with a capital, digit or opening quote.
_SENTENCE_BREAK = re.compile(
    r"(?:(?<=[.!?])|(?<=[.!?][\"'”’)\]]))\s+(?=[\"'“‘(\[]?[A-Z0-9])"
)
_ABBREVIATIONS = {
    "mr", "mrs", "ms", "dr", "prof", "st", "jr", "sr", "vs", "no", "gen", "gov", "sen",
    "rep", "col", "lt", "sgt", "capt", "u.s", "u.k", "u.n", "e.g", "i.e", "etc", "inc", "co",
}

CountTokens = Callable[[list[str]], list[int]]


def split_sentences(text: str) -> list[str]:
    """Sentences in order; paragraph breaks always end a sentence."""
    sentences: list[str] = []
    for paragraph in re.split(r"\n\s*\n|\r?\n", text):
        paragraph = " ".join(paragraph.split())
        if not paragraph:
            continue
        pieces = _SENTENCE_BREAK.split(paragraph)
        merged: list[str] = []
        for piece in pieces:
            # "Mr. Smith" or "the U.S. Army" should not end a sentence.
            last_word = merged[-1].rsplit(" ", 1)[-1].rstrip(".").lower() if merged else ""
            if merged and last_word in _ABBREVIATIONS:
                merged[-1] = f"{merged[-1]} {piece}"
            else:
                merged.append(piece)
        sentences.extend(merged)
    return sentences


def pack(counts: list[int], budget: int, overlap: int = 0) -> list[tuple[int, int]]:
    """Greedy packing of units (sentences or words) into [start, end) spans.

    Each span's counts sum to at most `budget`, unless a single unit is bigger
    than the budget (callers split those first). Consecutive spans share
    trailing units worth up to `overlap` tokens, and every span starts later
    than the one before, so the loop always ends.
    """
    if budget <= 0:
        raise ValueError("budget must be positive")
    spans: list[tuple[int, int]] = []
    start, n = 0, len(counts)
    while start < n:
        end, total = start, 0
        while end < n and total + counts[end] <= budget:
            total += counts[end]
            end += 1
        end = max(end, start + 1)
        spans.append((start, end))
        if end >= n:
            break
        back, carried = end, 0
        while back - 1 > start and carried + counts[back - 1] <= overlap:
            back -= 1
            carried += counts[back]
        start = back
    return spans


def chunk_text(text: str, count_tokens: CountTokens, budget: int, overlap: int = 0) -> list[str]:
    """Split `text` into chunks of at most `budget` tokens, at sentence boundaries.

    `count_tokens` maps a list of strings to their token counts. A sentence
    longer than the budget is split between words.
    """
    units: list[str] = []
    sentences = split_sentences(text)
    for sentence, n in zip(sentences, count_tokens(sentences), strict=True):
        if n <= budget:
            units.append(sentence)
            continue
        words = sentence.split()
        word_counts = count_tokens(words)
        units.extend(" ".join(words[a:b]) for a, b in pack(word_counts, budget))
    if not units:
        return []
    counts = count_tokens(units)
    return [" ".join(units[a:b]) for a, b in pack(counts, budget, overlap)]
