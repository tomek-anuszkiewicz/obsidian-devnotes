---
title: Standardizing Service Infrastructure with Reusable Blocks
tags:
  - infrastructure
  - microservices
  - platform-engineering
  - software-architecture
  - cloud
  - standardization
aliases:
  - Service Infrastructure Building Blocks
  - Reusable Service Platform Blocks
---

A service platform needs both reusable implementations and consistent operational behavior. A team can adopt the standard packages and still emit unusable telemetry; another can implement a capability differently while satisfying the same operational contract.

This article focuses on the organizational platform: supported building blocks, explicit composition, ownership, escape paths, and enforcement mechanisms. [[Operational Conformance Tests for Service Platforms]] turns its runtime promises into tests of a deployed service. [[Designing Internal NuGet Packages as an Explicit, Composable Framework]] develops dependency boundaries, replaceability, middleware visibility, and the cost of packaging shared code. The platform should explain which behavior is mandatory and who maintains the implementation and migration path.

## Context

As an organization, we repeatedly solve the same technical problems across many services.

Examples include:

- application startup and dependency injection,

- structured logging,

- distributed tracing,

- metrics,

- health checks,

- authentication,

- secrets management,

- database connectivity,

- messaging and queues,

- outbound HTTP communication,

- retries and timeouts,

- Grafana dashboards,

- deployment configuration.

At the same time, some of these capabilities should not merely look similar.

They should work consistently across the entire organization.

For example, every service should:

- emit logs in a searchable and predictable format,

- expose meaningful health checks,

- propagate trace and correlation identifiers,

- publish standard operational metrics,

- integrate with common dashboards,

- support consistent alerting,

- be diagnosable using the same operational tools.

This creates a legitimate need for standardization.

The key architectural question is:

> Should the organization build one framework in which all services are developed, or should it provide smaller building blocks that each service composes explicitly?

---

## The Real Problem We Are Trying to Solve

There are two different problems that are often mixed together.

### Repeated implementation

Teams repeatedly write similar code for:

- logging setup,

- telemetry registration,

- HTTP clients,

- health checks,

- database configuration,

- queue consumers,

- middleware,

- error handling.

This creates duplication and inconsistent implementations.

### Required operational consistency

The organization also needs guarantees that every deployed service behaves correctly as part of the platform.

For example:

- logs contain the required fields,

- traces cross service boundaries,

- metrics use common names and labels,

- health endpoints have consistent semantics,

- standard Grafana dashboards work,

- alerts can be defined centrally,

- retry and timeout behavior is observable,

- deployment metadata is attached to telemetry.

The first problem is about reuse.

The second problem is about conformance.

A shared runtime framework is only one possible solution to both problems.

---

## A Framework Is Not Inherently Bad

The problem is not that internal NuGet packages collectively form a framework.

A framework can be useful when it provides:

- stable capabilities,

- sensible defaults,

- tested integrations,

- a consistent developer experience,

- safe infrastructure mechanisms.

The important question is:

> Who owns the final composition of the application?

A healthy framework is composed by the application.

An unhealthy framework configures the application on its behalf.

---

## Prefer Explicit Composition

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

---

## Provide Building Blocks, Not One Mandatory Application Model

A better organizational approach is usually to provide a catalog of supported components.

For example:

```text
Company.Observability.Core
Company.Observability.Grafana
Company.Observability.AzureMonitor

Company.Messaging.Abstractions
Company.Messaging.AzureServiceBus
Company.Messaging.Kafka

Company.Persistence.Postgres
Company.Persistence.SqlServer
Company.Persistence.DocumentDatabase

Company.Security.Authentication
Company.Security.Authorization

Company.Http.Resilience
Company.HealthChecks
```

A service chooses and composes only the modules it needs.

For example:

```csharp
services.AddCompanyObservability();
services.AddGrafanaExporter();

services.AddCompanyMessaging();
services.AddAzureServiceBus();

services.AddPostgresPersistence();
```

Another service may choose Kafka, Azure Monitor, or a document database.

Both can remain compliant with the same organizational requirements.

The framework then becomes the result of composition rather than a mandatory starting point imposed on all services.

---

## Multiple Enforcement Mechanisms

A complete internal platform should not rely on one giant runtime package.

Different requirements are better handled by different mechanisms.

### Runtime NuGet packages

Use for shared code that must execute inside the service:

- telemetry integrations,

- authentication components,

- protocol clients,

- messaging adapters,

- health-check implementations.

### Project templates

Use `dotnet new` or starter repositories to provide:

- recommended project structure,

- initial configuration,

- Dockerfiles,

- deployment manifests,

- example tests,

- recommended package selection.

Templates provide a starting point, not permanent governance.

### Roslyn analyzers

Use for source-level rules:

- forbidden dependencies,

- architectural boundaries,

- unsafe APIs,

- missing cancellation tokens,

- incorrect logging patterns.

### Conformance tests

Use for observable behavior:

- logs,

- metrics,

- traces,

- health checks,

- error contracts,

- dashboard compatibility.

### Build tooling

Use `Directory.Build.props`, custom project SDKs, or MSBuild targets for:

- compiler settings,

- analyzers,

- warnings,

- package policies,

- build validation.

### Infrastructure modules

Use Terraform, Helm, deployment templates, or pipeline components for:

- cloud resources,

- collectors,

- Grafana dashboards,

- queues,

- databases,

- secrets,

- deployment conventions.

### Documentation and agent instructions

Use README files, implementation recipes, examples, and `AGENTS.md` for:

- architectural intent,

- supported patterns,

- composition guidance,

- migration instructions,

- code-generation constraints.

The platform is therefore a combination of code, tests, tooling, infrastructure, and documentation.

It should not be reduced to one `Company.Framework` package.

---

## Ownership Is Mandatory

A mandatory organizational framework cannot be safely left unmaintained.

A shared module should have:

- a clear owner,

- supported use cases,

- a versioning policy,

- a changelog,

- consumer-facing tests,

- a sample application,

- a migration strategy,

- a deprecation process,

- compatibility guarantees,

- usage feedback from real services.

A platform team must also dogfood its own building blocks by maintaining production services on the same paved road. If the team maintaining the packages does not experience the friction of package upgrades, breaking dependency trees, and runtime bugs firsthand, the platform inevitably drifts away from practical engineering realities.

An unmaintained but mandatory framework is one of the worst outcomes.

The organization loses:

- the flexibility of local code,

- the safety of an actively maintained platform,

- the ability to adopt new infrastructure,

- confidence in upgrades.

If the organization cannot commit to long-term ownership, it should prefer smaller packages, templates, documentation, and externally verifiable contracts.

---

## Recommended Model

The organization should provide a **service platform**, not only a mandatory runtime framework.

The platform should include:

### Supported building blocks

- logging,

- tracing,

- metrics,

- health checks,

- authentication,

- messaging,

- persistence,

- HTTP resilience,

- cloud integrations.

### A recommended paved road

- project templates,

- reference services,

- default configurations,

- standard dashboards,

- deployment modules.

### Explicit application composition

Each service selects and configures its modules visibly.

### Operational conformance

Every service proves through tests that it integrates correctly with:

- logging infrastructure,

- tracing infrastructure,

- metrics infrastructure,

- health monitoring,

- dashboards,

- alerts.

### Controlled escape paths

A team may replace a standard component when necessary, provided that the service continues to satisfy the platform contract.

---

## Decision Questions

Before adding a capability to a corporate framework, ask:

1. Is this behavior genuinely required by many services?

2. Do services need the same implementation or only the same result?

3. Can this be provided as a small independent module?

4. Does the package introduce unrelated dependencies?

5. Will the application configure it explicitly?

6. Can the module be replaced independently?

7. Does it leak framework types into business code?

8. Could documentation and local generated code be simpler?

9. Can the requirement be enforced through conformance tests?

10. Does the standard Grafana dashboard depend on this behavior?

11. Who will maintain the capability?

12. How will services migrate to future versions?

13. Can a service leave the paved road without fighting the framework?

14. Does the abstraction simplify the system or merely hide it?

---

## Mental Model

Organizations need both reuse and consistency.

However, consistency does not require every service to inherit the same complete application framework.

A healthier model is:

> The organization provides supported building blocks, a recommended composition, and executable operational standards.

The service remains responsible for:

- selecting the modules,

- configuring them,

- ordering middleware,

- owning its application structure,

- making important policies visible.

The platform remains responsible for:

- shared mechanisms,

- safe defaults,

- supported integrations,

- standard telemetry contracts,

- default dashboards,

- conformance tests,

- long-term maintenance.

The central contract should be:

> Every service must be operationally compatible with the platform.

Not necessarily:

> Every service must use exactly the same implementation.

The preferred outcome is a paved road rather than a walled garden:

> Make the correct path easy, visible, tested, and well supported—without hiding the application or making alternative implementations impossible.

(See [[Designing Internal NuGet Packages as an Explicit, Composable Framework]] and [[Scaling a Modular Monolith with Local-or-Remote Module Execution]]).

## Related Notes

- [[Designing Internal NuGet Packages as an Explicit, Composable Framework]] — Constructing composable infrastructure building blocks instead of magic wrappers.
- [[Scaling a Modular Monolith with Local-or-Remote Module Execution]] — Standardizing communication and worker execution across module boundaries.
- [[Remote Service Calls — Errors, Resilience, and Observability]] — Shared communication mechanisms with explicit retry, timeout, and telemetry policy.
- [[OpenTelemetry — Architecture, Signals, and Collector]] — Standard telemetry collection and logging infrastructure across services.
