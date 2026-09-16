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

In distributed architectures, answering the question *"Is this request allowed?"* requires determining **which service owns the authorization rule** and **which identity is being authorized**.

When a request crosses service boundaries, authorization is rarely a simple binary check against a single user ID. The upstream service is an active system component executing code, while the end user is the origin of the business intent. Decoupling service-level permissions from end-user authorization governs how services communicate securely across microservices and background workers.

---

## 1. The Core Authorization Dilemma

Consider a standard downstream call chain where Service A calls Service B to fulfill an operation triggered by User U:

```text
User U ──► API Gateway ──► Service A ──► Service B
```

Every request arriving at Service B involves two distinct identities:
1. **Technical Caller:** Service A (the machine identity executing the network request).
2. **Original Initiator:** User U (the human user, external client, or automated agent whose action initiated the workflow).

Authorization logic must resolve: does Service B evaluate permissions for **Service A**, for **User U**, or for the **combination of both**? 

Choosing the wrong model creates common failure modes: either downstream internal services become overly coupled to complex user permission logic they should know nothing about, or upstream services pass unverified user headers that allow compromised internal services to spoof any identity across the network.

---

## 2. The Three Authorization Topologies

Depending on resource ownership, data sensitivity, and network trust boundaries, systems implement one of three discrete authorization patterns.

```text
The Three Authorization Topologies:

1. Model 1 (Capability-Oriented) ──► Upstream Service A authorizes User U; Service B authorizes Service A.
2. Model 2 (Resource-Oriented)   ──► Service B authorizes User U directly against the target resource.
3. Model 3 (Token Exchange)       ──► Identity Provider issues downscoped delegated token for Service B.
```

---

### Model 1: Service B Authorizes Service A (Capability-Oriented)

In this model, Service A is the authoritative owner of the business use case and user permission checks. Service B provides a supporting internal capability or infrastructure utility.

```text
User U ──[places order]──► Order Service (Service A)
                              │
                              ├── (1) Validates User U has permission to place orders.
                              └── (2) Calls Inventory Service (Service B) with Service Token.
                                    │
                                    ▼
                           Inventory Service (Service B)
                              │
                              └── Verifies: "Order Service is allowed to reserve inventory."
                                  (Does NOT re-evaluate User U's permissions).
```

* **How It Works:** Service A authenticates User U at the system perimeter, verifies that User U has the rights to execute the business transaction (e.g., checkout), and then calls Service B using Service A's own machine credentials (such as an mTLS certificate or an OAuth 2.0 client credentials token). Service B only verifies that Service A possesses the permission to invoke its API (e.g., `inventory:reserve`).
* **When to Use:**
  * Service A completely owns the business workflow (e.g., order processing, batch generation).
  * Service B is an internal utility or low-level subsystem (e.g., inventory reservation, sending push notifications, generating PDFs, debiting an internal ledger).
  * The resource managed by Service B does not have a user-facing Access Control List (ACL). Individual users do not "own" warehouse inventory rows.
* **Audit Responsibility:** Even though Service B does not authorize User U, Service A must forward `initiatedByUserId` as contextual tracing metadata. Service B records both the technical caller (`order-service`) and the human initiator (`usr-98124`) in its audit log.

---

### Model 2: Service B Authorizes the User (Resource-Oriented)

In this model, Service B is the authoritative owner of the protected domain resource, its security policy, and its fine-grained access control lists.

```text
User U ──[edits doc]──► Web Portal (Service A)
                           │
                           └── Calls Document Service (Service B)
                                 passing User ID + Service Identity.
                                 │
                                 ▼
                        Document Service (Service B)
                           │
                           └── Evaluates: "Can User U edit Document D?"
```

* **How It Works:** Service A acts as an edge router, aggregator, or frontend orchestration layer. It authenticates the incoming call, establishes transport trust with Service B, and passes the user identity context along with the request. Service B evaluates the request directly against its own domain data:

  ```csharp
  await authorizationService.AuthorizeAsync(
      userId,
      documentId,
      Permission.Edit,
      cancellationToken);
  ```

* **When to Use:**
  * Service B owns sensitive domain entities with granular, row-level ACLs (e.g., document management, medical records, payroll systems, multi-tenant billing).
  * Access rules depend on resource-specific attributes, document sharing policies, tenant isolation rules, or dynamic department boundaries stored exclusively within Service B's database.
* **The Critical Machine Trust Prerequisite:** Service B must authenticate Service A at the transport or machine layer (via mTLS or an internal service token) *before* accepting the asserted user context. An unauthenticated or untrusted caller must never be allowed to pass an arbitrary `X-User-Id` header. Without verified caller identity, any service inside the perimeter could impersonate any user across the system.

---

### Model 3: Explicit Delegation via OAuth 2.0 Token Exchange (RFC 8693)

When services cross high-trust boundaries, or zero-trust architecture prohibits accepting forwarded identity headers on faith, systems implement cryptographic token exchange.

```text
Service A (with User Token) ──► Identity Provider (STS)
                                    │
                                    └── Exchanges User Token + Service A Credentials
                                          for a Downscoped Delegated Token
                                    │
                                    ▼
Service A ──[Delegated Token (aud: Service B, scope: read:docs)]──► Service B
```

* **How It Works:** Rather than passing the raw user token downstream or relying on unverified headers, Service A presents its machine credentials along with the user's incoming token to a Security Token Service (STS) implementing RFC 8693. The STS issues a new, short-lived delegated token specifically minted for Service B.
* **Token Characteristics:**
  * **Audience Restriction:** The token is explicitly scoped to Service B (`aud: "service-b"`). If Service B is compromised, the token cannot be replayed against Service C.
  * **Downscoped Privileges:** The token carries only the minimal scopes required for this specific downstream hop (e.g., `scope: "read:docs"`), stripping out administrative or unrelated user privileges.
  * **Cryptographic Delegation Chain:** The token explicitly pairs the machine actor and human subject using standard claims:

    ```json
    {
      "iss": "https://auth.internal.net",
      "sub": "usr-98124",
      "aud": "service-b",
      "act": {
        "sub": "order-service"
      },
      "scope": "read:docs",
      "exp": 1714838400
    }
    ```

* **When to Use:**
  * Calls crossing regulatory, organizational, or network trust boundaries (e.g., inter-departmental APIs, partner ecosystems, multi-cloud links).
  * Architectures requiring non-repudiation at every hop without shared network-layer trust.
* **Operational Trade-Off:** Token exchange introduces latency on downstream calls (an extra STS round-trip) and increases operational load on the identity provider. In practice, services must cache downscoped tokens locally using a compound cache key:

  $$\text{CacheKey} = (\text{UserId}, \text{TargetService}, \text{RequestedScopes})$$

---

## 3. Delegation vs. Impersonation

When propagating identity across internal hops, systems must preserve both identities rather than collapsing them into one:

```text
Preferred: Delegation
Service B understands: "Service A is acting on behalf of User U."
Audit Record: Caller = Service A, Initiator = User U.

Anti-Pattern: Impersonation
Service B behaves as if User U connected directly over a local loop.
Audit Record: Caller = User U (Hides the fact that Service A made the call).
```

Collapsing context into impersonation introduces significant security vulnerabilities:

1. **Blind Spot in Threat Detection:** If Service A is compromised via a remote code execution vulnerability or dependency exploit, it can forge requests to Service B using legitimate user IDs. If Service B only logs the user identity, forensics cannot identify which service originated the malicious calls.
2. **Loss of Non-Repudiation:** In regulated environments (HIPAA, PCI-DSS, SOC 2), compliance audits require proving not just who clicked the button, but precisely which software components handled the data along the transit path.
3. **Privilege Escalation:** If downstream services assume direct user contact, they cannot verify whether the intermediary service was actually authorized to perform the operation on the user's behalf.

---

## 4. Token Forwarding Hazards

Engineers often attempt to simplify context propagation by forwarding whatever credential arrived at the API gateway directly down the microservice call chain. This introduces critical design flaws.

### Why Not Forward Browser Cookies?
* **Domain Binding and State:** Cookies are scoped to external domain names and managed by browser cookie jars. Microservices run on internal domains, service meshes, or IP namespaces where cookie scoping breaks down.
* **Protocol Coupling:** Exposing cookies to internal backends couples internal microservices to external HTTP session semantics, preventing the migration of internal transports to gRPC, AMQP, or Apache Kafka.
* **Asynchronous Incompatibility:** Cookies cannot be passed safely to asynchronous background queues, scheduled tasks, or retry workers.

### Why Not Blindly Forward the User's JWT?
Passing the user's incoming JWT unchanged down the call stack is a common anti-pattern:

```text
User JWT ──► Gateway ──► Service A ──(Blind Forward)──► Service B ──(Blind Forward)──► Service C
```

1. **Audience Mismatch:** A user JWT issued at the gateway typically contains `aud: "api-gateway"` or `aud: "frontend-api"`. If Service B enforces standard JWT audience validation, the call fails. If Service B disables audience validation to make the call work, it opens the system to token replay attacks from entirely unrelated services.
2. **Excessive Privilege Leakage:** The user's original token often carries broad privileges: profile management, billing update permissions, or organization-wide read access. When Service A forwards this token to a low-level utility (e.g., an avatar resizing service), a vulnerability in that utility exposes the full scope of the user's token across the entire architecture.
3. **Mid-Flight Expiration in Long Flows:** User access tokens are intentionally short-lived (typically 5 to 15 minutes). If a business workflow involves multiple sequential RPC calls, background processing steps, or queue retry policies, the token will expire mid-transit, causing late-stage service calls to fail intermittently.

---

## 5. Structured Audit Logging

Regardless of whether Model 1, Model 2, or Model 3 is used, every mutating or security-sensitive internal operation must log a structured event capturing the dual-actor context.

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

Capturing both `technicalActor` and `initiatedByUserId` allows security teams to:
* Reconstruct the full sequence of events during incident triage.
* Identify which machine identity made an authorized call vs. which user authorized the business action.
* Correlate actions across services using the distributed `traceId` without requiring downstream services to maintain user-level access control tables.

---

## Context and Related Architecture Notes

* **[[Propagating User Context Between Services]]**: Wire protocols, HTTP header propagation (`X-Correlation-ID`, baggage), and context extraction across synchronous network hops.
* **[[User Context in Asynchronous Systems]]**: Managing identity, token lifetimes, and claim propagation across message queues, pub/sub topics, and background workers.
* **[[Service-to-Service Authentication and Authorization in Azure and Kubernetes]]**: Practical implementation of machine identities using mTLS, SPIFFE/SPIRE, and cloud workload identity credentials.
* **[[Standardizing Service Infrastructure with Reusable Blocks]]**: Embedding standard context extraction, token validation, and audit emission into shared service templates.
* **[[WebMCP - Turning Web Applications into Agent-Native Toolkits]]**: Enforcing dual-actor authorization boundaries when autonomous AI agents invoke tools and execute actions on behalf of authenticated users.
