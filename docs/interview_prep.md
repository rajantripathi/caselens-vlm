# Interview Prep

## Thirty-Second Version

CaseLens-VLM is a multimodal document RAG project over real scanned DocVQA pages. I used Qwen2.5-VL and Qwen3-VL to convert page images into textual evidence, indexed that evidence with BM25 and dense hybrid retrieval, and evaluated retrieval quality with real question-to-page labels. The best configuration improved Recall@5 from `0.035` with metadata-only retrieval to `0.708` with Qwen3-VL plus hybrid retrieval.

## Two-Minute Architecture Walkthrough

1. **Ingestion:** Start with scanned pages and questions from DocVQA.
2. **Understanding:** Run VLM inference to generate page-level evidence summaries from visual document pages.
3. **Indexing:** Store page evidence with provenance and build lexical plus dense indexes.
4. **Retrieval:** Given a question, retrieve candidate pages and return cited evidence.
5. **Evaluation:** Compare retrieved pages against DocVQA labels using Recall@1 and Recall@5.
6. **Governance:** Add citation audit, limitations, and an enterprise architecture with guardrails and human review.

## Result to Quote

| Mode | Recall@5 |
| --- | ---: |
| Metadata-only | 0.035 |
| Qwen2.5-VL summaries | 0.534 |
| Qwen2.5-VL hybrid | 0.587 |
| Qwen3-VL summaries | 0.658 |
| Qwen3-VL hybrid | 0.708 |

## How to Connect It to DialogXR

DialogXR-style systems are not just chatbots. They need secure ingestion, identity, policy controls, PII handling, retrieval, grounding, human review, and auditability. CaseLens maps well because it demonstrates the core pattern:

- Convert messy multimodal evidence into searchable records.
- Retrieve cited evidence rather than relying on model memory.
- Evaluate retrieval quality instead of only showing a demo.
- Add guardrails and audit logs so a reviewer can challenge the output.
- Keep humans responsible for sensitive decisions.

## What to Say If Asked About the Streamlit Demo

The public Streamlit app is a showcase, not a live GPU inference endpoint. It shows verified metrics, a small retrieval demo, image upload, and the enterprise architecture. The upload path previews the image and indexes a user-provided visual note. In production, that uploaded image would go through OCR/layout extraction and a VLM endpoint before indexing.

This is the right tradeoff for a public portfolio app because raw DocVQA images and model weights are not committed, and Streamlit Community Cloud is not suitable for running an 8B VLM.

## Questions You Should Be Ready For

**Why use VLM summaries instead of OCR only?**  
OCR extracts text but misses layout, handwriting context, charts, visual hierarchy, and page structure. VLM summaries turn visual cues into retrievable evidence. This is why retrieval improves over metadata-only search.

**Why BM25 and hybrid retrieval?**  
BM25 is a simple lexical baseline and is reproducible. Dense embeddings help with semantic matches. Hybrid retrieval is common in enterprise search because exact terms and semantic similarity both matter.

**Why page-level citations?**  
Page-level citations are easy for a human reviewer to inspect. In regulated workflows, traceability matters more than a fluent answer.

**Why is the demo upper-bound not a valid production result?**  
It indexes gold question text, so it is only a pipeline sanity check. The real claim is based on strict VLM summaries and hybrid retrieval.

**What would you improve next?**  
I would add OCR-only baselines, larger evaluation samples, reranking, a real multimodal embedding model, structured JSON validation, and a deployed Bedrock/SageMaker VLM endpoint for live image inference.

**How would this run on AWS?**  
S3 stores documents and evidence, Textract or Bedrock Data Automation extracts layout, Bedrock or SageMaker runs multimodal inference, OpenSearch or Bedrock Knowledge Bases handles retrieval, Bedrock Guardrails checks grounding and policy, and CloudWatch/CloudTrail/S3 provide monitoring and audit.

## Strong Interview Framing

Do not describe this as just a Streamlit app. Describe it as:

> A measured multimodal document intelligence pipeline with real data, VLM-based page understanding, hybrid retrieval, citations, audit controls, and an enterprise deployment design.

## Honest Limitations

- The benchmark is portfolio-scale: 100 pages and 339 questions, not the full DocVQA benchmark.
- Public Streamlit upload does not run live VLM inference.
- Some VLM outputs are JSON-like text rather than strictly validated JSON.
- The project evaluates retrieval, not final answer generation quality.
- Raw DocVQA images are excluded from GitHub by design.
