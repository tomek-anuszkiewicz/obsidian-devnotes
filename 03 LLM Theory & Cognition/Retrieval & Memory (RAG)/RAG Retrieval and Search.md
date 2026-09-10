---
title: RAG Retrieval and Search
tags:
  - rag
  - retrieval
  - vector-search
  - hybrid-search
  - reranking
  - bm25
  - semantic-search
aliases:
  - RAG Retrieval Mechanisms
  - Hybrid Search and Reranking in RAG
---

# RAG Retrieval and Search

This note covers the retrieval mechanics, search hybridity, reranking models, source authority resolution, and temporal versioning in a Retrieval-Augmented Generation (RAG) system.

It builds upon [[RAG Ingestion and Chunking Strategies]] and feeds directly into [[Advanced RAG Architectures]] and [[Introduction to RAG]].

---

## 1. Vector Search Is Not Enough

Semantic vector search (approximate nearest neighbor / ANN) is powerful for conceptual queries, but software engineering workflows frequently fail under vector search alone:

```text
Query: "CancelOrderHandler"
Vector model: Returns generic cancellation logic or order models, but misses the exact class definition.

Query: "FIN-421" or "0x7F" or "PaymentRequested"
Vector model: Semantic distance fails on exact alphanumeric tokens and identifiers.
```

Vector embeddings map text into broad semantic clusters. They are poorly suited for:
- Exact symbol and identifier lookups (`PaymentRequestedEvent`, `UserRepository`).
- Error codes and ticket keys (`JIRA-1048`, `HTTP 502`).
- Configuration keys, hexadecimal masks, and specific constants.

---

## 2. Hybrid Search Architecture

To achieve high recall and high precision, production RAG systems implement **hybrid search**, combining dense semantic vectors with sparse lexical indices and hard metadata filters.

```text
               User / Agent Query
                       │
       ┌───────────────┼───────────────┐
       ↓               ↓               ↓
 Dense Vector    Sparse Lexical    Metadata
 Similarity       Search (BM25)     Filters
 (Embeddings)    (Exact tokens)  (Repo, Branch)
       │               │               │
       └───────────────┬───────────────┘
                       ↓
           Fused Candidate Set (RRF)
                       ↓
               Reranking Model
                       ↓
             Top K Dense Context
```

### Fusion via Reciprocal Rank Fusion (RRF)
The candidate results from vector similarity and BM25 lexical search are combined using algorithms like RRF or weighted score linear combination:

$$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

where $r_m(d)$ is the rank of document $d$ in retrieval method $m$, and $k$ is a smoothing constant (typically 60).

---

## 3. Two-Stage Retrieval and Reranking

Retrieving too many documents floods the LLM context window, diluting model attention ("Lost in the Middle") and increasing token costs. Retrieving too few risks missing critical details.

The standard pattern is **two-stage retrieval**:

```text
Stage 1: Broad Retrieval (Candidate Generation)
  • Fast, scalable search across millions of chunks.
  • Retrieves top 50–100 candidates via Vector + BM25.

Stage 2: Cross-Encoder Reranking (Precision Scoring)
  • Uses a cross-encoder model (e.g. Cohere Rerank, BGE-Reranker).
  • Evaluates the deep full interaction between [Query] and [Candidate Chunk].
  • Emits top 3–7 high-signal chunks to the LLM context.
```

```text
Candidate Pool (50 items) ───[ Cross-Encoder Reranker ]───> High-Precision Context (5 items) ───> LLM Context
```

Reranking drastically improves context density and reduces hallucination rates.

---

## 4. Source Authority and Conflicting Information

In real-world repositories, different knowledge sources frequently contradict each other:

```text
Old Jira Comment (2022):       "We publish messages directly to RabbitMQ."
Architecture Doc (2023):       "System targets Apache Kafka."
Production Source Code (2026): "PublishEndpoint<PaymentProcessed> -> Azure Service Bus"
```

If a RAG system treats all chunks as equal text, the LLM may provide obsolete or contradictory recommendations.

### Authority Hierarchy
Systems should assign explicit trust scores or priority tiers based on source origin:

```text
1. Active Production Code (Ground Truth for current behavior)
2. Approved ADRs & Formal Specs (Ground Truth for architectural intent)
3. Formal Architecture Documentation
4. Closed PRs & Merge Commits (Reasoning behind past changes)
5. Jira Acceptance Criteria
6. Jira Comments & Slack/Meeting Transcripts (Lowest formal authority)
```

When sources conflict, the retrieval pipeline or context prompt should explicitly instruct the model to prioritize higher-tier sources over informal discussions.

---

## 5. Temporal Awareness and Versioning

Software knowledge is not static; it evolves across time, releases, and git branches.

A statement is rarely universally true; it is true **within a specific commit, branch, or time window**.

### Essential Temporal Metadata
To prevent mixing knowledge across distinct software eras, chunks must include:
- `valid_from` / `valid_to` timestamps
- `commit_sha` and `git_tag`
- `branch_name` (e.g., `main`, `feature/v2`)
- `version` (e.g., `v1.4.0`)

Without temporal filtering, an agent asking *"How do we configure database connections?"* could receive an answer merging a deprecated 2021 XML configuration format with a 2026 dependency injection pattern.

---

Next stage: [[Advanced RAG Architectures]] and [[Introduction to RAG]].
---

## Relationship to the Knowledge Graph

- **[[Introduction to RAG]]**: Baseline retrieval concepts.
- **[[Advanced RAG Architectures]]**: Self-reflective and speculative retrieval pipelines.
- **[[RAG Ingestion and Chunking Strategies]]**: Pre-filtering and metadata strategies to optimize retrieval latency and precision.
- **[[How Reasoning Models Explore and Evaluate Solutions]]**: Combining reasoning models with targeted vector retrieval.
- **[[How Modern LLM Systems Build Context, Reason, and Stay Constrained|Context Management and Conversational Grounding in LLM Workflows]]**: Avoiding hallucination by grounding generation in verified search hits.
