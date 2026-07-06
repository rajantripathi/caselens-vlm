#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from caselens.io import read_json, read_jsonl, write_json
from caselens.retrieval import BM25Index
from observability import flush_traces, log_retrieval, trace_query


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", required=True)
    parser.add_argument("--qas", required=True)
    parser.add_argument("--bm25-index", required=True)
    parser.add_argument("--dense-index", required=True)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--alpha", type=float, default=0.5, help="BM25 weight; dense weight is 1-alpha")
    parser.add_argument("--out", default="")
    return parser.parse_args()


def minmax(scores: dict[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    lo = min(scores.values())
    hi = max(scores.values())
    if hi == lo:
        return {key: 1.0 for key in scores}
    return {key: (value - lo) / (hi - lo) for key, value in scores.items()}


def main() -> None:
    args = parse_args()
    try:
        import numpy as np
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise SystemExit(
            "Hybrid retrieval requires optional dependencies. Install with: "
            "pip install -r requirements-hybrid.txt"
        ) from exc

    records = {record["page_id"]: record for record in read_jsonl(args.records)}
    qas = [qa for qa in read_jsonl(args.qas) if qa["page_id"] in records]
    bm25 = BM25Index.from_dict(read_json(args.bm25_index))
    dense = np.load(args.dense_index, allow_pickle=True)
    page_ids = dense["page_ids"].astype(str).tolist()
    embeddings = dense["embeddings"]
    model_name = str(dense["model"])
    model = SentenceTransformer(model_name)

    hits = 0
    for qa in qas:
        query = qa["question"]
        with trace_query(
            query,
            metadata={
                "entrypoint": "scripts/evaluate_hybrid_retrieval.py",
                "top_k": args.k,
                "alpha": args.alpha,
                "dense_model": model_name,
            },
        ):
            start = time.perf_counter()
            bm25_scores = {result.page_id: result.score for result in bm25.search(query, k=len(page_ids))}
            query_vec = model.encode([query], normalize_embeddings=True)[0]
            dense_scores = dict(zip(page_ids, embeddings @ query_vec))
            bm25_norm = minmax(bm25_scores)
            dense_norm = minmax(dense_scores)
            combined = {
                page_id: args.alpha * bm25_norm.get(page_id, 0.0)
                + (1 - args.alpha) * dense_norm.get(page_id, 0.0)
                for page_id in page_ids
            }
            ranked = sorted(combined, key=combined.get, reverse=True)[: args.k]
            log_retrieval(
                query,
                [{"page_id": page_id} for page_id in ranked],
                [combined[page_id] for page_id in ranked],
                (time.perf_counter() - start) * 1000,
            )
        hits += int(qa["page_id"] in ranked)

    total = len(qas)
    metrics = {
        "evaluated_questions": total,
        f"hits_at_{args.k}": hits,
        f"recall_at_{args.k}": hits / total if total else 0.0,
        "alpha": args.alpha,
        "dense_model": model_name,
    }
    print(metrics)
    if args.out:
        write_json(args.out, metrics)
    flush_traces()


if __name__ == "__main__":
    main()
