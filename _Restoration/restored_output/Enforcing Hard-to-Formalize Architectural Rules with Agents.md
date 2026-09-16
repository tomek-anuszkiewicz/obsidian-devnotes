---
title: "Enforcing Hard-to-Formalize Architectural Rules with Agents"
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
  - The Semantic Verification Continuum
  - Human Review Intuition as Executable Policy
---

Traditional software quality automation works best when a rule can be expressed precisely.

Consider the rules we already know how to verify automatically:

```text
Domain must not reference Infrastructure.
Every public endpoint must require authorization.
Result must never be negative.
All handlers must implement a particular interface.
```

We have spent decades building reliable tooling to enforce constraints like these:

- Unit and integration tests
- Static architecture tests (such as ArchUnit or custom AST visitors)
- Compiler type systems
- Linters and static analysis security testing (SAST) tools
- CI gating scripts

These tools are deterministic, fast, cheap to run, and reproducible. They form the backbone of modern build pipelines, and nothing about modern AI tooling changes their necessity.

However, a massive portion of software engineering has never fit into this deterministic model. Many of our most critical design guidelines are not difficult because engineers fail to understand them; they are difficult because translating them into static, binary rules is either prohibitively expensive or practically impossible.

LLM-based review agents give us a way to automate this previously human-only layer of software verification.

---

## Many Real Engineering Rules Are Semantic

#coding_standard

Consider the guidelines that populate team wikis, design docs, and pull request comments:

> Do not introduce an abstraction unless it represents a meaningful boundary.

> Controllers should remain thin adapters, but trivial request mapping does not justify an intermediate service layer.

> Modules should communicate through their public contracts rather than reaching into each other's internals.

> Do not introduce a generic framework for a problem that exists in only one place.

> Business rules should remain visible in domain code rather than being hidden inside ORM hooks, infrastructure helpers, or database triggers.

> Ensure error handling fails safely without swallowing the root cause.

Every seasoned engineer recognizes these principles. An experienced lead can review a diff and spot a violation within seconds. Yet encoding them as deterministic linting rules or compiler checks requires an extraordinary amount of AST plumbing—if it can be done at all.

The difficulty is not a lack of clear thinking. The difficulty is that these rules are fundamentally semantic. They depend on:

- **Developer intent**: What problem is this code actually trying to solve?
- **Context and placement**: Is this helper function truly generic, or is it tightly coupled to a single billing workflow?
- **Naming and domain language**: Does the method name reflect real business behavior or merely mechanical execution?
- **Surrounding architecture**: How do adjacent modules handle similar state transitions?
- **Degree rather than binary states**: Where is the line between a clean abstraction and premature over-engineering?

Because static analyzers operate on syntax trees rather than semantic intent, enforcement has historically relied on a single runtime: human attention.

---

## Human Attention Was the Missing Runtime

#review

Repositories routinely accumulate passive architectural documentation:

```text
docs/
├── architecture/principles.md
├── domain/invariants.md
├── conventions/error-handling.md
└── adrs/
    ├── 0004-isolate-payment-gateways.md
    └── 0012-outbox-event-streaming.md
```

The team reads these documents during onboarding. Everyone agrees with them in principle. But in practice, nothing executes them. Their runtime model is fragile:

```text
developer remembers the rule
        +
reviewer remembers the rule
        +
reviewer notices the violation while skimming a diff
```

This model breaks down under normal development pressure. Even top-tier engineers:

- Experience cognitive fatigue after reviewing multiple pull requests in a day.
- Skim large diffs, focusing on the files they understand best while glazing over peripheral changes.
- Focus on obvious stylistic issues or immediate business logic bugs while missing architectural drift.
- Simply forget an Architectural Decision Record (ADR) written eight months earlier.

A review agent changes this dynamic because it acts as an execution engine for passive documentation. It can evaluate code diffs against written guidelines systematically, on every single pull request, without fatigue.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   THE THREE-TIER VERIFICATION MODEL                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    ▼                               ▼                               ▼
[ TIER 1: DETERMINISTIC ]     [ TIER 2: SEMANTIC AGENTS ]    [ TIER 3: HUMAN JUDGMENT ]
• Compilers & Type Systems    • Natural-language policies     • Strategic business trade-offs
• Linters & AST Analyzers     • Architectural boundary leaks  • Risk tolerance & exceptions
• Unit & Integration Tests    • Unnecessary abstractions      • Unclear product intent
"Fast, cheap, reproducible"   "Context-aware architectural    "Final authority on system
                              intent & domain invariants"     evolution and design"
```

---

## Natural-Language Rules Can Become Executable Policies

Suppose an agentic reviewer in your CI pipeline has access to your repository's ADRs and architectural guidelines. For every incoming pull request, the agent executes a structured evaluation:

1. **Scope the Diff**: Identify the modified components, interfaces, database migrations, and public contracts.
2. **Retrieve Governing Policies**: Pull the relevant ADRs, boundary rules, and domain invariants matching those components.
3. **Evaluate Intent**: Check whether the implementation honors the spirit of the guidelines, rather than just matching syntax.
4. **Emit High-Signal Feedback**:
   - Point directly to the offending code block.
   - Cite the specific guideline or ADR being violated.
   - Explain *why* the implementation breaks the design intent.
   - Account for documented exceptions before commenting.
   - If confidence is low, stay silent to avoid review fatigue.

This is not an executable specification in the classical, deterministic sense. It is a **natural-language executable policy**. The fundamental shift is that an architectural rule no longer needs to be compiled into a custom linter plugin before it can be enforced automatically.

---

## The Semantic Gap: Real-World Scenarios

To see why this matters, consider where deterministic tools stop and semantic review begins.

### Case 1: The Database Shadow Leak

A team establishes an architectural boundary: *The Billing module must never depend on the Inventory module's internal data model.*

```text
┌──────────────────┐           ┌──────────────────┐
│  Billing Module  │           │ Inventory Module │
└─────────┬────────┘           └─────────┬────────┘
          │                              │
          │         Direct SQL Query     │
          └─────────────────────────────►│ [inventory_items]
            (Bypasses Service Contract)  │ (Internal Schema)
```

- **Deterministic Check**: A static dependency linter inspects project dependencies and module imports. It reports green: the `Billing.csproj` file does not reference `Inventory.Data.dll`, and no TypeScript imports cross the module boundary.
- **The Code**: Inside a billing handler, an engineer writes a direct SQL query against the `inventory_items` database table to fetch stock counts, bypassing the `InventoryService` public API to save time.
- **Semantic Review**: The linter sees an innocent database client executing a raw string query. The review agent, having read the boundary policy, recognizes that `inventory_items` belongs to the Inventory domain and flags the direct persistence coupling immediately.

### Case 2: Accidental or Malicious Compliance

A team enforces a strict business rule: *An invoice total must never be negative.*

```csharp
public decimal CalculateInvoiceTotal(Order order, Discount discount)
{
    var rawTotal = order.Subtotal - discount.Amount;
    
    // Developer adds this to pass the test: Assert.True(invoiceTotal >= 0)
    return Math.Max(0, rawTotal);
}
```

- **Deterministic Check**: A unit test runs `Assert.True(CalculateInvoiceTotal(order, discount) >= 0)`. The test suite passes cleanly in CI.
- **Semantic Reality**: Clamping the total to zero with `Math.Max` masks an invalid financial calculation. If the discount exceeds the subtotal, that indicates an invalid state, a race condition, or a misconfigured promo engine. Silently swallowing the negative value causes ledger drift down the line.
- **Semantic Review**: The unit test checks the mechanical boundary. The semantic reviewer evaluates the business context: *Clamping to zero hides an upstream discount calculation bug instead of explicitly failing or rejecting the operation.*

### Case 3: Premature Generic Boilerplate

A developer needs to query an external currency exchange rate service.

```text
src/
└── Currency/
    ├── IExchangeRateProviderFactoryStrategy.cs
    ├── AbstractExchangeRateProviderFactory.cs
    ├── CurrencyProviderRegistryPool.cs
    └── DefaultCurrencyExchangeRateProvider.cs
```

- **Deterministic Check**: Code compiles cleanly. SOLID principles are technically adhered to: interfaces are defined, dependencies are injected, and classes are small. SonarQube reports zero code smells.
- **Semantic Reality**: This exchange rate logic is used in exactly one background job. The three levels of factory indirection add maintenance overhead and mental drag without providing any runtime flexibility.
- **Semantic Review**: The review agent cross-references the pull request diff with the rest of the codebase, noticing that this abstraction has only a single implementation and a single call site. It notes that this violates the repository guideline: *Do not introduce generic frameworks or factory indirection for single-use dependencies.*

---

## Agents Are Relentless Reviewers

The real leverage of an LLM agent is not just that it can parse natural-language rules; it is that it applies them with unbroken procedural consistency.

A human tech lead might hold twenty architectural principles in their head. During a busy week, reviewing their tenth pull request on a Thursday afternoon, they will consciously evaluate perhaps three or four of them. They focus on the core business logic, skim the configuration changes, and approve the PR.

An agent evaluates the change against all twenty principles, every time. It does not care that:

- The diff spans 1,500 lines across 40 files.
- The change consists of repetitive, boring boilerplate.
- It is reviewing its sixtieth pull request of the day.
- A rule has passed without incident for the last six months.

This makes agents uniquely effective at catching rules that are individually critical but rarely violated. Humans are notoriously poor at maintaining vigilance for edge cases that almost always return "all clear." Machines do not experience boredom.

---

## Formal Rules Must Remain Deterministic

It is critical not to swing too far in the opposite direction. There is a real failure mode in thinking:

> *Now that we have LLM review agents, we can stop writing linters and unit tests.*

Replacing a deterministic check with a language model prompt is an architectural regression.

```text
// PREFER THIS:
Assert.True(result >= 0);

// NEVER REPLACE WITH THIS:
"Please review the code and tell me if `result` could ever be negative."
```

Deterministic verification is:

- **Order-of-magnitude faster**: Microseconds or milliseconds versus seconds of network latency and inference.
- **Substantially cheaper**: Local CPU instructions versus LLM token generation.
- **100% reproducible**: Zero temperature variation or model drift.
- **Trivially debuggable**: A failing test points directly to the failed assertion line and stack trace.

A sound principle for engineering teams is:

> Formalize what is cheap to formalize. Use agents where formalization becomes disproportionately complex or brittle.

The goal is not to hide deterministic rules from the agent. The agent must fully understand the deterministic constraints so it can maintain an accurate mental model of the system. If an agent spots a code path that appears to generate a negative balance, its first action should be to check whether existing unit tests cover that case—and if not, flag the missing test assertion.

---

## Connecting the Formal and the Semantic

The most effective quality pipelines use semantic agents to bridge the gap between static analysis and architectural intent.

```text
┌────────────────────────────────────────────────────────┐
│                  A BALANCED CI PIPELINE                │
└───────────────────────────┬────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        ▼                                       ▼
┌──────────────────────────────┐    ┌──────────────────────────────┐
│     DETERMINISTIC GATES      │    │        SEMANTIC GATES        │
│ • Compilation & Typechecks   │    │ • Policy & ADR Alignment     │
│ • Unit & Integration Tests   │    │ • Boundary Leak Detection    │
│ • Linter & SAST Scanners     │    │ • Intent & Context Review    │
└──────────────┬───────────────┘    └──────────────┬───────────────┘
               │                                   │
               └─────────────────┬─────────────────┘
                                 ▼
               ┌──────────────────────────────────┐
               │         MERGE CRITERIA           │
               │   Both Mechanical Invariants    │
               │    and Semantic Intent Pass      │
               └──────────────────────────────────┘
```

Consider how this works in practice:

1. **Detecting Semantic Evasion**: An architecture test asserts that `Core.Domain` cannot import `ThirdParty.Stripe`. A developer works around this by having `Core.Domain` read raw JSON payloads directly and parsing the Stripe webhook schema inline. The static namespace check passes cleanly. The semantic agent flags that domain models are now coupled to Stripe's raw wire schema.
2. **Explaining Opaque Failures**: A deterministic rule fails: `ArchitectureTest: ArchUnit rule violated - Assembly A references Assembly B`. Instead of leaving the developer to reverse-engineer why the dependency rule exists, the agent annotates the failure:
   > *"This rule exists because Assembly B contains persistence models tied to our legacy database schema. The intended integration point between these modules is `CustomerContract` in `Shared.Contracts`."*

The deterministic test gives certainty; the semantic agent gives context and intent.

---

## The Escalation Flywheel

Agentic review should not remain a permanent token tax for recurring, predictable violations. Instead, it acts as an exploratory incubator for new deterministic rules.

When an agent catches the same architectural boundary violation across several pull requests, that is a clear signal that the pattern has stabilized enough to be formalized.

```text
Informal architectural principle written in an ADR
                       │
                       ▼
Agent repeatedly checks and enforces it in PR reviews
                       │
                       ▼
Violation pattern stabilizes into predictable syntax/paths
                       │
                       ▼
Rule is formalized into an AST linter or architecture test
                       │
                       ▼
Agent instructions are updated, freeing context window for newer subtleties
```

This lifecycle keeps the review pipeline balanced:

1. **Informal**: A new convention is documented in markdown as team taste evolves.
2. **Semantic**: An agent enforces it, handling the edge cases, false positives, and context gathering.
3. **Formalized**: Once the boundary is well-defined and stable, write an AST linter or an architecture test (e.g., using ArchUnit, ESLint custom rules, or CodeQL).
4. **Retired**: Remove the mechanical check from the agent's prompt to save context and tokens, letting the compiler or linter guard that boundary permanently.

---

## Ephemeral Investigation vs. Permanent Tests

Agents also change how we write and run tests during code review.

Traditionally, every test written must be checked into version control and maintained indefinitely. This creates test-suite bloat: suites grow slower, CI times creep up, and engineers spend time updating assertions that validate minor internal implementation details.

An agent can treat tests as **temporary investigative tools**:

```text
1. Agent reviews a diff modifying an in-memory session cache.
2. Agent hypothesizes: "If two concurrent requests hit this lock simultaneously during a token refresh, the cache may drop the secondary write."
3. Agent writes an ephemeral concurrency test script in a sandbox.
4. Agent runs the script 100 times against the PR branch.
5. If no race occurs, the script is discarded—no permanent test suite bloat.
6. If the race condition reproduces, the agent posts the failing trace in the review and provides the test script as a permanent regression candidate.
```

This bifurcates testing into two distinct categories:

- **Permanent Specifications**: Tests committed to the repository that assert stable, long-term domain invariants.
- **Investigative Probes**: Ephemeral tests spun up on the fly to pressure-test specific assumptions during review.

---

## Continuous Architecture Review

Historically, architecture reviews happen in periodic meetings, during design phases, or when a major feature lands on a senior engineer's desk. Between those moments, codebases suffer gradual architectural decay: small compromises, slightly misaligned dependencies, and temporary hacks that become permanent.

With semantic review agents, architecture review becomes continuous. Every pull request is evaluated by an agent asking the questions a principal engineer would ask:

- *Did this change introduce a new dependency direction between bounded contexts?*
- *Did an internal implementation detail leak through a public module interface?*
- *Was an abstraction layer added, and does it have a concrete reason to exist today?*
- *Does this pattern contradict an active ADR?*
- *Does this implementation increase coupling in a way that will complicate planned migrations?*
- *Is business validation creeping into the presentation or infrastructure layers?*

These are not questions about syntax, spacing, or null checks. They are questions about software architecture.

---

## Practical Implementation for Engineering Teams

When rolling out semantic review agents, follow these operational rules:

1. **Protect your token budget on deterministic checks**: Do not ask an LLM to check code formatting, type safety, or missing imports. Let your compiler, Prettier, and standard linters handle syntax.
2. **Structure rules around domain context**: Store your design standards in structured, clear markdown documents (`docs/architecture/`). Treat those documents as inputs to your review agent's prompt harness.
3. **Require concrete evidence**: Configure your review agent to quote specific lines of code, cite the governing guideline, and explain the architectural impact before it comments.
4. **Tune for high precision**: If the agent's confidence in an architectural violation is low or ambiguous, it should stay silent. False alarms kill developer trust faster than missed edge cases.
5. **Run the escalation flywheel**: Review the agent's recurring comments monthly. If it repeatedly catches the same structural error, write a deterministic architecture test and remove that check from the prompt.

By treating natural-language documentation as an executable policy layer, teams bridge the gap between static analysis and human design intuition. Deterministic tools provide the rock-solid foundation; semantic agents provide the reach.
