---
title: "Evolving and Maintaining Internal NuGet Packages"
tags:
  - nuget
  - dotnet
  - package-management
  - maintainability
  - software-architecture
aliases:
  - "Internal Package Ownership and Evolution"
  - "Maintaining Shared NuGet Contracts"
  - "Replaceability and Consumer Variation in Shared Libraries"
  - "The Frozen Package Problem"
---

A package used by several services receives a new integration request. Adding a dependency or an option is easy; keeping every consumer upgradeable and the component safe to replace is the longer-lived problem.

The package needs a bounded responsibility, a small contract, understood dependencies, and someone who owns compatibility and migration. Consumer differences should reveal where an integration belongs instead of continually expanding one shared abstraction. Tests need to exercise the package from the consuming application's side.

The sections below connect those design choices with operational ownership and the risk of a package becoming too dangerous to change. [[Designing Internal NuGet Packages as an Explicit, Composable Framework]] develops application-owned composition. [[Internal NuGet Packages vs Agent-Generated Code]] asks the earlier question of whether a shared binary implementation is the right mechanism at all.

## Keep Dependency Trees Small

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

Pulling in broad transitive dependencies also triggers diamond dependency hell across an organization. When an internal package drags in a heavy JSON serializer, database driver, or cloud SDK, two unrelated libraries referencing incompatible major versions of that transitive dependency will break downstream builds and freeze upgrades across dozens of consumer repositories.

---

## Modularity Should Enable Replacement

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

### Modularity Means Replaceability

Splitting one framework into many NuGet packages is not enough.

The modules must be genuinely independent.

A useful module should have:

- one clear responsibility,

- a small public API,

- a limited dependency tree,

- explicit registration,

- explicit configuration,

- independent tests,

- a clear operational contract,

- the ability to be removed or replaced.

```csharp
services.AddCompanyTelemetry();
```

```csharp
services
    .AddOpenTelemetry()
    .WithTracing(...)
    .WithMetrics(...);
```

without rewriting:

- business logic,

- handlers,

- endpoints,

- domain models,

- unrelated infrastructure.

Replaceability is often more valuable than exposing dozens of configuration flags.

Instead of creating one module that supports every possible provider through options:

```csharp
services.AddCompanyLogging(options =>
{
    options.UseSerilog = true;
    options.UseGrafana = true;
    options.UseAzureMonitor = false;
    options.UseCustomFormatter = true;
});
```

prefer composition:

```csharp
services.AddCompanyLoggingCore();
services.AddSerilogLogging();
services.AddGrafanaExporter();
services.AddCompanyLogEnrichment();
```

Flexibility should come from replacing and composing modules, not from continuously expanding one configuration object.

## Prefer Replaceability Over Endless Configuration

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

## Avoid the Multi-Consumer Feature Trap

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

## Avoid the Package Nobody Wants to Change

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

## Small Public API Surface

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

## Separate Core, Integrations, and Testing

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

## Decision Questions

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

Treat a new consumer requirement as a change to a maintained contract and dependency graph. Review the impact on existing consumers, the independent replacement path, the tests that make upgrades safe, and the owner who will support migration and deprecation.

## Related Notes

- [[Designing Internal NuGet Packages as an Explicit, Composable Framework]] — Visible startup, middleware, policies, and application boundaries.
- [[Internal NuGet Packages vs Agent-Generated Code]] — Choosing a package, generated local code, or a service boundary.
- [[Operational Conformance Tests for Service Platforms]] — Checking shared operational behavior without requiring one runtime implementation.
