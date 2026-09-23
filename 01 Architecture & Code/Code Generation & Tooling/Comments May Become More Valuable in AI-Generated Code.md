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

The traditional rule for comments is often expressed as:

> Good code should explain what it does. Comments should explain why.

This distinction may become even more important in software increasingly written and modified by AI agents.

An agent can usually reconstruct the mechanics of code very well. It does not need comments that merely repeat the implementation.

For example:

```csharp
// Charge 50% if booking starts in less than 3 days.
if (booking.StartDate < DateTime.UtcNow.AddDays(3))
{
    cancellationFee = booking.TotalPrice * 0.5m;
}
```

The comment adds almost no information.

A much more valuable comment would be:

```csharp
// Cancellations within 72 hours are charged 50% because the supplier
// no longer refunds us after this point.
// Do not replace this with the standard hotel cancellation policy.
```

The code explains the mechanism.

The comment preserves information that cannot easily be reconstructed from the implementation:

- why the rule exists;
    
- where it comes from;
    
- whether it is intentional;
    
- which business constraint it represents;
    
- what apparently reasonable changes would be incorrect.
    

## Code Is Self-Documenting Syntactically, Not Semantically

Well-written code can communicate structure and behavior.

For example:

```csharp
ApplyNonRefundableSupplierCancellationFee();
```

This is much better than an obscure method name, but it still does not explain:

- why this supplier is treated differently;
    
- whether the behavior comes from a contract;
    
- whether it is temporary;
    
- which products it applies to;
    
- whether another similar rule should be reused;
    
- what assumptions the implementation depends on.
    

Historically, much of this knowledge lived outside the code:

- in developers' heads;
    
- Jira tickets;
    
- Slack conversations;
    
- meetings;
    
- old specifications;
    
- architecture documents.
    

Future agents modifying the code may never see any of those sources.

A comment located next to the implementation has a major advantage:

> It is very likely to enter the agent's context whenever the relevant code enters the context.

## Comments Can Act as Local Context Retrieval

Suppose an agent receives a task:

> Add partial cancellation support.

It retrieves the classes responsible for cancellations.

Any comments located inside those classes are naturally retrieved together with the implementation.

This makes comments a kind of very small, highly localized knowledge base.

They do not require the agent to know:

- that an ADR exists;
    
- which specification describes the rule;
    
- which ticket introduced it;
    
- what search query to use;
    
- which meeting contained the relevant discussion.
    

The knowledge is physically attached to the place where it matters.

This may make carefully written comments one of the most reliable forms of context delivery for future coding agents.

## Why Git Blame and Issue Trackers Cannot Replace Inline Comments

A common pushback from clean-code purists is: *"If someone wants to know why a line exists, they can check `git blame` or the original commit."*

While that works for a human engineer during a deep investigation, agents routinely fail to use source control history effectively during automated tasks:

1. **Lack of Proactive Doubt:** LLMs generate code based on statistical pattern matching. When an agent sees an unusual condition or a seemingly redundant check, it does not instinctively wonder whether an obscure production incident necessitated it. It assumes the check is inefficient dead code, refactors it away, and moves on with high confidence.
2. **Context and Latency Overhead:** Instructing an agent to run `git log -S`, inspect commit diffs, and query issue trackers for every line of code it touches explodes tool roundtrips, token consumption, and execution latency.
3. **History Decay:** Codebases experience churn. Bulk formatting passes, linter updates, namespace renames, and prior automated refactorings easily overwrite `git blame` annotations with meaningless commit messages.
4. **Preventative vs. Post-Mortem Value:** `git blame` is an autopsy tool used after a defect surfaces. An inline comment is a preventative guardrail positioned directly in the prompt before the model generates the wrong diff.

## Documentation Layers Still Have Different Roles

Comments should not replace specifications or architectural documentation.

Instead, the different layers can complement each other:

```text
Specification
    ↓
describes desired behavior and requirements

Architecture docs / ADRs
    ↓
describe system-wide decisions and trade-offs

Business comments
    ↓
preserve local intent, constraints and exceptions

Code
    ↓
contains the executable implementation
```

During the initial implementation, an agent may have access to the complete specification.

Several years later, another agent may receive only a small portion of the repository while working on an unrelated change.

The original specification may not enter its context at all.

A nearby comment probably will.

## Negative Knowledge May Be Especially Valuable

Some of the most useful comments may describe what must **not** be done.

For example:

```csharp
// Do not calculate this from Payment.Amount.
// Legacy bookings may already contain the agency margin there.
```

Or:

```csharp
// This check looks redundant, but some suppliers occasionally send
// the same reservation with different external IDs.
```

Or:

```csharp
// Intentionally executed before availability validation.
// Sales requires the original quoted price to remain available
// even when availability subsequently fails.
```

This is negative knowledge:

> A seemingly obvious implementation or refactoring is incorrect.

Such knowledge may be particularly important for agents.

An agent performing a local refactoring may see:

```text
strange condition
→ appears redundant
→ simplify it
```

A good comment changes the reasoning to:

```text
strange condition
→ explicitly intentional
→ represents a business constraint
→ preserve unless the requirement itself changes
```

### Driver and Protocol Limits

Consider an ingestion batch size:

```csharp
// WIRE PROTOCOL LIMIT:
// The underlying Postgres driver allows a maximum of 65,535 query parameters.
// With 240 columns per telemetry record, any batch larger than 273 rows triggers 
// a silent driver parameter buffer overflow. We cap at 250 for safety margin.
// DO NOT increase this batch size without changing the driver protocol.
public const int TelemetryBatchSize = 250;
```

An agent asked to optimize throughput will look at a batch size of 250 and bump it to 5,000 to minimize roundtrips. The comment explicitly states the mechanical ceiling of the runtime environment, stopping the optimization before it breaks the driver.

### Integration and Gateway Quirks

Clean code assumes external services behave reasonably. Production systems know they do not:

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

To an automated refactoring pass, checking for an error string inside an `HTTP 200 OK` handler looks like legacy sloppiness. An agent cleaning up API calls will instinctively modernize it to `if (response.IsSuccessStatusCode)`, accidentally treating failed credit card charges as successful orders.

### Concurrency and Socket Boundaries

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

In each case, the implementation looks suboptimal or redundant when viewed in isolation. The negative comment explains why the obvious refactoring causes an immediate outage.

## Clean Code Does Not Eliminate Business Context

The argument that "good code should not require comments" is reasonable when applied to comments describing mechanics.

Comments such as:

```csharp
// Iterate through users.
```

are usually unnecessary.

But business rationale cannot always be encoded through better naming or cleaner abstractions.

A method called:

```csharp
IsEligibleForLegacyCancellationCompensation()
```

still does not explain why legacy cancellation compensation exists.

The useful distinction may therefore become:

> Minimize comments explaining implementation.

> Maximize comments preserving intent, business meaning, invariants, constraints, exceptions and non-obvious decisions.

## Agents Can Produce Their Own Future Context

There is another important consequence.

When an agent implements a feature, it already has the specification in its context.

Instead of converting that specification only into executable code, it can also preserve the parts of the specification that future developers or agents will need.

A useful instruction could be:

> Whenever the implementation encodes a non-obvious business rule, invariant, exception or constraint that cannot be reconstructed from the code itself, preserve that information as a concise comment near the relevant code.

The process then becomes:

```text
task specification
       │
       ▼
     agent
    /     \
   ▼       ▼
code     durable intent
         comments
```

The code is the executable result of the specification.

The comments preserve selected parts of its semantics.

## Pre-Emptive Knowledge Rehydration: Mining Git History

In brownfield codebases, historical rationale has already escaped into commit logs and pull requests. You do not need engineers to spend weeks manually writing these comments.

You can use an offline script to systematically rehydrate the codebase:

1. Search your repository's `git log` for commits containing keywords like `hotfix`, `workaround`, `vendor bug`, `race condition`, `revert`, or `do not touch`.
2. Direct an agent to analyze the commit diff, commit message, and associated PR conversation.
3. Have the model synthesize a concise 2-to-3 line comment capturing the invariant, the reason for the workaround, and what must not be changed.
4. Place that comment directly above the impacted code and merge it back into the branch.

This lifts critical domain knowledge out of git archaeology and places it directly into the local execution path where future agents will automatically consume it.

## Comments May Become Part of Designing Code for Agents

Traditionally, comments were primarily written for human maintainers.

In agent-heavy development, another audience appears:

> the future model receiving a limited slice of the repository as context.

This changes how comments can be evaluated.

The question is no longer only:

> Will another developer understand this?

It also becomes:

> If an agent sees only this file two years from now, what important information could it incorrectly infer?

Comments can protect against those incorrect inferences.

This suggests that codebases optimized for agentic development may intentionally preserve more business context next to the implementation.

Not more comments in general.

Better comments.

Especially comments explaining:

- why a rule exists;
    
- which business concept it represents;
    
- which invariant must remain true;
    
- why an unusual implementation is intentional;
    
- which tempting simplification would be wrong;
    
- which external constraint shaped the implementation;
    
- which assumptions future changes must preserve.
    

In this sense, comments may become part of **context engineering for future coding agents** rather than merely an aid to human readability.

## Redefining Low-Level and Architectural Documentation

The ability of LLMs to analyze code and explain its mechanics on demand accelerates two major shifts:

1. **Obsolescence of Low-Level Comments and Descriptive Docs:**
   - Comments explaining *how* a function works or what steps it takes are now pure noise.
   - Broad architectural documentation that merely describes component relationships or data flows is easily reconstructed on the fly by an agent analyzing the codebase.

2. **From Structural Documentation to Decision Records:**
   - Documentation shifts almost entirely from *descriptive* (what exists) to *decisional* (why it was built this way).
   - High-level architecture docs remain valuable only as **guardrails and trade-offs** (e.g., ADRs, system constraints, performance budgets) that prevent agents from making architectural refactorings that break unstated non-functional requirements.

3. **Context Engineering via Comments:**
   - Comments are no longer just an aid for human eyes. They are a fundamental tool of context engineering for autonomous agents (see [[Designing Software for AI Agents]] and [[The Living Engineering Chronicle and Context Compaction]]).
   - They ensure that an isolated slice of code, separated from the team that built it and the documents that specified it, still carries the operational knowledge required to maintain it safely.

## Related Notes

- [[Designing Software for AI Agents]] — Structuring software and vertical slices so agents can infer boundaries and intent.
- [[Negative Knowledge and Explicit Architectural Dissents]] — Documenting non-obvious invariants and rejected alternatives.
- [[The Living Engineering Chronicle and Context Compaction]] — Compacting long-term engineering intent into active agent context.
