"""Streamlit app: summarize text of any length with BART."""

import hashlib
import math
from pathlib import Path

import streamlit as st

from src.config import (
    APP_TITLE,
    DEFAULT_LENGTH,
    LENGTH_PRESETS,
    MAX_TEXT_CHARS,
    MIN_TEXT_CHARS,
    MODEL_CHOICES,
    MODEL_PATH,
    REPO_URL,
    get_logger,
)
from src.model import Summarizer, validate_text
from src.utils import format_duration, html_text, reading_seconds, word_count

st.set_page_config(page_title=APP_TITLE, page_icon="✨", layout="wide", initial_sidebar_state="expanded")
logger = get_logger(__name__)

EXAMPLE = (
    "The city council of Riverton voted on Tuesday to expand its bike-sharing scheme from 40 to "
    "120 stations over the next two years, after a pilot that ran through the summer drew more "
    "riders than planners had expected.\n\n"
    "During the six-month pilot, residents and visitors made about 210,000 trips, roughly double "
    "the council's target. Most journeys were short: the median ride lasted 11 minutes, and almost "
    "a third started or ended at one of the four stations next to the central railway station. "
    "Council officers said the figures suggested that many people were using the bikes to cover "
    "the last stretch between the train and their office.\n\n"
    "The expansion will cost an estimated 3.2 million, of which 1.9 million will come from a "
    "national grant for low-carbon transport. The rest will be paid from parking revenue. New "
    "stations will be placed first in the northern districts, which had no stations during the "
    "pilot and where bus services are the least frequent.\n\n"
    "Not everyone supports the plan. Some shop owners on the high street said the stations took "
    "up space that had been used for deliveries, and two councillors voted against the expansion, "
    "arguing that the money should go to repairing roads. The council said it would move three "
    "stations away from loading bays and review the scheme again after its first full year."
)


@st.cache_resource(show_spinner=False)
def load_summarizer(model_path: str) -> Summarizer:
    return Summarizer(model_path)


def text_key(text: str) -> str:
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()


def clear() -> None:
    st.session_state["input_text"] = ""
    st.session_state.pop("result", None)


def load_example() -> None:
    st.session_state["input_text"] = EXAMPLE
    st.session_state.pop("result", None)


st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; padding: 32px 20px; border-radius: 15px; text-align: center;
        margin-bottom: 24px; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    .main-header h1 { font-size: 2.3em; margin: 0; font-weight: 700; color: white; }
    .main-header p { font-size: 1.05em; margin: 8px 0 0 0; opacity: 0.9; }
    .section-header {
        font-size: 1.5em; font-weight: 600; color: #667eea; margin: 10px 0 12px 0;
        padding-bottom: 8px; border-bottom: 3px solid #667eea;
    }
    .summary-box {
        background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%); color: #1f2937;
        border-left: 5px solid #10b981; padding: 18px 20px; border-radius: 10px; margin: 12px 0;
        line-height: 1.6;
    }
    .summary-box h4 { color: #059669; margin-top: 0; }
    .footer {
        text-align: center; padding: 24px 20px; color: #6b7280; border-top: 2px solid #e5e7eb;
        margin-top: 40px; font-size: 0.95em;
    }
    .footer a { color: #667eea; text-decoration: none; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="main-header">
        <h1>✨ Text Summarizer</h1>
        <p>Abstractive summaries of articles, reports and long documents with BART</p>
    </div>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR - SETTINGS & MODEL STATUS
# ============================================
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    labels = list(MODEL_CHOICES)
    default_label = next(label for label, path in MODEL_CHOICES.items() if path == MODEL_PATH)
    model_label = st.selectbox(
        "Model", labels, index=labels.index(default_label),
        help="BART large CNN scores best; DistilBART is about half the size and faster on CPU. "
             "See the evaluation in the README.",
    )
    length = st.radio(
        "Summary length", list(LENGTH_PRESETS), index=list(LENGTH_PRESETS).index(DEFAULT_LENGTH),
        horizontal=True,
        help="Short: 20–60 tokens · Standard: 56–142 (the setting BART was evaluated with) · "
             "Detailed: 100–220.",
    )
    show_stats = st.checkbox("Show statistics", value=True)

    st.markdown("---")
    st.markdown("### 📊 Model")
    summarizer = None
    try:
        with st.spinner("Loading the model (the first run downloads 1–1.6 GB)..."):
            summarizer = load_summarizer(MODEL_CHOICES[model_label])
        st.success("Model ready", icon="✅")
        st.caption(
            f"`{summarizer.model_path}` · {summarizer.num_parameters / 1e6:.0f}M parameters · "
            f"{summarizer.device.upper()}  \nReads {summarizer.max_input_tokens:,} tokens at a time; "
            "longer text is split into parts."
        )
    except Exception as e:  # noqa: BLE001 - show any load failure in the UI
        logger.exception("Model failed to load")
        st.error(f"Could not load the model: {str(e)[:200]}", icon="❌")
        if st.button("🔁 Retry", width="stretch"):
            load_summarizer.clear()
            st.rerun()

    st.markdown("---")
    st.markdown("### 💡 How it works")
    st.caption(
        "The model writes new sentences rather than copying them (abstractive summarization). "
        "It reads about 1,024 tokens (roughly 700 words) at once, so longer text is split at "
        "sentence boundaries, each part is summarized, and the part summaries are combined into "
        "one. It was trained on news, so it works best on articles and reports."
    )

# ============================================
# MAIN CONTENT
# ============================================
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<h3 class="section-header">📝 Input Text</h3>', unsafe_allow_html=True)
    text_input = st.text_area(
        "Text to summarize",
        height=350,
        max_chars=MAX_TEXT_CHARS,
        placeholder=f"Paste the text you want to summarize (at least {MIN_TEXT_CHARS} characters)...",
        label_visibility="collapsed",
        key="input_text",
    )
    button_cols = st.columns(2)
    button_cols[0].button("📄 Load example", on_click=load_example, width="stretch")
    button_cols[1].button("🔄 Clear", on_click=clear, width="stretch")

    if text_input.strip():
        details = f"📊 {len(text_input):,} characters · {word_count(text_input):,} words"
        if summarizer is not None:
            tokens = len(summarizer.tokenizer(" ".join(text_input.split()))["input_ids"])
            if tokens <= summarizer.max_input_tokens:
                details += f" · {tokens:,} tokens (fits in one pass)"
            else:
                parts = math.ceil(tokens / (summarizer.max_input_tokens - 64))
                details += f" · {tokens:,} tokens (will be split into about {parts} parts)"
        st.caption(details)

with col2:
    st.markdown('<h3 class="section-header">✨ Summary</h3>', unsafe_allow_html=True)
    summarize_clicked = st.button(
        "🚀 Summarize", type="primary", width="stretch", disabled=summarizer is None,
    )

    if summarize_clicked:
        try:
            validate_text(text_input)
        except ValueError as e:
            st.error(str(e), icon="❌")
        else:
            progress = st.progress(0.0, text="Summarizing...")

            def on_progress(done: int, total: int) -> None:
                progress.progress(done / total, text=f"Summarized part {done} of {total}")

            try:
                with st.spinner("Summarizing..."):
                    result = summarizer.summarize(text_input, length=length, on_progress=on_progress)
            except (RuntimeError, ValueError) as e:
                logger.exception("Summarization failed")
                st.error(f"Summarization failed: {str(e)[:300]}", icon="❌")
            else:
                st.session_state["result"] = {
                    "summary": result.text,
                    "parts": result.parts,
                    "chunks": result.chunks,
                    "input_tokens": result.input_tokens,
                    "seconds": result.seconds,
                    "source_words": word_count(text_input),
                    "source_seconds": reading_seconds(text_input),
                    "source_chars": len(text_input),
                    "source_key": text_key(text_input),
                    "model": summarizer.model_path,
                    "length": length,
                }
            finally:
                progress.empty()

    # Rendered from session state, so the summary, download and copy survive reruns.
    result = st.session_state.get("result")
    if result:
        if result["source_key"] != text_key(text_input):
            st.caption("⚠️ The input has changed since this summary was made.")
        st.markdown(
            f'<div class="summary-box"><h4>✅ Summary</h4>{html_text(result["summary"])}</div>',
            unsafe_allow_html=True,
        )

        if result["parts"]:
            with st.expander(f"How this long text was summarized: {result['chunks']} parts"):
                st.caption(
                    f"The input had {result['input_tokens']:,} tokens, more than the model reads at "
                    "once. Each part was summarized, then the part summaries were summarized again."
                )
                for i, part in enumerate(result["parts"], 1):
                    st.markdown(f"**Part {i}.** {html_text(part)}", unsafe_allow_html=True)

        if show_stats:
            summary_words = word_count(result["summary"])
            stat_cols = st.columns(4)
            stat_cols[0].metric("📖 Original", f"{result['source_words']:,} words",
                                f"{format_duration(result['source_seconds'])} read",
                                delta_color="off")
            stat_cols[1].metric("✂️ Summary", f"{summary_words:,} words",
                                f"{format_duration(reading_seconds(result['summary']))} read",
                                delta_color="off")
            reduction = (1 - summary_words / max(result["source_words"], 1)) * 100
            stat_cols[2].metric("📉 Shorter by", f"{reduction:.0f}%")
            stat_cols[3].metric("⏱️ Took", format_duration(result["seconds"]))

        st.download_button(
            "💾 Download summary", data=result["summary"], file_name="summary.txt",
            mime="text/plain", width="stretch",
        )
        with st.expander("📋 Copy as plain text"):
            st.code(result["summary"], language=None, wrap_lines=True)
    elif not summarize_clicked:
        st.info("Paste some text, or load the example, then click **Summarize**.")

# ============================================
# FOOTER
# ============================================
model_path = MODEL_CHOICES[model_label]
model_link = "" if Path(model_path).exists() else f'<a href="https://huggingface.co/{model_path}">Model card</a> • '
st.markdown(f"""
    <div class="footer">
        <p>✨ <strong>Text Summarizer</strong> · BART (Lewis et al., 2019)</p>
        <p>{model_link}<a href="{REPO_URL}">GitHub</a> • <a href="https://streamlit.io">Built with Streamlit</a></p>
    </div>
""", unsafe_allow_html=True)
