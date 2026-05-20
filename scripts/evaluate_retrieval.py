#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from caselens.io import read_json, read_jsonl
from caselens.retrieval import BM25Index


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", required=True)
    parser.add_argument("--records", required=True)
    parser.add_argument("--qas", required=True)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--out", default="", help="Optional JSON metrics output path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    index = BM25Index.from_dict(read_json(args.index))
    valid_pages = {record["page_id"] for record in read_jsonl(args.records)}
    qas = [qa for qa in read_jsonl(args.qas) if qa["page_id"] in valid_pages]
    if args.limit:
        qas = qas[: args.limit]

    hits = 0
    for qa in qas:
        retrieved = [result.page_id for result in index.search(qa["question"], k=args.k)]
        hits += int(qa["page_id"] in retrieved)

    total = len(qas)
    recall = hits / total if total else 0.0
    metrics = {
        "evaluated_questions": total,
        f"hits_at_{args.k}": hits,
        f"recall_at_{args.k}": recall,
    }
    print(f"evaluated_questions={total}")
    print(f"hits_at_{args.k}={hits}")
    print(f"recall_at_{args.k}={recall:.4f}")
    if args.out:
        from caselens.io import write_json

        write_json(args.out, metrics)


if __name__ == "__main__":
    main()
