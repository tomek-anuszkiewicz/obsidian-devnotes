---
title: Service-to-Service Authentication and Authorization in Azure and Kubernetes
tags:
  - authentication
  - authorization
  - azure
  - kubernetes
  - security
  - microservices
  - mtls
aliases:
  - Service-to-Service Authentication in Distributed Runtimes
  - S2S Auth in Azure and K8s
  - Service Authentication Patterns
---

Choosing service security starts with separate questions: can the caller reach the target, which workload is calling, and what may that workload do? A private network, a certificate, and an application permission answer different parts of that problem.

This article compares the models and keeps the organizational decision rules together. [[Workload Identity and Azure Resource Access from Services]] develops the Azure token, federation, resource-permission, and database flows. [[Workload Trust and Network Security in Kubernetes]] follows network policy, mTLS, meshes, and workload identity inside and between Kubernetes environments. A short decision table here remains useful before choosing either implementation path.

## Context

A distributed system may contain services running in several environments:

- inside one Kubernetes cluster,

- across multiple Kubernetes clusters,

- in Azure Kubernetes Service,

- in Azure App Service,

- on virtual machines,

- in other clouds,

- outside Kubernetes entirely.

These services may need to call:

- other HTTP or gRPC services,

- Azure SQL or PostgreSQL,

- Service Bus,

- Storage,

- Key Vault,

- services hosted on VMs,

- services hosted in App Service.

The main design question is not only:

> Can Service A reach Service B?

It is also:

- Can B prove that the caller is A?

- Is A allowed to perform this operation?

- Is the connection encrypted?

- Does the solution require distributing secrets?

- Does the identity remain valid across cluster boundaries?

- Who maintains the identity and authorization infrastructure?

No single technology solves all of these concerns.

---

## Separate the Security Layers

For every service-to-service interaction, distinguish the following layers.

### Connectivity

Can Service A establish a network connection to Service B?

Possible mechanisms:

- Kubernetes Service and DNS,

- routing,

- virtual networks,

- private endpoints,

- load balancers,

- gateways,

- Kubernetes `NetworkPolicy`,

- firewalls.

### Authentication

Can Service B establish that the caller really is Service A?

Possible mechanisms:

- Microsoft Entra access tokens,

- managed identities,

- AKS Workload Identity,

- mTLS certificates,

- service mesh workload identity,

- SPIFFE identities,

- custom signed JWTs,

- shared secrets.

### Authorization

Is Service A allowed to perform the requested operation?

Possible mechanisms:

- Entra app roles,

- OAuth scopes,

- service-mesh authorization policies,

- application policies,

- database roles,

- resource-level business authorization.

### Transport protection

Is the communication encrypted and protected from modification?

Possible mechanisms:

- TLS,

- mutual TLS,

- private networking combined with TLS,

- service mesh mTLS.

### Credential management

How are credentials issued, rotated, revoked, and audited?

A system may provide network isolation without identity, or identity without routing. These mechanisms should therefore be composed rather than confused with one another.

---

## Core Mental Model

```text
Kubernetes Service or routing
    tells A where B is

Network policy or firewall
    determines whether A can reach B

OAuth token, mTLS, or workload identity
    proves that A is A

Authorization policy
    determines what A may do

Application logic
    determines whether the operation is valid for the resource
```

A shared network should not automatically imply shared trust.

---

## Custom JWT or Custom Security Token Service

### How It Works

An organization may operate its own token issuer.

Service A authenticates to an internal Security Token Service and obtains a token:

```json
{
  "iss": "https://identity.internal",
  "aud": "service-b",
  "sub": "service-a",
  "permissions": [
    "customer.read"
  ],
  "exp": 1785980000
}
```

Service B validates the signature and claims using the issuer’s public keys.

The system may use OAuth standards or a fully custom token protocol.

### Advantages

- works independently of Azure,

- full control over claims and permission models,

- can support Kubernetes, VMs, multiple clouds, and legacy platforms,

- may integrate with an existing internal security platform,

- can offer a tailored developer experience.

### Disadvantages

The organization becomes responsible for:

- authenticating workloads,

- private signing keys,

- key rotation,

- JWKS publication,

- token expiration,

- audience validation,

- permission assignment,

- revocation strategy,

- audit,

- token endpoint availability,

- protocol and client libraries,

- long-term security maintenance.

Creating a JWT is easy.

Operating a trustworthy identity provider is not.

### Dangerous Custom Design

Avoid:

```text
Every service knows the same symmetric signing secret.
Every service can issue its own JWT.
```

Any compromised service could then:

- impersonate another service,

- grant itself roles,

- issue tokens for arbitrary audiences.

A safer model is:

```text
Central token issuer:
  owns private signing key

Services:
  only receive public verification keys
```

### Best Fit

A custom STS is justified mainly when:

- a mature internal identity platform already exists,

- multi-cloud or hybrid requirements cannot be met conveniently by Entra,

- the organization has dedicated security-platform ownership.

It should not normally be created merely to avoid configuring Entra.

---

## Shared Secrets and API Keys

### How They Work

Service A sends a shared credential:

```http
X-Api-Key: <secret>
```

or uses:

- client ID and secret,

- username and password,

- database connection password,

- shared certificate.

### Advantages

- simple,

- widely supported,

- cloud-neutral,

- works with legacy systems,

- low initial implementation cost.

### Disadvantages

- secrets must be distributed and stored,

- rotation is difficult,

- leaked credentials can often be reused from anywhere,

- weak workload identity,

- shared secrets may be reused by multiple instances or services,

- limited role and audience semantics,

- credentials may appear in logs, configuration, dumps, or CI systems,

- long-lived access remains valid until revoked.

### Best Fit

Use shared secrets mainly when:

- the target does not support workload identity or OAuth,

- integrating with legacy or third-party systems,

- temporarily migrating to a stronger mechanism.

Store them in a proper secret manager such as Key Vault rather than directly in application manifests.

---

## Scenario: Kubernetes Calling External SaaS or Non-Azure Systems

Managed Identity only helps directly when the external provider accepts:

- Microsoft Entra tokens,

- OIDC federation,

- workload identity federation.

Otherwise the integration may require:

- the provider’s OAuth client credentials,

- a client certificate,

- an API key,

- another secret.

Preferred order:

```text
workload federation
OAuth with short-lived token
mTLS client certificate
long-lived shared API key
```

Not every provider supports the stronger options.

When a secret is unavoidable:

- store it in Key Vault,

- access Key Vault with Workload Identity,

- rotate it,

- restrict its permissions,

- prevent logging.

To avoid writing custom secret-retrieval code in every pod, deploy the Azure Key Vault Secrets Store CSI Driver. Workload Identity authenticates the CSI driver against Key Vault, which mounts the secret as a local volume file in the container filesystem or synchronizes it to a Kubernetes `Secret` resource without exposing connection strings in source control.

---

## User Context Is Separate from S2S Authentication

Service-to-service authentication answers:

> Which workload is calling?

User context answers:

> Which user originally initiated the operation?

For example:

```text
technical caller = Service A
original initiator = User U
```

A token proving Service A’s identity does not automatically prove the user’s authorization.

A may additionally propagate:

- user ID,

- tenant ID,

- correlation ID,

- trace context.

Service B decides whether it authorizes:

- Service A,

- the user,

- or both.

The user ID should be treated as context unless protected delegation is explicitly used.

### Forwarding Browser Tokens vs. Protected Delegation

Forwarding an incoming user browser token directly across internal services is a dangerous anti-pattern. User tokens are issued for a specific public audience (such as the API gateway or edge service). Replaying them internally means downstream services must either skip audience validation—allowing any token to be replayed anywhere—or fail the call. Furthermore, if an internal service is compromised, stolen user tokens can be used to impersonate the user against other systems. User tokens also have short lifetimes (often 60 minutes), breaking background workers and asynchronous message consumers.

When downstream operations genuinely require verified user delegation, use the OAuth 2.0 On-Behalf-Of (OBO) flow. The edge service exchanges the user token for a new token scoped strictly to Service B's audience. Otherwise, keep machine authentication distinct: Service A authenticates with its own workload identity (Managed Identity or mTLS) and passes the user ID, tenant ID, and correlation ID strictly as unprivileged metadata headers (`X-User-ID`, `X-Correlation-ID`).

---

## Recommended Organizational Strategy

A pragmatic Azure and Kubernetes strategy could be:

### Kubernetes network security

Use:

```text
default-deny NetworkPolicy
explicit ingress and egress rules
```

### Azure resource access

Use:

```text
Managed Identity
AKS Workload Identity
```

for Azure SQL, Storage, Service Bus, Key Vault, and supported APIs.

### General Azure S2S

Use:

```text
Entra OAuth with audience and app roles
```

for communication across:

- clusters,

- AKS and App Service,

- AKS and VMs,

- different hosting environments.

### Strong Kubernetes workload security

Use a service mesh when:

- mTLS is required,

- there are many internal workload policies,

- Kubernetes is the dominant platform,

- the operational cost is justified.

### Multi-cloud or hybrid identity

Consider:

```text
SPIFFE/SPIRE
```

when portability is more important than Azure-native simplicity.

### Legacy and unsupported targets

Use secrets only when stronger identity mechanisms are unavailable.

Keep secrets in a dedicated secret store and design rotation from the beginning.

---

## Decision Table

|Scenario|Baseline|Preferred stronger solution|
|---|---|---|
|Pod to pod in one cluster|NetworkPolicy|Service mesh mTLS and workload authorization|
|Pod to pod across clusters|Routing and local policies|Entra OAuth or multicluster mesh|
|Pod to Azure SQL|Database secret|AKS Workload Identity and Entra authentication|
|Pod to Service Bus, Storage, or Key Vault|Secret|AKS Workload Identity|
|AKS to App Service|API key|Entra OAuth|
|AKS to VM API in Azure|Private network and secret|Entra OAuth|
|Kubernetes and VMs across clouds|mTLS or JWT|SPIFFE/SPIRE|
|App Service to Azure resource|Secret|Managed Identity|
|VM to Azure resource|Secret|Managed Identity|
|External SaaS|API key|OAuth or workload federation when supported|

---

## Warning Signs

The design should be reconsidered when:

- every pod can call every service,

- one cluster-wide identity is shared by all workloads,

- a shared API key is treated as workload identity,

- Service B validates only that a JWT is signed but ignores audience,

- all services use the role `internal-service`,

- applications share one JWT signing secret,

- Kubernetes YAML can grant arbitrary Azure permissions,

- one user-assigned managed identity is reused without clear justification,

- browser cookies are forwarded as S2S credentials,

- database passwords are used even though Entra authentication is supported,

- a service mesh is introduced without operational ownership,

- a custom token issuer has no clear key-rotation and audit model.

---

## Practical Rules

1. Treat the cluster as a shared network, not as one trusted identity.

2. Use `NetworkPolicy` as a baseline for Kubernetes network segmentation.

3. Give each important workload its own Kubernetes Service Account.

4. Use separate workload identities where least privilege matters.

5. Prefer Managed Identity for Azure resources that support Entra authentication.

6. Use AKS Workload Identity instead of client secrets in pods.

7. Use audience-restricted tokens for S2S APIs.

8. Validate issuer, audience, expiration, and permissions in Service B.

9. Do not treat a valid signature as sufficient authorization.

10. Keep network access and application authorization as separate controls.

11. Use service mesh only when its security and traffic-management benefits justify the operational cost.

12. Prefer Entra OAuth for communication across Azure hosting boundaries.

13. Prefer SPIFFE when workload identity must be portable across clouds and VMs.

14. Avoid custom JWT infrastructure unless there is dedicated long-term ownership.

15. Use shared secrets only when the target does not support a stronger identity mechanism.

16. Keep permission assignment in infrastructure code, not application Deployment YAML.

17. Test S2S access both positively and negatively: allowed callers should succeed, forbidden callers should fail.

---

## Final Mental Model

Inside a Kubernetes cluster:

```text
NetworkPolicy
    limits who can reach whom
```

For strong Kubernetes workload identity:

```text
service mesh or SPIFFE
    proves which workload is calling
```

For access to Azure resources:

```text
Managed Identity or AKS Workload Identity
    removes application secrets
```

For S2S across AKS, App Service, VMs, or clusters:

```text
Microsoft Entra OAuth
    provides a shared Azure identity model
```

For hybrid and multi-cloud systems:

```text
SPIFFE/SPIRE
    provides portable workload identity
```

The overall principle is:

> Use network controls to limit reachability, workload identity to authenticate callers, and target-owned policies to authorize operations.

Or more concisely:

> Network location is not identity.
> Identity is not authorization.
> Authentication should not require long-lived application secrets.

(See [[Service vs User Authorization Models]] and [[Propagating User Context Between Services]]).

## Related Notes

- [[Service vs User Authorization Models]] — Distinguishing between ambient service identity and end-user delegated authorization.
- [[Propagating User Context Between Services]] — Forwarding caller identities, claims, and tenant context across microservice chains.
- [[Remote Service Calls — Errors, Resilience, and Observability]] — Authentication, error interpretation, and runtime policy across service boundaries.
- [[Standardizing Service Infrastructure with Reusable Blocks]] — Standardizing token validation, mTLS, and identity bootstrapping.
