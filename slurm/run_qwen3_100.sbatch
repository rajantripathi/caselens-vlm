#!/bin/bash
#SBATCH --job-name=caselens_qwen3_100
#SBATCH --partition=workq
#SBATCH --nodes=1
#SBATCH --gres=gpu:1
#SBATCH --time=04:00:00
#SBATCH --output=logs/qwen3_100_%j.out
#SBATCH --error=logs/qwen3_100_%j.err

set -euo pipefail

cd "$SCRATCH/vlm_doc_project/caselens-vlm-github"
mkdir -p logs

export HF_HOME="${QWEN3_HF_HOME:-$SCRATCH/hf_cache_qwen3}"
export TRANSFORMERS_CACHE="$HF_HOME/transformers"

apptainer exec --nv --bind "$SCRATCH:$SCRATCH" \
  /lus/lfs1aip2/projects/public/u6ei/torch_cuda126.sif \
  python scripts/generate_vlm_summaries.py \
  --records data/docvqa_sample/page_records.jsonl \
  --image-root data/docvqa_sample \
  --out data/docvqa_sample/vlm_qwen3_8b_100.jsonl \
  --model Qwen/Qwen3-VL-8B-Instruct \
  --model-label Qwen/Qwen3-VL-8B-Instruct \
  --backend qwen3 \
  --limit 100 \
  --max-new-tokens 180 \
  --max-pixels 501760 \
  --resume
