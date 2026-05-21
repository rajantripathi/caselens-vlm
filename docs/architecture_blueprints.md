# Architecture Blueprints

These diagrams are designed for recruiters, interviewers, and LinkedIn readers. They show the same idea at three levels: the implemented open-source project, a DialogXR-style enterprise deployment, and an AWS managed-service deployment.

## 1. Open-Source CaseLens Topology

This is the architecture implemented in this repository.

```mermaid
flowchart LR
    user["Reviewer or evaluator"] --> ui["Streamlit demo"]

    subgraph ingress["INPUTS"]
        docs["DocVQA scanned pages"]
        upload["Uploaded demo image"]
        questions["DocVQA questions"]
    end

    subgraph processing["DOCUMENT PROCESSING"]
        export["Page export"]
        metadata["Metadata and QA records"]
        qwen3["Qwen3-VL summaries"]
    end

    subgraph retrieval["RETRIEVAL AND QA"]
        bm25["BM25 lexical index"]
        minilm["MiniLM dense vectors"]
        hybrid["Hybrid score fusion"]
        cited["Cited page retrieval"]
    end

    subgraph governance["EVALUATION AND GOVERNANCE"]
        recall["Recall metrics"]
        audit["Citation audit"]
        limits["Limitations and model notes"]
    end

    docs --> export --> metadata
    metadata --> qwen3
    upload --> ui
    qwen3 --> bm25
    qwen3 --> minilm
    bm25 --> hybrid
    minilm --> hybrid
    questions --> cited
    hybrid --> cited --> ui
    cited --> recall
    cited --> audit
    recall --> limits

    classDef input fill:#E0F2FE,stroke:#0284C7,color:#0F172A
    classDef process fill:#ECFDF5,stroke:#059669,color:#0F172A
    classDef retrieval fill:#FEF3C7,stroke:#D97706,color:#0F172A
    classDef gov fill:#F3E8FF,stroke:#7C3AED,color:#0F172A
    class docs,upload,questions,user input
    class export,metadata,qwen3,ui process
    class bm25,minilm,hybrid,cited retrieval
    class recall,audit,limits gov
```

**How to explain it:** CaseLens turns scanned pages into evidence records, uses VLMs to describe visual content, retrieves cited pages, and evaluates whether retrieval improves over metadata-only search.

## 2. DialogXR-Style Enterprise Topology

This version maps the same project pattern to a healthcare/public-sector style platform with trust zones, identity, observability, and human review.

```mermaid
flowchart LR
    client["Practitioner or case worker"] --> gateway["API gateway"]

    subgraph dmz["DMZ"]
        ingress["Ingress nginx"]
        frontend["Reviewer web app"]
    end

    subgraph identity["IDENTITY"]
        keycloak["OIDC and SSO"]
        opa["Policy checks"]
    end

    subgraph appzone["APPLICATION ZONE"]
        api["FastAPI backend"]
        orchestrator["RAG orchestrator"]
        pii["PII redaction"]
        parser["Parser and OCR"]
        vlm["VLM page understanding"]
        embed["Embedding worker"]
        retrieve["Hybrid retriever"]
        rerank["Reranker"]
        guardrail["Guardrail service"]
        evals["Evaluation worker"]
    end

    subgraph datazone["DATA ZONE"]
        object["Object store"]
        vector["Vector DB"]
        postgres["PostgreSQL metadata"]
        redis["Redis sessions"]
        audit["Audit WORM archive"]
    end

    subgraph observe["OBSERVABILITY"]
        metrics["Prometheus and Grafana"]
        traces["Langfuse traces"]
        logs["Loki or CloudWatch logs"]
    end

    client --> ingress --> gateway --> frontend --> api
    frontend --> keycloak
    api --> opa
    api --> orchestrator
    orchestrator --> pii --> parser --> vlm
    parser --> object
    vlm --> object
    vlm --> embed --> vector
    orchestrator --> retrieve --> vector
    retrieve --> rerank --> guardrail --> frontend
    guardrail --> audit
    orchestrator --> postgres
    api --> redis
    evals --> vector
    evals --> postgres
    api --> metrics
    orchestrator --> traces
    guardrail --> logs

    classDef zone fill:#F8FAFC,stroke:#64748B,stroke-dasharray: 6 4,color:#0F172A
    classDef app fill:#E0F2FE,stroke:#0284C7,color:#0F172A
    classDef data fill:#FEF3C7,stroke:#D97706,color:#0F172A
    classDef guard fill:#F3E8FF,stroke:#7C3AED,color:#0F172A
    classDef obs fill:#ECFDF5,stroke:#059669,color:#0F172A
    class ingress,gateway,frontend,api,orchestrator,pii,parser,vlm,embed,retrieve,rerank,evals app
    class object,vector,postgres,redis,audit data
    class keycloak,opa,guardrail guard
    class metrics,traces,logs obs
```

**How to explain it:** This is the version you would propose for DialogXR-like work: secure practitioner access, policy checks, PII handling, VLM-assisted evidence extraction, hybrid retrieval, guardrails, immutable audit, and monitoring.

## 3. AWS Managed-Service Topology

This version maps the pipeline to AWS services that are relevant to GenAI and the AWS AI Practitioner / GenAI certification story.

```mermaid
flowchart LR
    user["Reviewer"] --> cloudfront["CloudFront"]
    cloudfront --> amplify["Amplify or Streamlit app"]
    amplify --> apigw["API Gateway"]
    apigw --> ecs["ECS or Lambda API"]

    subgraph storage["SECURE STORAGE"]
        s3raw["S3 raw documents"]
        s3evidence["S3 evidence records"]
        s3audit["S3 audit archive"]
    end

    subgraph processing["PROCESSING"]
        stepfn["Step Functions"]
        batch["AWS Batch or ECS workers"]
        textract["Textract or Bedrock Data Automation"]
        bedrockvlm["Bedrock multimodal model"]
    end

    subgraph retrieval["RETRIEVAL"]
        kb["Bedrock Knowledge Bases"]
        opensearch["OpenSearch Serverless"]
        reranker["Bedrock reranker"]
    end

    subgraph safety["SAFETY AND GOVERNANCE"]
        guardrails["Bedrock Guardrails"]
        reasoning["Automated Reasoning checks"]
        iam["IAM and KMS"]
    end

    subgraph ops["OPERATIONS"]
        cloudwatch["CloudWatch metrics and logs"]
        cloudtrail["CloudTrail"]
        eval["Golden evaluation set"]
    end

    ecs --> stepfn
    stepfn --> batch
    batch --> s3raw
    batch --> textract
    batch --> bedrockvlm
    textract --> s3evidence
    bedrockvlm --> s3evidence
    s3evidence --> kb
    kb --> opensearch
    ecs --> kb
    kb --> reranker
    reranker --> guardrails
    guardrails --> reasoning
    guardrails --> amplify
    guardrails --> s3audit
    iam --> s3raw
    iam --> s3evidence
    iam --> s3audit
    ecs --> cloudwatch
    stepfn --> cloudwatch
    cloudtrail --> s3audit
    eval --> kb

    classDef edge fill:#DBEAFE,stroke:#2563EB,color:#0F172A
    classDef storage fill:#FEF3C7,stroke:#D97706,color:#0F172A
    classDef process fill:#ECFDF5,stroke:#059669,color:#0F172A
    classDef safety fill:#F3E8FF,stroke:#7C3AED,color:#0F172A
    classDef ops fill:#F1F5F9,stroke:#64748B,color:#0F172A
    class user,cloudfront,amplify,apigw,ecs edge
    class s3raw,s3evidence,s3audit,opensearch,kb storage
    class stepfn,batch,textract,bedrockvlm,reranker process
    class guardrails,reasoning,iam safety
    class cloudwatch,cloudtrail,eval ops
```

**How to explain it:** This is the managed version: S3 for documents, Textract or Bedrock Data Automation for extraction, Bedrock multimodal models for visual evidence, Bedrock Knowledge Bases and OpenSearch for retrieval, Bedrock Guardrails for grounding and policy checks, and CloudWatch/CloudTrail/S3 for observability and audit.

## Design Decisions to Defend

| Decision | Why it matters |
| --- | --- |
| Page-level evidence records | Keeps citations stable and reviewable |
| Hybrid retrieval | Combines exact lexical matches with semantic similarity |
| Human-in-the-loop review | Avoids autonomous decisions in sensitive workflows |
| Guardrails after retrieval | Checks generated answers against retrieved evidence |
| Immutable audit archive | Supports compliance, incident review, and model governance |
| Golden evaluation set | Prevents model or prompt changes from silently degrading retrieval |

## Sources

- Amazon Bedrock multimodal Knowledge Bases: https://docs.aws.amazon.com/bedrock/latest/userguide/kb-multimodal.html
- Amazon Bedrock Guardrails contextual grounding: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-contextual-grounding-check.html
- Amazon Bedrock Automated Reasoning checks: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-automated-reasoning-checks.html
- Amazon Bedrock reranking: https://docs.aws.amazon.com/en_us/bedrock/latest/userguide/rerank-use.html
