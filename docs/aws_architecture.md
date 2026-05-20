# AWS Architecture Mapping

CaseLens-VLM runs on Isambard for this portfolio version, but the same pattern maps cleanly to AWS managed services.

| CaseLens component | AWS equivalent |
| --- | --- |
| DocVQA/page images on scratch | Amazon S3 |
| VLM page summaries | Amazon Bedrock multimodal model |
| OCR or structured extraction | Amazon Textract or Bedrock Data Automation |
| JSONL page evidence | S3 + AWS Glue Data Catalog |
| Retrieval index | Amazon OpenSearch Serverless or Aurora PostgreSQL with pgvector |
| Batch orchestration | AWS Step Functions + AWS Batch/ECS |
| API and UI | API Gateway + Lambda/ECS + Amplify/Streamlit |
| Logs and monitoring | Amazon CloudWatch |

## Production Flow

1. Upload document images or PDFs to S3.
2. Convert PDFs to page images and run OCR/extraction.
3. Generate VLM page summaries and detected evidence fields.
4. Embed page evidence and write to a vector index.
5. Answer user questions with retrieved page citations.
6. Log retrieval quality, cited pages, and human feedback for monitoring.

## Certification Story

This project demonstrates the architecture behind an enterprise GenAI document intelligence workload: multimodal ingestion, foundation model inference, retrieval-augmented generation, orchestration, and monitoring.
