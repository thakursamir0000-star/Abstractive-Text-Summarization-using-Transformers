from itertools import pairwise

import pytest

from src.chunking import chunk_text, pack, split_sentences


def words(texts):
    return [len(t.split()) for t in texts]


def test_split_sentences_keeps_abbreviations_and_quotes():
    text = 'Mr. Smith visited the U.S. Army base. He left at noon. "Why?" she asked.\n\nA new paragraph'
    assert split_sentences(text) == [
        "Mr. Smith visited the U.S. Army base.",
        "He left at noon.",
        '"Why?" she asked.',
        "A new paragraph",
    ]


def test_split_sentences_does_not_break_decimals_or_lowercase():
    assert split_sentences("It cost 3.5 million. prices rose e.g. in May.") == [
        "It cost 3.5 million. prices rose e.g. in May."
    ]


def test_pack_respects_budget_and_covers_everything_in_order():
    counts = [5, 7, 3, 8, 2, 6, 4]
    spans = pack(counts, budget=12)
    assert all(sum(counts[a:b]) <= 12 for a, b in spans)
    assert spans[0][0] == 0 and spans[-1][1] == len(counts)
    assert all(b1 == a2 for (_, b1), (a2, _) in pairwise(spans))  # no overlap requested


def test_pack_overlaps_and_always_moves_forward():
    counts = [4] * 10
    spans = pack(counts, budget=12, overlap=4)
    assert all(a2 == b1 - 1 for (_, b1), (a2, _) in pairwise(spans))  # one unit shared
    assert [a for a, _ in spans] == sorted({a for a, _ in spans})
    # Overlap as big as the budget must still terminate.
    assert pack(counts, budget=8, overlap=100)[-1][1] == 10


def test_pack_gives_an_oversized_unit_its_own_span():
    assert pack([3, 50, 3], budget=10) == [(0, 1), (1, 2), (2, 3)]
    with pytest.raises(ValueError):
        pack([1], budget=0)


def test_chunk_text_fits_the_budget_and_keeps_every_sentence():
    text = " ".join(f"Sentence number {i} has six words." for i in range(30))
    chunks = chunk_text(text, words, budget=20, overlap=6)
    assert len(chunks) > 1 and all(n <= 20 for n in words(chunks))
    joined = " ".join(chunks)
    assert all(f"Sentence number {i} " in joined for i in range(30))
    # Consecutive chunks share the boundary sentence.
    assert chunks[0].split(". ")[-1] in chunks[1]


def test_chunk_text_splits_a_sentence_longer_than_the_budget():
    long_sentence = " ".join(["word"] * 45) + "."
    chunks = chunk_text(long_sentence, words, budget=20)
    assert words(chunks) == [20, 20, 5]


def test_chunk_text_of_empty_text():
    assert chunk_text("   \n\n ", words, budget=10) == []
