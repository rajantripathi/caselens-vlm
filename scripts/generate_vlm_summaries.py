#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from caselens.io import read_jsonl


PROMPT = """You are building page-level evidence for document question answering.
Describe the document page for retrieval. Focus on visible text, tables, forms,
dates, names, numeric values, headings, signatures, charts, and layout.
Return concise JSON with keys: visual_summary, detected_elements,
answer_relevant_text."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", required=True, help="page_records.jsonl")
    parser.add_argument("--image-root", required=True, help="Directory that image paths are relative to")
    parser.add_argument("--out", required=True)
    parser.add_argument("--model", default="Qwen/Qwen2.5-VL-3B-Instruct")
    parser.add_argument("--local-files-only", action="store_true", help="Do not call Hugging Face Hub APIs")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--mock", action="store_true", help="Generate deterministic summaries without loading a VLM")
    parser.add_argument("--max-new-tokens", type=int, default=256)
    parser.add_argument("--resume", action="store_true", help="Append missing page summaries to an existing output file")
    return parser.parse_args()


def mock_summary(record: dict[str, Any], model_name: str) -> dict[str, Any]:
    question_types = record.get("question_types", [])
    return {
        **record,
        "visual_summary": (
            f"Document page {record.get('page_no')} from {record.get('document_id')} "
            f"with evidence categories: {', '.join(question_types) or 'unknown'}."
        ),
        "detected_elements": question_types,
        "answer_relevant_text": record.get("page_summary", ""),
        "model_name": f"{model_name}-mock",
    }


def load_qwen(model_name: str, local_files_only: bool = False):
    import torch
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        local_files_only=local_files_only,
    )
    processor = AutoProcessor.from_pretrained(model_name, local_files_only=local_files_only)
    return model, processor


def qwen_summary(model, processor, image_path: Path, model_name: str, max_new_tokens: int) -> str:
    from qwen_vl_utils import process_vision_info

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": str(image_path)},
                {"type": "text", "text": PROMPT},
            ],
        }
    ]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    ).to(model.device)
    generated_ids = model.generate(**inputs, max_new_tokens=max_new_tokens)
    generated_ids_trimmed = [
        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    return processor.batch_decode(
        generated_ids_trimmed,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0]


def main() -> None:
    args = parse_args()
    records = read_jsonl(args.records)
    if args.limit:
        records = records[: args.limit]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    completed: set[str] = set()
    if args.resume and out_path.exists():
        for item in read_jsonl(out_path):
            completed.add(item["page_id"])
        records = [record for record in records if record["page_id"] not in completed]

    image_root = Path(args.image_root)

    model = processor = None
    if not args.mock:
        model, processor = load_qwen(args.model, local_files_only=args.local_files_only)

    mode = "a" if args.resume else "w"
    written = 0
    with out_path.open(mode, encoding="utf-8") as handle:
        for record in records:
            if args.mock:
                output = mock_summary(record, args.model)
            else:
                image_path = image_root / record["image_path"]
                raw_text = qwen_summary(model, processor, image_path, args.model, args.max_new_tokens)
                output = {
                    **record,
                    "visual_summary": raw_text,
                    "detected_elements": record.get("question_types", []),
                    "answer_relevant_text": raw_text,
                    "model_name": args.model,
                }
            import json

            handle.write(json.dumps(output, ensure_ascii=True) + "\n")
            handle.flush()
            written += 1
            print(f"wrote {written}/{len(records)} page_id={record['page_id']}", flush=True)

    print(
        f"Wrote {written} VLM summary records -> {args.out}"
        + (f" ({len(completed)} already completed)" if completed else "")
    )


if __name__ == "__main__":
    main()
