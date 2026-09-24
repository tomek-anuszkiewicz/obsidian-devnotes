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
  - Semantic Locality in Agentic Architecture
  - Mechanically Expandable Abstractions
  - Domain Vocabulary Alignment
---

Modern software engineering often tries to remove repetitive concerns from local code.

Instead of explicitly writing validation, authorization, retries, transactions, logging, tracing, error mapping, and other infrastructure in every operation, we move them into reusable mechanisms such as:

- middleware,
    
- interceptors,
    
- decorators,
    
- dependency injection,
    
- HTTP message handlers,
    
- framework filters,
    
- MediatR behaviors,
    
- Entity Framework interceptors and query filters,
    
- global exception handling,
    
- conventions,
    
- assembly scanning,
    
- ambient context.
    

This can make individual methods extremely small.

For example:

```csharp
public Task<Response> GetOrder(GetOrderRequest request)
{
    return mediator.Send(request);
}
```

The method appears simple.

However, the actual execution may look more like:

```text
HTTP request
→ authentication middleware
→ authorization middleware
→ exception middleware
→ request validation
→ MediatR
→ logging behavior
→ transaction behavior
→ handler
→ Entity Framework query filter
→ database interceptor
→ SQL
→ response mapping
→ serialization
```

The local code is simple, but the semantics are not.

This distinction may become increasingly important when software is primarily modified by agents.

## Local Simplicity Is Not the Same as Semantic Simplicity

An agent working on a method must understand more than the code visible inside the method.

Consider:

```csharp
await httpClient.SendAsync(request);
```

The request may implicitly include:

- authentication headers,
    
- correlation identifiers,
    
- retry policies,
    
- circuit breakers,
    
- timeouts,
    
- telemetry,
    
- logging,
    
- tenant context.
    

The important behavior is distributed across configuration and framework mechanisms.

Similarly:

```csharp
context.Orders.ToListAsync();
```

may actually mean:

```text
load Orders
where TenantId == CurrentTenant
excluding soft-deleted records
using an interceptor-defined database command behavior
```

because of global query filters and other Entity Framework configuration.

The problem is therefore not simply abstraction.

The deeper problem is **non-local semantics**.

The meaning of a line of code depends on code that is not locally visible.

## Hidden Execution Context Is Particularly Difficult

Some dependencies are not passed explicitly at all.

They may come from:

```text
HttpContext
AsyncLocal
Activity.Current
ClaimsPrincipal
current tenant services
current culture
scoped dependency resolution
feature flags
environment configuration
```

A method can therefore appear to depend on:

```csharp
Process(Order order)
```

while its real inputs include:

```text
order
current user
tenant
feature configuration
current transaction
request metadata
culture
authorization context
```

This makes the true dependency graph much larger than the function signature suggests.

Humans often tolerate this because experienced developers gradually learn the architecture.

An agent entering a repository for a single task must rediscover it.

This creates a distinct failure mode: an agent writes code that compiles, passes localized unit tests using standard mocks (where ambient contexts default to empty or null), and then breaks in multi-tenant production because it bypassed an implicit ambient filter or failed to populate an `AsyncLocal` state variable.

## Dynamic Dependency Injection Makes the Problem Worse

Constructor injection itself is usually relatively easy to understand.

The situation becomes more difficult when implementations depend on runtime context:

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

Local code may only contain:

```csharp
priceCalculator.Calculate(order);
```

but the implementation that actually runs depends on external state.

Similar problems appear with:

- keyed services,
    
- decorators,
    
- assembly scanning,
    
- open generic registrations,
    
- conditional registration,
    
- plugin architectures.
    

The call site no longer tells the agent what code it is calling.

When static analysis cannot determine which concrete class implements an interface for a given execution path, the agent loses the ability to trace dependencies or reliably verify its changes.

## Interceptors and Pipelines Can Hide Business-Relevant Semantics

Cross-cutting abstractions become especially problematic when they contain behavior that changes the meaning of an operation.

A call such as:

```csharp
repository.Save(order);
```

may secretly perform:

```text
authorization
→ validation
→ transaction creation
→ audit logging
→ persistence
→ event publication
→ cache invalidation
```

Some of these are infrastructure concerns.

Others are part of the operation's semantics.

The distinction matters.

A generic timing metric being invisible is usually harmless.

A transaction boundary, retry policy, tenant filter, authorization rule, or business validation being invisible can fundamentally change how an agent should modify the operation.

When an agent needs to alter how an order is saved, it cannot see where the transaction begins or commits, whether the cache update is atomic, or whether domain events fire before or after the database write. If those operations are buried inside generic decorators or database interceptors, an agent trying to fix a bug or add a step will frequently introduce race conditions, partial writes, or security bypasses.

## Agents May Change the Economics of Explicit Code

Traditional software engineering strongly rewards removing repetition.

The reasoning is understandable:

```text
duplication
→ more code
→ more maintenance
→ more opportunities for inconsistency
```

This encourages patterns such as:

```text
DRY
→ centralize behavior
→ hide repeated mechanics behind abstractions
```

But agents reduce the cost of producing and maintaining repetitive code.

Agents generate, read, and verify code at negligible marginal cost compared to humans. Conversely, their failure modes skew heavily toward hallucinating unstated assumptions, misinterpreting implicit behavior, and missing cross-file conventions.

This creates the possibility of a different tradeoff:

```text
some duplication
→ greater semantic locality
→ easier reasoning
→ safer automated modification
```

The goal does not need to be eliminating abstractions.

It may instead be eliminating **invisible semantics**.

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

## Semantic Locality May Become an Architectural Goal

We can think about code as having different levels of semantic locality.

High semantic locality:

```csharp
CalculatePrice(order, customer, pricingRules);
```

The important inputs are visible.

Lower semantic locality:

```csharp
priceCalculator.Calculate(order);
```

The implementation must be discovered.

Even lower semantic locality:

```csharp
priceCalculator.Calculate(order);
```

where dependency injection selects the implementation based on runtime context.

Very low semantic locality:

```csharp
priceCalculator.Calculate(order);
```

where the result also depends on:

```text
current tenant
feature flags
ambient user
interceptors
global cache
transaction context
dynamic configuration
```

The textual code can remain equally short while the reasoning cost increases dramatically.

For agent-maintained systems, **semantic locality may become as important as traditional measures such as coupling, cohesion, and duplication**.

## The Likely Direction Is Not "No Abstractions"

The more realistic direction is:

```text
hide mechanisms
expose semantic decisions
centralize implementation
localize intent
make abstractions inspectable
```

This could lead to code that is somewhat more verbose than today's most heavily abstracted application architectures.

But the code may also become:

- easier for agents to modify,
    
- easier for humans to review,
    
- easier to test,
    
- easier to analyze statically,
    
- less dependent on institutional knowledge,
    
- safer to refactor automatically.
    

The important shift may therefore not be from abstraction to no abstraction.

It may be from:

```text
implicit, non-local behavior
```

toward:

```text
explicit, composable, mechanically discoverable behavior
```

In software increasingly written and maintained by agents, the cost of repetition may fall while the cost of hidden semantics becomes much more visible (see [[Software Decay and the Hidden Costs of Frictionless AI Code]], [[Designing Internal NuGet Packages as an Explicit, Composable Framework]], and [[AI May Make Aggressive Code Optimization Economically Viable]]).

That could change what we consider "clean" architecture.

## Related notes

- **[[Designing Internal NuGet Packages as an Explicit, Composable Framework]]** — Turning implicit convention magic into explicit, typed components.
- **[[AI May Make Aggressive Code Optimization Economically Viable]]** — How shedding layers of indirection and reflection unlocks compiler optimizations and lowers hardware execution costs.
- **[[Designing Software for AI Agents]]** — Architectural patterns that reduce cognitive overhead and token burn for agents.
- **[[Software Decay and the Hidden Costs of Frictionless AI Code]]** — Why rapid generation without semantic transparency accelerates system entropy.
- **[[Internal NuGet Packages vs Agent-Generated Code]]** — Balancing central abstractions against self-contained local implementations.
