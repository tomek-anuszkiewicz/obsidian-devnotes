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

This is only the simplest form.

A practical RAG system usually contains several stages:

```text
data sources
    ↓
ingestion
    ↓
parsing / normalization
    ↓
chunking
    ↓
metadata enrichment
    ↓
indexing
    ↓
retrieval
    ↓
reranking
    ↓
context construction
    ↓
LLM / agent
```

Different tools may implement only one of these layers.

For example, **Docling** is mainly useful for parsing and structuring documents. It is not itself a complete RAG platform.

---

# Typical RAG Layers

## 1. Data sources

Knowledge may come from many systems:

```text
Git repositories
Jira
Confluence
SharePoint
Office documents
wikis
databases
logs
telemetry
tickets
meeting transcripts
```

Different sources describe different aspects of the system.

For example:

```text
code
→ how the system works now

Git history
→ how it changed

PR / commit
→ why a change was introduced

Jira
→ business requirement and discussion

ADR / architecture docs
→ intended architectural reasoning
```

The strongest RAG systems combine these perspectives rather than treating all sources as equivalent text.

---

## 2. Ingestion

Data first needs to be imported or accessed.

There are two broad approaches.

### Indexed ingestion

Data is periodically copied into the knowledge system:

```text
Jira
Git
Confluence
   ↓
RAG index
```

Advantages:

- fast retrieval,
    
- unified search,
    
- embeddings can be prepared in advance,
    
- metadata can be normalized.
    

Disadvantages:

- synchronization is required,
    
- permissions must be replicated,
    
- indexed information may become stale.
    

### Live retrieval

The agent directly queries the original system through an API, MCP server or another tool.

```text
agent
 ↓
Jira API
GitHub API
Confluence API
```

Advantages:

- current data,
    
- original permissions can often be respected,
    
- no need to index everything.
    

Disadvantages:

- slower,
    
- the agent must know what to search for,
    
- multiple tool calls may be necessary.
    

In practice, both approaches can be combined.

---

# RAG and Tools / MCP

RAG and MCP solve related but different problems.

A useful distinction is:

```text
RAG
= searchable prepared memory

MCP / tools
= active access to source systems
```

For example:

```text
RAG:
"This Jira issue and this PR are probably relevant."

Agent:
"I will now retrieve the exact issue and inspect the current code."
```

This leads to an effective architecture:

```text
indexed knowledge
       +
live tools
       ↓
     agent
```

RAG provides broad discovery, while tools provide precise verification.

---

# Parsing and Normalization

Documents cannot always be indexed directly.

PDF, DOCX, PPTX or HTML may contain:

- tables,
    
- headers,
    
- footnotes,
    
- multiple columns,
    
- code examples,
    
- images,
    
- diagrams,
    
- nested sections.
    

A parser such as **Docling** converts these formats into a structured representation that can later be chunked and indexed.

Example:

```text
PDF
 ↓
Docling
 ↓
document structure
 ├─ title
 ├─ section
 ├─ paragraph
 ├─ table
 └─ code block
```

Preserving structure is often more useful than extracting plain text.

---

# Chunking

Large documents normally cannot be retrieved as a single object.

They are divided into smaller pieces called **chunks**.

This is also what enables **context minimization**: by chunking documents into granular units, the system only pools the exact relevant snippet into the LLM's context window instead of dragging in the entire file.

A naive system may simply split every N tokens:

```text
1000 tokens
1000 tokens
1000 tokens
```

A better system respects semantic boundaries.

For documentation:

```text
section
subsection
paragraph group
table
```

For code:

```text
class
method
interface
namespace
module
```

For Jira:

```text
description
acceptance criteria
comment thread
```

Good chunking is one of the most important factors affecting RAG quality.

---

# Metadata

Chunks should not contain only text.

They should also carry metadata.

For example:

```json
{
  "source": "jira",
  "project": "PAY",
  "issue": "PAY-431",
  "component": "payments",
  "created": "2026-01-18",
  "updated": "2026-07-03"
}
```

For code:

```json
{
  "repository": "billing",
  "branch": "main",
  "file": "PaymentService.cs",
  "symbol": "AuthorizePayment",
  "language": "C#"
}
```

Metadata enables filtering and gives the agent additional context.

It also becomes important for:

- permissions,
    
- time,
    
- source authority,
    
- project boundaries,
    
- versions.
    

---

# Embeddings

Embeddings convert text into numerical vectors representing semantic similarity.

Conceptually:

```text
"retry failed payment"
        ↓
embedding model
        ↓
[0.17, -0.42, 0.81, ...]
```

Documents with similar meaning tend to produce vectors that are close to each other.

This enables semantic queries such as:

> Where is failed payment retry handled?

even if the exact phrase never occurs in the source material.

Embeddings can be generated locally using models such as SentenceTransformers or through local model runtimes.

---

# Vector Search Is Not Enough

Semantic search is useful but exact search remains essential.

For example:

```text
PaymentRequested
CancelOrderHandler
FIN-421
```

are identifiers for which exact keyword search is often better than semantic similarity.

Therefore a common architecture uses **hybrid search**:

```text
vector search
+
keyword / BM25 search
+
metadata filters
```

Example:

```text
semantic:
"failed payment retry"

keyword:
PaymentRequested

filters:
repository = billing
branch = main
```

Hybrid retrieval is usually a better default for software engineering knowledge than vector search alone.

---

# Reranking

Initial retrieval may return many approximately relevant results.

A second model or scoring mechanism can rank them again.

```text
50 search results
      ↓
reranker
      ↓
5 best results
      ↓
LLM context
```

This prevents the context window from being filled with weakly related information.

---

# Source Authority

Not every source should be trusted equally.

For example:

```text
current code
approved ADR
API specification
architecture documentation
Jira acceptance criteria
PR description
commit message
Jira comment
meeting note
```

may have very different authority.

If two sources disagree, the system should ideally know which one is more likely to represent the current truth.

For example:

```text
old Jira comment:
"We use RabbitMQ."

current code:
"Azure Service Bus"
```

RAG should not treat these statements as equally authoritative.

---

# Time and Versioning

Software knowledge is temporal.

A system may have used:

```text
2022 → RabbitMQ
2024 → Azure Service Bus
2026 → Kafka
```

All three statements may be correct, but only for different periods.

Therefore useful metadata may include:

```text
created_at
updated_at
valid_from
valid_to
commit_sha
branch
release
version
```

Without temporal awareness, RAG can easily combine knowledge from different generations of the system.

---

# Main Classes of RAG Systems

## Naive RAG

```text
documents
 ↓
chunks
 ↓
embeddings
 ↓
vector DB
 ↓
LLM
```

Useful for basic semantic document search.

---

## Hybrid RAG

```text
vector search
+
keyword search
+
metadata filtering
+
reranking
```

A strong general-purpose architecture.

---

## Agentic RAG

Retrieval becomes a multi-step process controlled by an agent.

Example:

```text
search code
   ↓
find suspicious service
   ↓
search Jira
   ↓
find ticket
   ↓
search Git history
   ↓
read ADR
   ↓
answer
```

The system does not perform one retrieval operation but investigates the problem iteratively.

---

## Graph RAG

Knowledge is represented not only as documents but also as relationships.

For example:

```text
PaymentService
   ↓ changed by
commit 92ab12
   ↓ belongs to
PR #481
   ↓ implements
PAY-133
   ↓ documented in
ADR-18
```

This can be particularly useful for software engineering because the underlying knowledge already forms a natural graph.

---

# RAG for Software Engineering

A project knowledge system could combine:

```text
Code
│
├─ calls
├─ implements
├─ publishes
└─ depends on

Git
│
├─ commit
├─ PR
└─ author

Jira
│
├─ requirement
├─ bug
├─ epic
└─ discussion

Docs
│
├─ ADR
├─ architecture
├─ API specification
└─ runbook
```

This makes it possible to answer questions such as:

> How does this feature work?

> Why was this implemented this way?

> When was this behavior introduced?

> Which Jira issue led to this code?

> Is the architecture documentation still consistent with the implementation?

> Which previous change is most similar to the feature I am implementing?

---

# RAG as a Project Knowledge Layer

For agent-based development, it may be useful to think beyond the term RAG itself.

Instead of:

> We have a vector database.

the goal can be:

> We have a project knowledge layer that agents can query.

Conceptually:

```text
                    Agent
                      │
               Context Planner
                      │
        ┌─────────────┼─────────────┐
        │             │             │
     Search         Graph        MCP / Tools
        │             │             │
        └─────────────┼─────────────┘
                      ↓
              Project Knowledge
```

The agent can then combine:

- semantic retrieval,
    
- keyword search,
    
- graph traversal,
    
- metadata filtering,
    
- direct source-system queries.
    

RAG becomes one part of a broader context architecture.

---

# Example Local RAG Stack

A simple local experimental stack could be:

```text
PDF / DOCX / HTML
        ↓
      Docling
        ↓
chunking + metadata
        ↓
SentenceTransformers
        ↓
      Qdrant
        ↓
      Haystack
        ↓
   Ollama / vLLM
```

Possible alternatives include:

```text
Parsing:
Docling
Unstructured
Apache Tika

Search:
Qdrant
OpenSearch
Weaviate
Milvus
pgvector

RAG orchestration:
Haystack
LlamaIndex
LangChain

Local model serving:
Ollama
vLLM

Graph:
Neo4j
GraphRAG

End-to-end platforms:
RAGFlow
AnythingLLM
Open WebUI
```

All major parts of such a stack can be self-hosted.

This is useful when company source code, Jira issues or internal documentation must not leave the organization's infrastructure.

---

# Security

Self-hosting solves only part of the security problem.

A major requirement is **permission-aware retrieval**.

If the knowledge base contains:

```text
source code
HR documents
contracts
executive documents
customer data
```

the RAG system cannot simply expose every indexed chunk to every user.

Retrieval should respect source permissions:

```text
user
 ↓
query
 ↓
retriever
 ↓
permission filter
 ↓
allowed documents
 ↓
LLM
```

Ideally, permissions from systems such as SharePoint, Jira or GitHub are preserved or mapped into the RAG layer.

Other relevant security concerns include:

- encryption,
    
- audit logs,
    
- document-level and chunk-level ACLs,
    
- data residency,
    
- model provider retention policies,
    
- prompt logging,
    
- embedding provider privacy,
    
- deletion and synchronization.
    

---

# A Sensible Adoption Path

A good way to learn RAG is to start small.

```text
1. documents
2. parsing
3. chunking
4. embeddings
5. vector retrieval
6. metadata
7. hybrid search
8. reranking
9. multiple data sources
10. Jira / repository integration
11. agentic retrieval
12. graph relationships
```

For example:

```text
v1
Docling + Qdrant + local embeddings

v2
+ metadata

v3
+ hybrid search

v4
+ Jira

v5
+ repository

v6
+ commits and PRs

v7
+ agent tools / MCP

v8
+ knowledge graph
```

This makes it possible to understand the value of each layer instead of immediately hiding the whole architecture behind an end-to-end RAG product.

---

## Key Idea

RAG should not be understood merely as:

> Search some vectors and give the results to an LLM.

A more useful definition is:

> **RAG is a mechanism for selecting the most relevant external knowledge and constructing the context needed by a model or agent to solve the current task.**

For software engineering, the eventual goal may therefore be broader than RAG itself:

> **build a reliable, permission-aware, temporally aware project knowledge layer that agents can explore and verify.**