# Real Results

These results were produced on Isambard using real DocVQA page images and Qwen2.5-VL-3B-Instruct.

## Environment

- Hardware: NVIDIA GH200 120GB GPU node
- Container: `/lus/lfs1aip2/projects/public/u6ei/torch_cuda126.sif`
- PyTorch in container: `2.9.1+cu126`
- Model: `Qwen/Qwen2.5-VL-3B-Instruct`
- Dataset split: DocVQA validation
- Sample: first 100 unique prepared pages from the 500-question sample
- Evaluated questions: 339
- Slurm job: `4662692`, completed in `00:24:47`

## Retrieval Results

| Retrieval mode | Indexed evidence | Questions | Recall@1 | Recall@5 |
| --- | --- | ---: | ---: | ---: |
| Metadata-only | page id, doc id, page number, question type labels | 339 | 0.003 | 0.035 |
| Qwen2.5-VL summaries | VLM-generated page descriptions and extracted visible text | 339 | 0.363 | 0.534 |
| Demo upper-bound | DocVQA question text included in index | 339 | 0.923 | 0.988 |

## Interpretation

The strict VLM-summary index substantially improves retrieval over metadata-only indexing. Recall@5 increased from 0.035 to 0.534 on 339 real DocVQA questions, confirming the core project claim: visual page understanding provides useful retrieval evidence for scanned document question answering.

The demo upper-bound is intentionally not a valid production setting because it indexes gold question text. It is retained only as a pipeline sanity check.

## Example VLM Outputs

Qwen2.5-VL generated useful page-level evidence, including visible text and layout cues. Examples included:

- A PepsiCo shareholder meeting notice with detected title text and meeting location.
- A job/news document with an extracted sentence about LTL service for frozen shipments.
- A medical communications plan page with extracted budget/table-like evidence.
- A table about vasomotor symptom treatments with treatment and adverse-effect columns.

## Current Limitations

- The 100-page result is a credible portfolio-scale benchmark, not a full DocVQA benchmark.
- Some VLM outputs are markdown-wrapped JSON rather than strict parsed JSON.
- Retrieval uses BM25 over generated summaries; embeddings are a natural next step.
- The model was run without a Hugging Face token, so larger runs may benefit from authenticated downloads.
