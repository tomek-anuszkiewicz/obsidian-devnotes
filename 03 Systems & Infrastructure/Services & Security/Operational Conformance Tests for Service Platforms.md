---
title: "Operational Conformance Tests for Service Platforms"
tags:
  - platform-engineering
  - testing
  - observability
  - microservices
  - infrastructure
aliases:
  - "Service Platform Conformance Testing"
  - "Operational E2E Tests for Services"
  - "Testing Telemetry and Runtime Platform Contracts"
---

Two services use the same logging package, but one omits deployment metadata and the other emits metric labels that the shared dashboard cannot query. Package adoption has not established that either service integrates correctly with the operating platform.

The platform contract should describe observable behavior: logs that can be correlated, traces that cross the boundary, bounded metric dimensions, usable health endpoints, and declared retry and timeout behavior. A conformance suite exercises the running service and observes those outputs. Business tests remain necessary because telemetry correctness does not establish business correctness.

The sections below develop that suite, including dashboard queries as consumers of the telemetry contract. [[Standardizing Service Infrastructure with Reusable Blocks]] supplies the organizational ownership and supported path. [[Designing Internal NuGet Packages as an Explicit, Composable Framework]] explains why the implementation can remain replaceable while the required behavior stays stable.

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

Version the operational contract and its tests together with the dashboards and supported tooling that consume it. A replacement implementation is acceptable when it demonstrates the same required behavior under the relevant runtime conditions.

## Related Notes

- [[Standardizing Service Infrastructure with Reusable Blocks]] — Platform ownership, supported components, and controlled alternatives.
- [[Designing Internal NuGet Packages as an Explicit, Composable Framework]] — Composing and replacing internal infrastructure implementations.
- [[OpenTelemetry — Architecture, Signals, and Collector]] — The telemetry path whose outputs the platform tests exercise.
