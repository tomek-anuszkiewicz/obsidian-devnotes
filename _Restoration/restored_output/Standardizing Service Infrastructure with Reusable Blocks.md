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

# Standardizing Service Infrastructure with Reusable Blocks

Organizations repeatedly face the challenge of standardizing service infrastructure across distributed architectures. Whether running independent microservices or deploying modules inside a [[Scaling a Modular Monolith with Local-or-Remote Module Execution|modular monolith]], teams solve the same fundamental problems across dozens of systems:

- Application startup and dependency injection
- Structured logging
- Distributed tracing
- Metrics and telemetry collection
- Health checks and readiness probes
- Authentication and token validation
- Secrets management
- Database connectivity and connection pooling
- Messaging and queue consumers
- Outbound HTTP communication and [[Service-to-Service Communication - How Service A Should Call Service B|service-to-service communication]]
- Retries, timeouts, and circuit breakers
- Grafana dashboards and monitoring
- Deployment configurations and container manifests

At the same time, some of these capabilities cannot merely look similar; they must operate consistently across the entire organization. Every service must:

- Emit logs in a searchable, predictable schema.
- Expose standardized liveness and readiness probes.
- Propagate W3C trace context and correlation identifiers across service boundaries.
- Publish standard operational Golden Signals (latency, traffic, errors, saturation).
- Integrate seamlessly with centralized monitoring dashboards.
- Support organizational alerting thresholds.
- Be diagnosable using standard operational tools.

This creates a legitimate need for standardization. The core architectural question is:

> Should the organization build a single framework in which all services are developed, or should it provide smaller, composable building blocks that each service assembles explicitly?

```text
+----------------------------------------------------------------------------------------------------+
|               STANDARDIZED SERVICE PLATFORM: PAVED ROAD VS CORPORATE FRAMEWORK                    |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|   MONOLITHIC FRAMEWORK (Anti-Pattern)              COMPOSABLE PAVED ROAD (Target Architecture)     |
|  +-------------------------------------+          +--------------------------------------------+   |
|  | Single Opaque Wrapper               |          | Application Host (Explicit Composition)    |   |
|  |   builder.Services                  |          |   builder.Services                         |   |
|  |     .AddCompanyPlatform();          |          |     .AddCompanyLogging()                   |   |
|  | (Couples all services to one mega-  |          |     .AddCompanyTracing()                   |   |
|  | dependency graph, leaks base        |          |     .AddCompanyHealthChecks()              |   |
|  | classes, forces lock-step upgrades) |          |     .AddCompanyPostgres();                 |   |
|  +-------------------------------------+          +--------------------------------------------+   |
|                     |                                                   |                          |
|                     v                                                   v                          |
|  +-------------------------------------+          +--------------------------------------------+   |
|  | Rigid Runtime Lock-In               |          | Independent Granular Packages              |   |
|  | Upgrading a telemetry package       |          | Telemetry | Security | Resilience | DB     |   |
|  | breaks database drivers and HTTP    |          | (Decoupled versioning & release cadences)  |   |
|  +-------------------------------------+          +--------------------------------------------+   |
|                     |                                                   |                          |
|                     v                                                   v                          |
|  +-------------------------------------+          +--------------------------------------------+   |
|  | Enforced by Compiler Types          |          | Enforced by Conformance Test Suites        |   |
|  | "Must inherit from BaseHandler"     |          | Black-box verification of W3C, OTLP, & HTTP|   |
|  +-------------------------------------+          +--------------------------------------------+   |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

---

## The Real Problem We Are Trying to Solve

Standardization initiatives often stall because two distinct engineering problems get conflated into one:

### 1. Repeated Implementation (Code Reuse)
Teams write similar boilerplate across repositories: setting up logging sinks, configuring [[OpenTelemetry as the Runtime Truth for Autonomous Agents]] pipelines, establishing HTTP client factories, wiring health checks, configuring database connection strings, binding queue consumers, and standardizing exception-handling middleware. This duplication leads to divergent implementations and wasted effort.

### 2. Required Operational Consistency (Platform Conformance)
The organization requires guarantees that every deployed service functions correctly as a node in the platform. Infrastructure operators need logs with uniform fields, traces that traverse network hops without losing parent context, metric names and labels that match centralized dashboards, predictable health-check status codes, and uniform telemetry metadata indicating environment, region, and commit SHA.

The first problem is about **reuse**. The second problem is about **conformance**. 

A shared, monolithic runtime framework is only one possible solution to both problems, and it usually creates more operational debt than it solves.

---

## The Appeal of a Corporate Framework

A corporate framework makes initial greenfield development effortless. A service bootstrap can be as brief as:

```csharp
builder.Services.AddCompanyPlatform(configuration);

var app = builder.Build();

app.UseCompanyPlatform();

app.Run();
```

Behind that single extension method, the framework auto-configures:
- Structured logging sinks
- OpenTelemetry instrumentation and Grafana exporters
- Health check endpoints
- JWT validation and service-to-service authentication
- Global exception handling middleware
- Outbound HTTP resilience policies (Polly)
- Database connections and ORM conventions
- Message broker connections and topologies
- Cloud provider integrations

To maximize consistency, the framework often imposes an application taxonomy:

```text
Commands/
Queries/
Handlers/
Repositories/
ExternalServices/
Infrastructure/
```

It frequently ships opinionated base types:
- Command and query handler interfaces
- Wrappers around document and relational databases
- Specialized handlers for outbound REST communication
- Corporate `Result<T>` and error types
- Request validation pipelines
- Mandatory base classes for entities and domain models
- Scanning conventions for dependency injection

This approach offers undeniable early benefits:
- New services spin up in an afternoon.
- The folder layout and code style look identical across teams.
- Onboarding developers is straightforward because patterns are pre-baked.
- Teams spend less time arguing over boilerplate architecture.
- Boilerplate is eliminated.
- The happy path is well-defined and frictionless.

It is easy to see why engineering leads reach for this model. It lets product engineers focus almost entirely on domain logic.

---

## The Deferred Cost of a Framework

The convenience of a single corporate framework comes with a substantial, deferred cost. Over time, the framework quietly usurps ownership of the application.

Common failure modes include:

- **Startup opacity**: Looking at `Program.cs` no longer reveals how the application actually behaves. Everything is hidden behind magic extension methods.
- **Hidden middleware ordering**: ASP.NET Core middleware pipelines depend heavily on execution order (e.g., routing before authentication, authentication before authorization, exception handling wrapping everything). A framework that bundles middleware into a single call hides this order, making it difficult to inject custom pipeline logic.
- **Buried runtime policies**: Default timeouts, retry counts, connection pool sizes, and circuit breaker thresholds live inside binary dependencies rather than source code.
- **Framework type pollution**: Custom result objects, base classes, and specialized interfaces spread throughout the business layer, making it impossible to migrate or decouple down the road.
- **Leaky wrapper abstractions**: Every external library (EF Core, MassTransit, NServiceBus, Redis) gets wrapped in a corporate-specific interface that exposes only 80% of the underlying library's features, frustrating developers who need advanced capabilities.
- **Feature bloat via configuration flags**: As edge cases emerge, the framework accumulates a sprawling configuration schema to satisfy services that need slightly different behavior.
- **Bloated dependency graphs**: A service that only needs to read from a queue pulls in transitively packaged database drivers, cloud SDKs, and REST libraries.
- **Upgrade paralysis**: Upgrading a minor version of a logging library forces a new release of the framework, which in turn forces a synchronized upgrade across all corporate services.
- **Unclear ownership and abandonment**: Teams become afraid to change the framework because its blast radius covers the entire enterprise. It slowly stagnates, and teams begin hacking around it.

What started as a helpful paved road becomes a rigid walled garden. The standard path is easy; any deviation from it becomes an uphill battle against the framework's internal assumptions.

---

## A Framework Is Not Inherently Bad

The issue is not the existence of shared internal packages. Internal libraries [[Designing Internal Packages as an Explicit, Composable Framework|designed as an explicit, composable framework]] provide real value when they deliver:

- Stable, vetted capabilities
- Sensible, production-tested defaults
- Reliable infrastructure integrations
- A consistent developer experience
- Safe security and resilience patterns

The foundational design question is:

> **Who owns the final composition of the application?**

In a healthy architecture, the **application owns the composition**, importing and assembling libraries as needed. In an unhealthy architecture, the **framework owns the composition**, dictating application lifecycle, structure, and dependencies on its own terms.

---

## Prefer Explicit Composition

Instead of a monolithic catch-all registration:

```csharp
// Anti-pattern: Monolithic, opaque platform registration
builder.Services.AddCompanyPlatform(configuration);
```

Prefer granular, explicit capability modules:

```csharp
// Target: Explicit, modular service composition
builder.Services.AddCompanyLogging();
builder.Services.AddCompanyTracing();
builder.Services.AddCompanyMetrics();
builder.Services.AddGrafanaExporter();
builder.Services.AddCompanyAuthentication();
builder.Services.AddCompanyServiceBus();
builder.Services.AddCompanyPostgres();
```

Keep the middleware pipeline fully visible in application code:

```csharp
// Target: Transparent middleware pipeline
app.UseCompanyCorrelation();
app.UseCompanyExceptionHandling();
app.UseAuthentication();
app.UseAuthorization();
app.UseCompanyRequestLogging();
```

This approach requires more lines of code in `Program.cs`, but that code is not meaningless boilerplate. It is an **executable architecture document**.

By inspecting `Program.cs`, an engineer or an automated agent immediately knows:
- Which infrastructure components are active.
- Which third-party or cloud providers are configured.
- What runtime policies are applied.
- The exact order of middleware execution.
- Which components can be removed, updated, or swapped out without unintended side effects.

The service must remain the master of its own bootstrap process.

---

## Provide Building Blocks, Not One Mandatory Application Model

Platform engineering should focus on maintaining a curated catalog of independent, composable building blocks rather than a monolithic runtime chassis:

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

Each service imports and configures only the modules it requires:

```csharp
// Service A: Relational persistence with Service Bus messaging
services.AddCompanyObservability();
services.AddGrafanaExporter();

services.AddCompanyMessaging();
services.AddAzureServiceBus();

services.AddPostgresPersistence();
```

A different service with different performance or transport needs might configure Kafka and a document store:

```csharp
// Service B: Event-streaming service with Document DB
services.AddCompanyObservability();
services.AddAzureMonitorExporter();

services.AddCompanyMessaging();
services.AddKafka();

services.AddDocumentDbPersistence();
```

Both services satisfy organizational requirements for telemetry, logging, and security, but neither carries dependencies or abstractions it does not need. Standardization emerges through **composition**, not forced inheritance.

---

## Modularity Means Replaceability

Splitting a monolith into twenty NuGet packages achieves nothing if they are tightly coupled behind the scenes. True modularity requires that packages be independently replaceable.

A well-designed platform module exhibits:
- A single, well-defined responsibility.
- A minimal, stable public API surface.
- A lean dependency graph (avoiding transitive dependencies on heavy external SDKs unless strictly necessary).
- Explicit dependency injection registration.
- Strongly typed, validated configuration options.
- Independent test suites that run without platform-wide dependencies.
- A clearly defined operational contract.
- The ability to be swapped out for a standard open-source library without requiring structural rewrites.

For example, a service using the platform's telemetry module:

```csharp
services.AddCompanyTelemetry();
```

should be cleanly replaceable with the raw OpenTelemetry SDK if the team requires specialized instrumentation:

```csharp
services
    .AddOpenTelemetry()
    .WithTracing(tracing => tracing
        .AddSource("CustomSource")
        .AddAspNetCoreInstrumentation()
        .AddOtlpExporter())
    .WithMetrics(metrics => metrics
        .AddMeter("CustomMeter")
        .AddAspNetCoreInstrumentation()
        .AddOtlpExporter());
```

This replacement must not require rewriting:
- Business domain logic
- CQRS handlers or controllers
- Route endpoints
- Domain entities
- Unrelated persistence or messaging infrastructure

Replaceability is almost always better than endlessly expanding a central configuration object with boolean flags:

```csharp
// Anti-pattern: The "God Options" configuration object
services.AddCompanyLogging(options =>
{
    options.UseSerilog = true;
    options.UseGrafana = true;
    options.UseAzureMonitor = false;
    options.UseCustomFormatter = true;
    options.EnableLegacyXmlSchema = false;
});
```

Prefer composition of smaller packages:

```csharp
// Target: Composing single-purpose libraries
services.AddCompanyLoggingCore();
services.AddSerilogLogging();
services.AddGrafanaExporter();
services.AddCompanyLogEnrichment();
```

Flexibility should come from adding, removing, and swapping modules, not from managing an sprawling matrix of configuration flags.

---

## Avoid Framework Types in Business Code

Infrastructure packages should operate at the application boundaries: HTTP adapters, message bus listeners, database contexts, and telemetry sinks. They should not dictate the internal language of the domain model.

Watch out for these red flags:
- Application handlers inheriting from corporate base classes.
- Public service methods forced to return corporate `ServiceResult<T>` wrappers.
- Domain models implementing framework interfaces.
- Outbound REST communication requiring inheritance from proprietary HTTP handlers.
- Database access funneled through an inflexible generic repository base class.
- Directory and class naming structures strictly enforced by reflection-based runtime runners.
- The inability to decouple business logic from the corporate package without a full rewrite.

Consider this inheritance-heavy anti-pattern:

```csharp
// Anti-pattern: Business handler coupled directly to framework base classes
public sealed class CustomerQueryHandler 
    : ExternalRestQueryHandlerBase<CustomerQuery, CustomerResponse>
{
    // Hidden execution life-cycle hooks buried in the base class
}
```

A cleaner, explicit design keeps the boundary clear:

```csharp
// Target: Clean boundary isolation using standard typed clients
public sealed class CustomerClient
{
    private readonly HttpClient _httpClient;

    public CustomerClient(HttpClient httpClient) => _httpClient = httpClient;

    public async Task<Customer> GetCustomerAsync(
        CustomerId id, 
        CancellationToken cancellationToken)
    {
        // Standard, testable HTTP invocation using application-level models
        return await _httpClient.GetFromJsonAsync<Customer>(
            $"/customers/{id}", 
            cancellationToken);
    }
}
```

The architectural requirement is that external communication is visible, isolated, resilient, and observable. That does not require creating a proprietary corporate abstraction over `HttpClient`.

Similarly, wrapping Entity Framework Core or Dapper inside an organizational "Generic Repository" often strips away the underlying library's best features (change tracking control, optimized projections, raw SQL escape hatches) while presenting a leaky abstraction that requires constant maintenance. Standardize the operational behavior, not the language primitives.

---

## Distinguish Mechanism from Policy

Platform packages should provide the **mechanism**. The application should specify the **policy**.

A resilience package should provide the plumbing for retries, timeouts, and circuit breakers, but the service must declare the actual thresholds:

```csharp
// Target: Mechanism provided by platform, policy declared by application
services.AddCompanyHttpResilience(options =>
{
    options.MaxAttempts = 3;
    options.Timeout = TimeSpan.FromSeconds(5);
    options.RetryNonIdempotentRequests = false;
});
```

Avoid sweeping these critical operational decisions behind magic catch-all defaults:

```csharp
// Anti-pattern: Hiding critical operational policy
services.AddCompanyDefaults();
```

An engineer reading the application code must be able to see:
- Timeout durations
- Retry counts and backoff algorithms
- Whether non-idempotent HTTP methods (POST, PATCH) are retried
- Whether sensitive request/response bodies are logged
- Which exporters are active
- How health check dependencies are weighted (critical dependency vs. degraded performance)
- Which downstream failures affect readiness probes

A framework does not eliminate these operational decisions; it merely buries them. When a downstream dependency degrades in production, engineers need these policies clearly visible in source code, not hidden in an external package's default settings.

---

## Standardize Outcomes, Not Necessarily Implementations

The organizational mandate should never be:

> *"Every service must import Company.Framework v4.2.1."*

The durable, resilient platform contract is:

> *"Every service must adhere to the platform's operational contract at runtime."*

Under this model, the organization mandates that every deployed service must:
- Emit structured logs as JSON matching the corporate schema.
- Provide a consistent, stable `service.name` attribute.
- Extract and propagate W3C `traceparent` and `tracestate` headers across boundaries.
- Export standard RED/Golden Signal request metrics.
- Expose `/healthz/live` and `/healthz/ready` endpoints with standard semantic payload structures.
- Trace inbound HTTP calls and downstream persistence/messaging dependencies.
- Emit queue consumer and database client telemetry.
- Supply telemetry attributes compatible with centralized Grafana dashboards.
- Output metrics required to trigger centralized alerts.

One service may satisfy these requirements using the internal `Company.Observability` building blocks. Another service—perhaps written in Go, Rust, or Python, or built by a team with unique performance requirements—can satisfy the exact same contract using native OpenTelemetry and open-source middleware.

Both services are fully compliant platform citizens. This mindset protects the architecture from obsolescence while guaranteeing operational consistency.

---

## Operational Conformance Tests

To verify that services meet the platform contract without dictating their internal implementation, treat operational readiness as a first-class testing discipline. This requires separating business validation from operational validation:

```text
BUSINESS END-TO-END TEST:
Create Order -> Reserve Inventory -> Publish Event -> Return HTTP 201 Created

OPERATIONAL CONFORMANCE TEST:
Trigger Request -> Verify Structured Log Format -> Verify Distributed Trace Propagation
                -> Verify Metric Export -> Verify Dashboard Schema Compatibility
```

A service can process business logic flawlessly while being completely invisible to monitoring systems. Conversely, a service can emit beautiful telemetry while calculating invoices incorrectly. Both aspects require independent automated validation.

---

## What Operational Conformance Tests Must Validate

An automated operational test suite should spin up the service in a test harness (e.g., using `WebApplicationFactory` or Testcontainers) and assert against its external telemetry and runtime behavior:

### 1. Logging
- Logs are emitted to standard output in structured JSON.
- Mandatory fields are present (`timestamp`, `log.level`, `message`, `service.name`, `deployment.environment`).
- Active W3C `trace_id` and `span_id` are automatically correlated into the log context.
- Inbound correlation IDs (e.g., `X-Correlation-ID`) are captured and attached.
- Handled and unhandled exceptions output complete stack traces without leaking connection strings, PII, or authorization credentials.

### 2. Distributed Tracing
- Inbound HTTP requests automatically create an active server span.
- Outbound HTTP requests, database queries, and message publications create child spans linked to the root trace.
- W3C `traceparent` context is injected into outbound transport headers.
- Spans contain mandatory OpenTelemetry semantic convention tags (`http.response.status_code`, `http.request.method`, `server.address`, `db.system`).

### 3. Metrics and Telemetry
- The runtime exposes a scraping endpoint (e.g., `/metrics`) or pushes via OTLP.
- Standard counters and histograms are emitted (`http.server.request.duration`, `http.client.request.duration`).
- Dependency latencies are tagged with the downstream target name.
- Metric labels use expected platform keys without unbound cardinality (avoiding raw user IDs or paths with dynamic IDs in label values).

### 4. Health and Readiness Contracts
- Liveness (`/healthz/live`) and readiness (`/healthz/ready`) endpoints are distinct.
- Readiness checks accurately report the state of critical backing stores (PostgreSQL, Kafka, Redis).
- Transient network drops to downstream dependencies flip readiness checks to unhealthy (503) while keeping liveness healthy (200).
- Health responses output a consistent JSON payload format.

### 5. Centralized Monitoring Compatibility
- Metrics and labels match the queries written in corporate Grafana dashboards.
- A metric rename or label modification fails the test suite before it can break production alerting.
- Alerting rules (e.g., error rate > 1% over 5 minutes) can evaluate the service's test metrics cleanly.

### 6. Runtime Resilience
- Transient 503 errors on outbound calls trigger the configured number of retries before bubbling up.
- Upstream client timeouts cleanly cancel internal downstream database queries via `CancellationToken`.
- Dead-letter queues accurately capture failed messages along with failure reason headers.

---

## Test the Result, Not the Library Choice

Avoid writing tests that verify an internal dependency graph or class structure. Verify the external, black-box runtime behavior instead.

```csharp
// Anti-pattern: Brittle unit test verifying internal framework types
[Fact]
public void ShouldUseCompanyRetryHandler()
{
    var handler = serviceProvider.GetService<HttpMessageHandler>();
    Assert.IsType<CompanyPlatformRetryHandler>(handler); // Coupled to internal types
}
```

Write behavioral assertions instead:

```csharp
// Target: Conformance test verifying observable operational behavior
[Fact]
public async Task OutboundClient_ShouldRetryThreeTimesOnTransientHttp503()
{
    // Arrange: Mock downstream server to fail twice with 503, then return 200 OK
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

    // Act
    var response = await client.GetAsync("/proxy-call");

    // Assert: Black-box verification of resilience mechanism
    Assert.Equal(HttpStatusCode.OK, response.StatusCode);
    Assert.Equal(3, downstreamMock.LogEntries.Count());
}
```

Apply the same philosophy to engineering policies:

- **Do not mandate**: *"Every service must use Serilog via Company.Logging."*
- **Mandate**: *"Every service must emit structured JSON logs to stdout conforming to Platform Schema v2."*

- **Do not mandate**: *"Every service must use Company.Telemetry."*
- **Mandate**: *"Every service must export traces and metrics using standard OTLP endpoints with valid W3C propagation."*

This shift decouples platform guarantees from package implementation details.

---

## Default Dashboards Are Part of the Contract

Centralized Grafana dashboards are not just visualizations; they are active consumers of your services' telemetry contracts.

A standard RED dashboard relies on exact label keys:

```text
service.name="orders-api"
deployment.environment="production"
http.request.method="GET"
http.response.status_code="200"
```

If one service emits `application="orders-api"` while another emits `service="orders"`, or if a team changes `status_code` to `status`, the shared dashboard breaks silently. The central dashboard becomes an unmaintainable collection of regex exceptions.

To prevent this:
- **Treat dashboards and alerts as code**: Version-control dashboard JSON definitions and Prometheus alerting rules alongside platform libraries.
- **Run automated dashboard queries against test data**: Conformance pipelines should spin up services, drive synthetic load, export telemetry to a temporary Prometheus or Loki instance, and run the actual dashboard PromQL queries to assert they return data.
- **Validate telemetry during CI**: Catch breaking label renames during the pull request build, not when an on-call engineer opens a blank dashboard during an outage.

A service is not operationally ready simply because it exports metrics; it is ready when its metrics populate platform dashboards and trigger platform alerts as expected.

---

## Multiple Enforcement Mechanisms

A mature internal platform does not rely solely on a single runtime package to maintain standards. It distributes enforcement across the software development lifecycle:

| Mechanism | Purpose | Scope / Application |
| :--- | :--- | :--- |
| **Runtime Modules** | Shared execution logic inside the process. | Distributed tracing setup, token validation, messaging adapters, health check publishers. |
| **Project Templates** (`dotnet new`) | Initial scaffolding for rapid service bootstrapping. | Base project structure, sample unit/conformance tests, baseline Dockerfiles, CI pipeline manifests. |
| **Roslyn Analyzers / Linters** | Compile-time architectural and safety rules. | Flagging unhandled cancellation tokens, preventing direct `DateTime.Now` calls, banning unauthorized dependencies. |
| **Operational Conformance Tests** | Behavioral verification against running services. | Asserting W3C trace propagation, log schemas, metrics format, HTTP error contract structures. |
| **Centralized Build Policy** (`Directory.Build.props`) | Standardized compiler and toolchain settings. | Enforcing C# language versions, treating warnings as errors, standardizing package vulnerability auditing. |
| **Infrastructure Modules** (Terraform / Helm) | Cloud and platform environment consistency. | Consistent collector daemonsets, pod disruption budgets, ingress rules, standard dashboard provisioning. |
| **Documentation & Agent Rules** (`AGENTS.md`) | Clear guidance for engineers and LLM agents. | Architecture Decision Records (ADRs), composition recipes, approved library alternatives, agent constraints. |

Distributing standards across these layers reduces the pressure on runtime packages to act as corporate gatekeepers.

---

## When Copy-Paste Is Better

Not every repeated pattern needs to be packaged into a shared NuGet library. Packaging small, frequently customized logic into binary dependencies creates unnecessary coupling.

For lightweight, context-dependent patterns, prefer well-documented code recipes:

```text
/docs/patterns/outbound-http-client.md
/examples/outbound-http-client/
```

Document the recipe clearly:
- How to configure the named `HttpClient`.
- Required timeout and retry configurations.
- Telemetry header propagation rules.
- Structural test examples.
- Extension points where teams can safely customize logic.

Teams can copy the reference implementation directly into their codebase, or an AI agent can generate it from the recipe file ([[Internal Shared Packages vs Agent-Generated Code]]).

This approach works best when:
- The code is small (under 100-200 lines).
- Teams frequently need local variations or customizations.
- High transparency into the underlying framework is helpful.
- A centralized package would obscure more than it simplifies.
- The pattern changes infrequently, making package release overhead unnecessary.

Conformance tests will still validate that the copied code conforms to platform requirements, without tying the service to an internal package lifecycle.

---

## Ownership Is Mandatory

A corporate platform without dedicated ownership will decay into technical debt. If an organization mandates the use of internal packages, it must treat those packages as tier-one products.

Every shared module must have:
- **An explicit owning team**: A funded platform or enablement team responsible for triage, feature requests, and maintenance.
- **Strict Semantic Versioning**: No breaking changes within minor or patch releases.
- **Transparent changelogs and migration guides**: Clear documentation on how to upgrade between major versions.
- **Consumer-facing test harnesses**: Pre-built test kits that consuming teams can use to validate their services.
- **Reference sample applications**: Minimal, clean repositories showing recommended composition patterns.
- **A defined deprecation lifecycle**: A clear schedule (e.g., N-2 support) with ample notice before older versions are sunset.
- **Active production dogfooding**: The maintaining team must run services that use the packages in production to experience the upgrade path firsthand.

If the organization cannot resource a dedicated team to maintain internal libraries, **do not build a mandatory framework**. Instead, lean on documentation, project templates, Roslyn analyzers, open-source building blocks, and black-box operational conformance tests.

---

## The Recommended Model: A Paved Road

The most effective architectural approach is to deliver a **Service Platform** rather than an all-or-nothing corporate framework.

```text
+----------------------------------------------------------------------------------------------------+
|                                    THE SERVICE PLATFORM MODEL                                      |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  1. SUPPORTED BUILDING BLOCKS (Modular NuGet Packages)                                             |
|     [ Logging ]   [ Tracing ]   [ Metrics ]   [ Auth ]   [ Messaging ]   [ Persistence ]           |
|                                                                                                    |
|  2. THE RECOMMENDED PAVED ROAD (Golden Paths)                                                      |
|     - dotnet new templates with recommended building blocks pre-wired                              |
|     - Pre-configured Grafana dashboards & Prometheus alerts                                        |
|     - Production-ready CI/CD pipelines & container images                                          |
|                                                                                                    |
|  3. EXPLICIT COMPOSITION (Program.cs)                                                              |
|     - Services explicitly register only the components they need                                   |
|     - Transparent middleware pipeline order                                                        |
|     - Policies (timeouts, retry counts) declared at the service host                               |
|                                                                                                    |
|  4. OPERATIONAL CONFORMANCE SUITE (Black-Box Verification)                                         |
|     - Automated tests verify logging, tracing, metrics, and health probes                          |
|     - Validates platform contract compliance regardless of internal libraries                      |
|                                                                                                    |
|  5. CONTROLLED ESCAPE HATCHES                                                                      |
|     - Services can replace any platform block with native open-source code                         |
|     - Conformance tests ensure the escape hatch still fulfills platform requirements               |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

1. **Provide Composable Building Blocks**: Granular, single-purpose libraries covering logging, metrics, tracing, auth, and persistence.
2. **Build a Paved Road**: Project templates (`dotnet new`) and reference architectures that assemble these blocks into a working application out of the box.
3. **Require Explicit Application Composition**: Keep application bootstrapping transparent. Services explicitly register dependencies and assemble their middleware pipeline in `Program.cs`.
4. **Enforce Standards via Operational Conformance**: Validate services using black-box integration tests that verify logging schemas, metric endpoints, W3C trace propagation, and health check behaviors.
5. **Support Clean Escape Hatches**: Give teams the freedom to swap out a platform building block for a native open-source library or custom implementation, as long as the service passes the operational conformance suite.

---

## Architecture Decision Checklist

Run this checklist before adding a new feature or abstraction to a shared corporate package:

1. **Cross-Cutting Value**: Is this capability genuinely required across multiple distinct services, or is it specific to one domain?
2. **Outcome vs. Implementation**: Do consuming services need an identical code implementation, or do they simply need to emit an identical operational result?
3. **Module Isolation**: Can this feature be shipped as an independent, loosely coupled package, or does it drag in the rest of the corporate ecosystem?
4. **Transitive Dependencies**: Does adding this package introduce heavy, transitive third-party dependencies that consumers might not need?
5. **Explicit Bootstrap**: Will consumers configure this module visibly in their startup pipeline, or does it rely on opaque reflection magic?
6. **Replaceability**: Can a consumer easily rip out this package and replace it with raw open-source libraries without rewriting their core business logic?
7. **Domain Boundary Leakage**: Does this package introduce base classes, interfaces, or result types that will leak into consuming domain models?
8. **Code Recipe Alternative**: Could this requirement be solved more cleanly with a documented pattern or an AI-assisted code recipe?
9. **Automated Conformance**: Can this standard be verified from the outside using automated conformance tests?
10. **Dashboard & Alerting Impacts**: Do platform dashboards and alerts depend on telemetry generated by this component?
11. **Clear Maintenance Ownership**: Who fixes bugs, updates dependencies, and cuts releases for this package over the next three years?
12. **Migration & Deprecation Path**: What is the upgrade strategy when the underlying third-party library introduces breaking API changes?
13. **Frictionless Escape Hatches**: If a team encounters a critical production blocker with this package, how easily can they bypass it?
14. **Complexity Check**: Does this abstraction actually solve underlying complexity, or does it merely sweep it under the rug until an incident occurs?

---

## Mental Model

Organizations need both **code reuse** and **operational consistency**. However, operational consistency does not require forcing every service into an identical, monolithic framework.

A healthy platform architecture separates responsibilities cleanly:

- **The Service** owns its composition, its startup code, its middleware pipeline order, its business logic, and its explicit runtime policies.
- **The Platform** provides modular building blocks, safe defaults, reference project templates, dashboard standards, and automated conformance tests.

The platform's foundational contract is simple:

> **Every service must be operationally compatible with the platform, but applications retain full ownership of their composition.**

Build a paved road rather than a walled garden. Make the safe, standard path transparent, testable, and effortless to adopt—without making custom requirements impossible to build.

---

## Related Concepts

- **[[Designing Internal Packages as an Explicit, Composable Framework]]**: Practical patterns for packaging modular internal libraries that avoid framework lock-in.
- **[[Internal Shared Packages vs Agent-Generated Code]]**: Balancing shared package dependencies against localized, agent-generated code.
- **[[Service-to-Service Communication - How Service A Should Call Service B]]**: Standardizing communication clients while letting applications own their dependencies.
- **[[Scaling a Modular Monolith with Local-or-Remote Module Execution]]**: Applying standardized composition patterns across modular monolith architectures.
- **[[OpenTelemetry as the Runtime Truth for Autonomous Agents]]**: The vendor-neutral observability standard for traces, metrics, and logs across distributed systems.
