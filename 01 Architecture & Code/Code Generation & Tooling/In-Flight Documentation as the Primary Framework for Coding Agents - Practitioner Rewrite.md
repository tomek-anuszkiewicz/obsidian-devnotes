---
title: In-Flight Documentation as the Primary Framework for Coding Agents
tags:
  - software-architecture
  - documentation
  - ai-agents
  - agentic-coding
  - developer-experience
  - context-engineering
aliases:
  - In-Flight Documentation Generation
  - Documentation as Agent Framework
  - Deterministic Agent Scaffolding
  - Generating Documentation During Code Writing
  - Documentation as Code for the Agent
  - Markdown as the Highest-Level Source Code
  - Documentation as AI Compiler Input
  - Two-Stage Agentic Compilation Pipeline
  - Source Code as Intermediate Representation
  - Operation Cards
  - Iterative Specification Calibration
---

# In-Flight Documentation as the Primary Framework for Coding Agents

## Write down the decisions while the agent still has them in context

Documentation often arrives after the code. By then, the engineer has moved on, and writing a design document for last week's implementation feels like extra work. The document soon falls behind the code. The team relies instead on what people remember, conventions that nobody wrote down, and class hierarchies that take time to untangle.

An agent changes when that documentation can be written. While it implements a feature, it already has the relevant types, code structure, boundaries, and edge cases in context. Ask it to record the decisions at that point, and the engineer spends almost no extra time reconstructing them later. The additional model work is small compared with rediscovering the design in another session.

This leads to a different way of using documentation:

1. **Generate it during implementation.** Capture the rules while the agent is working through them, rather than trying to remember them after the task is finished.
2. **Use Markdown to show the agent how the component works.** A short, structured explanation of contracts is easier for a model to follow than a deep inheritance tree, reflection, or framework magic (see [[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]).
3. **Constrain the next implementation.** Without written rules, an agent may invent a helper, add an unapproved dependency, or follow a different architectural pattern. A specification gives it a smaller set of valid choices.
4. **Spend context on the decisions that matter.** A 40-line card can explain the component's intent more directly than twenty source files from which the agent must infer it.

## Treat the specification as the starting point for the next change

The usual build starts with source code and ends with a compiled program. With an agent in the workflow, you can put a Markdown specification one step earlier:

```text
Traditional build:
Source code → compiler / type checker → executable

Agent workflow:
Markdown specification → coding agent → source code → compiler / tests → working system
```

Think of the Markdown as a higher-level description of the system. The generated source code is then an intermediate artifact: the agent writes it, automated checks verify it, and engineers review it. This is an analogy for how the work is organized, rather than a claim that the agent replaces a compiler.

The engineer still has important work to do. Write or refine the rules that the agent must follow: which component owns a state change, which dependencies it may call, and what happens when an operation fails. A clearer contract gives the agent less room to make the wrong choice. When business rules change, update the specification and have the agent refactor the implementation against the existing tests. That can be quicker than manually following the same rule through several files.

Review also becomes more focused. A lead engineer can read a compact specification and the relevant diff to keep an accurate picture of the architecture, without writing every line of routine code (see [[Reviewing AI-Generated Code]]).

## Why this differs from 4GL, CASE tools, and Executable UML

If you have seen earlier attempts to replace code with specifications, skepticism is reasonable. Fourth-generation languages, CASE tools, and Executable UML tried to describe runtime behavior in natural language or rigid diagrams. To make those descriptions executable, they had to account for details such as loop increments, allocation, null checks, and stack unwinding. The result could become a cumbersome programming language with poor debugging support and without the type checking and compiler tooling of a conventional language.

Here the specification has a narrower job. The engineer defines the system boundary, performance limits, and domain goal. The Markdown records invariants, allowed dependencies, and failure behavior. The agent uses its knowledge of the language and libraries to write ordinary source code. Then the compiler checks syntax and types, and the tests check the behavior. When a check fails, its concrete error output goes back to the agent for another pass.

The card does not need to explain how to loop over an array, parse JSON, or manage an ordinary buffer. It should say what the code must preserve: domain invariants, dependency boundaries, latency limits, and error contracts. That keeps the document useful without turning it into another programming language.

The checks are essential. Markdown alone leaves room for misinterpretation. Compilation, static type checks, and automated tests catch mistakes in the generated result (see [[Testing in the Model, Agent, LLM Era]]). A broken type contract should fail in the compiler; a violated behavior should fail in the tests. The agent can use those failures to correct its implementation. Architectural rules need suitable checks too, if you expect a violation to be caught automatically.

## Discover the specification while building the component

Trying to write a perfect specification before touching the code usually fails. In an event pipeline, a cache, or an integration with a poorly documented API, some requirements only become clear when the code runs. You find a connection pool limit, a rate limit, a serialization problem, or a race between lifecycle events. The document should record what you learned through that work.

The sequence is practical:

1. **Explore the unclear parts.** Give the agent small tasks, inspect its code, and use quick tests to expose behavior and edge cases.
2. **Get an implementation working.** Check the cases you found and run the unit and integration tests.
3. **Capture the decisions immediately.** Once the design has settled and the tests pass, ask the agent to write an Operation Card with the rules, dependencies, and decisions uncovered during implementation.
4. **Try the card in a fresh session.** Give another agent session the card and the tests, then ask it to make a small change. If it breaks an invariant or adds a forbidden package, clarify the card and commit the revision.

That third step matters. Without it, the reasoning behind the component stays in a chat history that the next agent may never see. It has to reconstruct the rules from source code and may miss an edge case that took real effort to discover. The fresh-session check tells you whether the card actually carries enough information for the next change.

## Use short cards to keep the relevant rules in view

A large context window does not make a large prompt automatically useful. The more unrelated code you load, the more work the agent has to do to find the contract that matters. It may also copy a nearby workaround or old convention because it looks like the local pattern (see [[How Context Narrows an AI's Solution Space]]).

| What you give the agent | Approximate context | What the agent must do | Risk |
| :--- | :--- | :--- | :--- |
| 15–30 source files | 15,000–40,000 tokens | Infer the rules among implementation details | Miss a subtle constraint or copy a legacy workaround |
| One in-flight card and the target file | A 300–800-token card plus code | Apply explicit contracts and interfaces | Less room to drift outside the documented boundaries |

A targeted card can reduce prompt size, time to first token, and token cost over repeated agent runs. More importantly, it puts the key constraints close to the task instead of burying them in a large collection of files. This is a reason to keep cards concise and specific, even when the model accepts hundreds of thousands of tokens.

## What an Operation Card contains

An Operation Card should tell the next engineer or agent why the component exists and what it must not break. It identifies the files to inspect, the dependencies it may use, and the expected response to failure. It does not restate the implementation line by line.

```markdown
### Operation: ProcessPaymentSettlement

**Purpose:** Coordinate credit card settlement with external payment gateways
and record ledger journal entries.

**Boundary rules:**
- Retrying with the same `TransactionId` must be safe.
- Do not write directly to Ledger tables; emit a `SettlementCompleted` domain event.
- Limit external gateway calls to 5000 ms.

**Files to inspect:**
- Orchestrator: `billing/settlement_coordinator`
- External client: `billing/gateways/stripe_client`
- Event contract: `billing/events/settlement_completed`
- Tests: `tests/billing/settlement_coordinator_test`

**Dependencies:**
- Allowed: gateway client, clock service, structured logger.
- Forbidden: shopping cart storage, direct user session store.

**Failure behavior:**
- Timeout: mark the transaction `PendingReconciliation` and emit an operational metric alert.
- Validation failure: return `DomainValidationError` immediately; do not retry.
```

When the next agent changes settlement processing, this card gives it the constraints and points it to the relevant code. It no longer has to scan five directories just to guess which component owns a ledger update or how a gateway timeout is handled.

## Working rules for the team

1. **Let the agent draft operational documentation when the code settles.** Have it write the Operation Card once the implementation and tests are in good shape. Engineers review and refine the rules instead of reconstructing the whole document by hand later.
2. **Use cards to state structural rules.** Record where code belongs, which dependencies are allowed, and how failures must be handled.
3. **Keep tests beside the written rules.** The Markdown states the intent; compilation and tests check the implementation against contracts they can verify.
4. **Be deliberate about context.** Give the agent the small set of cards and files it needs. A huge context window is not a reason to paste the whole repository into every task.
5. **Record boundaries as new code is added.** This gives later agent sessions a way to follow the design instead of adding another local variation (see [[Software Decay and the Hidden Costs of Frictionless AI Code]]).

## Related notes

- **[[Testing in the Model, Agent, LLM Era]]** — How compilers and tests verify the implementation behind a Markdown specification.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]** — How repository layout, module boundaries, and interface contracts change when agents read and write the code.
- **[[Reviewing AI-Generated Code]]** — How engineers combine short design notes with focused diff reviews to understand changes without writing every line.
- **[[AI-Generated Architectural Documentation from Code]]** — The reverse workflow: extracting an initial architectural description from an existing codebase.
- **[[Comments May Become More Valuable in AI-Generated Code]]** — Why domain intent, hardware quirks, and business rules that cannot be inferred from code belong in comments and companion cards.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]** — How standard cards can help prevent agent-generated complexity from spreading.
- **[[Designing Software for AI Agents]]** — Architectural patterns that make code easier for agents to find, isolate, and modify.
