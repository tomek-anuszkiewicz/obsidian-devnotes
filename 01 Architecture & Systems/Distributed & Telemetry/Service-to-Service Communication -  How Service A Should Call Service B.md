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
  - Service-to-Service Communication
  - Inter-Service Calling Patterns
---

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

The policy remains visible to A.

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

---

## API Compatibility

Backward compatibility is required regardless of whether the client is:

- handwritten,
    
- generated,
    
- distributed as a NuGet,
    
- created locally,
    
- expressed through an RPC interface.
    

Service B must assume that consumers update at different times.

A deployed B may be called by:

- an old client,
    
- the current client,
    
- a future client during a rolling deployment.
    

The contract must tolerate version skew.

---

## Usually Safe Changes

Changes that are often backward compatible include:

- adding a new endpoint,
    
- adding an optional request field,
    
- adding an optional response field,
    
- adding a new error code when consumers handle unknown codes safely,
    
- adding a query parameter with a default behavior,
    
- adding metadata that old consumers ignore.
    

Even these changes should be tested because generated clients and strict serializers may behave differently.

---

## Common Breaking Changes

Typical breaking changes include:

- removing an endpoint,
    
- renaming a field,
    
- removing a field,
    
- changing a field type,
    
- making an optional field required,
    
- changing the meaning of `null`,
    
- changing status codes,
    
- changing error codes,
    
- changing enum behavior,
    
- changing authentication requirements,
    
- changing idempotency semantics,
    
- changing default sorting or filtering,
    
- changing retry-related behavior,
    
- changing the business meaning of an existing value.
    

A contract may remain structurally valid while becoming semantically incompatible.

For example:

```text
status = active
```

may previously mean:

```text
The customer may place an order.
```

Later it may mean:

```text
The customer record is not archived.
```

The JSON still deserializes, but the consumer behavior may become incorrect.

Backward compatibility must therefore cover both schema and meaning.

---

## Enum Compatibility

Enums are a frequent source of hidden breaking changes.

Suppose B initially returns:

```text
active
inactive
```

Later it adds:

```text
suspended
```

A generated .NET enum may fail deserialization or map the value incorrectly.

Safer approaches include:

- string-based values,
    
- an `Unknown` fallback,
    
- tolerant deserialization,
    
- explicit handling of unknown values.
    

Consumer code should avoid assuming that all possible values are permanently known.

Bad:

```csharp
return response.Status switch
{
    CustomerStatus.Active => true,
    CustomerStatus.Inactive => false
};
```

Better:

```csharp
return response.Status switch
{
    "active" => Eligibility.Allowed,
    "inactive" => Eligibility.Denied,
    _ => Eligibility.Unknown
};
```

The correct fallback depends on the business risk.

---

## Request Compatibility

Adding a required request field is normally breaking.

Instead, B should:

- add an optional field,
    
- define a default behavior,
    
- introduce a new endpoint or API version when semantics differ substantially.
    

Old consumers must still be able to send the previous request format.

B should avoid interpreting omitted fields differently without an explicit version change.

---

## Response Compatibility

Adding a response field is generally safe when consumers ignore unknown fields.

Removing or changing an existing field is breaking.

B should also avoid turning:

```json
"items": []
```

into:

```json
"items": null
```

unless the distinction was part of the original contract.

Changes in nullability frequently break generated clients even when handwritten clients continue to work.

---

## Error Compatibility

Error contracts are part of the public API.

Service B should maintain stable:

- status codes,
    
- machine-readable error codes,
    
- error categories,
    
- retryability semantics,
    
- correlation identifiers.
    

Changing:

```text
404 customer_not_found
```

to:

```text
400 invalid_customer
```

can break Service A even if the successful response contract is unchanged.

Human-readable messages should not be used as stable programmatic identifiers.

Bad:

```csharp
if (error.Message == "Customer was not found")
```

Better:

```csharp
if (error.Code == "customer_not_found")
```

---

## Versioning Strategies

### Compatible evolution

Prefer evolving the existing API through additive, backward-compatible changes.

This should be the default.

### Explicit API versioning

Use a new version when:

- semantics change significantly,
    
- old behavior cannot be preserved,
    
- the contract requires structural redesign,
    
- migration requires a transition period.
    

Examples:

```text
/api/v1/customers
/api/v2/customers
```

or negotiated media types.

### Parallel support

During migration, B may support both versions.

A consumers migrate independently.

B removes the old version only after:

- usage is known,
    
- consumers have migrated,
    
- a deprecation period has passed,
    
- production traffic confirms no remaining users.
    

Versioning does not replace backward compatibility discipline. Creating a new API version for every small change creates long-term maintenance overhead.

---

## Source of Truth

There should be one primary source of truth for the public contract.

Possible choices include:

- OpenAPI specification generated from B,
    
- contract-first OpenAPI maintained separately,
    
- protocol schema such as Protobuf,
    
- another machine-readable IDL.
    

Avoid maintaining several independent manual definitions:

```text
ServiceB.Contracts.dll
openapi.json
ServiceB.Client.dll
documentation
```

They can drift apart.

A better pipeline is:

```text
Source of truth: OpenAPI

Generated artifacts:
- .NET client
- TypeScript client
- API documentation
- compatibility report
```

The generated artifacts should not become competing contract definitions.

---

## Compatibility Testing

Compatibility should be automated.

### Schema compatibility tests

Service B compares the new API specification with the previous released version.

The pipeline should detect:

- removed endpoints,
    
- removed properties,
    
- changed types,
    
- changed required fields,
    
- incompatible enum changes,
    
- changed response codes.
    

### Consumer-driven contract tests

Service A defines the subset of B behavior it depends on.

For example:

```text
A requires:
- GET /customers/{id}
- response fields: id, status
- 404 with code customer_not_found
- unknown status values must be possible
```

Service B validates those expectations before release.

This is especially useful when A uses only a small portion of a large API.

### Integration tests

Service A runs its adapter against:

- a real test instance of B,
    
- a compatible stub,
    
- or a contract test environment.
    

The test should validate:

- authentication,
    
- serialization,
    
- status codes,
    
- timeout behavior,
    
- trace propagation,
    
- error interpretation.
    

### Production or staging smoke tests

After deployment, verify:

- A can reach B,
    
- authentication works,
    
- telemetry is emitted,
    
- required endpoints behave correctly,
    
- the deployed API matches the expected contract.
    

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

## Warning Signs

The integration is becoming unhealthy when:

- Service B DTOs appear throughout Service A,
    
- business code directly depends on a generated client,
    
- the client package configures global logging,
    
- the client package creates its own tracing conventions,
    
- timeout and retry policies are hidden,
    
- every B error is converted into one generic exception,
    
- B’s domain behavior is distributed in a contracts package,
    
- A must update a large SDK to use one field,
    
- the client introduces a large dependency tree,
    
- client versions and deployed B versions are unclear,
    
- the official client is no longer maintained,
    
- nobody knows whether a field or endpoint can be safely changed.
    

---

## Practical Rules

1. Service B owns the public API contract.
    
2. Service A owns the business meaning of the integration.
    
3. The platform owns common HTTP, logging, tracing, and authentication mechanisms.
    
4. A should normally hide B behind an interface owned by A.
    
5. Generated and official clients should remain infrastructure details.
    
6. Transport DTOs should not become shared domain models.
    
7. Clients should be thin by default.
    
8. Retry and timeout policy should remain visible to A.
    
9. Service B should expose stable machine-readable errors.
    
10. A should interpret those errors according to its use case.
    
11. Use one machine-readable source of truth for the contract.
    
12. Prefer additive, backward-compatible API evolution.
    
13. Treat error behavior and semantics as part of compatibility.
    
14. Test compatibility automatically.
    
15. Depend only on the subset of B that A actually needs.
    
16. Do not hide remote-call failure semantics behind a local-looking interface.
    
17. A service-specific client should not own organization-wide observability policy.
    

---

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
---

## Relationship to the Knowledge Graph

- **[[Service-to-Service Authentication and Authorization in Azure and Kubernetes]]**: Workload identity, token exchange, and mutual TLS for inter-service communication.
- **[[Service vs User Authorization Models]]**: Distinguishing caller identity from acting-on-behalf-of user delegation.
- **[[Propagating User Context Between Services]]**: Propagating trace context, tenant IDs, and user identity across synchronous calls.
- **[[Scaling a Modular Monolith with Local-or-Remote Module Execution]]**: Designing remote-capable contracts that can execute locally or over HTTP/gRPC.
- **[[Designing APIs for LLM-Generated Integration Code]]**: Designing strongly typed API contracts that agents can easily consume and integrate.
- **[[OpenTelemetry]]**: Instrumenting inter-service requests with standardized W3C trace context headers.
