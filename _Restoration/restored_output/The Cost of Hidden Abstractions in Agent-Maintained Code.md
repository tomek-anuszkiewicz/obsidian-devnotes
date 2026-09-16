---
title: "The Cost of Hidden Abstractions in Agent-Maintained Code"
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

Modern software engineering often tries to strip repetitive mechanics out of application code. Instead of hand-rolling validation, authorization, retries, database transactions, logging, distributed tracing, and error mapping inside every single endpoint or command handler, we delegate them to reusable framework mechanisms:

- HTTP middleware pipelines
- Interceptors and dynamic decorators
- Inversion of Control (IoC) containers
- Delegating HTTP message handlers
- Framework action filters
- MediatR and command pipeline behaviors
- Entity Framework interceptors and global query filters
- Global exception mappers
- Assembly scanning and convention-based registrations
- Ambient execution contexts (`AsyncLocal<T>`, `HttpContext.Current`)

This pattern makes individual methods look remarkably lean. Consider a common C# controller action or minimal API endpoint:

```csharp
public Task<Response> GetOrder(GetOrderRequest request)
{
    return mediator.Send(request);
}
```

On the surface, this method is trivial to read. But at runtime, execution looks more like this:

```text
HTTP Request
→ Authentication middleware
→ Authorization middleware
→ Global exception handler
→ Request validation behavior (FluentValidation)
→ MediatR pipeline dispatch
→ Logging and telemetry scope behavior
→ Transaction scope behavior
→ Concrete OrderHandler execution
→ Entity Framework Core global query filter (TenantId check)
→ Database command interceptor (Soft-delete filter)
→ Generated SQL execution
→ Response DTO mapping (AutoMapper)
→ JSON serialization
→ HTTP Response
```

The method body has almost zero visual noise, but its runtime semantics are complex. 

For an experienced human engineer who built or lived in that codebase for two years, this ambient machinery is second nature. But when software is increasingly read, analyzed, and modified by AI coding agents entering a repository on demand, this split between visual brevity and operational reality becomes a serious liability.

---

## Local Simplicity Is Not the Same as Semantic Simplicity

An agent analyzing an isolated method must understand far more than the tokens visible within that method's curly braces.

Consider an outbound network call:

```csharp
await httpClient.SendAsync(request);
```

To an LLM scanning the file, this looks like a straightforward, one-shot HTTP request. But in a typical enterprise setup, the underlying `HttpClient` handler chain silently injects:

- Ambient authentication headers (OAuth bearer token refresh flows)
- Distributed tracing correlation identifiers (`traceparent`, `tracestate`)
- Centralized retry policies (Polly handlers with exponential backoff)
- Circuit breakers and bulkhead isolators
- Dynamic timeouts
- Client-side metrics emission
- Active tenant context headers

The actual runtime behavior is scattered across remote startup classes, configuration files, and framework extensions.

The same problem shows up in modern data access:

```csharp
context.Orders.ToListAsync();
```

Because of underlying EF Core configurations, this single call might actually translate to:

```sql
SELECT [o].[Id], [o].[OrderNumber], [o].[Total]
FROM [Orders] AS [o]
WHERE [o].[TenantId] = @__ef_filter__CurrentTenantId_0
  AND [o].[IsDeleted] = 0
```

The call site looks like an unrestricted read of the entire table. In reality, it executes with an implicit multi-tenant constraint, an implicit soft-delete filter, and custom interceptor logic attached to the underlying database connection.

The core problem here is not abstraction. Software cannot function without abstractions. The problem is **non-local semantics**: the meaning, constraints, and side effects of a line of code depend entirely on logic that is nowhere to be seen at the call site.

---

## The Spectrum of Semantic Locality

Codebases exist on a spectrum between total explicit clarity and completely invisible mechanics:

```text
Level 1: Explicit Parameterization (Highest Semantic Locality)
CalculatePrice(order, customerTier, discountPolicy);
-> All operational inputs, rules, and runtime dependencies are directly visible.

Level 2: Direct Interface Composition
priceCalculator.Calculate(order);
-> Clean interface boundary, navigable via standard symbol navigation.

Level 3: Runtime-Resolved Dependency Injection
priceCalculator.Calculate(order);
-> Implementation is conditionally chosen at runtime by the container based on 
   configuration, feature flags, or request metadata.

Level 4: Ambient Execution Magic (Lowest Semantic Locality)
priceCalculator.Calculate(order);
-> Behavior silently relies on ambient AsyncLocal user context, global DB interceptors, 
   middleware ordering, and auto-enlisted transaction scopes.
```

When an agent works on Level 1 or Level 2 code, it can reason about inputs, side effects, and failure modes directly from the surrounding context. 

When it encounters Level 4 code, visual brevity provides zero safety. The method is an iceberg: 10% visible application code, 90% hidden runtime plumbing.

---

## Hidden Execution Context and Ambient State

The most problematic dependencies are those never passed through a method signature or constructor. They ride along in ambient execution state:

- `HttpContext.Current` / `IHttpContextAccessor`
- `AsyncLocal<T>` and thread-local storage
- `Activity.Current` (distributed tracing baggage)
- `ClaimsPrincipal.Current`
- Ambient tenant resolution services
- Thread culture and timezone settings
- Container service locators resolving scoped instances mid-execution
- Feature flag state fetched dynamically from remote providers
- Ambient database transaction scopes (`TransactionScope`)

A method signature may state:

```csharp
public void Process(Order order)
```

while its actual execution requirements are:

```text
order 
+ current authenticated user
+ active organization / tenant ID
+ active distributed transaction
+ dynamic feature flag snapshot
+ request routing metadata
+ ambient culture info
```

The real dependency graph is significantly wider than the function signature reveals.

A human engineer slowly internalizes these hidden conventions through institutional memory, onboarding, and painful debugging sessions. An agent entering a repository to resolve an issue or add an endpoint has to rediscover this invisible context from scratch every single run.

This creates a distinct failure mode: an agent writes code that compiles, passes localized unit tests using standard mocks (where ambient contexts default to empty or null), and then breaks in multi-tenant production because it bypassed an implicit ambient filter or failed to populate an `AsyncLocal` state variable.

---

## Dynamic Dependency Injection Obscures the Call Graph

Standard constructor injection is usually straightforward for automated tools to trace. The friction increases dramatically when the IoC container uses runtime context to select implementations:

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

At the call site, the code appears clear:

```csharp
priceCalculator.Calculate(order);
```

Yet neither an engineer nor an LLM can determine what code actually runs without reverse-engineering the container registration, identifying how `OperationContext.Channel` is set in the HTTP pipeline, and mapping that against the current scenario.

This opacity compounds when systems lean heavily on:

- Keyed and tagged service resolutions
- Dynamic runtime decorators
- Assembly scanning (`services.Scan(...)`) that auto-registers classes by naming convention
- Open generic registrations (`typeof(IValidator<>)`)
- Conditional feature-flag registrations
- Plugin architectures loading assemblies via reflection

When static analysis cannot determine which concrete class implements an interface for a given execution path, the agent loses the ability to reliably verify its changes.

---

## Interceptors and Pipelines: Where Infrastructure Meets Business Semantics

Cross-cutting pipelines become dangerous when they quietly take on business-critical responsibilities.

Take a seemingly innocent data call:

```csharp
repository.Save(order);
```

In a framework-heavy codebase, that single line might trigger a chain of interceptors:

```text
repository.Save(order)
→ Check tenant permissions (Authorization)
→ Run domain validation rules (Validation)
→ Begin database transaction (Data integrity)
→ Write audit trail entry (Compliance)
→ Commit state to database (Persistence)
→ Publish Domain Events to message broker (Integration)
→ Invalidate Redis cache keys (Consistency)
```

Some of these are pure infrastructure: timing metrics, standard SQL tracing, connection pooling. But others—transaction boundaries, authorization rules, idempotency gates, domain events, and cache invalidations—are direct expressions of business semantics.

When an agent needs to alter how an order is saved, it cannot see where the transaction begins or commits, whether the cache update is atomic, or whether domain events fire before or after the database write. If those operations are buried inside generic decorators or database interceptors, an agent trying to fix a bug or add a step will frequently introduce race conditions, partial writes, or security bypasses.

---

## The Changing Economics of Explicit Code

Traditional software engineering placed an immense premium on minimizing line counts and keystrokes. The rationale was obvious:

```text
Human writes duplicate code
→ More code to read and maintain
→ Higher surface area for human error
→ High risk of inconsistent implementations
```

This dynamic drove developers toward strict DRY patterns: extract every common pattern into a global filter, hide repeated mechanics behind ambient interceptors, and keep methods under five lines at all costs.

AI coding agents change the economics of this tradeoff. Agents generate, read, and verify code at negligible marginal cost compared to humans. Conversely, their failure modes skew heavily toward hallucinating unstated assumptions, misinterpreting implicit behavior, and missing cross-file conventions.

This shifts the engineering balance:

```text
Traditional DRY Strategy:
Eliminate visual repetition 
→ Move logic into ambient frameworks and dynamic interceptors
→ Result: High cognitive load, non-local semantics, fragile automated edits

Agent-Friendly Strategy:
Maximize semantic locality 
→ Use explicit pipelines, direct parameters, and visible boundaries
→ Result: Slightly higher line counts, zero hidden runtime assumptions, low blast radius
```

The goal is not to write sprawling, unmaintainable boilerplate. The goal is to eliminate **invisible semantics**.

---

## Explicit Execution Pipelines

Instead of routing execution through opaque runtime buses:

```csharp
public Task<Response> Handle(GetOrderRequest request)
{
    return mediator.Send(request);
}
```

we can compose operations using explicit pipelines that state their execution graph openly:

```csharp
public static Task<OrderResponse> Handle(
    GetOrderRequest request, 
    IOrderRepository repository,
    CancellationToken ct)
{
    return Operation
        .From(request)
        .Validate(new GetOrderValidator())
        .Authorize(Permissions.OrdersRead)
        .Retry(RetryPolicies.ExternalNetworkRead)
        .Execute(req => repository.GetOrderAsync(req.OrderId, ct))
        .ValidateResponse(response => response != null)
        .MapErrors(OrderErrorMapper.ToHttpResult)
        .Return();
}
```

The syntax can vary based on language and team preferences. The architectural win is that the operational execution graph is laid out directly in the file:

```text
Incoming request
→ Specific validator
→ Explicit permission check
→ Configured retry strategy
→ Database operation execution
→ Response verification
→ Error mapping
→ Return response
```

An agent modifying this workflow does not have to hunt down MediatR pipeline registrations, check whether validation happens before or after authorization, or guess if the call is wrapped in a retry handler. The operational sequence is right in front of it.

---

## The Boundary: Framework Owns Mechanics, Operation Owns Semantics

Making code semantically explicit does not mean stripping out all abstractions and writing low-level socket code. 

For instance, an ASP.NET Core controller or endpoint handler accepts a strongly typed DTO:

```csharp
public async Task<Results<Ok<Order>, NotFound>> GetOrder(GetOrderRequest request)
```

The handler does not—and should not—manually orchestrate:

- TCP handshake and connection management
- TLS decryption
- HTTP/2 or HTTP/3 frame parsing
- UTF-8 byte decoding
- JSON tokenization and memory allocation
- Request buffer recycling

Those are **implementation mechanics**. The business operation does not care how the bytes on the wire turned into a `GetOrderRequest` instance, so long as the conversion adheres to the standard protocol.

The boundary is straightforward:

> **The framework owns mechanics. The operation owns semantics.**

The framework should silently handle how an HTTP packet becomes an object in memory. The operation itself must explicitly declare the rules that determine its business outcome: who can call it, what invariants must hold, how transactions are bounded, and what happens when an external dependency fails.

---

## What Can Stay Implicit vs. What Must Be Explicit

Not every system concern needs to be exposed at the call site. The dividing line comes down to whether the behavior alters business outcomes or operational invariants:

| System Behavior | Recommended Approach | Architectural Rationale |
| :--- | :--- | :--- |
| **Low-Level Plumbing** | **Implicit / Framework-Owned** | TCP framing, TLS negotiation, JSON tokenization, memory buffer pooling. These mechanics have no bearing on business logic; keep them hidden. |
| **Generic Telemetry** | **Implicit / Middleware** | Execution duration timers, Prometheus request counters, standard OpenTelemetry tracing spans. Safe to handle globally. |
| **Tenant Isolation** | **Explicit** | Multi-tenant leaks are severe security bugs. Passing tenant context explicitly or scoping queries visibly prevents silent cross-tenant data access. |
| **Transaction Scopes** | **Explicit** | Agents need to see exactly where units of work begin, commit, or abort to avoid deadlocks, partial writes, and distributed state corruption. |
| **Retries & Idempotency** | **Explicit Policy Attachment** | Knowing an operation can run multiple times dictates how side effects, unique constraints, and payment charges must be structured. |
| **Authorization Checks** | **Explicit Gates** | Security policies should be visible in the execution pipeline so agents cannot inadvertently bypass access controls during refactors. |
| **Cache Invalidation** | **Explicit Handlers** | Hiding cache updates in database interceptors causes stale reads and split-brain states that are notoriously hard for automated tools to trace. |

---

## Global Policy Configuration, Local Semantic Binding

Writing explicit code does not mean copy-pasting complex implementation details across every file.

Consider retry logic. Instead of burying retry rules inside a generic, opaque HTTP client factory:

```csharp
// Silent global injection: the call site has no idea it retries
await client.SendAsync(request);
```

you centralize the policy's implementation, but bind it explicitly at the call site:

```csharp
// Reusable policy defined centrally:
public static class RetryPolicies
{
    public static readonly IAsyncPolicy ExternalRead = Policy
        .Handle<HttpRequestException>()
        .Or<TimeoutException>()
        .WaitAndRetryAsync(3, attempt => TimeSpan.FromMilliseconds(200 * Math.Pow(2, attempt)));
}

// Call site:
await request
    .WithPolicy(RetryPolicies.ExternalRead)
    .ExecuteAsync(ct);
```

This neatly separates two concerns:

- **Local code declares WHAT semantic policy applies**: "This call retries using external read policies."
- **Central configuration defines HOW that policy executes**: 3 attempts, exponential backoff, jitter, specific exception filters.

The call site retains a visible semantic trace. An agent reading this code instantly understands an essential operational invariant: **this block of code may execute multiple times**.

That single piece of explicit context directly influences whether the agent can safely place an un-keyed database insert, a third-party charge, or an external messaging call inside that block.

---

## Why Truly Global Policies Break Down at Scale

Decoupling policies from call sites creates operational headaches even without AI in the mix. 

In large-scale production systems—spanning hundreds of endpoints, multiple databases, varied third-party integrations, and tight SLAs—a single "global" policy rarely stays truly global. It inevitably degrades into a maze of exceptions:

```text
Global HTTP Policy
  ├─ Default: 3 retries on failure
  ├─ Except Payments (never retry non-idempotent charges)
  ├─ Except Reporting (extended 60s timeout, no retries)
  ├─ Except Inventory Bulk Import (custom streaming timeout)
  └─ Except Legacy ERP (disable HTTP/2, custom headers)
```

The central configuration file turns into a brittle, high-cyclomatic-complexity router packed with conditional type checks, path matching, and custom attributes. You gain the illusion of simple endpoint handlers by shifting that complexity into an opaque, central configuration that is terrifying to modify.

Organizing policies by domain class or module, and binding them explicitly to operations, scales much better:

```text
Catalog Service:
    All read operations use CatalogPolicies.ResilientRead

Billing Service:
    Mutations explicitly require an IdempotencyKey
    No automatic retries without an Idempotency-Token header

Analytics Service:
    Read-only transaction semantics
    Extended command timeouts
```

The policies remain centralized and maintainable, but their application is declared clearly at the operational boundary.

---

## Mechanically Expandable Abstractions

An alternative to writing verbose call sites is providing tooling that lets agents mechanically expand abstractions on demand.

If source code contains:

```csharp
.WithPolicy(RetryPolicies.ExternalRead)
```

an agent equipped with static analysis tools or language server protocol (LSP) integrations can query the environment:

```text
$ tool resolve-policy RetryPolicies.ExternalRead

Result:
  Type: ExponentialBackoffRetry
  MaxAttempts: 3
  BaseDelay: 200ms
  HandledExceptions:
    - System.Net.Http.HttpRequestException
    - System.TimeoutException
  IdempotencyRequired: true
```

The same tooling could resolve an entire endpoint's operational profile:

```text
$ tool describe-endpoint OrdersController.GetOrder

Endpoint: OrdersController.GetOrder(Guid orderId)
Runtime Profile:
  Authentication: Required (JWT Bearer)
  Authorization: Policy "OrdersRead" (Claims: scope=orders:read)
  Tenant Isolation: Enforced (Query filter: TenantId == CurrentUser.TenantId)
  Transaction: Read-Only (Enlisted: false)
  Dependencies:
    - IOrderRepository (Scoped: SqlOrderRepository)
    - ICacheService (Scoped: RedisCacheService)
  Execution Pipeline:
    1. Validate Request (GetOrderValidator)
    2. Check Cache (Key: "orders:{tenant}:{orderId}", TTL: 300s)
    3. Query Database (EF Core - Tracking: Disabled)
```

If modern application frameworks exposed this kind of resolved semantic execution model via machine-readable endpoints or CLI commands, agents wouldn't have to guess how your dynamic dependencies assemble at runtime. 

The rule of thumb for designing modern framework layers is simple: **if you hide implementation details behind an abstraction, make sure that abstraction can be expanded mechanically by static tooling.**

---

## Encoding Business Meaning in Domain Vocabulary

Semantic locality isn't limited to control flow and execution graphs; it also applies to business vocabulary. Code should express concepts using the same ubiquitous domain language that appears across system documentation, API schemas, database tables, tests, and operational runbooks.

Consider a pattern found in many codebases:

```csharp
if (payment != null)
{
    // ...
}
```

In the original developer's head, this null-check represents a distinct business state: *the invoice has an active payment attempt underway, and is therefore unpaid*. 

An engineer reading that code after two years on the team might remember that convention. An AI agent scanning the file sees only the technical check: *an object reference exists*. It has to infer the business state, and that inference is often wrong.

Now look at the explicit version:

```csharp
if (payment.Status == PaymentStatus.Unpaid)
{
    // ...
}
```

or:

```csharp
if (payment.IsUnpaid)
{
    // ...
}
```

The code directly reflects the business concept.

This alignment becomes crucial when tracking behavior across an entire repository. If your architectural runbook states:

```text
"Retry all unpaid payments after 24 hours"
```

and your OpenAPI specification exposes:

```yaml
PaymentResponse:
  properties:
    status:
      type: string
      enum: [unpaid, processing, completed, failed]
```

and your test suite includes:

```csharp
[Fact]
public async Task ShouldRetryUnpaidPayment_WhenGracePeriodExpires()
```

an agent searching the codebase to implement a new billing rule can instantly link the docs, contracts, and tests to:

```csharp
PaymentStatus.Unpaid
```

If the implementation instead hides behind:

```csharp
if (payment != null)
```

the agent's semantic search loses the trail.

The same problem shows up with magic numbers and sentinel values:

```csharp
// Unclear sentinel values (require inferential jumps):
if (amount == 0)              // Means: "Price is complimentary/free"
if (endDate == null)          // Means: "Subscription is actively running"
if (retryCount == -1)         // Means: "Policy allows unlimited retries"
if (status == 2)              // Means: "Order is pending fulfillment"
if (customerId != null)       // Means: "Guest user has converted to registered account"
```

Each of these checks requires the reader to infer a business conclusion from raw technical data. 

Eliminate the guesswork by modeling the domain state explicitly:

```csharp
// Explicit domain representations:
if (price.IsFree)
if (subscription.IsActive)
if (retryPolicy.IsUnlimited)
if (order.Status == OrderStatus.PendingFulfillment)
if (customer.IsRegisteredAccount)
```

Always prefer code that directly states business conclusions over code that merely exposes low-level technical evidence.

```text
Documentation:
  "Unpaid invoices trigger a reminder email."

Domain Model:
  InvoiceStatus.Unpaid

API Contract:
  "status": "unpaid"

Database Schema:
  status_code = 'unpaid'

Domain Event:
  InvoicePaymentMarkedUnpaid

Test Name:
  ShouldSendReminderEmail_WhenInvoiceIsUnpaid()
```

When domain vocabulary is aligned across all artifacts:

- Semantic search and RAG indexing hit exact references.
- Documentation maps directly to executable code.
- Agents make edits using the domain model instead of hardcoded technical workarounds.
- Automated code reviews can cross-reference business requirements directly against diffs.

---

## Semantic Locality as a Core Architectural Metric

For decades, software architecture evaluated code through metrics like cyclomatic complexity, coupling, cohesion, and duplication.

When systems are maintained and refactored by AI agents, **semantic locality** becomes just as critical.

```csharp
// 1. Highest Semantic Locality:
CalculatePrice(order, customer, pricingRules);

// 2. Lower Semantic Locality:
priceCalculator.Calculate(order);

// 3. Significantly Lower Semantic Locality:
// Concrete implementation chosen dynamically at runtime via ambient state
priceCalculator.Calculate(order);

// 4. Near-Zero Semantic Locality:
// Real outcome depends on ambient thread state, dynamic middleware, and interceptors
priceCalculator.Calculate(order);
```

In all four cases, the line of code looks almost identical. But the cognitive work required to understand, test, and safely modify that line skyrockets as semantic locality drops.

The answer is not to abandon abstractions or return to writing monolithic 1,000-line procedures. The goal is to build architectures that:

- Hide low-level technical mechanics (parsing, allocations, transports).
- Expose business-relevant semantics (transactions, security, retries).
- Centralize policy definitions, but bind them explicitly at the call site.
- Make composite abstractions inspectable by automated tooling.
- Model explicit domain concepts instead of relying on implicit technical sentinels.

Code written this way is slightly more explicit than systems built around deep interceptor stacks. In exchange, it is radically easier for agents to update safely, faster for humans to review, and far more resilient to operational regressions.

---

## Related Notes

- [[Designing Software for AI Agents]]
- [[Software Decay and the Hidden Costs of Frictionless AI Code]]
- [[Optimizing Software Engineering and Code for Agents]]
- [[Designing Internal Packages as an Explicit, Composable Framework]]
- [[Data Access Economics with Coding Agents - ORMs vs Explicit SQL]]
- [[Internal Shared Packages vs Agent-Generated Code]]
- [[Testing in the Model, Agent, LLM Era]]
