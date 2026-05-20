# CaseLens-VLM

**CaseLens-VLM** is a multimodal document retrieval project over real scanned DocVQA pages. It uses a vision-language model to turn page images into searchable evidence, retrieves cited pages for questions, and evaluates retrieval quality with Recall@k.

I built this to test a practical question: when documents are scanned pages, tables, forms, and layout-heavy reports, how much does visual page understanding help retrieval compared with metadata alone?

## Problem

Most enterprise RAG demos assume clean text. Real documents often contain scanned pages, forms, charts, tables, signatures, and layout cues. CaseLens-VLM shows how to convert document images into retrievable multimodal evidence.

## What This Does

- Vision-language model inference on document pages
- Multimodal RAG over real document images
- Page-level citation and retrieval evaluation
- Isambard/HPC batch workflow
- Local grounding audit and AWS GenAI architecture mapping

## Dataset

The main dataset is **DocVQA**, a document visual question answering benchmark built from real document pages from the UCSF Industry Documents Library. Raw dataset files are not committed to this repository.

Useful references:

- DocVQA dataset: https://site.docvqa.org/datasets/docvqa
- Qwen2.5-VL model family: https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct

## Architecture

```mermaid
flowchart LR
    A[DocVQA saved dataset] --> B[Page image export]
    B --> C[Page evidence JSONL]
    C --> D[Qwen2.5-VL page summaries]
    D --> E[Retrieval index]
    E --> F[Cited document QA]
    F --> G[Recall@k evaluation]
```

## Isambard Quickstart

The project assumes DocVQA has already been downloaded to:

```bash
$SCRATCH/vlm_doc_project/docvqa_hf
```

Prepare a 500-question sample:

```bash
cd "$SCRATCH/vlm_doc_project/caselens-vlm"
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate vlm-doc

pip install -r requirements.txt

python scripts/prepare_docvqa.py \
  --dataset "$SCRATCH/vlm_doc_project/docvqa_hf" \
  --out data/docvqa_sample \
  --split validation \
  --limit 500
```

Run the demo retrieval baseline:

```bash
python scripts/build_index.py \
  --records data/docvqa_sample/page_records.jsonl \
  --out data/docvqa_sample/index_demo.json \
  --include-gold-questions

python scripts/evaluate_retrieval.py \
  --index data/docvqa_sample/index_demo.json \
  --records data/docvqa_sample/page_records.jsonl \
  --qas data/docvqa_sample/qa_records.jsonl \
  --k 5 \
  --out data/docvqa_sample/eval_demo.json
```

Generate VLM page summaries:

```bash
# Install a GPU-compatible PyTorch build first, then:
pip install -r requirements-vlm.txt

python scripts/generate_vlm_summaries.py \
  --records data/docvqa_sample/page_records.jsonl \
  --image-root data/docvqa_sample \
  --out data/docvqa_sample/vlm_page_summaries.jsonl \
  --model Qwen/Qwen2.5-VL-3B-Instruct \
  --limit 100 \
  --resume
```

On shared clusters, use `--local-files-only` with a cached model snapshot to avoid Hugging Face rate limits.

Build a strict VLM-summary index:

```bash
python scripts/build_index.py \
  --records data/docvqa_sample/vlm_page_summaries.jsonl \
  --out data/docvqa_sample/index_vlm.json \
  --text-field vlm_summary

python scripts/ask.py \
  --index data/docvqa_sample/index_vlm.json \
  --records data/docvqa_sample/vlm_page_summaries.jsonl \
  --question "Which page contains the coffee break time?" \
  --k 3
```

## Current Verified Baseline

The project now has both a demo baseline and real Qwen2.5-VL results. Full details are in `docs/results.md`.

| Sample | Pages | Questions | Mode | Recall@1 | Recall@5 |
| --- | ---: | ---: | --- | ---: | ---: |
| Qwen real run | 100 | 339 | hybrid BM25 + MiniLM embeddings | not measured | 0.587 |
| Qwen real run | 100 | 339 | strict VLM-summary retrieval | 0.363 | 0.534 |
| Same subset | 100 | 339 | metadata-only retrieval | 0.003 | 0.035 |
| Same subset | 100 | 339 | demo gold-question retrieval | 0.923 | 0.988 |
| Smoke | 29 | 100 | demo gold-question retrieval | not measured | 1.000 |
| Main | 138 | 500 | demo gold-question retrieval | not measured | 0.978 |

The real VLM run used Qwen2.5-VL-3B-Instruct on an NVIDIA GH200 GPU node through the public Isambard container `/lus/lfs1aip2/projects/public/u6ei/torch_cuda126.sif`. The 100-page VLM inference run completed in 24m47s. The hybrid row adds a lightweight dense retrieval pass using `sentence-transformers/all-MiniLM-L6-v2` over the same Qwen summaries.

On Isambard, verify the PyTorch build before VLM inference:

```bash
python - << 'EOF'
import torch
print(torch.__version__)
print("cuda_available:", torch.cuda.is_available())
print("torch_cuda:", torch.version.cuda)
EOF
```

## CLI Reference

```bash
python scripts/prepare_docvqa.py --dataset PATH --out DIR --split validation --limit 500
python scripts/generate_vlm_summaries.py --records page_records.jsonl --image-root DIR --out vlm_page_summaries.jsonl
python scripts/build_index.py --records RECORDS --out index.json --text-field metadata|vlm_summary
python scripts/ask.py --index index.json --records RECORDS --question "..." --k 5
python scripts/evaluate_retrieval.py --index index.json --records RECORDS --qas qa_records.jsonl --k 5
python scripts/audit_run.py --index index.json --records RECORDS --question "..." --answer "..." --out audit.jsonl
```

## Streamlit Demo

After generating local artifacts, launch the reviewer UI:

```bash
streamlit run app.py
```

The app lets you enter a question, retrieve cited pages, inspect page images, and read the VLM-generated evidence summary.

## Repository Policy

This repo intentionally excludes:

- Raw DocVQA images and saved datasets
- Generated indexes and JSONL outputs
- Model weights and Hugging Face caches
- Slurm logs

See `docs/aws_architecture.md` for the AWS implementation mapping and `docs/cv_project_summary.md` for a concise portfolio summary.
See `docs/results.md` for real Qwen2.5-VL retrieval metrics.
See `docs/linkedin_post.md` and `docs/interview_talking_points.md` for company-facing materials.
See `docs/enterprise_architecture.md` for the guardrails, audit, and monitoring design.

## Limitations

- The demo baseline uses DocVQA question text and is only a pipeline sanity check.
- The strict VLM path depends on downloading and running a VLM such as Qwen2.5-VL-3B.
- PyTorch/CUDA installation is cluster-specific; use a build compatible with the active NVIDIA driver.
- Official DocVQA OCR transcriptions are not bundled in the Hugging Face mirror used here.
