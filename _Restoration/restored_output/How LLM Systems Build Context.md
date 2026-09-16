---
title: How LLM Systems Build Context
tags:
  - llm
  - context-window
  - rag
  - system-prompts
  - retrieval
  - prompt-engineering
  - state-management
aliases:
  - LLM Context Construction
  - Context Assembly Pipeline
---

# How LLM Systems Build Context

A modern LLM system does not reason from the visible user prompt alone. In production, the practical capability, safety, and reliability of an LLM application are governed by its **context assembly pipeline** rather than the raw parameter count of the underlying model. As explored in [[How Modern LLM Systems Build Context, Reason, and Stay Constrained]], the runtime harness dynamically compiles a multi-layered working context from instructions, conversation history, episodic memory, retrieved internal documents, web search, live tools, APIs, and runtime telemetry.

```text
USER QUESTION / GOAL
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ CONTEXT ASSEMBLY PIPELINE                                   │
│                                                             │
│ ├─ System Instructions      (Safety, operational envelopes) │
│ ├─ Application Instructions (Workspace rules, schemas)      │
│ ├─ Session State            (Rolling window, summaries)     │
│ ├─ Episodic Memory          (Extracted user/domain facts)   │
│ ├─ Document RAG             (Hybrid BM25 + vector chunks)   │
│ ├─ External Doc Providers   (Framework docs via MCP)        │
│ ├─ Live Tool Telemetry      (Traces, compiler outputs, DBs) │
│ └─ Environment Metadata     (Timestamp, git branch, paths)  │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ COMPILED CONTEXT WINDOW                                     │
│ (Budgeted, ranked, and deduplicated tokens)                 │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ MODEL ENGINE                                                │
│ (Next-token inference across compiled attention space)       │
└─────────────────────────────────────────────────────────────┘
```

Treating context assembly as an explicit engineering discipline changes how you build agents. Many apparent "model capabilities"—and conversely, many model failures—are actually capabilities or failures of the surrounding context assembly pipeline.

---

## 1. The Model Does Not Start With an Empty Context

When a user submits a prompt, the model receives an assembled payload that is typically orders of magnitude larger than the input text. This payload narrows the model's exploratory solution space, as detailed in [[How Context Narrows an AI's Solution Space]].

The assembled context typically includes:

```text
- platform and system instructions (governed by [[How LLM Systems Enforce Safety and Higher-Level Instructions]])
- developer or application instructions
- the current user request
- previous messages in the conversation
- selected memories about the user and project conventions
- relevant information from previous conversations
- retrieved documents (powered by [[Introduction to RAG]])
- web search results
- tool outputs and API responses
- current metadata such as time, git branch, or runtime environment
```

Conceptually:

```text
                    ┌─ system instructions
                    ├─ application instructions
                    ├─ current conversation
                    ├─ memory
USER QUESTION ──────┼─ previous conversation retrieval
                    ├─ RAG
                    ├─ web search
                    ├─ tools / APIs
                    └─ metadata
                             ↓
                       context window
                             ↓
                           model
```

### Layer Precedence and Conflict Resolution

When context sources provide conflicting information, the system cannot rely on the model to guess which source is authoritative. High-reliability harnesses enforce an explicit precedence hierarchy:

1. **System & Safety Envelopes**: Non-negotiable boundaries, schema enforcement, and tool access limits.
2. **Application Rules**: Workspace conventions, coding standards, and project-specific constraints.
3. **Dynamic Tool Telemetry & Live State**: The current state of the filesystem, compiler diagnostics, or production logs (hard ground truth).
4. **Retrieved External Context (RAG)**: Indexed documentation, Jira tickets, and architecture decision records (can be outdated).
5. **Session History & Episodic Memory**: Past turns and user preferences (subservient to current constraints).
6. **User Input**: The immediate task or question.

If a retrieved architecture document from two years ago contradicts a live compiler error or an active system prompt, the hierarchy ensures the harness or the model drops or flags the stale retrieved context rather than hallucinates a compromise.

---

## 2. Some Knowledge Is Inside the Model, Some Is Retrieved

A foundational distinction in LLM architecture is the difference between **parametric memory** and **non-parametric retrieval**:

- **Parametric knowledge** lives inside the model weights, baked in during pre-training and fine-tuning. For stable, widely published topics—such as explaining how the TCP three-way handshake works or writing a standard quicksort algorithm—the model answers directly from its internal weights.
- **Non-parametric knowledge** lives outside the model, retrieved on demand from databases, search indexes, filesystems, or APIs, and placed into the prompt.

Parametric knowledge is static, expensive to update, and lacks verifiable provenance. It struggles with:
- Private codebases and internal APIs.
- Information that changed after the model's training cutoff.
- Highly specific configuration details and exact numerical thresholds.

For private, specialized, or operational domains, relying on parametric recall leads to subtle confabulations. Reliable systems use parametric weights for syntax, reasoning, and language comprehension, but delegate facts, contracts, and state to external retrieval.

---

## 3. Web Search Is a Form of External Retrieval

When a model performs web search, it does not browse the internet like a human using a web browser. It executes a retrieval pipeline:

```text
question
   ↓
search query generation
   ↓
search index / external web providers
   ↓
selected documents, web pages, or snippets
   ↓
model context window
   ↓
reasoning & synthesis
```

Search systems rarely feed entire HTML pages to the model. They parse the DOM, extract readable content, slice it into chunks, re-rank those chunks against the query, and inject only high-relevance snippets into the context window.

This introduces architectural and operational tensions:

```text
allow AI indexing
→ greater visibility in AI-driven answer engines
→ potentially fewer direct visits to the origin site

block AI indexing (robots.txt / bot blockers)
→ retain control of content and compute costs
→ disappear from AI-assisted discovery pipelines
```

As search shifts toward synthesis engines, optimizing internal documentation and public technical content shifts from legacy SEO toward **retrieval-friendly structuring**: concise summaries, explicit metadata, clean markdown schemas, and clear semantic headings.

---

## 4. Conversation History and Attention Budgeting

In conversational systems, the dialogue history is one of the strongest contextual signals available. Rather than handling an isolated prompt:

```text
isolated prompt → response
```

the runtime passes the accumulated context:

```text
conversation history so far
+
new user message
→ response
```

However, context windows are not free, and they are not infinite. Even with windows supporting 128k, 1M, or 2M tokens, stuffing entire chat transcripts into the prompt creates two engineering problems:

1. **Latency and Compute Cost**: Time-to-first-token (TTFT) and inference cost scale with prompt size.
2. **Attention Dilution and "Lost-in-the-Middle"**: Transformer attention mechanisms do not attend equally to all tokens. Models tend to recall tokens at the absolute beginning (system prompt) and the absolute end (latest turn) far better than tokens buried in the middle of a massive context payload.

```text
Attention Weight
  ▲
  │   ████                                           ████
  │   ████                                           ████
  │   ████                                           ████
  │   ████ ─── "Lost in the Middle" ───►             ████
  │   ████       Low Attention Floor                 ████
  │   ████                                           ████
  └───┴──────────────────────────────────────────────┴────►
      Beginning of Context                      End of Context
      (System Prompt)                          (Latest Turn)
```

To manage this, production systems implement sliding context strategies:

- **FIFO Truncation**: Keep the system prompt, discard the oldest turns, and keep the latest $N$ turns.
- **Rolling Summarization**: Periodically summarize older messages into an evolving state object, discarding the raw turns while preserving key decisions.
- **Turn-by-Turn Pruning**: Strip verbose tool outputs (e.g., a 2,000-line build log or raw JSON dump) from historical turns once the model has derived its conclusion, retaining only the summary line or error trace.

---

## 5. Memory and Previous Conversations Behave Like Retrieval

Human users expect long-lived systems to remember preferences, constraints, and historical decisions across multiple disjoint sessions. Dumping years of conversation history into every request is unworkable.

Instead, long-term memory functions like an internal RAG system:

```text
years of conversations
        ↓
fact extraction / indexing
        ↓
vector / key-value memory store
        ↓
selective retrieval on intent
        ↓
current context window
```

During a conversation, the harness monitors the dialogue for durable facts:

```text
user works mainly with .NET and C#
user prefers modular monoliths over microservices
user requires strict null-handling and nullable reference types
```

When the user starts a new session weeks later asking: "How should I structure this new transaction handler?", the system queries its episodic memory store, pulls out these three relevant facts, and prepends them as operational constraints. The model gets personalized grounding without carrying the weight of hundreds of historical transcripts.

---

## 6. RAG Extends the Model With External Knowledge

In enterprise systems, the same retrieval principle applies across organizational boundaries:

```text
Git repositories
Jira / issue trackers
Confluence / wikis
Architecture Decision Records (ADRs)
Meeting transcripts
Post-mortem incident reports
Product specifications
Relational & document databases
```

When an engineer asks:

> Why does the payment retry mechanism behave like this?

A naive approach fails:

```text
question embedding
→ nearest 10 text chunks
→ LLM
```

Vector similarity alone struggles with technical questions because semantic vector distance cannot determine code dependencies or temporal updates. A chunk from an obsolete commit might match the vector embedding better than the active implementation.

A robust enterprise retrieval pipeline operates across structured signals:

```text
question
   ↓
identify payment module (code search / repo structure)
   ↓
find active architecture decisions (ADRs)
   ↓
query related Jira issue keys and pull requests
   ↓
extract recent git commits / diffs
   ↓
assemble code snippets + rationale
   ↓
model context window
   ↓
reasoning & synthesis
```

Advanced retrieval systems combine:
- **Hybrid Search**: Dense vectors (embeddings) combined with sparse lexical search (BM25) for exact keyword and symbol matching.
- **Structural Signals**: Abstract Syntax Tree (AST) graphs, file hierarchies, and symbol reference graphs.
- **Temporal Filtering**: Timestamps, git commit metadata, and document status flags (Draft, Approved, Deprecated).
- **Relational Metadata**: Authorship, issue linkage, and repository dependencies.

See [[RAG Ingestion and Chunking Strategies]] for deep dives into document decomposition and indexing topologies.

---

## 7. External Documentation Providers as Context

Not every external knowledge corpus belongs inside your local vector database. Frameworks, cloud SDKs, third-party APIs, and programming languages update continuously on their own release cycles. Ingesting every revision of the AWS SDK or .NET documentation into an internal corporate index creates a massive maintenance burden.

Modern architectures offload this to **external documentation providers** designed specifically to serve real-time technical documentation to agents on demand. Examples include Context7 or documentation providers exposed via the Model Context Protocol (MCP).

```text
question
   ↓
agent selects documentation provider
   ↓
provider searches its authoritative, managed corpus
   ↓
relevant, version-pinned documentation / examples
   ↓
model context window
   ↓
reasoning
```

### Knowledge Sources vs. Access Mechanisms

It is critical to distinguish between where context lives and how it is fetched:

> **Knowledge Source** = Where the information lives and who maintains it.
>
> **Delivery Mechanism** = The protocol, tool, or pipeline used to pull it into the prompt.

| Knowledge Source | Typical Delivery Mechanism | Maintenance Model |
| :--- | :--- | :--- |
| **Framework Docs (e.g., Microsoft Learn)** | MCP, external documentation APIs | Managed by vendor / third-party |
| **Internal Wikis (Confluence)** | Hybrid RAG, REST API tool | Managed by company platform team |
| **Code Repositories (Git)** | Code search index, AST graphs, MCP | Managed by repository maintainers |
| **Production Telemetry** | KQL, Prometheus API, Observability MCP | Managed by SRE / infra pipeline |

MCP is not a knowledge category; it is a standardized transport protocol. It allows an agent to query different sources through a unified interface.

### The Context Router Pattern

Instead of dumping every tool and document into the prompt, high-performance systems use a **context router** (or source selector):

```text
                     ┌─ Internal RAG (wikis, design docs)
                     ├─ Code Search (ASTs, symbol lookup)
                     ├─ Issue Trackers (Jira, Linear)
Agent → Source Router ├─ Architecture & Dependency Graphs
                     ├─ Runtime Telemetry (traces, metrics)
                     ├─ External Documentation Providers
                     ├─ Web Search
                     └─ Direct DB / Tool Execution
```

The router determines the source of truth based on the nature of the prompt:

- *"How does this external library API contract work?"* $\rightarrow$ External framework documentation.
- *"Why did we configure PaymentService this way?"* $\rightarrow$ Git history + ADRs + Jira issue.
- *"Does production actually exercise this code path?"* $\rightarrow$ Runtime telemetry and distributed traces.

This prevents prompt clutter, saves token budget, and ensures the model consults the authoritative system for each type of question.

---

## 8. Runtime Telemetry and Observability as Context

Source code and documentation only reveal part of an application's behavior:

- **Architecture Documentation** describes what the system *should* do.
- **Source Code & Static Graphs** describe what the system *can* do.
- **Runtime Telemetry** describes what the system *actually does* in production under real traffic, at what latency, and with what failure modes.

Telemetry context includes:
- Distributed traces (OpenTelemetry, Application Insights).
- Dynamic dependency graphs and Application Maps.
- Latency percentiles ($p50$, $p95$, $p99$), failure rates, and retry counts.
- Queue backpressure, consumer lag, and thread pool exhaustion metrics.
- Dominant execution paths vs. dead code.

Static analysis might identify twenty theoretical execution paths through a switch statement or interface implementation. Telemetry proves that two paths handle 99.8% of production requests, while a third path only fires during transient network drops.

### Telemetry Context Hierarchy

Raw logs are high-volume, low-density context. Feeding thousands of raw JSON log lines into an LLM wastes tokens and triggers attention dilution. Instead, telemetry context should be structured hierarchically:

```text
1. Architecture & System Contracts   (Intended Design)
        ↓
2. Static AST & Dependency Graphs     (Structural Potential)
        ↓
3. Application Topology / Maps       (Observed System Boundaries)
        ↓
4. Aggregated Metrics & Hot Paths     (Dominant Production Behaviors)
        ↓
5. Filtered Exemplar Traces           (Specific Causality & Latency Spikes)
        ↓
6. Raw Error Logs / Exceptions       (Atomic Evidence)
```

The agent starts at the top of the pyramid. It checks the service map to see which nodes talk to each other, looks at aggregated metrics to identify regressions, and only drops down to query specific KQL logs or individual trace IDs when it needs to isolate a specific stack trace.

### Telemetry Tools vs. Diagnostic Skills

There is a clean line between the access protocol and the operational procedure:

- **The Tool / MCP Server** provides access to the raw data (e.g., executing a KQL query or pulling trace spans).
- **The Diagnostic Skill** teaches the agent *how to investigate*.

A diagnostic skill guides the model through an SRE runbook:
1. Locate the endpoint or service reporting errors.
2. Query downstream dependency metrics to see if the degradation is local or upstream.
3. Compare the current failure rate against pre-deployment baselines.
4. Extract the top three exception stack traces from correlated traces.
5. Cross-reference the failing code path with the latest deployment commit diff.

Observability ceases to be an external dashboard a human looks at; it becomes a structured, queryable runtime model that grounds agentic reasoning.

```text
Documentation ──► Intended system
Codebase      ──► Implemented system
Runtime Graph ──► Observed system
Telemetry     ──► Verifiable evidence
```

---

## 9. Reasoning Can Control Retrieval (Closed-Loop Feedback)

Context assembly is not necessarily a single-shot operation executed before inference begins. Complex problem-solving requires an iterative loop between reasoning and retrieval.

```text
       ┌────────────────────────┐
       │     Initial Context    │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │         REASON         │
       │  "What am I missing?"  │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │        RETRIEVE        │
       │  (Fetch missing piece) │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │         REASON         │
       │  "Does this make sense │
       │    with the code?"     │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │         VERIFY         │
       │  (Run test / compile)  │
       └───────────┬────────────┘
                   │
                   ▼
              [ Conclusion ]
```

Consider diagnosing an operational failure:

> Why did checkout latency spike after the 14:00 UTC deployment?

An agent operating in an open loop tries to guess from its initial prompt. A closed-loop agent breaks the problem down into sub-queries:

1. **Reason**: "I need to know what changed in that deployment."
   - **Retrieve**: Fetch the git commit log between the current release tag and the prior tag.
2. **Reason**: "Commit `a7f3b1` modified database connection pool sizing. I need to check connection wait metrics."
   - **Retrieve**: Query telemetry for `ConnectionWaitTime` percentiles around 14:00 UTC.
3. **Reason**: "Wait times spiked from 5ms to 1200ms. Did active connections hit the pool ceiling?"
   - **Retrieve**: Fetch active vs. idle pool metrics from the database monitoring API.
4. **Verify**: Correlate connection pool exhaustion events with upstream API timeouts.

The model controls the context assembly pipeline dynamically, pulling in precisely the tokens it needs to validate or reject hypotheses.

---

## 10. More Context Helps, But Does Not Eliminate the Problem

Injecting high-density, relevant context dramatically improves model output. When an LLM has access to exact schemas, current code, and concrete constraints, it ceases to rely on generic boilerplate and performs sharp deductive reasoning.

```text
Provided Fact:
"Old and new service versions run concurrently during rolling deployments."

Valid Deduction:
The database schema change must maintain backward compatibility with the previous version.

Concrete Implementation:
Introduce the column as nullable in phase one; update application code in phase two; apply NOT NULL constraints in phase three.
```

```text
Provided Fact:
"Ticket inventory reservations cannot exceed the current quota limit under concurrent access."

Valid Deduction:
A simple read-modify-write pattern introduces race conditions.

Concrete Implementation:
Use optimistic concurrency with row versioning, or execute an atomic SQL update: `UPDATE Inventory SET Reserved = Reserved + @Qty WHERE Id = @Id AND Reserved + @Qty <= Total`.
```

This is valid domain inference, grounded by context.

### Context Pathologies

However, simply increasing context volume does not guarantee correctness. More context can actively degrade output if the pipeline suffers from common pathologies:

- **Incomplete Context**: The prompt includes the service implementation but omits the middleware handling authentication, leading the model to generate redundant or conflicting auth checks.
- **Outdated Context**: The RAG index returns an obsolete ADR that contradicts the current production architecture.
- **Contradictory Context**: Two retrieved documents prescribe opposing patterns, and the system lacks a precedence hierarchy to resolve them.
- **Noise and Context Bloat**: Dumping thousands of lines of unrelated code or verbose logs drowns the critical signal, pushing the model toward attention dilution and missed instructions.
- **Hidden Organizational State**: The true constraint exists only as unwritten team tribal knowledge or a manual operational procedure not indexed anywhere.

The objective of context assembly is not to maximize the token count up to the window boundary. The objective is to maximize **information density** while strictly minimizing noise.

---

## Relationship to the Knowledge Graph

- **[[How Modern LLM Systems Build Context, Reason, and Stay Constrained]]**: Architectural synthesis connecting context assembly with downstream reasoning loops and constraint boundaries.
- **[[How Context Narrows an AI's Solution Space]]**: Mathematical and operational models explaining how token injection prunes non-deterministic solution spaces.
- **[[How LLM Systems Enforce Safety and Higher-Level Instructions]]**: Deep dive into system prompt hierarchy, prompt shields, and boundary enforcement.
- **[[Introduction to RAG]]**: The foundations of external retrieval, indexing mechanics, and similarity search.
- **[[RAG Ingestion and Chunking Strategies]]**: Practical strategies for tokenizing, chunking, and indexing code, documents, and schemas without losing semantic context.
- **[[LLM Agents and Institutional Memory]]**: How enterprise systems turn tribal knowledge, ADRs, and post-mortems into queryable context.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: How execution harnesses combine context management, compiler loops, and test oracles to drive autonomous coding workflows.
