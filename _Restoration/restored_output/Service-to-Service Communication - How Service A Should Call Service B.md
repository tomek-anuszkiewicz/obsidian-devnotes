---
title: Service-to-Service Communication - How Service A Should Call Service B
tags:
  - microservices
  - distributed-systems
  - api-design
  - grpc
  - rest-api
  - messaging
  - resilience
aliases:
  - Service-to-Service Communication -  How Service A Should Call Service B
  - Service-to-Service Communication
  - Inter-Service Calling Patterns
---

## Context

Assume that Service A needs data or behavior owned by Service B. When architecting distributed microservices, or even when determining module boundaries in a system designed for [[Scaling a Modular Monolith with Local-or-Remote Module Execution|local-or-remote module execution]], this is the most common integration scenario you will encounter:

```text
Service A ─── HTTP / gRPC ───► Service B
```

On paper, this looks like a simple network call. In a production environment, however, crossing this boundary introduces distributed systems concerns that do not exist within a single process. You immediately face several architectural questions:

- Who owns the API contract?
- Who generates or maintains the client library?
- Who defines the request and response models?
- Who configures `HttpClient`, connection pooling, and socket lifecycles?
- Who decides retry, timeout, and circuit breaker policies?
- Who interprets errors and maps status codes to domain outcomes?
- Who owns logging, distributed tracing, and metrics?
- Who maintains backward compatibility across rolling deployments?
- How much of Service B's internal model should become visible inside Service A?

A convenient client library can reduce boilerplate, but it can also become an architectural trap. It often hides network realities beneath the illusion of a local method call, leaks upstream schemas into downstream business logic, and tightly couples the release cycles of two independent teams.

The guiding objective is straightforward:

> Make the integration easy to use and maintain without disguising the remote call as a local, infallible in-memory method.

---

## Core Responsibility Model

To keep services decoupled and prevent shared libraries from turning into unmaintainable pseudo-frameworks, enforce a three-way division of responsibility:

> **Service B** owns the public API contract.  
> **Service A** owns how that contract is interpreted and used within its own domain.  
> The **Platform** owns cross-cutting communication infrastructure and transport standards.

```text
+-----------------------------------------------------------------------------+
|                      SERVICE-TO-SERVICE RESPONSIBILITY                      |
+-----------------------------------------------------------------------------+
|                                                                             |
|  SERVICE A (Consumer Domain)         PLATFORM              SERVICE B        |
|  +------------------------+      +---------------+      +-----------------+ |
|  | Application Logic      |      | Observability |      | Business Logic  | |
|  | (Use Cases / Invariants|      | (W3C Traces,  |      | & Domain Model  | |
|  +------------------------+      |  OpenTelemetry|      +-----------------+ |
|             │                    +---------------+               ▲          |
|             ▼                            │                       │          |
|  +------------------------+              │              +-----------------+ |
|  | Consumer-Owned Port    |      +---------------+      | Public Handler  | |
|  | (Domain Interface)     |      | Auth & mTLS   |      | (Endpoint / API)| |
|  +------------------------+      | (Workload ID) |      +-----------------+ |
|             │                    +---------------+               ▲          |
|             ▼                            │                       │          |
|  +------------------------+              │              +-----------------+ |
|  | Adapter & Local Schema |              │              | Wire Contract   | |
|  | (Anti-Corruption Layer)|              │              | (OpenAPI / IDL) | |
|  +------------------------+              │              +-----------------+ |
|             │                            │                       ▲          |
|             ▼                            ▼                       │          |
|  +------------------------+     HTTP/2 / JSON wire call          │          |
|  | Thin Transport Client  |──────────────────────────────────────┘          |
|  +------------------------+                                                 |
|                                                                             |
+-----------------------------------------------------------------------------+
```

### Service B Should Own

- Endpoint definitions and route structures.
- Request and response serialization schemas.
- Business error codes exposed across the wire.
- API versioning and deprecation timelines.
- API documentation and machine-readable contract specifications (OpenAPI/Swagger, Protobuf), which are critical when [[Designing APIs for LLM-Generated Integration Code|designing APIs for programmatic integration]].
- Backward compatibility guarantees of the public wire contract.
- Optional, strictly thin generated transport clients.

### Service A Should Own

- The business meaning of the dependency within its own domain.
- The interface (port) consumed by its application code.
- Mapping from Service B's wire DTOs into Service A's local domain models (Anti-Corruption Layer).
- Contextual interpretation of Service B's responses and business error codes.
- Use-case-specific timeout budgets and deadlines.
- Retry suitability (knowing whether an operation is safe to re-execute in the current context).
- Fallback strategies, caching, and circuit-breaking thresholds.
- How failures propagate to upstream callers or background workers.

### The Shared Platform Should Own

- Standard HTTP client factory instrumentation and connection lifecycle management.
- Distributed trace-context propagation (such as W3C `traceparent` headers via [[OpenTelemetry as the Runtime Truth for Autonomous Agents]]).
- Correlation identifiers and shared telemetry enrichment.
- Standard authentication and authorization handlers (workload identity, mTLS, token acquisition, and token caching as detailed in [[Service-to-Service Authentication in Distributed Runtimes]]).
- Guidelines for [[Propagating User Context Between Services|propagating user context]] (tenant IDs, actor claims, audit context).
- PII-safe logging rules and error envelope formatting (e.g., RFC 7807 Problem Details).
- Base resilience mechanics (standardized Polly policies, retry backoffs, connection timeouts).
- Service discovery and dynamic endpoint resolution.

This division ensures that a client package from Service B does not dictate how Service A constructs its domain, handles errors, or configures its runtime.

---

## Option 1: Service B Publishes a Contracts NuGet

In this model, the team owning Service B publishes a lightweight, passive package containing only transport models:

```text
ServiceB.Contracts
```

The package contains pure data transfer objects (DTOs):

```csharp
public sealed record GetCustomerResponse(
    string Id,
    string Name,
    string Status);
```

Service A references the package and serializes or deserializes directly to these types.

### Advantages

- **Single Wire Definition**: Eliminates manual schema duplication across teams working in the same ecosystem.
- **Compile-Time Safety**: Breaking changes to properties in the package trigger compile errors in Service A.
- **Low Ceremony**: Extremely easy to set up and distribute in a homogeneous environment.
- **Explicit Version Tracking**: NuGet dependency versioning makes upstream changes visible in dependency graphs.

### Risks

- **Release Cadence Coupling**: Service A's build can become tightly coupled to Service B's library release cadence.
- **Version Skew**: Referencing the newest package does not guarantee the deployed instance of Service B is running that version.
- **Domain Pollution**: Developers are easily tempted to pass Service B's DTOs straight into Service A's domain handlers, entities, and database queries.
- **Behavior Creep**: Over time, teams often sneak validation rules, helper methods, extension libraries, or JSON converter dependencies into this "contracts" assembly.
- **Implementation Leakage**: Consumers often begin relying on the internal C# type system rather than treating the interaction as an external HTTP contract.

### Rules for Contracts Packages

If you distribute contracts via a shared package, treat them as immutable wire descriptions, not shared domain libraries.

Never include:
- Domain business logic or state transitions.
- Validation routines and business rules.
- Heavy external dependencies (e.g., FluentValidation, Entity Framework attributes).
- Dependency injection extension methods.
- Database mapping attributes.
- Complex class inheritance hierarchies.

```csharp
// BAD: Domain behavior, validation, and mutable logic leaked into a contracts package
public sealed class Customer
{
    public string Status { get; set; }

    public bool CanPlaceOrder()
    {
        // Business logic owned by Service B leaking into consumers
        return Status == "Active";
    }

    public void Validate()
    {
        // Validation logic owned by Service B leaking into consumers
        if (string.IsNullOrWhiteSpace(Status))
            throw new ValidationException("Status cannot be empty");
    }
}

// GOOD: Passive, immutable transport DTO
public sealed record CustomerResponse(
    string Id,
    string Status);
```

A contracts package must describe network messages, nothing more. It should never export the internal domain model or business rules of Service B.

---

## Option 2: Service B Publishes a Full Client NuGet

Here, the Service B team publishes a full-featured client library:

```text
ServiceB.Client
```

Service A installs the package and registers it during application startup:

```csharp
services.AddServiceBClient(options =>
{
    options.BaseAddress = configuration["ServiceB:BaseAddress"];
});
```

Application handlers inject the client interface:

```csharp
public sealed class OrderHandler(IServiceBClient serviceBClient)
{
    public async Task HandleAsync(PlaceOrder command, CancellationToken ct)
    {
        var customer = await serviceBClient.GetCustomerAsync(command.CustomerId, ct);
        // ...
    }
}
```

The package typically wraps:
- Endpoint URLs and HTTP verbs.
- Request and response serialization.
- Dependency injection setup extensions.
- Client credential and token acquisition logic.
- HTTP status code checks and error deserialization.
- Embedded telemetry and resilience pipelines.

### Advantages

- **Zero-Boilerplate Integration**: Downstream teams can onboard and make calls in minutes.
- **Encapsulated Protocol Details**: Complex multipart queries, specific header requirements, or strange legacy quirks are handled internally by the team that built them.
- **Bug Fix Distribution**: Protocol-level serialization bugs or incorrect route bindings can be fixed centrally in the client library.
- **Uniform Protocol Usage**: Ensures every consumer hits the endpoints with the correct headers, parameters, and compression settings.

### Risks

A full client SDK often takes on too much responsibility. It frequently configures:
- Hardcoded retries and Polly policies.
- Fixed timeout thresholds that do not match the consumer's SLA.
- Bespoke logging pipelines that bypass the consumer's Serilog or OpenTelemetry configurations.
- Custom exception hierarchies that swallow HTTP context and surface generic runtime exceptions.
- Global `HttpClientHandler` settings that cause socket issues or conflict with service mesh sidecars.

This leads to several concrete production issues:
- **Hidden Runtime Policies**: Service A cannot predict how many times a call will retry or when it will time out.
- **Telemetry Disconnects**: Duplicate spans, missing traceparents, or inconsistent field names in logs.
- **Dependency Hell**: Version conflicts between client libraries needing different versions of `System.Text.Json`, `Polly`, or `Azure.Core`.
- **Domain Inversion**: Business logic gets embedded in the client, making it impossible for Service A to treat edge cases differently.

### The Guiding Principle

> A service-specific SDK must only own the transport mechanics of the provider's protocol. It must never dictate the operational, resilience, or telemetry policy of the consuming application.

If an SDK is provided, keep it strictly thin.

---

## Option 3: Service A Generates a Client from OpenAPI

In this approach, Service B publishes a formal, machine-readable contract:

```text
openapi.json
```

Service A pulls this contract during its build or code-generation step, using tools such as Microsoft Kiota, NSwag, or openapi-generator to generate a client.

### Advantages

- **Platform Neutrality**: Works seamlessly across heterogeneous environments where Service B is written in Go and Service A is written in .NET.
- **Contract as the Source of Truth**: The OpenAPI specification is the authoritative document. Code generation guarantees alignment with the documented API.
- **Consumer Independence**: Service A decides when to update, what code to generate, and how to configure the generated output.
- **No Shared Binary Dependencies**: Completely decouples package release pipelines and eliminates library version conflicts.

### Risks

- **Generated Code Bloat**: Generators often produce thousands of lines of verbose, hard-to-read code and hundreds of models for endpoints Service A never calls.
- **Schema Drift vs. Semantic Drift**: The schema may generate cleanly, but runtime behavior or field semantics may have changed in ways the OpenAPI file cannot express.
- **Type Pollution**: Generated types can easily leak into business logic if developers inject the generated client directly into domain handlers.
- **Tooling Churn**: Generator updates can cause massive, noisy Git diffs across generated files.

### Recommended Pattern: Treat Generated Code as an Infrastructure Detail

Never let generated clients escape your infrastructure layer. Wrap the generated client inside an application port:

```text
Application Core
  └── ICustomerRiskProvider (Domain Port owned by Service A)

Infrastructure Layer
  ├── GeneratedServiceBClient (Generated via OpenAPI)
  └── ServiceBCustomerRiskProvider (Adapter implementing the Port)
```

The application logic depends exclusively on a domain-owned interface:

```csharp
public interface ICustomerRiskProvider
{
    Task<RiskLevel> GetRiskAsync(
        CustomerId customerId,
        CancellationToken cancellationToken);
}
```

The infrastructure adapter calls the generated client and maps the output into Service A's domain types:

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

        return MapToRiskLevel(response);
    }

    private static RiskLevel MapToRiskLevel(CustomerGeneratedDto dto)
    {
        return dto.Status switch
        {
            "Restricted" => RiskLevel.High,
            "Active" => RiskLevel.Low,
            _ => RiskLevel.Unknown
        };
    }
}
```

This isolates generated code completely. If you switch from a generated client to a handwritten one, not a single line of business logic changes.

---

## Option 4: Service A Implements a Small Local Client

If Service A only calls one or two endpoints and needs three fields out of a fifty-field response, building a hand-crafted HTTP adapter inside Service A is often the cleanest choice.

First, define the port Service A actually needs:

```csharp
public interface ICustomerStatusProvider
{
    Task<CustomerStatus?> FindAsync(
        CustomerId customerId,
        CancellationToken cancellationToken);
}
```

Then implement it with a standard, typed `HttpClient`:

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

    // Local, private DTO representing only what Service A cares about
    private sealed record ServiceBResponse(
        string Code,
        bool IsActive);
}
```

### Advantages

- **Zero External Dependencies**: No packages to restore, no code generators in your build pipeline, and no shared assemblies.
- **Minimal Surface Area**: Consumes only the fields needed for the use case; upstream changes to unused fields will not break Service A.
- **Full Transparency**: Timeouts, headers, serialization, and error handling are explicit and easy to step through in a debugger.
- **Strict Domain Isolation**: Service B's wire models remain private implementation details inside the adapter.

### Risks

- **Manual Maintenance**: If Service B changes route definitions or renames required fields, the adapter must be updated manually.
- **Duplicated Transport Logic**: Different consumer services may end up writing similar boilerplate for the same upstream API.
- **Inconsistent Error Handling**: Without disciplined testing, local implementations may misinterpret status codes or fail to handle transient network errors properly.

### When to Use It

- Service A needs a tiny slice of an otherwise large, complex API.
- The upstream API is stable and rarely changes.
- The platform already provides standard HTTP handlers for telemetry, authentication, and resilience.
- Bringing in a heavy SDK or running a code generator would introduce unnecessary complexity.

---

## Option 5: Service B Publishes an RPC-Like Interface

Some teams use declarative HTTP libraries (such as Refit or RestEase in .NET) to turn an annotated C# interface into a dynamic HTTP client:

```csharp
public interface IServiceBApi
{
    [Get("/customers/{id}")]
    Task<CustomerResponse> GetCustomerAsync(
        string id,
        CancellationToken cancellationToken);
}
```

Service A registers this interface in its DI container and injects it directly into application components.

### Advantages

- **Minimal Boilerplate**: Eliminates handwritten serialization and URL concatenation.
- **Clear Method Signatures**: Makes API routes and parameters explicit in standard C# syntax.
- **Fast Prototyping**: Ideal for internal services during early development phases.

### The Pitfall: The Local-Call Illusion

Consider this invocation:

```csharp
var customer = await serviceBApi.GetCustomerAsync(id, cancellationToken);
```

Syntactically, this looks identical to an in-memory method invocation on a local service. In reality, it:
- Crosses a network boundary, traversing switches, routers, and firewalls.
- Can fail with a DNS lookup failure, TCP reset, or TLS handshake timeout.
- Can take anywhere from 5 milliseconds to 30 seconds depending on upstream load.
- May execute multiple times behind the scenes if a retry handler is configured.
- Can return partial responses or leave resources in indeterminate states.
- Can fail due to expired OAuth tokens or revoked service permissions.

When developers mistake remote calls for local operations, they omit timeouts, call remote services inside loops, run calls inside distributed database transactions, and fail to build fallback strategies.

### The Rule for RPC-Style Interfaces

Keep declarative RPC interfaces confined to your **infrastructure layer**. Never inject them directly into domain handlers or application use cases. 

Wrap the RPC interface inside an application-owned port:

```text
Application Layer:
  ICustomerRiskProvider (Owned by Service A)
       ▲
       │ implements
Infrastructure Layer:
  ServiceBCustomerRiskAdapter
       │ calls
  IServiceBApi (Refit / RestEase declarative interface)
```

The adapter catches network-level exceptions, translates HTTP-specific status codes into domain-level outcomes, and ensures the rest of your application never handles raw transport concerns.

---

## The Interface Should Usually Be Owned by Service A

A core principle of hexagonal architecture and Domain-Driven Design is:

> The provider owns the wire contract.  
> The consumer owns the interface that describes why it needs that contract.

Service B exposes general capabilities:

```csharp
// Service B's capability view
public interface IServiceBApi
{
    Task<CustomerDto> GetCustomerAsync(string id, CancellationToken ct);
}
```

Service A needs to satisfy a specific business use case:

```csharp
// Service A's domain requirement
public interface ICustomerEligibilitySource
{
    Task<CustomerEligibility> GetEligibilityAsync(
        CustomerId customerId, 
        CancellationToken cancellationToken);
}
```

These two abstractions address fundamentally different concerns:

1. **Decoupled Evolution**: Service B might replace its REST API with a gRPC endpoint, an event-driven cache, or an internal database lookup. If Service A owns its interface, its business logic remains completely untouched—only the infrastructure adapter changes.
2. **True Domain Isolation**: Service B’s transport models never enter Service A's business logic.
3. **Simple, Predictable Unit Testing**: Mocking `ICustomerEligibilitySource` in Service A's domain tests is straightforward. Mocking an external HTTP client or an upstream SDK with nested models and HTTP responses is tedious and brittle.
4. **Composition**: A single method on `ICustomerEligibilitySource` might call Service B, query a local Redis cache, and fall back to a default value if Service B is degraded.

---

## Error Handling Responsibilities

Shared client libraries often handle errors poorly by catching everything and throwing a single, generic exception:

```csharp
// The anti-pattern: flattening all failure modes into one exception
throw new ServiceBClientException("Call failed", ex);
```

This makes it impossible for downstream code to determine what actually went wrong. Robust inter-service communication requires distinguishing between three distinct failure domains:

```text
+-----------------------------------------------------------------------------+
|                            FAILURE CATEGORIES                               |
+-----------------------------------------------------------------------------+
| 1. TRANSPORT FAILURES                                                       |
|    - DNS resolution failed, connection refused, connection reset            |
|    - TLS handshake failure, raw TCP timeout                                 |
|    - Meaning: The byte stream never made it to Service B (or return dropped)|
|    - Action: Evaluate retry suitability, check network/mesh health         |
+-----------------------------------------------------------------------------+
| 2. PROTOCOL FAILURES                                                        |
|    - HTTP 502 Bad Gateway, 503 Service Unavailable, 504 Gateway Timeout     |
|    - Invalid HTTP headers, broken chunked transfer, unparseable JSON        |
|    - Meaning: An intermediary failed, or Service B returned garbage         |
|    - Action: Trigger circuit breaker, short-circuit, fallback               |
+-----------------------------------------------------------------------------+
| 3. BUSINESS RESPONSES                                                       |
|    - 404 Not Found (Domain entity does not exist)                           |
|    - 409 Conflict (Concurrency conflict, duplicate idempotency key)        |
|    - 422 Unprocessable Entity (Business validation failure)                 |
|    - Meaning: The message was received, parsed, and rejected by B's domain  |
|    - Action: Map to consumer domain state; do NOT blindly retry             |
+-----------------------------------------------------------------------------+
```

A client should never conflate a network timeout with a business validation failure.

---

## Who Interprets Errors?

Service B is responsible for returning clear, machine-readable error details rather than arbitrary human-readable text. Using the RFC 7807 Problem Details standard is the industry baseline:

```json
{
  "type": "https://errors.company.com/customer-not-found",
  "title": "Customer not found",
  "status": 404,
  "code": "customer_not_found",
  "detail": "Customer 849201 does not exist in the active tenant.",
  "traceId": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
}
```

The platform establishes the standard JSON envelope structure. Service B defines the stable, domain-specific `code` strings (`customer_not_found`, `account_suspended`, `insufficient_funds`).

Service A determines what that error code means **in the context of its own operation**:

- In an *Order Checkout* use case: `customer_not_found` indicates corrupted state or fraud. The checkout should fail immediately and log an alert.
- In a *User Registration* use case: `customer_not_found` is an expected outcome indicating the username or customer ID is available.
- In a *Batch Sync* use case: `customer_not_found` means Service A should create a new stub record and continue.

Upstream clients should never throw downstream domain exceptions:

```csharp
// ANTI-PATTERN: Service B's client deciding what an error means to Service A
if (response.StatusCode == HttpStatusCode.NotFound)
{
    throw new CustomerMissingFromOrderException(); // B cannot possibly know this context!
}
```

Instead, the transport client returns a structured result:

```csharp
public sealed record ServiceBResponse<T>(
    bool IsSuccess,
    T? Value,
    ServiceBError? Error);

public sealed record ServiceBError(
    string Code,
    HttpStatusCode StatusCode,
    string? Message,
    string? TraceId);
```

Service A's adapter examines `ServiceBError.Code` and maps it to the appropriate outcome for its specific use case.

---

## Logging and Tracing

When every team builds its own logging and tracing setup into their client packages, observability quickly falls apart. You end up with:
- Redundant log messages for a single HTTP call (one from the client, one from the caller, one from `HttpClient`).
- Sensitive data (passwords, tokens, PII) accidentally logged in request and response bodies.
- Broken distributed traces due to inconsistent header propagation.
- Mismatched metric names (`http_client_requests_duration` vs `service_b_call_latency_ms`).

### The Golden Rule of Inter-Service Observability

> Client libraries may enrich distributed traces and telemetry, but they must never construct or configure the telemetry infrastructure itself.

```text
Platform Layer (Shared)
  └── Registers OpenTelemetry, W3C TraceContext Handlers, Redaction Rules, Base Metrics
        ▼
Service A Configuration
  └── Binds platform handlers to Service B's HttpClient
        ▼
Service B Client (Enrichment Only)
  └── Adds span tags: { "peer.service": "ServiceB", "rpc.method": "GetCustomer" }
```

The platform configures the core pipeline:
- Standard W3C `traceparent` and `tracestate` header injection.
- Consistent OpenTelemetry semantic conventions for HTTP metrics.
- PII-safe log sanitization pipelines.

The Service B client or local adapter simply enriches the current active activity:

```csharp
var activity = Activity.Current;
activity?.SetTag("service_b.operation", "get_customer");
activity?.SetTag("service_b.error_code", error?.Code);
```

---

## Retry and Timeout Ownership

Resilience policies are often misplaced in distributed systems. A client library should not ship with hardcoded retries and timeouts baked into its internals.

Consider the asymmetry of knowledge between the two services:

```text
Service B Knows:
  - Which endpoints are safe to retry (idempotent operations like GET, PUT, or POST with Idempotency-Key).
  - Its normal internal latency profile (p50 of 20ms, p99 of 400ms).
  - Which error states are transient vs permanent.

Service A Knows:
  - Its total end-to-end deadline (e.g., an interactive UI user is waiting on a 2-second timeout).
  - How many other downstream services it needs to call to complete the overall request.
  - Whether a fallback is acceptable if Service B is down (e.g., returning cached or degraded data).
  - The business cost of failing fast versus waiting for a retry.
```

Service B should document its idempotency guarantees and latency expectations. Service A must configure the final execution budget.

In modern .NET, configure resilience explicitly in Service A using `Microsoft.Extensions.Resilience`:

```csharp
services
    .AddHttpClient<IServiceBTransportClient, ServiceBTransportClient>(client =>
    {
        client.BaseAddress = configuration.GetServiceUri("ServiceB");
    })
    .AddStandardHttpTelemetry() // Platform-owned logging & tracing
    .AddResilienceHandler("service-b-pipeline", pipeline =>
    {
        // Service A sets the total timeout budget for this specific use case
        pipeline.AddTimeout(TimeSpan.FromSeconds(2.5));

        // Service A configures retry behavior based on its tolerance for latency
        pipeline.AddRetry(new HttpRetryStrategyOptions
        {
            MaxRetryAttempts = 2,
            BackoffType = DelayBackoffType.Exponential,
            Delay = TimeSpan.FromMilliseconds(50),
            // Only retry safe, transient status codes
            ShouldHandle = new PredicateBuilder<HttpResponseMessage>()
                .Handle<HttpRequestException>()
                .HandleResult(r => r.StatusCode is HttpStatusCode.RequestTimeout 
                                                or HttpStatusCode.BadGateway 
                                                or HttpStatusCode.ServiceUnavailable 
                                                or HttpStatusCode.GatewayTimeout)
        });

        // Add a circuit breaker to prevent cascading failures
        pipeline.AddCircuitBreaker(new HttpCircuitBreakerStrategyOptions
        {
            FailureRatio = 0.5,
            SamplingDuration = TimeSpan.FromSeconds(10),
            MinimumThroughput = 8,
            BreakDuration = TimeSpan.FromSeconds(30)
        });
    });
```

The policy is declared and tuned right where the operational context is understood: inside Service A.

---

## Authentication Responsibility

Authentication mechanics must be decoupled from application-specific business endpoints.

```text
+-----------------------------------------------------------------------------+
|                   AUTHENTICATION RESPONSIBILITY MODEL                       |
+-----------------------------------------------------------------------------+
|                                                                             |
| 1. Platform Infrastructure:                                                 |
|    - Manages workload identity (e.g., Azure Managed Identity, SPIFFE/SPIRE).|
|    - Handles token acquisition, in-memory caching, and proactive renewal.   |
|    - Handles mutual TLS (mTLS) certificate rotation and handshakes.         |
|                                                                             |
| 2. Service B (Provider):                                                    |
|    - Defines the required OAuth2 scopes, claims, and audience targets.       |
|    - Example: Audience: "api://service-b", Scope: "customers.read"         |
|                                                                             |
| 3. Service A (Consumer):                                                    |
|    - Configures which client credentials or managed identity to use.        |
|    - Assigns the required scope to its configured HTTP client pipeline.     |
|                                                                             |
+-----------------------------------------------------------------------------+
```

Service B's client package must never implement its own token caching loops, file-based credential loaders, or custom crypto routines. It should rely on platform-provided delegating handlers:

```csharp
// Standard platform delegating handler injected into Service A's client registration
services.AddHttpClient<IServiceBTransportClient, ServiceBTransportClient>()
    .AddPlatformTokenAcquisitionHandler(options =>
    {
        options.Audience = "api://service-b";
        options.Scopes = ["customers.read"];
    });
```

For deeper design decisions regarding caller vs. user identities, review [[Service vs User Authorization Models]].

---

## API Compatibility

Regardless of whether you use generated clients, manual adapters, or contract packages, **Service B must always assume version skew exists in production.**

During a rolling deployment, blue-green deployment, or canary release:
- New instances of Service B will process requests from old instances of Service A.
- Old instances of Service B will process requests from new instances of Service A.
- Downstream consumers in other teams will update their dependencies on their own schedules—often weeks or months later.

Every public contract must be designed for forward and backward compatibility.

---

## Usually Safe Changes

These changes generally do not break consumers, provided consumers follow standard serialization hygiene:

- Adding a new endpoint.
- Adding an optional request parameter or body property.
- Adding a new property to a response payload (provided consumers ignore unknown fields).
- Adding a new machine-readable error code (provided consumers have a fallback for unmodeled errors).
- Adding an optional query string parameter with a safe default on the server.

Always verify these changes against your code generators and serializers. Some strict serializers fail on unexpected JSON fields by default.

---

## Common Breaking Changes

These changes break consumers at runtime, even if the schema appears structurally valid:

- Removing an endpoint or changing its HTTP verb.
- Renaming a property or field name in a request or response.
- Changing the data type of an existing property (e.g., converting an integer to a string).
- Changing an optional request property into a required one.
- Altering the semantics of an existing value. For instance:

```text
Previously:  "status": "active"  ──► "Customer is verified and eligible for purchases"
Updated to:  "status": "active"  ──► "Customer record exists and is not soft-deleted"
```

The JSON payload deserializes without a single schema error, but Service A makes incorrect business decisions because the underlying meaning changed. **Semantic compatibility is just as critical as schema compatibility.**

---

## Enum Compatibility

Enums are one of the most common causes of hidden breaking changes in distributed systems.

Assume Service B returns an enum representing customer state:

```json
{
  "status": "active"
}
```

Six months later, Service B introduces a new state: `"suspended"`.

If Service A uses a strictly typed enum and an exhaustive switch statement, one of two failures occurs:
1. **Deserialization Crash**: The JSON parser throws an exception because `"suspended"` is not a valid enum member.
2. **Unhandled Branch Panic**: The message deserializes, but the application throws an unexpected runtime exception.

```csharp
// DANGEROUS: Strict enum assumptions break on additive upstream changes
public enum CustomerStatus
{
    Active,
    Inactive
}

// In application code:
return response.Status switch
{
    CustomerStatus.Active => Eligibility.Allowed,
    CustomerStatus.Inactive => Eligibility.Denied,
    _ => throw new ArgumentOutOfRangeException() // CRASHES when Service B adds "Suspended"
};
```

### The Resilient Approach: Tolerant Matching with Unknown Fallbacks

Consume enums as strings or use serializers configured for tolerant parsing. Always provide an explicit fallback for unmodeled values:

```csharp
// RESILIENT: String-based matching with safe business fallback
public Eligibility EvaluateEligibility(string rawStatus)
{
    return rawStatus switch
    {
        "active" => Eligibility.Allowed,
        "inactive" => Eligibility.Denied,
        _ => Eligibility.Unknown // Safe fallback: treat unrecognized states defensively
    };
}
```

Design every consumer to gracefully handle unexpected enum values from upstream providers.

---

## Request Compatibility

When evolving request payloads, follow Postel’s Law (*be conservative in what you send, and liberal in what you accept*):

- Never make an optional property required in a subsequent release.
- If an operation requires a new parameter, provide a sensible default on the server so existing callers can omit it without failing.
- If a parameter change fundamentally alters the business operation, create a new endpoint route or an explicitly versioned API.

---

## Response Compatibility

When returning response payloads:
- Ensure your JSON serializer omits null fields if they add no value, or keep nullability consistent.
- Never switch an empty array to `null`:

```json
// Predictable contract:
{ "tags": [] }

// DANGEROUS change:
{ "tags": null }
```

Turning empty collections into `null` frequently triggers `NullReferenceException` crashes in generated clients, even if handwritten code handles it.

---

## Error Compatibility

Error contracts are part of your public API. Treat them with the same backward compatibility discipline as your success payloads.

Never change:
- Machine-readable error codes (e.g., changing `"customer_not_found"` to `"err_client_missing"`).
- HTTP status codes for established outcomes (e.g., changing a `404 Not Found` to a `400 Bad Request`).
- The semantic meaning of an existing error code.

Do not rely on human-readable error messages for programmatic logic:

```csharp
// FRAGILE: Relies on string matching against human-readable text
if (error.Message.Contains("Customer was not found")) 
{
    // ...
}

// RESILIENT: Relies on an immutable, machine-readable error code
if (error.Code == "customer_not_found")
{
    // ...
}
```

---

## Versioning Strategies

### 1. Additive Evolution (Preferred)

Evolve APIs additively. Add new optional properties, new endpoints, and new response fields while keeping existing fields intact. Additive evolution avoids the operational overhead of running parallel versions in production.

### 2. Explicit Major API Versioning

When an endpoint requires fundamental structural or semantic changes that cannot be introduced additively, introduce an explicit new version:

```text
POST /api/v1/orders
POST /api/v2/orders
```

Alternatively, use media-type or header-based versioning:

```http
Accept: application/vnd.company.order.v2+json
```

### 3. Parallel Version Deprecation

When deploying a new API version:
1. Run Version 1 and Version 2 in production concurrently.
2. Direct all new feature work in consumers to Version 2.
3. Monitor production metrics to identify which consumers are still calling Version 1.
4. Establish an explicit deprecation timeline, communicate with consuming teams, and remove Version 1 only after its traffic drops to zero.

Never bump an API version for minor, non-breaking modifications. Maintaining multiple parallel versions creates long-term operational baggage.

---

## Source of Truth

To keep documentation, types, and wire behaviors aligned, establish a single source of truth for the API contract:

```text
                  Single Source of Truth
                  (OpenAPI Spec / Proto)
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
   Generated SDK       Generated Docs     Breaking-Change
  (or Local Adapters)  (Developer Portal)  CI Verification
```

Avoid scenarios where an assembly, an OpenAPI file, and a documentation page are maintained by hand separately:

```text
ServiceB.Contracts.dll  ◄─── DRIFT ───►  openapi.json  ◄─── DRIFT ───►  Developer Wiki
```

When manual definitions drift apart, teams spend hours debugging discrepancies between the documentation and reality.

A reliable pipeline generates the OpenAPI document directly from Service B's code during compilation, or uses a contract-first approach where code and documentation are generated from a canonical specification repository.

---

## Compatibility Testing

Verify contract compatibility automatically in your continuous integration (CI) pipeline:

### 1. Automated Schema Diffs

In Service B's build pipeline, compare the newly compiled OpenAPI schema against the version currently running in production using tools like `openapi-diff`:

```text
CI Check:
  - Error if an existing endpoint was removed.
  - Error if an existing response field was renamed or removed.
  - Error if a required request field was added without a default.
  - Warn if new enum values were introduced.
```

### 2. Consumer-Driven Contract Testing (e.g., Pact)

Consumer-Driven Contract Testing flips the verification dynamic:
- Service A defines the minimal slice of Service B it relies on (e.g., `GET /customers/123`, requiring only `id` and `status`).
- This expectation is published as a contract artifact.
- Service B runs these contract tests in its build pipeline before merging code. If an upstream change breaks Service A's contract, Service B's build fails.

This provides confidence when changing APIs that have dozens of downstream consumers.

### 3. End-to-End Smoke Tests

After deploying Service B to staging or production canary environments, execute smoke tests that validate:
- Authentication handshake and token acceptance.
- Correct headers and traceparent propagation.
- Real response payload serialization.

---

## Partial Contract Consumption

Service A should only deserialize and interact with the data it needs to fulfill its business capability.

Suppose Service B's customer endpoint returns a comprehensive payload:

```json
{
  "id": "cust_9921",
  "name": "Jane Doe",
  "status": "active",
  "email": "jane@example.com",
  "address": { "street": "123 Main St", "zip": "90210" },
  "creditScore": 750,
  "preferences": { "marketing": false, "darkMode": true },
  "audit": { "createdAt": "2023-01-01T00:00:00Z" }
}
```

If Service A's only job is to verify whether an account is active before processing an order, its transport model should reflect only that:

```csharp
// Service A's internal, focused deserialization model
internal sealed record ServiceBCustomerStatusDto(
    string Id,
    string Status);
```

Ensure your JSON deserializer is configured to ignore unknown fields (the default in `System.Text.Json`). 

This makes Service A immune to changes, additions, or deprecations affecting any of the other fields in Service B's payload.

---

## Avoid Shared Domain Models

Do not share domain entities across service boundaries via shared libraries.

```text
+-----------------------------------------------------------------------------+
|                      THE SHARED DOMAIN MODEL TRAP                           |
+-----------------------------------------------------------------------------+
|                                                                             |
|                     Shared Domain Package: Customer.dll                     |
|                   ┌─────────────────────────────────────┐                   |
|                   │ - CustomerId                        │                   |
|                   │ - Address, BillingInfo, Preferences │                   |
|                   │ - CreditRules, DiscountCalculators  │                   |
|                   └─────────────────────────────────────┘                   |
|                                      ▲                                      |
|                 ┌────────────────────┴────────────────────┐                 |
|                 │                                         │                 |
|      SERVICE A (Billing)                       SERVICE B (Shipping)         |
|      Requires: Balance & Invoices              Requires: Address & Carrier  |
|                                                                             |
+-----------------------------------------------------------------------------+
```

While both services deal with a concept called "Customer", their bounded contexts require completely different views of that entity:
- To **Service B (Identity/Profile)**: A Customer is a complete record containing personal identity, addresses, login audit trails, and privacy preferences.
- To **Service A (Billing)**: A Customer is simply an ID, a tax exemption status, and an outstanding account balance.

Sharing a single `Customer` class creates tight coupling:
- A change requested by Billing forces a redeployment and testing cycle for Shipping.
- Unnecessary validation dependencies and logic leak across boundaries.
- Database annotations or ORM configurations from one service pollute the other.

Keep domain models private to each service. Share only passive, wire-level transport DTOs.

---

## Thin Client vs. Smart Client

When designing an official client library, resist the pressure to turn it into a "smart" client:

```text
+------------------------------------+------------------------------------+
|            THIN CLIENT             |            SMART CLIENT            |
|       (Recommended Pattern)        |       (Architectural Trap)         |
+------------------------------------+------------------------------------+
| - Contains endpoints and verbs     | - Bakes in opinionated retries     |
| - Pure serialization / DTO parsing | - Embeds custom caching logic      |
| - Unpacks error envelopes          | - Maps domain exceptions internally|
| - Leaves resilience to consumer    | - Injects custom logging pipelines |
| - Zero opinion on domain usage     | - Hides raw network realities      |
+------------------------------------+------------------------------------+
```

Smart clients seem helpful at first because they reduce initial consumer boilerplate. Over time, however, they become unmaintainable bottlenecks:
- One consumer wants to cache responses for 10 minutes; another requires real-time data.
- One consumer wants to retry 5 times; another is on an interactive UI thread and needs to fail fast after 500ms.
- Upgrading a dependency inside a smart client forces an upgrade across all consuming applications simultaneously.

**Default to thin clients.** Let the consuming application manage its own caching, retries, and domain translations.

---

## Recommended Layering in Service A

To maintain clean boundaries, organize Service A’s code to keep external integration concerns cleanly separated from your core domain:

```text
ServiceA.src
│
├── Domain / Application (Core Business Logic)
│   ├── UseCases/
│   │   └── PlaceOrderHandler.cs
│   └── Ports/
│       └── ICustomerEligibilitySource.cs     ◄── Consumer-owned interface
│
└── Infrastructure (External Communications)
    └── ExternalServices/
        └── ServiceB/
            ├── ServiceBTransportClient.cs    ◄── Thin HTTP client / generated SDK
            ├── ServiceBCustomerAdapter.cs    ◄── Implements ICustomerEligibilitySource
            ├── Models/
            │   └── ServiceBCustomerResponse.cs
            └── ServiceBOptions.cs
```

### The Domain Port

```csharp
namespace ServiceA.Domain.Ports;

public interface ICustomerEligibilitySource
{
    Task<CustomerEligibility> GetEligibilityAsync(
        CustomerId customerId,
        CancellationToken cancellationToken);
}
```

### The Infrastructure Adapter (Anti-Corruption Layer)

```csharp
namespace ServiceA.Infrastructure.ExternalServices.ServiceB;

internal sealed class ServiceBCustomerAdapter(
    IServiceBTransportClient transportClient,
    ILogger<ServiceBCustomerAdapter> logger)
    : ICustomerEligibilitySource
{
    public async Task<CustomerEligibility> GetEligibilityAsync(
        CustomerId customerId,
        CancellationToken cancellationToken)
    {
        var result = await transportClient.GetCustomerAsync(
            customerId.Value, 
            cancellationToken);

        // Handle business outcomes and error translations locally
        if (!result.IsSuccess)
        {
            if (result.Error?.Code == "customer_not_found")
            {
                logger.LogInformation(
                    "Customer {CustomerId} not found in Service B; treating as ineligible.", 
                    customerId);
                    
                return CustomerEligibility.Ineligible;
            }

            logger.LogError(
                "Unexpected failure calling Service B: {ErrorCode}", 
                result.Error?.Code);
                
            throw new UpstreamServiceException(
                $"Failed to evaluate customer eligibility. Upstream error: {result.Error?.Code}");
        }

        // Map upstream wire DTO into Service A's domain model
        return result.Value.Status switch
        {
            "Active" => CustomerEligibility.Eligible,
            "Suspended" => CustomerEligibility.Ineligible,
            _ => CustomerEligibility.RequiresManualReview
        };
    }
}
```

This layout gives you clean separation of concerns:
- Business use cases depend exclusively on `ICustomerEligibilitySource`.
- Service B's wire models, HTTP status codes, and network exceptions are caught and resolved entirely inside `ServiceBCustomerAdapter`.
- If Service B changes its API or is replaced by another system, only the files inside the `Infrastructure/ExternalServices/ServiceB/` directory change.

---

## Recommended Decision Model

Use this decision matrix when choosing an integration approach:

```text
                           How many consumer teams?
                                      │
                 ┌────────────────────┴────────────────────┐
                 ▼                                         ▼
            Single Team                               Many Teams
                 │                                         │
        API complexity & scope?                    Heterogeneous tech stack?
        ┌────────┴────────┐                       ┌────────┴────────┐
        ▼                 ▼                       ▼                 ▼
   Small / 1-2 eps   Large / Many eps            Yes                No
        │                 │                       │                 │
        ▼                 ▼                       ▼                 ▼
 [Option 4: Local]  [Option 3: OpenAPI]     [Option 3: OpenAPI]  Do you have resources
    Small Adapter     Code Generation         Code Generation    to maintain an SDK?
                                                                    ┌───┴───┐
                                                                    ▼       ▼
                                                                   Yes      No
                                                                    │       │
                                                                    ▼       ▼
                                                             [Option 2: SDK] [Option 1: Contracts]
                                                               Thin Client    Passive Package
```

### Summary of Best Fits

- **Use a Contracts Package (Option 1)** when all services are built on the same runtime, teams coordinate closely, and you need simple compile-time type safety for passive DTOs.
- **Provide an Official Thin Client (Option 2)** when Service B is a core capability called by dozens of teams, and centralizing serialization and route definitions prevents widespread duplication. Keep it thin.
- **Generate from OpenAPI (Option 3)** when consumers are written in different programming languages, or when you want to automate client creation from a canonical specification.
- **Write a Small Local Adapter (Option 4)** when you only consume a handful of fields from one or two endpoints, the upstream API is stable, and you want zero external package dependencies.
- **Use an RPC-Style Client (Option 5)** only for rapid prototyping or simple internal utilities, and keep it confined to your infrastructure layer.

---

## Warning Signs in Code Reviews

Watch for these warning signs during pull request reviews:

- **Upstream DTOs in Domain Signatures**: A handler method or domain entity signature references a type from `ServiceB.Contracts` or a generated client namespace.
- **Deep SDK Dependency Trees**: Installing a client library pulls in logging frameworks, Polly, or third-party JSON libraries that conflict with the consuming host.
- **Catch-All Exception Flattening**: The client catches all exceptions and rethrows a generic `ApiException`, destroying the original HTTP status code and error details.
- **Hidden, Hardcoded Retry Loops**: The client automatically retries non-idempotent `POST` requests without the caller's knowledge.
- **Direct Controller Injection**: Application handlers inject raw `HttpClient` or generated clients directly instead of programming against a local domain port.
- **Shared Database or Domain Libraries**: Service A references an assembly from Service B that contains Entity Framework configurations or database entities.
- **String Matching on Error Messages**: Downstream logic checks `if (ex.Message.Contains("404"))` instead of inspecting structured error codes.

---

## Practical Rules

1. **Provider owns the wire contract**: Service B owns endpoints, schemas, and error codes.
2. **Consumer owns the dependency**: Service A defines its own domain interfaces (ports) describing what it needs.
3. **Platform owns the pipes**: Logging frameworks, W3C trace propagation, token lifecycle, and mTLS belong to the shared platform.
4. **Isolate external models**: Keep transport DTOs in your infrastructure layer; map them to domain models at the boundary.
5. **Treat remote calls as fallible**: Never let an RPC library fool you into treating a network call like an in-memory function.
6. **Keep clients thin**: Never allow an SDK to configure global timeouts, application-wide retries, or custom logging engines.
7. **Control resilience at the consumer**: Timeouts and retries belong in Service A, where the operational SLA and use-case context are known.
8. **Use machine-readable error codes**: Base business decisions on stable, structured error codes, not HTTP text messages.
9. **Single source of truth**: Drive documentation, schemas, and clients from a single OpenAPI or Protobuf specification.
10. **Design for version skew**: Always assume callers will run older or newer versions of the contract during deployments.
11. **Use tolerant enum parsing**: Never use strict, exhaustive switches on upstream enums without an explicit fallback for unmodeled states.
12. **Consume only what you need**: Model only the properties your use case requires to avoid breaking on unrelated upstream changes.
13. **Do not share domain packages**: Share passive transport contracts, never internal domain models or validation rules.

---

## The Mental Model

A remote client library is not simply a convenience wrapper. It is an architectural boundary between two independently deployed, independently scaling systems.

The most resilient architecture always follows this path:

```text
Service B (Provider)
  └── Exposes canonical, versioned wire contract (OpenAPI / Proto)
            │
            ▼
Thin Transport Layer (SDK, Generated Client, or Raw HttpClient)
            │
            ▼
Service A Infrastructure (Adapter / Anti-Corruption Layer)
  └── Translates wire models and status codes to domain outcomes
            │
            ▼
Service A Domain (Application Core)
  └── Consumes application-owned port (ICustomerEligibilitySource)
```

Cross-cutting operational concerns are supplied orthogonal to application logic:

```text
Platform Infrastructure
  ├── Workload Identity & Token Management
  ├── OpenTelemetry W3C Distributed Trace Context
  └── Standard Resilience Mechanics
```

To summarize the relationship in three sentences:

> **Service B owns the contract.**  
> **Service A owns the dependency.**  
> **The platform owns the communication standards.**

---

## Related Notes

- **[[Service-to-Service Authentication in Distributed Runtimes]]**: Workload identity, token exchange, and mutual TLS for inter-service communication.
- **[[Service vs User Authorization Models]]**: Distinguishing caller identity from acting-on-behalf-of user delegation.
- **[[Propagating User Context Between Services]]**: Propagating trace context, tenant IDs, and user identity across synchronous calls.
- **[[Scaling a Modular Monolith with Local-or-Remote Module Execution]]**: Designing remote-capable contracts that can execute locally or over HTTP/gRPC.
- **[[Designing APIs for LLM-Generated Integration Code]]**: Designing strongly typed API contracts that automated tools and agents can reliably consume.
- **[[OpenTelemetry as the Runtime Truth for Autonomous Agents]]**: Instrumenting inter-service requests with standardized W3C trace context headers.
