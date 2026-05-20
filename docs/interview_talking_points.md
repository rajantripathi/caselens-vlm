# Interview Talking Points

## One-Minute Summary

CaseLens-VLM is a multimodal document RAG system for real scanned documents. It uses Qwen2.5-VL to convert page images into textual evidence, indexes those summaries, retrieves cited pages for questions, and evaluates Recall@k on DocVQA.

## System Design

- **Ingestion:** DocVQA saved dataset is converted into page images, page metadata, and QA records.
- **Understanding:** Qwen2.5-VL generates page-level summaries and visible text/layout evidence.
- **Retrieval:** BM25 indexes metadata or VLM summaries and returns cited page IDs.
- **Evaluation:** DocVQA question-to-page labels are used to measure Recall@1 and Recall@5.
- **Infrastructure:** GPU inference runs on Isambard GH200 using Apptainer and Slurm.

## Enterprise Framing

This maps to document intelligence workloads in regulated or operational settings: invoices, forms, scanned case files, reports, compliance packs, and mixed text/image PDFs.

## AWS Mapping

- S3 for document storage
- Textract or Bedrock Data Automation for OCR/layout extraction
- Bedrock multimodal models for visual page understanding
- OpenSearch Serverless or Aurora pgvector for retrieval
- Step Functions or Batch for orchestration
- CloudWatch for observability

## Tradeoffs

- BM25 is simple and reproducible, but embedding retrieval is the next natural upgrade.
- VLM summaries improve retrieval but cost more than metadata-only indexing.
- The demo upper-bound indexes gold question text and is only a sanity check, not a valid production method.

## Result to Quote

On a real DocVQA subset, VLM-summary retrieval improved Recall@5 from 0.145 metadata-only to 0.605 using Qwen2.5-VL summaries.
