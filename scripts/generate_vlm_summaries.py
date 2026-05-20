#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from caselens.io import read_jsonl, write_jsonl


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
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--mock", action="store_true", help="Generate deterministic summaries without loading a VLM")
    parser.add_argument("--max-new-tokens", type=int, default=256)
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


def load_qwen(model_name: str):
    import torch
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    processor = AutoProcessor.from_pretrained(model_name)
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

    image_root = Path(args.image_root)
    outputs: list[dict[str, Any]] = []

    model = processor = None
    if not args.mock:
        model, processor = load_qwen(args.model)

    for record in records:
        if args.mock:
            outputs.append(mock_summary(record, args.model))
            continue
        image_path = image_root / record["image_path"]
        raw_text = qwen_summary(model, processor, image_path, args.model, args.max_new_tokens)
        outputs.append(
            {
                **record,
                "visual_summary": raw_text,
                "detected_elements": record.get("question_types", []),
                "answer_relevant_text": raw_text,
                "model_name": args.model,
            }
        )

    write_jsonl(args.out, outputs)
    print(f"Wrote {len(outputs)} VLM summary records -> {args.out}")


if __name__ == "__main__":
    main()
