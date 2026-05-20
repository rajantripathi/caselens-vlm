#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

from datasets import load_from_disk
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from caselens.io import write_jsonl


def page_id(row: dict) -> str:
    return f"{row['ucsf_document_id']}_p{row['ucsf_document_page_no']}"


def build_page_summary(record: dict) -> str:
    types = ", ".join(sorted(record["question_types"])) or "unknown"
    return (
        f"DocVQA page {record['page_no']} from document {record['document_id']}. "
        f"Observed question evidence types: {types}. "
        f"Image size: {record['image_width']}x{record['image_height']} pixels. "
        "Use this page as visual document evidence and inspect the image for exact values."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Path to saved DocVQA dataset")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--split", default="validation")
    parser.add_argument("--limit", type=int, default=500)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out)
    image_dir = out_dir / "page_images"
    image_dir.mkdir(parents=True, exist_ok=True)

    dataset = load_from_disk(args.dataset)[args.split]
    if args.limit:
        dataset = dataset.select(range(min(args.limit, len(dataset))))

    pages: dict[str, dict] = {}
    qas_by_page: defaultdict[str, list[dict]] = defaultdict(list)
    qa_records: list[dict] = []

    for row in tqdm(dataset, desc=f"Preparing {args.split}"):
        pid = page_id(row)
        image_path = image_dir / f"{pid}.png"
        if pid not in pages:
            image = row["image"]
            image.save(image_path)
            pages[pid] = {
                "page_id": pid,
                "document_id": row["ucsf_document_id"],
                "doc_id": row["docId"],
                "page_no": row["ucsf_document_page_no"],
                "image_path": str(image_path.relative_to(out_dir)),
                "image_width": image.size[0],
                "image_height": image.size[1],
                "question_types": set(),
            }
        pages[pid]["question_types"].update(row.get("question_types") or [])
        qa = {
            "question_id": row["questionId"],
            "page_id": pid,
            "question": row["question"],
            "answers": row.get("answers") or [],
            "question_types": row.get("question_types") or [],
        }
        qas_by_page[pid].append(qa)
        qa_records.append(qa)

    page_records: list[dict] = []
    for pid, record in sorted(pages.items()):
        record["question_types"] = sorted(record["question_types"])
        record["qas"] = qas_by_page[pid]
        record["qa_count"] = len(record["qas"])
        record["page_summary"] = build_page_summary(record)
        page_records.append(record)

    write_jsonl(out_dir / "page_records.jsonl", page_records)
    write_jsonl(out_dir / "qa_records.jsonl", qa_records)
    print(f"Wrote {len(page_records)} page records and {len(qa_records)} QA records to {out_dir}")


if __name__ == "__main__":
    main()
