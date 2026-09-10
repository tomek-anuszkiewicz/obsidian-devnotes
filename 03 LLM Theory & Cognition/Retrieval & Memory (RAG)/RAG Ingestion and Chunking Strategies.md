---
title: RAG Ingestion and Chunking Strategies
tags:
  - rag
  - chunking
  - data-ingestion
  - embeddings
  - document-processing
  - metadata-enrichment
aliases:
  - Chunking Strategies for RAG
  - Data Ingestion Pipeline for RAG
---

# RAG Ingestion and Chunking Strategies

This note details the data ingestion, document parsing, chunking, metadata enrichment, and embedding stages of a Retrieval-Augmented Generation (RAG) system. 

It is an atomic component of the broader [[Introduction to RAG]] architecture, feeding into [[RAG Retrieval and Search]] and [[Advanced RAG Architectures]].

---

## 1. Ingestion Approaches: Indexed vs. Live

Before data can be transformed into context, it must be ingested or accessed. Two primary patterns exist:

```text
Indexed Ingestion:
Jira / Git / Confluence ──(Batch / Changefeed)──> Ingestion Pipeline ──> RAG Vector / Hybrid Index

Live Retrieval:
Agent ──(Tool / MCP Call)──> Jira API / GitHub API / Confluence API ──> Real-time Context
```

### Indexed Ingestion
Data is periodically or continuously synced into an intermediate knowledge store.
- **Advantages:**
  - Fast, predictable retrieval latency during agent runs.
  - Enables pre-computed vector embeddings, BM25 indexing, and semantic graph construction.
  - Normalizes heterogeneous data into a unified schema.
- **Disadvantages:**
  - Synchronization overhead; potential for stale data between sync intervals.
  - Complex permission replication (access control lists must be mirrored or verified).

### Live Retrieval
The agent directly queries source systems via APIs or MCP servers at execution time.
- **Advantages:**
  - Always up-to-date information.
  - Native permission models and access controls are respected automatically.
  - No storage overhead for indexing massive repositories.
- **Disadvantages:**
  - High latency during multi-turn agent execution.
  - Multi-hop searches require multiple tool calls and consume agent context.

> [!TIP]
> **Hybrid Pattern:** Use indexed ingestion for broad discovery across large repositories, and live MCP tools for precise, immediate verification of current state.

---

## 2. Parsing and Normalization

Raw organizational documents (PDF, DOCX, PPTX, HTML, Markdown) contain complex layouts that naive text extraction destroys:
- Multi-column text
- Header and section hierarchies
- Tables and spreadsheets
- Footnotes and annotations
- Embedded code snippets, diagrams, and figures

### Structural Parsing (e.g. Docling)
Modern parsers like **Docling**, **Unstructured**, or **Apache Tika** convert unstructured binary documents into structured document graphs (e.g. Markdown or JSON-LD):

```text
PDF / Office Document
        ↓
     Docling
        ↓
Document Object Model
  ├── Title & Metadata
  ├── Headings (H1, H2, H3)
  ├── Paragraphs
  ├── Tables (preserved as Markdown/HTML tables)
  └── Code Blocks (preserved with language annotations)
```

Preserving semantic structure is essential because tables and code lose their meaning when converted to flat, unformatted strings.

---

## 3. Chunking Strategies

Large documents cannot and should not be passed into language model prompts in their entirety. They must be divided into granular units called **chunks**.

Chunking directly governs **context minimization**: by isolating exact units of logic or documentation, the retriever avoids diluting the LLM's attention with thousands of lines of irrelevant boilerplate.

### Naive Chunking vs. Semantic Chunking

| Approach | Mechanism | Failure Mode |
| :--- | :--- | :--- |
| **Fixed-Size (Naive)** | Splits every $N$ characters/tokens (e.g. 1000 tokens) with fixed overlap (e.g. 100 tokens). | Cuts sentences, methods, or table rows in half; breaks semantic meaning across boundaries. |
| **Document-Aware** | Splits along markdown headers, section boundaries, or paragraph clusters. | Preserves narrative coherence and thematic unity. |
| **Code-Aware (AST)** | Uses parsers (e.g. tree-sitter) to chunk by class, function, struct, or interface. | Preserves call boundaries, types, and method signatures intact. |
| **Issue / Ticket-Aware** | Chunks by issue description, acceptance criteria, and distinct comment threads. | Separates business requirements from ongoing developer discussions. |

```text
Code Chunking Example:
┌──────────────────────────────────────────────┐
│ Class: PaymentProcessor                      │
│ ┌──────────────────────────────────────────┐ │
│ │ Chunk 1: Interface & Constructor         │ │
│ └──────────────────────────────────────────┘ │
│ ┌──────────────────────────────────────────┐ │
│ │ Chunk 2: ProcessCreditCard() Method      │ │
│ └──────────────────────────────────────────┘ │
│ ┌──────────────────────────────────────────┐ │
│ │ Chunk 3: RefundTransaction() Method      │ │
│ └──────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

---

## 4. Metadata Enrichment

A chunk must not be raw text alone. To support precise filtering, permission checks, and temporal validation, chunks must carry rich structured metadata.

### Example: Software Engineering Metadata Schema
```json
{
  "source": "git",
  "repository": "billing-service",
  "branch": "main",
  "commit_sha": "a1b2c3d4",
  "file_path": "src/Payments/PaymentProcessor.cs",
  "language": "csharp",
  "symbol_type": "method",
  "symbol_name": "ProcessCreditCard",
  "created_at": "2025-04-12T10:15:00Z",
  "updated_at": "2026-01-20T14:32:00Z",
  "acl_groups": ["eng-core", "billing-devs"]
}
```

Metadata enables:
- Filtering results before or after vector similarity search.
- Scoping searches to specific repositories, branches, or tenants.
- Discarding outdated versions or historical branches.

---

## 5. Embeddings Generation

Embeddings transform textual and code chunks into continuous high-dimensional vector representations:

```text
"Retry failed payment transaction" 
         ↓
  Embedding Model (e.g., SentenceTransformers, text-embedding-3)
         ↓
  [ 0.0412, -0.2185, 0.7819, ... ] (1536-dimensional vector)
```

- **Semantic Proximity:** Chunks with conceptually similar meaning yield high cosine similarity, even if they share few literal keywords.
- **Local vs. Cloud Models:** For sensitive enterprise code, embeddings can be generated entirely on-premises using local embedding models (e.g. `bge-large`, `nomic-embed-text`) running via Ollama, vLLM, or Hugging Face runtimes.

Next stage in the pipeline: [[RAG Retrieval and Search]].
---

## Relationship to the Knowledge Graph

- **[[Introduction to RAG]]**: The core RAG pipeline overview.
- **[[Advanced RAG Architectures]]**: Hierarchical and multi-representation chunking for complex documents.
- **[[RAG Retrieval and Search]]**: Indexing chunk vectors and metadata for precision retrieval.
- **[[How Modern LLM Systems Build Context, Reason, and Stay Constrained]]**: Preparing structured context chunks that fit model attention patterns.
- **[[AI-Generated Architectural Documentation from Code]]**: Structuring code-generated architecture docs for high-precision retrieval.
