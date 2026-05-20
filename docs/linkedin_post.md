# LinkedIn Post Draft

I built **CaseLens-VLM**, a multimodal document RAG project over real scanned document images from DocVQA.

Most RAG demos assume clean text. Real enterprise documents are messier: scanned pages, forms, tables, charts, handwriting, layout, and visual evidence. I wanted to build something closer to that reality.

What I implemented:

- Qwen2.5-VL page understanding over real DocVQA page images
- Page-level evidence summaries with cited retrieval
- BM25 retrieval over VLM-generated visual summaries
- Recall@k evaluation against DocVQA question/page labels
- Isambard GH200 GPU batch inference using Apptainer
- AWS architecture mapping for a managed enterprise version

Initial real result:

- Metadata-only Recall@5: 0.145
- Qwen2.5-VL summary Recall@5: 0.605

The main lesson: visual page understanding gives retrieval systems much better evidence than document metadata alone.

Next step: scale the benchmark, add embedding retrieval, and compare OCR-only vs VLM-assisted retrieval.

GitHub: https://github.com/rajantripathi/caselens-vlm

#GenAI #MultimodalAI #RAG #DocumentAI #AWS #HPC #VisionLanguageModels
