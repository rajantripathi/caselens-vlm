# LinkedIn Post Drafts

## Short Version

I built **CaseLens-VLM**, a multimodal document RAG project over real scanned document images from DocVQA.

Most RAG demos assume clean text. Real enterprise documents are messier: scanned pages, forms, tables, charts, handwriting, layout, and visual evidence. I wanted to build something closer to that reality and measure it properly.

What I implemented:

- Qwen2.5-VL page understanding over real DocVQA page images
- Page-level evidence summaries with cited retrieval
- BM25 retrieval over VLM-generated visual summaries
- Recall@k evaluation against DocVQA question/page labels
- Isambard GH200 GPU batch inference using Apptainer
- AWS architecture mapping for a managed enterprise version

Initial real result:

- Metadata-only Recall@5: 0.035
- Qwen2.5-VL summary Recall@5: 0.534

This was measured on 100 real DocVQA pages covering 339 questions, using a GH200 GPU on Isambard.

The main lesson: visual page understanding gives retrieval systems much better evidence than document metadata alone.

Next step: scale the benchmark, add embedding retrieval, and compare OCR-only vs VLM-assisted retrieval.

GitHub: https://github.com/rajantripathi/caselens-vlm

#GenAI #MultimodalAI #RAG #DocumentAI #AWS #HPC #VisionLanguageModels

## Technical Version

I have been working on **CaseLens-VLM**, a small but realistic multimodal document AI pipeline.

The pipeline takes real DocVQA page images, generates page-level evidence with Qwen2.5-VL, indexes those summaries, retrieves cited pages for questions, and evaluates Recall@k against DocVQA labels.

The part I found most useful was comparing retrieval modes:

- Metadata-only Recall@5: 0.035
- Qwen2.5-VL summary Recall@5: 0.534
- Demo upper-bound Recall@5: 0.988

This was measured on 100 real scanned pages and 339 questions using an NVIDIA GH200 node on Isambard.

I also added the pieces I would expect in an enterprise version: citation-level audit logs, grounding checks, an AWS architecture mapping, and a lightweight reviewer UI.

The project is not a production deployment, but it is a working implementation of the core pattern behind multimodal document intelligence: convert visual pages into evidence, retrieve with provenance, and evaluate the retrieval quality.

GitHub: https://github.com/rajantripathi/caselens-vlm
