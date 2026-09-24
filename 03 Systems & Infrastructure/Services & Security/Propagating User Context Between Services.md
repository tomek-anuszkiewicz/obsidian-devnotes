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
---

> [!NOTE] Foundational Systems Architecture (Non-LLM Scope)
> This note forms part of an emerging exploration into foundational distributed systems and runtime infrastructure (independent of LLM or agent workflows). While currently cataloged as an isolated architectural blueprint, it is slated for future consolidation into a unified backend systems pillar as broader operational notes are developed.

## Context

In distributed systems, Service A may receive a request initiated by a user and then call Service B.

The full flow may look like:

```text
User U
→ Gateway
→ Service A
→ Service B
```

Service B may need to know:
- which service made the call,
- which user originally initiated the operation,
- which tenant the operation belongs to,
- which trace and correlation identifiers belong to the flow,
- whether the operation is authorized.

These concerns are related, but they are not the same. Treating all of them as one generic request context leads to security bugs and architecture decay.

A clean model strictly separates:
- **Service identity** (who is calling),
- **User identity** (who initiated the operation),
- **Authorization** (is this allowed),
- **Audit context** (who did what and when),
- **Trace context** (technical execution chain),
- **Tenant context** (boundary of the data).

---

## Core Principle

A robust responsibility model is:

> **The calling service authenticates itself.**  
> **The user identifier is propagated as contextual metadata.**  
> **The service owning the resource decides how authorization should work.**

In practical terms:

```text
userId tells Service B whose operation this is;

service identity tells Service B who is making the call;

authorization determines whether the operation is allowed.
```

These three concepts must never be treated as interchangeable.

---

## Architectural Deep Dives

This guideline is modularized into specialized architecture references:

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

Service B must verify the technical caller independently:

```text
Authenticated caller: Service A
Original initiator: User U
```

Possible service authentication mechanisms include:
- workload identity (Kubernetes / Cloud provider IAM),
- mutual TLS (mTLS),
- client credentials (OAuth2),
- signed service tokens,
- trusted service mesh identity (e.g. Istio / Linkerd).

Service B should verify that the request genuinely came from Service A. Only then may it trust the user context metadata supplied by Service A.

```http
# Dangerous: An unauthenticated caller supplying an arbitrary User-Id
X-User-Id: user-123
```

The system boundary (API Gateway) must strip, overwrite, or reject untrusted internal-context headers sent from external clients.

If an incoming external request carries an unverified `X-User-Id` or `X-Tenant-Id` header, the gateway must drop it immediately before authenticating caller credentials and attaching verified downstream headers. Leaving header sanitization to downstream internal services introduces confused-deputy vulnerabilities if any internal service misconfigures transport authentication or exposes an unauthenticated debug route.

---

## Trace Context Is Separate from User Context

Distributed tracing should use standard W3C trace propagation (`traceparent`, `tracestate`).

- **Trace context** answers: *Which technical execution chain does this call belong to?*
- **User context** answers: *Who initiated the business operation?*
- **Correlation context** answers: *Which logical business workflow or batch does this belong to?*

```text
traceId        = technical execution chain (W3C traceparent)
correlationId  = logical business operation or request family
tenantId       = organizational / security boundary
userId         = original initiator
```

They may travel together in headers, but they belong to different technical contracts.

Conflating W3C trace IDs with user identity also introduces regulatory and compliance hazards. Telemetry collectors and APM systems routinely ingest trace headers without redaction; embedding user identity or tenant keys into trace state risks leaking Personally Identifiable Information (PII) across log aggregators and third-party monitoring vendors.

---

## Tenant Context

In multi-tenant systems, `tenantId` is often propagated alongside `userId`.

Service B must not trust an arbitrary `X-Tenant-Id` header without verification. The tenant must be verified against a trusted identity:
- Verified claims in a cryptographically signed token,
- Authenticated caller that is authorized to act on behalf of the tenant,
- Explicit database lookup confirming that `userId` is an active member of `tenantId`.

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
A dangerous anti-pattern is copying all inbound HTTP headers directly to downstream calls. This risks leaking:
- browser cookies,
- credentials with excessive scopes,
- sensitive client claims,
- internal routing or debug headers.

Always use an **explicit allowlist** of validated context fields for outbound requests.

---

## A Shared Context Contract in Code

Model the context contract explicitly using strongly-typed records rather than an untyped dictionary:

```csharp
public sealed record ExecutionContext(
    string CallerService,
    string? InitiatedByUserId,
    string? TenantId,
    string CorrelationId);

public sealed record ActorContext(
    string TechnicalActor,
    string? OriginalUser,
    string? TenantId,
    string? DelegationChain);
```

### Avoid One Global Ambient Context
Avoid relying heavily on ambient global state (e.g. static `CurrentUser.Id`, unchecked `AsyncLocal` globals, or direct access to `HttpContext` deep inside business domains):
- Makes unit testing difficult and hides method prerequisites.
- Risks leaking user context into fire-and-forget background tasks or thread pool threads.
- Domain logic should receive required identity values explicitly via method arguments or scoped domain interfaces:

```csharp
public Task UpdateDocumentAsync(
    DocumentId documentId,
    UserId initiatedBy,
    CancellationToken cancellationToken);
```

Relying on ambient storage like `AsyncLocal` or `ThreadLocal` also introduces non-deterministic execution bugs under high load. When asynchronous tasks hand execution off across thread pool boundaries or run detached background jobs, ambient context can silently drop or cross-contaminate concurrent requests. Passing context explicitly down the call stack makes dependencies visible to compilers and keeps execution paths deterministic.

---

## Who Owns What?

| Boundary | Responsibilities |
| :--- | :--- |
| **Service A (Caller)** | • Authenticates user at system edge.<br>• Validates user intent and use-case authorization.<br>• Propagates user/tenant context via an allowlist.<br>• Authenticates itself technically to Service B. |
| **Service B (Callee)** | • Authenticates Service A.<br>• Validates received context format.<br>• Authorizes the operation against resources B owns.<br>• Logs both technical actor and user initiator. |
| **Platform / Mesh** | • Service-to-service mTLS or workload identity.<br>• W3C trace propagation and correlation IDs.<br>• Edge gateway stripping of internal context headers.<br>• Middleware for typed context serialization and extraction. |

---

## Failure Handling

Service B should distinguish failure reasons using stable, machine-readable error codes:

```text
AUTH_SERVICE_UNAUTHENTICATED  -> Caller service failed authentication
AUTH_SERVICE_UNAUTHORIZED     -> Service A not permitted to invoke this capability
AUTH_USER_CONTEXT_MISSING     -> Required user identity metadata absent
AUTH_TENANT_MISMATCH          -> User does not belong to specified tenant
AUTH_USER_FORBIDDEN           -> User lacks permission for resource D
```

Avoid collapsing all security failures into a generic `403 Forbidden` without logging the exact failure reason.

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

> **Propagate identity for context and audit.**  
> **Authenticate the service independently.**  
> **Authorize at the service that owns the relevant rule or resource.**

## Related notes

- **[[Service vs User Authorization Models]]** — Detailed breakdown of caller-centric, end-user-centric, and token-exchange authorization patterns.
- **[[User Context in Asynchronous Systems]]** — Managing user identity, tenant boundaries, and correlation across queues and background tasks.
- **[[Service-to-Service Authentication and Authorization in Azure and Kubernetes]]** — mTLS, workload identity, and signed technical tokens between services.
- **[[Service-to-Service Communication — How Service A Should Call Service B]]** — Communication patterns, timeouts, and transport resilience.
- **[[Standardizing Service Infrastructure with Reusable Blocks]]** — Platform middleware for tracing, headers, and security context.
