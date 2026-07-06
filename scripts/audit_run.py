#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
    parser.add_argument("--answer", default="")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def cited_page_ids(answer: str, retrieved_ids: list[str]) -> list[str]:
    answer_lower = answer.lower()
    return [page_id for page_id in retrieved_ids if page_id.lower() in answer_lower]


def audit_status(answer: str, retrieved_ids: list[str]) -> tuple[str, list[str]]:
    warnings: list[str] = []
    if not answer.strip():
        warnings.append("empty_answer")
    if answer.strip() and not cited_page_ids(answer, retrieved_ids):
        warnings.append("answer_has_no_retrieved_page_citation")
    if not retrieved_ids:
        warnings.append("no_retrieved_pages")
    return ("pass" if not warnings else "review"), warnings


def main() -> None:
    args = parse_args()
    index = BM25Index.from_dict(read_json(args.index))
    records = {record["page_id"]: record for record in read_jsonl(args.records)}
    with trace_query(args.question, metadata={"entrypoint": "scripts/audit_run.py", "top_k": args.k}):
        results = index.search(args.question, k=args.k)
    retrieved = [
        {
            "page_id": result.page_id,
            "score": result.score,
            "image_path": records.get(result.page_id, {}).get("image_path", ""),
        }
        for result in results
    ]
    retrieved_ids = [item["page_id"] for item in retrieved]
    status, warnings = audit_status(args.answer, retrieved_ids)
    payload: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": args.question,
        "answer": args.answer,
        "retrieved": retrieved,
        "cited_retrieved_pages": cited_page_ids(args.answer, retrieved_ids),
        "grounding_status": status,
        "warnings": warnings,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
    print(json.dumps(payload, indent=2))
    flush_traces()


if __name__ == "__main__":
    main()
