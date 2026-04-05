"""Streamlit web app for text summarization - Enhanced UI."""

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

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================
# CUSTOM CSS - ENHANCED DESIGN
# ============================================
st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary: #6366f1;
        --secondary: #8b5cf6;
        --success: #10b981;
        --danger: #ef4444;
        --warning: #f59e0b;
        --info: #3b82f6;
    }
    
    /* Overall styling */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Header styles */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 40px 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    .main-header h1 {
        font-size: 2.5em;
        margin: 0;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .main-header p {
        font-size: 1.1em;
        margin: 10px 0 0 0;
        opacity: 0.9;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.8em;
        font-weight: 600;
        color: #667eea;
        margin: 20px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 3px solid #667eea;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #f0f4ff 0%, #f9fafb 100%);
        border-left: 5px solid #667eea;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.1);
    }
    
    /* Success box */
    .success-box {
        background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
        border-left: 5px solid #10b981;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        box-shadow: 0 2px 10px rgba(16, 185, 129, 0.1);
    }
    
    .success-box h3 {
        color: #10b981;
        margin-top: 0;
    }
    
    /* Error box */
    .error-box {
        background: linear-gradient(135deg, #fef2f2 0%, #fdf2f2 100%);
        border-left: 5px solid #ef4444;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        box-shadow: 0 2px 10px rgba(239, 68, 68, 0.1);
    }
    
    .error-box h3 {
        color: #ef4444;
        margin-top: 0;
    }
    
    /* Stats grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stat-card .label {
        font-size: 0.9em;
        opacity: 0.9;
        margin-bottom: 8px;
    }
    
    .stat-card .value {
        font-size: 1.8em;
        font-weight: 700;
    }
    
    /* Input/Output container */
    .container {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        margin: 15px 0;
    }
    
    /* Button styling - already handled by Streamlit */
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 30px 20px;
        color: #6b7280;
        border-top: 2px solid #e5e7eb;
        margin-top: 50px;
        font-size: 0.95em;
    }
    
    .footer a {
        color: #667eea;
        text-decoration: none;
        font-weight: 600;
    }
    
    .footer a:hover {
        text-decoration: underline;
    }
    
    /* Loading animation */
    .spinner {
        display: inline-block;
        margin-right: 5px;
    }
    
    /* Background pattern */
    .hero-section {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# HEADER SECTION
# ============================================
st.markdown("""
    <div class="main-header">
        <h1>✨ Text Summarizer Pro</h1>
        <p>Powered by advanced BART AI Model</p>
    </div>
""", unsafe_allow_html=True)

# Hero section with description
st.markdown("""
    <div class="hero-section">
        <h3>🚀 Transform Your Text in Seconds</h3>
        <p>Paste any text and let our AI create a concise, meaningful summary. Perfect for articles, reports, and long documents!</p>
    </div>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR - INFORMATION & SETTINGS
# ============================================
with st.sidebar:
    st.markdown("### 📚 About This App")
    st.info("""
    **Text Summarizer Pro** uses state-of-the-art BART (Bidirectional and Auto-Regressive Transformers) 
    model to generate accurate, concise summaries of your text.
    
    ✨ **Key Features:**
    - Abstractive summarization (generates new text)
    - Handles up to 100,000 characters
    - GPU-accelerated processing
    - Smart compression ratios
    """)
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    
    show_stats = st.checkbox("Show detailed statistics", value=True)
    show_tips = st.checkbox("Show tips & tricks", value=True)
    
    st.markdown("---")
    st.markdown("### 📊 Model Status")
    
    try:
        with st.spinner("Loading model..."):
            model = get_model()
        st.success("✅ Model Ready", icon="✅")
        st.caption("BART Large CNN - Ready to summarize")
    except Exception as e:
        st.error(f"❌ Model Error: {str(e)}", icon="❌")
    
    st.markdown("---")
    st.markdown("### 💡 Tips")
    if show_tips:
        st.caption("""
        • Use clear, well-structured text
        • Minimum 50 characters required
        • Longer documents = better summaries
        • Works best with articles and reports
        """)

# ============================================
# MAIN CONTENT AREA
# ============================================

# Input and Output sections
col1, col2 = st.columns([1, 1], gap="large")

# ============================================
# LEFT COLUMN - INPUT
# ============================================
with col1:
    st.markdown('<h3 class="section-header">📝 Input Text</h3>', unsafe_allow_html=True)
    
    st.markdown('<div class="container">', unsafe_allow_html=True)
    
    text_input = st.text_area(
        "Paste your text here:",
        height=350,
        placeholder="📄 Enter the text you want to summarize... (minimum 50 characters)",
        label_visibility="collapsed",
    )
    
    if text_input.strip():
        char_count = len(text_input)
        st.caption(f"📊 Characters: {char_count:,} | Words: {len(text_input.split()):,}")
        
        # Progress bar for text length
        max_chars = 100000
        progress = min(char_count / max_chars, 1.0)
        st.progress(progress)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# RIGHT COLUMN - OUTPUT & CONTROLS
# ============================================
with col2:
    st.markdown('<h3 class="section-header">✨ Summary</h3>', unsafe_allow_html=True)
    
    st.markdown('<div class="container">', unsafe_allow_html=True)
    
    # Summarize button
    col_btn1, col_btn2 = st.columns([2, 1])
    
    with col_btn1:
        summarize_btn = st.button(
            "🚀 Summarize Text",
            use_container_width=True,
            type="primary",
            help="Click to generate summary"
        )
    
    with col_btn2:
        clear_btn = st.button(
            "🔄 Clear",
            use_container_width=True,
            help="Clear all text"
        )
    
    if clear_btn:
        text_input = ""
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# SUMMARIZATION LOGIC
# ============================================

def validate_and_summarize(text: str) -> tuple[bool, str]:
    """Validate and summarize text."""
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

# Process input
if summarize_btn:
    if not text_input.strip():
        st.error("❌ Please enter some text to summarize.", icon="❌")
    else:
        with st.spinner("🔄 Processing your text..."):
            success, result = validate_and_summarize(text_input)

            if success:
                # Success message
                st.markdown(f"""
                    <div class="success-box">
                        <h3>✅ Summary Generated!</h3>
                        <p>{result}</p>
                    </div>
                """, unsafe_allow_html=True)

                # Statistics
                if show_stats:
                    st.markdown("---")
                    st.markdown("<h4>📊 Summary Statistics</h4>", unsafe_allow_html=True)
                    
                    original_length = len(text_input)
                    summary_length = len(result)
                    compression = (summary_length / original_length * 100)
                    original_time = estimate_reading_time(text_input)
                    summary_time = estimate_reading_time(result)
                    time_saved = original_time - summary_time

                    # Stats grid
                    stat_cols = st.columns(3)
                    
                    with stat_cols[0]:
                        st.metric(
                            "📖 Original",
                            f"{original_length:,} chars",
                            f"~{original_time} min read"
                        )
                    
                    with stat_cols[1]:
                        st.metric(
                            "✂️ Summary",
                            f"{summary_length:,} chars",
                            f"~{summary_time} min read"
                        )
                    
                    with stat_cols[2]:
                        st.metric(
                            "📉 Compressed",
                            f"{compression:.1f}%",
                            f"Save ~{time_saved} min"
                        )

                    # Download button
                    st.markdown("---")
                    col_download, col_copy = st.columns(2)
                    
                    with col_download:
                        st.download_button(
                            label="💾 Download Summary",
                            data=result,
                            file_name="summary.txt",
                            mime="text/plain",
                            use_container_width=True,
                        )
                    
                    with col_copy:
                        if st.button("📋 Copy to Clipboard", use_container_width=True):
                            st.success("Copied! (Use Ctrl+V to paste)")

            else:
                # Error message
                st.markdown(f"""
                    <div class="error-box">
                        <h3>❌ Error Occurred</h3>
                        <p>{result}</p>
                    </div>
                """, unsafe_allow_html=True)

# ============================================
# CHARACTER COUNT INFO
# ============================================
if text_input.strip():
    chars = len(text_input)
    is_valid_length = 50 <= chars <= 100000
    status_emoji = "✅" if is_valid_length else "⚠️"
    st.markdown(f"""
        <div class="info-box">
            {status_emoji} <strong>Text Status:</strong> {chars:,} characters
            {' (Ready to summarize!)' if is_valid_length else ' (Needs 50-100,000 characters)'}
        </div>
    """, unsafe_allow_html=True)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
    <div class="footer">
        <p>🚀 <strong>Text Summarizer Pro</strong> | Powered by BART AI</p>
        <p>
            <a href="https://huggingface.co/facebook/bart-large-cnn">Model Info</a> • 
            <a href="https://github.com">GitHub</a> • 
            <a href="https://streamlit.io">Built with Streamlit</a>
        </p>
        <p style="opacity: 0.7;">Made with ❤️ for better reading</p>
    </div>
""", unsafe_allow_html=True)
