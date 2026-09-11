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

> [!IMPORTANT]
> **Executive Summary & Architectural BLUF**:  
> The effective capability and reliability of an LLM application is primarily determined by its **Context Assembly Pipeline**, not merely the raw parameter weights of the underlying model. An LLM never reasons over an isolated user prompt; instead, the runtime harness dynamically compiles a multi-layered working context from:
> 1. **System & Safety Invariants** (authoritative baseline instructions and non-negotiable boundaries),
> 2. **Session & Conversational State** (turn history and user episodic memory),
> 3. **Semantic Retrieval / RAG** (domain documents, indexed codebases, external web grounding),
> 4. **Dynamic Tool & API Responses** (runtime state, telemetry, command outputs).  
> Expanding context windows does not eliminate the need for curation. Uncurated context dumps trigger **attention dilution**, **lost-in-the-middle omissions**, and **contradictory priors**. High-reliability systems treat the context window as a strictly managed cache, prioritizing high-signal invariants and explicit task boundaries.

### Comparative Matrix: Context Pipeline Ingestion Sources

| Context Source Layer | Ingestion Mechanism | Freshness & Mutability | Attention Density & Signal-to-Noise | Verifiability & Provenance | Primary Failure Modes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Parametric Model Weights** | Pre-training and post-training / fine-tuning. | Static: Frozen at training cutoff date. | High density, but general and probabilistic. | Low: Implicit, unciteable, prone to hallucination on private domains. | Outdated knowledge, confabulation, zero awareness of local enterprise rules. |
| **System & Developer Instructions** | Hard-coded or template-injected system prompts. | Highly static per deployment version. | **Maximum**: Serves as the authoritative frame for all subsequent reasoning. | Complete: Auditable source text in repository. | Rule collision, instruction drift, prompt injection vulnerability. |
| **Conversational History (Session State)** | Sliding FIFO window or compressed turn summarization. | Dynamic: Grows turn-by-turn within active session. | Variable: Can become diluted with conversational noise and failed attempts. | High: Visible in message history log. | **Attention Gravity** (locking onto irrelevant early turns), memory bloat, context exhaustion. |
| **Retrieval-Augmented Generation (RAG)** | Dense vector embeddings or hybrid lexical search over chunked corpora. | Dynamic: Real-time query over updated databases. | Moderate: Depends heavily on chunking quality, reranking, and semantic relevance. | **Explicit**: Attributable to exact source documents, line numbers, or URIs. | Chunk fragmentation, semantic drift, retrieving outdated or contradictory documentation. |
| **Dynamic Tool / API Outputs** | Structured JSON or text payloads returned by executed tool actions. | Real-time: Reflects immediate live system state. | Focused: High operational relevance for specific execution steps. | **Deterministic**: Exact payload recorded in execution telemetry. | Schema mismatch, excessive payload size blowing context budgets, unhandled tool errors. |

---

A modern LLM system does not reason from the visible user prompt alone. As synthesized in [[How Modern LLM Systems Build Context, Reason, and Stay Constrained|how modern LLM systems build context, reason, and stay constrained]], effective context is assembled from instructions, conversation history, memory, retrieved documents, web search, tools, APIs, and metadata.

## 1. The Model Does Not Start With an Empty Context

When a user asks a question, the model may receive substantially more information than the visible prompt, illustrating [[How Context Narrows an AI's Solution Space|how context narrows the effective solution space]].

The effective context may include:

```text
- platform and system instructions (governed by [[How LLM Systems Enforce Safety and Higher-Level Instructions|higher-level safety instructions]])
- developer or application instructions
- the current user request
- previous messages in the conversation
- selected memories about the user
- relevant information from previous conversations
- retrieved documents (powered by [[Introduction to RAG|retrieval-augmented generation (RAG)]])
- web search results
- tool outputs and API responses
- current metadata such as time or environment
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

This means that many apparent "model capabilities" are actually capabilities of the whole system around the model.

---

## 2. Some Knowledge Is Inside the Model, Some Is Retrieved

The model itself contains knowledge acquired during training.

For stable questions, such as:

> What is TCP?

it may answer directly from what has been encoded in its parameters.

But the model cannot rely on its internal knowledge for everything.

For recent, private, specialized, or highly detailed information, the system may perform retrieval.

---

## 3. Web Search Is a Form of External Retrieval

When the model searches the web, the process can roughly be thought of as:

```text
question
   ↓
search query
   ↓
search index / web sources
   ↓
selected documents or snippets
   ↓
model context
   ↓
reasoning
```

The model does not necessarily download every page directly.

The search system may use:

- search indexes,
    
- cached copies,
    
- crawled documents,
    
- snippets,
    
- external search providers,
    
- direct page retrieval.
    

A publisher may also prevent particular AI crawlers from indexing its content.

This creates an important tension:

```text
allow AI indexing
→ greater visibility in AI answers
→ potentially fewer direct visits

block AI indexing
→ retain more control
→ potentially disappear from AI-driven discovery
```

The old SEO problem is therefore gradually becoming a broader problem of optimizing information for AI retrieval and answer systems.

---

## 4. Conversation History Is Another Source of Context

The current conversation is usually one of the strongest contextual signals.

Instead of answering:

```text
isolated prompt → response
```

the system can answer:

```text
conversation so far
+
new message
→ response
```

However, context windows are finite.

For long conversations, systems may need to:

- retain recent messages directly,
    
- summarize older parts,
    
- retrieve only relevant fragments,
    
- discard information that appears irrelevant.
    

So a model does not necessarily receive the entire raw history of a long conversation on every turn.

---

## 5. Memory and Previous Conversations Behave Like Retrieval

Information from older conversations can be handled similarly to RAG.

Rather than loading every historical conversation, a system can retrieve relevant facts.

Conceptually:

```text
years of conversations
        ↓
retrieval
        ↓
relevant facts
        ↓
current context
```

For example:

```text
user works mainly with .NET
user prefers modular monoliths
the previous discussion concerned agentic code review
```

may be enough context for the current question.

This makes personal memory effectively another knowledge source available to the agent.

---

## 6. RAG Extends the Model With External Knowledge

In a company environment, the same principle can be applied to:

```text
Git repositories
Jira
Confluence
architecture documents
meeting transcripts
incident reports
product specifications
databases
```

Suppose someone asks:

> Why does the payment retry mechanism behave like this?

A useful agent might perform:

```text
question
   ↓
find payment module
   ↓
find architecture decision
   ↓
find related Jira tickets
   ↓
find recent implementation changes
   ↓
retrieve relevant code
   ↓
reason
```

The naive form of RAG:

```text
question embedding
→ nearest 10 text chunks
→ LLM
```

is therefore only the simplest version.

More advanced retrieval can use:

- semantic similarity,
    
- keyword search,
    
- metadata,
    
- dependency graphs,
    
- document hierarchy,
    
- timestamps,
    
- authorship,
    
- source code structure,
    
- previous retrieval results.
    

---

## 7. External documentation providers as context

Not every external knowledge source needs to be copied into the company's own RAG index.

Some services are designed specifically to expose technical documentation to agents on demand. Examples include:

- Context7,
- Microsoft Learn MCP,
- similar documentation or API knowledge providers exposed through MCP or another queryable interface.

These systems form another useful category of context source:

> **external documentation providers**

They are especially useful for questions about frameworks, SDKs, cloud services, APIs, language features and other knowledge that changes independently of the company's own codebase.

Conceptually:

```text
question
   ↓
agent chooses documentation provider
   ↓
provider searches its authoritative corpus
   ↓
relevant documentation / examples
   ↓
model context
   ↓
reason
```

This differs from the simplest company RAG architecture:

```text
question
   ↓
search internally indexed corpus
   ↓
retrieve chunks
   ↓
model
```

The difference is not that one mechanism is "RAG" and the other is fundamentally unrelated. Both are forms of retrieval. The important architectural distinction is that the knowledge may be maintained and searched by an external provider rather than ingested into the company's own vector store or search index.

### Source of knowledge vs access mechanism

It is useful to separate two concepts:

> **Source of context** = where the knowledge comes from.

> **Context delivery mechanism** = how the agent obtains it.

For example:

```text
Microsoft Learn        → knowledge source
MCP                    → access protocol

Confluence             → knowledge source
RAG / search / MCP     → possible access mechanisms

Git repository         → knowledge source
code search / graph / MCP → possible access mechanisms
```

MCP therefore should not itself be treated as a knowledge category. It is better understood as a standard interface through which many different context sources and tools can be exposed.

This leads to a broader view of retrieval:

```text
                     ┌─ internal RAG
                     ├─ code / repository search
                     ├─ Jira / Confluence
Agent → source router ├─ architecture / code graph
                     ├─ runtime telemetry
                     ├─ external documentation providers
                     ├─ APIs and tools
                     └─ web search
```

The agent does not need to load all of these sources at once. It can choose the source that best matches the current question.

For example:

```text
"How does this .NET API work?"
→ external framework documentation

"Why do we use it this way in PaymentService?"
→ repository + ADR + Jira + commit history

"Does production actually exercise this path?"
→ runtime telemetry / traces
```

This suggests a useful architectural component: a **context router** or **source selector**.

Its job is not merely to retrieve documents, but to decide which knowledge system should be queried first and when another source is needed for verification. This is often more effective than attempting to place every possible source into one large vector database.

---

## 8. Runtime telemetry and observability as context

An agent does not have to infer the system only from source code and documentation. Runtime observability can provide another important source of context.

Examples include:

- distributed traces,
    
- Application Insights / Azure Monitor,
    
- Application Map,
    
- service and dependency graphs,
    
- request and dependency telemetry,
    
- queue and consumer activity,
    
- latency, failure and retry statistics,
    
- hot paths and frequently used execution paths.
    

This context answers a different question than static code analysis.

Static sources describe:

> What can the system do?

Architecture documentation describes:

> What should the system do?

Runtime telemetry describes:

> What does the system actually do in production, how often, and at what cost?

For example, static analysis may discover many possible execution paths, while telemetry may show that three paths account for 99% of production traffic.

This makes runtime data useful not only for incident investigation, but also as architectural context for agents.

A useful hierarchy is:

```text
Architecture / business documentation
        ↓
Source code and static relationship graph
        ↓
Runtime topology / dependency graph
        ↓
Aggregated traces and hot paths
        ↓
Individual traces
        ↓
Raw logs
```

The agent should preferably start from a compressed runtime model rather than repeatedly reconstructing the entire topology from raw logs.

For example, an Application Map or another precomputed dependency graph can answer which services communicate with each other. The agent can then use KQL or individual traces only for drill-down.

This suggests an important distinction:

**MCP/tool access provides the telemetry.**

**A skill tells the agent how and when to use it.**

A skill could instruct the agent to:

1. identify the operation being modified,
    
2. inspect its runtime dependencies,
    
3. determine dominant execution paths,
    
4. identify hot paths and rare fallback paths,
    
5. compare observed behavior with architecture documentation,
    
6. use raw telemetry only when additional detail is required.
    

Therefore observability can become a queryable runtime model of the application rather than merely a debugging facility.

### Relationship to other context mechanisms

This complements rather than replaces other sources:

- **RAG** retrieves relevant knowledge and documentation.
    
- **Code comments** expose local business meaning close to implementation.
    
- **Static code graphs / Graphify-like tools** describe structural relationships present in the code.
    
- **Runtime graphs** describe relationships actually exercised in production.
    
- **MCP/tools** allow the agent to query those sources dynamically.
    

Together they provide complementary views of the same system:

```text
Documentation → intended system
Code graph     → implemented system
Runtime graph  → observed system
Telemetry      → evidence
```

---

## 9. Reasoning Can Control Retrieval

The system does not have to collect all information before reasoning begins.

Instead, reasoning and retrieval can form a loop:

```text
initial context
      ↓
reason
      ↓
"I am missing X"
      ↓
retrieve X
      ↓
reason again
      ↓
"I should verify Y"
      ↓
retrieve Y
      ↓
continue
```

This produces a more agent-like process:

```text
REASON
  ↓
RETRIEVE
  ↓
REASON
  ↓
RETRIEVE
  ↓
VERIFY
```

The model can therefore actively decide what information it needs.

For example:

> Why did latency increase after the latest deployment?

An agent might create subquestions:

```text
What changed in the deployment?
Which endpoints became slower?
Did database latency change?
Did resource limits change?
Was an external dependency affected?
```

and then query:

```text
Git
logs
metrics
deployment configuration
tickets
architecture documentation
```

before reaching a conclusion.

---

## 10. More context helps, but does not eliminate the problem

Providing the model with more relevant context reduces the need to rely on generic patterns.

Useful context includes:

- business rules and invariants,
    
- edge cases,
    
- current code,
    
- tests,
    
- API contracts,
    
- database schemas,
    
- deployment configuration,
    
- architecture decision records,
    
- incident history,
    
- telemetry,
    
- operational procedures,
    
- migration constraints,
    
- descriptions of real end-to-end workflows.
    

With enough context, the model can infer valid consequences.

Example:

```text
Fact:
Old and new application versions run simultaneously.

Inference:
The data model must remain compatible with both versions.

Consequence:
The schema change should be introduced in stages.
```

Or:

```text
Fact:
A reservation cannot exceed the available limit.

Inference:
Read, validation, and write must be protected against concurrency.

Consequence:
A simple unprotected read-modify-write flow is insufficient.
```

This is useful inference, not hallucination.

However, more context does not guarantee correctness.

The context may still be:

- incomplete,
    
- outdated,
    
- contradictory,
    
- too large and noisy,
    
- missing organizational knowledge,
    
- missing undocumented consumers,
    
- missing manual operational processes.
    

The goal should not be to provide the maximum possible context.

The goal should be to provide context relevant to the decision.

---

## Relationship to the Knowledge Graph

- **[[How Modern LLM Systems Build Context, Reason, and Stay Constrained]]**: Synthesizes context assembly with downstream reasoning and constraint enforcement.
- **[[How Context Narrows an AI's Solution Space]]**: Explores how assembled context prunes and biases the model's exploratory solution space.
- **[[Introduction to RAG]]**: Architectural overview of retrieval pipelines that dynamically inject external context into the model window.
- **[[RAG Ingestion and Chunking Strategies]]**: Details how documents must be chunked and indexed to ensure precise context retrieval without attention dilution.
- **[[LLM Agents and Institutional Memory]]**: How organizational history and decision records become context sources for enterprise coding agents.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: How execution harnesses manage context compaction, rule enforcement, and state progression.