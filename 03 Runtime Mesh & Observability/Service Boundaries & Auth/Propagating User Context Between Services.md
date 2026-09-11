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

> [!IMPORTANT] Executive Architectural Thesis: Orthogonal Identity and Context Separation
> In distributed systems and microservice meshes, conflating technical caller authentication with user context causes security vulnerabilities, confused-deputy attacks, and architectural rot. Resilient architectures enforce a strict six-way separation of concerns:
> $$\text{Service Identity} \neq \text{User Identity} \neq \text{Authorization Decision} \neq \text{Audit Context} \neq \text{Distributed Trace} \neq \text{Tenant Boundary}$$
> - **The calling service authenticates itself** via technical workload identity (mTLS, service tokens, or cloud IAM).
> - **The user identifier is propagated as trusted metadata** only after the technical caller has been authenticated.
> - **Authorization is decided locally by the service owning the resource**, preserving service boundary autonomy.

| Context Dimension | Semantic Purpose | Wire Protocol / Header | Verification & Trust Boundary |
| :--- | :--- | :--- | :--- |
| **Service Identity** | Who is physically making the call | mTLS (SPIFFE/SAN), OAuth Client Credentials | Verified cryptographically at network/transport layer |
| **User Identity** | Who initiated the original business intent | Propagated metadata header or Token Exchange (RFC 8693) | Trusted only if calling service is authenticated |
| **Authorization** | Is the technical caller or user allowed this action | Local domain engine / policy enforcement point (PEP) | Evaluated by the service owning the resource |
| **Audit Context** | Non-repudiation and compliance logging | Structured immutable metadata payload | Written to append-only audit trail with actor chains |
| **Trace Context** | Causal distributed execution chain | W3C `traceparent` and `tracestate` | Transparently forwarded across all RPC and message hops |
| **Tenant Boundary** | Logical data isolation barrier | Cryptographically signed claim or verified header | Validated against user identity and organizational claims |

---

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

Model the context contract explicitly using strongly-typed structures rather than an untyped generic dictionary:

```text
// Strongly typed execution context schema
record ExecutionContext {
    callerService: string,
    initiatedByUserId?: string,
    tenantId?: string,
    correlationId: string,
    traceParent: string
}

record ActorContext {
    technicalActor: string,
    originalUser?: string,
    tenantId?: string,
    delegationChain?: string[]
}
```

### Avoid One Global Ambient Context
Avoid relying heavily on ambient global state (e.g., static thread-local variables, unchecked task-local globals, or direct access to HTTP request objects deep inside business domains):
- Makes unit testing difficult and conceals method prerequisites.
- Risks leaking user context into fire-and-forget background worker routines or thread pools.
- Domain logic should receive required identity and context values explicitly via method arguments or scoped domain execution interfaces:

```text
// Explicit context passing in domain operations
updateDocument(
    documentId: DocumentId,
    initiatedBy: UserId,
    context: ExecutionContext
): Promise<OperationResult>
```

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
---

## Relationship to the Knowledge Graph

- **[[User Context in Asynchronous Systems]]**: Propagating user identity, security claims, and tracing through message brokers and background jobs.
- **[[Service vs User Authorization Models]]**: Disentangling acting user credentials from underlying service principal permissions.
- **[[Service-to-Service Authentication and Authorization in Azure and Kubernetes]]**: Secure cryptographic token exchange (OAuth2 On-Behalf-Of) between microservices.
- **[[Service-to-Service Communication -  How Service A Should Call Service B]]**: Transporting trace and user context headers across HTTP/gRPC boundaries.
- **[[OpenTelemetry]]**: Tracing context flow across distributed boundaries.
