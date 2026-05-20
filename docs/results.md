# Real Results

These results were produced on Isambard using real DocVQA page images.

## Environment

- Hardware: NVIDIA GH200 120GB GPU node
- Container: `/lus/lfs1aip2/projects/public/u6ei/torch_cuda126.sif`
- PyTorch in container: `2.9.1+cu126`
- Baseline model: `Qwen/Qwen2.5-VL-3B-Instruct`
- Challenger model: `Qwen/Qwen3-VL-8B-Instruct`
- Dataset split: DocVQA validation
- Sample: first 100 unique prepared pages from the 500-question sample
- Evaluated questions: 339
- Qwen2.5-VL Slurm job: `4662692`, completed in `00:24:47`
- Qwen3-VL Slurm job: `4664742`, completed in `00:30:42`
- Qwen3-VL settings: `max_new_tokens=180`, `max_pixels=501760`

## Retrieval Results

| Retrieval mode | Indexed evidence | Questions | Recall@1 | Recall@5 |
| --- | --- | ---: | ---: | ---: |
| Metadata-only | page id, doc id, page number, question type labels | 339 | 0.003 | 0.035 |
| Qwen2.5-VL summaries | VLM-generated page descriptions and extracted visible text | 339 | 0.363 | 0.534 |
| Hybrid Qwen2.5-VL summaries | BM25 over VLM summaries plus MiniLM dense embeddings | 339 | not measured | 0.587 |
| Qwen3-VL summaries | VLM-generated page descriptions and extracted visible text | 339 | 0.445 | 0.658 |
| Hybrid Qwen3-VL summaries | BM25 over VLM summaries plus MiniLM dense embeddings | 339 | not measured | 0.708 |
| Demo upper-bound | DocVQA question text included in index | 339 | 0.923 | 0.988 |

## Interpretation

The strict VLM-summary index substantially improves retrieval over metadata-only indexing. Recall@5 increased from 0.035 to 0.534 on 339 real DocVQA questions, confirming the core project claim: visual page understanding provides useful retrieval evidence for scanned document question answering.

Qwen3-VL improved the strict VLM-summary run from 0.534 to 0.658 Recall@5 on the same 100-page subset. A simple hybrid retriever improved the Qwen3-VL result again to 0.708 by combining BM25 scores with dense MiniLM embeddings over the same generated evidence. This is still a small portfolio-scale experiment, but it is closer to how an enterprise search stack would combine lexical and semantic retrieval.

The demo upper-bound is intentionally not a valid production setting because it indexes gold question text. It is retained only as a pipeline sanity check.

## Example VLM Outputs

The VLMs generated useful page-level evidence, including visible text and layout cues. Examples included:

- A PepsiCo shareholder meeting notice with detected title text and meeting location.
- A job/news document with an extracted sentence about LTL service for frozen shipments.
- A medical communications plan page with extracted budget/table-like evidence.
- A table about vasomotor symptom treatments with treatment and adverse-effect columns.
- A handwritten CSF run sheet where Qwen3-VL captured `PD- 5960 C` and `83.4%`.

## Current Limitations

- The 100-page result is a credible portfolio-scale benchmark, not a full DocVQA benchmark.
- Some VLM outputs are markdown-wrapped or truncated JSON-like text rather than strict parsed JSON.
- Hybrid retrieval was tested with MiniLM embeddings; larger embedding models and reranking are natural next steps.
- The model was run without a Hugging Face token, so larger runs may benefit from authenticated downloads.
