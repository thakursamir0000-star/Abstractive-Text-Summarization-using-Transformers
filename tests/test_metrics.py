import numpy as np
import pytest

from evaluation.metrics import (
    bootstrap_ci,
    lead,
    novel_ngram_share,
    numbers_supported,
    paired_difference,
    rouge,
    rouge1_recall,
)


def test_rouge_bounds():
    text = "The council approved the new bike stations. Riders welcomed the plan."
    assert rouge(text, text) == pytest.approx({"rouge1": 100, "rouge2": 100, "rougeLsum": 100})
    assert rouge("apples and pears", "the council met on Tuesday")["rouge1"] == 0


def test_rouge_uses_stemming():
    assert rouge("the council votes", "the council voted")["rouge1"] == pytest.approx(100)


def test_rouge1_recall_measures_coverage_of_the_reference():
    assert rouge1_recall("council approved stations", "council approved stations") == pytest.approx(100)
    assert rouge1_recall("council", "council approved stations") == pytest.approx(100 / 3)


def test_lead_takes_the_first_sentences():
    article = "First point. Second point. Third point. Fourth point."
    assert lead(article, 3) == "First point. Second point. Third point."


def test_novel_ngram_share():
    source = "the city council voted to expand the bike scheme on tuesday"
    assert novel_ngram_share("the city council voted to expand", source) == 0
    assert novel_ngram_share("mayor praises cyclists", source) == 100
    assert novel_ngram_share("one", source) == 0  # no bigrams at all


def test_numbers_supported_catches_made_up_numbers():
    source = "The scheme cost 1,500 pounds and served 210,000 riders in 2024."
    assert numbers_supported("It cost 1500 pounds.", source) == 100
    assert numbers_supported("It cost 1,500 pounds and had 300 stations.", source) == 50
    assert numbers_supported("It was popular.", source) is None


def test_bootstrap_ci_contains_the_mean():
    values = np.random.default_rng(1).normal(20, 5, 200)
    low, high = bootstrap_ci(values)
    assert low < values.mean() < high
    assert bootstrap_ci([3.0] * 10) == (3.0, 3.0)


def test_paired_difference_sign():
    diff = paired_difference([10, 11, 12, 13], [12, 13, 14, 15])
    assert diff["mean"] == 2 and diff["ci_low"] == diff["ci_high"] == 2
