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
