---
title: "The Increasing Value of Comments in AI-Generated Code"
tags:
  - ai-agents
  - software-engineering
  - documentation
  - code-review
  - maintainability
  - intent-specification
  - code-comments
aliases:
  - Code Comments in AI Era
  - Semantic Value of Comments in AI Code
  - Comments as Local Context Retrieval
  - Negative Knowledge Comments in Agentic Code
---

The traditional rule for writing comments has long been summarized simply:

> Good code should explain what it does. Comments should explain why.

For years, many engineering teams pushed this idea to an extreme: *"Good code is completely self-documenting. If you need a comment, your code is too complicated."* That rule was a healthy reaction against lazy comments that merely parroted the syntax:

```csharp
// Increment the counter by one
counter += 1;
```

Modern language models and coding agents parse syntax, infer control flow, and trace call graphs effortlessly. Writing comments that describe *what* an algorithm does or narrate its execution step-by-step is an absolute waste of context. 

However, in codebases increasingly written, refactored, and maintained by AI agents, comments that preserve the *why*—the non-obvious business intent, external constraints, and historical edge cases—become the most valuable lines in your repository.

Agents can reconstruct the mechanics of code very well. They cannot reconstruct the hidden business contracts, upstream vendor bugs, or physical infrastructure limits that forced those mechanics into existence.

```text
TRADITIONAL VIEW:
  Comments explain code mechanics ──► Low value (clean code is readable).
  Business intent lives in Jira, Slack, ADRs, or developers' heads.

AGENTIC REALITY:
  Descriptive comments (what code does) ──► Zero value (models parse ASTs instantly).
  Contextual comments (why it must be this way) ──► Maximum value.
  Comments are the only documentation guaranteed to sit directly inside
  the model's context window alongside the code being edited.
```

---

## Code Is Self-Documenting Syntactically, Not Semantically

Well-written code communicates structure and execution flow clearly:

```csharp
// Charge 50% if booking starts in less than 3 days.
if (booking.StartDate < DateTime.UtcNow.AddDays(3))
{
    cancellationFee = booking.TotalPrice * 0.5m;
}
```

The comment above adds almost no value. It merely translates the C# conditional into English.

Compare that with:

```csharp
// Cancellations within 72 hours are charged 50% because the supplier
// no longer refunds us after this point.
// Do not replace this with the standard hotel cancellation policy.
if (booking.StartDate < DateTime.UtcNow.AddDays(3))
{
    cancellationFee = booking.TotalPrice * 0.5m;
}
```

The code explains the mechanism. The comment preserves information that cannot be derived from the AST or the types alone:
- Why the rule exists.
- Where the rule originated (a commercial supplier contract).
- Whether the magic number (`3` days / `0.5m`) is intentional or arbitrary.
- Which specific business domain it represents.
- What seemingly reasonable refactoring would break the business model.

Consider another idiomatic example:

```csharp
ApplyNonRefundableSupplierCancellationFee();
```

A clean method name communicates intent better than an obscure conditional, but it still leaves crucial production questions unanswered:
- Why is this specific supplier handled differently from others?
- Does this behavior stem from a contractual clause or a temporary operational workaround?
- Is it tied to specific product classes, or across the board?
- Can another developer—or an agent—safely consolidate this with a similar-looking fee calculation?
- What unstated assumptions break if this method is invoked out of order?

Clean naming captures executable abstractions. It does not capture commercial realities or environmental boundaries.

---

## Comments as Physical Local Context Retrieval

Historically, domain context lived outside the codebase:
- In developer memory.
- In closed Jira tickets and PR discussions.
- In Slack threads that expired months ago.
- In design docs and Architecture Decision Records (ADRs).

When a human senior engineer works on a task, they rely on institutional memory or conduct archaeological research across these tools. An autonomous coding agent working on a prompt does not.

Suppose an agent receives a localized ticket:
> *"Add partial cancellation support for multi-room bookings."*

The harness or language server retrieves the files and classes responsible for booking cancellations. The agent receives a localized window of code—often just a few thousand tokens sliced out of a massive repository.

```text
TICKET: "Add partial cancellation support"
                      │
                      ▼
            Agent Retrieval Step
                      │
      ┌───────────────┴───────────────┐
      ▼                               ▼
[CancellationService.cs]    [BookingDomainModel.cs]
  (Loaded into context)       (Loaded into context)
      │                               │
      └───────────────┬───────────────┘
                      ▼
   Agent Prompt Context Window (20k tokens)
   ────────────────────────────────────────
   - Code AST & Signatures
   - INLINE COMMENTS (Loaded automatically)
   ────────────────────────────────────────
   MISSING FROM CONTEXT:
   - Jira ticket from 2022 explaining supplier agreements
   - Confluence ADR #42 on cancellation fee structures
   - Slack incident thread debugging double-billing
```

Any comment physically written inside those classes is guaranteed to enter the model's context window.

This makes inline comments a highly reliable, zero-latency local knowledge base. The agent does not need to guess that an ADR exists, know which search term to query against a vector store, or run tool calls across an issue tracker. The context is physically bound to the exact lines of code being evaluated.

---

## Why Git Blame and Issue Trackers Cannot Replace Inline Comments

A common pushback from clean-code purists is: *"If someone wants to know why a line exists, they can check `git blame` or the original commit."*

While that works for a human engineer during a deep investigation, agents routinely fail to use source control history effectively during automated tasks:

1. **Lack of Proactive Doubt:** LLMs generate code based on statistical pattern matching. When an agent sees an unusual condition or a seemingly redundant check, it does not instinctively wonder: *"Could there be an obscure production incident from 18 months ago that necessitated this?"* It assumes the check is inefficient dead code, refactors it away, and moves on with high confidence.
2. **Context and Latency Overhead:** Instructing an agent to run `git log -S`, inspect commit diffs, and query issue trackers for every line of code it considers touching explodes tool roundtrips, token consumption, and execution time.
3. **History Decay:** Codebases experience churn. Bulk formatting passes, linter updates, namespace renames, and prior automated refactorings easily overwrite `git blame` annotations with meaningless commit messages (`style: run prettier`, `refactor: reorder imports`).
4. **Preventative vs. Post-Mortem Value:** `git blame` is an autopsy tool used *after* a defect surfaces. An inline comment is a preventative guardrail positioned directly in the prompt *before* the model generates the wrong diff.

---

## Negative Knowledge: Protecting Against Naive Simplification

Some of the highest-leverage comments describe what **not** to do.

When an agent analyzes code, its baseline objective is to clean up redundancies, eliminate boilerplate, and standardize patterns. If a code block looks unusual, the model's default instinct is to "fix" it.

Negative knowledge comments explicitly block those tempting simplifications.

### 1. Invariant and Contract Guards (C#)

```csharp
// Do not calculate this from Payment.Amount.
// Legacy bookings may already contain the agency margin there,
// leading to double-counting margins on pre-2023 reservations.
decimal baseAmount = payment.RawTransactionTotal;
```

```csharp
// This check looks redundant, but some suppliers occasionally send
// the same reservation with different external IDs across parallel webhooks.
if (existingReservations.Any(r => r.SupplierReference == incomingRef && r.Status != Status.Cancelled))
{
    return DuplicateResolutionResult.Ignore;
}
```

```csharp
// Intentionally executed before availability validation.
// Sales requires the original quoted price to remain available
// even when inventory availability checks subsequently fail.
pricingEngine.PinQuotedRate(bookingSession.QuoteId);
```

Without these comments, an agent performing a routine cleanup will see:
- An indirect calculation instead of `Payment.Amount` $\rightarrow$ refactor to use the standard property $\rightarrow$ silently corrupt financial reports.
- A redundant lookup on `SupplierReference` $\rightarrow$ remove it to save a database round-trip $\rightarrow$ reintroduce duplicate bookings in production.
- A price-pinning call placed ahead of validation $\rightarrow$ move it after the guard clauses $\rightarrow$ break sales requirements.

### 2. Driver and Protocol Limits

Consider an ingestion batch size:

```csharp
// WIRE PROTOCOL LIMIT:
// The underlying Postgres driver allows a maximum of 65,535 query parameters.
// With 240 columns per telemetry record, any batch larger than 273 rows triggers 
// a silent driver parameter buffer overflow. We cap at 250 for safety margin.
// DO NOT increase this batch size without changing the driver protocol.
public const int TelemetryBatchSize = 250;
```

An agent asked to *"optimize ingestion throughput"* will naturally look at a batch size of 250 and try to bump it to 5,000 to minimize network roundtrips. That comment explicitly explains the mechanical ceiling of the runtime environment, stopping the optimization before it breaks the driver.

### 3. Integration and Vendor Quirks

Clean code assumes the outside world behaves reasonably. Production code knows it does not:

```csharp
// THIRD-PARTY GATEWAY QUIRK:
// The payment clearinghouse gateway returns HTTP 200 OK even on terminal card declines,
// placing the decline code inside an unescaped XML payload within the body.
// DO NOT refactor this to standard HTTP status checks (e.g., response.IsSuccessStatusCode).
if (response.StatusCode == HttpStatusCode.OK && responseBody.Contains("<DeclineCode>"))
{
    return ProcessDecline(responseBody);
}
```

To any automated refactoring pass, checking for an error string inside an `HTTP 200 OK` handler looks like legacy incompetence. An agent cleaning up API calls will instinctively modernize it to `if (response.IsSuccessStatusCode)`, accidentally treating failed credit card charges as successful orders.

### 4. Concurrency and Socket Boundaries

```csharp
// NETWORK CONCURRENCY GUARD:
// Do not replace this sequential loop with Task.WhenAll.
// The downstream TLS endpoint drops connections if concurrent handshakes exceed 16.
// Throughput is bound by remote socket limits, not local CPU or async scheduling.
foreach (var endpoint in clusterEndpoints)
{
    await EstablishSecureSessionAsync(endpoint, cancellationToken);
}
```

```csharp
// DEDUPLICATION GUARD:
// This check looks redundant with the database unique constraint, but the upstream
// webhook provider occasionally sends duplicate events across separate connections
// within 5 milliseconds. Keep this in-memory check to prevent duplicate email alerts.
if (!idempotencyCache.TryAdd(incomingEvent.Id, true))
{
    return EventProcessingResult.AlreadyProcessed;
}
```

In every one of these cases, the code looks suboptimal or redundant when viewed in isolation. The negative comment explains why the obvious refactoring is disastrous.

---

## The Documentation Hierarchy

Comments do not replace system specifications or architectural decision records (ADRs). Rather, system knowledge stratifies into distinct layers, each serving a different operational scope:

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. SYSTEM SPECIFICATIONS                                    │
│    Functional requirements, business models, user workflows.│
├─────────────────────────────────────────────────────────────┤
│ 2. ARCHITECTURAL DECISION RECORDS (ADRs)                    │
│    System-wide design decisions, performance budgets, tech   │
│    stack trade-offs, network topology.                      │
├─────────────────────────────────────────────────────────────┤
│ 3. INLINE INTENT & CONSTRAINT COMMENTS                      │
│    Local intent, negative knowledge, non-obvious boundaries,│
│    hardware/vendor quirks, operational edge cases.          │
├─────────────────────────────────────────────────────────────┤
│ 4. SOURCE CODE                                              │
│    Executable implementation, AST, types, control flow.     │
└─────────────────────────────────────────────────────────────┘
```

During initial feature development, an agent or engineer might have the full Tier 1 Specification loaded in its working context.

Two years later, an agent working on an isolated bug fix in an auxiliary module will never see that specification. It will almost certainly not pull down Tier 2 ADRs unless explicitly directed to do so. 

Tier 3 comments, however, travel with the source code. They act as local, indestructible semantic anchors directly adjacent to Tier 4 execution logic.

---

## Agents Producing Context for Future Agents

This dynamics introduces an important operational loop: when an agent implements a feature today, it already has the entire specification loaded into its context.

Instead of translating that specification solely into executable code, the agent can be instructed to explicitly leave behind the semantic residue that future agents will need.

```text
Task Specification & Requirements
               │
               ▼
       Developing Agent
      ┌────────┴────────┐
      ▼                 ▼
Executable Code   Durable Context Comments
(Syntax & Logic)  (Constraints, negative knowledge,
                   and non-obvious invariants)
                        │
                        ▼
             Future Agent (Two Years Later)
             Only loads a single file slice, but
             inherits the durable context immediately.
```

A practical system prompt instruction for development harnesses:

> *"Whenever your implementation encodes a non-obvious business rule, operational constraint, physical limit, or vendor workaround that cannot be inferred purely from the types and names, preserve that information as a concise comment directly above the relevant code. Include negative constraints: explain what obvious-looking refactorings would break the system."*

This turns documentation into an active, distributed process rather than a neglected post-hoc chore.

---

## Pre-Emptive Knowledge Rehydration: Mining Git History

In brownfield codebases, historical rationale has already escaped into commit logs and pull requests. You do not need engineers to spend weeks manually writing these comments.

You can use an offline script to systematically rehydrate the codebase:
1. Search your repository's `git log` for commits containing keywords like `hotfix`, `workaround`, `vendor bug`, `race condition`, `revert`, or `do not touch`.
2. Direct an agent to analyze the commit diff, commit message, and associated PR conversation.
3. Have the model synthesize a 2-to-3 line comment capturing the invariant, the reason for the workaround, and what must not be changed.
4. Place that comment directly above the impacted code and merge it back into the branch.

This lifts critical domain knowledge out of git archaeology and places it directly into the local execution path where future agents will automatically consume it.

---

## Redefining Low-Level and Architectural Documentation

As AI systems handle more day-to-day software development, our definition of what documentation should accomplish changes:

1. **The Death of Implementation Comments:**
   Comments explaining *how* a function works or walking through its control flow line-by-line are pure noise. Agents do not need them, and human developers are distracted by them. Similarly, broad structural documentation that merely describes component relationships or data flows can be reconstructed on the fly by an agent parsing the repository.
   
2. **From Structural Documentation to Decision Records:**
   Documentation shifts entirely from *descriptive* (what exists) to *decisional* (why it was built this way). Architecture documentation remains valuable primarily as **guardrails and trade-offs**—defining performance budgets, consistency guarantees, security boundaries, and invariants that prevent agents from performing broad refactorings that compromise system-level requirements.

3. **Context Engineering via Comments:**
   Comments are no longer just an aid for human eyes. They are a fundamental tool of context engineering for autonomous agents. They ensure that an isolated slice of code, separated from the team that built it and the documents that specified it, still carries the operational knowledge required to maintain it safely.

---

## Related Notes

- **[[Why Business Logic Is the Hardest Part of Agentic Coding]]**: Why domain nuances and commercial realities resist clean structural abstraction.
- **[[Optimizing Software Engineering and Code for Agents]]**: Designing codebases for machine legibility, explicit interfaces, and isolated context.
- **[[Designing Software for AI Agents]]**: Repository patterns that allow agents to reason across code boundaries without context exhaustion.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Maintaining active Markdown context specifications alongside inline comments.
- **[[Testing in the Model, Agent, LLM Era]]**: Using deterministic test harnesses to validate the business constraints that comments document.
- **[[LLM Agents and Institutional Memory]]**: Bridging the gap between transient corporate knowledge and permanent code artifacts.
