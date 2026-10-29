---
title: "Choosing Service Clients — SDKs, Generated Code, and Local Adapters"
tags:
  - api-design
  - microservices
  - dotnet
  - code-generation
  - software-architecture
aliases:
  - "SDK vs Generated Client vs Local Adapter"
  - "Choosing API Client Distribution"
  - "Shared Contracts and Consumer-Owned HTTP Clients"
---

A service publishes an API, but its consumers still need a way to call it. Sharing DTOs, adopting an official SDK, generating a client, and writing a small adapter trade different kinds of work and coupling.

Choose according to the protocol's complexity, the subset a consumer needs, supported languages, the release relationship, and who can maintain the result. A package version is not the deployed API version, and a convenient interface does not remove network failure. In every option, the consumer can keep transport details behind its own application boundary.

The comparison below retains concrete C# examples and a decision model. [[Service-to-Service Communication — How Service A Should Call Service B]] develops the adapter and local domain interface in more detail. The context and responsibility model are repeated here so the choices can be evaluated independently.

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

This article focuses on choosing a client and keeping Service A's dependency under its own control. [[Remote Service Calls — Errors, Resilience, and Observability]] develops the failure, retry, timeout, authentication, and telemetry behavior of that boundary. [[Evolving Service API Contracts Without Breaking Consumers]] explains how independently deployed consumers survive API changes.

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

## Option 1: Service B Publishes a Contracts NuGet

Service B publishes a package such as:

```text
ServiceB.Contracts
```

It contains request and response DTOs:

```csharp
public sealed record GetCustomerResponse(
    string Id,
    string Name,
    string Status);
```

Service A references the package and uses the shared types.

### Advantages

- one shared definition of transport models,

- compile-time type safety,

- easy distribution in a .NET-only environment,

- reduced manual duplication,

- simple version tracking through package references.

### Risks

- A becomes coupled to the release process of B,

- package versions may not match deployed API versions,

- transport types may leak into A’s domain and application layers,

- the package may gradually include helpers, validation, behavior, or framework dependencies,

- consumers may become dependent on implementation details rather than the public wire contract.

### Important rule

Transport DTOs should remain passive data structures.

Avoid models containing:

- domain behavior,

- validation methods,

- infrastructure dependencies,

- service registration,

- database attributes,

- business calculations,

- inheritance hierarchies.

Bad:

```csharp
public sealed class Customer
{
    public string Status { get; set; }

    public bool CanPlaceOrder()
    {
        // Business behavior from Service B
    }

    public void Validate()
    {
        // Validation owned by Service B
    }
}
```

Better:

```csharp
public sealed record CustomerResponse(
    string Id,
    string Status);
```

A contracts package should describe messages, not export the internal domain model of Service B.

---

## Option 2: Service B Publishes a Full Client NuGet

Service B publishes:

```text
ServiceB.Client
```

Service A registers it:

```csharp
services.AddServiceBClient(options =>
{
    options.BaseAddress = configuration["ServiceB:BaseAddress"];
});
```

Application code receives an interface:

```csharp
public sealed class Handler(IServiceBClient serviceBClient)
{
}
```

The package may provide:

- typed endpoints,

- request and response DTOs,

- serialization,

- dependency injection registration,

- authentication support,

- error deserialization,

- optional telemetry,

- optional resilience configuration.

### Advantages

- very low integration cost,

- consistent protocol implementation,

- fewer duplicated clients,

- easier onboarding,

- Service B can publish a supported official SDK,

- repeated transport bugs can be fixed centrally.

### Risks

A full client can easily take responsibility for too much.

It may silently configure:

- logging,

- tracing,

- retry,

- timeouts,

- exception mapping,

- authentication,

- circuit breakers,

- metrics,

- global `HttpClient` behavior.

This creates several problems:

- hidden runtime policy,

- inconsistent behavior between different service clients,

- duplicate logging and tracing,

- dependency conflicts,

- difficult platform-wide upgrades,

- business interpretation of errors embedded in the client,

- strong coupling to the Service B package.

An SDK that creates and disposes its own connection pools for each request can exhaust available ports; a long-lived pool without a suitable connection lifetime can keep using old DNS results. The SDK should cooperate with the application's chosen handler and lifetime strategy ([HttpClient lifetime guidance](https://learn.microsoft.com/en-us/dotnet/fundamentals/networking/http/httpclient-guidelines)). Bundled Polly or serializer dependencies can also create version conflicts during platform upgrades.

### Guiding principle

> A service-specific client should own the Service B protocol, not the communication policy of the whole organization.

A full client may provide a thin transport abstraction, but it should not become the owner of all cross-cutting communication behavior.

---

## Option 3: Service A Generates a Client from OpenAPI

Service B publishes an OpenAPI document:

```text
openapi.json
```

Service A uses tools such as NSwag, Kiota, Refit-based generation, or another generator to create a client.

### Advantages

- OpenAPI becomes the language-neutral contract,

- consumers can exist in different programming languages,

- the generated client matches the published API schema,

- Service A controls when and how the client is regenerated,

- no need for Service B to maintain handwritten SDKs for every language.

### Risks

- generated clients may be very large,

- all endpoints and schemas may be generated even when A needs only one operation,

- generated types may leak throughout A,

- code can be difficult to read or debug,

- generator upgrades may produce large unrelated diffs,

- schema compatibility does not automatically guarantee semantic compatibility.

### Recommended use

Treat the generated client as an infrastructure detail.

```text
Application
  ICustomerRiskProvider

Infrastructure
  GeneratedServiceBClient
  ServiceBCustomerRiskProvider
```

Business code should not depend directly on generated DTOs.

```csharp
public interface ICustomerRiskProvider
{
    Task<RiskLevel> GetRiskAsync(
        CustomerId customerId,
        CancellationToken cancellationToken);
}
```

The adapter uses the generated client:

```csharp
internal sealed class ServiceBCustomerRiskProvider(
    ServiceBGeneratedClient client)
    : ICustomerRiskProvider
{
    public async Task<RiskLevel> GetRiskAsync(
        CustomerId customerId,
        CancellationToken cancellationToken)
    {
        var response = await client.GetCustomerAsync(
            customerId.Value,
            cancellationToken);

        return Map(response);
    }
}
```

The generated code remains replaceable and isolated.

---

## Option 4: Service A Implements a Small Local Client

If Service A needs only one endpoint and a few fields, a small local adapter may be simpler than a full SDK.

```csharp
public interface ICustomerStatusProvider
{
    Task<CustomerStatus?> FindAsync(
        CustomerId customerId,
        CancellationToken cancellationToken);
}
```

Implementation:

```csharp
internal sealed class ServiceBCustomerStatusProvider(
    HttpClient httpClient)
    : ICustomerStatusProvider
{
    public async Task<CustomerStatus?> FindAsync(
        CustomerId customerId,
        CancellationToken cancellationToken)
    {
        using var response = await httpClient.GetAsync(
            $"/customers/{customerId.Value}/status",
            cancellationToken);

        if (response.StatusCode == HttpStatusCode.NotFound)
        {
            return null;
        }

        response.EnsureSuccessStatusCode();

        var dto = await response.Content
            .ReadFromJsonAsync<ServiceBResponse>(
                cancellationToken: cancellationToken);

        return new CustomerStatus(
            dto!.Code,
            dto.IsActive);
    }

    private sealed record ServiceBResponse(
        string Code,
        bool IsActive);
}
```

### Advantages

- very small dependency surface,

- complete visibility,

- easy local customization,

- no large generated client,

- no dependency on unrelated B endpoints,

- explicit mapping into A’s local model.

### Risks

- duplicated transport code,

- repeated implementation mistakes,

- manual maintenance when B changes,

- possible inconsistent authentication and telemetry,

- risk of incomplete error handling.

### Best fit

This approach works well when:

- only a small part of B is needed,

- the API is simple,

- A values minimal coupling,

- standard platform helpers already handle HTTP concerns,

- full SDK generation would be disproportionate.

---

## Option 5: Service B Publishes an RPC-Like Interface

Libraries can create an HTTP client from an interface:

```csharp
public interface IServiceBApi
{
    [Get("/customers/{id}")]
    Task<CustomerResponse> GetCustomerAsync(
        string id,
        CancellationToken cancellationToken);
}
```

Service A requests the interface from dependency injection and calls it like a local method.

### Advantages

- very little boilerplate,

- readable method declarations,

- typed requests and responses,

- easy registration,

- convenient for simple APIs.

### Main risk: local-call illusion

This code:

```csharp
await serviceBApi.GetCustomerAsync(id, cancellationToken);
```

looks like an ordinary method call.

In reality it may:

- cross a network boundary,

- take seconds,

- time out,

- fail partially,

- be retried,

- execute more than once,

- depend on authentication and service availability.

When engineers fall for this illusion, the failure modes are predictable: calling remote endpoints inside loops, holding open local database transactions across network roundtrips, omitting explicit timeout budgets, or retrying non-idempotent operations until thread pools saturate.

The abstraction is useful only when the network semantics remain visible in design and error handling.

### Recommended rule

The RPC-like interface should normally remain inside the infrastructure layer.

Application code should depend on an interface owned by Service A:

```csharp
public interface ICustomerRiskProvider
{
    Task<RiskLevel> GetRiskAsync(
        CustomerId customerId,
        CancellationToken cancellationToken);
}
```

The infrastructure adapter can internally use the RPC-style client.

---

## Recommended Decision Model

### Use a Service B contracts package when

- consumers are primarily .NET,

- DTOs are small and passive,

- package and API versions are carefully managed,

- shared compile-time types provide real value.

### Use an official Service B client when

- B has many consumers,

- the protocol is non-trivial,

- B can actively maintain the SDK,

- the client remains thin,

- common transport implementation reduces real risk.

### Generate from OpenAPI when

- the API contract is machine-readable,

- consumers use multiple languages,

- generation can be automated,

- generated code is kept inside infrastructure.

### Write a small local adapter when

- A needs only a small API subset,

- the interaction is simple,

- full SDK adoption would create unnecessary coupling,

- platform HTTP helpers already exist.

### Use an RPC-style client when

- convenience is valuable,

- the interface remains an infrastructure detail,

- network failure semantics are not hidden,

- the client is wrapped behind an A-owned interface.

---

Compare the maintenance and dependency boundary as well as the amount of generated or handwritten code. Keep transport models inside infrastructure, select visible runtime policy, and verify the client against the provider behavior it will encounter.

## Related Notes

- [[Service-to-Service Communication — How Service A Should Call Service B]] — Consumer-owned interfaces, local domain models, and adapter layering.
- [[Remote Service Calls — Errors, Resilience, and Observability]] — Failure interpretation, retry budgets, authentication, and telemetry.
- [[Evolving Service API Contracts Without Breaking Consumers]] — Schema and semantic compatibility across independent releases.
