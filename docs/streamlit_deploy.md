# Streamlit Demo Deployment

The public Streamlit demo works without committing raw DocVQA images or generated model artifacts. It opens with verified metrics, a bundled retrieval demo, an image-upload path for user-provided document pages, and the enterprise architecture view.

The app is suitable as a no-GPU portfolio artifact. It does not rerun Qwen3-VL; it demonstrates the retrieval and reviewer workflow around bundled evidence snippets while the measured benchmark remains documented in `docs/results.md`.

## Streamlit Community Cloud

1. Create a new Streamlit app from `rajantripathi/caselens-vlm`.
2. Set the main file path to `app.py`.
3. Use the default branch `main`.
4. No secrets are required for the public demo.

The local-artifacts tab is for running the app inside the repo after generating DocVQA records and indexes on Isambard.

The upload path in the public demo previews the image and indexes the visitor's visual note. It does not run a live VLM on Streamlit Community Cloud; the production architecture maps that step to Bedrock multimodal models or a GPU-hosted VLM endpoint.

## Local Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Run the offline portfolio smoke test:

```bash
make portfolio-smoke
```

For the full local artifact mode, generate:

- `data/docvqa_sample/vlm_qwen3_8b_100.jsonl`
- `data/docvqa_sample/index_qwen3_8b_100.json`
- `data/docvqa_sample/page_images/`
