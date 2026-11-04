"""Small helpers for the summarization app."""

import html

WORDS_PER_MINUTE = 230  # typical adult silent-reading speed


def word_count(text: str) -> int:
    return len(text.split())


def reading_seconds(text: str) -> float:
    return word_count(text) / WORDS_PER_MINUTE * 60


def format_duration(seconds: float) -> str:
    """'45 s', '3.5 min' — honest at both ends instead of rounding to whole minutes."""
    if seconds < 60:
        return f"{max(1, round(seconds))} s"
    return f"{seconds / 60:.1f} min"


def html_text(text: str) -> str:
    """Escape model output for st.markdown(unsafe_allow_html=True).

    Escapes HTML, and dollar signs too, which Streamlit would otherwise render
    as LaTeX ("$5 million and $3 billion").
    """
    return html.escape(text).replace("$", "&#36;").replace("\n", "<br>")
