---
title: Comments May Become More Valuable in AI-Generated Code
tags:
  - ai-agents
  - software-engineering
  - documentation
  - code-review
  - maintainability
  - intent-specification
aliases:
  - Code Comments in AI Era
  - Semantic Value of Comments in AI Code
---

The traditional rule of thumb for comments has always been straightforward:

> Good code explains what it does. Comments explain why.

As software engineering shifts toward systems written, refactored, and maintained by AI agents, that distinction stops being a stylistic preference and becomes a fundamental design constraint.

An LLM can reconstruct the mechanics of an abstract syntax tree almost instantaneously. It does not need a comment that merely restates what the code is already executing.

Consider this:

```csharp
// Charge 50% if booking starts in less than 3 days.
if (booking.StartDate < DateTime.UtcNow.AddDays(3))
{
    cancellationFee = booking.TotalPrice * 0.5m;
}
```

The comment burns tokens without adding a single bit of useful entropy. It simply mirrors the syntax.

Now consider the alternative:

```csharp
// Cancellations within 72 hours are charged 50% because the supplier
// no longer refunds us after this point.
// Do not replace this with the standard hotel cancellation policy.
```

The code handles the operational mechanism. The comment preserves the latent context that cannot be derived by static analysis or AST inspection:

- Why the business rule exists in the first place.
- The external boundary condition (the supplier contract) driving the logic.
- Confirmation that this is an intentional carve-out, not an oversight.
- The exact domain constraint being enforced.
- The trap: a seemingly obvious, clean refactoring that would silently break business invariants.

---

## Code Is Self-Documenting Syntactically, Not Semantically

Clean code practices teach us to write descriptive, expressive method names:

```csharp
ApplyNonRefundableSupplierCancellationFee();
```

This is infinitely better than an obscure helper method, but it still falls short on semantics. Looking at that signature alone, you cannot determine:

- Why this specific supplier requires custom handling while others do not.
- Whether this logic is bound to a hard contractual SLA or a temporary operational workaround.
- Which specific product lines or inventory feeds this rule applies to.
- Whether a similar-looking policy elsewhere in the codebase can be safely consolidated with this one.
- What implicit assumptions the implementation makes about upstream state.

Historically, this business context lived across fragmented human channels:

- In the heads of the two engineers who originally built the integration.
- Buried inside resolved Jira tickets.
- Scattered across archived Slack threads.
- In design meeting notes that nobody cataloged.
- In outdated Confluence specifications.
- In enterprise architecture documents that drift out of sync with every release.

When an agent is tasked with modifying this code, it rarely has access to those external silos. Even if it has an enterprise search tool, it rarely knows what to search for.

A comment anchored directly above the implementation has a decisive architectural advantage:

> Whenever the relevant code is loaded into an agent's context window, the business context is loaded alongside it.

---

## Comments Can Act as Local Context Retrieval

Imagine an agent receives an incoming task:

> Support partial cancellations on multi-room bookings.

The agent's retrieval mechanism—whether driven by Language Server Protocol symbols, ripgrep, or vector-based embeddings—pulls the cancellation domain classes into its context window.

Any comments embedded within those classes are automatically pulled into the same prompt.

```text
Task: "Add partial cancellation support"
                      │
                      ▼
             LSP / File Retrieval
                      │
                      ▼
┌──────────────────────────────────────────────┐
│ CancellationService.cs                       │
│                                              │
│  // Local context retrieved automatically    │
│  // No external RAG or wiki lookups required │
│  ApplyNonRefundableSupplierCancellationFee() │
└──────────────────────────────────────────────┘
```

This effectively turns the codebase into a distributed, micro-localized knowledge base.

By colocating context with code, you eliminate retrieval failure. The agent does not need to know:

- That an Architectural Decision Record (ADR) was drafted three quarters ago.
- Which product specification outlines the cancellation tier rules.
- Which Jira issue tracked the supplier billing bug.
- What search query will surface the edge-case discussions in the team wiki.
- Which team retro discussed the vendor's payment quirks.

The knowledge sits precisely at the execution point. For an LLM navigating strict context budgets, co-locating business context with the implementation is the most deterministic retrieval strategy you can deploy.

---

## Documentation Layers Still Have Different Roles

This does not mean comments should swallow your entire documentation stack. Each layer still serves a distinct operational purpose:

```text
Specification
    │
    ▼
Describes desired system behavior and product requirements.

Architecture Decision Records (ADRs)
    │
    ▼
Document system-wide trade-offs, boundaries, and architectural patterns.

Business Comments
    │
    ▼
Preserve local intent, boundary constraints, and domain exceptions.

Executable Code
    │
    ▼
Provides the deterministic, runnable implementation.
```

During greenfield development, an agent might operate with the complete product specification loaded into its context window. It has the total picture.

Fast forward two years. A different agent receives a targeted prompt to patch a concurrency bug in a single file. That agent is operating with a tightly scoped context window containing only a few related classes. The original specification is absent. The architecture docs may not match the retrieval query.

The local comment is the only layer of context that survives the handoff.

---

## Negative Knowledge May Be Especially Valuable

Some of the highest-leverage comments describe **negative knowledge**—explicit documentation of what *not* to do, and why an intuitive refactoring is a trap.

Consider this edge case:

```csharp
// Do not calculate this from Payment.Amount.
// Legacy bookings may already contain the agency margin there.
```

Or this defense against a dirty upstream API:

```csharp
// This check looks redundant, but some suppliers occasionally send
// the same reservation with different external IDs.
```

Or an intentional sequence break:

```csharp
// Intentionally executed before availability validation.
// Sales requires the original quoted price to remain available
// even when availability subsequently fails.
```

Negative knowledge is Chesterton’s Fence for software systems. It communicates that an apparent anomaly is not technical debt—it is an intentional defense against an external reality.

This is critical when working with LLMs. Coding agents are strongly biased toward consistency, pattern matching, and eliminating perceived dead weight.

An agent analyzing an undocumented idiosyncrasy follows a predictable loop:

```text
Unusual branching logic detected
    │
    ▼
Evaluated as redundant or suboptimal
    │
    ▼
Refactored and simplified
    │
    ▼
Production outage or contract breach
```

When you document the negative space, the agent’s reasoning changes entirely:

```text
Unusual branching logic detected
    │
    ▼
Comment identifies an explicit external constraint
    │
    ▼
Logic recognized as intentional defense
    │
    ▼
Implementation preserved during refactoring
```

---

## Clean Code Does Not Eliminate Business Context

The dogmatic Clean Code claim that "comments are always an admission of failure" holds true only when comments explain basic programming mechanics.

A comment like this is noise and should be flagged in code review:

```csharp
// Iterate through users.
```

But you cannot rename a function enough to encode an entire commercial reality without creating absurd, unreadable abstractions.

Take this method:

```csharp
IsEligibleForLegacyCancellationCompensation()
```

The name is clean. It clearly communicates *what* predicate is being evaluated. But it tells you nothing about *why* the legacy policy exists, who funded the compromise, or when it can safely be deprecated.

The operational rule for engineering teams shifts from broad comment elimination to precise context triage:

- **Strip out** comments that explain implementation mechanics, control flow, or language constructs.
- **Aggressively preserve** comments that capture business intent, domain invariants, edge-case constraints, and non-obvious trade-offs.

---

## Agents Can Produce Their Own Future Context

This dynamic opens up a practical workflow: agents should write the very context that future agents will depend on.

When an agent implements a feature, it possesses the maximum possible context. It has the ticket, the domain spec, the edge cases, and the acceptance criteria loaded directly in memory.

Rather than compressing that specification entirely into executable code and throwing the rest away, the agent can distill the non-obvious domain rules directly into the code as persistent intent comments.

A solid system prompt rule looks like this:

> Whenever the implementation encodes a non-obvious business rule, invariant, exception, or constraint that cannot be reconstructed from the code itself, preserve that information as a concise comment adjacent to the relevant logic.

The lifecycle then moves from a lossy translation to a durable artifact:

```text
Task Specification
       │
       ▼
     Agent
    ┌──────┴──────────────────────────────────────┐
    ▼                                             ▼
Clean Code                     Durable In-Situ Intent Comments
(Executable Mechanics)         (Constraints, Invariants, Trade-offs)
```

The code drives the runtime. The comments preserve the semantic reasoning that keeps the runtime from being broken during the next maintenance pass.

---

## Designing Code for Agentic Maintenance

Historically, we reviewed comments with a human peer in mind: *Will a mid-level engineer on-call understand this at 2:00 AM?*

In agent-driven development, you have a second target consumer: *a language model operating on a partial slice of the repository with zero external organizational context.*

That shifts how we review pull requests. The question is no longer just readability. It becomes:

> If an LLM reads only this file two years from now, what incorrect inferences will it make about this system?

Targeted comments protect the system against those hallucinations and naive optimizations.

This does not mean stuffing files with wall-to-wall text. It means running a deliberate context engineering pass over the code you commit. Focus directly on documenting:

- **Origin:** Why a specific rule or branch exists.
- **Domain meaning:** The commercial or physical reality that the code maps to.
- **Invariants:** Conditions that must remain true, even if they look inefficient.
- **Defensive anomalies:** Why an unusual implementation pattern was used deliberately.
- **False simplifications:** Obvious refactorings that have already failed in production.
- **External friction:** Upstream API bugs, hardware limitations, or vendor contracts driving the structure.
- **Hidden assumptions:** Invariants that future modifications must not violate.

Viewed through this lens, comments are no longer just human notes. They are hard token-level context anchors embedded directly into the executable codebase.

---

## Redefining Low-Level and Architectural Documentation

The ability of LLMs to parse, explain, and trace execution paths on demand fundamentally reorganizes how we should approach software documentation.

### 1. The Obsolescence of Mechanical Documentation
Comments explaining *how* an algorithm works, what a private helper does, or what order operations execute in are completely obsolete. They add no value. If an engineer or an agent needs to trace code paths, calculate cyclomatic complexity, or parse data transformations, the model can synthesize that from the raw code instantly.

Similarly, architectural diagrams that merely document static directory structures or basic service-to-service routing are disposable. They drift out of sync immediately and can be dynamically generated on the fly via code analysis whenever needed.

### 2. The Shift from Descriptive Docs to Decisional Guardrails
Documentation must pivot from *describing mechanics* to *recording decisions*:

```text
Descriptive Docs (Obsolete)         Decisional Guardrails (Critical)
───────────────────────────         ────────────────────────────────
• How the auth loop runs            • Why OAuth was picked over SAML
• Data flow across services         • Hard performance/latency budgets
• Step-by-step method descriptions  • Unstated non-functional requirements
• Class relationship charts         • Upstream contract guarantees
```

Broad system architecture documentation remains vital, but only when focused on system constraints, operational guardrails, and explicit trade-offs—such as ADRs and throughput budgets. At the micro level, localized comments preserve the business invariants.

Everything between those two poles—the mechanical descriptions of what the code is already doing—is just noise to be filtered out.
