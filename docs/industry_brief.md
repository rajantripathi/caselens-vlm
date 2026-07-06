# Industry Brief: VLM Evidence for Enterprise Document RAG

## Executive Summary

CaseLens-VLM is a multimodal document RAG benchmark over real scanned DocVQA pages. It tests whether visual page understanding improves retrieval when documents are scanned, layout-heavy, table-rich, or otherwise poorly represented by metadata alone.

On a 100-page / 339-question DocVQA subset, metadata-only retrieval reached 0.035 Recall@5. Qwen3-VL page summaries reached 0.658 Recall@5, and hybrid BM25 + MiniLM retrieval over the same VLM evidence reached 0.708 Recall@5.

The result is evidence for this limited benchmark setup, not a full DocVQA leaderboard claim.

## Why It Matters for AI Teams

Enterprise document estates rarely look like clean text corpora. They include scanned forms, tables, charts, signatures, handwritten notes, and visual layout cues. A text-only or metadata-only RAG pipeline can miss the evidence even when the page is present.

CaseLens-VLM demonstrates a production-relevant pattern:

1. Convert document pages into page-level VLM evidence.
2. Retrieve evidence with lexical and dense search.
3. Return cited pages.
4. Audit retrieval and answer grounding.
5. Map the workflow to enterprise observability and AWS deployment patterns.

## What the Benchmark Provides

- Real scanned document pages from DocVQA.
- Qwen3-VL-8B-Instruct page-level visual summaries.
- Metadata-only, VLM-summary, and hybrid retrieval comparisons.
- Recall@k evaluation against DocVQA question-to-page labels.
- Local citation audit and grounding checks.
- No-GPU portfolio smoke test and Streamlit demo path.
- AWS reference architecture and self-hosted Langfuse observability design.

## Key Result

| Retrieval mode | Evidence indexed | Questions | Recall@5 |
| --- | --- | ---: | ---: |
| Metadata-only | page metadata | 339 | 0.035 |
| Qwen3-VL summaries | visual page summaries | 339 | 0.658 |
| Hybrid Qwen3-VL summaries | BM25 + MiniLM over summaries | 339 | 0.708 |

Interpretation: visual page summaries supplied much stronger retrieval evidence than page metadata alone on this subset. Hybrid retrieval improved the VLM evidence layer further without changing the VLM.

## How an Engineering Team Can Reuse the Pattern

- Use OCR/layout extraction for baseline text and structure.
- Use a VLM to summarize page-level visual evidence where OCR is weak or incomplete.
- Store page IDs, document IDs, image paths, summary text, and provenance.
- Retrieve pages with lexical and dense methods.
- Score retrieval using page-level labels or reviewer-approved evidence targets.
- Keep generation and retrieval metrics separate before optimizing models.

## Claims to Make

- VLM-generated page evidence improved retrieval over metadata-only indexing in this benchmark.
- The project shows a practical architecture for cited multimodal document RAG.
- The no-GPU demo is a reviewer path; the measured benchmark was produced separately on Isambard GH200.

## Claims to Avoid

- Do not claim full DocVQA state-of-the-art performance.
- Do not claim the public Streamlit demo reruns Qwen3-VL live.
- Do not compare directly against proprietary systems without matched data and settings.
- Do not treat the demo upper-bound as a production method, because it indexes gold question text.

## Positioning

This project is strongest as an applied multimodal RAG engineering artifact: real document images, measured retrieval gains, citations, audit controls, observability, and an enterprise deployment map.
