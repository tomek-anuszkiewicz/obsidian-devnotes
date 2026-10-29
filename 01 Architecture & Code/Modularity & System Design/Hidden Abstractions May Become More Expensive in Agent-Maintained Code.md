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

A handler can contain very little code while depending on a transaction wrapper, an ambient tenant, a dynamically selected implementation, and an interceptor that changes writes. An agent editing the handler must reconstruct those dependencies before it can judge the effect of a change.

This article examines that cost: which behavior is hidden, how it affects investigation and verification, and why cheap code generation changes the trade-off around repetition. [[Designing Explicit Operations for Agent-Maintained Code]] develops the design response through explicit pipelines, named policies, inspectable execution models, and consistent business vocabulary. Keep enough visible context to identify the real inputs and effects of the operation.

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
