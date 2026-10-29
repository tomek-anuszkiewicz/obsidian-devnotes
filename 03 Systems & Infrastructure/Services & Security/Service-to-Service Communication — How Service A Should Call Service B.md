---
title: Service-to-Service Communication — How Service A Should Call Service B
tags:
  - microservices
  - distributed-systems
  - api-design
  - grpc
  - rest-api
  - messaging
  - resilience
aliases:
  - Service-to-Service Communication - How Service A Should Call Service B
  - Service-to-Service Communication
  - Inter-Service Calling Patterns
---

Service A needs a business answer from Service B. B's endpoint and transport model are not necessarily the interface A should expose to its own application code. A consumer-owned adapter can keep that distinction explicit.

This article follows dependency ownership, partial contracts, local models, and layering inside A. [[Choosing Service Clients — SDKs, Generated Code, and Local Adapters]] compares the client mechanisms used behind that boundary: shared DTOs, an official SDK, generation, a local adapter, and an interface-based HTTP client. The runtime and compatibility articles then develop the failure and release behavior of the same integration.

## Context

Assume that Service A needs data or behavior owned by Service B.

The technical problem may look simple:

```text
Service A → HTTP → Service B
```

However, several responsibilities must be assigned correctly:

- Who owns the API contract?

- Who generates or maintains the client?

- Who defines request and response models?

- Who configures `HttpClient`?

- Who decides retry and timeout policies?

- Who interprets errors?

- Who owns logging, tracing, and metrics?

- Who maintains backward compatibility?

- How much of Service B should become visible inside Service A?

A convenient client library can reduce boilerplate, but it can also introduce strong coupling and hide important runtime behavior.

The goal should be:

> Make the integration easy to use without making the remote call look like a local, infallible method.

This article focuses on the consumer-owned boundary around a service dependency. [[Choosing Service Clients — SDKs, Generated Code, and Local Adapters]] compares the transport-client options. [[Remote Service Calls — Errors, Resilience, and Observability]] develops the failure, retry, timeout, authentication, and telemetry behavior of that boundary. [[Evolving Service API Contracts Without Breaking Consumers]] explains how independently deployed consumers survive API changes.

The C# examples illustrate layering and ownership. Domain types, mapping functions, configuration helpers, and some registration methods belong to the example application; the snippets are not a complete runnable project.

---

## Core Responsibility Model

A useful high-level division is:

> Service B owns the public API contract.
> Service A owns how that contract is used inside Service A.
> The platform owns cross-cutting communication standards.

More specifically:

### Service B should own

- endpoint definitions,

- request and response schemas,

- business error codes exposed by the API,

- API versioning,

- API documentation,

- OpenAPI specification,

- backward compatibility of the public API,

- optional generated transport clients.

### Service A should own

- the business meaning of the dependency,

- the interface used by its application code,

- mapping from B’s transport models into A’s local models,

- interpretation of B’s responses and errors,

- use-case-specific timeout budget,

- retry suitability,

- fallback behavior,

- caching,

- failure propagation.

### The shared platform should own

- standard HTTP client instrumentation,

- trace-context propagation,

- correlation identifiers,

- common telemetry conventions,

- authentication mechanisms,

- safe logging rules,

- shared error envelope conventions,

- basic resilience mechanisms,

- service discovery or endpoint resolution.

This division prevents the Service B client from becoming a hidden application framework inside Service A.

---

## The Interface Should Usually Be Owned by Service A

Service B exposes technical capabilities.

Service A depends on a business need.

These are not necessarily the same abstraction.

Service B may expose:

```csharp
IServiceBApi.GetCustomerAsync(...)
```

Service A may need:

```csharp
ICustomerEligibilitySource.GetEligibilityAsync(...)
```

The second interface is better for A because it describes why A needs the dependency.

Benefits include:

- Service B transport types do not enter business code,

- REST can later be replaced by messaging, caching, or another provider,

- Service A can use simple test doubles,

- changes to B are contained in one adapter,

- A can combine multiple B calls behind one locally meaningful operation.

A useful principle is:

> The provider owns the public protocol.
> The consumer owns the interface expressing its dependency.

---

## Partial Contract Consumption

Service A often needs only one endpoint and a subset of fields.

It should not be forced to adopt the complete Service B model.

Suppose B returns:

```json
{
  "id": "123",
  "name": "Example",
  "status": "active",
  "address": {},
  "permissions": [],
  "preferences": {},
  "audit": {}
}
```

A may only need:

```csharp
private sealed record ServiceBResponse(
    string Id,
    string Status);
```

Most JSON serializers can ignore additional fields.

This reduces coupling to irrelevant parts of B.

However, A must still understand the semantic contract of the fields it uses.

A useful rule is:

> Depend on the smallest stable subset of the provider contract that satisfies the consumer’s need.

---

## Avoid Shared Domain Models

Service A and Service B should not normally share one domain model package.

Even when both discuss a concept called `Customer`, the concept may have different responsibilities.

For B:

```text
Customer = complete customer record
```

For A:

```text
Customer = eligibility information required to place an order
```

Sharing a domain model creates pressure to combine unrelated needs.

Instead:

- B exposes transport DTOs,

- A maps them into its own local concepts,

- each service owns its own domain model.

Shared contracts are acceptable.

Shared domain ownership is much more dangerous.

---

## Thin Client vs Smart Client

### Thin client

A thin client provides:

- endpoint methods,

- serialization,

- protocol-specific DTOs,

- error-envelope parsing,

- basic DI registration.

It leaves application policy to A.

### Smart client

A smart client may also provide:

- retries,

- caching,

- fallback,

- business validation,

- domain mapping,

- global error translation,

- logging policy,

- tracing policy.

Smart clients are attractive because they reduce work for consumers.

However, they often embed assumptions that are correct for one use case and wrong for another.

Prefer thin clients unless the additional behavior is:

- truly universal,

- owned by Service B,

- stable,

- carefully documented,

- independently configurable,

- tested across consumers.

---

## Recommended Layering in Service A

A practical structure is:

```text
Service A

Application
  ICustomerEligibilitySource
  OrderUseCase

Infrastructure
  ServiceBGeneratedClient
  ServiceBCustomerEligibilitySource
  ServiceBConfiguration
```

Application interface:

```csharp
public interface ICustomerEligibilitySource
{
    Task<CustomerEligibility> GetAsync(
        CustomerId customerId,
        CancellationToken cancellationToken);
}
```

Adapter:

```csharp
internal sealed class ServiceBCustomerEligibilitySource(
    IServiceBTransportClient client)
    : ICustomerEligibilitySource
{
    public async Task<CustomerEligibility> GetAsync(
        CustomerId customerId,
        CancellationToken cancellationToken)
    {
        var response = await client.GetCustomerAsync(
            customerId.Value,
            cancellationToken);

        return response switch
        {
            { IsSuccess: true } =>
                Map(response.Value),

            { Error.Code: "customer_not_found" } =>
                CustomerEligibility.NotAvailable,

            _ =>
                throw MapUnexpectedFailure(response.Error)
        };
    }
}
```

This isolates:

- generated code,

- Service B DTOs,

- HTTP-specific concerns,

- error translation,

- compatibility adaptations.

---

## Warning Signs

The integration is becoming unhealthy when:

- Service B DTOs appear throughout Service A,
- business code directly depends on a generated client,
- B’s domain behavior is distributed in a contracts package,
- A must update a large SDK to use one field,
- the client introduces a large dependency tree,
- client versions and deployed B versions are unclear,
- the official client is no longer maintained,

## Practical Rules

- Service B owns the public API contract.
- Service A owns the business meaning of the integration.
- The platform owns common HTTP, logging, tracing, and authentication mechanisms.
- A should normally hide B behind an interface owned by A.
- Generated and official clients should remain infrastructure details.
- Transport DTOs should not become shared domain models.
- Clients should be thin by default.
- Depend only on the subset of B that A actually needs.
- Do not hide remote-call failure semantics behind a local-looking interface.

## Mental Model

A remote client is not only a convenience wrapper.

It defines a boundary between independently deployed systems.

The healthiest model is:

```text
Service B
  owns the public protocol
        ↓
Thin transport client or generated client
        ↓
Adapter owned by Service A
        ↓
Interface and domain concepts owned by Service A
```

Cross-cutting behavior is provided separately:

```text
Platform
  authentication
  tracing
  logging
  metrics
  resilience mechanisms
```

The final principle is:

> Service B should make its API easy to consume, but it should not decide how Service A structures its application or interprets every outcome.

Or more concisely:

> B owns the contract.
> A owns the dependency.
> The platform owns the communication standards.

(See [[Service-to-Service Authentication and Authorization in Azure and Kubernetes]] and [[Propagating User Context Between Services]]).

## Related Notes

- [[Service-to-Service Authentication and Authorization in Azure and Kubernetes]] — Managed identities, mTLS, and workload tokens across service boundaries.
- [[Propagating User Context Between Services]] — Passing user identities, tenancy, and trace context across synchronous calls.
- [[Standardizing Service Infrastructure with Reusable Blocks]] — Packaging resilient HTTP/gRPC pipelines into reusable service infrastructure.
- [[Scaling a Modular Monolith with Local-or-Remote Module Execution]] — Decoupling module contracts from physical network boundaries.
- [[Remote Service Calls — Errors, Resilience, and Observability]] — Assigning error interpretation, retry budgets, authentication, and telemetry responsibilities.
- [[Evolving Service API Contracts Without Breaking Consumers]] — Evolving schemas and behavior while old consumers remain deployed.
