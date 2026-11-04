"""Summary quality metrics: ROUGE, a lead-N baseline, abstractiveness, number checks
and bootstrap confidence intervals."""

from __future__ import annotations

import re

import numpy as np
from rouge_score import rouge_scorer

from src.chunking import split_sentences

ROUGE_TYPES = ("rouge1", "rouge2", "rougeLsum")
_SCORER = rouge_scorer.RougeScorer(list(ROUGE_TYPES), use_stemmer=True)
_WORD = re.compile(r"[a-z0-9]+")
_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


def _lines(text: str) -> str:
    # rougeLsum scores sentence by sentence and expects one sentence per line.
    return "\n".join(split_sentences(text))


def rouge(prediction: str, reference: str) -> dict[str, float]:
    """ROUGE F1 (x100) with stemming, as used for the published CNN/DailyMail results."""
    scores = _SCORER.score(_lines(reference), _lines(prediction))
    return {name: scores[name].fmeasure * 100 for name in ROUGE_TYPES}


def rouge1_recall(prediction: str, reference: str) -> float:
    """Share of the reference's words (x100) that the prediction covers."""
    return _SCORER.score(reference, prediction)["rouge1"].recall * 100


def lead(text: str, n: int = 3) -> str:
    """The first n sentences: the classic, strong baseline for news."""
    return " ".join(split_sentences(text)[:n])


def _ngrams(text: str, n: int) -> list[tuple[str, ...]]:
    words = _WORD.findall(text.lower())
    return [tuple(words[i:i + n]) for i in range(len(words) - n + 1)]


def novel_ngram_share(summary: str, source: str, n: int = 2) -> float:
    """% of the summary's n-grams that do not appear in the source.

    0 means pure copying (extractive); higher means more rephrasing.
    """
    grams = _ngrams(summary, n)
    if not grams:
        return 0.0
    source_grams = set(_ngrams(source, n))
    return 100 * sum(g not in source_grams for g in grams) / len(grams)


def _numbers(text: str) -> list[str]:
    return [m.replace(",", "").rstrip(".") for m in _NUMBER.findall(text)]


def numbers_supported(summary: str, source: str) -> float | None:
    """% of numbers in the summary that also appear in the source.

    A cheap hallucination check: a number the source never mentions was made
    up. None when the summary has no numbers.
    """
    numbers = _numbers(summary)
    if not numbers:
        return None
    source_numbers = set(_numbers(source))
    return 100 * sum(n in source_numbers for n in numbers) / len(numbers)


def bootstrap_ci(values, n_boot: int = 2000, seed: int = 0, level: float = 0.95) -> tuple[float, float]:
    """Percentile bootstrap confidence interval for the mean."""
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    means = values[rng.integers(0, len(values), (n_boot, len(values)))].mean(axis=1)
    tail = (1 - level) / 2 * 100
    return float(np.percentile(means, tail)), float(np.percentile(means, 100 - tail))


def paired_difference(a, b, n_boot: int = 2000, seed: int = 0) -> dict[str, float]:
    """Mean of (b - a) over the same items, with a bootstrap 95% interval."""
    diff = np.asarray(b, dtype=float) - np.asarray(a, dtype=float)
    low, high = bootstrap_ci(diff, n_boot, seed)
    return {"mean": float(diff.mean()), "ci_low": low, "ci_high": high}
