---
title: AI-Generated Architectural Documentation from Code
tags:
  - ai-agents
  - software-architecture
  - documentation
  - reverse-engineering
  - code-review
  - system-design
aliases:
  - AI-Generated Architectural Documentation
  - Extracting Architecture from Code with LLMs
  - Documentation as Semantic Cache
  - Architectural Drift Detection
  - Operation Cards from Code
---

# AI-Generated Architectural Documentation from Code

## Core Principles & Architecture
In software engineering, large language models are usually discussed as code writers. But models are equally powerful in the reverse direction: **extracting, reconstructing, and maintaining high-level architectural documentation from existing codebases**.

This is especially critical when dealing with legacy repositories where:
- Original design documents are years out of date or missing entirely,
- Tribal knowledge walked out the door with previous developers (see [[LLM Agents and Institutional Memory|institutional memory in software teams]]),
- The system is too large for any single developer to hold in their head.

The goal is **not** to generate trivial comments on every class or method (`GetOrder retrieves an order`). The true value lies in reconstructing the system's **relational architecture**:
- Which components exist and what boundaries isolate them,
- Who owns which database tables and business aggregates,
- How data flows synchronously versus asynchronously across services,
- What state transitions and failure modes are enforced in code.

```text
STATIC RECONSTRUCTION PIPELINE:
Source Code ──► Dependency & Call Graphs ──► LLM Interpretation ──► Living Architecture Docs
[Raw Implementation]   [Structural Facts]        [Domain Meaning]       [Compact Operation Cards]
```

---

## Documentation as a Semantic Cache for Agents

Without high-level architectural docs, an AI coding agent assigned to a task must spend dozens of tool calls reading controllers, handlers, repositories, and config files just to figure out where to begin:

```text
WITHOUT ARCHITECTURAL DOCS (EXPENSIVE RECONNAISSANCE):
Read 15 files ──► Map dependencies ──► Guess business flow ──► 25,000 tokens burned ──► First edit

WITH ARCHITECTURAL DOCS (DIRECT EXECUTION):
Read 40-line Operation Card ──► Inspect target file ──► 2,000 tokens burned ──► First edit
```

Architectural documentation acts as a **semantic cache for the repository**:
1. **Saves Context Window Budget**: Instead of loading sprawling file trees into context, the agent ingests a concise summary card that defines boundaries and entry points.
2. **Speeds Up Execution**: The agent moves from prompt to implementation immediately, skipping exploratory grep-and-read loops.
3. **Prevents Boundary Violations**: LLMs naturally pattern-match against existing code. If legacy code has messy coupling, the model will copy it unless explicit architectural cards state: *"Orders must never write to Inventory tables directly."*

---

## Why Tests Alone Aren't Enough for Maintenance

A common belief is that an exhaustive test suite eliminates the need for architectural documentation.

While deterministic tests are essential as the verification floor (see [[Testing in the Model, Agent, LLM Era|automated test verification]]), **tests and architectural documentation solve completely different problems**:

| Dimension | Automated Test Suites | Architectural Documentation |
| :--- | :--- | :--- |
| **Primary Purpose** | Verifies behavior (`actual == expected`) | Guides navigation and structural boundaries |
| **Greenfield / Rewrites** | Excellent (run tests until all pass) | Helpful, but tests alone can guide the rewrite |
| **Ongoing Maintenance** | Blind to architecture (passes even if coupling is terrible) | Prevents architectural drift across modules |
| **New Capabilities** | Zero coverage (tests don't exist yet) | Shows where the new feature belongs and what rules apply |

A test suite will happily pass even if an agent queries another module's database directly or bypasses validation middleware. Tests verify output correctness; architectural documentation protects structural boundaries (see [[Tests Are for Verification, Not Architectural Navigation]]).

---

## The Four Zoom Levels: Hierarchical Context for Agents

A monolithic 50-page document for an entire system is useless for an agent—it swamps context and dilutes attention. Instead, architecture should be organized in hierarchical zoom levels (similar to the C4 model):

```text
Level 1: System Context  ──► Users, external payment gateways, core platform boundaries
Level 2: Containers      ──► Web apps, APIs, workers, databases, message queues
Level 3: Components      ──► Ingress controllers, domain handlers, repositories
Level 4: Implementation  ──► Source code, method signatures, exact state transitions
```

When an agent is given a task, the workflow navigates down the hierarchy:
1. **Macro Routing (Level 1 & 2)**: Determine which service or container owns the requested feature.
2. **Component Mapping (Level 3)**: Identify existing handlers and interfaces without reading their implementation.
3. **Targeted Mutation (Level 4)**: Load only the single file or interface needed to make the change.

By scoping context hierarchically, the agent achieves first-pass success while using 90% fewer tokens.

---

## Operation Cards: Workflow-Centric Documentation

Organizing documentation strictly by file or class creates silos. The most valuable architectural docs are organized around **business workflows**:

```markdown
### Operation: ConfirmPayment

**Purpose**: Confirms an authorized payment and kicks off downstream fulfillment.

**Entry Points**:
- HTTP: `POST /payments/{id}/confirm`
- Worker: `PaymentConfirmationWorker`

**Synchronous Flow**:
1. Validate incoming request contract
2. Load payment record from PostgreSQL
3. Verify state is `Authorized`
4. Call external Payment Gateway
5. Persist status as `Confirmed`

**Asynchronous Flow**:
6. Publish `PaymentConfirmed` event to message broker
7. Accounting and Inventory consumers process the event asynchronously

**State Transitions**:
`Authorized` ──► `Confirmed` (or `Failed` on terminal provider error)

**Failure Modes & Retries**:
- Provider timeout: Exponential backoff, max 3 attempts.
- Persistence failure: Abort transaction and log operational alert.
```

From this compact markdown representation, tools can generate Mermaid sequence diagrams, verification checklists, and prompt context for coding agents.

---

## Intended vs. Implemented Architecture: Detecting Drift

One of the most practical applications of generated documentation is comparing **how the system was supposed to work** with **how it is actually implemented**:

```text
SPECIFICATION (Intended Architecture)
            │
            ▼
    Source Codebase
            │
            ▼
RECONSTRUCTED MODEL (Implemented Architecture)
            │
            ▼
COMPARE SPEC vs RECONSTRUCTION ──► Surface Architectural Drift
```

Comparing the two models immediately highlights:
- A module was supposed to be isolated, but code directly imports an internal database model from another domain,
- A workflow described as asynchronous event-driven is actually making synchronous blocking HTTP calls,
- A cache was added to bypass a slow query, masking a database bottleneck without updating design docs.

---

## Architectural Diffs in Pull Requests

Traditional code reviews focus on file diffs: *"Which lines changed?"*  
AI-generated architectural analysis answers: **"What changed architecturally?"**

```text
TRADITIONAL PR DIFF:
Modified: orders_controller, payment_client, event_publisher (340 lines added, 120 removed)

ARCHITECTURAL PR DIFF:
- Payment processing changed from synchronous HTTP calls to asynchronous event publishing.
- Added eventual consistency boundary: Order completion now depends on PaymentConsumer.
- Introduced new failure mode: Unhandled messages in the payment dead-letter queue.
```

This summary allows senior engineers reviewing PRs to immediately spot architectural trade-offs, security implications, and reliability risks without getting lost in cosmetic syntax (see [[Reviewing AI-Generated Code]]).

---

## Combining Static Code Analysis with Runtime Telemetry

Static code analysis shows what a system *can* do. Real-world runtime telemetry shows what the system *actually does*.

By combining code inspection with distributed tracing, logs, and metrics, generated documentation turns into an **operational blueprint**:

```text
STATIC CODE PATH:
Orders API ──► Payment Gateway ──► Ledger Service ──► Database

RUNTIME OPERATIONAL REALITY:
- P50 Latency: 65ms | P95 Latency: 480ms | P99 Latency: 2.3s
- External Payment Gateway times out on ~1.8% of requests during peak load.
- Background reconciliation job cleans up stranded transactions every 15 minutes.
```

This bridges the gap between software design and production operations, giving agents and developers an accurate picture of system behavior under load.

---

## Practical Rules for Teams

1. **Document relationships, not syntax**: Never waste tokens explaining what a single function does; document data ownership, module boundaries, async boundaries, and failure handling.
2. **Generate docs continuously in CI**: Hook architectural extraction into your pull request pipeline to keep markdown cards and diagrams synchronized with code.
3. **Use Operation Cards as agent context**: When dispatching an agent to modify a feature, pass the Operation Card as the primary blueprint (see [[In-Flight Documentation as the Primary Framework for Coding Agents]]).
4. **Surface architectural diffs in code review**: Review pull requests at the structural level before diving into individual code lines.

---

## Related Notes

- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Generating concise architectural blueprints concurrently during code authoring to guide future agents.
- **[[Tests Are for Verification, Not Architectural Navigation]]**: Why deterministic test suites verify functionality but cannot guide agents on architectural boundaries.
- **[[Reviewing AI-Generated Code]]**: How senior engineers pivot from line-by-line syntax checks to reviewing structural invariants and architectural diffs.
- **[[Comments May Become More Valuable in AI-Generated Code]]**: Why non-derivable domain intent recorded in code comments feeds directly into generated architectural documentation.
- **[[LLM Agents and Institutional Memory]]**: Preserving institutional engineering knowledge and system rationale across team transitions.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]**: How codebases adapt their layout and boundaries to make semantic extraction and automated maintenance seamless.
- **[[Testing in the Model, Agent, LLM Era]]**: The foundational verification layer that ensures reconstructed code and implementations adhere to specifications.
