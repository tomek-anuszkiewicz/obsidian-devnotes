---
title: Propagating User Context Between Services
tags:
  - distributed-systems
  - microservices
  - authentication
  - authorization
  - security
  - context-propagation
aliases:
  - User Context Propagation
  - Service Identity and End-User Identity
  - Orthogonal Identity and Context Separation
  - Secure Microservice Context Propagation
---

# Propagating User Context Between Services

## Context

In distributed systems, Service A frequently receives a request initiated by an end user and must subsequently call Service B to complete the operation:

```text
User U ──► API Gateway (Sanitizes headers, authenticates user)
                 │
                 ▼
            Service A (Authenticates as Service A via mTLS / Workload Identity)
                 │
                 ▼ [Propagates allowlisted headers: User-Id, Tenant-Id, traceparent]
            Service B (Verifies Service A identity ──► Validates User Context ──► Authorizes Resource Access)
```

When the request lands on Service B, that service needs to know:
- Which service made the network call,
- Which user originally initiated the operation,
- Which tenant the operation belongs to,
- Which trace and correlation identifiers track the execution chain,
- Whether the operation is authorized.

These concerns are interrelated, but conflating them into a single generic request context creates subtle security holes, confused-deputy vulnerabilities, and architectural rot.

A clean design strictly separates six distinct concerns:
- **Service identity:** Who is physically making the call over the wire.
- **User identity:** Who initiated the business operation.
- **Authorization:** Whether the requested operation is permitted on the target resource.
- **Audit context:** Who did what, when, and under what delegation chain.
- **Trace context:** The technical distributed execution chain across hops.
- **Tenant context:** The organizational boundary owning the target data.

---

## Core Principle

A reliable responsibility model follows three rules:

> **The calling service authenticates itself.**  
> **The user identifier is propagated as contextual metadata.**  
> **The service owning the resource decides how authorization should work.**

In practical terms:
- `userId` tells Service B whose operation this is.
- `service identity` tells Service B who is making the call.
- `authorization` determines whether the operation is allowed.

These three concepts must never be treated as interchangeable.

---

## Architectural Deep Dives

This guideline works alongside two dedicated architectural references:

1. **[[Service vs User Authorization Models]]**
   - Choosing between **Model 1** (Service B authorizes Service A) and **Model 2** (Service B authorizes the User).
   - Delegation vs. Impersonation (preserving technical caller vs. user initiator).
   - Dangers of forwarding browser cookies and raw user access tokens across internal networks.
   - Explicit token delegation via OAuth 2.0 Token Exchange (RFC 8693).
   - Structured audit logging models.

2. **[[User Context in Asynchronous Systems]]**
   - Context propagation through message brokers (RabbitMQ, Kafka, Azure Service Bus).
   - Dangers of storing live tokens in message queues or dead-letter queues.
   - Pre-authorization at acceptance time vs. post-authorization at execution time.
   - Context semantics for Commands vs. Domain Events.
   - Strongly-typed message context contracts.

---

## Authenticate the Calling Service Independently

Service B must verify the technical caller before it inspects or trusts any propagated user metadata:

```text
Authenticated caller: Service A
Original initiator:   User U
```

Standard service authentication mechanisms include:
- Workload identity (Kubernetes ServiceAccount tokens, AWS IAM Roles for Service Accounts, Azure Managed Identities),
- Mutual TLS (mTLS) with SPIFFE/SAN validation,
- Client credentials grant via OAuth 2.0 (service-to-service JWTs),
- Service mesh sidecar identity (Istio, Linkerd).

If Service B accepts requests from an unauthenticated caller, an attacker can forge any arbitrary user identifier:

```http
# Critical vulnerability: An unauthenticated caller supplying an arbitrary User-Id
POST /orders HTTP/1.1
Host: service-b.internal
X-User-Id: admin-user-42
```

Service B must verify that the request genuinely originated from an authorized service (such as Service A). Only after that caller identity is proven should Service B trust the downstream context headers.

### Edge Gateway Sanitization
The system boundary (API Gateway) must unconditionally strip, overwrite, or drop untrusted internal-context headers (`X-User-Id`, `X-Tenant-Id`, `X-Initiated-By-User-Id`) received from external clients. If an external client sends an `X-User-Id` header, the gateway must remove it, authenticate the incoming user credentials (session cookie, bearer token), and set its own trusted headers before forwarding internally.

---

## Trace Context Is Separate from User Context

Distributed tracing tracks physical execution hops. It uses standard W3C trace propagation (`traceparent`, `tracestate`). Keep this technical telemetry decoupled from business and security identity:

- **Trace context** answers: *Which technical execution chain does this call belong to?*
- **Correlation context** answers: *Which logical business workflow or batch job does this call belong to?*
- **Tenant context** answers: *Which organizational security boundary owns this data?*
- **User context** answers: *Which human or automated agent initiated the business intent?*

```text
traceId        = technical execution chain (W3C traceparent)
correlationId  = logical business operation or request family
tenantId       = organizational / security boundary
userId         = original initiator
```

These values often travel alongside one another in HTTP headers, but they belong to different operational contracts. Conflating W3C trace IDs with user identity risks leaking Personally Identifiable Information (PII) into telemetry collectors, APM tools, and log aggregators.

---

## Tenant Context

In multi-tenant architectures, `tenantId` is commonly propagated alongside `userId`.

Service B must never accept an arbitrary `X-Tenant-Id` header without verification. Doing so opens the door to cross-tenant data access if a compromised or buggy upstream service passes the wrong ID. The tenant must always be validated against an authenticated identity:
- Verified claims in a cryptographically signed token,
- An authenticated caller that is explicitly authorized to act on behalf of that tenant,
- An explicit database lookup confirming that the authenticated `userId` is an active member of `tenantId`.

> [!IMPORTANT]
> **Tenant Isolation Rule:** Tenant context must always be derived from or validated against an authenticated identity. Never permit cross-tenant data access based on an unverified header.

---

## HTTP Context Propagation and Allowlisting

For synchronous HTTP communication, Service A sends explicit, allowlisted headers:

```http
Authorization: Bearer <service-token>
X-Initiated-By-User-Id: user-123
X-Tenant-Id: tenant-7
X-Correlation-Id: operation-456
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

### Avoid Blind Header Propagation
A dangerous anti-pattern is copying all inbound HTTP headers directly to outbound downstream calls:

```text
Incoming Request ──► [Blind Header Copying] ──► Downstream Call
```

Blind copying frequently leaks:
- End-user session cookies and basic auth headers,
- Broadly scoped user tokens to services that do not need them,
- Sensitive client IP addresses, browser user-agents, and geographic markers,
- Internal routing, proxy, and debugging headers.

Always use an **explicit allowlist** in your outbound HTTP client pipeline, picking only the specific context fields intended for downstream consumption.

---

## Strongly-Typed Context Contracts vs. Ambient State

Model your context contract explicitly using strongly-typed data structures rather than untyped string maps or dictionaries.

### C# Contract Definition

```csharp
public sealed record ExecutionContext(
    string CallerService,
    string? InitiatedByUserId,
    string? TenantId,
    string CorrelationId,
    string TraceParent);

public sealed record ActorContext(
    string TechnicalActor,
    string? OriginalUser,
    string? TenantId,
    IReadOnlyList<string>? DelegationChain);
```

### TypeScript Contract Definition

```typescript
export interface ExecutionContext {
  readonly callerService: string;
  readonly initiatedByUserId?: string;
  readonly tenantId?: string;
  readonly correlationId: string;
  readonly traceParent: string;
}

export interface ActorContext {
  readonly technicalActor: string;
  readonly originalUser?: string;
  readonly tenantId?: string;
  readonly delegationChain?: readonly string[];
}
```

### Avoid Ambient Global State
Relying heavily on ambient global state—such as static `CurrentUser.Id` holders, raw `ThreadLocal`, unchecked `AsyncLocal` globals, or injecting raw `HttpContext` deep into business logic—causes persistent production issues:
- It hides method dependencies, making unit testing painful.
- It frequently leaks user context across thread pools or into asynchronous fire-and-forget background tasks.
- It makes asynchronous task scheduling non-deterministic when context fails to flow across thread pool handoffs.

Pass context explicitly to domain operations via method arguments or scoped domain execution boundaries:

```csharp
// Explicit context passing in C#
public Task UpdateDocumentAsync(
    DocumentId documentId,
    UserId initiatedBy,
    ExecutionContext context,
    CancellationToken cancellationToken);
```

```typescript
// Explicit context passing in TypeScript
async function updateDocument(
  documentId: DocumentId,
  initiatedBy: UserId,
  context: ExecutionContext
): Promise<OperationResult> {
  // Domain logic uses context explicitly
}
```

---

## Responsibility Matrix: Who Owns What?

| Boundary | Responsibilities |
| :--- | :--- |
| **Service A (Caller)** | • Authenticates user at system edge.<br>• Validates user intent and use-case authorization.<br>• Propagates user/tenant context via an explicit allowlist.<br>• Authenticates itself technically to Service B. |
| **Service B (Callee)** | • Authenticates Service A.<br>• Validates received context format.<br>• Authorizes the operation against resources B owns.<br>• Logs both technical actor and user initiator in immutable audit trails. |
| **Platform / Mesh** | • Service-to-service mTLS or workload identity.<br>• W3C trace propagation and correlation IDs.<br>• Edge gateway stripping of internal context headers.<br>• Middleware for typed context serialization and extraction. |

---

## Discrete Failure Taxonomy

Service B should distinguish failure modes using stable, machine-readable error codes rather than collapsing all rejections into a generic `403 Forbidden`:

```text
AUTH_SERVICE_UNAUTHENTICATED  ──► Caller service failed transport or token authentication
AUTH_SERVICE_UNAUTHORIZED     ──► Service A is authenticated, but not permitted to invoke this capability
AUTH_USER_CONTEXT_MISSING     ──► Required user identity metadata is absent from the request
AUTH_TENANT_MISMATCH          ──► User does not belong to the target tenant boundary
AUTH_USER_FORBIDDEN           ──► User is identified, but lacks permission for the requested resource
```

Collapsing all security errors into an opaque `403 Forbidden` makes operational debugging miserable. An on-call engineer cannot tell if a spike in 403s is due to an expired service mesh mTLS certificate, an IAM role misconfiguration, or an actual end user attempting an unauthorized action. Granular error codes inside the response body and structured logs make diagnosing production failures straightforward.

---

## Mental Model Summary

```text
Service A authenticates itself to Service B.

Service A propagates the original user ID as trusted context.

Service B decides whether it authorizes:
- Service A (Model 1),
- User U (Model 2),
- or both via token exchange.

Service B logs both identities in its audit trail.
```

1. **Propagate identity for context and audit.**
2. **Authenticate the service independently.**
3. **Authorize at the service that owns the relevant rule or resource.**

---

## Related Documentation

- **[[Service vs User Authorization Models]]**: Choosing between service-level authorization, end-user token pass-through, and RFC 8693 token exchange.
- **[[User Context in Asynchronous Systems]]**: Managing identity, security claims, and execution boundaries across message brokers, event streams, and workers.
- **[[Service-to-Service Authentication and Authorization in Azure and Kubernetes]]**: Practical implementation of mTLS, workload identity, and managed service identities.
- **[[Service-to-Service Communication - How Service A Should Call Service B]]**: Transport patterns, resiliency strategies, and header propagation across HTTP and gRPC boundaries.
- **[[OpenTelemetry]]**: Best practices for tracing context propagation across microservice architectures.
- **[[Standardizing Service Infrastructure with Reusable Blocks]]**: Embedding standardized context propagation middleware into shared service templates.
