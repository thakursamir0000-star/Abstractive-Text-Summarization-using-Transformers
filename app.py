"""Streamlit web app for text summarization."""

import sys
import logging
import streamlit as st
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.model import summarize, get_model
    from src.config import (
        APP_TITLE,
        MIN_TEXT_LENGTH,
        MAX_TEXT_LENGTH,
        get_logger,
    )
    from src.utils import estimate_reading_time, truncate_text
except ImportError as e:
    st.error(f"❌ Failed to load modules: {str(e)}")
    st.stop()

logger = get_logger(__name__)

# Streamlit page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main-header {
        color: #1f77b4;
        text-align: center;
        margin-bottom: 30px;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Main title
st.markdown(f"<h1 class='main-header'>{APP_TITLE}</h1>", unsafe_allow_html=True)

# Sidebar information
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown(
        """
        This app uses a fine-tuned **BART** model for abstractive text summarization.
        
        **Features:**
        - Abstractive summarization (generates new text, not just extracts)
        - Works with documents up to 100,000 characters
        - GPU acceleration when available
        
        **Tips:**
        - Use clear, well-written text
        - Minimum 50 characters required
        - Longer documents produce better summaries
        """
    )
    
    st.divider()
    st.subheader("📊 Model Info")
    try:
        model = get_model()
        st.success("✅ Model loaded successfully")
    except Exception as e:
        st.error(f"❌ Model loading failed: {str(e)}")


def validate_and_summarize(text: str) -> tuple[bool, str]:
    """
    Validate and summarize text.

    Returns:
        Tuple of (success, result_text)
    """
    try:
        summary = summarize(text)
        return True, summary
    except ValueError as e:
        return False, f"Input Error: {str(e)}"
    except RuntimeError as e:
        return False, f"Summarization Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False, "An unexpected error occurred. Please try again."


# Main interface
col1, col2 = st.columns([1, 1], gap="medium")

with col1:
    st.subheader("📝 Input Text")
    text_input = st.text_area(
        "Enter text to summarize:",
        height=300,
        placeholder="Paste your text here...",
        label_visibility="collapsed",
    )

with col2:
    st.subheader("✨ Summary")
    if st.button("🚀 Summarize", use_container_width=True, type="primary"):
        if not text_input.strip():
            st.error("❌ Please enter some text to summarize.")
        else:
            with st.spinner("Generating summary..."):
                success, result = validate_and_summarize(text_input)

                if success:
                    st.markdown(
                        f"""
                        <div class='success-box'>
                        {result}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Stats
                    col_a, col_b, col_c = st.columns(3)
                    original_time = estimate_reading_time(text_input)
                    summary_time = estimate_reading_time(result)
                    compression = (
                        len(result) / len(text_input) * 100
                    )

                    with col_a:
                        st.metric("Original Length", f"{len(text_input)} chars")
                    with col_b:
                        st.metric("Summary Length", f"{len(result)} chars")
                    with col_c:
                        st.metric("Compression Ratio", f"{compression:.1f}%")

                    col_x, col_y = st.columns(2)
                    with col_x:
                        st.metric("Original Read Time", f"~{original_time} min")
                    with col_y:
                        st.metric("Summary Read Time", f"~{summary_time} min")

                    # Download button
                    st.download_button(
                        label="📥 Download Summary",
                        data=result,
                        file_name="summary.txt",
                        mime="text/plain",
                    )
                else:
                    st.markdown(
                        f"""
                        <div class='error-box'>
                        {result}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # Display placeholder summary in sidebar
    if text_input.strip():
        st.info(f"📊 Text contains {len(text_input)} characters")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px; margin-top: 50px;'>
    <p>Built with ❤️ using Streamlit • BART Model • PyTorch</p>
    <p><a href='https://github.com' style='color: gray;'>GitHub Repository</a></p>
    </div>
    """,
    unsafe_allow_html=True,
)
