---
title: Remote Service Calls — Errors, Resilience, and Observability
tags:
  - distributed-systems
  - microservices
  - resilience
  - observability
  - api-design
  - dotnet
aliases:
  - Remote Call Failure Semantics
  - Service Client Retry and Timeout Ownership
  - Service Communication Runtime Policies
  - Errors and Telemetry Across Service Boundaries
---

Service A calls Service B to decide whether an order can proceed. The request times out. A has no response, but B might already have completed the operation. A convenient client method cannot decide whether repeating it is safe or whether the result still matters to the user.

The integration needs three owners. B defines endpoint behavior, stable errors, required permissions, and duplicate-execution guarantees. A interprets those outcomes for its use case and chooses its latency and failure policy. The platform supplies reusable communication mechanisms and telemetry conventions. A client can implement B's protocol while leaving these decisions visible.

This remains true for a generated client, an official SDK, an interface-based HTTP client, or a small handwritten adapter. [[Service-to-Service Communication — How Service A Should Call Service B]] compares those choices and shows how to hide the transport behind an interface owned by A.

## Keep the Network Boundary Visible

An HTTP method call can cross a network, wait for another service, fail after a partial result, or execute more than once. Holding a local database transaction open while waiting for B couples local resources to remote latency. Calling B once per item can turn a cheap local-looking loop into many sequential network round trips.

A timeout means that the caller stopped waiting; it does not establish that B made no state change. Repeating a mutation requires an endpoint whose semantics and duplicate handling make that repetition safe. Cancellation also needs an explicit transport and server contract; passing a local cancellation token does not prove a remote transaction was undone.

The examples below are fragments illustrating ownership. Application types and project-specific registration helpers are omitted.

## Error Handling Responsibilities

Error handling is one of the most difficult parts of a shared client.

Three different categories must be distinguished.

### Transport failures

Examples:

- DNS failure,

- connection refused,

- connection reset,

- timeout,

- TLS failure.

These indicate that communication did not complete normally.

### Protocol failures

Examples:

- malformed response,

- unsupported content type,

- unexpected status code,

- invalid JSON,

- incompatible schema.

These indicate a problem in communication or contract handling.

### Business responses

Examples:

- customer not found,

- operation not permitted,

- insufficient balance,

- conflicting state,

- validation failure.

These are meaningful outcomes defined by Service B.

The client should not flatten all of these into one exception or one generic result.

---

## Who Interprets Errors?

Service B should define stable machine-readable error codes.

For example:

```json
{
  "type": "https://errors.company/customer-not-found",
  "title": "Customer not found",
  "status": 404,
  "code": "customer_not_found",
  "traceId": "abc123"
}
```

The shared platform may define the common envelope.

Service B defines the domain-specific error codes.

Service A decides what they mean in its use case.

For one use case:

```text
customer_not_found → normal absence
```

For another:

```text
customer_not_found → inconsistent system state
```

For another:

```text
customer_not_found → create a new customer
```

Therefore, a Service B client should not automatically map all errors into application-specific exceptions such as:

```csharp
throw new CustomerMissingFromOrderException();
```

That exception belongs to A.

A transport client may expose:

```csharp
public sealed record ServiceBError(
    string Code,
    HttpStatusCode StatusCode,
    string? Message,
    string? TraceId);
```

The adapter in A performs the final mapping.

---

## Logging and Tracing

Service-specific clients should not independently invent logging and tracing standards.

Otherwise each client may:

- use different field names,

- create duplicate log entries,

- log request or response bodies unsafely,

- propagate trace context differently,

- create redundant spans,

- use incompatible metric names,

- hide its retry behavior.

The shared platform should provide:

- standard `HttpClient` instrumentation,

- trace-context propagation,

- correlation identifiers,

- common semantic attributes,

- safe redaction rules,

- dependency metrics,

- consistent span and log conventions.

The Service B client may enrich telemetry with information such as:

- logical operation name,

- target service name,

- API version,

- stable error code.

It should not configure a separate observability stack.

The platform can configure HTTP instrumentation and W3C `traceparent` propagation for the shared handler pipeline. Service-specific code can enrich the current activity with bounded operation and error attributes, or create a meaningful operation span when needed. It should use the configured telemetry pipeline and avoid raw unredacted payload logs. For example:

```csharp
var activity = Activity.Current;
activity?.SetTag("peer.service", "ServiceB");
activity?.SetTag("service_b.operation", "get_customer");
activity?.SetTag("service_b.error_code", error?.Code);
```

A useful principle is:

> Service-specific clients may enrich telemetry, but they should not own the telemetry infrastructure.

---

## Retry and Timeout Ownership

Retry and timeout decisions are often incorrectly hidden inside a client package.

Service B knows:

- whether an endpoint is idempotent,

- whether duplicate execution is safe,

- typical processing time,

- which failures may be transient.

Service A knows:

- its end-to-end latency budget,

- whether retrying still has business value,

- whether the user is waiting,

- whether a fallback exists,

- how many dependencies are involved in the complete operation.

Therefore:

- B should document endpoint semantics,

- the platform should provide resilience mechanisms,

- A should usually select the final policy.

For example:

```csharp
services
    .AddHttpClient<IServiceBTransportClient, ServiceBTransportClient>(
        client =>
        {
            client.BaseAddress = configuration.GetServiceUri("ServiceB");
        })
    .AddStandardHttpTelemetry()
    .AddResilienceHandler(
        "service-b-order-validation",
        pipeline =>
        {
            pipeline.AddTimeout(
                TimeSpan.FromSeconds(2));

            pipeline.AddRetry(
                new HttpRetryStrategyOptions
                {
                    MaxRetryAttempts = 1
                });
        });
```

The policy remains visible to A. `GetServiceUri` and `AddStandardHttpTelemetry` are example project helpers. In this sketch the timeout surrounds the retry strategy, so the two-second budget applies to the combined execution rather than granting two seconds to every attempt. A real policy must also specify retryable outcomes, operation safety, backoff, and caller cancellation.

Use one deliberately composed resilience handler for this client rather than accidentally stacking an SDK retry loop, a platform handler, and another application retry loop. The .NET guidance describes both standard and custom handler composition ([HTTP resilience guidance](https://learn.microsoft.com/en-us/dotnet/core/resilience/http-resilience)).

Retries during a sustained outage can amplify load and keep requests, connections, and memory occupied longer. Circuit breakers and concurrency limits can bound that pressure; asynchronous HTTP calls do not inherently block a worker thread for their entire duration. Retry only suitable transient failures and operations whose semantics make repetition safe. Blindly retrying a mutation after an ambiguous result risks duplicate state changes.

A single default policy hidden inside the B client may be wrong for different consumers or use cases.

---

## Authentication Responsibility

Authentication mechanisms should usually be standardized by the platform.

The platform may provide:

- service identity,

- token acquisition,

- certificate handling,

- token caching,

- propagation rules,

- standard authorization headers.

Service B should define:

- required scopes,

- permissions,

- audience,

- access rules.

Service A should configure:

- which identity it uses,

- which credentials or workload identity apply,

- which scope is requested.

The Service B client may integrate with the shared authentication handler, but it should not implement a separate authentication framework.

A platform-provided `DelegatingHandler` can acquire and attach bearer tokens, using an identity library that handles token caching and renewal. Client certificates for mTLS belong in the transport configuration and its certificate lifecycle. Workload identity systems can supply tokens or certificate material, but these are different mechanisms. Keep the chosen credentials and target permissions explicit (see [[Service-to-Service Authentication and Authorization in Azure and Kubernetes]]).

---

## Verify the Boundary as a Running Integration

Exercise the adapter against controlled responses and a real test deployment where appropriate. Check how it handles a missing customer, an unexpected error code, an invalid response, a slow response, and a lost response after a mutation. Verify the number of attempts and the time budget externally; a configured retry count does not prove the desired runtime behavior.

Also check that authentication succeeds with the intended workload identity, trace context reaches B, error codes remain visible, and sensitive headers or payloads are absent from logs. [[Evolving Service API Contracts Without Breaking Consumers]] places these checks alongside schema comparisons, consumer expectations, and deployment smoke tests.

## Warning Signs

- the client package configures global logging,
- the client package creates its own tracing conventions,
- timeout and retry policies are hidden,
- every B error is converted into one generic exception,

## Practical Rules

- The platform owns common HTTP, logging, tracing, and authentication mechanisms.
- Retry and timeout policy should remain visible to A.
- Service B should expose stable machine-readable errors.
- A should interpret those errors according to its use case.
- Do not hide remote-call failure semantics behind a local-looking interface.
- A service-specific client should not own organization-wide observability policy.

B defines what its endpoint means. A chooses how that meaning participates in its business operation. The platform implements shared mechanisms, while the adapter makes the selected behavior inspectable and testable.

## Related Notes

- [[Service-to-Service Communication — How Service A Should Call Service B]] — Choosing the client and keeping transport types behind a consumer-owned boundary.
- [[Evolving Service API Contracts Without Breaking Consumers]] — Preserving error codes, retry semantics, and response meaning across releases.
- [[Service-to-Service Authentication and Authorization in Azure and Kubernetes]] — Workload identities, tokens, certificates, and authorization.
- [[Propagating User Context Between Services]] — Carrying user, tenant, and trace context across calls.
- [[OpenTelemetry — Architecture, Signals, and Collector]] — Instrumentation, propagation, and the shared telemetry pipeline.
- [[Standardizing Service Infrastructure with Reusable Blocks]] — Reusable communication mechanisms with explicit application policy.
