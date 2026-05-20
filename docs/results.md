# Real Results

These results were produced on Isambard using real DocVQA page images and Qwen2.5-VL-3B-Instruct.

## Environment

- Hardware: NVIDIA GH200 120GB GPU node
- Container: `/lus/lfs1aip2/projects/public/u6ei/torch_cuda126.sif`
- PyTorch in container: `2.9.1+cu126`
- Model: `Qwen/Qwen2.5-VL-3B-Instruct`
- Dataset split: DocVQA validation
- Sample: first 25 unique prepared pages from the 500-question sample
- Evaluated questions: 76
- Slurm job: `4662289`, completed in `00:10:08`

## Retrieval Results

| Retrieval mode | Indexed evidence | Questions | Recall@1 | Recall@5 |
| --- | --- | ---: | ---: | ---: |
| Metadata-only | page id, doc id, page number, question type labels | 76 | not measured | 0.145 |
| Qwen2.5-VL summaries | VLM-generated page descriptions and extracted visible text | 76 | 0.382 | 0.605 |
| Demo upper-bound | DocVQA question text included in index | 76 | not measured | 0.987 |

## Interpretation

The strict VLM-summary index substantially improves retrieval over metadata-only indexing. This confirms the core project claim: visual page understanding provides useful retrieval evidence for scanned document question answering.

The demo upper-bound is intentionally not a valid production setting because it indexes gold question text. It is retained only as a pipeline sanity check.

## Example VLM Outputs

Qwen2.5-VL generated useful page-level evidence, including visible text and layout cues. Examples included:

- A PepsiCo shareholder meeting notice with detected title text and meeting location.
- A job/news document with an extracted sentence about LTL service for frozen shipments.
- A medical communications plan page with extracted budget/table-like evidence.
- A table about vasomotor symptom treatments with treatment and adverse-effect columns.

## Current Limitations

- The 25-page result is a credible first real run, not a full benchmark.
- Some VLM outputs are markdown-wrapped JSON rather than strict parsed JSON.
- Retrieval uses BM25 over generated summaries; embeddings are a natural next step.
- The model was run without a Hugging Face token, so larger runs may benefit from authenticated downloads.
