#!/usr/bin/env python
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from caselens.retrieval import BM25Index
from observability import flush_traces, trace_query


DEMO_RECORDS = [
    {
        "page_id": "medical_plan_p4",
        "document_id": "medical_plan",
        "page_no": "4",
        "image_path": "page_images/medical_plan_p4.png",
        "question_types": ["table", "free_text"],
        "page_summary": "Medical communications planning page with budget and timeline evidence.",
        "visual_summary": (
            "A communications planning page with budget fields, timeline notes, "
            "campaign planning details, and table-like evidence for financial questions."
        ),
        "detected_elements": ["budget table", "timeline", "planning notes"],
    },
    {
        "page_id": "pepsico_notice_p2",
        "document_id": "pepsico_notice",
        "page_no": "2",
        "image_path": "page_images/pepsico_notice_p2.png",
        "question_types": ["letter", "meeting"],
        "page_summary": "PepsiCo annual meeting notice with company and agenda details.",
        "visual_summary": (
            "A PepsiCo annual meeting notice with meeting location, agenda items, "
            "voting details, and a signature block."
        ),
        "detected_elements": ["company letterhead", "meeting notice", "agenda"],
    },
    {
        "page_id": "clinical_table_p12",
        "document_id": "clinical_table",
        "page_no": "12",
        "image_path": "page_images/clinical_table_p12.png",
        "question_types": ["table", "medical"],
        "page_summary": "Clinical table comparing treatments and adverse effects.",
        "visual_summary": (
            "A structured clinical table comparing treatments, effectiveness notes, "
            "adverse-effect columns, and medical comparison text."
        ),
        "detected_elements": ["clinical table", "treatment names", "adverse effects"],
    },
]


def main() -> None:
    # Keep the portfolio smoke path offline and deterministic.
    os.environ.pop("LANGFUSE_PUBLIC_KEY", None)
    os.environ.pop("LANGFUSE_SECRET_KEY", None)

    query = "Which page contains budget evidence?"
    expected_page = "medical_plan_p4"
    index = BM25Index.from_records(DEMO_RECORDS, text_field="vlm_summary")

    with trace_query(
        query,
        metadata={
            "entrypoint": "scripts/portfolio_smoke.py",
            "mode": "no_gpu_portfolio_smoke",
        },
    ):
        results = index.search(query, k=3)

    if not results:
        raise SystemExit("portfolio smoke failed: no retrieval results")

    top_result = results[0]
    answer = f"The strongest cited evidence is {top_result.page_id}."
    cited_pages = [
        result.page_id
        for result in results
        if result.page_id.lower() in answer.lower()
    ]

    passed = top_result.page_id == expected_page and expected_page in cited_pages
    payload = {
        "status": "pass" if passed else "fail",
        "gpu_required": False,
        "live_vlm_inference": False,
        "langfuse_required": False,
        "query": query,
        "expected_top_page": expected_page,
        "top_result": {
            "page_id": top_result.page_id,
            "score": round(top_result.score, 6),
        },
        "retrieved_pages": [
            {"page_id": result.page_id, "score": round(result.score, 6)}
            for result in results
        ],
        "cited_pages": cited_pages,
    }
    print(json.dumps(payload, indent=2))
    flush_traces()

    if not passed:
        raise SystemExit("portfolio smoke failed: expected page was not top-ranked and cited")


if __name__ == "__main__":
    main()
