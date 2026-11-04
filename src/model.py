"""BART summarizer that handles text of any length.

    from src.model import Summarizer
    summarizer = Summarizer("facebook/bart-large-cnn")
    result = summarizer.summarize(long_text)
    result.text, result.parts, result.chunks

Text that fits in the model's 1,024-token window is summarized in one pass.
Longer text is split into overlapping, sentence-aligned chunks; each chunk is
summarized ("map"), and the chunk summaries are summarized again ("reduce").
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from src.chunking import chunk_text
from src.config import (
    CHUNK_OVERLAP_TOKENS,
    DEFAULT_LENGTH,
    LENGTH_PRESETS,
    MAX_INPUT_TOKENS,
    MAX_TEXT_CHARS,
    MIN_TEXT_CHARS,
    MODEL_PATH,
    NUM_BEAMS,
    get_logger,
)

logger = get_logger(__name__)

MAX_REDUCE_ROUNDS = 3
Progress = Callable[[int, int], None]


@dataclass
class Summary:
    text: str
    input_tokens: int
    chunks: int = 1  # how many pieces the input was split into
    parts: list[str] = field(default_factory=list)  # one summary per chunk (empty for one pass)
    truncated: bool = False  # True only if the input was cut (strategy="truncate")
    seconds: float = 0.0


def validate_text(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Please enter some text to summarize.")
    text = text.strip()
    if len(text) < MIN_TEXT_CHARS:
        raise ValueError(f"Text must be at least {MIN_TEXT_CHARS} characters long.")
    if len(text) > MAX_TEXT_CHARS:
        raise ValueError(f"Text is longer than the {MAX_TEXT_CHARS:,}-character limit.")
    return text


class Summarizer:
    def __init__(self, model_path: str = MODEL_PATH, device: str | None = None,
                 max_input_tokens: int = MAX_INPUT_TOKENS):
        self.model_path = model_path
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        logger.info("Loading %s on %s", model_path, self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path).to(self.device).eval()
        positions = getattr(self.model.config, "max_position_embeddings", None) or max_input_tokens
        tokenizer_limit = self.tokenizer.model_max_length if self.tokenizer.model_max_length < 1e6 else positions
        self.max_input_tokens = min(max_input_tokens, positions, tokenizer_limit)
        self.max_output_tokens = positions

    @property
    def num_parameters(self) -> int:
        return sum(p.numel() for p in self.model.parameters())

    def count_tokens(self, texts: list[str]) -> list[int]:
        """Tokens per string, counted as they appear mid-text (after a space)."""
        if not texts:
            return []
        encoded = self.tokenizer([" " + t for t in texts], add_special_tokens=False)["input_ids"]
        return [len(ids) for ids in encoded]

    def fits(self, text: str) -> bool:
        return len(self.tokenizer(text)["input_ids"]) <= self.max_input_tokens

    def chunk(self, text: str) -> list[str]:
        # Leave room for <s> and </s>, plus one token of slack for the first word.
        budget = self.max_input_tokens - 3
        return chunk_text(text, self.count_tokens, budget, min(CHUNK_OVERLAP_TOKENS, budget // 4))

    def generate(self, texts: list[str], length: str = DEFAULT_LENGTH, batch_size: int | None = None,
                 on_progress: Progress | None = None) -> list[str]:
        """Summarize each text in one pass (inputs longer than the window are cut)."""
        # Batching only pays off on a GPU. On CPU it was no faster, and 4 chunks
        # x 4 beams of 1,024 tokens needed ~2 GB more and crashed PyTorch with an
        # access violation on a 16 GB laptop.
        batch_size = batch_size or (4 if self.device == "cuda" else 1)
        min_len, max_len = LENGTH_PRESETS[length]
        max_len = min(max_len, self.max_output_tokens)
        min_len = min(min_len, max_len - 1)
        summaries: list[str] = []
        for start in range(0, len(texts), batch_size):
            batch = self.tokenizer(texts[start:start + batch_size], return_tensors="pt", padding=True,
                                   truncation=True, max_length=self.max_input_tokens).to(self.device)
            with torch.inference_mode():
                output = self.model.generate(
                    **batch,  # input_ids and attention_mask, so padding is ignored
                    num_beams=NUM_BEAMS,
                    min_length=min_len,
                    max_length=max_len,
                    length_penalty=2.0,
                    no_repeat_ngram_size=3,
                    early_stopping=True,
                    # Checkpoints saved after training often have use_cache=False,
                    # which makes every decoding step recompute the whole prefix.
                    use_cache=True,
                )
            summaries += [self.tokenizer.decode(ids, skip_special_tokens=True).strip() for ids in output]
            if on_progress:
                on_progress(len(summaries), len(texts))
        return summaries

    def summarize(self, text: str, length: str = DEFAULT_LENGTH, strategy: str = "chunk",
                  on_progress: Progress | None = None) -> Summary:
        """Summarize text of any length.

        strategy="chunk" (default) splits long input; "truncate" cuts it at the
        model's window, as the original app (and the standard CNN/DailyMail
        evaluation) did.
        """
        if strategy not in {"chunk", "truncate"}:
            raise ValueError(f"Unknown strategy: {strategy}")
        text = validate_text(text)
        flat = " ".join(text.split())
        start = time.perf_counter()
        input_tokens = len(self.tokenizer(flat)["input_ids"])

        if input_tokens <= self.max_input_tokens or strategy == "truncate":
            summary = self.generate([flat], length)[0]
            return Summary(summary, input_tokens, truncated=input_tokens > self.max_input_tokens,
                           seconds=time.perf_counter() - start)

        chunks = self.chunk(text)
        logger.info("Input has %d tokens: summarizing %d chunks", input_tokens, len(chunks))
        parts = self.generate(chunks, DEFAULT_LENGTH, on_progress=on_progress)

        # Reduce: if the chunk summaries are still too long, summarize them in
        # chunks again. Stop if a round does not shrink the input.
        pieces = parts
        for _ in range(MAX_REDUCE_ROUNDS):
            combined = " ".join(pieces)
            if self.fits(combined):
                break
            regrouped = self.chunk(combined)
            if len(regrouped) >= len(pieces):
                break
            pieces = self.generate(regrouped, DEFAULT_LENGTH)
        final = self.generate([" ".join(pieces)], length)[0]
        return Summary(final, input_tokens, len(chunks), parts, seconds=time.perf_counter() - start)
