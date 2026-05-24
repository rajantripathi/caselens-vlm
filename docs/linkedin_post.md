# LinkedIn Post Drafts

## Professional Version

Over the past few weeks I benchmarked VLM-assisted retrieval for multimodal RAG over scanned documents on Isambard-AI GH200 nodes.

The evaluation uses a 100-page DocVQA subset with 339 questions and compares retrieval pipelines against the same question-to-page labels:

- Metadata-only baseline: Recall@5 = 0.035
- Qwen3-VL summary retrieval: Recall@5 = 0.658
- Qwen3-VL + hybrid retrieval (BM25 + MiniLM): Recall@5 = 0.708

The hybrid VLM-assisted pipeline produced roughly a 20-fold improvement over metadata-only retrieval on this subset.

The main takeaway was that retrieval design carried most of the practical gain. Visual page summaries gave the retriever much stronger evidence than metadata alone, and adding dense retrieval improved the result again without changing the VLM evidence layer.

That pattern is consistent with my earlier bilingual RAG work: corpus preparation, evidence representation, and retrieval engineering often dominate production retrieval metrics more than swapping the base model in isolation.

The repository includes the benchmark code, AWS reference architecture, and a reproducible Slurm workflow:

https://github.com/rajantripathi/caselens-vlm

#GenAI #MultimodalAI #RAG #DocumentAI #AWS #HPC #VisionLanguageModels

## Technical Version

CaseLens-VLM is a multimodal document AI pipeline for scanned document retrieval.

The pipeline takes real DocVQA page images, generates page-level evidence with Qwen3-VL, indexes those summaries, retrieves cited pages for questions, and evaluates Recall@k against DocVQA labels.

Retrieval results on the current 100-page / 339-question subset:

| Retrieval mode | Recall@5 |
| --- | ---: |
| Metadata-only | 0.035 |
| Qwen3-VL summaries | 0.658 |
| Qwen3-VL hybrid BM25 + MiniLM | 0.708 |
| Demo upper-bound | 0.988 |

The project also includes hybrid retrieval, citation-level audit logs, grounding checks, an AWS architecture mapping, and a lightweight reviewer UI.

This is not a production deployment, but it is a working implementation of a production-relevant pattern: convert visual document pages into evidence, retrieve with provenance, and evaluate retrieval quality directly.

GitHub: https://github.com/rajantripathi/caselens-vlm
