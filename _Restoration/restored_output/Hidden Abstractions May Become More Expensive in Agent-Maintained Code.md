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
