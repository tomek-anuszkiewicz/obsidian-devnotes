## What RAG Is

**RAG — Retrieval-Augmented Generation** — is a pattern in which a language model does not answer only from its trained knowledge and current conversation context.

Instead, before generating an answer, the system retrieves additional information from an external knowledge source and adds it to the model context.

The basic flow is:

```text
question
   ↓
retrieval
   ↓
relevant context
   ↓
LLM
   ↓
answer
```

In practice, RAG can be thought of as a way to give a model access to a large body of knowledge without putting all of that knowledge into the prompt at once.

For example, an agent working on a software project may retrieve information from:
- source code,
- Git history,
- commits and pull requests,
- Jira,
- Confluence,
- SharePoint / Office 365,
- ADRs,
- API specifications,
- incident reports,
- logs and telemetry,
- meeting notes.

This makes RAG one of the main mechanisms of **context engineering** for agents.

---

## Context Minimization: Why Not Just Dump Whole Files?

Even with modern models offering context windows of 1M+ tokens, loading entire files or whole repositories into the prompt is often inefficient and detrimental:

- **Targeted context over whole files**: Instead of pulling 10 entire 2,000-line source files or a 50-page architecture PDF, RAG selects only the specific 20 lines of logic, single class method, or relevant paragraph.
- **Reducing "Lost in the Middle" and noise**: Language models reason significantly better when the prompt contains dense, high-signal information. Flooding context with thousands of lines of boilerplate, imports, and unrelated helper functions degrades reasoning and invites hallucinations.
- **Latency and cost reduction**: Passing a 1,500-token prompt is substantially faster (time-to-first-token) and drastically cheaper than repeatedly transferring 100,000+ tokens across agent iterations.
- **Headroom for agent loops**: In multi-step agent workflows, keeping retrieved fragments minimal leaves context budget open for reasoning chains, conversation history, and subsequent tool execution outputs.

```text
Naive Whole-File Ingestion:
[ File A (1,500 lines) ] + [ File B (2,500 lines) ] + [ Architecture PDF (40 pages) ]
→ Bloated context (50k+ tokens), high latency, attention dilution, noise

RAG Precision Context:
[ Function A (25 lines) ] + [ Relevant Type Interface (15 lines) ] + [ Spec Section 3.2 ]
→ Compact context (<1k tokens), focused attention, fast response, low cost
```

---

## RAG Is More Than a Vector Database

A common simplification is:

> RAG = embeddings + vector database.

This is only the simplest form. A practical RAG system contains several specialized stages across the ingestion, search, and generation pipelines:

```text
data sources
    ↓
ingestion  ──────────────────────────┐
    ↓                                │
parsing / normalization              ├──> Detailed in [[RAG Ingestion and Chunking Strategies]]
    ↓                                │
chunking                             │
    ↓                                │
metadata enrichment                  │
    ↓                                │
indexing (embeddings + lexical) ─────┘
    ↓
retrieval  ──────────────────────────┐
    ↓                                ├──> Detailed in [[RAG Retrieval and Search]]
reranking                            │
    ↓                                │
source authority & versioning ───────┘
    ↓
architectural paradigms  ────────────┐
    ↓                                ├──> Detailed in [[Advanced RAG Architectures]]
context construction & agents ───────┘
    ↓
LLM / agent
```

---

## Modular Knowledge Map

This guide is modularized into specialized references covering each phase of the architecture:

1. **[[RAG Ingestion and Chunking Strategies]]**
   - Ingestion models: Indexed batch synchronization vs. live API retrieval.
   - Layout-aware parsing and normalization (Docling, PDF tables, multi-column code blocks).
   - AST and boundary-aware chunking strategies (code, markdown, tickets).
   - Metadata enrichment schemas and embeddings generation.

2. **[[RAG Retrieval and Search]]**
   - Limitations of pure vector similarity search for exact identifiers and symbols.
   - Hybrid search architecture (Dense vectors + BM25 sparse keyword search + metadata filtering).
   - Candidate fusion via Reciprocal Rank Fusion (RRF) and cross-encoder reranking.
   - Resolving source authority conflicts (Production Code > ADRs > Tickets > Comments).
   - Temporal awareness and versioning metadata (`valid_from`, `commit_sha`, branch tracking).

3. **[[Advanced RAG Architectures]]**
   - Architectural evolution: Naive, Hybrid, Agentic, and Graph RAG.
   - Multi-hop agentic investigations and dependency-graph reasoning.
   - Constructing a unified Project Knowledge Layer for software engineering.
   - Complete on-premises / local RAG technology stacks (Docling, Qdrant, Haystack, vLLM).
   - Enterprise security: Permission-aware retrieval and chunk-level ACLs.

---

## RAG and Tools / MCP

RAG and MCP solve related but distinct problems in agent workflows:

```text
RAG
= searchable prepared memory (broad discovery across historical documents and code)

MCP / tools
= active live access to source systems (real-time verification and action)
```

For example:
- **RAG:** *"This Jira issue PAY-431 and this PR #512 introduced the retry policy."*
- **Agent via MCP:** *"I will now call the GitHub MCP server to inspect the exact current code on the main branch."*

```text
indexed knowledge (RAG)
          +
   live tools (MCP)
          ↓
   autonomous agent
```

RAG provides broad historical discovery, while live tools provide authoritative current verification.

---

## A Sensible Adoption Path

A reliable path to adopt RAG in engineering teams is to progress incrementally rather than adopting an opaque, monolithic black-box platform:

```text
v1: Basic Document Search
    Docling + Qdrant + local embeddings (SentenceTransformers)
    ↓
v2: Structured Metadata
    Add repository, branch, author, and timestamp filtering
    ↓
v3: Hybrid Search & Reranking
    Combine vector embeddings with BM25 lexical search and a cross-encoder reranker
    ↓
v4: Multi-Source Ingestion
    Index Jira tickets, Confluence ADRs, and API specifications
    ↓
v5: Codebase & Git History Integration
    Link AST-parsed code chunks with commits and pull requests
    ↓
v6: Agentic Tools & MCP Interconnect
    Expose the knowledge layer as a tool to autonomous developer agents
    ↓
v7: Knowledge Graph (Graph RAG)
    Model relationships explicitly between services, tickets, authors, and specs
```

---

## Key Takeaway

RAG should not be understood merely as:

> Search some vectors and give the results to an LLM.

A more useful definition is:

> **RAG is a mechanism for selecting the most relevant external knowledge and constructing the context needed by a model or agent to solve the current task.**

For software engineering, the ultimate objective is:

> **Build a reliable, permission-aware, temporally aware project knowledge layer that agents can explore, navigate, and verify.**