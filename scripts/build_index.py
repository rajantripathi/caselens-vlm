#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from caselens.io import read_jsonl, write_json
from caselens.retrieval import BM25Index


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--include-gold-questions", action="store_true")
    parser.add_argument(
        "--text-field",
        choices=["metadata", "vlm_summary"],
        default="metadata",
        help="Evidence text to index. Use vlm_summary after running generate_vlm_summaries.py.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = read_jsonl(args.records)
    index = BM25Index.from_records(
        records,
        include_gold_questions=args.include_gold_questions,
        text_field=args.text_field,
    )
    payload = index.to_dict()
    payload["include_gold_questions"] = args.include_gold_questions
    payload["text_field"] = args.text_field
    write_json(args.out, payload)
    print(f"Indexed {len(records)} pages -> {args.out}")
    if args.include_gold_questions:
        print("Mode: demo retrieval includes DocVQA question text.")
    else:
        print(f"Mode: strict retrieval over {args.text_field}.")


if __name__ == "__main__":
    main()
