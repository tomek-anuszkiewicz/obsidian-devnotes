---
title: "Designing Explicit Operations for Agent-Maintained Code"
tags:
  - software-architecture
  - ai-agents
  - code-maintainability
  - modularity
  - domain-driven-design
aliases:
  - "Explicit Execution Pipelines for Coding Agents"
  - "Visible Policies and Business Vocabulary in Code"
  - "Inspectable Abstractions for Agent Maintenance"
---

An operation that charges a payment needs to reveal whether retries, authorization, a transaction, and external side effects participate. Repeating the implementation of each mechanism would create its own maintenance cost. The useful design question is how to keep the mechanism reusable while making its participation and meaning visible.

An explicit pipeline can name the steps. A call site can name the selected policy while its implementation remains centralized. A framework can expose the resolved behavior of an operation. Domain vocabulary can keep the same business concept recognizable across code, contracts, tests, and data.

These approaches still use abstractions. They reduce the unrelated code an engineer or agent must inspect before understanding an operation. [[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]] explains the corresponding failure modes and cost. The sections below develop design choices and their limits rather than treating explicitness as a universal reason to remove frameworks.

## Explicit Execution Pipelines

One possible direction is to make important operation semantics visible directly in the operation definition.

Instead of:

```csharp
return mediator.Send(request);
```

an operation might resemble:

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

The exact syntax is not important.

The important property is that the execution graph becomes visible:

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

An agent can reason about the operation without reconstructing several layers of framework configuration.

## This Does Not Mean Eliminating All Abstraction

Some abstractions should remain hidden.

For example, an ASP.NET action can reasonably receive:

```csharp
GetOrderRequest request
```

without explicitly handling:

```text
TCP
HTTP parsing
TLS
UTF-8
JSON tokenization
object allocation
deserialization
```

These are implementation mechanisms.

The operation usually does not care how the DTO was produced.

Similarly, returning a response object does not require the business operation to explicitly handle HTTP serialization or socket writes.

A useful boundary may therefore be:

```text
framework owns mechanics
operation owns semantics
```

The framework can hide how input becomes a DTO.

The operation should make visible the decisions that influence what the operation means.

## Infrastructure Can Be Implicit More Safely Than Business Semantics

Not all hidden behavior has the same cost.

Relatively safe candidates for implicit handling include:

```text
generic logging
tracing
request timing
metrics
compression
correlation IDs
serialization
```

More dangerous hidden behavior includes:

```text
authorization
tenant selection
business validation
transaction boundaries
retry behavior
idempotency
cache semantics
feature flags
currency or locale selection
handler selection
error interpretation
```

A possible rule is:

> Infrastructure may be implicit. Business-relevant semantics should preferably be explicit.

The boundary will not always be perfect, but it provides a useful design direction.

The operational distinction comes down to failure blast radius. When generic timing metrics or trace baggage fail, the endpoint degrades slightly. When tenant filters, transaction boundaries, or cache invalidations are hidden in interceptors, an agent modifying the code risks introducing silent cross-tenant leaks, partial writes, or split-brain cache states that localized unit tests will not catch.

## Global Configuration Still Has Value

Making behavior explicit does not require copying implementation details into every operation.

For example, retry may still be centrally configured:

```csharp
RetryPolicies.ExternalRead
```

could define:

```text
3 attempts
exponential backoff
jitter
retry on timeout
retry on HTTP 502/503/504
```

while the operation only says:

```csharp
.Retry(RetryPolicies.ExternalRead)
```

This separates two different concerns:

```text
local code:
WHAT semantic policy applies

central configuration:
HOW that policy works
```

This may be a particularly useful compromise.

Global configuration defines reusable policy.

The call site explicitly declares that the policy participates in the operation.

## Named Semantics Are Better Than Silent Global Behavior

Compare:

```csharp
await client.SendAsync(request);
```

where retry is silently injected by global `HttpClient` configuration,

with:

```csharp
await request
    .Retry(RetryPolicies.ExternalRead)
    .Execute();
```

The second version still uses abstraction.

However, the abstraction leaves a visible semantic trace.

The agent immediately knows that:

```text
this operation may execute more than once
```

That knowledge can affect decisions about:

- idempotency,

- database writes,

- external side effects,

- request identifiers,

- duplicate handling.

The exact implementation of retry remains reusable and centrally controlled.

## Large Applications Already Struggle With Truly Global Policies

This approach may also address a problem that exists even without AI.

In a large system containing:

```text
hundreds of endpoints
many modules
multiple databases
different external integrations
different SLA requirements
different business risks
```

a single global policy is rarely actually global.

It gradually becomes:

```text
default behavior
except Payments
except Reporting
except legacy integration
except bulk operations
except endpoint X
unless attribute Y exists
unless interface Z is implemented
```

The centralized configuration eventually becomes another complex program.

The apparent simplicity of each endpoint is paid for by complexity elsewhere.

Module-level or operation-class policies may therefore scale better:

```text
system defaults
→ module defaults
→ operation category
→ explicit operation override
```

For example:

```text
Catalog:
    external reads may retry

Payments:
    commands do not retry unless explicitly idempotent

Reporting:
    long timeout
    read-only transaction semantics
```

The policy implementation remains centralized, while the semantic choice stays close to the operation.

## Abstractions Could Become Mechanically Expandable

There is another possible solution that does not require removing existing abstractions.

Future frameworks and development tools could expose the resolved semantics of an operation.

The source might contain:

```csharp
.Retry(RetryPolicies.ExternalRead)
```

while an agent can request:

```text
resolve RetryPolicies.ExternalRead
```

and receive:

```text
max attempts: 3
backoff: exponential
jitter: enabled
retry:
  timeout
  502
  503
  504
```

The same mechanism could resolve an entire endpoint:

```text
GetOrder

authentication:
    required

authorization:
    ReadOrderPolicy

validation:
    GetOrderValidator

tenant:
    request tenant

transaction:
    read-only

retry:
    ExternalRead
    attempts: 3

handler:
    GetOrderHandler

cache:
    OrderById
    TTL: 5 minutes
```

This suggests an important property for future abstractions:

> Abstractions should be mechanically expandable.

Documentation is useful.

A machine-readable resolved execution model is much more useful to an agent.

## Good Abstractions for Agents May Optimize for Different Things

Traditional APIs often optimize for:

```text
few lines
few parameters
minimal boilerplate
maximum reuse
```

Agent-oriented APIs may increasingly optimize for:

```text
semantic locality
explicit dependencies
visible execution flow
mechanically discoverable behavior
predictable composition
```

This does not imply that code must become low-level.

For example:

```csharp
.RetryTransient(3)
```

is still an abstraction.

It hides backoff implementation, timers, exception matching, and scheduling.

But it preserves the fact that matters semantically:

```text
the operation may execute multiple times
```

By contrast:

```csharp
.ExecuteUsingStandardEnterprisePolicies()
```

may hide almost everything the agent needs to know.

A useful distinction is therefore:

> A good abstraction reduces syntax without hiding important semantics.

## Business Meaning Should Be Encoded in the Same Vocabulary

Semantic locality is not only about where behavior executes.

It is also about whether the code uses the same concepts and vocabulary as the domain, documentation, API contracts, database schema, tests, and operational descriptions.

Consider:

```csharp
if (payment != null)
{
    ...
}
```

In a particular system, this may implicitly mean:

```text
the invoice is unpaid
```

A developer who has worked on the system for years may know that convention.

An agent may not.

The agent sees evidence:

```text
Payment exists
```

but must infer the business conclusion:

```text
invoice is unpaid
```

That inference may be correct, incorrect, or missed entirely.

Compare that with:

```csharp
if (payment.Status == PaymentStatus.Unpaid)
{
    ...
}
```

or:

```csharp
if (payment.IsUnpaid)
{
    ...
}
```

Now the business concept is explicitly represented in the code.

This matters particularly when the same concept appears elsewhere in the system.

Suppose the documentation says:

```text
retry unpaid payments
```

the API specification contains:

```text
paymentStatus: unpaid
```

and tests are named:

```text
ShouldRetryUnpaidPayment
```

An agent searching for or reasoning about "unpaid payment" can directly associate all of these artifacts with:

```csharp
PaymentStatus.Unpaid
```

It has a much weaker semantic connection to:

```csharp
payment != null
```

The same problem appears with sentinel values and technical representations:

```csharp
amount == 0
endDate == null
retryCount == -1
status == 2
customerId != null
```

These values may encode business meanings such as:

```text
free
active
unlimited retries
awaiting payment
customer assigned
```

but the meaning is not present in the expression itself.

A more agent-friendly model exposes the conclusion:

```csharp
price.IsFree
subscription.IsActive
retryPolicy.IsUnlimited
payment.Status == PaymentStatus.Unpaid
order.HasAssignedCustomer
```

This suggests a broader rule:

> Prefer code that encodes business conclusions rather than only technical evidence from which those conclusions must be inferred.

The principle extends beyond source code.

Ideally, the same domain vocabulary should appear consistently in:

```text
domain model
API contracts
database schema
tests
documentation
events and messages
logs and telemetry
```

For example:

```text
Documentation:
    unpaid payment

Code:
    PaymentStatus.Unpaid

API:
    paymentStatus = "unpaid"

Database:
    payment_status = "unpaid"

Event:
    PaymentBecameUnpaid

Test:
    ShouldRetryUnpaidPayment
```

This creates **semantic alignment across artifacts**.

For an agent, that alignment has several benefits:

- repository search becomes more reliable,
- embeddings and RAG retrieval are more likely to connect relevant artifacts,
- documentation can be mapped to implementation more directly,
- fewer hidden conventions must be reconstructed,
- code review requires less inference,
- generated changes are more likely to use the correct business concept.

Comments can help:

```csharp
// A non-null Payment means the invoice has not been paid yet.
if (payment != null)
```

but comments are weaker than encoding the meaning in the model itself.

They can become stale, they may not participate in all tooling, and they still leave the underlying representation semantically indirect.

Documentation or schema descriptions are also useful when the technical representation cannot be changed.

For example, if a legacy database uses:

```text
payment_state = 2
```

then the schema or mapping layer should make the meaning mechanically discoverable:

```text
2 = unpaid
```

or preferably expose it to application code as:

```csharp
PaymentStatus.Unpaid
```

This leads to another useful design principle:

> Use the same business vocabulary across code, contracts, schemas, tests, and documentation whenever practical.

For humans, this reduces the amount of institutional knowledge needed to understand the system.

For agents, it reduces the number of semantic translations that must be inferred before a change can be made safely.

In this sense, agent-friendly code should not merely be readable.

It should be **semantically searchable and cross-referenceable**.

Choose the details that materially change business behavior and make them discoverable at the operation boundary. Reuse implementation where it helps, while keeping policy selection, real inputs, and side effects available to review and verification.

## Related Notes

- [[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]] — Why ambient state and invisible execution behavior increase the cost of safe changes.
- [[Designing Internal NuGet Packages as an Explicit, Composable Framework]] — Reusable infrastructure whose composition stays under application control.
- [[Strong Domain Types with Coding Agents]] — Encoding distinctions and local rules in types the compiler can check.
