# Streamlit Demo Deployment

The public Streamlit demo works without committing raw DocVQA images or generated model artifacts. It opens with verified metrics, a small bundled retrieval demo, and the enterprise architecture view.

## Streamlit Community Cloud

1. Create a new Streamlit app from `rajantripathi/caselens-vlm`.
2. Set the main file path to `app.py`.
3. Use the default branch `main`.
4. No secrets are required for the public demo.

The local-artifacts tab is for running the app inside the repo after generating DocVQA records and indexes on Isambard.

## Local Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

For the full local artifact mode, generate:

- `data/docvqa_sample/vlm_qwen3_8b_100.jsonl`
- `data/docvqa_sample/index_qwen3_8b_100.json`
- `data/docvqa_sample/page_images/`
