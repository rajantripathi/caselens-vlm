#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from caselens.io import read_json, read_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-dir", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--summary-file", default="vlm_qwen3_8b_100.jsonl")
    return parser.parse_args()


def load_metric(eval_dir: Path, filename: str, key: str) -> str:
    path = eval_dir / filename
    if not path.exists():
        return "not measured"
    payload = read_json(path)
    value = payload.get(key)
    return f"{value:.3f}" if isinstance(value, float) else str(value)


def main() -> None:
    args = parse_args()
    eval_dir = Path(args.eval_dir)
    summary_path = eval_dir / args.summary_file
    page_count = 0
    question_count = 0
    if summary_path.exists():
        summaries = read_jsonl(summary_path)
        page_count = len(summaries)
        question_count = sum(len(item.get("qas", [])) for item in summaries)

    rows = [
        [
            "Metadata-only",
            "page/document metadata and question type labels",
            load_metric(eval_dir, "eval_metadata100_k1.json", "recall_at_1"),
            load_metric(eval_dir, "eval_metadata100_k5.json", "recall_at_5"),
        ],
        [
            "Qwen3-VL summaries",
            "VLM page descriptions and extracted visible text",
            load_metric(eval_dir, "eval_qwen3_8b_100_k1.json", "recall_at_1"),
            load_metric(eval_dir, "eval_qwen3_8b_100.json", "recall_at_5"),
        ],
        [
            "Demo upper-bound",
            "DocVQA question text included in index",
            load_metric(eval_dir, "eval_demo100_k1.json", "recall_at_1"),
            load_metric(eval_dir, "eval_demo100_k5.json", "recall_at_5"),
        ],
    ]

    lines = [
        "# Generated Results Summary",
        "",
        f"- VLM summary file: `{summary_path.name}`",
        f"- Indexed pages: {page_count}",
        f"- Associated DocVQA questions: {question_count}",
        "",
        "| Retrieval mode | Indexed evidence | Recall@1 | Recall@5 |",
        "| --- | --- | ---: | ---: |",
    ]
    lines.extend(f"| {mode} | {evidence} | {r1} | {r5} |" for mode, evidence, r1, r5 in rows)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    print(json.dumps({"pages": page_count, "questions": question_count}, indent=2))


if __name__ == "__main__":
    main()
