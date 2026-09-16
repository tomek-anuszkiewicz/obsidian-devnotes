# Consolidated Reference Restored Notes (Practitioner Voice & Tone)

This document aggregates the reference set of notes rewritten under the practitioner-voice-and-tone.md standard.

---

# Note: Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize

---
title: Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize
tags:
  - ai-agents
  - code-review
  - software-engineering
  - quality-assurance
  - static-analysis
  - compliance
  - review
aliases:
  - Natural-Language Rules as Executable Policies
  - Agentic Review Rules
  - Semantic Code Review
---

Traditional software quality automation works best when a rule can be expressed as a deterministic boolean:

```text
Domain must not reference Infrastructure.
Every public endpoint must require authorization.
Result must never be negative.
All handlers must implement a particular interface.
```

We already have great tools for these. You encode them into your CI pipeline using:

- Unit and integration tests
- Architecture tests (ArchUnit, NetArchTest)
- Static analysis tools and compiler passes
- Linters and AST-based rule engines
- Strong type systems

This layer of deterministic verification is non-negotiable. It runs fast, costs almost nothing per execution, and provides ironclad regression boundaries.

However, a massive portion of software engineering has never cleanly fit into this model. Many of our most critical rules aren't difficult because engineers fail to understand them; they are difficult because writing a programmatic parser or static analyzer to enforce them is either brutally complex or practically impossible.

LLM-based review agents give us an automated mechanism for this previously human-only layer.

---

## Many Real Engineering Rules Are Semantic

Consider the architectural heuristics senior engineers use every day:

> Do not introduce an abstraction unless it represents a meaningful, reusable boundary.

> Controllers should remain thin, but a trivial request mapping does not need an intermediate service layer just to satisfy a layered architecture diagram.

> Modules must communicate through public contracts rather than reaching into peer module internals.

> Do not build a generic framework for a problem that exists in exactly one place.

> Core business rules must remain visible in domain entities rather than being buried inside persistence or messaging helpers.

These are legitimate architectural requirements. A tech lead can look at a pull request and spot a violation within thirty seconds. Yet writing a deterministic static analyzer or compiler rule to catch them is a nightmare. 

The issue is not a lack of architectural rigor. The issue is that the rule depends on:

- **Developer intent:** Why was this class extracted?
- **Context:** Is this a core billing domain or a throwaway export utility?
- **Naming and domain language:** Does this method name accurately describe a business transition, or is it a generic CRUD mutation?
- **Surrounding topology:** How does this change affect the downstream consumer contracts?
- **Nuance and degree:** Is this controller method slightly too fat, or has it completely absorbed business orchestration?

Historically, enforcing these principles required human attention. If a senior engineer didn't catch them during a code review, they slipped into master.

---

## Human Attention Was the Missing Runtime

Open up almost any system repository and you will find an architecture document, a wiki, or an ADR directory containing rules like this:

```text
Prefer explicit dependencies over service locators or ambient context.
Avoid leaking persistence concerns into the domain model.
Do not create premature abstractions.
Cross-module access must happen through defined contract packages.
```

The engineering team typically agrees with these statements. But markdown files do not execute. 

In practice, the runtime execution engine for these rules has always looked like this:

```text
developer remembers the rule
        +
reviewer remembers the rule
        +
reviewer actively spots the violation in an 800-line diff
```

This runtime is remarkably fragile. Even your best engineers run into structural limits:

- They get fatigued at the end of a sprint.
- They skim large, mechanical refactors or generated diffs.
- They focus on an obvious SQL injection or syntax issue and miss a subtle boundary leak.
- They are constrained by time and context-switching between their own tickets and reviewing pull requests.
- They do not evaluate every single PR with identical depth.

A review agent changes the baseline economics of this process. It can execute the exact same policy against every single commit without degradation. The architecture document stops being passive shelfware and becomes an active, executing quality gate.

---

## Natural-Language Rules Can Become Executable Policies

Suppose your repository contains an established architectural baseline:

```text
docs/architecture/principles.md
docs/domain/invariants.md
docs/security/guidelines.md
docs/performance/guidelines.md
ADRs/
```

You can feed these specifications directly into an agentic review step in your CI pipeline. For every pull request, the agent evaluates the incoming diff against the documented standards:

```text
Evaluate this diff against the repository's architectural guidelines:

1. Identify concrete code segments that violate documented principles.
2. Link the finding directly to the specific guideline or ADR.
3. Explain the technical trade-off and why the current approach breaks the rule.
4. Check for explicitly documented exceptions before flagging.
5. Provide a confidence score for the violation.
6. Suppress comments if the confidence score is below threshold or evidence is weak.
```

This is not an executable specification in the sense of a Gherkin feature file or a unit test. It is a natural-language executable policy. 

The practical shift here is profound: **you no longer need to spend two weeks writing a bespoke AST analyzer or Roslyn plugin to make a rule automatically enforceable in CI.**

---

## Expanding the Automatable Surface Area

Historically, our quality pipeline was divided into two distinct buckets:

```text
Formalizable rule
    -> CI Automation (Linters, Compilers, Unit Tests)

Non-formalizable rule
    -> Human Review (PR comments, pairing, architectural reviews)
```

Integrating review agents introduces an intermediate layer:

```text
Formalizable rule
    -> Deterministic Automation (compilers, linters, static analysis)

Semantically interpretable rule
    -> Agentic Verification (review agents, heuristic boundary checks)

Strategic or ambiguous decision
    -> Human Judgment (leads, staff engineers, product context)
```

This structural shift pulls a massive amount of low-leverage inspection work out of the human review queue. An agent can reliably flag scenarios like:

- An abstraction that wraps a single implementation without any polymorphic or testing justification.
- Leaking infrastructure dependencies (like ORM annotations or HTTP client types) into core business models.
- An inconsistent error-handling pattern that breaks conventions used across the rest of the service.
- Accidental duplication of an existing domain utility hidden in another module.
- Public API contract changes that subtly drift away from existing REST or gRPC conventions.
- Temporary hacks or workarounds that explicitly contradict an existing ADR.
- A class or service quietly absorbing unrelated responsibilities until it violates cohesive design.

These are the precise issues senior engineers spend their energy catching in code reviews.

---

## The Value of Relentless Inspection

The primary advantage of an agent here isn't that it possesses deeper architectural wisdom than a principal engineer. The advantage is that **it does not get tired.**

A tech lead might know twenty core architectural rules inside and out, but when reviewing a 40-file PR at 5:30 PM on a Friday, they might only consciously evaluate three of them.

An agent evaluates all twenty rules, across every file, on every PR, every single time. It doesn't care that:

- The diff is 1,500 lines of repetitive boilerplate.
- It is reviewing its sixtieth pull request of the day.
- A particular rule has passed cleanly without a single violation for six months.
- The change spans across five different module boundaries.

Humans are notoriously bad at monitoring high-frequency pipelines for low-probability events. If an architectural violation only happens in 1 out of every 200 pull requests, human vigilance will inevitably drop to near zero. A machine will inspect the 200th pull request with the exact same fidelity as the first.

---

## Agents Must Understand Deterministic Invariants

There is a risk in drawing too hard of a boundary between:

```text
tests handle the simple checks
LLMs handle the complex architecture
```

An effective review agent must understand the deterministic invariants of the system, even if those invariants are already guarded by test suites.

Take a classic invariant:

```text
A price must never be negative.
```

You probably already have unit tests verifying this invariant across your calculation engines. But a review agent inspecting incoming business logic still needs to understand this constraint. If the agent doesn't know that prices cannot be negative, its mental model of the system's business boundaries is broken.

The relationship between the two should be structured like this:

> **Deterministic tools are the authoritative execution engine; the review agent must understand what those tools are enforcing and why.**

When an agent understands the formal invariants, it can reason proactively:

```text
This code branch calculates an adjusted discount. Under certain edge conditions, 
it appears mathematically capable of yielding a negative balance. 

There is an explicit invariant in this domain that prices cannot be negative.

I need to flag this risk and verify whether the existing test suite exercises 
this boundary condition.
```

The deterministic test provides the final, unarguable proof, but the agent identifies the risk vector before the code ever hits production.

---

## Formal Rules Must Remain Deterministic

If an invariant can be validated cheaply, rapidly, and unambiguously in code, keep it in code:

```csharp
Assert.True(result >= 0);
```

Replacing that assertion with an LLM prompt asking:

```text
Does result appear to be greater than or equal to zero in this code path?
```

is an architectural regression.

Deterministic assertions provide properties that probabilistic agents cannot match:

- Execution times measured in microseconds.
- Zero marginal token cost.
- 100% reproducible outcomes across runs.
- Absolute precision.
- Simple, local debugging when a check fails.
- Complete isolation from model drift or hallucination.

Review agents should sit on top of deterministic infrastructure, not replace it.

> **Formalize everything that is cheap and practical to formalize. Use review agents where formalization is too expensive, brittle, or context-dependent.**

---

## Bridging the Formal and the Semantic

The real leverage emerges when an agent operates simultaneously across both the formal mechanics and the semantic intent of the codebase.

Consider an architectural boundary rule:

> Module A must not depend on Module B's persistence model.

You might enforce this with an ArchUnit rule that fails the build if any class in `Namespace.ModuleA` imports `Namespace.ModuleB.Infrastructure`.

Now, look at what an engineer does to work around that restriction when rushed:

```text
ArchUnit passes: 
There is no forbidden namespace or assembly reference.

However, Module A introduces an internal DTO that mirrors the exact column layout 
and relations of Module B's internal database tables, querying them through a raw SQL view.
```

The deterministic test passes completely. The AST is clean. But the architectural intent—decoupling the modules at the data-storage layer—has been completely subverted.

The review agent spots this because it operates at the semantic level:

```text
Warning: While this change does not directly import Module B's persistence namespace,
OrderQueryService is mapping directly to the underlying schema of Module B's 
internal ledger tables via a raw query. 

This violates the boundary established in ADR-008. Module A must consume the 
LedgerClosedEvent or query the ILedgerQueryContract interface.
```

The same dynamic plays out in core logic. Take a deterministic invariant:

```csharp
// Unit test:
[Fact]
public void Price_Cannot_Be_Negative()
{
    Assert.Throws<ArgumentException>(() => new OrderItem(sku, -10m));
}
```

A developer changes an upstream pricing calculator to bypass this exception:

```csharp
public decimal CalculatePrice(CartItem item)
{
    var rawPrice = item.BasePrice - item.Discount;
    return Math.Max(0, rawPrice); // Clamping negative values
}
```

The unit test passes. No exception is thrown. The system meets the technical constraint. 

A review agent, however, can call out the semantic flaw:

```text
Warning: Negative price calculations are being clamped to zero via Math.Max(0, rawPrice). 
While this satisfies the non-negative invariant in OrderItem, it silently masks an 
invalid business state where discounts exceed the base item price without a 
promotional override.
```

Deterministic verification catches the syntax and the explicit assertions; the agent evaluates whether the implementation honors the underlying engineering and business intent.

---

## Escalating Semantic Findings to Deterministic Automation

Agentic review serves as an ideal staging ground for identifying rules that ought to be formalized.

If your review agent repeatedly flags the same structural violation:

```text
PR #102: Direct dependency added from Domain to Infrastructure.
PR #108: Direct dependency added from Domain to Infrastructure.
PR #115: Direct dependency added from Domain to Infrastructure.
```

The engineering lead should not keep spending tokens and review cycles on that finding. That is the signal to codify the rule into a deterministic gate:

```text
Informal team convention
        │
        ▼
Review agent catches violations across PRs
        │
        ▼
Pattern stabilizes and boundaries are clearly defined
        │
        ▼
Codified into an ArchUnit rule, ESLint plugin, or custom analyzer
        │
        ▼
Enforced authoritatively at compile/test time in CI
```

Review agents operate as the scout layer. They identify the rough edges, surface repeated patterns, and help you determine where building deterministic tooling is actually worth the investment.

---

## Adding Context to Deterministic Failures

The reverse pipeline is just as valuable. When a deterministic test breaks, the output is often an opaque stack trace or a cryptic AST analyzer violation:

```text
Error: ArchUnit failure. Rule 'classes that reside in a package '..domain..' 
should not depend on classes that reside in a package '..infrastructure..'' 
was violated (1 times):
Class <com.billing.domain.BillingService> references 
class <com.billing.infrastructure.S3InvoiceStorage>
```

To a junior engineer or someone unfamiliar with the architectural history, this can feel like an arbitrary annoyance. They might try to bypass it with reflection, dynamic loading, or loose typing.

The agent can intercept this failure and attach real engineering context:

```text
Architecture Test Failure Explanation:

BillingService directly injects S3InvoiceStorage, violating our hexagonal architecture boundary. 

Why this matters:
The domain layer must stay independent of specific cloud storage implementations so we 
can test billing logic in-memory without spinning up LocalStack or mocking S3 clients.

How to resolve:
1. Define an interface in com.billing.domain (e.g., InvoiceStoragePort).
2. Have S3InvoiceStorage implement that interface in com.billing.infrastructure.
3. Inject InvoiceStoragePort into BillingService via the constructor.
```

The test runner provides the deterministic guarantee; the agent provides the context and remediation path.

---

## Ephemeral Diagnostic Tests

Our standard approach to automated testing has always been cumulative:

```text
Write a test -> Commit the test -> Maintain that test in CI forever
```

This model works for regression suites, but it creates a maintenance tax. Over time, test suites become bloated with hyperspecific tests written to catch one-off edge cases that rarely recur.

An agent can treat tests as temporary investigative instruments.

Consider an agent reviewing a complex, stateful concurrency change:

```text
Hypothesis: 
The double-checked locking implementation in ConcurrentCache.cs could lead to 
uninitialized memory reads under high reader concurrency.
```

Instead of simply leaving a speculative comment, the agent spins up an ephemeral test script designed to reproduce the race condition:

```csharp
// Ephemeral diagnostic script generated by agent
[Fact]
public async Task Verify_Concurrent_Initialization_Race()
{
    var cache = new ConcurrentCache<string, object>();
    var barrier = new Barrier(50);
    var tasks = Enumerable.Range(0, 50).Select(_ => Task.Run(() => {
        barrier.SignalAndWait();
        return cache.GetOrAdd("key", () => new object());
    }));
    
    var results = await Task.WhenAll(tasks);
    Assert.All(results, item => Assert.NotNull(item));
}
```

The agent runs this diagnostic in an isolated runner. 

```text
Agent generates targeted diagnostic test
        │
        ▼
Test reproduces race condition / proves violation
        │
        ▼
Agent provides concrete proof in PR review
        │
        ├─ If behavior is an ongoing regression risk -> Promoted to permanent test suite
        │
        └─ If one-off verification -> Discarded after confirmation
```

This draws a clean line between tests as **permanent system specifications** and tests as **disposable diagnostic tools**.

---

## Continuous Architectural Governance

Architecture drift rarely happens in a single, catastrophic pull request. It happens incrementally. A forgotten boundary here, an extra parameter added to anemic domain models there, a leaked database abstraction in a shared utility class.

Today, architectural governance is maintained through an ad-hoc mix of:

- Architecture strategy pages that nobody reads.
- Architecture Review Boards (ARBs) that meet every few weeks and bottleneck delivery.
- Senior engineers manually inspecting PRs when they have bandwidth.
- Occasional post-mortem cleanups when structural rot finally causes a major incident.

With review agents, architectural review can run continuously on every branch:

- *Did this PR create an inverted dependency?*
- *Did an internal domain object escape across an API boundary?*
- *Did someone introduce a new abstraction layer without an actual second consumer?*
- *Does this PR directly contradict an existing ADR?*
- *Is this change going to make our planned migration to split out the ordering service harder?*
- *Does this logic bypass our aggregate root to mutate state directly?*

Most of these questions cannot be answered by static linters. They require reading the diff against the broader context of the system's design.

---

## The Unified Quality Pipeline

A resilient, scalable verification pipeline combines these layers rather than trying to force everything into prompts or everything into static code:

```text
                    ┌───────────────────────────────┐
                    │       Human Judgment          │
                    │   Strategic risk, trade-offs, │
                    │   competing business drivers  │
                    └───────────────▲───────────────┘
                                    │
                                    │ Escalations & Edge Cases
                                    │
                    ┌───────────────┴───────────────┐
                    │    Agentic Semantic Review    │
                    │  ADR compliance, architecture │
                    │  drift, intent, idiomatic use │
                    └───────────────▲───────────────┘
                                    │
                                    │ Passes AST & Type Checks
                                    │
                    ┌───────────────┴───────────────┐
                    │   Deterministic Verification  │
                    │  Compilers, linters, unit     │
                    │  tests, architecture tests    │
                    └───────────────────────────────┘
```

Deterministic verification forms the concrete foundation. It guarantees that the code compiles, types align, formatting is consistent, unit contracts pass, and hard boundaries aren't crossed.

Agentic review handles the semantic translation layer. It monitors the design boundaries, spots subtle boundary leaks, reviews intent, and checks compliance with high-level architecture documents.

Humans remain at the top of the stack. They step in when trade-offs conflict—like accepting technical debt in a subsystem to hit a hard compliance deadline, or deciding when an existing architectural standard needs to be rewritten entirely.

---

## Do Not Replace Compilers with Prompts

The goal of this architectural pattern is not to dump our existing verification infrastructure into an LLM context window:

> "We have an LLM reviewing our code, so we don't need to write ArchUnit tests, linters, or granular unit tests anymore."

That throws away the most valuable asset in our engineering pipeline: **cheap, zero-variance deterministic execution.**

Use this operational framework when designing review policies:

1. **If a rule can be validated cheaply and deterministically in code:** Write the unit test, configure the linter, or write the architecture test.
2. **If a rule is semantic, contextual, or too expensive to formalize:** Pass it to an agent with clear evaluation heuristics and link it to an ADR.
3. **If an agent keeps flagging the same issue repeatedly:** Invest the engineering time to codify that finding into an automated analyzer or test.
4. **If a decision hinges on business strategy, operational risk, or architectural pivots:** Route it directly to human engineers.

---

## Scaling Senior Engineering Bandwidth

Historically, an engineering organization's standards were bounded by a simple equation:

```text
Quality of architectural enforcement 
≈ 
Available senior engineering bandwidth
```

When hiring outpaced the capacity of senior engineers to review code, architectural rot accelerated. Principles that were established during early architecture phases were gradually diluted as teams grew and PR throughput increased.

Review agents break that bottleneck. A Principal Architect can define a concrete standard once:

> "Do not hide transaction orchestrations inside infrastructure event handlers."

Instead of hoping that every engineer reads the wiki and that every reviewer remembers to look for it, that rule is embedded into the review agent's active system prompt.

The architect provides the judgment once. The agent enforces the heuristic across thousands of pull requests.

The best systems we build moving forward will balance both modes of verification: **ironclad, non-negotiable execution for rules that can be formalized, paired with scalable, semantic inspection for the rules that define the long-term integrity of our systems.**

---

# Note: Comments May Become More Valuable in AI-Generated Code

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

---

# Note: Designing APIs for LLM-Generated Integration Code

---
title: Designing APIs for LLM-Generated Integration Code
tags:
  - api-design
  - ai-agents
  - software-architecture
  - integration
  - developer-experience
  - documentation
aliases:
  - Agent-Friendly API Design
  - APIs for LLM Integrations
---

## Goal

When you bring an LLM coding agent into your codebase, your goal is rarely to have the model fire off arbitrary HTTP calls directly against a raw network endpoint. 

Instead, you want the agent to operate the same way a disciplined software engineer does:

1. Understand the incoming business requirement.
2. Discover which downstream service or capability owns that domain operation.
3. Locate the corresponding generated, strongly typed client in the repository.
4. Select the precise client method designed for that operation.
5. Author clean, maintainable application code that invokes that client correctly.

Here is the operational mental model:

```text
Business requirement
        ↓
Discover business capability
        ↓
Find appropriate client
        ↓
Find appropriate operation
        ↓
Generate application code
        ↓
Generated client
        ↓
REST API
```

By structuring the workflow this way, the agent avoids dealing with transport-level mechanics and focuses entirely on domain logic.

---

## Internal vs External APIs

To make this pattern work across a large architecture, you need to draw a clear line between internal and external APIs.

### Internal APIs

Internal APIs sit inside a tight service boundary. They:

- Reflect the internal topology and database schema of a specific service.
- Expose implementation-specific primitives and transient data models.
- Use internal representations that make sense only to the team maintaining them.
- Change rapidly, often without formal deprecation cycles.
- Rely heavily on tribal knowledge and shared assumptions baked into the service's private codebase.

### External APIs

External APIs cross team, domain, or organizational boundaries. They must:

- Expose stable, backwards-compatible contracts.
- Encapsulate internal persistence models and service mechanics completely.
- Expose explicit business capabilities rather than generic data mutations.
- Maintain compatibility over long lifecycles.
- Use ubiquitous, domain-driven terminology that external consumers understand.

This boundary is critical when working with LLM agents. An internal endpoint named `POST /service-b/v1/sync-state` gives an agent zero domain context, increasing the likelihood of hallucinations or improper usage. Conversely, an externalized, business-aligned contract gives the model an unambiguous target. The clearer the business intent behind an operation, the more reliably an agent will choose it.

---

## OpenAPI as the Source of Truth

For REST APIs, an OpenAPI specification must be more than a list of routes and JSON payloads; it needs to document the operational semantics of the system.

Take this weak specification:

```yaml
/users/{id}/sessions:
  delete:
    operationId: deleteSessions
```

From an agent's perspective, this endpoint could mean anything from "log out the current device" to "nuke the entire user profile." 

Compare that to an explicit specification:

```yaml
/users/{userId}/sessions:
  delete:
    operationId: revokeUserSessions
    summary: Revoke all active sessions for a user
    description: |
      Revokes all active authentication sessions belonging
      to the specified user.

      Use this operation when access for the user must be
      immediately invalidated.

      This operation does not delete the user account.
```

High-quality API descriptions should directly answer several key operational questions:

- What does this operation accomplish in the domain?
- Under what specific conditions should an engineer (or agent) use it?
- When should it **not** be used?
- What preconditions must be satisfied before calling it?
- What side effects does it trigger across the system?
- What are the explicit failure modes?

Negative guidance is especially effective when directing coding agents. Because models operate on probabilistic pattern matching, a word like "delete" can easily trigger an agent to call a destructive endpoint when a non-destructive state transition was required.

Explicitly ruling out incorrect paths prevents this failure mode:

```yaml
description: |
  Permanently deletes a draft invoice.

  Only draft invoices can be deleted.

  Do not use this operation for issued invoices.
  Issued invoices must be cancelled using cancelInvoice.
```

With this context in place, the agent will not mistake a hard delete for a business cancellation simply because both operations imply removing an item from a view.

---

## Prefer Business-Oriented Operations

APIs should expose domain intent rather than generic state manipulation.

Prefer explicit, domain-driven operations:

```text
cancelInvoice
revokeUserSessions
reserveInventory
approveOrder
```

Avoid vague, anemic abstractions:

```text
updateEntity
executeAction
changeStatus
processRequest
```

Standard CRUD operations are entirely appropriate when the underlying domain requirement is fundamentally CRUD. For instance, hard-deleting an uncommitted draft is genuinely a deletion:

```http
DELETE /drafts/{id}
```

However, business-critical transitions—such as cancelling an issued invoice—carry legal, audit, and domain ramifications. Modeling that lifecycle change as a basic deletion or a generic patch creates ambiguity:

```http
POST /invoices/{id}/cancel
```

The underlying architectural rule is straightforward:

> Expose business capabilities through your API, not naked database mutations.

When your API exposes business capabilities, coding agents can directly map user stories and acceptance criteria to concrete operations without having to reverse-engineer side effects.

---

## Generate Strongly Typed Clients

Coding agents should not be generating raw HTTP network calls.

Do not let an agent produce unstructured I/O like this:

```csharp
await httpClient.DeleteAsync(
    $"/users/{userId}/sessions");
```

Instead, guide the agent toward an interface backed by a strongly typed, generated client:

```csharp
await identityClient.RevokeUserSessionsAsync(
    userId,
    cancellationToken);
```

You can generate these clients directly from your OpenAPI specifications using established tooling:

- **Microsoft Kiota** for clean, lightweight, highly idiomatic SDKs.
- **NSwag** for deep .NET and TypeScript integration.
- **OpenAPI Generator** for broad, multi-language ecosystem support.

The pipeline looks like this:

```text
OpenAPI
   ↓
Client generator
   ↓
Strongly typed client
   ↓
LLM-generated application code
```

This drastically shrinks the failure surface for the agent. By relying on a generated client, the agent no longer has to hand-craft:

- URL paths and route parameter interpolations.
- HTTP verbs and status code expectations.
- Serialization and deserialization logic.
- Request and response body contracts.
- Query string formatting and encoding.

If the agent gets a method name or argument wrong, the local compiler or type-checker flags it instantly, allowing the agent to self-correct before the code ever runs.

---

## Preserve Documentation in Generated Clients

A common breakdown occurs when the client generation pipeline strips out API documentation. Your generator should be configured to preserve OpenAPI descriptions as native docstrings—such as C# XML documentation, TypeScript JSDoc, or Go godoc.

```csharp
public interface IInvoicesClient
{
    /// <summary>
    /// Cancels an issued invoice while preserving it for audit.
    /// Do not use for draft invoices.
    /// </summary>
    Task CancelInvoiceAsync(
        Guid id,
        CancellationToken cancellationToken);

    /// <summary>
    /// Permanently deletes a draft invoice.
    /// Issued invoices cannot be deleted.
    /// </summary>
    Task DeleteDraftInvoiceAsync(
        Guid id,
        CancellationToken cancellationToken);
}
```

This directly optimizes context window usage. Instead of forcing the agent to ingest a massive, multi-megabyte `openapi.json` file, the agent only needs to read the generated interface file. The semantic intent, preconditions, and negative constraints are located right alongside the method signatures.

---

## Client Discoverability

Generating clean clients is only half the battle; the agent still needs to find them within the project tree.

Name your client interfaces after their business domains:

```text
IIdentityClient
IOrdersClient
IBillingClient
IInvoicesClient
```

Avoid grouping by transport, version, or arbitrary service divisions:

```text
IServiceAClient
IBackendClient
IApiV2Client
```

Method names should similarly lead with explicit domain intent:

```text
RevokeUserSessionsAsync
CancelInvoiceAsync
ReserveInventoryAsync
```

This naming strategy allows coding agents to locate dependencies via fast codebase symbol searches or semantic indexing:

```text
Requirement:
"When an employee is disabled, invalidate all login sessions."

↓ Search repository for:
session
revoke session
identity

↓ Discovers interface:
IIdentityClient

↓ Inspects method signatures:
RevokeUserSessionsAsync

↓ Generates correct integration:
await identityClient.RevokeUserSessionsAsync(...)
```

The repository’s type system effectively becomes a self-describing directory of external capabilities.

---

## Repository Guidance for Agents

You should explicitly instruct the agent on how to approach third-party and inter-service integrations. 

Add these rules directly to your project's `AGENTS.md`, `.cursorrules`, or local system prompt:

```text
When integrating with another service:

1. Search existing generated clients by business concept.
2. Inspect method names and documentation.
3. Prefer generated clients over direct HTTP calls.
4. If the correct operation is unclear, inspect the source OpenAPI specification.
5. Do not invent endpoint URLs or construct REST requests manually when a generated client exists.
```

This separates operational responsibilities cleanly:

- The **repository instructions** tell the agent how to discover and navigate internal abstractions.
- The **OpenAPI specifications** define what capabilities actually exist and govern their operational limits.

---

## OpenAPI Does Not Always Need to Be Read Directly

When your generated clients are well-named and include full docstrings, an agent rarely needs to read the raw `swagger.json` or `openapi.yaml` during day-to-day coding tasks.

The default workflow runs quickly and consumes minimal context tokens:

```text
Business requirement
        ↓
Search generated clients
        ↓
Inspect documented methods
        ↓
Generate code
```

The raw OpenAPI file serves as the underlying contract of record. The agent only needs to open it when resolving deeper edge cases:

- Inspecting detailed error response structures.
- Checking validation rules on optional or deeply nested query parameters.
- Reviewing complex object state lifecycles.
- Resolving edge-case behaviors not fully captured by typed client interfaces.

This establishes a clear hierarchy of information:

```text
OpenAPI
   ↓
Generated typed client
   ↓
Generated documentation/comments
   ↓
Coding agent
```

---

## Error Responses Should Also Be Semantic

Downstream services must communicate failures using domain semantics rather than generic, opaque status payloads.

Avoid uninformative error models:

```json
{
  "errorCode": 3817
}
```

Design errors that explain the state of the resource and point toward resolution:

```json
{
  "code": "invoice_already_issued",
  "message": "Issued invoices cannot be deleted.",
  "suggestedOperation": "cancelInvoice"
}
```

Semantic errors provide immediate feedback to both human engineers and LLM agents executing within an automated test-and-repair loop. If an agent writes an integration test that hits this failure mode, the error payload provides the exact path forward: switch from `delete` to `cancelInvoice`.

---

## The Same Principle Applies Beyond REST

This approach is not limited to HTTP and OpenAPI. The same mechanical pattern applies to any modern integration style.

### GraphQL

With GraphQL, leverage schema documentation and strong typing:

- Write explicit field and mutation descriptions in the schema.
- Name queries and mutations around domain workflows rather than generic data fetching.
- Rely on schema introspection.
- Generate typed clients and hooks using tools like GraphQL Code Generator.

```graphql
"""
Cancels an issued invoice while preserving it for audit.
Do not use for draft invoices.
"""
cancelInvoice(id: ID!): Invoice!
```

### Messaging

For asynchronous, event-driven architectures, apply the same rigor using message contracts and AsyncAPI.

Maintain a strict naming distinction between commands and events:

- `RevokeUserSessions` is an imperative command instructing a service to perform an action.
- `UserSessionsRevoked` is an immutable domain event stating that the operation has finished.

AsyncAPI specifications should document:

- Message envelopes and JSON/Avro/Protobuf payload schemas.
- Target channels, topics, or exchanges.
- Publishing versus consumption boundaries.
- Protocol headers, routing keys, and correlation identifiers.
- Broader operational semantics and processing guarantees.

With this structure in place, an agent can discover the appropriate command publisher or event handler without guessing message formats or topic naming rules.

---

## Preferred Architecture

A resilient integration architecture for LLM-assisted development follows this layout:

```text
                       Business requirement
                                ↓
                           Coding agent
                                ↓
                 Discover business capability
                                ↓
                     Strongly typed interface
                                ↓
           ┌────────────────────┼────────────────────┐
           │                    │                    │
        OpenAPI             GraphQL              AsyncAPI
           │                    │                    │
         REST                GraphQL             Messaging
```

The abstraction exposed to the coding agent should almost always be a **typed, semantically named client interface**. Wire protocols, transport serialization, and raw network mechanics should remain encapsulated beneath that boundary.

---

## Core Principle

When designing systems for human and AI collaboration, anchor on this rule:

> External integrations must expose well-documented formal contracts, compile down into strongly typed clients, and make those clients easy to discover by business capability.

When you establish this pipeline, coding agents will consistently use your generated clients instead of attempting to assemble raw transport calls from scratch.

A well-structured API contract is no longer just a machine-readable protocol definition. It becomes an integral part of the semantic environment that informs the LLM:

- What capabilities the system actually supports.
- Which operation maps cleanly to the requested business requirement.
- How to invoke that operation with the compiler's backing.
- Which similar, yet conflicting, operations must be avoided.

---

# Note: Designing Software Architecture with LLM Assistance

---
title: Designing Software Architecture with LLM Assistance
tags:
  - software-architecture
  - system-design
  - ai-agents
  - llm
  - decision-making
  - tradeoff-analysis
aliases:
  - LLM-Assisted Software Architecture
  - Architecture Exploration with AI
---

## The Core Engineering Reality

LLMs accelerate early-stage architectural exploration, but they cannot guarantee structural completeness. 

Used correctly, they are exceptional tools for:
- Mapping out unfamiliar technology stacks and evaluating integration patterns.
- Generating distinct, viable design alternatives.
- Extracting hard constraints from scattered requirements and architecture decision records (ADRs).
- Stress-testing trade-offs between competing approaches.
- Generating throwaway prototypes and proof-of-concept harnesses.
- Spotting well-known failure modes and edge cases.
- Performing adversarial reviews on an existing design document.

Where they fail is in the gaps between the code and reality:
- Discovering constraints that exist nowhere in the written record.
- Formulating the critical unknown-unknown questions that neither you nor the model have surfaced yet.
- Distinguishing a hard invariant from an accidental implementation quirk in legacy code.
- Capturing the tribal knowledge, political compromises, and operational habits running inside your engineers' heads.
- Raising a flag when the problem description is fundamentally underspecified.

The primary hazard when designing systems with an LLM is rarely pure hallucination. The real trap is **plausible completion**: when given an incomplete problem statement, an LLM quietly backfills the missing context with standard industry defaults. It hands you a coherent, elegant, and well-justified architecture that falls apart in production because it rests on unverified assumptions about your environment.

This creates a dangerous illusion of completeness.

---

## Plausible Answers vs. Missing Knowledge

When you feed an LLM an incomplete system description, it does not stop to demand clarification. Its training pushes it to complete the narrative. 

In system design, that means the model silently assumes:
- Eventual consistency is completely fine for the business workflow.
- Every mutating network call can be made safely idempotent.
- Messages can be retried indefinitely without out-of-order execution or duplicate billing.
- State machines are strictly linear with no messy back-transitions or manual overrides.
- No legacy reporting system or shadow ETL pipeline reads directly from your production database.
- A standard relational database engine can absorb the target write throughput.
- Zero-downtime rolling deployments will not trigger dual-version schema compatibility bugs.

In a textbook greenfield scenario, those assumptions might be reasonable. In your actual production environment, half of them are likely false. 

The dangerous part is that an answer built on false assumptions looks identical to an evidence-based design. The model will effortlessly hand you:
- Clean component diagrams and boundary definitions.
- Detailed justifications citing enterprise architecture patterns.
- Migration runbooks and sequence diagrams.
- Production-ready infrastructure-as-code and service boilerplate.
- Balanced lists of pros and cons.

Because the artifact looks professional, engineers are tempted to sign off on it without inspecting the structural assumptions underpinning the design. 

> Never treat a fluent, internally consistent response as evidence that the model actually understood your system's operational realities.

---

## Constraints Originate in the Domain

Technical constraints do not exist in a vacuum; they trace directly back to business domain invariants. 

Your reasoning chain should always move from domain rules to technical mechanisms:

```text
Business Rule
  └──> Required System Invariant
        └──> Architectural Constraint
              └──> Concrete Technology Choice
```

Look at how these map in real systems:

```text
Business Rule:
"A customer must never be billed twice for the same checkout intent."

Required System Invariant:
Payment processing must be strictly idempotent and safe against network-level retries.

Architectural Constraint:
Mutations require deterministic idempotency keys, distributed transaction boundaries, 
or strict database-level deduplication before reaching payment gateways.
```

```text
Business Rule:
"A passenger must know immediately whether their seat reservation was secured."

Required System Invariant:
The booking confirmation path cannot rely on eventual consistency or background queues.

Architectural Constraint:
The reservation workflow requires an immediate, strongly consistent synchronous commit path; 
a purely asynchronous message-driven topology is unacceptable here.
```

```text
Business Rule:
"The business must be able to audit and reconstruct the exact inputs to an automated underwriting decision years later."

Required System Invariant:
Point-in-time domain state and operational inputs must be permanently preserved and reproducible.

Architectural Constraint:
The persistence layer requires immutable append-only ledgers, event sourcing, or bi-temporal audit tables.
```

Technology choices—such as selecting a specific storage engine or messaging topology—are direct derivatives of domain requirements, not stylistic preferences.

By the same token, whenever a stated constraint surfaces—such as *"We must use SQL Server"*—interrogate it immediately. That statement might represent:
- A genuine organizational compliance and support boundary.
- Deep, battle-tested operational expertise within the reliability team.
- Substantial sunk licensing investments.
- Rigid third-party integrations running Change Data Capture (CDC) pipelines directly off transaction logs.
- Hard ACID transaction requirements across shared domain tables.
- A fragile, external enterprise reporting tool querying schemas directly.
- Or nothing more than team habit and historical inertia.

Make the model peel back the constraint. Have it identify which underlying system property actually demands that technical choice.

---

## The Three Categories of Constraints

To prevent blind spots, segment system constraints into three operational categories:

### 1. Explicit Constraints
These are clearly documented in the project context:
- Product requirements documents (PRDs) and Jira tickets.
- Architecture Decision Records (ADRs) and design RFCs.
- Internal documentation, API schemas, and service contracts.
- Explicit security, compliance, and regulatory policies.

LLMs parse and incorporate explicit constraints effectively if you keep them within the active context window.

### 2. Discoverable Constraints
These are undocumented, but they leave hard traces in your environment:
- Existing codebases, build pipelines, and configuration files.
- Unit, integration, and end-to-end test assertions.
- Production database schemas, foreign keys, and indexes.
- Deployment manifests, Helm charts, and Terraform state.
- Network routing, API gateway configs, and reverse proxy rules.
- Production telemetry, APM traces, and query execution plans.
- Incident post-mortems and bug tracker histories.

An LLM cannot guess these out of thin air. Surfacing them requires an explicit discovery phase where you feed relevant code, schemas, and metrics directly into the prompt context.

### 3. Hidden Constraints
These leave zero trace in the repository:
- Tribal knowledge retained by two senior engineers who survived the last rewrite.
- Undocumented, manual operational interventions performed during off-hours.
- Informal agreements and back-channel handoffs between teams.
- Internal organizational politics and budget boundaries.
- Wild, undocumented customer workarounds that rely on unintended system behaviors.
- Legacy edge-case exceptions grandfathered into the system years ago.

An LLM cannot discover hidden constraints. Unless you deliberately extract this information from stakeholders and add it to the prompt, the model will design around a clean abstraction that does not exist. This is where architectures fail.

---

## Stop Starting with Architecture Selection

The default, low-signal engineering pattern looks like this:

```text
Problem Description ──> Architecture Proposal ──> Implementation
```

This workflow invites disaster because it skips the discovery phase entirely. A resilient, professional design workflow forces validation before generation:

```text
Problem Description
  └──> Confirmed Production Facts
        └──> Missing System Information
              └──> Explicit Working Assumptions
                    └──> Required System Invariants
                          └──> Design Alternatives
                                └──> Adversarial Invalidation Passes
                                      └──> Conditional Recommendations
                                            └──> Implementation
```

Your initial phase must focus on **constraint discovery, not solution generation**. 

Before the model is permitted to recommend a single technology, framework, or architectural pattern, require it to surface:
- What is definitively known about the environment.
- What is being logically deduced from the input.
- What assumptions are being introduced to plug information gaps.
- What critical operational data is completely unknown.
- Which requirements are open to conflicting interpretations.
- What specific discoveries would immediately invalidate the preferred design.

Only after this baseline is locked down should the conversation shift toward system topology and tooling.

---

## Separate Facts, Inferences, Assumptions, and Unknowns

Never let an LLM present architectural reasoning as an unbroken narrative. When you allow continuous prose, assumptions blend into verifiable facts, and standard practices masquerade as firm requirements.

Force the model to categorize every key claim into five clear buckets:

### Confirmed Fact
Verified against production, source code, or binding engineering standards.
> *"Deployments use a rolling update strategy across Kubernetes pods; old and new application instances run concurrently for up to thirty minutes."*

### Inference
A strict logical deduction derived directly from confirmed facts.
> *"Any database schema migration introduced in this release must maintain backward compatibility with both the N and N-1 application versions simultaneously."*

### Assumption
A temporary working placeholder introduced because actual system context is missing.
> *"No external reporting engines or analytics workers are executing raw SQL queries directly against this table."*

### Unknown
A critical gap in domain or technical reality that has not yet been resolved.
> *"It is unknown whether message ordering must be strictly preserved across all tenants globally, or only per tenant account."*

### Typical Practice
A common industry default that may or may not fit the operational reality of this system.
> *"Placing an asynchronous message broker between the intake API and the execution worker."*

Rigidly enforcing this classification prevents plausible defaults from quietly hardening into production requirements.

---

## Interrogate What Could Invalidate the Recommendation

The single most useful prompt you can give an LLM during an architectural review is:

> *"What specific information or undiscovered system property would completely invalidate your recommendation?"*

Push the model further with questions designed to expose structural fragility:
- Under what specific traffic shapes, data volumes, or failure modes is this design the wrong choice?
- Which single assumption carries the highest risk of breaking this architecture if proven false?
- What implicit operational defaults did you assume that I never explicitly stated?
- What operational guarantees must our infrastructure provide for this system to survive? Which of those remain unverified?
- What exact property would make an alternative pattern (e.g., synchronous transactions vs. event-driven workers) the superior choice?
- Which specific components of your proposal are directly driven by my documented constraints, and which are generic industry defaults?

A production-grade recommendation is always **conditional**:

> *"If eventual consistency of up to five seconds is acceptable to the domain, mutations are guaranteed to be idempotent, and the team has the operational capacity to manage and monitor a distributed event broker, asynchronous messaging is the recommended path. If the business invariant demands an immediate, authoritative reservation confirmation to prevent overbooking, a synchronous path backed by strict database-level isolation is required."*

Conditional recommendations force engineering trade-offs into the open. Blanket recommendations obscure them.

---

## Force Exploration of the Entire Solution Space

When you ask an LLM for "a few options," it almost always returns minor variations of the exact same design pattern—like proposing Kafka, RabbitMQ, and AWS SQS for a problem that might not even need an asynchronous queue.

Demand solutions drawn from fundamentally different architectural categories:
- **The simplest possible implementation:** The lowest-complexity approach that solves the problem.
- **The zero-new-infrastructure option:** Solving the problem entirely within the existing stack (e.g., using Postgres transactional locks or `SKIP LOCKED` instead of deploying an external broker).
- **The incremental migration:** A step-by-step evolution that avoids high-risk cutovers.
- **The reversible experiment:** An implementation designed to be feature-flagged, benchmarked, and easily rolled back.
- **The conservative baseline:** The boring, battle-tested pattern with predictable operational profiles.
- **The target-state architecture:** The unconstrained, long-term ideal assuming migration costs were zero.
- **The non-obvious alternative:** An atypical but viable technical approach that challenges standard defaults.
- **The process or domain change:** Solving the problem upstream by tweaking business rules or operational processes, eliminating the technical challenge entirely.
- **The "do nothing" baseline:** Documenting the real operational and financial cost of leaving the current implementation alone.

For every proposed option, require the model to explicitly detail:
1. Prerequisites and operational conditions.
2. Underlying assumptions.
3. Quantifiable architectural benefits.
4. Concrete failure modes and operational risks.
5. Infrastructure and maintenance overhead.
6. Migration mechanics.
7. Rollback complexity if the approach fails.
8. A cheap, fast experiment to validate core assumptions.
9. Missing data points that could immediately change its evaluation.

---

## Implementation Bias and Contextual Anchoring

Even when prompted with a neutral tone, an LLM's recommendations are structurally biased.

Large language models inherently favor architectures that are:
- Heavily represented across public GitHub repositories and technical blogs.
- Extensively documented in open-source ecosystems.
- Easy to explain using textbook architectural patterns.
- Straightforward to generate as plausible, self-contained code snippets.

This is not conscious reasoning; it is a statistical reality of generative models:

```text
High-Probability Pattern in Training Data
  └──> Proposed More Frequently
        └──> Justified More Fluently
              └──> Implemented More Cleanly by the Model
```

While high implementability is a legitimate engineering consideration, it can warp architectural decisions. 

> The design pattern an LLM can generate and defend most easily is often not the design pattern that best fits your production constraints.

### The Danger of Contextual Anchoring

This bias worsens when technologies are casually dropped into the prompt history. If Kafka, Temporal, Kubernetes, MongoDB, or Event Sourcing appear anywhere in earlier turns of the conversation, the model routinely over-indexes on them. It treats those mentions as:
- An implicit architectural preference.
- Pre-approved, available infrastructure.
- A constraint that must be preserved.
- A hint about what the engineer wants to hear.

This happens even if you mentioned the technology strictly as a counter-example, a failed past experiment, or an unrelated operational detail.

```text
Technology Mentioned in Context
  └──> Token Weights Elevated in Attention Mechanism
        └──> Distorts Invariant Extraction and Trade-Off Analysis
              └──> Biases Final Architecture Recommendation
```

A question asked after discussing a specific technology is rarely context-neutral. The model will optimize for the narrative established by the conversation rather than evaluating the system from first principles.

### Countering Implementation Bias and Anchoring
- Explicitly instruct the model that previously mentioned tools are examples, not requirements.
- Demand that the model design a solution that explicitly bans the technologies already discussed.
- Require system invariants to be derived entirely from domain rules before evaluating any tooling.
- Ask the model directly: *"Which of your recommendations would change if we stripped every technology name from our conversation history?"*
- Spin up fresh, isolated conversation contexts when transitioning from brainstorming to formal architectural reviews.
- Formally categorize mentioned technologies as: **Required**, **Available**, **Preferred**, **Under Consideration**, or **Explicitly Rejected**.

Use an explicit steering prompt:

> *"Treat every previously discussed technology as non-binding unless it is listed in the confirmed system constraints. Derive the required system invariants first, then evaluate solution options without giving preference to tools already mentioned in the chat."*

The most dangerous workflow is the unvalidated feedback loop:

```text
Model Defines Evaluation Criteria
  └──> Model Selects Technology
        └──> Model Justifies Selection
              └──> Model Generates Implementation
                    └──> Model Reviews Its Own Code
```

This loop produces a completely self-consistent, beautifully documented, non-viable system. To break it, enforce human checkpoints and decouple the evaluation stages:
- Decouple design selection from code generation.
- Force options across radically different complexity tiers.
- Demand the model distinguish domain fit from its own generation confidence.
- Make human engineers approve the evaluation scorecard.
- Audit the architecture thoroughly before asking the model for a single line of implementation code.

Use this evaluation framework for critical decisions:

| Evaluation Dimension | Core Architectural Question |
| :--- | :--- |
| **Problem Fit** | How precisely does this design satisfy our confirmed domain rules and operational constraints? |
| **Evidence Quality** | Which components are backed by verified production data, and which rely on standard industry assumptions? |
| **Implementation Confidence** | How reliably can this design be implemented, tested, and maintained by the actual team? |
| **Ecosystem Familiarity** | Is this tool recommended because it is truly optimal, or because public training data for it is ubiquitous? |
| **Decision Uncertainty** | What missing metrics, production realities, or business changes would immediately invalidate this choice? |

Implementation confidence matters, but it must be an explicit, conscious trade-off—not a hidden bias steering your systems.

---

## Review the System Across Real Engineering Dimensions

Do not let the model limit its analysis to component diagrams and technology selections. Force it to evaluate the proposal across concrete systems engineering dimensions:

- **Domain Invariants:** How the design prevents invalid business states from persisting.
- **State Machine Topology:** Whether transitions are strictly deterministic, and how invalid or partial transitions are handled.
- **Data Ownership and Boundaries:** Which service is the single source of truth for every write, and whether schemas are leaking across boundaries.
- **Consistency Models:** Where strong consistency is non-negotiable versus where eventual consistency is acceptable.
- **Isolation and Concurrency:** How the system behaves under high write contention (optimistic locking, pessimistic locking, serializable transactions).
- **Network Boundaries and Transports:** Where synchronous REST/gRPC boundaries introduce latency chains versus where asynchronous messaging decouples them.
- **Message Semantics and Idempotency:** How consumers handle duplicate deliveries, out-of-order execution, and poison-pill messages.
- **Failure Domains and Retries:** Backoff intervals, circuit breakers, jitter strategies, and dead-letter queues.
- **Distributed Failure Modes:** Handling network partitions, split-brain scenarios, cascading timeouts, and downstream degraded states.
- **API and Contract Evolution:** Backward and forward compatibility, schema registries, protobuf/JSON migrations, and deprecation paths.
- **Deployment Mechanics:** Dual-version application coexistence during rolling or canary deployments.
- **Database Schema Migrations:** Expanding and contracting columns without locking production tables, handling historical data backfills.
- **Rollback Complexity:** What happens when a deployment fails mid-migration, and whether data written by the new version breaks the old version.
- **Security Boundaries:** Zero-trust network segmentation, token propagation, authentication, and authorization checkpoints.
- **Data Privacy and Governance:** PII isolation, data masking, encryption in transit and at rest, and hard deletion compliance (e.g., GDPR/CCPA).
- **Audit Trails and Lineage:** Tamper-evident logging, temporal tracking of state changes, and long-term regulatory retention.
- **Throughput, Latency, and Scalability:** P99 SLA targets, hot-spotting on shard keys, connection pool exhaustion, and CPU vs. I/O bottlenecks.
- **Telemetry and Debuggability:** Distributed trace propagation, contextual structured logging, and metric cardinality.
- **Operational Ergonomics:** Disaster recovery runbooks, automated health checks, manual operational overrides, and alert noise.
- **Cost Realities:** Network egress fees, managed service compute tiers, storage tiering, and operational licensing.
- **Team Topology and Skills:** Whether the engineering team can realistically operate, debug, and patch this stack at 3:00 AM.
- **Reversibility Score:** The blast radius and financial/time cost of unwinding this architectural choice twelve months from now.

The goal is not to fill out an exhaustive 22-point scorecard for every micro-decision. It is to quickly identify which specific dimensions pose fatal risks to this particular system.

---

## Use the Model in Specialized Adversarial Roles

An LLM asked to play generic "architect" produces generic, uncontroversial answers. To get real depth, force the model into specialized personas that mimic a complete, adversarial architectural review board.

```text
                         Architecture Proposal
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
   Domain Analyst               Skeptic                 Site Operator
  (Invariants/Rules)      (Assumptions/Failures)      (Runbooks/Deploys)
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
  Security Reviewer                                  Migration Engineer
(Trust Boundaries/Auth)                              (Rollbacks/Dual-Runs)
```

- **The Domain Analyst:** Extracts strict business invariants, domain actors, valid state lifecycles, exception pathways, and semantic ambiguities from requirements.
- **The Lead Architect:** Generates concrete design alternatives, balances structural trade-offs, and defines component boundaries.
- **The Skeptic:** Hunts for unsupported assumptions, unstated constraints, edge cases, cascading failure cascades, and conditions that break the design.
- **The Site Reliability Engineer / Operator:** Interrogates deployment topology, observability, metric cardinality, runbooks, failure recovery, failover automation, and operational maintenance burdens.
- **The Security Engineer:** Maps attack surfaces, zero-trust boundaries, sensitive data handling, least-privilege access, authorization leakage, and compliance constraints.
- **The Database / Migration Engineer:** Evaluates schema expansion and contraction, concurrent version execution, database locking behavior, asynchronous data backfills, rollback safety, and legacy integrations.

Running these prompts does not guarantee correctness, but it strips away the polite agreement that causes standard LLM outputs to gloss over production risks.

---

## Exploration Mode vs. Commitment Mode

LLMs drastically lower the cost of technical spikes. They allow teams to:
- Quickly prototype integrations against unfamiliar SDKs or frameworks.
- Generate disposable proof-of-concept services and mock harnesses.
- Run comparative simulations between competing database access patterns.
- Stress-test alternative data serialization formats.
- Scaffold out migration scripts and data transformation pipelines.

This unlocks a tight, iterative learning loop:

```text
Hypothesis ──> Cheap Prototype ──> Profiling / Testing ──> Adversarial Critique ──> Architectural Commitment
```

However, high development velocity is not the same as architectural comprehension. 

An LLM can generate a functioning prototype for an event-driven CQRS system in ten minutes. It does not equally compress the time required to understand:
- How the system behaves when the event store drops connections under load.
- The operational headache of handling out-of-order event projections.
- How to debug subtle data drift between the write and read models.
- The organizational cost of training developers to reason about eventual consistency.

To protect systems from unvetted technical debt, draw a hard line between two operational modes:

### Exploration Mode
*Objective: Maximize learning velocity and test hypotheses cheaply.*
- Generate multiple divergent design spikes.
- Prototype with unfamiliar tools and patterns.
- Accept explicitly labeled, provisional assumptions.
- Write disposable, single-use test scripts and harness code.
- Ignore enterprise-grade completeness in favor of validating technical unknowns.
- Ensure all experiments are fully isolated and easily discarded.

### Commitment Mode
*Objective: Guarantee production stability, operational safety, and system reversibility.*
- Validate all explicit, discoverable, and hidden constraints.
- Cross-reference design assumptions against authoritative vendor documentation and source code.
- Subject the design to chaos testing, concurrency checks, and failure-mode drills.
- Finalize runbooks, monitoring, and operational alerting strategies.
- Eliminate all unverified working assumptions.
- Design and dry-run rolling schema migrations and emergency rollback procedures.
- Document trade-offs in a formal ADR approved by human engineers.

The most catastrophic failure mode occurs when an exploratory spike is quietly pushed to production as permanent architecture.

---

## The Correct Role for the Model

An LLM is not an authoritative chief architect. It is an interactive, high-bandwidth accelerator for:
- Mapping unfamiliar technical terrain.
- Surfacing neglected operational questions.
- Extracting discoverable constraints from code and logs.
- Generating diverse, non-obvious alternatives.
- Stress-testing trade-offs under varying operational conditions.
- Rapidly assembling proof-of-concept harnesses.
- Conducting adversarial peer reviews.
- Drafting structured documentation and runbooks.
- Designing targeted verification suites.

The human engineering team owns final accountability for confirming the model of reality upon which the architecture depends.

When evaluating an LLM's architecture proposal, the primary question is never:
> *"Did the model produce a clean, reasonable design?"*

The primary question is always:
> *"Does this design reflect the confirmed, messy constraints of our specific production environment, or did the model quietly substitute a textbook default that will fail under load?"*

---

## The Six-Phase Architectural Workflow

To get reliable, high-signal results from an LLM during system design, follow this structured six-phase pattern:

```text
Phase 1: Discovery    ──> Force the model to inventory facts, gaps, and invariants.
Phase 2: Verification ──> Validate assumptions against production reality.
Phase 3: Generation   ──> Solicit distinct, structurally diverse design options.
Phase 4: Adversarial  ──> Assume proposals are broken; stress-test edge cases.
Phase 5: Decision     ──> Produce conditional, trade-off-driven recommendations.
Phase 6: Handoff      ──> Pass hard constraints and boundary contracts to implementers.
```

### Phase 1: Problem Discovery
Instruct the model that solutions are strictly prohibited. Demand:
- Confirmed production facts extracted from your prompt.
- Deductions logically derived from those facts.
- Explicit working assumptions introduced to bridge gaps.
- Missing operational and business context.
- Ambiguities in domain rules.
- High-impact questions ranked by their ability to change the design.

### Phase 2: Constraint Verification
Take the high-impact questions and assumptions generated in Phase 1 and validate them against reality:
- Search repositories, schemas, and pipeline definitions.
- Inspect telemetry, error budgets, and database query logs.
- Query domain experts, team leads, and product owners directly.
- Feed verified answers back to the model, converting assumptions into confirmed facts.

### Phase 3: Strategic Option Generation
Demand solution patterns drawn from fundamentally different architectural categories. Prohibit the model from naming an unconditional "winner."

### Phase 4: Adversarial Stress-Testing
Instruct the model to assume its proposed architectures are fatally flawed. Have it systematically hunt for:
- Domain invariants that break under edge cases.
- Cascading network failures, connection pool starvation, and race conditions.
- Direct database dependencies from unmonitored external systems.
- Zero-downtime deployment traps and schema lock contention.
- Operational cost explosions under non-linear data growth.
- Subtle differences between local prototype success and production failure.

### Phase 5: Conditional Recommendation
Require the model to deliver a conditional decision framework:
- The preferred option for specific operational profiles.
- The precise prerequisites under which that option remains valid.
- The production metrics or business shifts that would invalidate the choice.
- Unresolved operational risks that require runtime mitigation.
- The smallest, cheapest prototype required to validate unverified assumptions.

### Phase 6: Implementation Handoff
When handing off the approved design to an engineering team or a coding agent, provide an unambiguous operational specification:
- Core business objectives and throughput SLAs.
- Global domain invariants that must never be violated.
- Approved architectural topology and component boundaries.
- Contextual schemas and neighboring service contracts.
- Explicit working assumptions that remain in scope.
- Non-negotiable unit, integration, and concurrency tests.
- Prohibited changes (e.g., changes to legacy tables, introduced dependencies, bypassed gateways).

---

## Production-Ready Prompt Templates

Use these templates directly in your design workflows.

### Template 1: Discovery Before Design

```text
Analyze the architecture problem described below. You are strictly forbidden from proposing any solutions, patterns, or technologies in this step.

Perform a thorough constraint analysis on the input. Structure your response into these exact categories:

1. Confirmed Facts: Information explicitly stated in my description or directly verified by production evidence.
2. Inferred Deductions: Logical conclusions derived strictly from the confirmed facts.
3. Working Assumptions: Defaults, placeholders, or standard practices you are introducing to fill gaps in the description. Label these aggressively.
4. Unknown Information: Critical missing context regarding domain rules, data volumes, traffic shapes, team topologies, or legacy systems.
5. Typical Practices to Avoid: Common industry defaults (e.g., eventual consistency, microservices, asynchronous queues) that may not apply to this system.

Analyze this problem across every critical engineering dimension, explicitly including:
- Core business rules and domain invariants
- Data consistency models and transaction boundaries
- Concurrency, race conditions, and locking strategies
- Message ordering, retry semantics, and idempotency guarantees
- Partial failure modes, network splits, and downstream latency chains
- External integrations, direct database couplings, and contract schemas
- Throughput, p99 latency targets, data growth, and resource bottlenecks
- Security perimeters, authentication, trust boundaries, and compliance
- Auditability, event tracking, and regulatory retention policies
- Zero-downtime deployments, backward-compatible schema changes, and rollbacks
- Observability, trace propagation, metric cardinality, and operational debugging
- Infrastructure costs, vendor lock-in, and team operational capability

Provide a prioritized list of questions whose answers would materially alter the architectural design. Rank them by decision impact.

Surface the hidden assumptions you would normally make to design this system, identify which carry the highest operational risk, and highlight the questions an engineer might forget to ask.

Stop immediately after the analysis and questions. Propose no solutions.

[INSERT PROBLEM DESCRIPTION HERE]
```

### Template 2: Generating Distinct Architectural Alternatives

```text
Review the confirmed facts, invariants, and explicitly validated assumptions below. 

Propose viable architectural solutions drawn from structurally distinct categories. Do not give me minor variations of the same pattern.

You must provide options from these categories:
1. The Simplest Solution: Minimal complexity, zero accidental engineering.
2. Zero-New-Infrastructure: Solves the problem purely using our existing production stack.
3. The Incremental Evolution: Low-risk, step-by-step transition with no big-bang cutovers.
4. The Reversible Spike: Optimized for rapid validation, instrumentation, and easy rollback.
5. The Conservative Standard: Boring, predictable, battle-tested enterprise architecture.
6. The Long-Term Target: The unconstrained ideal architecture assuming zero migration drag.
7. The Non-Obvious Alternative: An unusual but structurally viable design pattern.
8. The Process/Domain Alternative: A non-technical change to upstream business logic or operations that eliminates the engineering problem entirely.

For each option, provide:
- Core Mechanism: How it fundamentally works.
- Prerequisites: What must be true about our infrastructure, team, and systems for this to work.
- Underlying Assumptions: What this design assumes about traffic, consistency, and operations.
- Best Fit: The precise conditions where this option is optimal.
- Worst Fit: The conditions where this option fails catastrophically.
- Engineering and Operational Risks: Failure modes, concurrency bottlenecks, and operational debt.
- Deployment and Rollback Mechanics: How this is released without downtime, and how it is unwound if it fails.
- Validation Spike: The cheapest, fastest prototype or experiment to prove its viability.
- Invalidation Triggers: Discoveries that would remove this option from consideration.

Do not declare any option unconditionally superior. Present the trade-offs objectively.

[INSERT CONFIRMED FACTS, INVARIANTS, AND ASSUMPTIONS HERE]
```

### Template 3: Adversarial Review

```text
Assume the proposed architectural design below is fundamentally flawed and will fail in production. 

Perform an adversarial review to expose its failure modes. Specifically interrogate:
- Undocumented assumptions masquerading as confirmed facts.
- Unstated domain constraints that break the core model.
- Concurrency limits, race conditions, write skew, and deadlocks.
- Distributed failure modes: network partitions, connection starvation, cascading timeouts.
- Idempotency leaks, duplicate mutations, out-of-order message delivery, and poison pills.
- Zero-downtime rolling update incompatibilities and database migration locks.
- Operational maintenance burdens, debugging obscurity, and runbook complexity.
- Cross-team organizational friction, skill gaps, and unowned dependencies.
- Subtleties where this pattern succeeds in a local proof-of-concept but degrades under production scale.

Answer these questions directly:
1. What non-negotiable operational conditions must hold for this architecture to survive?
2. Which of those conditions are currently unverified in our context?
3. What specific piece of missing information would instantly invalidate this recommendation?
4. What exact tests, benchmarks, metric analyses, schema queries, or stakeholder reviews are required to validate the working assumptions?
5. Which parts of this design are directly derived from our explicit context, and which are generic industry defaults imported by the model?

Be ruthlessly specific. Point to concrete runtime mechanisms, network boundaries, and data layouts.

[INSERT PROPOSED ARCHITECTURE HERE]
```

---

## The Mental Model

An LLM output is not an architecture. It is an unverified projection generated from an incomplete mental model of your system.

That internal projection is composed of:
- A handful of verified facts you remembered to supply.
- Deductions the model drew from those inputs.
- Unverified assumptions introduced to smooth over missing context.
- Glaring real-world omissions hidden behind professional prose.
- Statistical industry averages lifted from public repositories.

Your first responsibility as an engineer is not to review the proposed technology stack. It is to **interrogate and validate the model of reality that produced that proposal**.

LLMs give us the leverage to explore wider design spaces, run faster prototyping spikes, and spot failure modes earlier than ever before. Use them to aggressively expand cheap, reversible experimentation—never to introduce irreversible architectural risk into your production systems.

---

# Note: Developing Features with AI Coding Agents

---
title: Developing Features with AI Coding Agents
tags:
  - ai-agents
  - software-engineering
  - agentic-workflows
  - feature-development
  - testing
  - code-review
aliases:
  - Feature Development with Agents
  - End-to-End Agentic Feature Lifecycle
---

## A Battle-Tested Workflow for Larger Features

When you hand an autonomous agent a loose prompt for a complex feature—like "add multi-tenant billing with tiered seat pricing"—disaster usually follows. The model writes dozens of sprawling files, invents its own business logic, mocks out critical network boundaries, and writes green tests that pass purely because they assert against its own flawed assumptions.

To ship reliable, production-ready code with coding agents, you need a disciplined, phased pipeline that treats the model as an implementer rather than an unsupervised architect:

```text
repository analysis
→ behavioral specification
→ examples and decision tables
→ acceptance tests
→ human review
→ implementation of one vertical slice
→ architectural review
→ full implementation
→ independent skeptical review
→ documentation update
```

---

### Step 1: Repository Analysis

The first command you give the agent must enforce a strict read-only boundary. Do not let it create or modify a single line of code yet. 

Its job is to inspect the codebase and map the existing operational reality:

* **Business flows:** Trace the exact call paths, controller actions, domain events, and background workers that will interact with the new capability.
* **Data models and storage:** Inspect existing database schemas, migrations, indices, foreign key constraints, and entity relationships. Note whether tables are partitioned or if certain fields rely on implicit database defaults.
* **Integration points:** Identify external API clients, message queues, webhook handlers, and third-party dependencies. Check how retries and idempotency keys are handled.
* **Transaction boundaries:** Look at where database transactions start and end. Are they handled at the service layer, inside repository methods, or managed via unit-of-work patterns?
* **Existing test infrastructure:** Note how current tests run. Are they isolated unit tests, container-backed integration tests (e.g., Testcontainers), or heavily mocked end-to-end suites?
* **Compatibility risks:** Pinpoint where schema changes could break older running instances during a rolling deploy, or where changes to serialized queue payloads could poison active consumers.
* **Hidden assumptions and tribal knowledge:** Surface monkey-patches, hard-coded environment toggles, custom error-handling middleware, and unwritten domain invariants embedded in legacy helper utilities.

The goal here is a grounded discovery report. If the model cannot accurately describe how the system works today, it cannot safely modify it for tomorrow.

---

### Step 2: Behavioral Specification

Once the system context is established, write a strict behavioral specification. You can have the agent draft this, but you must curate and approve it. 

This document must define the boundary conditions in plain, unambiguous domain terms:

* **Business objective:** The root problem being solved and the exact value delivered, stripped of technical implementation details.
* **Terminology:** An explicit glossary. If the codebase uses "Account," "Workspace," and "Tenant," define what each word means so the agent doesn't conflate identity boundaries.
* **Core rules:** Explicit state machine transitions, validation invariants, authorization checks, and calculation formulas.
* **Exceptions and failures:** Exactly how the system responds when things go wrong—network timeouts, validation failures, concurrency conflicts, and rate limits.
* **Negative cases:** What the system *must reject*. For example: "A user cannot downgrade a plan if their current seat usage exceeds the target plan's limit."
* **Side effects:** Background jobs enqueued, cache keys invalidated, domain events published to message brokers, and audit logs recorded.
* **Compatibility constraints:** Wire formats, database backward-compatibility, and API versioning rules that must remain intact.
* **Non-functional constraints:** Hard limits on memory usage, database query counts (preventing N+1 queries), connection pool starvation, and P99 latency budgets.
* **Explicit out-of-scope boundaries:** A firm list of features the agent must *not* attempt to build. Without this, models tend to over-engineer speculative abstractions and secondary workflows.

---

### Step 3: Tests Before Implementation

With the specification locked, have the agent write the tests before writing any production implementation.

These tests serve as executable guardrails across multiple layers:

* **Business-rule tests:** Pure, IO-free tests that exercise domain models, calculation engines, and state machines with comprehensive edge-case coverage.
* **Acceptance tests:** High-level scenarios that exercise full use cases against the public API or service boundary, asserting on observable business outcomes.
* **Regression tests:** Targeted tests ensuring that adjacent features, shared utilities, and existing database queries remain entirely unaffected.
* **API contract tests:** Strict validation of HTTP status codes, JSON schema payloads, error response structures, and header behaviors.
* **Integration tests:** Scenarios that touch real backing services (e.g., PostgreSQL or Redis instances in Docker) to validate transactions, constraint violations, and query mechanics.

**The Golden Rule:** These new tests must fail when run against the current codebase. A test that passes before the implementation exists is either a tautology, testing the wrong code path, or asserting nothing of value. The failure confirms the test can detect the absence of the required behavior.

---

### Step 4: Human Review of Meaning

Do not skim this step just to verify that the test code looks clean, idiomatic, or passes linting. You are conducting a semantic audit of the test suite.

Inspect the suite through these critical questions:

* **Does the test reflect true business requirements?** Ensure the assertions match the behavioral specification, not a shallow mechanical echo of input to output.
* **Did the agent invent an unstated rule?** Models frequently introduce plausible-sounding assumptions (e.g., auto-refunding money on a canceled subscription or silently swallowing errors with default fallbacks) that contradict actual domain policy.
* **Are negative paths genuinely validated?** Check that failure assertions test the specific domain error, rather than just asserting that *any* exception was thrown (which might be an unexpected `NullPointerException`).
* **Are rule priorities and conflicts resolved correctly?** If two business rules collide (e.g., an enterprise discount code applied alongside an automated seasonal promotion), does the test assert the correct priority order?
* **Is the test decoupled from implementation details?** Tests that assert on internal private methods or rely on extensive, brittle mocking will shatter the moment you refactor the underlying classes. Assert on behavior, inputs, and outputs.
* **Does the test accidentally preserve legacy bugs?** If an existing endpoint returns an incorrect status code or malformed payload, make sure the new test doesn't codify that accidental behavior as a permanent requirement.

---

### Step 5: Freeze the Acceptance Contract

Once you approve the acceptance test suite, freeze it. 

The agent responsible for implementing the production code must not have permission to modify these approved acceptance tests. If the model is allowed to edit both the implementation and the tests simultaneously, it will inevitably mutate assertions to make a failing test pass whenever it struggles with an edge case.

The implementing agent is free to create internal, lower-level unit tests for technical plumbing (such as parser utilities or helper functions). However, modifying any part of the agreed acceptance contract requires human intervention and explicit re-review.

---

### Step 6: Implement a Small Vertical Slice

Resist the urge to let the agent generate the entire feature across all layers at once. Asking an agent to build twenty database models, ten repositories, ten services, and five controllers in one shot leads to fragmented code that rarely links together properly.

Instead, instruct it to implement a single, narrow vertical slice:

```text
HTTP Controller / Entry Point
  → Route Validation
    → Domain Service
      → Data Repository / Query
        → Database Transaction / Persistence
```

Pick one critical happy-path operation. Wire it from the external entry point down to disk storage and back out. 

Building a vertical slice validates your architectural decisions immediately:
* Are the dependency injection setups working?
* Do the database transactions roll back cleanly on errors?
* Is context passing correctly through the service layers?
* Are the chosen abstractions clean and ergonomic to build upon?

You catch structural flaws when only three files exist, rather than after twenty files have been committed.

---

### Step 7: Architectural Review

Stop and evaluate the vertical slice before scaling out. 

Examine the integration points:
* Did the agent introduce unnecessary architectural layers, leaky abstractions, or redundant DTO conversions?
* Are database queries efficient, or are we setting ourselves up for memory bloat and connection starvation?
* Is error propagation consistent, or did the agent wrap domain errors in generic runtime exceptions?

Fix the architectural patterns here. This code now acts as the canonical few-shot pattern the agent will reference when implementing the rest of the feature.

---

### Step 8: Full Implementation

With the pattern proven and locked, authorize the agent to fan out and implement the remaining paths: secondary use cases, edge cases, error conditions, and negative branches.

Because the acceptance tests are frozen, the agent can iterate autonomously in a tight loop: write code, run the acceptance suite, inspect failures, and refine the implementation until every test turns green.

---

### Step 9: Independent Skeptical Review

Never rely solely on the implementing agent to review its own work. Pass the resulting Git diff to an independent review process—either a senior engineer or a freshly prompted model configured with an adversarial, critical persona.

The reviewer should scrutinize the diff specifically for:
* Race conditions and lack of row-level locking or optimistic concurrency controls on shared mutable state.
* Resource leaks: unclosed database handles, missing transaction rollbacks, or dangling goroutines/threads.
* Subtly broken edge cases that bypass the test suite.
* Security vulnerabilities: missed authorization checks, improper tenant scoping in database queries, or unvalidated user input.

---

### Step 10: Documentation Update

Code is not complete until the surrounding operational context reflects the changes:

* Update OpenAPI/Swagger definitions.
* Record Architectural Decision Records (ADRs) explaining *why* specific trade-offs were made.
* Update schema migration logs and operational runbooks for deployment and rollback procedures.
* Ensure domain glossaries reflect any newly introduced concepts.

---

## Tests Are Executable Specifications, but Not Complete Specifications

A common trap in agentic workflows is treating test suites as the sole source of truth. Tests are concrete examples of expected behavior, but they are not complete specifications.

A passing test suite demonstrates that specific inputs yield specific outputs under predefined conditions. It does not explain:
* **The "why":** The business rationale or regulatory requirements driving the logic.
* **Domain definitions:** What terms actually signify to human operators in the real world.
* **Protected constraints:** Which code paths look redundant or inefficient to an optimizer, but exist to prevent subtle edge cases or third-party API quirks.
* **Differentiating nuances:** Why two seemingly identical workflows must be handled with slight variations in transaction isolation or event emission.
* **Historical necessity:** Which behaviors are legacy technical debt that must be preserved for backward compatibility versus which can be safely cleaned up.

The most resilient engineering approach combines all four pillars:

```text
business decision
+ examples or decision table
+ acceptance tests
+ explicit implementation
```

### The Peril of Self-Grading Agents

If you allow a model to define both the implementation and the criteria for correctness, it operates inside an unvalidated loop. 

An agent that misunderstands a requirement will write a flawed implementation, write a tautological test asserting that flawed behavior, run the test, watch it pass, and report that the task is complete. Without an independent human verifying the semantic meaning of the tests, the suite merely automates the confirmation of its own hallucinations.

---

## Practical Working Rules

Keep these operational rules front and center when driving feature work with autonomous agents:

* **Analyze before modifying:** Never generate implementation code in the same step as repository discovery. Force a read-only analysis phase.
* **Write and approve the behavioral specification first:** Do not write code or tests until the domain boundaries, edge cases, and terminology are explicitly defined and reviewed.
* **Use examples and decision tables:** When business rules have combinatorial inputs (e.g., combinations of user roles, subscription states, and feature flags), map them out in truth tables. Agents parse tabular logic far more reliably than prose.
* **Review acceptance tests before writing production code:** Ensure test assertions validate business intent rather than implementation details or accidental behavior.
* **Freeze approved business tests:** Keep the acceptance suite locked so the implementing agent cannot alter the grading rubric to match its code.
* **Implement one vertical slice first:** Prove the architecture from the controller down to the database row on a single use case before fanning out to the full feature set.
* **Separate mechanical changes from business changes:** Run refactorings, dependency updates, and lint fixes in isolated commits completely separate from behavioral feature code.
* **Require a skeptical second review:** Treat agent-generated code with the same scrutiny you would apply to code submitted by an over-confident junior engineer: verify invariants, check the edge cases, and run adversarial tests before merging to main.

---

# Note: Hidden Abstractions May Become More Expensive in Agent-Maintained Code

---
title: Hidden Abstractions May Become More Expensive in Agent-Maintained Code
tags:
  - software-architecture
  - ai-agents
  - abstraction
  - code-maintainability
  - simplicity
  - software-engineering
aliases:
  - Cost of Hidden Abstractions with Agents
  - Explicit vs Magic Abstractions in AI Era
---

Modern software architecture has spent the last two decades obsessing over a single goal: stripping repetitive boilerplate out of local code. 

Instead of writing out validation, authorization checks, retry loops, database transaction boundaries, structured logging, distributed tracing, and error mapping in every single handler, we push those concerns down into reusable infrastructure mechanisms. We lean heavily on:

- Middleware pipelines
- Interceptors
- Decorators and dynamic proxies
- Dependency injection containers and factory delegates
- HTTP message handlers and delegating handlers
- MVC/API framework filters
- MediatR and command-bus pipeline behaviors
- Entity Framework Core interceptors and global query filters
- Centralized exception-handling middleware
- Convention-based routing and binding
- Assembly scanning and auto-registration
- Ambient context and thread-local state

The result is local code that looks impossibly clean. You open an API controller or a minimal API endpoint, and you see something like this:

```csharp
public Task<Response> GetOrder(GetOrderRequest request)
{
    return mediator.Send(request);
}
```

On the surface, the method is trivial. It looks like a single line of plumbing. But if you profile that request in production or step through it with a debugger, the actual execution path looks more like this:

```text
HTTP request
→ authentication middleware
→ authorization middleware
→ exception middleware
→ request validation
→ MediatR pipeline
→ logging behavior
→ transaction behavior
→ handler execution
→ Entity Framework query filter
→ database command interceptor
→ SQL generation and execution
→ response mapping
→ serialization
```

The local method signature is simple. The runtime semantics are anything but simple.

This gap between syntax and runtime behavior has always been a source of subtle bugs for engineering teams. But as software development shifts toward systems authored, modified, and debugged by automated coding agents, this distinction moves from a minor annoyance to a critical architectural bottleneck.

---

## Local Simplicity Is Not the Same as Semantic Simplicity

When an automated agent is assigned to modify a method, it has to reason about everything that happens when that method runs. It cannot just look at the lines of code physically sitting between the opening and closing curly braces.

Take a routine outbound call:

```csharp
await httpClient.SendAsync(request);
```

To an LLM looking only at this line, this appears to be a raw HTTP invocation. But in a mature production service, that `HttpClient` instance is usually wrapped in an `IHttpClientFactory` pipeline that invisibly injects:

- Outgoing authentication headers (Bearer tokens, mutual TLS)
- Distributed correlation IDs (`X-Correlation-ID`, W3C trace contexts)
- Polly retry policies with exponential backoff and jitter
- Circuit breakers watching downstream failure rates
- Per-request and total call timeouts
- OpenTelemetry spans and metric counters
- Structured request/response logging (often scrubbing PII)
- Multi-tenant routing headers

The critical behavior of this network call does not exist at the call site. It is scattered across distant service registration files, application settings, and framework conventions.

You run into the exact same problem with database access:

```csharp
context.Orders.ToListAsync();
```

In an enterprise EF Core codebase, this rarely translates to a simple `SELECT * FROM Orders`. In reality, it often means:

```text
load Orders
where TenantId == CurrentTenant
  and IsDeleted == false
using an interceptor-defined command timeout and query-tagging behavior
```

Because someone registered a global query filter inside `OnModelCreating` and an interceptor in `AddDbContext`, the line of code you are reading is actually an incomplete representation of the query that hits the database engine.

The architectural challenge here is not abstraction itself. Abstraction is fundamental to managing complexity. The real problem is **non-local semantics**—when the actual meaning, side effects, and failure modes of a line of code depend entirely on logic that is physically and structurally invisible at the call site.

---

## Hidden Execution Context Breaks Reasoning

One of the hardest patterns for an agent—or a newly hired engineer—to navigate is ambient state. These are the dependencies that never show up in a method signature or a class constructor, but get pulled in sideways from runtime context:

```text
HttpContext
AsyncLocal<T>
Activity.Current
ClaimsPrincipal.Current
TenantContext / ICurrentTenant
CultureInfo.CurrentCulture
Scoped dynamic service resolution
Feature flag providers
Environment-variable overrides
```

You end up with a method signature that advertises a very simple contract:

```csharp
Process(Order order)
```

Yet the hidden input vector actually looks like this:

```text
order
current user identity and roles
tenant identifier
active feature flags
ambient database transaction
trace and span IDs
user culture and timezone
fine-grained authorization context
```

The true dependency graph is five times larger than the public interface suggests.

Human teams usually survive this by relying on institutional knowledge. An engineer who has spent two years on the codebase knows that calling `Process` within an asynchronous background task will blow up because `HttpContext` is null, or that a database save will fail unless a tenant header was passed upstream. They have stepped on those landmines before.

An automated agent does not have that institutional memory. It lands in a repository to execute a targeted prompt, examines the immediate file and its immediate imports, and has to reconstruct the entire runtime context from scratch. If that context is ambient, the agent will frequently make invalid assumptions, produce broken changes, or introduce regressions that pass unit tests but fail under integration conditions.

---

## Dynamic Dependency Injection Amplifies the Blind Spot

Standard constructor injection is relatively easy to trace: `OrderService` takes an `IPriceCalculator`, and you can inspect the classes implementing that interface.

The machinery becomes far more opaque when the DI container starts resolving implementations conditionally based on runtime state:

```csharp
services.AddScoped<IPriceCalculator>(sp =>
{
    var context = sp.GetRequiredService<OperationContext>();

    return context.Channel switch
    {
        Channel.Web => new WebPriceCalculator(),
        Channel.Api => new ApiPriceCalculator(),
        _ => new DefaultPriceCalculator()
    };
});
```

At the call site, the code remains totally generic:

```csharp
priceCalculator.Calculate(order);
```

Static analysis of that call site tells you almost nothing about what logic will actually execute. The implementation is selected dynamically at runtime based on the state of `OperationContext`. 

You see this exact same pattern repeated across:

- Keyed and tagged service registrations
- Dynamic decorators (such as Scrutor scanning and wrapping interfaces)
- Open-generic registrations that bind dynamically to payload types
- Conditional registrations driven by environment variables or feature toggles
- Runtime plugin loaders and reflection-based assembly scanners

When you use these patterns, the call site ceases to be an accurate map of execution. An agent reading `priceCalculator.Calculate(order)` cannot determine which concrete algorithm executes without analyzing the IoC container's registration graph and simulating the runtime context.

---

## Interceptors and Pipelines Conceal Business-Critical Semantics

Cross-cutting pipelines become dangerous the moment they start handling domain logic instead of pure infrastructure mechanics.

Consider a simple persistence call:

```csharp
repository.Save(order);
```

Behind the scenes, a dynamic proxy or an interceptor pipeline might trigger:

```text
authorization check
→ input validation
→ ambient transaction initiation
→ audit-log generation
→ database write
→ outbox event publication
→ distributed cache invalidation
```

Some of those steps are generic operational concerns. But others—authorization, validation, transaction boundaries, and event publishing—are fundamental to the business semantics of the operation.

This distinction is critical:

- If a generic execution-timer metric is invisible at the call site, it rarely matters. It does not alter state, it does not change control flow, and it will not cause a bug if an agent modifies how the order is saved.
- If a **transaction boundary**, a **retry policy**, an **implicit tenant filter**, or a **business validation rule** is invisible, modifying that method becomes hazardous.

If an agent does not know that `repository.Save(order)` automatically publishes an integration event via an interceptor, it might introduce a second call to an event publisher right next to it, causing duplicate events downstream. The magic that saved a human five lines of typing becomes a direct cause of bugs for an agent.

---

## Agents Shift the Trade-Offs of Explicit Code

Traditional software engineering has always pushed hard to eliminate duplication. The classical engineering calculus goes like this:

```text
code duplication
→ larger codebase
→ higher ongoing maintenance overhead
→ more surface area for human inconsistency
```

To fight that drift, we adopted the DRY (Don't Repeat Yourself) principle as an absolute rule. We built deep layers of abstraction, centralized behavior into cross-cutting interceptors, and hid repetitive operational mechanics behind framework conventions.

That trade-off made sense when humans had to type, read, and maintain every single line of code by hand. But automated agents alter the economics of code generation and maintenance. The friction of generating and updating repetitive, explicit code drops significantly, while the reasoning cost of deciphering non-local, dynamic abstractions skyrockets.

This introduces a different architectural trade-off:

```text
controlled semantic explicitness
→ higher semantic locality
→ straightforward static reasoning
→ safer automated modifications
```

The objective is not to return to writing raw ADO.NET data readers or manually packing JSON bytes into sockets. The goal is to eliminate **invisible business semantics**.

---

## Explicit Execution Pipelines

One practical way to restore semantic locality without losing clean architecture is to make the execution pipeline explicit directly at the definition site of the operation.

Instead of hiding the execution chain behind an opaque mediator:

```csharp
return mediator.Send(request);
```

You structure the operation so that its processing pipeline is readable from top to bottom:

```csharp
return Operation
    .From(request)
    .Validate<GetOrderValidator>()
    .Authorize<ReadOrderPolicy>()
    .Retry(ExternalPolicies.Read)
    .Execute<GetOrderHandler>()
    .ValidateResponse<GetOrderResponseValidator>()
    .MapErrors<OrderHttpErrors>()
    .Return();
```

The specific fluent syntax matters less than the structural property: the entire execution graph is directly declared in the file:

```text
request
→ validation
→ authorization
→ retry policy
→ execution
→ response validation
→ error mapping
→ response
```

An agent reading this file does not need to search through 10 registration classes, trace open-generic assembly scanning rules, or inspect container configurations to understand what will happen. The operational semantics are right there in the source code.

---

## Keeping Abstraction Where It Belongs

Being explicit about business semantics does not mean abandoning infrastructure abstractions.

An HTTP endpoint handler in an ASP.NET Core service should still receive a strongly typed DTO:

```csharp
GetOrderRequest request
```

It should not be dealing with low-level runtime mechanics:

```text
TCP socket management
HTTP/2 frame parsing
TLS handshakes
UTF-8 byte decoding
JSON tokenization and memory allocation
Model deserialization
```

These are mechanical infrastructure concerns. The business logic of fetching an order does not care how the bytes were converted into a DTO, nor should it manually construct HTTP responses and write raw bytes back down the socket.

A clear architectural boundary looks like this:

```text
Framework owns runtime mechanics
Operation owns business semantics
```

Let the framework handle the plumbing that turns network packets into objects. But when it comes to deciding what policies, checks, boundaries, and fallbacks apply to that domain operation, keep those choices explicit within the operation itself.

---

## Safe Implicit Infrastructure vs. Dangerous Implicit Semantics

Not all hidden behavior carries the same risk profile. When designing systems that both humans and agents can easily reason about, separate generic operational plumbing from logic that alters business execution.

### Safe Candidates for Implicit Infrastructure
These concerns rarely alter control flow, business state, or data correctness. They can safely live in background middleware, delegating handlers, and framework hooks:

```text
Structured diagnostic logging
Distributed tracing spans (W3C trace context)
Request duration metrics and counters
Payload compression (Gzip/Brotli)
Correlation ID propagation
Wire-format serialization and deserialization
Connection pooling and socket lifecycle
```

### Dangerous Candidates for Implicit Handling
These mechanisms directly dictate business rules, data boundaries, and operational safety. Hiding them behind ambient contexts or magic interceptors dramatically increases the likelihood of breaking changes:

```text
Authorization and role/permission enforcement
Tenant isolation and data filtering
Domain-level input validation
Database transaction boundaries and isolation levels
Retry policies and backoff curves
Idempotency keys and replay protection
Cache read/write/invalidation rules
Feature flag evaluations
Locale, currency, and timezone conversions
Dynamic handler or strategy resolution
Domain error mapping and status codes
```

A good working rule:

> **Infrastructure mechanics can be implicit. Business-relevant semantics should be explicit.**

While the boundary between the two can occasionally blur, applying this standard keeps critical business paths visible and maintainable.

---

## Global Configuration Still Has Value

Keeping semantics explicit does not mean copy-pasting low-level implementation details into every single endpoint.

Consider a retry policy. You do not want every developer or agent writing custom loop logic, defining arbitrary backoff math, or hand-picking HTTP status codes inside every handler. You still centralize the policy definition:

```csharp
RetryPolicies.ExternalRead
```

That policy configuration centrally establishes the operational rules:

```text
3 retry attempts
Exponential backoff with full jitter
Triggered on connection timeouts
Triggered on HTTP 502, 503, and 504 status codes
```

The handler, meanwhile, simply references the policy by name:

```csharp
.Retry(RetryPolicies.ExternalRead)
```

This draws a clean line between two separate concerns:

```text
Local call site:
WHAT semantic policy applies to this operation

Central configuration:
HOW that policy is executed under the hood
```

This balances reusability with visibility. The policy logic is defined once, tested once, and maintained centrally. But the call site explicitly declares that retries are active, alerting both humans and agents to how the operation behaves.

---

## Named Semantics vs. Silent Global Behavior

Look at the difference between these two approaches when dealing with an HTTP call.

First, the silent approach:

```csharp
await client.SendAsync(request);
```

Here, an engineer added a Polly handler to the underlying `HttpClient` registration in an IoC module three directories away. The call site looks like a simple one-off request, but it quietly executes retries behind the scenes.

Now look at the explicit alternative:

```csharp
await request
    .Retry(RetryPolicies.ExternalRead)
    .Execute();
```

Both approaches encapsulate the retry logic inside an abstraction. But the second version leaves an explicit **semantic trace** at the call site.

An agent analyzing that code immediately knows a vital piece of context:

```text
This operation is expected to run multiple times in failure scenarios.
```

That single piece of explicit context directly informs how the agent handles:

- Ensuring downstream operations are strictly idempotent
- Generating unique database keys or transaction IDs before the loop
- Avoiding unintended side effects (such as sending duplicate emails or queue messages)
- Managing request stream positions during retries

The implementation remains clean and reusable, but the semantic reality is impossible to miss.

---

## The Breakdown of "Global" Policies in Large Systems

This shift toward explicit policy application also solves an architectural failure mode that predates AI: the myth of the truly global policy.

In any system of substantial size—spanning hundreds of endpoints, dozens of integration surfaces, multiple persistence engines, and wildly different performance SLAs—a single "global" policy almost never survives contact with production.

What starts as a clean, centralized rule:

```text
All HTTP calls automatically retry three times on failure.
```

inevitably decays under production edge cases into a maze of special-case exceptions:

```text
Default retry policy
  except for Payment gateway calls (risk of double billing)
  except for Bulk export endpoints (timeouts cause massive memory pressure)
  except for Legacy inventory integrations (cannot handle concurrent retries)
  unless the request payload is a non-rewindable stream
  unless the endpoint implements INonRetryable
  unless [SkipGlobalRetries] is decorated on the action
```

Before long, that "clean" centralized configuration becomes its own fragile, highly coupled sub-program. The apparent simplicity of each endpoint is paid for by massive, invisible complexity lurking in framework filters.

A much cleaner, more scalable architecture uses hierarchical policy scoping:

```text
System defaults
→ Module-level defaults
→ Operation categories
→ Explicit local overrides
```

For instance:

```text
Catalog Module:
    Default: External read operations may retry

Payments Module:
    Default: Zero retries on mutating commands unless an explicit idempotency key is proven

Reporting Module:
    Default: Extended timeouts, read-uncommitted transaction semantics
```

The concrete policy implementations remain centralized and shared, but the *application* of the policy stays anchored directly to the operation.

---

## Mechanically Expandable Abstractions

There is an alternative path that allows us to keep local code concise without blinding automated agents: making abstractions **mechanically expandable** through tooling.

Imagine local code that remains cleanly abstracted:

```csharp
.Retry(RetryPolicies.ExternalRead)
```

Instead of forcing an agent to search the repository and guess how `RetryPolicies.ExternalRead` is defined, the development environment (via an LSP extension, a Roslyn analyzer, or a CLI command) allows the agent to issue a structured query:

```text
resolve RetryPolicies.ExternalRead
```

The tooling immediately expands the abstraction into its full mechanical definition:

```text
max attempts: 3
backoff: exponential (initial: 200ms, factor: 2.0)
jitter: enabled
handled exceptions:
  - System.TimeoutException
  - HttpRequestException (where StatusCode in [502, 503, 504])
```

You can apply that same mechanical expansion to an entire endpoint:

```text
inspect endpoint GetOrder

resolved pipeline:
  authentication:
    scheme: Bearer
    required: true
  authorization:
    policy: ReadOrderPolicy
    required claims: [ "orders.read" ]
  validation:
    validator: GetOrderValidator
  tenant context:
    source: Header (X-Tenant-ID)
    enforcement: GlobalQueryFilter (Orders.TenantId == CurrentTenant)
  transaction:
    ambient: false
    mode: ReadOnly
  retry:
    policy: ExternalRead (max: 3)
  handler:
    target: GetOrderHandler
  caching:
    key: "orders:{id}"
    ttl: 300s
```

This points to a vital requirement for the next generation of application frameworks:

> **Abstractions must be mechanically expandable via machine-readable tooling.**

Markdown documentation is helpful for human onboarding, but a machine-readable, fully resolved execution graph allows an agent to navigate abstractions with near-perfect reliability, eliminating the guesswork caused by runtime magic.

---

## Designing Abstractions for Agent Readability

Human-centric API design has historically prioritized terseness:

```text
Minimal lines of code
Minimal method parameters
Zero boilerplate
Aggressive reuse of implicit behaviors
```

Agent-centric API design shifts those priorities toward clarity and predictability:

```text
Semantic locality over textual brevity
Explicit dependencies over ambient context
Visible control flow over interceptor chains
Mechanically discoverable behavior over convention-based magic
Predictable composition over dynamic runtime dispatch
```

This does not mean code has to become low-level or messy.

```csharp
.RetryTransient(attempts: 3)
```

is still an abstraction. It completely encapsulates the complex mechanics of timers, backoff calculations, cancellation tokens, and exception matching. But it keeps the critical semantic reality front and center: *this operation can and will execute multiple times.*

Compare that to:

```csharp
.ExecuteUsingStandardEnterprisePolicies()
```

That second method completely obscures the execution characteristics of the call. It saves a few characters at the cost of hiding every semantic detail an agent needs to know to write safe code.

> **A well-designed abstraction reduces mechanical syntax without obscuring business semantics.**

---

## Encoding Business Meaning in the Ubiquitous Vocabulary

Semantic locality goes beyond where code physically executes. It also depends heavily on whether the source code uses the exact same concepts and vocabulary as the surrounding domain model, database schema, API contracts, tests, and business documentation.

Take this routine conditional:

```csharp
if (payment != null)
{
    // ...
}
```

In an older codebase, this check might quietly rely on an unwritten convention: *if a payment record exists in this table, it means the invoice has been created but is currently unpaid.*

A staff engineer who has worked on the billing engine for three years knows that convention by heart. An agent has no way of knowing it. The agent sees a technical null-check:

```text
Payment record exists
```

From that, it has to guess the underlying business state:

```text
Invoice is unpaid
```

That inference is fragile. In many cases, the agent will misinterpret the check, assume the payment has already cleared, and write code that introduces subtle accounting bugs.

Now look at the explicit version:

```csharp
if (payment.Status == PaymentStatus.Unpaid)
{
    // ...
}
```

Or better yet:

```csharp
if (payment.IsUnpaid)
{
    // ...
}
```

Now the domain concept is stamped directly into the code.

This becomes especially powerful when the same concept appears across different parts of the system. If the architecture documentation states:

```text
"Retry unpaid payments after 24 hours"
```

The OpenAPI specification defines:

```yaml
paymentStatus:
  type: string
  enum: [unpaid, processing, settled, failed]
```

And the test suite contains:

```csharp
[Fact]
public async Task ShouldRetryUnpaidPayment_WhenGracePeriodExpires()
```

An agent searching the repository can instantly and accurately link the documentation, the API spec, the unit tests, and the source code using the shared identifier:

```csharp
PaymentStatus.Unpaid
```

That link breaks down completely when business states are hidden behind technical sentinels or indirect object checks:

```csharp
amount == 0
endDate == null
retryCount == -1
statusCode == 2
customerId != null
```

These raw values usually encode core business rules:

```text
amount == 0            → Plan is free
endDate == null        → Subscription is actively running
retryCount == -1       → Retry policy is unlimited
statusCode == 2        → Transaction is awaiting settlement
customerId != null     → Order has an assigned customer profile
```

Writing code that relies on raw sentinel values forces the agent to constantly infer intent from technical artifacts. A much safer, agent-friendly codebase elevates those technical states into first-class business domain models:

```csharp
price.IsFree
subscription.IsActive
retryPolicy.IsUnlimited
payment.Status == PaymentStatus.Unpaid
order.HasAssignedCustomer
```

> **Code should express explicit business conclusions, not just raw technical states from which those conclusions must be deduced.**

This semantic alignment should be consistent across every engineering artifact:

```text
Documentation:
    "unpaid payment"

Domain Code:
    PaymentStatus.Unpaid

API Contract:
    paymentStatus: "unpaid"

Database Schema:
    payment_status = 'unpaid'

Domain Event:
    PaymentMarkedUnpaidIntegrationEvent

Test Suite:
    ShouldRetryUnpaidPayment()
```

This strict alignment gives an agent distinct advantages:

- Codebase-wide symbol searches yield precise, relevant hits.
- Vector embeddings and RAG pipelines retrieve the exact files needed for a task without pulling in irrelevant noise.
- Translating an issue description or user story into an actionable code modification requires zero guesswork.
- Code reviews and diff validations become significantly more deterministic.
- Generated code uses the existing domain language instead of hallucinating parallel concepts.

Inline comments can help bridge the gap when dealing with legacy systems:

```csharp
// In the legacy billing system, a non-null payment record indicates an unpaid invoice.
if (payment != null)
```

While useful, comments are fundamentally second-class citizens compared to strongly typed models. They drift out of date, they don't participate in compiler type-checking or refactoring tools, and they leave the underlying execution model indirect.

If you are dealing with legacy databases where you cannot alter the underlying storage representations (e.g., a database column where `2` means `unpaid`), push that translation to the boundary. Use mapping layers to convert the database sentinel into a rich domain enum before it reaches your application code:

```csharp
// Map legacy database integer to domain enum at the repository boundary
PaymentStatus = legacyRow.payment_state switch
{
    2 => PaymentStatus.Unpaid,
    3 => PaymentStatus.Settled,
    _ => PaymentStatus.Unknown
};
```

Keep your domain vocabulary unified across code, schemas, tests, and documentation. It spares human engineers from having to memorize tribal knowledge, and it spares agents from having to make blind guesses about what your code is doing.

---

## Semantic Locality as an Architectural Metric

We evaluate architectures using cohesion, coupling, cyclomatic complexity, and duplication. As automated development tools become standard, **semantic locality** belongs on that list.

You can think of semantic locality as a spectrum:

### Maximum Semantic Locality
```csharp
CalculatePrice(order, customer, pricingRules);
```
Every input, dependency, and rule required to compute the outcome is passed directly into the function. There is zero ambient context, no dynamic dependency lookup, and no framework interference. You can evaluate the function in total isolation.

### Moderate Semantic Locality
```csharp
priceCalculator.Calculate(order);
```
The dependencies are abstracted behind an interface. You have to locate the concrete implementation of `IPriceCalculator`, but the execution graph is still direct and discoverable through standard static analysis.

### Degraded Semantic Locality
```csharp
priceCalculator.Calculate(order);
```
The interface is identical, but `IPriceCalculator` is dynamically resolved at runtime through a container factory that evaluates an ambient `OperationContext`. Static analysis alone can no longer identify which implementation runs.

### Minimal Semantic Locality
```csharp
priceCalculator.Calculate(order);
```
The interface and method call look entirely harmless, but the actual computation is shaped by a sprawling runtime environment:

```text
Ambient tenant context (via AsyncLocal)
Dynamic feature toggles
Thread-local security context (ClaimsPrincipal)
EF Core global query filters
Interceptors modifying database commands
Distributed caching decorators
Ambient transaction scopes
```

The method signature remains short and clean, but the cognitive overhead required to reason about what it actually does is massive.

In an agent-maintained codebase, low semantic locality causes immediate problems. It burns through the agent's context window, causes hallucinated implementations, and results in modifications that break outside the immediate call site.

---

## What Pragmatic Architecture Looks Like Going Forward

The goal is not to swing the pendulum all the way back to procedural, un-abstracted spaghetti code. We do not need to abandon design patterns, interfaces, or frameworks.

The shift is much more practical:

```text
Hide underlying runtime mechanics
Expose critical semantic decisions
Centralize policy logic
Localize domain intent
Make abstractions inspectable and expandable
```

Code written this way will occasionally be slightly more verbose than architectures that push everything into framework filters and dynamic interceptors. You might write five lines of clear, composable pipeline configuration where you used to write a single opaque method call.

In exchange for that slight increase in verbosity, you gain a system that is:

- Dramatically safer for coding agents to modify without side effects
- Faster and less mentally exhausting for human engineers to review
- Straightforward to unit test and integration test without spinning up massive mocking setups
- Clear and predictable during static analysis and profiling
- Free of tribal knowledge and unwritten architectural conventions
- Far more resilient to automated large-scale refactoring

The industry's definition of "clean code" was forged in an era when saving keystrokes was paramount because humans had to write and maintain every character by hand. 

When code is increasingly navigated, maintained, and modified by automated agents, hiding runtime semantics behind layers of dynamic magic is no longer clean—it is an architectural liability. True architectural quality will be measured by how clearly and explicitly a system expresses its intent.

---

