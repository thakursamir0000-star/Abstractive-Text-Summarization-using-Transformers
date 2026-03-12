import streamlit as st
from model import summarize

st.title("Text Summarization using BART")

text = st.text_area("Enter text to summarize")

if st.button("Summarize"):
    summary = summarize(text)
    st.subheader("Summary")
    st.write(summary)
