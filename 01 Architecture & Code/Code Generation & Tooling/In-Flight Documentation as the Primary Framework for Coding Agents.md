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

# Write the documentation while the coding agent still has the decisions in context

## Capture the decisions as part of implementation

Documentation often comes after the code. By then, the engineer has moved on, and writing up last week's implementation feels like a separate task. The document soon falls behind. People rely on what they remember, unwritten conventions, and class hierarchies that take time to untangle.

A coding agent gives us a better moment to write it. While implementing a feature, it already has the relevant types, code structure, boundaries, and edge cases in context. Ask it to record the decisions while they are still in view. The engineer then spends almost no extra time reconstructing them later, and the extra model work is small compared with rediscovering the design in another session.

That changes how I would use documentation:

1. **Write it during implementation.** Record the rules while the agent is working through them, before the reasoning disappears into an old chat.
2. **Explain the component in Markdown.** A short account of its contracts is easier for an agent to follow than a deep inheritance tree, reflection, or framework magic (see [[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]).
3. **Use it to guide the next change.** Without written rules, the next agent may invent a helper, add an unapproved dependency, or choose a different architectural pattern. A specification narrows the valid choices.
4. **Keep the important decisions close to the task.** A 40-line card can state a component's intent more clearly than twenty source files from which the agent has to infer it.

## Start the next change from the specification

A conventional build takes source code through a compiler and type checker to produce a program. With an agent in the workflow, a Markdown specification can sit one step before the source code:

```text
Conventional build:
Source code → compiler / type checker → executable

Agent workflow:
Markdown specification → coding agent → source code → compiler / tests → working system
```

Think of the Markdown as a description of the system at a higher level. The agent writes the source code from it; automated checks verify the code, and engineers review it. In this workflow, source code is an intermediate result. This is an analogy for organizing the work, not a claim that the agent replaces a compiler.

The engineer still decides which rules the agent must follow: which component owns a state change, which dependencies it can call, and what to do when an operation fails. The clearer the contract, the less room the agent has to choose incorrectly. When a business rule changes, update the specification and ask the agent to refactor the code against the existing tests. That may be faster than tracing the same rule through several files by hand.

A lead engineer can then review a compact specification alongside the relevant diff and keep a clear picture of the architecture without writing every line of routine code (see [[Reviewing AI-Generated Code]]).

## Why this is different from 4GL, CASE tools, and Executable UML

If you remember earlier attempts to replace code with specifications, the skepticism makes sense. Fourth-generation languages, CASE tools, and Executable UML tried to describe runtime behavior in natural language or rigid diagrams. To execute those descriptions, they had to cover details such as loop increments, allocation, null checks, and stack unwinding. The specification could become a cumbersome programming language with poor debugging support and without the type checking and compiler tooling of a conventional language.

This specification has a smaller job. The engineer defines the system boundary, performance limits, and domain goal. The Markdown records invariants, allowed dependencies, and failure behavior. The agent uses its knowledge of the language and libraries to write ordinary source code. The compiler checks syntax and types; tests check behavior. When a check fails, the agent gets the concrete error output and tries again.

The card does not have to teach the agent how to loop over an array, parse JSON, or manage an ordinary buffer. It has to say what the code must preserve: domain invariants, dependency boundaries, latency limits, and error contracts. That keeps the document useful without turning it into another programming language.

Markdown can still be misunderstood. Compilation, static type checks, and automated tests have to check the resulting code (see [[Testing in the Model, Agent, LLM Era]]). A broken type contract should fail during compilation; a behavior that violates a rule should fail a test. The agent can work from those failures. If you want an architectural rule enforced automatically, it needs an appropriate check as well.

## Learn the rules while building the component

Writing a perfect specification before touching the code rarely works. In an event pipeline, a cache, or an integration with a poorly documented API, some requirements only show up when the code runs. You might find a connection pool limit, a rate limit, a serialization problem, or a race between lifecycle events. Put what you learn back into the document.

A practical sequence looks like this:

1. **Explore what you do not yet know.** Give the agent small tasks, inspect its code, and run quick tests to expose behavior and edge cases.
2. **Get the implementation working.** Check the cases you found, then run the unit and integration tests.
3. **Keep the card current.** After each code change, check whether it introduces, changes, or removes a rule that the card must preserve. Add what was learned and remove rules that belonged only to an abandoned approach.
4. **Test the card in a fresh session.** Give another agent session the card and the tests, then ask for a small change. If the agent breaks an invariant or adds a forbidden package, clarify the card and commit that revision.

The third step keeps the reasoning from being stranded in a chat history the next agent may never see. Otherwise, it has to recover the rules from code and may miss an edge case that took real effort to discover. The fresh-session change tells you whether the card contains enough information to guide the next task.

## Rebuild from the current decisions when the code carries old attempts

Several rounds of changing the design can leave code that still works but no longer expresses the final design cleanly. An unused helper is easy to notice in a diff when it first appears. Months later, a leftover field or a roundabout data path is simply part of the existing code. An agent working on another task may treat it as intentional and build around it. Ordinary review of the latest diff will not draw attention to that old line.

This is a reason to check the card after *every code change*, not merely write one when the implementation settles. The check does not require documenting every line of code. It asks whether the change revealed or altered behavior, interfaces, ownership, or constraints that the next implementation must preserve. Add those decisions to the card. When a decision changes, replace the old rule there; keep the reason for rejecting it in the engineering history if it may matter later. Before discarding the code, compare the card with the working implementation, tests, and recorded discoveries. Resolve any gaps while the code is still available. The card should describe what must be rebuilt, not the sequence of attempts that happened to produce it.

Once the current card captures those decisions, a larger reset becomes possible: revert the accumulated implementation, give the agent the card and independent checks, and build the code again without the abandoned versions in view. This need not stop at one function or file. If the design changed across a whole module, the module can be rebuilt from the current rules. The fresh implementation still needs compilation, tests, and review against the card. This tests whether the recorded intent can reproduce the required behavior, rather than assuming that passing tests or a plausible note proves completeness (see [[Correcting AI-Generated Code — Patch, Regenerate, or Change the Specification]]).

## Give the agent a short card and the relevant code

A large context window does not make a large prompt useful by itself. The more unrelated code you load, the more the agent has to sift through to find the contract that matters. It may copy a nearby workaround or an old convention simply because it looks like the local pattern (see [[How Context Narrows an AI's Solution Space]]).

| What you give the agent | Approximate context | What the agent must do | Risk |
| :--- | :--- | :--- | :--- |
| 15–30 source files | 15,000–40,000 tokens | Infer the rules from implementation details | Miss a subtle constraint or copy a legacy workaround |
| One card written during implementation and the target file | A 300–800-token card plus code | Follow explicit contracts and interfaces | Less room to drift outside the documented boundaries |

A focused card can reduce prompt size, time to first token, and token cost across repeated runs. More importantly, it puts the constraints next to the task instead of burying them among source files. Keep cards short and specific even if the model accepts hundreds of thousands of tokens.

## What to put in an Operation Card

An Operation Card should tell the next engineer or agent why a component exists and what a change must preserve. Point to the files worth reading, list the dependencies the component may use, and spell out what happens on failure. Do not describe the implementation line by line.

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

When the next agent changes settlement processing, the card gives it the constraints and directs it to the right code. It does not have to search five directories to guess who owns a ledger update or what to do after a gateway timeout.

## Rules for using the cards on a team

1. **Check the card after every code change.** Update it when the change alters a decision or reveals a rule that the next implementation must preserve. Engineers check that the current rules and discoveries are present before treating the card as a basis for future changes or regeneration.
2. **State structural rules explicitly.** Record where code belongs, which dependencies it may use, and how failures must be handled.
3. **Keep tests alongside the written rules.** Markdown says what the code is meant to do. Compilation and tests check the parts of that contract they can verify.
4. **Choose context deliberately.** Give the agent the few cards and files it needs. A huge context window is no reason to paste the whole repository into every task.
5. **Record boundaries as you add code.** Later sessions can then follow the design instead of introducing one more local variation (see [[Software Decay and the Hidden Costs of Frictionless AI Code]]).

## Related notes

- **[[Testing in the Model, Agent, LLM Era]]** — How compilers and tests verify the implementation behind a Markdown specification.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]** — How repository layout, module boundaries, and interface contracts change when agents read and write the code.
- **[[Reviewing AI-Generated Code]]** — How engineers combine short design notes with focused diff reviews to understand changes without writing every line.
- **[[AI-Generated Architectural Documentation from Code]]** — The reverse workflow: extracting an initial architectural description from an existing codebase.
- **[[Comments May Become More Valuable in AI-Generated Code]]** — Why domain intent, hardware quirks, and business rules that cannot be inferred from code belong in comments and companion cards.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]** — How standard cards can help prevent agent-generated complexity from spreading.
- **[[Designing Software for AI Agents]]** — Architectural patterns that make code easier for agents to find, isolate, and modify.
