.PHONY: prepare demo-index vlm-index eval-demo eval-vlm app

DATASET ?= $(SCRATCH)/vlm_doc_project/docvqa_hf
OUT ?= data/docvqa_sample

prepare:
	python scripts/prepare_docvqa.py --dataset "$(DATASET)" --out "$(OUT)" --split validation --limit 500

demo-index:
	python scripts/build_index.py --records "$(OUT)/page_records.jsonl" --out "$(OUT)/index_demo.json" --include-gold-questions

vlm-index:
	python scripts/build_index.py --records "$(OUT)/vlm_page_summaries.jsonl" --out "$(OUT)/index_vlm.json" --text-field vlm_summary

eval-demo:
	python scripts/evaluate_retrieval.py --index "$(OUT)/index_demo.json" --records "$(OUT)/page_records.jsonl" --qas "$(OUT)/qa_records.jsonl" --k 5

eval-vlm:
	python scripts/evaluate_retrieval.py --index "$(OUT)/index_vlm.json" --records "$(OUT)/vlm_page_summaries.jsonl" --qas "$(OUT)/qa_records.jsonl" --k 5

app:
	streamlit run app.py
