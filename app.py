from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image
import streamlit as st

from src.caselens.io import read_json, read_jsonl
from src.caselens.retrieval import BM25Index


RESULTS = [
    {
        "Mode": "Metadata-only",
        "Pages": 100,
        "Questions": 339,
        "Recall@1": "0.003",
        "Recall@5": "0.035",
    },
    {
        "Mode": "Qwen2.5-VL summaries",
        "Pages": 100,
        "Questions": 339,
        "Recall@1": "0.363",
        "Recall@5": "0.534",
    },
    {
        "Mode": "Qwen2.5-VL hybrid",
        "Pages": 100,
        "Questions": 339,
        "Recall@1": "not measured",
        "Recall@5": "0.587",
    },
    {
        "Mode": "Qwen3-VL summaries",
        "Pages": 100,
        "Questions": 339,
        "Recall@1": "0.445",
        "Recall@5": "0.658",
    },
    {
        "Mode": "Qwen3-VL hybrid",
        "Pages": 100,
        "Questions": 339,
        "Recall@1": "not measured",
        "Recall@5": "0.708",
    },
]


DEMO_RECORDS: list[dict[str, Any]] = [
    {
        "page_id": "fgbd0079_p7",
        "document_id": "fgbd0079",
        "page_no": "7",
        "image_path": "page_images/fgbd0079_p7.png",
        "question_types": ["form", "handwritten", "layout"],
        "page_summary": "Handwritten CSF run sheet with production fields and numeric values.",
        "visual_summary": (
            "A handwritten CSF Run Sheet with fields for date, PD, CSF, run numbers, "
            "net pounds infeed, and net pounds out. Qwen3-VL identified PD- 5960 C, "
            "CSF- 721, net pounds infeed 584, net pounds out 487, and 83.4%."
        ),
        "detected_elements": ["handwritten form", "numeric values", "production run sheet"],
        "qas": [
            {
                "question": "What is the PD?",
                "answers": ["5960 C"],
            },
            {
                "question": "What is the percentage of net pounds out over net pounds infeed?",
                "answers": ["83.4%"],
            },
        ],
    },
    {
        "page_id": "fkpj0226_p2",
        "document_id": "fkpj0226",
        "page_no": "2",
        "image_path": "page_images/fkpj0226_p2.png",
        "question_types": ["free_text", "layout"],
        "page_summary": "PepsiCo annual meeting notice with company, meeting, and agenda details.",
        "visual_summary": (
            "A PepsiCo notice of annual meeting of shareholders. The page contains the "
            "PepsiCo heading, meeting date of May 3, 2006, location at 7701 Legacy Drive "
            "in Plano, Texas, agenda items, voting details, and a signature block."
        ),
        "detected_elements": ["company letterhead", "meeting notice", "agenda"],
        "qas": [
            {
                "question": "What is the name of the company in the letterhead?",
                "answers": ["PEPSICO"],
            },
            {
                "question": "When is the meeting held?",
                "answers": ["May 3, 2006"],
            },
        ],
    },
    {
        "page_id": "medical_plan_p4",
        "document_id": "medical_plan",
        "page_no": "4",
        "image_path": "page_images/medical_plan_p4.png",
        "question_types": ["table", "free_text"],
        "page_summary": "Medical communications planning page with budget and table-like evidence.",
        "visual_summary": (
            "A communications planning page with budget fields, timeline notes, and "
            "table-like sections. The page is relevant for questions about financial "
            "figures, campaign planning, responsible teams, and dated milestones."
        ),
        "detected_elements": ["budget table", "timeline", "planning notes"],
        "qas": [
            {
                "question": "Which page contains budget evidence?",
                "answers": ["medical_plan_p4"],
            }
        ],
    },
    {
        "page_id": "vasomotor_table_p12",
        "document_id": "vasomotor_table",
        "page_no": "12",
        "image_path": "page_images/vasomotor_table_p12.png",
        "question_types": ["table", "medical"],
        "page_summary": "Table of vasomotor symptom treatments and adverse effects.",
        "visual_summary": (
            "A structured table comparing vasomotor symptom treatments. It includes "
            "treatment names, effectiveness notes, adverse-effect columns, and clinical "
            "comparison text useful for table-grounded retrieval."
        ),
        "detected_elements": ["clinical table", "treatment names", "adverse effects"],
        "qas": [
            {
                "question": "Which page has treatment and adverse-effect columns?",
                "answers": ["vasomotor_table_p12"],
            }
        ],
    },
]


def build_index(records: list[dict[str, Any]]) -> BM25Index:
    return BM25Index.from_records(records, text_field="vlm_summary")


def uploaded_image_record(uploaded_file, visual_note: str) -> dict[str, Any] | None:
    if uploaded_file is None:
        return None
    image_bytes = uploaded_file.getvalue()
    image = Image.open(uploaded_file)
    width, height = image.size
    summary = visual_note.strip() or (
        "User-uploaded document image. In a production deployment this page would be sent "
        "through OCR/layout extraction and a VLM to generate searchable evidence."
    )
    return {
        "page_id": "uploaded_page",
        "document_id": "uploaded_document",
        "page_no": "uploaded",
        "image_path": uploaded_file.name,
        "image_width": width,
        "image_height": height,
        "question_types": ["uploaded_image", "visual_evidence"],
        "page_summary": summary,
        "visual_summary": (
            f"Uploaded image evidence, {width}x{height} pixels. {summary} "
            "This record is included in retrieval to demonstrate the multimodal ingestion path."
        ),
        "detected_elements": ["uploaded image", "document page"],
        "qas": [
            {
                "question": "What did the user upload?",
                "answers": [uploaded_file.name],
            }
        ],
        "_uploaded_image": image_bytes,
    }


def render_metrics() -> None:
    st.subheader("Verified Retrieval Results")
    cols = st.columns(4)
    cols[0].metric("Best Recall@5", "0.708", "+0.673 vs metadata")
    cols[1].metric("Evaluated questions", "339")
    cols[2].metric("Document pages", "100")
    cols[3].metric("Qwen3 runtime", "30m42s")
    st.table(RESULTS)


def render_record(result_rank: int, result, record: dict[str, Any], image_root: Path | None = None) -> None:
    with st.container(border=True):
        st.markdown(f"#### {result_rank}. `{result.page_id}`")
        score_col, type_col, page_col = st.columns(3)
        score_col.metric("BM25 score", f"{result.score:.3f}")
        type_col.write("**Evidence type**")
        type_col.write(", ".join(record.get("question_types", [])) or "unknown")
        page_col.write("**Page**")
        page_col.write(record.get("page_no", "unknown"))

        left, right = st.columns([1, 2])
        image_path = image_root / record["image_path"] if image_root else None
        if record.get("_uploaded_image"):
            left.image(record["_uploaded_image"], caption=record["image_path"], use_container_width=True)
        elif image_path and image_path.exists():
            left.image(str(image_path), caption=record["image_path"], use_container_width=True)
        else:
            left.info("Image omitted from the public demo. The local app shows page images when DocVQA artifacts are available.")

        right.markdown("**VLM evidence summary**")
        right.write(record.get("visual_summary", record.get("page_summary", "")))
        right.markdown("**Example ground-truth QA**")
        for qa in record.get("qas", [])[:3]:
            right.write(f"- {qa['question']} -> {qa.get('answers')}")


def demo_retrieval() -> None:
    st.subheader("Live Retrieval Demo")
    st.caption(
        "This public demo uses bundled evidence snippets derived from the real DocVQA/Qwen3 run. "
        "You can also upload an image to exercise the multimodal ingestion path."
    )
    upload_col, note_col = st.columns([1, 2])
    uploaded_file = upload_col.file_uploader(
        "Upload a document image",
        type=["png", "jpg", "jpeg"],
        help="The public demo previews the image and indexes your note. The production path would run OCR and VLM inference.",
    )
    visual_note = note_col.text_area(
        "Visual evidence note for uploaded image",
        value="",
        placeholder="Example: invoice page with supplier name, total amount, date, and line-item table",
        height=96,
    )

    records_for_demo = list(DEMO_RECORDS)
    upload_record = uploaded_image_record(uploaded_file, visual_note)
    if upload_record:
        records_for_demo.insert(0, upload_record)
        st.info(
            "Uploaded image added as a retrievable evidence record. "
            "For the GitHub demo, the note stands in for live VLM/OCR inference."
        )

    examples = [
        "What is the PD?",
        "Which page mentions the PepsiCo annual meeting?",
        "Which page contains adverse-effect columns?",
        "Where is budget evidence mentioned?",
        "What did I upload?",
    ]
    question = st.selectbox("Try a question", examples)
    custom = st.text_input("Or enter your own question", "")
    query = custom.strip() or question
    k = st.slider("Cited pages", min_value=1, max_value=4, value=3, key="demo_k")

    index = build_index(records_for_demo)
    records = {record["page_id"]: record for record in records_for_demo}
    results = index.search(query, k=k)

    st.markdown("**Retrieved evidence**")
    if not results:
        st.info("No evidence found. Try a more document-specific query.")
        return
    for rank, result in enumerate(results, start=1):
        render_record(rank, result, records[result.page_id])


def local_artifacts() -> None:
    st.subheader("Local Isambard Artifacts")
    st.caption("Use this mode when running the app in the repo with generated DocVQA artifacts available.")
    data_dir = Path(st.text_input("Data directory", "data/docvqa_sample"))
    records_path = Path(st.text_input("Records", str(data_dir / "vlm_qwen3_8b_100.jsonl")))
    index_path = Path(st.text_input("Index", str(data_dir / "index_qwen3_8b_100.json")))
    image_root = Path(st.text_input("Image root", str(data_dir)))
    question = st.text_input("Question", "What is the PD?", key="local_question")
    k = st.slider("Citations", min_value=1, max_value=10, value=5, key="local_k")

    if not records_path.exists() or not index_path.exists():
        st.warning("Local records or index were not found. Use the public demo tab, or generate artifacts on Isambard first.")
        return

    records = {record["page_id"]: record for record in read_jsonl(records_path)}
    index = BM25Index.from_dict(read_json(index_path))
    if st.button("Retrieve local evidence", type="primary"):
        results = index.search(question, k=k)
        if not results:
            st.info("No cited pages found.")
        for rank, result in enumerate(results, start=1):
            render_record(rank, result, records[result.page_id], image_root=image_root)


def architecture() -> None:
    st.subheader("Enterprise Reference Architecture")
    st.markdown(
        """
```mermaid
flowchart LR
    A["PDFs and scanned pages"] --> B["Page extraction"]
    B --> C["OCR and layout"]
    B --> D["VLM page understanding"]
    C --> E["Evidence records"]
    D --> E
    E --> F["BM25 and vector indexes"]
    F --> G["Retriever and reranker"]
    G --> H["Cited answer generation"]
    H --> I["Grounding guardrails"]
    I --> J["Reviewer UI and audit log"]
```
"""
    )
    st.markdown(
        """
**AWS mapping:** S3 for document storage, Textract or Bedrock Data Automation for OCR/layout,
Bedrock or SageMaker for multimodal model inference, OpenSearch Serverless or Aurora pgvector
for retrieval, Step Functions or Batch for orchestration, Bedrock Guardrails for grounding checks,
and CloudWatch/S3 for monitoring and audit archives.
"""
    )


def main() -> None:
    st.set_page_config(page_title="CaseLens-VLM", layout="wide")
    st.title("CaseLens-VLM")
    st.caption("Enterprise multimodal document intelligence with VLMs, hybrid retrieval, citations, and audit controls.")

    tab_results, tab_demo, tab_architecture, tab_local = st.tabs(
        ["Results", "Live demo", "Architecture", "Local artifacts"]
    )
    with tab_results:
        render_metrics()
    with tab_demo:
        demo_retrieval()
    with tab_architecture:
        architecture()
    with tab_local:
        local_artifacts()


if __name__ == "__main__":
    main()
