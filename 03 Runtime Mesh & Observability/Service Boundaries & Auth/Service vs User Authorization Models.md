---
title: Service vs User Authorization Models
tags:
  - authorization
  - security
  - microservices
  - distributed-systems
  - rbac
  - oauth
aliases:
  - Service-to-Service vs User Auth
  - Authorization Patterns in Microservices
  - Disentangling Service Identity from User Authorization
  - Delegation vs Impersonation in Distributed Systems
---

# Service vs User Authorization Models

> [!IMPORTANT]
> **The Dual-Actor Authorization Axiom**: In distributed microservice architectures, answering *"Is this request authorized?"* requires establishing **which service owns the security rule** and **which identity is being evaluated**:
> $$\text{Request Authorization} = f(\text{Technical Caller (Service A)}, \text{End-User Initiator (User U)}, \text{Target Resource Domain})$$
> Blindly forwarding user JWTs across internal service hops creates audience mismatches, excessive privilege leakage, and tight cross-service coupling. Systems must choose an explicit authorization model: **Model 1 (Capability-Oriented)** where upstream orchestrators validate the user and call downstream utilities via service tokens; **Model 2 (Resource-Oriented)** where the resource-owning service evaluates user ACLs directly over trusted context; or **Model 3 (Explicit Token Exchange / RFC 8693)** where identity providers issue downscoped, audience-restricted delegated tokens.

```text
User U ──► API Gateway ──► Service A (Order Service) ──► Service B (Inventory Service)
                               │                               │
                               ├── Evaluates User Permissions  └── Evaluates Service A Permission:
                               │   ("Can User U place order?")     ("Is Order Service allowed to reserve?")
                               └── Calls with Service Token        (Audit logs both Service A and User U)
```

---

## Executive Summary & Core Architectural Invariants

Decoupling service-level permissions from end-user authorization governs secure service communication across microservices and agent meshes, complementing [[Propagating User Context Between Services|context propagation]] and [[User Context in Asynchronous Systems|asynchronous queues]]:

1. **The Dual-Actor Reality**: Every internal RPC carries two distinct actors: the **Technical Caller** (the machine identity executing the request, e.g., Service A) and the **Original Initiator** (the human or personal agent who initiated the business intent, e.g., User U).
2. **Model 1 (Capability-Oriented Authorization)**: Upstream orchestrators validate user permissions at the system perimeter and call internal utility services using machine credentials. The downstream utility authorizes Service A without re-evaluating the user, decoupling low-level subsystems from user permission schemas.
3. **Model 2 (Resource-Oriented Authorization)**: When a downstream service owns sensitive domain entities with granular ACLs (e.g., medical records, payroll, documents), that service evaluates User U's permissions directly against the specific resource, requiring Service A to be authenticated before accepting user context.
4. **Model 3 (Explicit Token Exchange via RFC 8693)**: High-security environments eliminate shared trust by exchanging upstream user tokens for downscoped, audience-restricted delegated tokens containing explicit actor (`act: service-a`) and subject (`sub: user-u`) claims.
5. **Delegation Over Impersonation**: Systems must preserve the full delegation chain (`User -> Gateway -> Service A -> Service B`). Impersonation (pretending the user connected directly to Service B) hides machine identity, blinding audit logs to compromised internal services.
6. **The Hazard of Forwarding Raw Browser Cookies**: Cookies are domain-bound, fragile, and expose internal services to cross-site request forgery. Internal networks must never accept or forward browser session cookies.
7. **The Hazard of Blind JWT Forwarding**: Forwarding external access tokens across internal service hops causes audience mismatches (`aud: api-gateway`), leaks excessive administrative privileges to downstream microservices, and risks mid-flight token expiration during long-running workflows.
8. **Structured Immutable Audit Logging**: High-trust services write structured audit events capturing `technicalActor`, `initiatedByUserId`, `tenantId`, `operation`, `authorizationModel`, and `traceId`, ensuring complete forensic non-repudiation.

---

## The Three Authorization Topologies

When Service A calls Service B on behalf of User U, systems deploy one of three discrete authorization patterns based on resource ownership:

```text
The Three Authorization Models:

1. Model 1 (Capability-Oriented) ──► Upstream Service A authorizes User U; Service B authorizes Service A.
2. Model 2 (Resource-Oriented)   ──► Service B authorizes User U directly on the resource using trusted context.
3. Model 3 (Token Exchange)       ──► IdP issues downscoped delegated token specifically for Service B.
```

### Model 1: Service B Authorizes Service A (Capability-Oriented)
Service A is the authoritative owner of the business workflow. Service B provides an internal supporting utility:

```text
User U ──[places order]──► Order Service (Service A)
                              │
                              ├── 1. Validates User U has permission to place order.
                              └── 2. Calls Inventory Service (Service B) with Service Token.
                                    │
                                    ▼
                           Inventory Service (Service B)
                              │
                              └── Verifies: "Order Service is allowed to reserve inventory."
                                  (Does NOT re-evaluate User U's permissions).
```

- **When to Use**: Workflow orchestrators calling internal utilities (inventory reservation, notification sending, PDF generation) where downstream resources lack individual user ACLs.
- **Audit Responsibility**: Service A passes `initiatedByUserId` as contextual metadata so Service B records both the technical actor and the user in its audit log.

### Model 2: Service B Authorizes the User (Resource-Oriented)
Service B is the authoritative owner of a protected domain resource and its access control list:

```text
User U ──[edits doc]──► Web Portal (Service A)
                           │
                           └── Calls Document Service (Service B) passing User ID + Service Identity.
                                 │
                                 ▼
                        Document Service (Service B)
                           │
                           └── Evaluates: "Can User U edit Document D?"
```

- **When to Use**: Downstream services holding sensitive domain entities with granular ACLs (e.g., Document Management, Financial Ledgers, HR Records).
- **Critical Requirement**: Service B must verify Service A's technical identity before accepting `userId`. An unauthenticated caller must never be allowed to assert arbitrary user context.

### Model 3: Explicit Delegation via OAuth 2.0 Token Exchange (RFC 8693)
When zero-trust boundaries forbid trusting forwarded metadata headers, services implement explicit cryptographic token exchange:

```text
Service A (with User Token) ──► Identity Provider (STS)
                                    │
                                    └── Exchanges User Token + Service A Credentials
                                          for a Downscoped Delegated Token
                                    │
                                    ▼
Service A ──[Delegated Token (aud: Service B, scope: read:docs)]──► Service B
```

The delegated token enforces:
- **Audience Restriction**: Valid solely for `aud: service-b`.
- **Least Privilege**: Restricted to the minimum operational scope.
- **Cryptographic Delegation Chain**: Contains an actor claim (`act: service-a`) and subject claim (`sub: user-u`).

---

## Delegation vs. Impersonation

When propagating identity, systems must preserve both actors rather than collapsing them:

```text
Preferred: Delegation
Service B understands: "Service A is acting on behalf of User U."
Audit Record: Caller = Service A, Initiator = User U.

Anti-Pattern: Impersonation
Service B behaves as if User U connected directly over a local loop.
Audit Record: Caller = User U (Hides the fact that Service A made the call).
```

Preserving the full delegation chain (`User -> Gateway -> Service A -> Service B`) is essential for:
- Detecting compromised microservices attempting privilege escalation,
- Enforcing compliance with strict regulatory non-repudiation mandates,
- Enabling granular forensics during security breaches.

---

## Token Forwarding Hazards: Cookies and Raw JWTs

### 1. The Hazard of Forwarding Browser Cookies
- Cookies are tightly coupled to edge frontend domains and browser session state.
- Exposing cookies to internal microservices creates tight coupling to external web protocols and exposes internal networks to cross-site request forgery.
- Cookies cannot be forwarded to asynchronous message queues or background workers.

### 2. The Hazard of Blind JWT Forwarding
Forwarding the original user access token received at the API gateway down an internal call chain introduces severe vulnerabilities:

```text
User JWT ──► Gateway ──► Service A ──(Blind Forward)──► Service B ──(Blind Forward)──► Service C
```

1. **Audience Mismatch**: Tokens issued for `aud: "api-gateway"` or `aud: "service-a"` are semantically invalid when presented to Service B.
2. **Excessive Privilege Leakage**: The user's token carries broad scopes (billing, personal profile, admin flags) that downstream internal microservices should never receive.
3. **Mid-Flight Expiration**: In multi-step or asynchronous workflows, short-lived user tokens expire while requests are waiting in internal queues or retry loops.

---

## Structured Immutable Audit Logging

High-trust services record structured audit events capturing both technical and end-user identities:

```json
{
  "timestamp": "2026-09-04T02:20:00Z",
  "technicalActor": "order-service",
  "initiatedByUserId": "usr-98124",
  "tenantId": "tenant-corp-42",
  "operation": "reserve_stock",
  "resourceId": "sku-10492",
  "authorizationModel": "service_level",
  "decision": "allowed",
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736"
}
```

Capturing the complete dual-actor context ensures that security audits can attribute every mutation to both the executing code and the human or agent who initiated it.

---

## Relationship to the Knowledge Graph

- **[[Propagating User Context Between Services]]**: Passing end-user identity across service boundaries to enforce dual-context authorization.
- **[[User Context in Asynchronous Systems]]**: Managing authorization claims in background asynchronous worker queues.
- **[[Service-to-Service Authentication and Authorization in Azure and Kubernetes]]**: Machine-to-machine authentication protocols, mTLS, and workload identity tokens.
- **[[Standardizing Service Infrastructure with Reusable Blocks]]**: Encapsulating standard authorization middleware into shared infrastructure blocks.
- **[[WebMCP - Turning Web Applications into Agent-Native Toolkits]]**: Enforcing user context and authorization when agents invoke in-browser tools.
