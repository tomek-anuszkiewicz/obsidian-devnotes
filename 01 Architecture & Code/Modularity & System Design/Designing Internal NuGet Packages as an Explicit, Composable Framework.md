---
title: Designing Internal NuGet Packages as an Explicit, Composable Framework
tags:
  - dotnet
  - nuget
  - software-architecture
  - framework-design
  - modular-design
  - maintainability
  - ai-agents
  - package-management
aliases:
  - Designing Internal Packages as an Explicit, Composable Framework
  - Internal NuGet Framework Architecture
  - Explicit Composable NuGet Packages
  - Designing Internal Shared Libraries
  - Service Platform Composition and Replacement
---

A shared package can provide a useful capability while leaving the application in control of startup, middleware order, and operational policy. It can also hide those decisions behind a single registration method and spread its types into business code.

This article develops the composition boundary: what the application selects, where shared infrastructure participates, and which behavior must remain visible. [[Evolving and Maintaining Internal NuGet Packages]] follows dependencies, public contracts, replaceability, consumer variation, ownership, and migrations. [[Internal NuGet Packages vs Agent-Generated Code]] compares shared runtime code with local generated implementations and external behavioral checks. Choose that sharing model deliberately, then make its composition understandable.

## Core Idea

Internal NuGet packages may collectively form a corporate framework.

That is not inherently a problem.

The problem begins when the framework:

- hides application configuration,

- silently registers large parts of the runtime,

- owns the bootstrap process,

- introduces a large dependency tree,

- becomes difficult to replace,

- accumulates unrelated features for many teams,

- grows so complex that nobody feels safe changing it.

A good internal framework should provide **modular building blocks** that are explicitly selected, configured, and composed by the consuming application.

The application should remain the owner of its runtime configuration.

When maintaining codebases alongside AI coding agents, magic shared packages become severe operational bottlenecks. Coding agents cannot reliably infer ambient reflection scanning, hidden dependency injection registrations, or implicit bootstrap hooks without hallucinating side effects. Explicit composition keeps the execution graph directly in the context window as executable documentation (see [[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]).

---

## Prefer Configuration by Composition

The framework should provide building blocks.

The application should compose them explicitly.

For example:

```csharp
builder.Services.AddCompanyLogging(options =>
{
    options.ApplicationName = "Orders";
});

builder.Services.AddCompanyTracing();

builder.Services.AddGrafanaExporter();

builder.Services.AddCompanyAuthentication(options =>
{
    options.Authority = configuration["Auth:Authority"];
});

builder.Services.AddCompanyProblemDetails();

var app = builder.Build();

app.UseCompanyCorrelation();
app.UseCompanyRequestLogging();
app.UseAuthentication();
app.UseAuthorization();
app.UseCompanyExceptionHandling();
```

This is more verbose than:

```csharp
builder.Services.AddCompanyPlatform(configuration);

var app = builder.Build();

app.UseCompanyPlatform();
```

However, the explicit configuration is valuable.

It shows:

- which capabilities are enabled,

- how they are configured,

- which infrastructure providers are used,

- which middleware is active,

- the order in which the pipeline executes,

- which component can be removed or replaced.

The startup code is not merely boilerplate.

It is an executable description of the application architecture.

---

### Prefer Explicit Composition

Instead of one large registration:

```csharp
builder.Services.AddCompanyPlatform(configuration);
```

prefer explicit modules:

```csharp
builder.Services.AddCompanyLogging();
builder.Services.AddCompanyTracing();
builder.Services.AddCompanyMetrics();
builder.Services.AddGrafanaExporter();
builder.Services.AddCompanyAuthentication();
builder.Services.AddCompanyServiceBus();
builder.Services.AddCompanyPostgres();
```

Middleware should also remain visible:

```csharp
app.UseCompanyCorrelation();
app.UseCompanyExceptionHandling();
app.UseAuthentication();
app.UseAuthorization();
app.UseCompanyRequestLogging();
```

This configuration may contain more lines of code, but those lines are not meaningless boilerplate.

They form an executable description of the service architecture.

A developer or agent can see:

- which capabilities are active,

- which providers are used,

- which policies are configured,

- in what order middleware executes,

- which component can be removed,

- which component can be replaced.

The application should remain the owner of its bootstrap process.

## Middleware Must Be Explicit

Middleware order is part of application behavior.

A NuGet package may provide middleware, but the consuming application should explicitly add it to the pipeline.

Prefer:

```csharp
app.UseCompanyCorrelation();
app.UseCompanyRequestLogging();
app.UseAuthentication();
app.UseAuthorization();
app.UseCompanyExceptionHandling();
```

Avoid hiding the complete pipeline behind:

```csharp
app.UseCompanyDefaults();
```

The hidden method may register several components whose ordering and behavior are not visible to the application.

This creates problems when:

- a middleware must be moved,

- one middleware must be removed,

- a custom implementation must be inserted,

- the order differs between applications,

- debugging requires understanding the execution path.

A framework should make the pipeline easier to assemble, not make it invisible.

Pipeline order directly dictates resource utilization, security, and runtime correctness. If request body parsing executes before authentication, unauthenticated callers can stream multi-megabyte payloads that exhaust memory and trigger expensive garbage collection pauses before being rejected. Similarly, if exception logging runs before correlation ID extraction, unhandled failures drop the distributed tracing context needed for production triage.

---

## A Framework Is Acceptable When the Application Composes It

The goal is not to prevent internal packages from forming a framework.

A useful corporate framework may provide:

- logging components,

- telemetry integrations,

- authentication modules,

- middleware,

- cloud integrations,

- configuration helpers,

- API conventions,

- health checks,

- internal service clients.

The important distinction is between two models.

### Framework composed by the application

```csharp
services.AddCompanyLogging();
services.AddCompanyTracing();
services.AddGrafanaExporter();
services.AddCompanyAuthentication();
services.AddAzureKeyVault();

app.UseCompanyCorrelation();
app.UseCompanyRequestLogging();
app.UseAuthentication();
app.UseAuthorization();
```

The application owns the composition.

### Framework that owns the application

```csharp
services.AddCompanyPlatform();
app.UseCompanyPlatform();
```

The framework decides what is installed and how the application behaves.

The first model preserves visibility and control.

The second model hides architecture behind a small number of extension methods.

A useful rule is:

> Prefer a framework that is composed by the application over a framework that configures the application on its behalf.

---

A corporate service platform makes this trade-off concrete: the same convenience that removes startup work can become a hidden owner of runtime behavior.

### The Appeal of a Corporate Framework

A corporate framework can make the common path very easy.

A service may only need:

```csharp
builder.Services.AddCompanyPlatform(configuration);

var app = builder.Build();

app.UseCompanyPlatform();

app.Run();
```

The framework may configure:

- logging,

- OpenTelemetry,

- Grafana exporters,

- health checks,

- authentication,

- exception handling,

- HTTP resilience,

- databases,

- queues,

- cloud integrations.

It may also impose an application structure:

```text
Commands/
Queries/
Handlers/
Repositories/
ExternalServices/
Infrastructure/
```

It may define:

- command and query handlers,

- wrappers for document databases,

- special handlers for REST calls,

- result types,

- validation pipelines,

- base classes,

- conventions for dependency injection.

This approach offers real benefits:

- fast creation of new services,

- consistent code structure,

- easier onboarding,

- fewer architectural discussions,

- predictable locations for code,

- reduced boilerplate,

- a clear happy path.

Many developers may reasonably prefer this model because it lets them concentrate on business functionality.

### The Deferred Cost of a Framework

The cost of such convenience is often delayed.

A framework can gradually become the hidden owner of the application.

- application startup no longer explains how the service works,

- middleware registration and ordering are hidden,

- runtime policy is buried inside extension methods,

- framework types spread through business code,

- every integration receives a dedicated abstraction,

- uncommon scenarios require special flags or workarounds,

- consumers depend on features they do not use,

- the package introduces a large dependency graph,

- the framework becomes difficult to update,

- ownership becomes unclear,

- teams are afraid to change it,

- the framework eventually stops evolving.

In ASP.NET Core, middleware execution is strictly order-dependent—routing must precede authentication, authentication must precede authorization, and exception handlers must wrap the entire pipeline. When a monolithic platform method registers these internally, teams cannot inject custom middleware between framework layers or adjust the pipeline without cracking open or bypassing the framework entirely.

The framework may have started as a useful paved road but gradually become a closed architectural model.

The common path remains easy.

Anything outside the common path becomes disproportionately difficult.

## Do Not Let the Framework Penetrate the Entire Application

Infrastructure packages should integrate at application boundaries.

They should not force the whole codebase to use framework-specific types.

Warning signs include:

- all handlers inherit from a framework base class,

- domain models implement package interfaces,

- every result uses a corporate result wrapper,

- folder structure is dictated by the package,

- the package owns the mediator abstraction,

- business logic depends directly on infrastructure types,

- removing the package requires rewriting the application.

A replaceable framework should mainly appear in:

- startup configuration,

- infrastructure adapters,

- API boundaries,

- integration layers.

Business logic should remain independent.

---

### Avoid Framework Types in Business Code

Infrastructure modules should integrate at application boundaries.

They should not define the internal language of the whole application.

- every handler inherits from a framework base class,

- every operation returns a corporate result wrapper,

- domain models implement package interfaces,

- REST calls require special framework handlers,

- database access must use a generic framework repository,

- application structure is enforced through runtime types,

- removing the framework requires rewriting business logic.

For example, this may be unnecessary:

```csharp
public sealed class CustomerQueryHandler
    : ExternalRestQueryHandlerBase<CustomerQuery, CustomerResponse>
{
}
```

A simpler and more explicit design may be:

```csharp
public sealed class CustomerClient
{
    public Task<Customer> GetCustomerAsync(
        CustomerId id,
        CancellationToken cancellationToken);
}
```

The important architectural requirement is that external communication is isolated and visible.

It does not necessarily require a new category of framework handler.

Similarly, a generic document repository may hide important database capabilities and eventually become a limited reimplementation of the native client.

The organization should standardize the required behavior and operational properties without unnecessarily replacing every underlying technology with a corporate abstraction.

## Mechanism and Policy Should Be Separated

A package may provide a mechanism.

The application should explicitly choose the policy.

For example, the package may provide retry support:

```csharp
services.AddRequestRetry(options =>
{
    options.MaxAttempts = 3;
    options.Timeout = TimeSpan.FromSeconds(5);
    options.RetryNonIdempotentRequests = false;
});
```

Avoid hiding policy inside:

```csharp
services.AddCompanyDefaults();
```

where the application cannot easily see:

- how many retries are configured,

- which failures are retried,

- which requests are considered safe,

- what timeout is used,

- whether request bodies are logged,

- which exporters are enabled.

The framework may provide safe defaults, but important operational policies should remain visible.

Mechanism is the generic capability—such as an interceptor executing exponential backoff with full jitter, or a filter measuring request durations. Policy is the operational trade-off decided by service owners: financial settlement calls must never retry automatically on timeouts, while idempotent catalog queries can safely retry three times with tight deadlines. Hardcoding operational policies into a shared package removes critical runtime tuning from the engineers who own the production on-call rotation.

---

### Distinguish Mechanism from Policy

Shared packages may provide mechanisms.

Applications should explicitly select important policies.

For example, a package may provide retry support:

```csharp
services.AddCompanyHttpResilience(options =>
{
    options.MaxAttempts = 3;
    options.Timeout = TimeSpan.FromSeconds(5);
    options.RetryNonIdempotentRequests = false;
});
```

Avoid hiding these decisions behind:

```csharp
services.AddCompanyDefaults();
```

Operational decisions such as the following should remain visible:

- timeout duration,

- retry count,

- which operations may be retried,

- whether request bodies are logged,

- which exporters are enabled,

- how health checks are classified,

- which failures affect readiness.

A framework does not remove such decisions.

It only moves them somewhere else.

If they are important for the behavior of the service, they should remain inspectable.

## Practical Principles

A well-designed internal NuGet ecosystem should follow these principles:

- Packages should be small and focused.

- Dependency trees should be intentionally limited.

- Applications should explicitly compose the framework.

- Middleware should be added explicitly.

- Runtime configuration should remain visible.

- Important operational policies should be local and readable.

- Components should be replaceable.

- Flexibility should come from composition rather than many flags.

- Consumer-specific features should not automatically enter the shared core.

- Public APIs should remain small.

- Infrastructure types should not spread through the domain.

- Core packages, integrations, and testing utilities should be separated.

- Small repeated code may be better documented and copied than packaged (see [[Internal NuGet Packages vs Agent-Generated Code]]).

- Conformance tests may enforce standards without enforcing one implementation (see [[Executable Architecture Tests for Coding Agent Guardrails]] and [[Standardizing Service Infrastructure with Reusable Blocks]]).

---

## Mental Model

Internal NuGet packages may form a framework.

The framework itself is not the problem.

The real question is who owns the composition.

A healthy model is:

> The framework provides the building blocks.
> The application selects, configures, orders, and composes them.

An unhealthy model is:

> The framework takes over application startup and silently decides how the application behaves.

The preferred design can be summarized as:

> Build a framework that is composed by the application, not a framework that configures the application on its behalf.

And the final decision rule is:

> Use a shared package when it makes the system easier to understand, change, and operate.
> Use local code, documentation, and tests when the package would hide more than it simplifies.

## Related notes

- **[[Internal NuGet Packages vs Agent-Generated Code]]** — Why cheap generation changes the trade-off between packaging common code and letting agents generate it locally.
- **[[Standardizing Service Infrastructure with Reusable Blocks]]** — Providing common infrastructure foundations without imposing opinionated application runtime coupling.
- **[[Hidden Abstractions May Become More Expensive in Agent-Maintained Code]]** — The hidden operational cost of complex shared frameworks in agent workflows.
- **[[Executable Architecture Tests for Coding Agent Guardrails]]** — Verifying package dependency boundaries and consumer contracts with automated architecture tests.
