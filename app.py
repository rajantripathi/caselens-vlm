from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.caselens.io import read_json, read_jsonl
from src.caselens.retrieval import BM25Index


st.set_page_config(page_title="CaseLens-VLM", layout="wide")
st.title("CaseLens-VLM")
st.caption("Multimodal document evidence retrieval over DocVQA page images")

data_dir = Path(st.sidebar.text_input("Data directory", "data/docvqa_sample"))
records_path = Path(st.sidebar.text_input("Records", str(data_dir / "vlm_qwen100.jsonl")))
index_path = Path(st.sidebar.text_input("Index", str(data_dir / "index_qwen100.json")))
image_root = Path(st.sidebar.text_input("Image root", str(data_dir)))

question = st.text_input("Question", "Which page contains the coffee break time?")
k = st.slider("Citations", min_value=1, max_value=10, value=5)

if not records_path.exists() or not index_path.exists():
    st.warning("Generate records and index first. Raw data is intentionally not committed to GitHub.")
    st.stop()

records = {record["page_id"]: record for record in read_jsonl(records_path)}
index = BM25Index.from_dict(read_json(index_path))

if st.button("Retrieve", type="primary"):
    results = index.search(question, k=k)
    if not results:
        st.info("No cited pages found.")
    for rank, result in enumerate(results, start=1):
        record = records[result.page_id]
        with st.container(border=True):
            st.subheader(f"{rank}. {result.page_id}  score={result.score:.3f}")
            left, right = st.columns([1, 2])
            image_path = image_root / record["image_path"]
            if image_path.exists():
                left.image(str(image_path), caption=record["image_path"], use_container_width=True)
            else:
                left.code(str(image_path))
            right.markdown("**VLM summary**")
            right.write(record.get("visual_summary", record.get("page_summary", "")))
            right.markdown("**Example ground-truth QA on this page**")
            for qa in record.get("qas", [])[:3]:
                right.write(f"- {qa['question']} -> {qa.get('answers')}")
