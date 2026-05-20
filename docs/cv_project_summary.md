# CV Project Summary

## CV Bullet

Built **CaseLens-VLM**, a multimodal document RAG system over real DocVQA scanned documents using Qwen2.5-VL/Qwen3-VL page understanding, hybrid retrieval, cited question answering, and Recall@k evaluation on Isambard GH200 GPU infrastructure; improved Recall@5 from 0.035 metadata-only to 0.708 with Qwen3-VL evidence plus dense embeddings on a 339-question real DocVQA subset.

## Role-Specific Versions

**Applied AI Engineer:** Built a multimodal document retrieval pipeline over real DocVQA scans using Qwen2.5-VL/Qwen3-VL page summaries, cited hybrid retrieval, audit logging, and Recall@k evaluation; improved Recall@5 from 0.035 metadata-only to 0.708 with VLM evidence plus dense embeddings.

**GenAI Solutions Architect:** Designed an enterprise-style multimodal RAG architecture mapping page extraction, VLM evidence generation, retrieval, guardrails, audit logging, and monitoring to AWS services including S3, Bedrock, Textract/BDA, OpenSearch, Step Functions, and CloudWatch.

**ML / Research Engineer:** Evaluated VLM-assisted retrieval on a 339-question DocVQA subset using Qwen2.5-VL, Qwen3-VL, metadata-only retrieval, hybrid dense retrieval, and demo upper-bound controls; documented limitations and reproducible Isambard GH200 inference workflow.

## Interview Explanation

CaseLens-VLM takes real document images from DocVQA, exports page-level records, generates visual summaries using a vision-language model, indexes those summaries, and answers questions with page citations. The project compares retrieval modes so the difference between metadata-only, demo/gold-question retrieval, and VLM-summary retrieval is explicit.

## Why It Matters

Most enterprise documents are not clean text. They contain scanned forms, charts, tables, signatures, and layout cues. This project shows how to turn document images into grounded evidence that can be retrieved and cited, which is the core pattern behind production multimodal RAG systems.
