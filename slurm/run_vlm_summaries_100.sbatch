#!/bin/bash
#SBATCH --job-name=caselens_qwen100
#SBATCH --partition=workq
#SBATCH --nodes=1
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH --output=logs/qwen100_%j.out
#SBATCH --error=logs/qwen100_%j.err

set -euo pipefail

cd "$SCRATCH/vlm_doc_project/caselens-vlm-github"
mkdir -p logs

export HF_HOME="$SCRATCH/hf_cache"
export TRANSFORMERS_CACHE="$SCRATCH/hf_cache/transformers"

apptainer exec --nv --bind "$SCRATCH:$SCRATCH" \
  /lus/lfs1aip2/projects/public/u6ei/torch_cuda126.sif \
  python scripts/generate_vlm_summaries.py \
  --records data/docvqa_sample/page_records.jsonl \
  --image-root data/docvqa_sample \
  --out data/docvqa_sample/vlm_qwen100.jsonl \
  --model "$SCRATCH/hf_cache/hub/models--Qwen--Qwen2.5-VL-3B-Instruct/snapshots/66285546d2b821cf421d4f5eb2576359d3770cd3" \
  --limit 100 \
  --max-new-tokens 160 \
  --resume \
  --local-files-only
