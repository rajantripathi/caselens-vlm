# CV Project Summary

## CV Bullet

Built **CaseLens-VLM**, a multimodal document RAG system over real DocVQA scanned documents using VLM-generated page summaries, BM25 retrieval, cited question answering, and Recall@k evaluation on Isambard GPU/HPC infrastructure.

## Interview Explanation

CaseLens-VLM takes real document images from DocVQA, exports page-level records, generates visual summaries using a vision-language model, indexes those summaries, and answers questions with page citations. The project compares retrieval modes so the difference between metadata-only, demo/gold-question retrieval, and VLM-summary retrieval is explicit.

## Why It Matters

Most enterprise documents are not clean text. They contain scanned forms, charts, tables, signatures, and layout cues. This project shows how to turn document images into grounded evidence that can be retrieved and cited, which is the core pattern behind production multimodal RAG systems.
