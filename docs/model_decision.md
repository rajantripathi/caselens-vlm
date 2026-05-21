# Model Decision

CaseLens-VLM uses **Qwen3-VL-8B-Instruct** as the primary open vision-language model.

## Why a Single Primary Model

For a recruiter-facing portfolio project, the goal is not to benchmark every available VLM. The goal is to show a complete, defensible enterprise pattern:

- real scanned document data
- page-level visual evidence generation
- cited retrieval
- Recall@k evaluation
- audit and guardrail design
- Isambard GPU batch workflow
- AWS production mapping

Keeping Qwen3-VL as the single primary model makes the project easier to explain and maintain. The repository still has meaningful comparisons, but they compare retrieval architecture rather than unrelated model families:

| Comparison | Purpose |
| --- | --- |
| Metadata-only retrieval | Shows the weakness of indexing shallow page metadata |
| Qwen3-VL summary retrieval | Measures the value of visual page understanding |
| Qwen3-VL hybrid retrieval | Shows how lexical plus dense retrieval improves search quality |
| Demo upper-bound | Sanity check only; not a production setting |

## Result to Quote

On the 100-page / 339-question DocVQA subset, Recall@5 improved from **0.035** with metadata-only retrieval to **0.658** with Qwen3-VL page summaries, and to **0.708** with Qwen3-VL plus MiniLM hybrid retrieval.

## When to Add Another Model

Add another VLM only if there is enough time to run and document it cleanly across the same pages, prompts, retrieval index, and evaluation questions. Otherwise, a second model creates noise without improving the project story.

Good future comparisons:

- a smaller model for cost and latency tradeoffs
- a larger closed model through AWS Bedrock for managed deployment comparison
- a stronger embedding/reranking stack while keeping Qwen3-VL fixed
