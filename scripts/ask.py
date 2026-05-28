#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from caselens.io import read_json, read_jsonl
from caselens.retrieval import BM25Index
from observability import flush_traces, trace_query


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", required=True)
    parser.add_argument("--records", required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--k", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    index = BM25Index.from_dict(read_json(args.index))
    records = {record["page_id"]: record for record in read_jsonl(args.records)}
    with trace_query(args.question, metadata={"entrypoint": "scripts/ask.py", "top_k": args.k}):
        results = index.search(args.question, k=args.k)

    print(f"Question: {args.question}\n")
    if not results:
        print("No matching pages found.")
        flush_traces()
        return

    print("Top cited pages:")
    for rank, result in enumerate(results, start=1):
        record = records[result.page_id]
        print(
            f"{rank}. {result.page_id} score={result.score:.3f} "
            f"image={record['image_path']} types={','.join(record['question_types'])}"
        )
        print(f"   {record['page_summary']}")
        if record.get("qas"):
            nearest = record["qas"][0]
            print(f"   Example QA: {nearest['question']} -> {nearest['answers']}")
    flush_traces()


if __name__ == "__main__":
    main()
