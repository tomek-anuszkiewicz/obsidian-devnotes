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

> [!IMPORTANT]
> **The Orthogonal Context Separation Axiom**: In distributed systems and microservice meshes, conflating technical caller authentication with user context causes critical security vulnerabilities, confused-deputy attacks, and architectural rot. Resilient architectures enforce a strict six-way separation of concerns:
> $$\text{Service Identity} \neq \text{User Identity} \neq \text{Authorization Decision} \neq \text{Audit Context} \neq \text{Distributed Trace} \neq \text{Tenant Boundary}$$
> - **The calling service authenticates itself** via technical workload identity (mTLS, service tokens, or cloud IAM).
> - **The user identifier is propagated as trusted metadata** only after the technical caller has been independently authenticated.
> - **Authorization is decided locally by the service owning the resource**, preserving service boundary autonomy.

```text
User U ──► API Gateway (Strips external X-Headers, Authenticates User)
                 │
                 ▼
            Service A (Authenticates as Service A via mTLS / Workload Identity)
                 │
                 ▼ [Propagates allowlisted headers: User-Id, Tenant-Id, traceparent]
            Service B (Verifies Service A identity ──► Validates User Context ──► Authorizes Resource Access)
```

---

## Executive Summary & Core Architectural Invariants

Managing identity across microservices, asynchronous queues, and autonomous agent systems requires treating context propagation as a first-class distributed systems contract:

1. **The Six-Way Orthogonal Separation**: Systems must strictly disentangle:
   - **Service Identity**: *Who is physically making the network call?* (mTLS, SPIFFE, OAuth Client Credentials).
   - **User Identity**: *Which human or agent initiated the business intent?* (`X-Initiated-By-User-Id` or token exchange).
   - **Authorization Decision**: *Is the operation permitted on the target resource?* (Decided by the service owning the data).
   - **Audit Context**: *Who did what and under what delegation chain?* (Immutable append-only audit trail).
   - **Trace Context**: *Which technical execution chain does this belong to?* (W3C `traceparent` and `tracestate`).
   - **Tenant Boundary**: *Which logical organization owns the data?* (Verified organizational claim).
2. **Independent Caller Authentication**: Service B must verify that the incoming call genuinely originated from Service A before inspecting any propagated user metadata. Never trust user identity headers from an unauthenticated caller.
3. **Edge Gateway Header Sanitization**: The perimeter API Gateway must unconditionally strip, overwrite, or reject untrusted internal context headers (`X-User-Id`, `X-Tenant-Id`) sent from external clients to prevent spoofing.
4. **Strict Header Allowlisting Over Blind Forwarding**: Downstream clients must never blindly copy all inbound HTTP headers to outbound requests. Blind copying leaks browser session cookies, excessive OAuth scopes, and internal debug headers. Outbound calls must construct an explicit, allowlisted context envelope.
5. **Decoupling Technical Traces from User Identity**: Distributed tracing ([[OpenTelemetry]]) tracks physical execution hops. It must not be conflated with business correlation IDs or user identity.
6. **Cryptographically Verified Tenant Isolation**: Multi-tenant architectures must never accept an arbitrary `X-Tenant-Id` header without verification. The tenant context must be verified against cryptographically signed token claims or verified against an authenticated user directory.
7. **Strongly-Typed Context Contracts**: Application code must discard untyped string dictionaries in favor of strongly-typed records (`ExecutionContext`, `ActorContext`) passed explicitly to domain operations, avoiding dangerous ambient global state.
8. **Granular Machine-Readable Failure Taxonomy**: Services must not collapse all security failures into a generic `403 Forbidden`. The error payload must explicitly distinguish caller service failures (`AUTH_SERVICE_UNAUTHENTICATED`) from user permission denials (`AUTH_USER_FORBIDDEN`).

---

## Architectural Deep Dives

This guideline is supported by specialized architectural references across the vault:

1. **[[Service vs User Authorization Models]]**:
   - Choosing between **Model 1** (Service B authorizes Service A) and **Model 2** (Service B authorizes the User).
   - Delegation vs. Impersonation (preserving technical caller vs. user initiator).
   - Dangers of forwarding browser cookies and raw user access tokens across internal networks.
   - Explicit token delegation via OAuth 2.0 Token Exchange (RFC 8693).
2. **[[User Context in Asynchronous Systems]]**:
   - Context propagation through message brokers (RabbitMQ, Kafka, Azure Service Bus).
   - Dangers of storing live tokens in message queues or dead-letter queues.
   - Pre-authorization at acceptance time vs. post-authorization at execution time.
   - Context semantics for Commands vs. Domain Events.

---

## The Core Principle: Three Distinct Concerns

A resilient distributed architecture enforces:

```text
Service Identity:   Tells Service B who is physically making the call.
User Identity:      Tells Service B whose business operation this is.
Authorization:      Determines whether the requested operation is permitted.
```

These three concerns must never be treated as interchangeable.

### Authenticating the Calling Service Independently
Service B must verify the technical caller independently:
- Workload identity (Kubernetes ServiceAccount IAM / Cloud provider managed identity),
- Mutual TLS (mTLS) with SPIFFE/SAN validation,
- Client credentials (OAuth 2.0 service tokens),
- Trusted service mesh sidecar identity (Istio / Linkerd).

```http
# Critical Vulnerability: An unauthenticated caller supplying an arbitrary User-Id
X-User-Id: admin-user-42
```

Service B verifies that the request arrived from an authorized, authenticated microservice. Only after Service A's identity is verified does Service B inspect the `X-Initiated-By-User-Id` context metadata.

---

## Wire Protocols, Header Allowlisting & Gateway Stripping

For synchronous HTTP communication, Service A constructs an explicit, allowlisted header envelope:

```http
Authorization: Bearer <service-to-service-token>
X-Initiated-By-User-Id: user-123
X-Tenant-Id: tenant-7
X-Correlation-Id: operation-456
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

### The Peril of Blind Header Forwarding
A widespread anti-pattern in microservice middleware is copying all incoming HTTP headers directly to downstream HTTP clients:

```text
Incoming Request ──► [Blind Header Copy Middleware] ──► Downstream Microservice
```

This anti-pattern frequently leaks:
- Raw end-user session cookies and JWTs containing administrative scopes,
- Sensitive client IP addresses and user agents,
- Internal routing and debug flags.

All outbound HTTP clients must assemble an **explicit allowlist** of validated context fields.

---

## Strongly-Typed Context Contracts vs. Ambient State

Software should model context explicitly using strongly-typed data structures rather than untyped string dictionaries:

```typescript
// Strongly typed execution context schema
interface ExecutionContext {
  callerService: string;
  initiatedByUserId?: string;
  tenantId?: string;
  correlationId: string;
  traceParent: string;
}

interface ActorContext {
  technicalActor: string;
  originalUser?: string;
  tenantId?: string;
  delegationChain?: string[];
}
```

### Avoiding Ambient Global State
Relying heavily on ambient global state (static thread-local variables or unchecked async task-local globals) introduces severe operational bugs:
- Conceals method prerequisites and complicates unit testing,
- Risks leaking user context into fire-and-forget background worker routines or thread pools.

Domain logic should receive required identity and context values explicitly via method arguments or scoped domain execution interfaces:

```typescript
// Explicit context passing in domain operations
async function updateDocument(
  documentId: DocumentId,
  initiatedBy: UserId,
  context: ExecutionContext
): Promise<OperationResult> { ... }
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

Service B should distinguish failure reasons using stable, machine-readable error codes:

```text
AUTH_SERVICE_UNAUTHENTICATED  ──► Caller service failed transport/token authentication
AUTH_SERVICE_UNAUTHORIZED     ──► Service A not permitted to invoke this capability
AUTH_USER_CONTEXT_MISSING     ──► Required user identity metadata absent from payload
AUTH_TENANT_MISMATCH          ──► User does not belong to specified tenant boundary
AUTH_USER_FORBIDDEN           ──► User lacks permission for the requested resource
```

Avoiding generic, opaque `403 Forbidden` responses ensures that operational monitoring and automated self-healing agents can instantly identify whether a failure was caused by network certificate expiration, misconfigured workload IAM, or actual user access denial.

---

## Relationship to the Knowledge Graph

- **[[User Context in Asynchronous Systems]]**: Propagating user identity, security claims, and tracing through message brokers and background jobs.
- **[[Service vs User Authorization Models]]**: Disentangling acting user credentials from underlying service principal permissions.
- **[[Service-to-Service Authentication and Authorization in Azure and Kubernetes]]**: Secure cryptographic token exchange (OAuth2 On-Behalf-Of) between microservices.
- **[[Service-to-Service Communication -  How Service A Should Call Service B]]**: Transporting trace and user context headers across HTTP/gRPC boundaries.
- **[[OpenTelemetry]]**: Tracing context flow across distributed boundaries.
- **[[Standardizing Service Infrastructure with Reusable Blocks]]**: Embedding standardized context propagation middleware into service templates.
