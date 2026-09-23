---
title: Designing Internal NuGet Packages as an Explicit, Composable Framework
tags:
  - dotnet
  - nuget
  - software-architecture
  - framework-design
  - modular-design
  - maintainability
aliases:
  - Internal NuGet Framework Architecture
  - Explicit Composable NuGet Packages
---

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

---

## 1. Keep Dependency Trees Small

An internal package should not reference many unrelated packages.

Adding one package should not silently bring in:

- multiple cloud SDKs,
    
- logging providers,
    
- telemetry exporters,
    
- retry libraries,
    
- serializers,
    
- database clients,
    
- messaging frameworks,
    
- health-check packages,
    
- configuration providers.
    

A package should depend only on what is required for its primary responsibility.

Instead of one large package:

```text
Company.Platform
```

prefer smaller packages:

```text
Company.Logging.Core
Company.Logging.Serilog
Company.Telemetry.Core
Company.Telemetry.OpenTelemetry
Company.Telemetry.Grafana
Company.Telemetry.AzureMonitor
Company.Authentication
Company.Azure.KeyVault
```

This gives applications control over which components and transitive dependencies they actually use.

Small dependency trees provide:

- fewer version conflicts,
    
- easier upgrades,
    
- lower security exposure,
    
- easier package removal,
    
- clearer ownership,
    
- better understanding of the runtime composition.
    

---

## 2. Prefer Configuration by Composition

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

## 3. Middleware Must Be Explicit

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

---

## 4. A Framework Is Acceptable When the Application Composes It

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

## 5. Modularity Should Enable Replacement

Each framework component should be replaceable without rebuilding the entire application.

For example, an application may initially use:

```csharp
services.AddCompanyTelemetry();
```

Later, it should be possible to replace it with:

```csharp
services
    .AddOpenTelemetry()
    .WithTracing(...)
    .WithMetrics(...);
```

Similarly:

```csharp
services.AddCompanySecrets();
```

should be replaceable with:

```csharp
services.AddAzureKeyVault(...);
```

without changing:

- domain logic,
    
- handlers,
    
- endpoints,
    
- business services,
    
- unrelated infrastructure modules.
    

A module is properly isolated when it can be removed or replaced at the application boundary.

---

## 6. Prefer Replaceability Over Endless Configuration

A package should be configurable within the scope of its responsibility.

However, configurability should not mean supporting every possible scenario through dozens of flags.

A problematic design may look like:

```csharp
services.AddCompanyLogging(options =>
{
    options.UseSerilog = true;
    options.UseOpenTelemetry = false;
    options.UseGrafana = true;
    options.UseAzureMonitor = false;
    options.UseCustomFormatter = true;
    options.IncludeHeaders = false;
    options.IncludeBodies = true;
});
```

This often indicates that too many independent concerns were placed inside one module.

A better design is composition:

```csharp
services.AddCompanyLoggingCore();
services.AddSerilogLogging();
services.AddGrafanaExporter();
services.AddCompanyLogEnrichment();
```

This gives flexibility through replaceable components rather than one large configuration object.

A useful distinction is:

### Configurability

The component can change some of its behavior.

### Replaceability

The component can be removed and replaced with another implementation.

Replaceability is often more valuable than a large number of configuration switches.

---

## 7. Avoid the Multi-Consumer Feature Trap

A shared package often starts with one clear purpose.

Then different teams request different behavior:

- one team needs Azure integration,
    
- another uses AWS,
    
- another needs Kafka,
    
- another requires a custom serializer,
    
- another needs a special retry policy,
    
- another cannot use the standard authentication setup.
    

The package gradually accumulates:

- flags,
    
- callbacks,
    
- optional dependencies,
    
- provider factories,
    
- special cases,
    
- environment-specific branches.
    

This is often a sign that the package is sharing the wrong abstraction level.

A better response may be:

- keep a small common core,
    
- move integrations to separate packages,
    
- let applications compose the required modules,
    
- keep consumer-specific behavior local.
    

A useful rule is:

> When consumers require fundamentally different behavior, do not keep extending one shared package. Reconsider the abstraction boundary.

---

## 8. Avoid the Package Nobody Wants to Change

A complex internal package can become organizationally frozen.

Typical symptoms include:

- many unknown consumers,
    
- incomplete test coverage,
    
- unclear ownership,
    
- hidden side effects,
    
- undocumented configuration,
    
- many compatibility assumptions,
    
- no safe migration strategy,
    
- fear of breaking unrelated applications.
    

This creates a paradox:

> The package was created to centralize change, but it becomes too risky to change centrally.

A maintainable package should have:

- a clear owner,
    
- a narrowly defined responsibility,
    
- semantic versioning,
    
- a changelog,
    
- consumer-facing integration tests,
    
- a sample application,
    
- a migration path,
    
- a deprecation policy,
    
- documented compatibility guarantees.
    

Tests should validate the package from the perspective of a consuming application, not only through isolated unit tests of internal classes.

---

## 9. Small Public API Surface

A package should expose the smallest practical public API.

Prefer:

- a few stable interfaces,
    
- a few extension methods,
    
- explicit options,
    
- well-defined result types.
    

Keep implementation details internal.

A small public API:

- reduces coupling,
    
- makes versioning easier,
    
- prevents accidental dependencies,
    
- limits the number of behaviors that must remain compatible,
    
- makes the package easier to replace.
    

A package becomes difficult to evolve when consumers depend on many internal types, base classes, helper classes, and implementation details.

---

## 10. Do Not Let the Framework Penetrate the Entire Application

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

## 11. Separate Core, Integrations, and Testing

Large packages should be split by responsibility.

For example:

```text
Company.Telemetry.Abstractions
Company.Telemetry.Core
Company.Telemetry.AspNetCore
Company.Telemetry.Grafana
Company.Telemetry.AzureMonitor
Company.Telemetry.Testing
```

This lets consumers reference only what they need.

It also separates:

- stable contracts,
    
- runtime implementation,
    
- framework integration,
    
- provider-specific code,
    
- test utilities.
    

This structure limits transitive dependencies and allows components to evolve independently.

---

## 12. README and Copy-Paste Can Be Better Than a Package

Not every repeated implementation should become a NuGet package.

For small, understandable, application-specific code, a better solution may be:

```text
/docs/patterns/request-auditing.md
/examples/request-auditing/
```

The documentation can describe:

- the required behavior,
    
- the intended structure,
    
- important invariants,
    
- why ordering matters,
    
- which parts may be changed,
    
- which tests must pass.
    

The code can then be copied into the application and become locally owned.

This approach has several advantages:

- the complete flow is visible,
    
- there is no runtime dependency,
    
- there are no package-version conflicts,
    
- the implementation can be adapted locally,
    
- agents can inspect and modify the code directly,
    
- the application is not coupled to an abstraction that may become obsolete.
    

Copy-paste may be preferable when the code:

- is small,
    
- changes rarely,
    
- is easy to understand,
    
- requires local customization,
    
- does not need one centrally maintained runtime implementation.
    

Instead of writing:

> Do not change this structure.

prefer:

> Preserve the documented invariants unless the specification and conformance tests are intentionally updated.

The goal should be understanding and verifiable constraints, not ritualistic preservation of a copied structure.

---

## 13. Use Conformance Tests Where Shared Behavior Matters

Sometimes applications do not need the same implementation.

They only need the same externally observable behavior.

In that case, an organization may provide a conformance test package instead of a production package.

Examples:

```text
Company.Api.ConformanceTests
Company.Security.ConformanceTests
Company.Observability.ConformanceTests
```

These tests may verify:

- error response format,
    
- correlation identifiers,
    
- required headers,
    
- authorization behavior,
    
- telemetry output,
    
- health endpoints,
    
- retry behavior,
    
- timeout behavior,
    
- audit events.
    

The implementation may remain local and explicit.

The organization controls the contract through tests rather than forcing every application to use the same framework code.

Tests should validate behavior, not internal implementation types.

Bad:

```csharp
service.Should().BeOfType<CompanyRetryHandler>();
```

Better:

```csharp
await AssertRetriesTransientFailureAsync(
    client,
    expectedAttempts: 3);
```

---

## 14. Mechanism and Policy Should Be Separated

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

---

## 15. Decision Questions

Before creating or expanding an internal package, ask:

1. Does the package have one clear responsibility?
    
2. How many transitive dependencies does it introduce?
    
3. Can the application explicitly select every major capability?
    
4. Is middleware registration and ordering visible?
    
5. Can one module be replaced without changing the rest of the application?
    
6. Are we adding another flag because one consumer has a special case?
    
7. Is the shared abstraction genuinely common?
    
8. Is the package easier to understand than equivalent local code?
    
9. Can the package be removed without rewriting business logic?
    
10. Is the public API small and stable?
    
11. Does the package hide operational policy?
    
12. Would README, example code, and conformance tests be simpler?
    
13. Who owns the package?
    
14. How are breaking changes migrated?
    
15. Is the package still safe to change?
    

---

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
    
- Small repeated code may be better documented and copied than packaged.
    
- Conformance tests may enforce standards without enforcing one implementation.
    

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