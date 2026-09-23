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

## The Appeal of a Corporate Framework

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

---

## The Deferred Cost of a Framework

The cost of such convenience is often delayed.

A framework can gradually become the hidden owner of the application.

Typical symptoms include:

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

## Modularity Means Replaceability

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
    

For example:

```csharp
services.AddCompanyTelemetry();
```

should be replaceable with:

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

---

## Avoid Framework Types in Business Code

Infrastructure modules should integrate at application boundaries.

They should not define the internal language of the whole application.

Warning signs include:

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

---

## Distinguish Mechanism from Policy

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

---

## Standardize Outcomes, Not Necessarily Implementations

The central organizational contract should not always be:

> Every service must use the same NuGet package.

A more durable contract is:

> Every service must demonstrate the required runtime behavior.

For example, the organization may require that every service:

- emits structured logs,
    
- provides a stable `service.name`,
    
- propagates correlation and trace identifiers,
    
- exports standard request metrics,
    
- exposes liveness and readiness endpoints,
    
- produces traces for inbound and outbound calls,
    
- exposes queue and database telemetry,
    
- works with standard Grafana dashboards,
    
- produces the data required by standard alerts.
    

One service may satisfy this contract using internal packages.

Another may use OpenTelemetry directly.

Both should be acceptable when they produce the same compliant operational result.

This preserves replaceability while maintaining platform consistency.

---

## Operational Conformance Tests

Every service should be tested as a running system for compliance with the operational platform.

This is separate from business end-to-end testing.

### Business E2E tests

These validate a business workflow:

```text
Create order
→ reserve inventory
→ publish event
→ return confirmation
```

### Operational E2E tests

These validate integration with the platform:

```text
Request
→ structured log
→ metric
→ trace
→ dashboard-compatible labels
```

A service can behave correctly from a business perspective while being operationally invisible.

It can also emit telemetry correctly while implementing business behavior incorrectly.

Both kinds of testing are necessary.

---

## What Operational E2E Tests Should Validate

An operational certification suite may verify that:

### Logging

- logs are actually emitted,
    
- logs are structured,
    
- required fields are present,
    
- `service.name` is correct,
    
- environment and deployment metadata are present,
    
- correlation ID is propagated,
    
- trace ID is included,
    
- errors produce appropriate log entries,
    
- secrets and sensitive values are not logged.
    

### Tracing

- inbound HTTP requests create spans,
    
- outbound REST calls create child spans,
    
- database calls are traced,
    
- queue publication and consumption are traced,
    
- trace context propagates across service boundaries,
    
- spans contain standard attributes.
    

### Metrics

- request count is exported,
    
- error count is exported,
    
- request duration is available,
    
- dependency latency is available,
    
- queue metrics are available,
    
- retries and timeouts are visible,
    
- metric names and labels match platform conventions.
    

### Health checks

- liveness and readiness are separate,
    
- readiness reflects required dependencies,
    
- temporary dependency failures have the expected effect,
    
- health endpoints use a stable response contract,
    
- health checks do not expose sensitive details.
    

### Grafana integration

- the service appears in standard dashboards,
    
- dashboard queries return data,
    
- labels use expected names,
    
- required panels are populated,
    
- common alerts can evaluate the service,
    
- a metric rename does not silently break dashboards.
    

### Runtime behavior

- retry policies behave as declared,
    
- timeouts are enforced,
    
- queue failures are observable,
    
- dead-letter behavior is measurable,
    
- deployment information is attached to telemetry.
    

---

## Test the Result, Not the Library Choice

A conformance test should not require a particular implementation type.

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

For example, a conformance test for outbound HTTP resilience should spin up the application in a test harness (such as `WebApplicationFactory`), mock the downstream dependency with WireMock to return transient errors, and verify the resulting retry behavior through external network observations rather than inspecting dependency injection registrations:

```csharp
[Fact]
public async Task OutboundClient_ShouldRetryThreeTimesOnTransientHttp503()
{
    var downstreamMock = WireMockServer.Start();
    downstreamMock
        .Given(Request.Create().WithPath("/api/v1/resource"))
        .InScenario("TransientRetry")
        .WillReturn(Response.Create().WithStatusCode(503))
        .SetNextScenarioState("FirstRetry");

    downstreamMock
        .Given(Request.Create().WithPath("/api/v1/resource"))
        .InScenario("TransientRetry")
        .WhenStateIs("FirstRetry")
        .WillReturn(Response.Create().WithStatusCode(503))
        .SetNextScenarioState("SecondRetry");

    downstreamMock
        .Given(Request.Create().WithPath("/api/v1/resource"))
        .InScenario("TransientRetry")
        .WhenStateIs("SecondRetry")
        .WillReturn(Response.Create().WithStatusCode(200).WithBody("OK"));

    var client = factory.CreateClient();

    var response = await client.GetAsync("/proxy-call");

    Assert.Equal(HttpStatusCode.OK, response.StatusCode);
    Assert.Equal(3, downstreamMock.LogEntries.Count());
}
```

Bad requirement:

```text
The service must use Serilog.
```

Better requirement:

```text
The service must emit structured logs compatible with the platform schema.
```

Bad requirement:

```text
The service must use Company.Telemetry.
```

Better requirement:

```text
The service must export traces and metrics using the required names, labels, and propagation rules.
```

This lets teams replace implementation details without losing operational guarantees.

---

## Default Dashboards Are Part of the Contract

Standard Grafana dashboards are not only documentation or convenience.

They are consumers of the telemetry contract.

A shared dashboard may expect labels such as:

```text
service.name=orders
deployment.environment=production
http.request.method=GET
http.response.status_code=200
```

If individual services publish inconsistent labels such as:

```text
application=orders-api
```

or:

```text
service=orders
```

the central dashboard becomes a collection of exceptions.

Therefore, dashboard compatibility should be tested.

A reliable way to enforce this in CI is to spin up the service in a test harness, drive synthetic load, export telemetry to an ephemeral Prometheus or Loki container, and execute the actual dashboard PromQL queries to assert that every panel returns data. If a metric rename or missing label breaks a query or alert expression, the build fails before reaching staging.

Dashboards and alerts should also be treated as code:

- versioned,
    
- reviewed,
    
- tested,
    
- deployed through automation,
    
- validated against test services.
    

A service is not fully compliant merely because it emits some metrics.

It should emit metrics that are usable by the supported platform tooling.

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

## When Copy-Paste Is Better

Not every repeated solution should become a runtime dependency.

For small and understandable patterns, the organization may provide:

```text
/docs/patterns/external-http-client.md
/examples/external-http-client/
```

The pattern can explain:

- the required behavior,
    
- timeout and retry rules,
    
- telemetry requirements,
    
- important structural invariants,
    
- expected tests,
    
- which parts may be adapted.
    

The code can be copied into the service and become locally owned.

This may be better when:

- the code is small,
    
- local customization is expected,
    
- implementation visibility is valuable,
    
- one exact central implementation is not required,
    
- a package would hide more than it simplifies.
    

An agent can generate the local implementation from the documented pattern and verify it against conformance tests.

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
```
