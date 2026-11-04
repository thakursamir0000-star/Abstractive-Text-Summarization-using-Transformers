import os

# A 0.3 MB random BART with a 100-token window: fast, and small enough that
# ordinary test text has to be split into several chunks. Set before any
# src import so the app and config pick it up too.
TINY_MODEL = "hf-internal-testing/tiny-random-bart"
os.environ["MODEL_PATH"] = TINY_MODEL

import pytest  # noqa: E402


@pytest.fixture(scope="session")
def tiny():
    from src.model import Summarizer

    return Summarizer(TINY_MODEL)


@pytest.fixture
def long_text():
    return "\n\n".join(
        f"Paragraph {p} starts here. It talks about topic number {p} in some detail. "
        f"The council said the plan for area {p} would cost {p}.5 million. Critics disagreed."
        for p in range(1, 9)
    )
