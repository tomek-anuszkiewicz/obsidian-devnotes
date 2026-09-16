# Consolidated Restored Reference Notes

> Reference knowledge base for Gemini Gem: Lean, fact-dense, active-voice engineering notes.

================================================================================
FILE: Agentic Review Can Enforce Rules That Were Previously Too Hard to Formalize.md
================================================================================

### Executable Architecture Policies

Traditional static analysis handles deterministic invariants:

```text
Domain must not reference Infrastructure.
Every public endpoint must require authorization.
Result must never be negative.
All handlers must implement a particular interface.
```

Deterministic checkers enforce syntax, AST patterns, and types well.
However, critical architectural rules rely on context and semantic intent:
- Avoid premature abstractions.
- Keep controllers thin without redundant mapping layers.
- Prevent domain logic leaks into infrastructure helpers.
- Restrict cross-module communication to public contracts.

Encoding these semantic rules into linters costs too much time.
Reviewers traditionally enforced these standards from memory.

### Agent Runtime for Natural-Language Rules

Feed architecture documentation directly into the review agent context:

```text
docs/architecture/principles.md
docs/domain/invariants.md
docs/security/guidelines.md
ADRs/
```

Prompt the agent to inspect incoming pull requests:
1. Pinpoint the violating lines.
2. Cite the breached policy or ADR.
3. Explain the architectural conflict.
4. Suppress output when confidence falls below threshold.

### Three-Tier Quality Stack

```text
Human Review       -> Strategic architectural trade-offs
Agentic Review     -> Semantic policy and intent checks
Deterministic CI   -> Types, linters, unit tests, analyzers
```

Review agents eliminate manual auditing fatigue.
They audit 100-file pull requests without skimming.
They evaluate rarely violated rules on every commit.

### Deterministic Tests vs. Semantic Inspection

Never replace fast deterministic checks with LLM prompts.
Deterministic checks remain authoritative, cheap, and reproducible:

```csharp
Assert.True(result >= 0);
```

Reserve agents for rules where formalization costs too much.
Use agents to catch semantic bypasses of formal rules.

#### Case 1: Invariant Circumvention
A price invariant states that values cannot fall below zero.
A developer clamps negative inputs to zero.
The deterministic unit test passes:

```csharp
// Unit test passes
Assert.True(price >= 0);
```

The agent flags the bug: Clamping silently masks invalid domain state.

#### Case 2: Structural Decoupling Evasion
An architecture test forbids importing Module B from Module A.
The test passes because Module A copies Module B internal schemas directly.
The agent flags semantic coupling despite zero direct project references.

### Bidirectional Feedback Loop

#### 1. Promote Agent Findings to Deterministic Analyzers
Track repeated agent detections.
If an agent repeatedly catches infrastructure imports in domain code, write an AST analyzer.
Automate the check permanently.
Free the agent context for novel patterns:

```text
Informal Principle -> Agent Audits PRs -> Pattern Stabilizes -> Static Analyzer Rule Added
```

#### 2. Explain Deterministic Failures
Use agents to explain static analysis failures.
A linter flags: `Namespace X references Namespace Y`.
The agent provides context:
`Namespace Y contains raw database entities. Use CustomerContract instead.`

### Ephemeral Investigative Tests

Agents can generate throwaway tests to validate hypotheses during review.
An agent suspects a race condition in a cache implementation.
It writes a temporary test and executes it:

```text
Agent Generates Test -> Reproduces Concurrency Bug -> Promotes to Regression Suite
```

If the race reproduces, promote the test to the regression suite.
Otherwise, discard the scratchpad test.

### Continuous Architecture Checklist

Run these semantic checks on every pull request:
- Does this diff introduce a one-off generic framework?
- Does domain logic leak into infrastructure adapters?
- Does this change contradict recorded ADR decisions?
- Does the new abstraction justify its operational cost?


================================================================================
FILE: Comments May Become More Valuable in AI-Generated Code.md
================================================================================

## Semantic Comments vs. Syntax Echoes

LLMs parse syntax without help.
They fail when inferring unstated business rules.
Do not explain code mechanics in comments.
Record intent, external constraints, and invariants directly in source files.

```csharp
// BAD: Repeats the code.
// Charge 50% if booking starts in less than 3 days.
if (booking.StartDate < DateTime.UtcNow.AddDays(3)) {
    cancellationFee = booking.TotalPrice * 0.5m;
}

// GOOD: Preserves business constraints.
// Suppliers stop refunds 72 hours before booking starts.
// Do not replace this with the standard hotel cancellation policy.
if (booking.StartDate < DateTime.UtcNow.AddDays(3)) {
    cancellationFee = booking.TotalPrice * 0.5m;
}
```

## Anchor Context Next to Code

Agents fetch files locally during edits.
They miss external tickets, chat threads, and design docs.
Comments placed next to code enter the context window automatically.
Clean method names show what runs, not why contracts exist:

```csharp
ApplyNonRefundableSupplierCancellationFee();
```

Method names omit contract sources, date rules, and vendor quirks.
Use comments to supply these hidden constraints.

Separate system knowledge across distinct tiers:
- Specs: Define product goals.
- ADRs: Track global trade-offs.
- Source comments: Anchor local invariants and exceptions.
- Code: Runs the logic.

Coding models refactor single files without reading parent specs.
Source comments preserve business rules when specs drop out of context.

## Negative Knowledge and Guard Comments

Models often refactor defensive code into generic patterns.
Negative knowledge records forbidden changes and deliberate anomalies.
Use guard comments to stop broken edits:

```csharp
// Do not calculate this from Payment.Amount.
// Legacy bookings store agency margins there.
```

```csharp
// Keep this check.
// Suppliers occasionally send duplicate records with distinct external IDs.
```

```csharp
// Run this before checking availability.
// Sales insists that quoted prices persist when inventory calls fail.
```

Without comments, models apply naive logic:
```text
strange code -> looks redundant -> delete
```

Negative knowledge updates the prompt context:
```text
strange code -> deliberate rule -> keep
```

## Instruct Agents to Preserve Constraints

Direct coding agents to store downstream context when building features.
Use this prompt rule in agent pipelines:

```text
Preserve non-obvious business rules as concise comments next to the code.
```

```text
Spec -> Agent -> Executable Code + Invariant Comments
```

## Invariant Checklist

Write comments to prompt future models.
Audit comments with one test:
What will an agent break if it reads only this file?

Always record:
- Upstream business logic driving the rule.
- Non-obvious domain invariants.
- Deliberate workarounds for external vendor bugs.
- Tempting cleanups that break system guarantees.


================================================================================
FILE: Designing APIs for LLM-Generated Integration Code.md
================================================================================

## Core Integration Flow

Coding agents must not construct raw HTTP requests. The agent discovers capabilities, selects typed clients, and generates calling code.

```text
Requirement -> Discover Client -> Select Method -> Generate Code -> Typed Client -> API
```

## Business Intent Over Generic CRUD

External APIs must expose stable domain capabilities. Never expose internal database schemas or internal mechanics. Express intent directly in endpoint names. Prefer `cancelInvoice` over `updateEntity`. 

For actual deletions, standard CRUD works:
```http
DELETE /drafts/{id}
```

For state transitions, use explicit action routes:
```http
POST /invoices/{id}/cancel
```

## OpenAPI Semantic Contracts

OpenAPI specs define runtime semantics, not just routes.

Weak spec:
```yaml
/users/{id}/sessions:
  delete:
    operationId: deleteSessions
```

Strong spec:
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

Add negative constraints to descriptions:
```yaml
description: |
  Permanently deletes a draft invoice.

  Only draft invoices can be deleted.

  Do not use this operation for issued invoices.
  Issued invoices must be cancelled using cancelInvoice.
```
Negative constraints stop agents from picking wrong endpoints.

## Strongly Typed Clients

Generate typed clients with Kiota, NSwag, or OpenAPI Generator. Typed clients eliminate route typos and JSON parse bugs.

Do not let agents generate manual HTTP requests:
```csharp
await httpClient.DeleteAsync(
    $"/users/{userId}/sessions");
```

Direct agents to call typed client methods:
```csharp
await identityClient.RevokeUserSessionsAsync(
    userId,
    cancellationToken);
```

## Preserve Documentation in Generated SDKs

Configure generators to emit OpenAPI descriptions as client docstrings. Docstrings put domain rules directly into the agent context window.

```csharp
public interface IInvoicesClient {
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

## Interface Discoverability

Name client interfaces by business domain, not infrastructure.
* Prefer: `IIdentityClient`, `IOrdersClient`, `IBillingClient`, `IInvoicesClient`
* Avoid: `IServiceAClient`, `IBackendClient`, `IApiV2Client`

Domain names let agents locate tools through repository search.

## Repository Guidance (`AGENTS.md`)

Add integration rules to `AGENTS.md`:
```text
When integrating with another service:
1. Search generated clients by business domain.
2. Inspect method names and docstrings.
3. Call generated clients instead of raw HTTP clients.
4. Read the OpenAPI schema only to resolve parameter ambiguity.
5. Never construct raw URLs manually.
```

## Semantic Errors

Return machine-readable errors with recovery hints. Avoid opaque numeric codes:
```json
{
  "errorCode": 3817
}
```

Provide semantic error payloads with recovery paths:
```json
{
  "code": "invoice_already_issued",
  "message": "Issued invoices cannot be deleted.",
  "suggestedOperation": "cancelInvoice"
}
```
Agents use `suggestedOperation` to trigger fallback calls automatically.

## Beyond REST

Apply these rules across all integration patterns.

### GraphQL
Write explicit mutation names and docstrings:
```graphql
"""
Cancels an issued invoice while preserving it for audit.
Do not use for draft invoices.
"""
cancelInvoice(id: ID!): Invoice!
```

### Messaging
Document message contracts with AsyncAPI. Distinguish commands from events by name:
* Command: `RevokeUserSessions`
* Event: `UserSessionsRevoked`

Commands execute tasks; events report state changes. Keep transport protocols below a typed, semantically named client interface.


================================================================================
FILE: Designing Software Architecture with LLM Assistance.md
================================================================================

# LLM-Assisted Systems Design

LLMs generate plausible architectures but miss undocumented boundaries.
Models fill unstated requirements with typical defaults.
They implicitly assume eventual consistency, idempotent endpoints, or linear states.
These defaults often fail in production systems.
Never accept fluent output as proof of technical accuracy.
Audit core assumptions before picking technologies or writing code.

---

## Deriving Constraints from Invariants

Technical choices stem from business invariants.
Always trace choices through this derivation chain:

```text
Business Rule -> System Invariant -> Architecture Constraint -> Technology Choice
```

Examples:
- **Rule**: Never double-charge a customer.
  - **Invariant**: Operations require duplicate execution prevention.
  - **Constraint**: Enforce idempotency keys with unique database constraints.
- **Rule**: Deliver immediate booking confirmations.
  - **Invariant**: The user path cannot rely on asynchronous convergence.
  - **Constraint**: Use synchronous ACID transactions over eventual consistency.
- **Rule**: Audit decision inputs five years later.
  - **Invariant**: Preserve point-in-time state transitions and inputs.
  - **Constraint**: Implement an immutable, append-only event log.

Challenge arbitrary mandates like "must use PostgreSQL".
Extract the underlying driver: license limits, reporting tools, DBA skills, or legacy habit.

---

## Constraint Taxonomy

Classify constraints into three operational groups:

- **Explicit**: Exists in ADRs, tickets, specifications, and schemas. Models parse these well.
- **Discoverable**: Exists in codebases, configs, migrations, and telemetry. Extract these with targeted prompts.
- **Hidden**: Exists in tribal memory, manual runbooks, and informal agreements. Humans must supply this context.

---

## Discovery-First Architecture Workflow

Do not jump directly to stack selection.

Flawed pipeline:
```text
Problem -> Tech Stack -> Code
```

Pragmatic pipeline:
```text
Problem -> Facts -> Gaps -> Invariants -> Alternatives -> Invalidation -> Stack Choice
```

Structure context into five explicit categories:
1. **Confirmed Fact**: Verified property backed by code, tests, or production metrics.
2. **Inference**: Logical deduction derived directly from confirmed facts.
3. **Assumption**: Temporary placeholder filling a context gap.
4. **Unknown**: Unresolved variable requiring investigation.
5. **Common Practice**: Industry default that might fail your specific workload.

---

## Bias and Context Anchoring

Models suffer from contextual anchoring.
Mentioning a tool primes the model to recommend it.
The model designs around mentioned tools, even when unsuited for the workload.
Reset context windows when evaluating critical architectural forks.
Instruct the model to solve the problem without previously mentioned technologies.

Models also favor patterns frequent in public training data.
Easy generation does not indicate correct architecture.
Evaluate proposals against this matrix:

| Dimension | Evaluation Focus |
| :--- | :--- |
| **Problem Fit** | Satisfies verified business invariants |
| **Grounding** | Draws from project telemetry or code |
| **Operational Risk** | Quantifies failure modes, rollouts, and rollback costs |
| **Availability Bias** | Over-indexes on boilerplate code and documentation |

---

## Strategic Solution Exploration

Reject homogeneous technology options.
Force alternatives across distinct strategic archetypes:
- **Simplest viable**: Minimum moving parts.
- **Existing stack**: Zero new operational dependencies.
- **Reversible experiment**: High-leverage feature flag or adapter pattern.
- **Non-technical change**: Policy shift or dropped requirement.
- **Long-term architecture**: Eventual target state under sustained scale.

Require explicit failure modes, operational burdens, and rollback mechanics for every option.

---

## Dual Operating Modes

Run architecture work in two separate modes:

### Exploration Mode
- Prioritize discovery speed.
- Build quick spikes.
- Test unfamiliar libraries.
- Accept labeled assumptions.
- Write throwaway prototypes.

### Commitment Mode
- Prioritize correctness and reversibility.
- Verify edge cases.
- Audit failure domains.
- Write migration scripts.
- Eliminate hidden assumptions.
- Require human sign-off.

Never promote an exploration prototype directly to production.

---

## Review Roles and System Dimensions

Prompt the model through distinct operational personas:
- **Domain Analyst**: Extract business invariants, actors, state transitions, and edge cases.
- **Architect**: Map tradeoffs, state boundaries, component coupling, and blast radiuses.
- **Skeptic**: Find broken assumptions, scale limits, poison messages, and race conditions.
- **Operator**: Review deployment mechanics, zero-downtime rollouts, observability, and disaster recovery.
- **Security Lead**: Audit trust boundaries, auth models, data retention, and compliance limits.

Audit every proposal across these technical vectors:
- **State**: Concurrency, idempotency keys, ordering guarantees, transactional boundaries.
- **Failure**: Partial outages, cascading failures, backoff retries, dead-letter queues.
- **Operations**: Dual-write avoidance, backward schema compatibility, telemetry, rollback cost.

---

## Core Architecture Prompts

### Discovery Prompt
```text
Analyze this system problem. Do not propose solutions yet.

Separate the input into:
- Confirmed facts
- Inferences derived from facts
- Working assumptions
- Missing information
- Generic defaults that might fail here

Highlight business invariants, concurrency models, transactional boundaries, and failure states.
List questions whose answers could reverse the architectural direction.
Rank questions by impact.
Stop here.
```

### Alternatives Prompt
```text
Generate distinct architectural options using only confirmed facts and explicit assumptions.

Include these archetypes:
- Simplest viable design
- Zero-new-infrastructure design (existing stack only)
- Reversible experiment
- Non-technical or process-level fix
- Long-term target architecture

For each option detail:
1. Required system properties
2. Operational cost and blast radius
3. Failure modes
4. Migration and rollback strategy
5. Information that invalidates this choice

Do not declare any option universally superior.
```

### Adversarial Invalidation Prompt
```text
Assume this proposed solution fails in production.

Identify:
- Unstated assumptions
- Latent race conditions and concurrency failures
- Partial outage behaviors
- Deployment or backward-compatibility traps
- Production costs hidden during prototyping

Answer:
1. What unverified condition breaks this system?
2. What findings reverse this decision?
3. What benchmarks or tests prove this design?


================================================================================
FILE: Developing Features with AI Coding Agents.md
================================================================================

## Agent Feature Workflow

```text
Analyze repo -> Write spec -> Build decision tables -> Write acceptance tests -> Human audit -> Build vertical slice -> Arch review -> Full build -> Skeptical review
```

### 1. Repository Analysis
Point the agent at the codebase before writing code.
Map data models, integration boundaries, transactions, and hidden constraints.
Keep code read-only during this phase.

### 2. Behavioral Specification
Define business rules, domain terms, negative paths, and out-of-scope boundaries.
Build decision tables for branching logic.
Models invent requirements when branch priorities stay ambiguous.

### 3. Test-First Setup
Write acceptance and contract tests before writing feature code.
Run tests to confirm they fail.
Failing tests prove the suite catches missing behavior.

### 4. Audit Test Semantics
Review test meaning, not syntax.
Check whether the agent hallucinated unstated requirements.
Ensure negative cases run.
Verify the tests reject accidental legacy behavior.

### 5. Freeze Test Contracts
Lock approved acceptance tests in git.
Block the agent from editing these tests while writing code.
Allow the agent to add internal unit tests only.
Review all changes to acceptance files manually.

### 6. Vertical Slice
Build one complete path from ingress to storage.
Validate architectural boundaries on this single slice.
Do not scaffold multiple files before this slice passes review.

### 7. Stop Circular Logic
Tests show examples. They do not capture intent.
Never let the agent write both tests and code unsupervised.
Self-authored tests confirm the agent's own misconceptions.
Anchor tests to explicit decision tables.

### Execution Checklist
- Inspect the repo before editing.
- Write explicit specs with decision tables.
- Freeze failing acceptance tests.
- Build one end-to-end slice first.
- Separate mechanical refactors from business changes.
- Review final output with a skeptical peer.


================================================================================
FILE: Hidden Abstractions May Become More Expensive in Agent-Maintained Code.md
================================================================================

Syntactic brevity often hides massive execution pipelines. 
Consider this common MediatR call:

```csharp
public Task<Response> GetOrder(GetOrderRequest request) => mediator.Send(request);
```

The call site hides the true execution flow:

```text
Auth -> Validation -> Logging -> Transaction -> EF Interceptors -> Handler -> SQL
```

Local code stays small. Semantic complexity explodes.
Coding agents struggle with this hidden execution context.

### Non-Local Semantics and Ambient State

Agents cannot infer dependencies outside the local context window.
Consider an HTTP call:

```csharp
await httpClient.SendAsync(request);
```

Global handlers inject headers, auth, telemetry, and retries silently.
Entity Framework query filters also inject hidden SQL clauses:

```csharp
context.Orders.ToListAsync();
// Injects: WHERE TenantId = @currentTenant AND IsDeleted = 0
```

Do not hide business dependencies in ambient state.
Avoid `AsyncLocal`, `HttpContext.Items`, or implicit thread-local state.
Pass required context explicitly.

### Dynamic DI Breaks Static Analysis

Dynamic DI and runtime factories break static analysis tools.

```csharp
services.AddScoped<IPriceCalculator>(sp => {
    var context = sp.GetRequiredService<OperationContext>();
    return context.Channel switch
    {
        Channel.Web => new WebPriceCalculator(),
        Channel.Api => new ApiPriceCalculator(),
        _ => new DefaultPriceCalculator()
    };
});
```

The call site obscures the concrete implementation:

```csharp
priceCalculator.Calculate(order);
```

Keyed services, decorators, and assembly scanning destroy call-site discoverability.
Agents fail to identify the active execution path.
Interceptors also hide critical business semantics:

```csharp
repository.Save(order); // Silently runs auth, validation, and audit logging
```

Keep business-critical operations visible at the call site.

### The Shift in DRY Economics

Traditional DRY minimizes typing and repeated lines.
Agents generate and maintain repeated code cheaply.
Prioritize semantic locality over extreme deduplication.
Allow repeated code to keep pipelines explicit.

### Explicit Execution Pipelines

Expose the execution pipeline directly in the handler:

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

This code exposes the full execution graph.
Agents parse this pipeline without inspecting external framework configurations.

### Mechanics vs. Business Semantics

Let frameworks hide low-level mechanics.
Keep domain semantics explicit.

Safe to hide (Mechanics):
- JSON parsing, serializing, TCP handling
- Low-level telemetry, correlation IDs, compression

Keep explicit (Semantics):
- Authorization and tenant filtering
- Business validation and retry policies
- Transaction bounds and idempotency keys
- Cache invalidation and feature flags

### Named Semantics Over Silent Policies

Do not hide retries inside `HttpClient`.
Expose the retry policy at the call site:

```csharp
await request
    .Retry(RetryPolicies.ExternalRead)
    .Execute();
```

The call site declares *what* policy applies.
Central configuration defines *how* the policy executes.
Agents immediately recognize that the call may run multiple times.
They then handle idempotency and side effects correctly.

### Ubiquitous Vocabulary

Encode domain conclusions directly into code.
Avoid technical sentinels.

Bad:
```csharp
if (payment != null) // Implicitly means unpaid
if (amount == 0)     // Implicitly means free
if (status == 2)     // Implicitly means active
```

Good:
```csharp
if (payment.IsUnpaid)
if (price.IsFree)
if (subscription.IsActive)
```

Align naming across schemas, API contracts, tests, and code:
- Spec: `paymentStatus: "unpaid"`
- DB: `payment_status = "unpaid"`
- Code: `PaymentStatus.Unpaid`
- Test: `ShouldRetryUnpaidPayment()`

Consistent terminology improves agent retrieval and code reasoning.

### Semantic Locality Spectrum

Measure code quality by semantic locality:

- **High Locality:** 
```csharp
CalculatePrice(order, customer, pricingRules);
```
- **Medium Locality:** 
```csharp
priceCalculator.Calculate(order);
```
- **Low Locality:** Ambient DI resolves implementations via runtime tenant and flags.

Syntactic brevity no longer equals architectural simplicity.
Prioritize explicit, composable, and mechanically discoverable pipelines.

