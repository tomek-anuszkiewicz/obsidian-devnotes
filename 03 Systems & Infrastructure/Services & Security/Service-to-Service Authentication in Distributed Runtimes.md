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
  - S2S Auth in Azure and K8s
  - Service Authentication Patterns
---

> [!NOTE] Foundational Systems Architecture (Non-LLM Scope)
> This note forms part of an emerging exploration into foundational distributed systems and runtime infrastructure (independent of LLM or agent workflows). While currently cataloged as an isolated architectural blueprint, it is slated for future consolidation into a unified backend systems pillar as broader operational notes are developed.

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

# Kubernetes NetworkPolicy

## What It Does

Kubernetes `NetworkPolicy` controls network communication between selected pods and external destinations.

A common baseline is:

```text
default deny
+
explicit allow rules
```

For example:

```text
orders-api may connect to inventory-api:8080
reporting-api may not connect to inventory-api
```

A policy can select workloads using:

- namespaces,
    
- pod labels,
    
- protocols,
    
- ports,
    
- source and destination rules.
    

## Advantages

- declarative YAML configuration,
    
- no authentication code in the application,
    
- low runtime overhead,
    
- useful protection against lateral movement,
    
- good visibility of intended network flows,
    
- natural fit for Kubernetes,
    
- no application secrets required.
    

## Disadvantages

- mainly a network-level control,
    
- does not normally provide cryptographic workload identity,
    
- Service B may not know with certainty that the caller is A,
    
- does not automatically encrypt traffic,
    
- usually cannot express business operations,
    
- does not naturally work across cluster boundaries,
    
- depends on a CNI implementation that enforces the policies,
    
- labels and namespace structure become security-relevant.
    

## Best Fit

Use it as a baseline for traffic inside a Kubernetes cluster.

It is particularly useful for:

- reducing unnecessary pod-to-pod access,
    
- limiting database egress,
    
- separating namespaces or domains,
    
- protecting internal services from unrelated workloads.
    

It should not normally be the only protection for highly privileged APIs.

---

# Service Mesh and mTLS

## What It Does

A service mesh such as Istio can provide:

- workload identity,
    
- automatic mutual TLS,
    
- short-lived certificates,
    
- service-to-service authorization policies,
    
- routing,
    
- retries and traffic management,
    
- communication telemetry.
    

A workload may be identified using its Kubernetes Service Account:

```text
cluster.local/ns/orders/sa/orders-api
```

A policy can then express:

```text
orders-api may POST /reservations on inventory-api
```

## Advantages

- strong cryptographic workload identity,
    
- encrypted pod-to-pod traffic,
    
- no bearer tokens handled by application code,
    
- short-lived and automatically rotated credentials,
    
- policies based on workload identity rather than only IP,
    
- possible HTTP method and path authorization,
    
- common traffic telemetry,
    
- can support multiple clusters.
    

## Disadvantages

- significant DevOps complexity,
    
- additional proxies or ambient data-plane components,
    
- more difficult networking diagnostics,
    
- extra CPU, memory, and latency,
    
- control-plane and certificate-management responsibilities,
    
- interactions between Kubernetes networking and mesh routing,
    
- does not replace business-level authorization,
    
- can be disproportionate for a small system.
    

## Best Fit

Consider a mesh when:

- Kubernetes is the primary application platform,
    
- many teams share the platform,
    
- workloads require strong mutual identity,
    
- internal traffic must be encrypted,
    
- there are many service-to-service policies,
    
- a multi-cluster Kubernetes platform needs one identity model.
    

---

# SPIFFE and SPIRE

## What They Do

SPIFFE defines a standard format for workload identities.

A workload may receive an identity such as:

```text
spiffe://company.internal/orders/orders-api
```

SPIRE can issue and rotate:

- X.509 workload certificates,
    
- signed JWT identities,
    
- trust bundles.
    

The identities can be used by:

- applications,
    
- Envoy proxies,
    
- service meshes,
    
- Kubernetes workloads,
    
- virtual machines,
    
- workloads in multiple clouds.
    

## Advantages

- cloud-neutral workload identity,
    
- strong cryptographic authentication,
    
- no long-lived application secrets,
    
- suitable for Kubernetes, VMs, and hybrid environments,
    
- supports multiple clusters and trust-domain federation,
    
- avoids tying workload identity to one cloud provider.
    

## Disadvantages

- the organization operates its own identity infrastructure,
    
- requires SPIRE servers, agents, registration, and trust management,
    
- authorization still needs a separate design,
    
- higher operational and conceptual complexity,
    
- fewer developers and operators may be familiar with it,
    
- integration may require proxies or application changes.
    

## Best Fit

SPIFFE/SPIRE is attractive when:

- the organization is multi-cloud,
    
- Kubernetes and VMs must share one workload identity model,
    
- cloud-provider independence is important,
    
- the organization can maintain an internal identity platform.
    

---

# Microsoft Entra OAuth for S2S

## How It Works

Service B is exposed as a protected API.

Service A has its own workload or application identity.

A obtains an access token for B:

```text
audience = Service B
caller = Service A
roles = allowed capabilities
```

It then calls B:

```http
Authorization: Bearer <access-token>
```

Service B validates:

- token signature,
    
- issuer,
    
- audience,
    
- expiration,
    
- caller identity,
    
- app roles or permissions.
    

B normally validates the JWT locally using the issuer’s public signing keys. It does not need to call Entra for every request.

## Advantages

- strong service identity,
    
- standard OAuth and JWT mechanisms,
    
- audience-restricted tokens,
    
- app roles and application permissions,
    
- works across clusters,
    
- works between AKS, App Service, VMs, and other hosts,
    
- central key rotation and token issuance,
    
- no need to maintain a custom token issuer,
    
- good auditability.
    

## Disadvantages

- requires Entra configuration,
    
- APIs and caller identities must be registered,
    
- app-role assignments require management,
    
- token acquisition and caching must be configured,
    
- routing and TLS are still separate concerns,
    
- introduces dependency on Entra for issuing new tokens,
    
- may feel administratively heavy for a very small internal system.
    

## Best Fit

Entra OAuth is a natural default when:

- the environment is strongly Azure-based,
    
- services run on different hosting platforms,
    
- services communicate across cluster boundaries,
    
- a consistent identity model is required for AKS, App Service, and VMs.
    

---

# Managed Identity

## What It Is

A managed identity is an identity managed by Microsoft Entra for an Azure workload.

Instead of storing:

```text
client ID
client secret
```

the workload obtains short-lived access tokens through the Azure identity platform.

Managed Identity can be used for more than service-to-service HTTP calls.

The same workload identity may access:

- Azure SQL,
    
- Azure Database for PostgreSQL,
    
- Key Vault,
    
- Storage,
    
- Service Bus,
    
- another Entra-protected API.
    

## System-Assigned Identity

A system-assigned identity belongs to the lifecycle of one Azure resource.

It is natural for:

- App Service,
    
- Azure Functions,
    
- VMs,
    
- other directly managed Azure resources.
    

Deleting the Azure resource deletes the identity.

## User-Assigned Identity

A user-assigned identity is an independent Azure resource.

It can be attached or federated to workloads.

This is commonly useful for AKS because Kubernetes pods are dynamic and are not themselves persistent Azure resources.

## Advantages

- removes long-lived client secrets,
    
- Azure manages the identity lifecycle and credentials,
    
- short-lived access tokens,
    
- good integration with Azure SDKs,
    
- centralized role assignment,
    
- one identity can access several Azure resource types,
    
- supports least-privilege permissions per workload.
    

## Disadvantages

- Azure-specific,
    
- role assignments can become difficult to inventory,
    
- accidental identity sharing can create excessive permissions,
    
- not all resources support Entra authentication,
    
- local development uses a different identity source,
    
- application and database permissions may require separate configuration.
    

---

# AKS Workload Identity

## How It Works

AKS Workload Identity connects a Kubernetes workload to Microsoft Entra using OIDC federation.

The flow is:

```text
Kubernetes Service Account
        ↓
projected Kubernetes OIDC token
        ↓
federated identity credential
        ↓
Entra workload or managed identity
        ↓
access token for target resource
```

The trust relationship is normally bound to:

```text
cluster issuer
namespace
Kubernetes Service Account
```

Under the hood, an admission webhook intercepts pod creation, projecting a short-lived Kubernetes ServiceAccount token into the pod volume and injecting environment variables (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_FEDERATED_TOKEN_FILE`). The Azure SDK exchanges this projected OIDC token with Microsoft Entra ID using the federated credential configured for the Managed Identity, scoped to the audience `api://AzureADTokenExchange`.

## Kubernetes Configuration

A Service Account can identify which Entra identity the workload should use:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: orders-api
  namespace: orders
  annotations:
    azure.workload.identity/client-id: "<identity-client-id>"
```

The Deployment selects the Service Account:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orders-api
  namespace: orders
spec:
  template:
    metadata:
      labels:
        azure.workload.identity/use: "true"
    spec:
      serviceAccountName: orders-api
      containers:
        - name: orders-api
          image: company/orders-api:1.0
```

## Important Responsibility Boundary

Kubernetes YAML should state:

> Which identity does this workload use?

Azure infrastructure configuration should state:

> What may that identity access?

For example:

```text
Kubernetes YAML:
  Service Account
  workload identity binding
  non-secret endpoint configuration

Terraform or Bicep:
  managed identity
  federated credential
  Azure RBAC
  API role assignments
  database principals
```

Changing a Deployment should not automatically allow a team to grant itself access to arbitrary resources.

## Advantages

- no client secret in Kubernetes,
    
- identity aligned with Kubernetes Service Accounts,
    
- separate identity per application,
    
- reusable for APIs, databases, queues, and storage,
    
- integrates with `DefaultAzureCredential`,
    
- works across pod restarts and replicas,
    
- suitable for fine-grained least privilege.
    

## Disadvantages

- requires federation configuration between AKS and Entra,
    
- debugging issuer, subject, and audience errors can be difficult,
    
- incorrect Service Account or annotation configuration causes runtime failures,
    
- Azure role assignment and resource-specific permissions are still required,
    
- remains tied to Entra and Azure-supported targets.
    

---

# Passwordless Database Access

## What “Passwordless” Means

The application still needs target configuration:

```text
server = orders-db.database.windows.net
database = Orders
```

It no longer needs:

```text
username
password
```

A connection string may still exist, but it contains location and authentication mode rather than a secret.

For example:

```text
Server=tcp:orders-db.database.windows.net,1433;
Database=Orders;
Encrypt=True;
Authentication=Active Directory Default;
```

A more precise term is:

> secretless connection configuration

rather than literally no connection string.

## Authorization Layers

Managed Identity does not automatically provide database access.

The database must:

1. support Microsoft Entra authentication,
    
2. recognize the workload identity,
    
3. grant the identity the necessary database permissions.
    

For example:

```sql
CREATE USER [orders-api-identity]
FROM EXTERNAL PROVIDER;

ALTER ROLE db_datareader
ADD MEMBER [orders-api-identity];

ALTER ROLE db_datawriter
ADD MEMBER [orders-api-identity];
```

The network may additionally restrict access using:

- private endpoints,
    
- firewalls,
    
- Kubernetes egress policies,
    
- private virtual networks.
    

## Advantages

- no database password to distribute,
    
- no password rotation in Kubernetes,
    
- separate identity per service,
    
- centralized access revocation,
    
- short-lived credentials,
    
- improved least privilege and auditability.
    

## Disadvantages

- requires database and driver support,
    
- token refresh must work correctly with connection pooling,
    
- database migrations may use a different identity,
    
- CI/CD requires its own access model,
    
- diagnosing token and database-principal problems can be harder than checking a password,
    
- Azure RBAC does not always replace grants inside the database.
    

## Connection Pooling and Token Expiration

When using secretless authentication with database connection poolers (such as ADO.NET, HikariCP, or Npgsql), verify driver support for automated token refreshes. 

If a connection pooler initializes physical TCP connections with an OAuth access token, those pooled connections can fail or throw authentication exceptions when the initial token expires (typically after 60 minutes) unless the driver or pooler actively retrieves fresh tokens when validating or opening connections. Modern drivers (such as `Microsoft.Data.SqlClient` or modern `Npgsql` plugins) manage token lifecycles natively when configured for Active Directory Default authentication.

---

# Custom JWT or Custom Security Token Service

## How It Works

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

## Advantages

- works independently of Azure,
    
- full control over claims and permission models,
    
- can support Kubernetes, VMs, multiple clouds, and legacy platforms,
    
- may integrate with an existing internal security platform,
    
- can offer a tailored developer experience.
    

## Disadvantages

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

## Dangerous Custom Design

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

## Best Fit

A custom STS is justified mainly when:

- a mature internal identity platform already exists,
    
- multi-cloud or hybrid requirements cannot be met conveniently by Entra,
    
- the organization has dedicated security-platform ownership.
    

It should not normally be created merely to avoid configuring Entra.

---

# Shared Secrets and API Keys

## How They Work

Service A sends a shared credential:

```http
X-Api-Key: <secret>
```

or uses:

- client ID and secret,
    
- username and password,
    
- database connection password,
    
- shared certificate.
    

## Advantages

- simple,
    
- widely supported,
    
- cloud-neutral,
    
- works with legacy systems,
    
- low initial implementation cost.
    

## Disadvantages

- secrets must be distributed and stored,
    
- rotation is difficult,
    
- leaked credentials can often be reused from anywhere,
    
- weak workload identity,
    
- shared secrets may be reused by multiple instances or services,
    
- limited role and audience semantics,
    
- credentials may appear in logs, configuration, dumps, or CI systems,
    
- long-lived access remains valid until revoked.
    

## Best Fit

Use shared secrets mainly when:

- the target does not support workload identity or OAuth,
    
- integrating with legacy or third-party systems,
    
- temporarily migrating to a stronger mechanism.
    

Store them in a proper secret manager such as Key Vault rather than directly in application manifests.

---

# Scenario: Services Inside One Kubernetes Cluster

## Minimal Practical Baseline

```text
separate Kubernetes Service Account per service
+
default-deny NetworkPolicy
+
explicit A → B rules
+
TLS where required
+
application authorization for privileged operations
```

### Benefits

- relatively simple,
    
- no identity infrastructure required for every request,
    
- useful reduction of lateral movement,
    
- easy to represent as YAML.
    

### Limitations

- network policy alone does not provide strong caller identity,
    
- access is tied to network placement and selectors,
    
- difficult to extend directly outside the cluster.
    

## Stronger Model

Add:

```text
service mesh mTLS
+
workload identity
+
authorization policies
```

Use when the cluster hosts many sensitive or independently owned workloads.

For example, an Istio policy can enforce cryptographic identity and method restrictions without application changes:

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-orders-to-inventory
  namespace: inventory
spec:
  selector:
    matchLabels:
      app: inventory-api
  action: ALLOW
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/orders/sa/orders-api"]
      to:
        - operation:
            methods: ["POST"]
            paths: ["/reservations*"]
```

## Azure-Consistent Model

Use Entra OAuth even between pods when one uniform identity model is desired across:

- AKS,
    
- multiple clusters,
    
- App Service,
    
- VMs.
    

This may be more configuration than necessary for simple internal communication, but it avoids changing the authentication model when a service later moves outside the cluster.

---

# Scenario: Communication Between Kubernetes Clusters

## NetworkPolicy Alone

`NetworkPolicy` remains local to each cluster.

It can allow:

- egress from A,
    
- ingress to B,
    
- communication through a gateway.
    

It does not create:

- cross-cluster routing,
    
- shared DNS,
    
- end-to-end workload identity,
    
- mutual trust.
    

## Available Models

### Entra OAuth

Good when clusters run in Azure or services already use Entra.

Advantages:

- identity survives cluster boundaries,
    
- no shared mesh required,
    
- works with non-Kubernetes targets.
    

Disadvantages:

- network routing and TLS remain separate,
    
- every API must validate tokens,
    
- role assignments must be administered.
    

### Multicluster Service Mesh

Good when Kubernetes is the dominant platform.

Advantages:

- common service discovery,
    
- workload identity,
    
- mTLS,
    
- routing and authorization policies.
    

Disadvantages:

- complex gateways, trust domains, routing, and operations,
    
- large failure and upgrade surface.
    

### SPIFFE Federation

Good for multi-cloud and hybrid infrastructure.

Advantages:

- portable workload identity,
    
- supports Kubernetes and VMs,
    
- avoids cloud-provider lock-in.
    

Disadvantages:

- self-operated identity control plane,
    
- separate authorization design.
    

---

# Scenario: AKS Workload Calling Azure SQL

Recommended composition:

```text
private network or firewall rules
+
AKS Workload Identity
+
Entra authentication
+
database grants
```

Network controls determine whether the pod can reach SQL.

Workload Identity proves which application is connecting.

Database roles determine what that identity can read or modify.

This is generally preferable to storing a database password in Kubernetes.

---

# Scenario: AKS Calling Azure Service Bus, Storage, or Key Vault

Recommended model:

```text
AKS Workload Identity
+
Azure RBAC or resource-specific permissions
+
private endpoint where appropriate
```

Advantages:

- no service credentials in Kubernetes,
    
- one identity per workload,
    
- centralized revocation,
    
- standard Azure SDK support.
    

Key Vault is still needed for external or legacy secrets, but Managed Identity removes the need for a secret to access Key Vault itself.

---

# Scenario: AKS Calling App Service

## Preferred Azure Model

```text
AKS Workload Identity
    obtains Entra token for App Service API

App Service
    validates Entra token
```

Network access may use:

- public HTTPS,
    
- private endpoints,
    
- VNet integration,
    
- internal gateways.
    

## Advantages

- same identity model across different hosting environments,
    
- no shared API key,
    
- caller identity and roles are visible,
    
- does not depend on a common Kubernetes cluster.
    

## Disadvantages

- API registration and role assignment are required,
    
- private routing requires additional Azure networking,
    
- token validation must be configured correctly.
    

---

# Scenario: AKS Calling a Service on a VM

## Entra OAuth

Appropriate when the VM and API are part of the Azure identity environment.

The VM-hosted API validates Entra JWTs.

Advantages:

- unified identity model,
    
- no custom issuer,
    
- application roles and audience.
    

Disadvantages:

- the VM application must configure token validation,
    
- TLS, routing, and firewalls remain the operator’s responsibility.
    

## mTLS or SPIFFE

Appropriate for hybrid or multi-cloud systems.

Advantages:

- strong workload identity,
    
- cloud-independent,
    
- encryption and authentication together.
    

Disadvantages:

- certificate and trust infrastructure,
    
- higher operational complexity.
    

## Custom JWT

Use only when a mature internal STS exists.

---

# Scenario: App Service or VM Calling Azure Resources

Managed Identity is usually the preferred mechanism.

Examples:

```text
App Service → Key Vault
App Service → Azure SQL
VM → Storage
VM → Service Bus
```

A system-assigned identity is often appropriate when access belongs exclusively to that Azure resource.

A user-assigned identity can be used when:

- lifecycle must be independent,
    
- an identity must survive resource recreation,
    
- selected workloads intentionally share the same access profile.
    

Identity sharing should be deliberate because it reduces audit precision and increases the impact of a compromised workload.

---

# Scenario: Kubernetes Calling External SaaS or Non-Azure Systems

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

# User Context Is Separate from S2S Authentication

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

## Forwarding Browser Tokens vs. Protected Delegation

Forwarding an incoming user browser token directly across internal services is a dangerous anti-pattern. User tokens are issued for a specific public audience (such as the API gateway or edge service). Replaying them internally means downstream services must either skip audience validation—allowing any token to be replayed anywhere—or fail the call. Furthermore, if an internal service is compromised, stolen user tokens can be used to impersonate the user against other systems. User tokens also have short lifetimes (often 60 minutes), breaking background workers and asynchronous message consumers.

When downstream operations genuinely require verified user delegation, use the OAuth 2.0 On-Behalf-Of (OBO) flow. The edge service exchanges the user token for a new token scoped strictly to Service B's audience. Otherwise, keep machine authentication distinct: Service A authenticates with its own workload identity (Managed Identity or mTLS) and passes the user ID, tenant ID, and correlation ID strictly as unprivileged metadata headers (`X-User-ID`, `X-Correlation-ID`).

---

# Recommended Organizational Strategy

A pragmatic Azure and Kubernetes strategy could be:

## Kubernetes network security

Use:

```text
default-deny NetworkPolicy
explicit ingress and egress rules
```

## Azure resource access

Use:

```text
Managed Identity
AKS Workload Identity
```

for Azure SQL, Storage, Service Bus, Key Vault, and supported APIs.

## General Azure S2S

Use:

```text
Entra OAuth with audience and app roles
```

for communication across:

- clusters,
    
- AKS and App Service,
    
- AKS and VMs,
    
- different hosting environments.
    

## Strong Kubernetes workload security

Use a service mesh when:

- mTLS is required,
    
- there are many internal workload policies,
    
- Kubernetes is the dominant platform,
    
- the operational cost is justified.
    

## Multi-cloud or hybrid identity

Consider:

```text
SPIFFE/SPIRE
```

when portability is more important than Azure-native simplicity.

## Legacy and unsupported targets

Use secrets only when stronger identity mechanisms are unavailable.

Keep secrets in a dedicated secret store and design rotation from the beginning.

---

# Decision Table

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

# Warning Signs

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

# Practical Rules

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

# Final Mental Model

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
- [[Service-to-Service Communication - How Service A Should Call Service B]] — Synchronous and asynchronous communication mechanics between distributed services.
- [[Standardizing Service Infrastructure with Reusable Blocks]] — Standardizing token validation, mTLS, and identity bootstrapping.
