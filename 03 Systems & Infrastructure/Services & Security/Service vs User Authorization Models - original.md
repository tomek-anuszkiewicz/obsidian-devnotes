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
---

# Service vs User Authorization Models

In distributed microservice architectures, answering the question *"Is this request allowed?"* requires determining **which service owns the authorization rule** and **which identity is being authorized**.

This document details the authorization models, token handling practices, and identity delegation principles when propagating user context. It is an atomic guideline complementing [[Propagating User Context Between Services]] and [[User Context in Asynchronous Systems]].

---

## 1. The Core Authorization Dilemma

When Service A calls Service B on behalf of User U:

```text
User U ──> Gateway ──> Service A ──> Service B
```

There are two primary actors involved:
1. **Technical Caller:** Service A (authenticated machine identity).
2. **Original Initiator:** User U (human or external user context).

Authorization must determine: does Service B evaluate permissions for **Service A**, for **User U**, or for the combination of both?

---

## 2. Two Valid Authorization Models

### Model 1: Service B Authorizes Service A (Capability-Oriented)

In this model, Service A is the authoritative owner of the business use case and user permission checks. Service B provides a supporting internal capability.

```text
User U ──[places order]──> Order Service (Service A)
                              │
                              ├── (1) Validates User U has permission to order.
                              └── (2) Calls Inventory Service (Service B) with Service Token.
                                    ↓
                           Inventory Service
                              │
                              └── Verifies: "Order Service is allowed to reserve inventory."
                                  (Does NOT re-evaluate User U's permissions).
```

* **When to use:**
  * Service A completely owns the business workflow (e.g. checkout, batch processing).
  * Service B is an internal utility or low-level subsystem (e.g. inventory ledger, notification sender).
  * The resource in Service B does not have a direct user-facing access control list.
* **Audit Responsibility:** Service A passes `initiatedByUserId` as contextual metadata so Service B records both the technical actor (Order Service) and the original user in its audit logs.

---

### Model 2: Service B Authorizes the User (Resource-Oriented)

In this model, Service B is the authoritative owner of the protected domain resource and its security rules.

```text
User U ──[edits doc]──> Web Portal (Service A)
                           │
                           └── Calls Document Service (Service B)
                                 passing User ID + Service Identity.
                                 ↓
                        Document Service
                           │
                           └── Evaluates: "Can User U edit Document D?"
```

* **When to use:**
  * Service B owns sensitive domain entities with granular ACLs (e.g. Document Service, Payroll Service, Medical Records).
  * Access rules depend on resource-specific ownership, department boundaries, or document-level sharing settings stored exclusively within Service B.
* **Evaluation in Code:**
  ```csharp
  await authorizationService.AuthorizeAsync(
      userId,
      documentId,
      Permission.Edit,
      cancellationToken);
  ```
* **Critical Requirement:** Service B must authenticate Service A before accepting `userId`. An untrusted caller must never be allowed to assert arbitrary user identities.

---

## 3. Delegation vs. Impersonation

When propagating user context, systems must preserve both identities rather than collapsing them:

```text
Preferred: Delegation
Service B understands: "Service A is acting on behalf of User U."
Audit record: Caller = Service A, Initiator = User U.

Anti-Pattern: Impersonation
Service B behaves as if User U connected directly over a local loop.
Audit record: Caller = User U (Hides the fact that Service A made the call).
```

Preserving the full delegation chain (`User -> Gateway -> Service A -> Service B`) is essential for:
- Forensics during security incidents (detecting compromised internal services).
- Detecting privilege escalation where an unauthorized service attempts to invoke operations using legitimate user IDs.
- Compliance and non-repudiation auditing.

---

## 4. Token Forwarding Hazards

### Why Not Forward Browser Cookies?
- Cookies are tightly bound to the frontend domain and gateway session state.
- Exposing cookies to internal microservices tightly couples backends to external authentication schemes.
- Cookies cannot be safely forwarded to asynchronous queues or background tasks.

### Why Not Blindly Forward the User's JWT?
Forwarding the original user access token received at the API gateway down the entire call chain introduces severe risks:

```text
User JWT ──> Gateway ──> Service A ──(Blind Forward)──> Service B ──(Blind Forward)──> Service C
```

1. **Audience Mismatch:** A token issued for `aud: "api-gateway"` or `aud: "service-a"` is semantically invalid for Service B or Service C.
2. **Excessive Privilege Leakage:** The user's token may carry scopes for billing, administration, or personal profiles that downstream services have no business seeing.
3. **Token Expiration in Long Flows:** If downstream processing takes time or involves retries, the user's short-lived token will expire midway through the execution chain.

---

## 5. Explicit Delegation via Token Exchange

When Service B genuinely requires cryptographically verified user claims, implement explicit token exchange (such as **OAuth 2.0 Token Exchange, RFC 8693**):

```text
Service A (with User Token) ──> Identity Provider (IdP) / STS
                                    │
                                    └── Exchanges User Token + Service A Credentials
                                          for a Downscoped Delegated Token
                                    ↓
Service A ──[Delegated Token (aud: Service B, scope: read:docs)]──> Service B
```

The delegated token:
- Targets Service B specifically (`aud: service-b`).
- Is constrained to the minimum scopes needed for the operation.
- Explicitly contains an `act` (actor) claim representing Service A and a `sub` (subject) claim representing User U.

---

## 6. Audit Logging Structure

When user context is propagated, Service B should record structured audit events capturing both identities:

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

---

Next steps: See [[User Context in Asynchronous Systems]] for message brokers and queues, or return to [[Propagating User Context Between Services]].
