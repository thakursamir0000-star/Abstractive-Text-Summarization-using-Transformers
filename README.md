<div align="center">

# ✨ Abstractive Text Summarization using Transformers

**Summarize articles and long documents with BART, evaluated with ROUGE on CNN/DailyMail, in a Streamlit app.**

[![CI](https://github.com/thakursamir0000-star/Abstractive-Text-Summarization-using-Transformers/actions/workflows/ci.yml/badge.svg)](https://github.com/thakursamir0000-star/Abstractive-Text-Summarization-using-Transformers/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.46%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97-Hugging%20Face%20Space-blue)](https://huggingface.co/spaces/samirthakur345/bart_summarizer_project)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[**Try the Live Demo →**](https://huggingface.co/spaces/samirthakur345/bart_summarizer_project)

</div>

---

## 📌 Overview

**Abstractive** summarization means the model writes new sentences instead of copying the important ones. This project uses [BART](https://arxiv.org/abs/1910.13461) (`facebook/bart-large-cnn`, trained on news), with a smaller and faster [DistilBART](https://huggingface.co/sshleifer/distilbart-cnn-12-6) as an option, and adds what a production summarizer needs around the model:

| | |
|---|---|
| 📏 **Text of any length** | BART reads at most 1,024 tokens, about 700 words. Longer text is split into sentence-aligned, overlapping chunks. Each chunk is summarized, then the summaries are combined, so nothing is silently cut off. |
| 📊 **Measured quality** | ROUGE on the CNN/DailyMail test set with 95% bootstrap confidence intervals, against a lead-3 baseline, plus abstractiveness, a made-up-number check, speed and model size |
| 🖥️ **Streamlit app** | Model choice, summary length, per-part summaries for long text, statistics, download and copy |
| ✅ **Engineering** | Tests (including the app UI) on a tiny random BART, GitHub Actions CI, and a CPU-only Docker image that runs as a non-root user |

---

## 📊 Results

### News articles (CNN/DailyMail test set)

100 randomly sampled test articles (seed 13), scored with ROUGE F1 (with stemming) against the reference highlights. The models read the first 1,024 tokens, the standard protocol, so the numbers compare with published ones. Full per-article results are in [`evaluation/results/`](evaluation/results).

| System | ROUGE-1 | ROUGE-2 (95% CI) | ROUGE-L | Novel bigrams | Numbers found in the article | Words | Seconds / article | Parameters |
|---|---|---|---|---|---|---|---|---|
| Lead-3 (first 3 sentences) | 41.77 | 18.82 (16.5–21.3) | 38.10 | 0% | 100% | 76 | – | – |
| **BART large CNN** (default) | **43.81** | **20.51** (17.8–23.5) | **40.86** | 9.1% | 100% | 64 | 16.2 | 406M |
| DistilBART CNN 12-6 | 43.05 | 20.17 (17.6–22.8) | 40.36 | 10.8% | 100% | 72 | 10.9 | 306M |
| Local fine-tuned BART | 42.73 | 19.04 (16.9–21.3) | 40.00 | 15.1% | 99.6% | 64 | 19.0* | 406M |

Speed is per article on a laptop CPU (Intel i5-1235U, 4 beams). \*Measured in a later session under different load; it has the same architecture as BART large.

What this shows:
- **The evaluation is sound.** BART large CNN scores 43.8 / 20.5 / 40.9 on this sample; its published full-test-set scores are 44.2 / 21.3 / 40.9.
- **BART beats the lead-3 baseline**, which is strong on news because articles put the key facts first: +2.0 ROUGE-1 and +2.8 ROUGE-L, both outside the 95% interval of the paired difference. The ROUGE-2 gain (+1.7) is within noise on 100 articles.
- **DistilBART is the better choice on CPU.** It is within 0.8 points of BART on every metric (no difference is significant) with 25% fewer parameters and is 33% faster.
- **29.2% of CNN/DailyMail test articles are longer than 1,024 tokens** (33 of these 100). The original app silently cut them; the app now splits them (see below).
- **Made-up numbers are rare.** Every number in the BART and DistilBART summaries appears in the article. The fine-tuned model's only miss was "more than 1,000" fans, a figure the article doesn't give.

### The fine-tuned model

`fine_tuned_bart_model/` is `bart-large-cnn` trained for one more epoch on 2,000 CNN/DailyMail training articles (the notebook removed in commit `785ded8`).
- **Training changed it a little:** the weights moved by 1.5% (relative L2 distance), with 99.5% of them slightly different.
- **It didn't get better.** On the same 100 articles it scores −1.1 / −1.5 / −0.9 ROUGE-1/2/L against the base model; every 95% interval includes zero (ROUGE-2: −3.6 to +0.5). It rephrases more (15% novel bigrams against 9%), and it made up the one unsupported number in the table.
- **Why:** the base model was already trained on all 287,000 training articles of this dataset, so one pass over 2,000 of them has little left to teach. A fine-tune pays off on a domain the news model is weak at (see Future work).
- **Its checkpoint was saved with `use_cache: false`**, which made generation several times slower: about 2 minutes per article instead of about 20 seconds. `Summarizer.generate` now always enables the KV cache (with a test), so the output is identical and fast.

The app therefore defaults to `facebook/bart-large-cnn` and keeps the fine-tuned model as a selectable experiment.

### Long documents

To see what is lost when a text is longer than the model's window, three test articles were joined into one document (median 2,594 tokens) and summarized with BART large CNN, using all three sets of highlights as the reference. "Article recall" is the share of each article's highlight words that the summary covers.

| Method (8 documents) | ROUGE-1 | ROUGE-2 | ROUGE-L | Article 1 / 2 / 3 recall | Words | Seconds |
|---|---|---|---|---|---|---|
| Cut at 1,024 tokens (the original app) | 29.20 | 9.58 | 26.81 | 45% / 21% / 15% | 63 | 16 |
| **Split, then combine** (the app's summary) | 35.42 | **17.77** | 33.30 | 39% / 28% / 25% | 59 | 52 |
| Split, all part summaries (shown in the app) | **44.17** | **18.59** | **41.81** | **61% / 51% / 46%** | 204 | 52 |

- **Cutting the text loses its later parts.** The model never sees most of the second and third articles; their recall is close to what common words alone produce.
- **Splitting nearly doubles ROUGE-2 at the same length** (9.6 to 17.8, about 60 words each), with coverage spread across all three articles. It costs about 3× the time, because each part is summarized and then the summaries are summarized again.
- **The combined summary is still short for a multi-topic text**, so the app also shows the summary of every part, which keeps the most detail (46–61% recall) at about 200 words.
- 8 documents is a small sample, so read these numbers as the direction of the effect rather than exact values.

---

## 🏗️ How it works

```
                 ┌──────────────────────────────────────────────────────┐
 input text ───▶ │ fits in 1,024 tokens? ── yes ──▶ one pass of BART     │──▶ summary
                 │        │ no                                           │
                 │        ▼                                              │
                 │ split into sentences (paragraphs, abbreviations)      │
                 │ pack sentences into chunks ≤ 1,021 tokens,            │
                 │ 64 tokens of overlap between neighbours               │
                 │        ▼                                              │
                 │ summarize every chunk ("map") ──────────────────────▶ │──▶ part summaries
                 │        ▼                                              │
                 │ summarize the joined part summaries ("reduce"),       │
                 │ repeated while they are still too long                │──▶ overview
                 └──────────────────────────────────────────────────────┘
```

- **Decoding:** beam search with 4 beams, length penalty 2.0 and no repeated trigrams, the settings `bart-large-cnn` was published with. On a GPU the parts are generated in batches, with an attention mask so padding doesn't change the output (there's a test for it). On a CPU they're generated one at a time: batching was no faster there, and four parts at once needed ~2 GB more memory.
- **Length presets:** Short (20–60 tokens), Standard (56–142, as published) and Detailed (100–220).
- **Code:** [`src/chunking.py`](src/chunking.py) (sentence splitting and token-budget packing, no model needed), [`src/model.py`](src/model.py) (`Summarizer`), [`app.py`](app.py) (UI) and [`evaluation/`](evaluation) (metrics and benchmark).

---

## 🚀 Getting Started

### Option A — Use the hosted demo

**<https://huggingface.co/spaces/samirthakur345/bart_summarizer_project>**

### Option B — Run locally

**Prerequisites:** Python 3.10+.

```bash
git clone https://github.com/thakursamir0000-star/Abstractive-Text-Summarization-using-Transformers.git
cd Abstractive-Text-Summarization-using-Transformers

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

streamlit run app.py
```

The app opens at **http://localhost:8501**. The first run downloads the model (1.6 GB for BART large, 1.2 GB for DistilBART). On a machine without a GPU, `pip install torch --index-url https://download.pytorch.org/whl/cpu` first avoids the large CUDA build.

### Option C — Docker

```bash
docker build -t text-summarizer .
docker run -p 7860:7860 text-summarizer
```

Open **http://localhost:7860**. The image uses CPU-only PyTorch and runs as a non-root user, the way Hugging Face Spaces expects.

---

## 📋 Usage

1. Paste text, or click **Load example**.
2. Pick a model and a summary length in the sidebar.
3. Click **Summarize**. Under the input you can see whether the text fits in one pass or how many parts it will be split into.
4. Long text: open **How this long text was summarized** to see the summary of every part.
5. **Download** the summary, or open **Copy as plain text**.

---

## 🔬 Reproducing the evaluation

```bash
pip install -r requirements-dev.txt
python -m evaluation.benchmark --n 100 --digests 8    # what the tables above used
python -m evaluation.benchmark --n 20 --systems lead-3 distilbart-cnn-12-6   # quick look
python -m evaluation.benchmark --table                # print the tables from saved results
```

Per-article predictions and scores are saved in [`evaluation/results/`](evaluation/results), so every number above can be checked against the summaries that produced it.

---

## ⚙️ Configuration

Environment variables or a `.env` file (see [`.env.example`](.env.example)):

| Variable | Default | Description |
|---|---|---|
| `MODEL_PATH` | `facebook/bart-large-cnn` | Default model: a Hugging Face Hub id or a local folder |
| `MAX_INPUT_TOKENS` | `1024` | Longest input read in one pass (capped by the model's own limit) |
| `CHUNK_OVERLAP_TOKENS` | `64` | Overlap between neighbouring chunks of long text |
| `NUM_BEAMS` | `4` | Beam-search width |
| `LOG_LEVEL` | `INFO` | Python log level |

---

## 📁 Project Structure

```
├── app.py                    # Streamlit app
├── src/
│   ├── config.py             # Settings, model choices, length presets
│   ├── chunking.py           # Sentence splitting and token-budget chunking
│   ├── model.py              # Summarizer: one pass or map-reduce for long text
│   └── utils.py              # Reading time, safe HTML for model output
├── evaluation/
│   ├── metrics.py            # ROUGE, lead-3, novel n-grams, number check, bootstrap
│   ├── benchmark.py          # CNN/DailyMail and long-document experiments
│   └── results/              # Saved predictions, scores and report.json
├── tests/                    # pytest suite (tiny random BART, Streamlit AppTest)
├── Dockerfile                # CPU-only, non-root image for HF Spaces / self-hosting
├── upload_model_to_hub.py    # Push a local model folder to the Hugging Face Hub
├── requirements.txt          # App runtime
├── requirements-dev.txt      # + evaluation, tests, lint
└── .github/workflows/ci.yml  # Lint, tests on Python 3.11 / 3.12, Docker build + health check
```

---

## 🧪 Testing

```bash
pip install -r requirements-dev.txt
ruff check .
pytest                 # about 1–2 minutes; downloads a 0.3 MB random BART once
pytest -m "not model"  # only the tests that need no model
```

The tests cover sentence splitting and chunk packing (budget, overlap and order, sentences longer than the budget), the metrics, input validation, long text being split instead of truncated, every chunk fitting the model's window, padding not changing batched output, every length preset, and the app itself: summarizing, the summary surviving reruns, the copy and download options, Clear, rejecting short input and flagging a summary when the input changes.

The tests use `hf-internal-testing/tiny-random-bart`, whose window is only 100 tokens, so ordinary test text has to go through the long-document path.

---

## ⚠️ Limitations

- **News-trained.** Both models were trained on CNN/DailyMail, so they summarize news-like text best. On dialogue, code or very technical text, quality drops.
- **ROUGE measures word overlap, not truth.** The number check catches made-up numbers, but not other kinds of unsupported claims.
- **CPU speed.** On a laptop CPU a news article takes several seconds and long documents about a minute (see the tables). A GPU is many times faster.
- **Evaluation size.** 100 test articles and 8 long documents. The confidence intervals show how much the news numbers could move on the full test set; the long-document results are indicative.

### Future work

- **Fine-tune for a new domain** where the news model is weak, such as meeting or chat summaries (DialogSum, SAMSum), with LoRA, and report ROUGE before and after.
- **Faithfulness metrics** such as SummaC or QAFactEval, plus a small human evaluation.

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 License

[MIT](LICENSE)

---

<div align="center">

[Live Demo](https://huggingface.co/spaces/samirthakur345/bart_summarizer_project) · [Report Bug](https://github.com/thakursamir0000-star/Abstractive-Text-Summarization-using-Transformers/issues) · [Request Feature](https://github.com/thakursamir0000-star/Abstractive-Text-Summarization-using-Transformers/issues)

</div>
