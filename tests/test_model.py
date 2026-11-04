import pytest

from src.config import LENGTH_PRESETS, MAX_TEXT_CHARS
from src.model import validate_text

pytestmark = pytest.mark.model


@pytest.mark.parametrize("text, message", [
    ("", "enter some text"),
    ("   ", "enter some text"),
    ("too short", "at least"),
    ("x" * (MAX_TEXT_CHARS + 1), "longer than"),
], ids=["empty", "blank", "short", "too-long"])
def test_validate_text_rejects_bad_input(text, message):
    with pytest.raises(ValueError, match=message):
        validate_text(text)


def test_window_comes_from_the_model(tiny):
    # The tiny model has 100 positions, so that is its window, not the configured 1,024.
    assert tiny.max_input_tokens == 100 and tiny.max_output_tokens == 100


def test_short_text_is_one_pass(tiny):
    result = tiny.summarize("The council approved forty new bike stations on Tuesday after a pilot.")
    assert result.chunks == 1 and result.parts == [] and not result.truncated
    assert isinstance(result.text, str) and result.seconds > 0


def test_long_text_is_split_not_truncated(tiny, long_text):
    assert not tiny.fits(long_text)
    calls = []
    result = tiny.summarize(long_text, on_progress=lambda done, total: calls.append((done, total)))
    assert result.chunks > 1 and len(result.parts) == result.chunks
    assert not result.truncated and result.input_tokens > tiny.max_input_tokens
    assert calls and calls[-1] == (result.chunks, result.chunks)


def test_every_chunk_fits_the_window(tiny, long_text):
    chunks = tiny.chunk(long_text)
    assert all(tiny.fits(c) for c in chunks)
    assert "Paragraph 1 " in chunks[0] and "Critics disagreed." in chunks[-1]


def test_truncate_strategy_reports_truncation(tiny, long_text):
    result = tiny.summarize(long_text, strategy="truncate")
    assert result.truncated and result.chunks == 1 and result.parts == []
    with pytest.raises(ValueError, match="Unknown strategy"):
        tiny.summarize(long_text, strategy="magic")


@pytest.mark.parametrize("length", list(LENGTH_PRESETS))
def test_every_length_preset_runs(tiny, length):
    # Presets above the model's 100 positions are clamped instead of crashing.
    assert tiny.generate(["The council approved forty new bike stations on Tuesday."], length)


def test_batches_with_padding_match_single_runs(tiny):
    texts = ["A short sentence about bikes.", "A much longer sentence about the council and its plans for roads."]
    assert tiny.generate(texts, batch_size=2) == [tiny.generate([t])[0] for t in texts]


def test_generation_always_uses_the_kv_cache(tiny, monkeypatch):
    # A fine-tuned checkpoint saved with use_cache=False generated many times slower.
    monkeypatch.setattr(tiny.model.config, "use_cache", False)
    seen = {}
    original = tiny.model.generate

    def spy(**kwargs):
        seen.update(kwargs)
        return original(**kwargs)

    monkeypatch.setattr(tiny.model, "generate", spy)
    tiny.generate(["The council approved forty new bike stations on Tuesday."])
    assert seen["use_cache"] is True and "attention_mask" in seen


def test_cpu_generates_one_text_at_a_time(tiny, monkeypatch):
    # Batched beam search on CPU was no faster and crashed PyTorch (access violation) on a 16 GB laptop.
    sizes = []
    original = tiny.model.generate

    def spy(**kwargs):
        sizes.append(kwargs["input_ids"].shape[0])
        return original(**kwargs)

    monkeypatch.setattr(tiny.model, "generate", spy)
    tiny.generate(["One short text about bikes.", "Another text about roads.", "A third text."])
    assert sizes == [1, 1, 1]
