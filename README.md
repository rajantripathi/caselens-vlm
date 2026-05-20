# CaseLens-VLM

**CaseLens-VLM** is a multimodal document RAG prototype for evidence review over real scanned document images from DocVQA. It prepares document pages, generates page-level visual evidence with a VLM, builds a retrieval index, answers questions with cited pages, and reports retrieval metrics.

The project is designed as a CV-ready applied GenAI project: small enough to reproduce, but close to the architecture used in enterprise document intelligence systems.

## Why This Project

Most enterprise RAG demos assume clean text. Real documents often contain scanned pages, forms, charts, tables, signatures, and layout cues. CaseLens-VLM shows how to convert document images into retrievable multimodal evidence.

This project demonstrates:

- Vision-language model inference on document pages
- Multimodal RAG over real document images
- Page-level citation and retrieval evaluation
- Isambard/HPC batch workflow
- AWS GenAI architecture mapping

## Dataset

The main dataset is **DocVQA**, a document visual question answering benchmark built from real document pages from the UCSF Industry Documents Library. Raw dataset files are not committed to this repository.

Useful references:

- DocVQA dataset: https://site.docvqa.org/datasets/docvqa
- Qwen2.5-VL model family: https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct

## Architecture

```text
DocVQA saved dataset
  -> page image export
  -> page evidence JSONL
  -> VLM page summaries
  -> retrieval index
  -> cited document QA
  -> Recall@k evaluation
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
python scripts/generate_vlm_summaries.py \
  --records data/docvqa_sample/page_records.jsonl \
  --image-root data/docvqa_sample \
  --out data/docvqa_sample/vlm_page_summaries.jsonl \
  --model Qwen/Qwen2.5-VL-3B-Instruct \
  --limit 20
```

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

The demo baseline indexes DocVQA question text to verify the retrieval and evaluation pipeline before VLM inference.

| Sample | Pages | Questions | Mode | Recall@5 |
| --- | ---: | ---: | --- | ---: |
| Smoke | 29 | 100 | demo gold-question retrieval | 1.000 |
| Main | 138 | 500 | demo gold-question retrieval | 0.978 |

The VLM-summary mode is the real multimodal path and is designed to run on Isambard GPU nodes via `slurm/run_vlm_summaries.sbatch`.

## CLI Reference

```bash
python scripts/prepare_docvqa.py --dataset PATH --out DIR --split validation --limit 500
python scripts/generate_vlm_summaries.py --records page_records.jsonl --image-root DIR --out vlm_page_summaries.jsonl
python scripts/build_index.py --records RECORDS --out index.json --text-field metadata|vlm_summary
python scripts/ask.py --index index.json --records RECORDS --question "..." --k 5
python scripts/evaluate_retrieval.py --index index.json --records RECORDS --qas qa_records.jsonl --k 5
```

## Repository Policy

This repo intentionally excludes:

- Raw DocVQA images and saved datasets
- Generated indexes and JSONL outputs
- Model weights and Hugging Face caches
- Slurm logs

See `docs/aws_architecture.md` for the AWS implementation mapping and `docs/cv_project_summary.md` for a concise portfolio summary.

## Limitations

- The demo baseline uses DocVQA question text and is only a pipeline sanity check.
- The strict VLM path depends on downloading and running a VLM such as Qwen2.5-VL-3B.
- Official DocVQA OCR transcriptions are not bundled in the Hugging Face mirror used here.
