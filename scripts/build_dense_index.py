#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from caselens.io import read_jsonl
from caselens.retrieval import evidence_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--text-field", choices=["metadata", "vlm_summary"], default="vlm_summary")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        import numpy as np
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise SystemExit(
            "Dense indexing requires optional dependencies. Install with: "
            "pip install -r requirements-hybrid.txt"
        ) from exc

    records = read_jsonl(args.records)
    page_ids = [record["page_id"] for record in records]
    texts = [evidence_text(record, text_field=args.text_field) for record in records]
    model = SentenceTransformer(args.model)
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out,
        page_ids=np.array(page_ids),
        embeddings=np.asarray(embeddings, dtype="float32"),
        model=np.array(args.model),
        text_field=np.array(args.text_field),
    )
    print(f"Indexed {len(page_ids)} dense vectors -> {out}")


if __name__ == "__main__":
    main()
