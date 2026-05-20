#!/bin/bash
#SBATCH --job-name=caselens_vlm
#SBATCH --partition=workq
#SBATCH --nodes=1
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH --output=logs/vlm_summaries_%j.out
#SBATCH --error=logs/vlm_summaries_%j.err

set -euo pipefail

cd "$SCRATCH/vlm_doc_project/caselens-vlm"
mkdir -p logs

export HF_HOME="$SCRATCH/hf_cache"
export TRANSFORMERS_CACHE="$SCRATCH/hf_cache/transformers"

apptainer exec --nv --bind "$SCRATCH:$SCRATCH" \
  /lus/lfs1aip2/projects/public/u6ei/torch_cuda126.sif \
  python scripts/generate_vlm_summaries.py \
  --records data/docvqa_sample/page_records.jsonl \
  --image-root data/docvqa_sample \
  --out data/docvqa_sample/vlm_page_summaries.jsonl \
  --model Qwen/Qwen2.5-VL-3B-Instruct \
  --limit 25 \
  --max-new-tokens 160
