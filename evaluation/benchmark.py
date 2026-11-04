"""Evaluate summarizers on CNN/DailyMail news and on long multi-article documents.

    python -m evaluation.benchmark                    # full run (about an hour on a laptop CPU)
    python -m evaluation.benchmark --n 20 --systems lead-3 distilbart-cnn-12-6
    python -m evaluation.benchmark --long-only        # only the long-document experiment
    python -m evaluation.benchmark --table            # print the README tables from saved results

1. News: a fixed random sample of the CNN/DailyMail 3.0.0 test set, scored
   with ROUGE against the reference highlights. Models read the first 1,024
   tokens, the standard protocol, so the numbers compare with published ones.
2. Long documents: three test articles joined into one ~2,500-token text,
   with all three sets of highlights as the reference. This shows what is lost
   when a long text is cut at 1,024 tokens versus split into chunks.

Results (per-item predictions and aggregates) are written to evaluation/results/.
"""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from huggingface_hub import hf_hub_download

from evaluation.metrics import (
    ROUGE_TYPES,
    bootstrap_ci,
    lead,
    novel_ngram_share,
    numbers_supported,
    paired_difference,
    rouge,
    rouge1_recall,
)
from src.config import BASE_MODEL, FAST_MODEL, LOCAL_MODEL_DIR
from src.model import Summarizer

RESULTS_DIR = Path(__file__).resolve().parent / "results"
SYSTEMS = {
    "lead-3": None,
    "bart-large-cnn": BASE_MODEL,
    "distilbart-cnn-12-6": FAST_MODEL,
    "local-fine-tuned": str(LOCAL_MODEL_DIR),
}
REFERENCE_SYSTEM = "bart-large-cnn"
SEED = 13


def load_cnn_dm_test() -> pd.DataFrame:
    path = hf_hub_download("abisee/cnn_dailymail", "3.0.0/test-00000-of-00001.parquet",
                           repo_type="dataset")
    return pd.read_parquet(path)


def sample(frame: pd.DataFrame, n: int, seed: int, exclude: set[int] = frozenset()) -> list[dict]:
    candidates = np.array([i for i in range(len(frame)) if i not in exclude])
    picked = np.sort(np.random.default_rng(seed).choice(candidates, n, replace=False))
    return [{"index": int(i), "id": frame.at[i, "id"], "article": frame.at[i, "article"],
             "highlights": frame.at[i, "highlights"]} for i in picked]


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _model_info(summarizer: Summarizer, load_seconds: float) -> dict:
    params = summarizer.num_parameters
    return {"model": summarizer.model_path, "parameters_m": round(params / 1e6, 1),
            "fp32_size_gb": round(params * 4 / 1e9, 2), "load_seconds": round(load_seconds, 1)}


# ---------------------------------------------------------------- news (CNN/DM)

def score_news(system: str, item: dict, summary: str, seconds: float, extra: dict) -> dict:
    return {
        "id": item["id"], "system": system, "summary": summary,
        **{k: round(v, 3) for k, v in rouge(summary, item["highlights"]).items()},
        "novel_bigrams": round(novel_ngram_share(summary, item["article"]), 2),
        "numbers_supported": numbers_supported(summary, item["article"]),
        "words": len(summary.split()), "seconds": round(seconds, 3), **extra,
    }


def run_news(system: str, items: list[dict], out_dir: Path) -> dict:
    info: dict = {}
    rows = []
    if SYSTEMS[system] is None:
        for item in items:
            start = time.perf_counter()
            summary = lead(item["article"], 3)
            rows.append(score_news(system, item, summary, time.perf_counter() - start, {}))
    else:
        start = time.perf_counter()
        summarizer = Summarizer(SYSTEMS[system])
        info = _model_info(summarizer, time.perf_counter() - start)
        for k, item in enumerate(items, 1):
            result = summarizer.summarize(item["article"], strategy="truncate")
            rows.append(score_news(system, item, result.text, result.seconds,
                                   {"input_tokens": result.input_tokens, "truncated": result.truncated}))
            if k % 10 == 0 or k == len(items):
                mean_r2 = statistics.mean(r["rouge2"] for r in rows)
                print(f"  {system}: {k}/{len(items)}  ROUGE-2 so far {mean_r2:.2f}", flush=True)
        del summarizer
    _write_jsonl(out_dir / "news" / f"{system}.jsonl", rows)
    (out_dir / "news" / f"{system}.info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    return info


def summarize_news(out_dir: Path) -> dict:
    """Aggregate every system's saved predictions (only items all systems share)."""
    files = {p.stem: p for p in (out_dir / "news").glob("*.jsonl")}
    per_system = {name: _read_jsonl(files[name]) for name in SYSTEMS if name in files}
    if not per_system:
        return {}
    shared = set.intersection(*({r["id"] for r in rows} for rows in per_system.values()))
    report = {}
    for system, rows in per_system.items():
        rows = sorted((r for r in rows if r["id"] in shared), key=lambda r: r["id"])
        info_file = out_dir / "news" / f"{system}.info.json"
        info = json.loads(info_file.read_text(encoding="utf-8")) if info_file.exists() else {}
        numbers = [r["numbers_supported"] for r in rows if r["numbers_supported"] is not None]
        entry = {"n": len(rows), **info}
        for metric in ROUGE_TYPES:
            values = [r[metric] for r in rows]
            low, high = bootstrap_ci(values)
            entry[metric] = {"mean": round(statistics.mean(values), 2), "ci_low": round(low, 2),
                             "ci_high": round(high, 2)}
        entry["novel_bigrams_pct"] = round(statistics.mean(r["novel_bigrams"] for r in rows), 1)
        entry["numbers_supported_pct"] = round(statistics.mean(numbers), 1) if numbers else None
        entry["words_mean"] = round(statistics.mean(r["words"] for r in rows), 1)
        entry["seconds_median"] = round(statistics.median(r["seconds"] for r in rows), 3)
        if "truncated" in rows[0]:
            entry["truncated_pct"] = round(100 * statistics.mean(r["truncated"] for r in rows), 1)
        report[system] = entry

    if REFERENCE_SYSTEM in per_system:
        ref = sorted((r for r in per_system[REFERENCE_SYSTEM] if r["id"] in shared), key=lambda r: r["id"])
        for system, rows in per_system.items():
            if system == REFERENCE_SYSTEM:
                continue
            rows = sorted((r for r in rows if r["id"] in shared), key=lambda r: r["id"])
            report[system][f"vs_{REFERENCE_SYSTEM}"] = {
                metric: {k: round(v, 2) for k, v in
                         paired_difference([r[metric] for r in ref], [r[metric] for r in rows]).items()}
                for metric in ROUGE_TYPES
            }
    return report


def length_stats(frame: pd.DataFrame, limit: int = 1024) -> dict:
    """How many test articles are longer than the model's window."""
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    lengths = np.array([len(ids) for ids in tokenizer(list(frame["article"]))["input_ids"]])
    return {"articles": int(len(lengths)), "median_tokens": int(np.median(lengths)),
            "p90_tokens": int(np.percentile(lengths, 90)),
            f"longer_than_{limit}_pct": round(float((lengths > limit).mean() * 100), 1)}


def weight_change(base: str, other: str) -> dict:
    """How far a fine-tuned checkpoint moved from the model it started from.

    Reads both safetensors files one tensor at a time: loading two full
    BART-large models side by side needs ~3.3 GB and ran a 16 GB laptop out
    of memory mid-benchmark.
    """
    from safetensors import safe_open

    def weights_file(model: str) -> str:
        local = Path(model) / "model.safetensors"
        return str(local) if local.exists() else hf_hub_download(model, "model.safetensors")

    diff_sq = base_sq = 0.0
    changed = total = compared = 0
    with safe_open(weights_file(base), "pt") as a, safe_open(weights_file(other), "pt") as b:
        for name in sorted(set(a.keys()) & set(b.keys())):
            x, y = a.get_tensor(name).float(), b.get_tensor(name).float()
            if x.shape != y.shape:
                continue
            delta = y - x
            diff_sq += float(delta.pow(2).sum())
            base_sq += float(x.pow(2).sum())
            changed += int((delta.abs() > 1e-6).sum())
            total += x.numel()
            compared += 1
    return {"relative_l2_change_pct": round(100 * (diff_sq / base_sq) ** 0.5, 3),
            "weights_changed_pct": round(100 * changed / total, 1), "tensors_compared": compared}


# ---------------------------------------------------------- long documents

def make_digests(items: list[dict], size: int = 3) -> list[dict]:
    digests = []
    for k in range(0, len(items) - size + 1, size):
        group = items[k:k + size]
        digests.append({
            "id": "+".join(g["id"][:8] for g in group),
            "text": "\n\n".join(g["article"] for g in group),
            "highlights": [g["highlights"] for g in group],
        })
    return digests


def score_long(method: str, digest: dict, summary: str, seconds: float, chunks: int) -> dict:
    reference = "\n".join(digest["highlights"])
    return {
        "id": digest["id"], "method": method, "summary": summary,
        **{k: round(v, 3) for k, v in rouge(summary, reference).items()},
        # How much of each article's key points the summary covers.
        "article_recall": [round(rouge1_recall(summary, h), 2) for h in digest["highlights"]],
        "words": len(summary.split()), "seconds": round(seconds, 2), "chunks": chunks,
    }


def run_long(digests: list[dict], model: str, out_dir: Path) -> None:
    # Saved after every document, and documents already in the file are
    # skipped, so an interrupted run resumes instead of starting over.
    path = out_dir / "long" / "predictions.jsonl"
    wanted = {d["id"] for d in digests}
    rows = [r for r in _read_jsonl(path) if r["id"] in wanted] if path.exists() else []
    done = {r["id"] for r in rows}
    summarizer = Summarizer(model)
    for k, digest in enumerate(digests, 1):
        if digest["id"] not in done:
            cut = summarizer.summarize(digest["text"], strategy="truncate")
            rows.append(score_long("truncate", digest, cut.text, cut.seconds, 1))
            full = summarizer.summarize(digest["text"], strategy="chunk")
            rows.append(score_long("chunk + combine", digest, full.text, full.seconds, full.chunks))
            rows.append(score_long("chunk, all parts", digest, " ".join(full.parts), full.seconds, full.chunks))
            _write_jsonl(path, rows)
        print(f"  long documents: {k}/{len(digests)}", flush=True)
    meta = {"model": model, "digests": len(digests), "articles_per_digest": len(digests[0]["highlights"]),
            "input_tokens_median": int(np.median([len(summarizer.tokenizer(d["text"])["input_ids"])
                                                  for d in digests]))}
    (out_dir / "long" / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


def summarize_long(out_dir: Path) -> dict:
    path = out_dir / "long" / "predictions.jsonl"
    if not path.exists():
        return {}
    rows = _read_jsonl(path)
    report = {"meta": json.loads((out_dir / "long" / "meta.json").read_text(encoding="utf-8"))}
    for method in dict.fromkeys(r["method"] for r in rows):
        mine = [r for r in rows if r["method"] == method]
        recalls = np.array([r["article_recall"] for r in mine])
        report[method] = {
            **{m: round(statistics.mean(r[m] for r in mine), 2) for m in ROUGE_TYPES},
            "article_recall": [round(float(x), 1) for x in recalls.mean(axis=0)],
            "words_mean": round(statistics.mean(r["words"] for r in mine), 1),
            "seconds_median": round(statistics.median(r["seconds"] for r in mine), 1),
            "chunks_median": statistics.median(r["chunks"] for r in mine),
        }
    return report


# ------------------------------------------------------------------ report

def write_report(out_dir: Path, extra: dict | None = None) -> dict:
    report_file = out_dir / "report.json"
    report = json.loads(report_file.read_text(encoding="utf-8")) if report_file.exists() else {}
    report.update(extra or {})
    report["news"] = summarize_news(out_dir)
    report["long"] = summarize_long(out_dir)
    report["environment"] = {"python": platform.python_version(), "torch": torch.__version__,
                             "device": "cuda" if torch.cuda.is_available() else "cpu",
                             "cpu_threads": torch.get_num_threads(), "processor": platform.processor()}
    report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def tables(report: dict) -> str:
    lines = ["| System | ROUGE-1 | ROUGE-2 | ROUGE-L | Novel bigrams | Numbers in source | Words "
             "| Seconds / article | Parameters |",
             "|---|---|---|---|---|---|---|---|---|"]
    for system, e in report.get("news", {}).items():
        numbers = "–" if e.get("numbers_supported_pct") is None else f"{e['numbers_supported_pct']:.1f}%"
        params = f"{e['parameters_m']:.0f}M" if "parameters_m" in e else "–"
        lines.append(
            f"| {system} | {e['rouge1']['mean']:.2f} | {e['rouge2']['mean']:.2f} "
            f"({e['rouge2']['ci_low']:.1f}–{e['rouge2']['ci_high']:.1f}) | {e['rougeLsum']['mean']:.2f} | "
            f"{e['novel_bigrams_pct']:.1f}% | {numbers} | {e['words_mean']:.0f} | "
            f"{e['seconds_median']:.2f} | {params} |")
    for system, e in report.get("news", {}).items():
        diff = e.get(f"vs_{REFERENCE_SYSTEM}")
        if diff:
            d = diff["rouge2"]
            lines.append(f"\n{system} vs {REFERENCE_SYSTEM}, ROUGE-2: {d['mean']:+.2f} "
                         f"(95% CI {d['ci_low']:+.2f} to {d['ci_high']:+.2f})")
    long = report.get("long") or {}
    if long:
        lines += ["", "| Method | ROUGE-1 | ROUGE-2 | ROUGE-L | Article 1 / 2 / 3 recall | Words | Seconds |",
                  "|---|---|---|---|---|---|---|"]
        for method, e in long.items():
            if method == "meta":
                continue
            recall = " / ".join(f"{x:.0f}%" for x in e["article_recall"])
            lines.append(f"| {method} | {e['rouge1']:.2f} | {e['rouge2']:.2f} | {e['rougeLsum']:.2f} | "
                         f"{recall} | {e['words_mean']:.0f} | {e['seconds_median']:.0f} |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--n", type=int, default=200, help="news articles to score")
    parser.add_argument("--digests", type=int, default=30, help="long documents (3 articles each)")
    parser.add_argument("--systems", nargs="+", choices=list(SYSTEMS), default=list(SYSTEMS))
    parser.add_argument("--long-only", action="store_true")
    parser.add_argument("--news-only", action="store_true")
    parser.add_argument("--table", action="store_true", help="print tables from saved results and exit")
    parser.add_argument("--out", type=Path, default=RESULTS_DIR)
    args = parser.parse_args()

    if args.table:
        print(tables(json.loads((args.out / "report.json").read_text(encoding="utf-8"))))
        return

    frame = load_cnn_dm_test()
    news_items = sample(frame, args.n, SEED)
    extra = {"news_sample": {"dataset": "abisee/cnn_dailymail 3.0.0 test", "n": args.n, "seed": SEED}}

    if not args.long_only:
        extra["dataset_lengths"] = length_stats(frame)
        print(f"Test-set lengths: {extra['dataset_lengths']}", flush=True)
        for system in args.systems:
            if SYSTEMS[system] and system == "local-fine-tuned" and not LOCAL_MODEL_DIR.exists():
                print("Skipping local-fine-tuned: fine_tuned_bart_model/ not found")
                continue
            print(f"News: {system}", flush=True)
            run_news(system, news_items, args.out)
            write_report(args.out, extra)
        if "local-fine-tuned" in args.systems and LOCAL_MODEL_DIR.exists():
            extra["local_fine_tuned_weight_change"] = weight_change(BASE_MODEL, str(LOCAL_MODEL_DIR))

    if not args.news_only:
        print("Long documents", flush=True)
        long_items = sample(frame, args.digests * 3, SEED + 1, exclude={i["index"] for i in news_items})
        run_long(make_digests(long_items), BASE_MODEL, args.out)

    report = write_report(args.out, extra)
    print(tables(report))


if __name__ == "__main__":
    main()
