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

# Service-to-Service Authentication and Authorization in Azure and Kubernetes

When designing communication between microservices, a common trap is conflating network reachability with workload identity. An IP address, a Kubernetes Service DNS name (`inventory-api.orders.svc.cluster.local`), or a private virtual network subnet lets packets flow between hosts, but it provides zero cryptographic proof of who the caller actually is. 

Relying on network-level reachability alone invites lateral movement: if an attacker gains execution inside any pod or container on that network, every downstream internal API is wide open. A solid service-to-service architecture separates packet routing from cryptographic authentication and fine-grained authorization.

```text
+-----------------------------------------------------------------------------------------+
|                         LAYERED SERVICE-TO-SERVICE TOPOLOGY                             |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|  [ Workload A (Pod / VM / App) ]                    [ Workload B (Target Service) ]     |
|  Identity: sa/orders-api                             Identity: sa/inventory-api         |
|                                                                                         |
|  +-----------------------------+                    +--------------------------------+  |
|  | Layer 7: Application / Authz |                    | Layer 7: Policy Verification   |  |
|  | Audience-bound Token / Role | -- App Claims ---> | Validates Issuer, Aud, Roles   |  |
|  +-----------------------------+                    +--------------------------------+  |
|                 |                                                  ^                    |
|  +-----------------------------+                    +--------------------------------+  |
|  | Layer 4: Cryptographic mTLS |                    | Layer 4: TLS Termination       |  |
|  | Short-lived SPIFFE/X.509    | == Mutual TLS ===> | Verifies SAN / Client Cert     |  |
|  +-----------------------------+                    +--------------------------------+  |
|                 |                                                  ^                    |
|  +-----------------------------+                    +--------------------------------+  |
|  | Layer 3: Network Topology   |                    | Layer 3: Packet Filtering      |  |
|  | DNS Resolution / Service IP | --- IP Packet ---> | NetworkPolicy / Subnet NSG     |  |
|  +-----------------------------+                    +--------------------------------+  |
|                                                                                         |
+-----------------------------------------------------------------------------------------+
```

---

## Context

In modern distributed topologies, workloads rarely run in a single homogeneous cluster. A typical system often runs services across several environments:

- Inside a single Kubernetes cluster
- Across multiple Kubernetes clusters (multi-region or multi-tenant)
- In Azure Kubernetes Service (AKS)
- In Azure App Service or Azure Container Apps
- On virtual machines (IaaS)
- In other clouds (AWS, GCP) or on-premise data centers
- Outside Kubernetes entirely

These services call a mix of internal APIs and cloud infrastructure:

- Downstream HTTP or gRPC internal APIs
- Azure SQL, PostgreSQL, or managed MySQL
- Azure Service Bus or event brokers
- Azure Blob Storage
- Azure Key Vault
- Services running on private VMs or App Services

The core architectural question is not simply:

> Can Service A reach Service B over the network (governed by [[Service-to-Service Communication - How Service A Should Call Service B|service-to-service communication]])?

It requires answering six distinct operational questions:

1. **Proof of Origin**: Can Service B cryptographically prove that the caller is Service A (establishing clear [[Service vs User Authorization Models|service vs user authorization models]])?
2. **Authorization**: Is Service A allowed to perform this specific operation on this specific resource?
3. **Transport Integrity**: Is the payload encrypted in flight and protected against man-in-the-middle manipulation?
4. **Secret Management**: Does the interaction rely on static passwords and pre-shared keys, or on automated, short-lived tokens and certificates?
5. **Portability**: Does the caller's identity remain valid and verifiable across cluster, subnet, or cloud boundaries?
6. **Caller Context**: How is the original user identity or tenant context propagated downstream without conflating service permissions with user permissions (see [[Propagating User Context Between Services|propagating user context between services]] and [[User Context in Asynchronous Systems|user context in asynchronous systems]])?

No single tool or abstraction solves all of these concerns simultaneously.

---

## Separate the Security Layers

For every service-to-service interaction—whether delivered via independent microservices or standardized components in [[Standardizing Service Infrastructure with Reusable Blocks|reusable infrastructure blocks]]—keep each security layer distinct.

### 1. Connectivity
*Can Service A route a packet to Service B?*
- Kubernetes Services and CoreDNS
- Virtual network peering and routing tables
- Azure Private Endpoints and Private Link
- Internal load balancers and API gateways
- Kubernetes `NetworkPolicy` and Azure Network Security Groups (NSGs)
- Firewalls and egress proxies

### 2. Authentication
*Can Service B verify that the caller is genuinely Service A?*
- Microsoft Entra ID access tokens (OAuth 2.0 Client Credentials or Workload Identity)
- Azure Managed Identities
- AKS Workload Identity (federated OIDC tokens)
- Mutual TLS (mTLS) with X.509 client certificates
- Service mesh workload identities (Istio, Linkerd)
- SPIFFE IDs issued by SPIRE
- Custom signed JSON Web Tokens (JWTs)
- Static shared secrets or API keys

### 3. Authorization
*Is Service A permitted to execute the requested operation?*
- Entra App Roles and application permissions
- OAuth 2.0 scopes (`scp` / `roles`)
- Service mesh L7 authorization policies (`AuthorizationPolicy` in Istio)
- Application-level business rules
- Database roles and permissions (`db_datareader`, `db_datawriter`)
- Domain-level access control lists (ACLs)

### 4. Transport Protection
*Is the wire traffic encrypted and tamper-proof?*
- One-way TLS (server authenticated)
- Mutual TLS (client and server authenticated)
- Private network encapsulation combined with TLS
- Transparent service mesh mTLS sidecars or ambient proxies

### 5. Credential Management
*How are credentials minted, distributed, refreshed, revoked, and audited?*
- Ephemeral, projected service account tokens (Kubernetes Bound Service Account Tokens)
- Automated cloud OIDC federation
- Short-lived X.509 certs issued by an automated PKI control plane
- Centralized secret stores (Azure Key Vault)

Network isolation without cryptographic identity leaves internal networks vulnerable once a boundary is crossed. Identity without network filtering leaves sensitive endpoints exposed to scanning and denial-of-service. These layers must compose together.

---

## Core Mental Model

```text
Kubernetes Service or routing
    tells Service A where Service B is located

Network policy or firewall
    determines whether Service A can send packets to Service B

OAuth token, mTLS certificate, or Workload Identity
    proves cryptographically that Service A is Service A

Authorization policy
    determines whether Service A is allowed to invoke the operation

Application logic
    determines whether the operation is valid for this specific resource instance
```

Sharing a private network or cluster does not imply shared trust.

---

# Kubernetes NetworkPolicy

## What It Does

`NetworkPolicy` is an L3/L4 packet filter enforced inside the Kubernetes cluster by the Container Network Interface (CNI) plugin (e.g., Cilium, Calico, Azure CNI with Network Policy).

A robust baseline relies on a default-deny ingress/egress posture combined with explicit allow rules:

```text
default deny all pod ingress/egress
+
explicit allow rules based on pod selectors
```

For instance:

```text
orders-api may connect to inventory-api:8080
reporting-api is dropped when attempting to connect to inventory-api
```

Policies select traffic targets using:
- Namespaces (`namespaceSelector`)
- Pod labels (`podSelector`)
- Transport protocols (`TCP`, `UDP`)
- Destination and source ports
- CIDR blocks (for external IP egress)

## Advantages
- Declarative YAML manifests managed via GitOps.
- Operates entirely at the network layer; applications need no custom code or SDKs.
- Negligible runtime latency overhead.
- Excellent containment of lateral movement if a pod is compromised.
- High visibility of allowed network topologies directly in source control.
- Requires no secret distribution or certificate tracking.

## Disadvantages
- Purely an L3/L4 control; provides no cryptographic identity or caller provenance.
- Service B cannot verify that an incoming connection actually originates from Service A (IP spoofing within a shared kernel or node bridge is theoretically possible if the CNI does not strictly enforce eBPF/iptables rules).
- Does not encrypt payload bytes on the wire.
- Cannot inspect HTTP verbs, REST paths, or gRPC methods.
- Operates only within a single cluster boundary; does not extend cleanly across clouds or to external VMs.
- Entirely dependent on the underlying CNI; if the cluster runs a basic CNI without policy support (like standard kubenet without a policy engine), manifests are ignored silently.
- Label drift: if an engineer mistypes or reuses labels, network rules can inadvertently open or break.

## Best Fit
Use `NetworkPolicy` as the mandatory foundation for all in-cluster network traffic. It is best suited for:
- Dropping unauthorized cross-namespace pod traffic.
- Restricting egress to external databases and third-party endpoints.
- Isolating sensitive operational domains (e.g., payment processing namespaces).

It is a reachability filter, not an authentication system. It should never be the sole gatekeeper for privileged business operations.

---

# Service Mesh and mTLS

## What It Does

A service mesh (such as Istio, Linkerd, or Consul Connect) deploys an L7 data plane (sidecar proxies or ambient node-level proxies) alongside applications, coordinated by a central control plane.

The mesh provides:
- **Workload Identity**: Injects a cryptographically verifiable identity into every pod, typically tied to its Kubernetes Service Account.
- **Mutual TLS (mTLS)**: Enforces end-to-end wire encryption and mutual authentication between pods using short-lived X.509 certificates.
- **Automated Certificate Rotation**: Issues and rotates certificates on an hourly or daily cadence without restarting applications.
- **L7 Authorization**: Evaluates policies based on cryptographic identity, HTTP paths, verbs, and gRPC methods.
- **Traffic Routing & Telemetry**: Collects detailed latency metrics, tracing context, and enforces retries and circuit breaking.

In an Istio mesh, a pod's identity is formatted as a SPIFFE ID derived from its Service Account:

```text
spiffe://cluster.local/ns/orders/sa/orders-api
```

An `AuthorizationPolicy` can then enforce:

```text
Workload 'spiffe://cluster.local/ns/orders/sa/orders-api'
may execute 'POST /reservations'
against workload 'inventory-api'
```

## Advantages
- Strong cryptographic authentication backed by mutual public-key cryptography.
- Wire encryption is transparent; application code remains agnostic to TLS certificates.
- No bearer tokens are handled by application code, eliminating the risk of token leakage in application logs.
- Credentials have short lifespans and rotate automatically.
- Policies evaluate caller identity rather than unstable pod IP addresses.
- Granular L7 authorization (e.g., allow `GET`, deny `DELETE`).
- Uniform telemetry, metrics, and distributed tracing injection across languages.
- Can federate identities across multi-cluster Kubernetes topologies.

## Disadvantages
- High operational and cognitive overhead.
- Increased resource consumption (CPU and memory overhead from sidecars or node proxies).
- Adds latency (typically 1–3 ms per hop due to proxy interception and TLS handshakes).
- Networking debugging becomes noticeably harder (tracing issues through iptables redirection, Envoy configs, and listener states).
- Complex upgrades; mesh control plane version transitions require careful operational handling.
- Does not replace domain-level business authorization (e.g., checking if the caller owns resource ID `1234`).
- Overkill for small platforms with only a handful of microservices.

## Best Fit
Adopt a service mesh when:
- Kubernetes is the primary runtime platform across the organization.
- Dozens or hundreds of microservices are managed by disparate engineering teams.
- Strict regulatory compliance mandates wire encryption and mutual identity everywhere.
- You need uniform traffic policies, automated retries, and mutual identity across multiple Kubernetes clusters without writing platform code inside every service.

---

# SPIFFE and SPIRE

## What They Do

The **Secure Production Identity Framework for Everyone (SPIFFE)** provides a standardized specification for workload identity in heterogeneous, dynamic environments. 

A workload is assigned a uniform SPIFFE ID:

```text
spiffe://company.internal/orders/orders-api
```

**SPIRE (SPIFFE Runtime Engine)** is the reference implementation that runs on nodes as an agent, interacting with a central SPIRE Server:
- **SPIFFE Workload API**: A local Unix domain socket exposed to pods or VM processes. Applications (or local proxies like Envoy) query this socket to retrieve identities without static secrets.
- **SVIDs (SPIFFE Verifiable Identity Documents)**: Short-lived X.509 certificates or signed JWTs minted dynamically.
- **Trust Bundles**: Automated distribution and rotation of root public keys across disparate platforms.

SPIFFE works identically across bare-metal servers, virtual machines, cloud instances, and Kubernetes clusters.

## Advantages
- Fully cloud-neutral and open standard (CNCF graduated).
- Eliminates hardcoded API keys, client secrets, and bootstrap passwords across any platform.
- Unifies identity across hybrid infrastructure: a process running on an on-premise Linux VM can authenticate to an AKS pod using the same cryptographic semantics.
- Supports trust domain federation: separate business units or clouds can establish cryptographic cross-trust without sharing central IAM directories.
- Strong protection against credential theft due to very short-lived SVID lifespans.

## Disadvantages
- You are running and maintaining core public key infrastructure.
- Requires deploying, securing, and monitoring SPIRE servers, back-end datastores, and node agents.
- SPIFFE solves authentication (who you are), but provides no built-in authorization engine; you must combine it with Open Policy Agent (OPA), Envoy RBAC, or application-level policy checks.
- Requires team expertise in PKI and trust-domain management.
- Applications must either speak to the SPIFFE Workload API via an SDK or run behind an Envoy sidecar.

## Best Fit
SPIFFE/SPIRE is the gold standard when:
- Workloads run across multiple cloud providers (e.g., AWS and Azure) and on-premise data centers.
- Applications run across both virtual machines and Kubernetes clusters and require a single, uniform identity framework.
- The platform team has the operational maturity to manage distributed PKI infrastructure.

---

# Microsoft Entra OAuth for S2S

## How It Works

Microsoft Entra ID (formerly Azure AD) supports the standard OAuth 2.0 Client Credentials Grant (`client_credentials`) and federated token exchanges for machine-to-machine interactions.

```text
+---------------+             +-------------------+             +---------------+
|               |  1. Request |                   |             |               |
|               |  Token      |  Microsoft Entra  |             |               |
|               | ----------->|        ID         |             |               |
|               |  2. JWT     |                   |             |               |
|  Service A    | <-----------|                   |             |  Service B    |
| (Caller App)  |             +-------------------+             | (Target API)  |
|               |                                               |               |
|               |  3. Call with Bearer Token (aud: Service B)   |               |
|               | --------------------------------------------> |  Validates:   |
|               |                                               |  - Signature  |
+---------------+                                               |  - Expiration |
                                                                |  - Audience   |
                                                                |  - Roles/App  |
                                                                +---------------+
```

1. Service B registers an Application in Entra ID, defining App Roles (e.g., `Orders.Read`, `Orders.Write`) and exposing an Application ID URI (its target audience).
2. Service A requests a token from Entra ID scoped specifically to Service B (`resource` / `scope = api://service-b/.default`).
3. Service A attaches the returned JWT in the HTTP request header:
   ```http
   Authorization: Bearer <access-token>
   ```
4. Service B validates the token:
   - Verifies the signature against Entra ID’s public JSON Web Key Set (JWKS).
   - Validates the `iss` (issuer) claim matches your tenant.
   - Validates the `aud` (audience) claim matches Service B's client ID or URI.
   - Validates the `exp` (expiration) timestamp.
   - Checks the `roles` or `appid` claims to determine whether Service A has permission to invoke the endpoint.

Because Service B caches Entra ID's public signing keys, **token validation happens locally in-memory**. Service B does not call Entra ID on every request.

## Advantages
- Industry standard OAuth 2.0 and JWT architecture.
- Tokens are audience-restricted: a token minted for Service B cannot be forwarded and replayed against Service C or an Azure SQL database.
- Granular permission modeling through Entra App Roles assigned via infrastructure code.
- Native integration across Azure: works smoothly across AKS, App Service, Functions, and VMs.
- Eliminates custom token-minting infrastructure; Microsoft manages key rotation, signing security, and high availability.
- Clear audit logging in Entra sign-in and audit logs.

## Disadvantages
- Tight coupling to Microsoft Entra ID.
- Application registration and app role assignments must be provisioned and managed via Terraform, Bicep, or scripts.
- Client applications must implement robust token acquisition and in-memory caching logic (typically handled via MSAL or the Azure SDK).
- Relies on an external Identity Provider: if Entra ID token issuance experiences downtime, workloads cannot mint new tokens once local caches expire.
- Does not encrypt wire traffic; must be layered on top of HTTPS or TLS.

## Best Fit
Entra OAuth is the primary choice when:
- Systems run predominantly within Microsoft Azure.
- Services communicate across disparate compute models (e.g., an AKS pod calling an App Service or an Azure VM).
- Services cross cluster boundaries and require standard, auditable application permissions.

---

# Managed Identity

## What It Is

Azure Managed Identity removes the operational burden of managing and rotating service credentials when communicating with Entra-protected resources. 

Instead of configuring applications with static secrets:
```text
client_id = "00000000-0000-0000-0000-000000000000"
client_secret = "mY_sUpEr_sEcReT_kEy~"  <-- DANGEROUS: Leaks in logs, env vars, git
```

The application calls an Azure-provided local endpoint to retrieve short-lived access tokens dynamically. The underlying infrastructure handles the credential lifecycle automatically.

Managed Identity works across the entire Azure ecosystem:
- Azure SQL and Azure Database for PostgreSQL
- Azure Key Vault
- Azure Storage (Blob, Queues)
- Azure Service Bus
- Custom internal APIs protected by Entra ID

## System-Assigned Identity
A system-assigned identity is tied directly to the lifecycle of a single Azure resource (e.g., an App Service instance or a VM).
- Created automatically with the resource.
- Shared with no other Azure resources.
- Automatically deleted when the Azure resource is deleted.
- Ideal for dedicated services that do not share access profiles with other workloads.

## User-Assigned Identity
A user-assigned identity is created as a standalone Azure resource with its own lifecycle.
- Created independently and assigned to one or more Azure resources.
- Survives the deletion or redeployment of the underlying compute hosts.
- Ideal for auto-scaling pools, multi-pod Kubernetes environments, and scenarios where multiple microservices share identical access policies.

## Advantages
- Zero secrets to store, rotate, or leak in source control.
- Credentials rotate transparently behind the scenes.
- Standard integration across modern runtime environments via `Azure.Identity` (`DefaultAzureCredential`).
- Unified role-based access control (Azure RBAC) across storage, messaging, and databases.
- Centralized visibility into identity permissions inside the Azure portal and Resource Graph.

## Disadvantages
- Locked to the Azure ecosystem.
- Azure RBAC assignments can proliferate rapidly without rigorous infrastructure-as-code discipline.
- Assigning a single user-assigned identity to multiple unrelated services creates a blast-radius risk (privilege creep).
- Local developer environments cannot run the Azure metadata service natively; developers must authenticate using Azure CLI, environment variables, or developer service principals.
- Internal database roles (such as SQL users and table grants) still require in-engine configuration.

---

# AKS Workload Identity

## How It Works

AKS Workload Identity bridges the gap between native Kubernetes workloads and Azure Managed Identity. It supersedes the deprecated Pod Identity model (which relied on intercepting node-level Azure Instance Metadata Service traffic with NMI/MIC daemons).

Workload Identity uses standard OpenID Connect (OIDC) federation:

```text
[ Kubernetes Pod ]
       |
       | 1. Mounts projected ServiceAccount token (OIDC JWT)
       v
[ Azure SDK (DefaultAzureCredential) ]
       |
       | 2. Sends projected token to Entra ID (Federated Credential exchange)
       v
[ Microsoft Entra ID ]
       |
       | 3. Validates token against AKS OIDC Issuer URL
       | 4. Confirms Subject matches: system:serviceaccount:<namespace>:<serviceaccount>
       v
[ Returns Access Token ]
       |
       | 5. Pod calls Azure SQL / Key Vault / Downstream API
       v
[ Downstream Azure Resource ]
```

The trust federation is established by configuring three attributes on the Azure Managed Identity:
- **Issuer**: The AKS cluster's public OIDC discovery endpoint (`https://<region>.oic.prod-aks.azure.com/...`).
- **Subject**: The Kubernetes Service Account identifier (`system:serviceaccount:<namespace>:<sa-name>`).
- **Audience**: `api://AzureADTokenExchange`.

## Kubernetes Configuration

First, define a dedicated `ServiceAccount` annotated with the Managed Identity's client ID:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: orders-api
  namespace: orders
  annotations:
    azure.workload.identity/client-id: "11111111-2222-3333-4444-555555555555"
```

Next, configure the `Deployment`. The Workload Identity mutating webhook inspects the pod, injects environment variables (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_FEDERATED_TOKEN_FILE`), and mounts the short-lived projected service account token:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orders-api
  namespace: orders
spec:
  replicas: 3
  selector:
    matchLabels:
      app: orders-api
  template:
    metadata:
      labels:
        app: orders-api
        azure.workload.identity/use: "true"
    spec:
      serviceAccountName: orders-api
      containers:
        - name: orders-api
          image: myregistry.azurecr.io/orders-api:2.1.0
          env:
            - name: DATABASE_URL
              value: "orders-db.database.windows.net"
```

## Important Responsibility Boundary

Maintain a strict separation between Kubernetes application manifests and cloud infrastructure definitions:

- **Kubernetes Manifests (Application Scope)**:
  Declare *which* identity the application runs as:
  - `ServiceAccount` definition
  - Workload identity annotations
  - Target endpoints (database hosts, queue URLs)

- **Terraform / Bicep (Platform Scope)**:
  Declare *what* permissions that identity holds:
  - Provisioning the User-Assigned Managed Identity
  - Configuring the federated identity credential linked to the cluster OIDC issuer
  - Azure RBAC assignments (e.g., `Key Vault Secrets User`, `Azure Service Bus Data Receiver`)
  - Target API App Role assignments

An application developer updating a `Deployment` YAML must not be able to elevate their cloud privileges simply by changing an annotation. If they point their `ServiceAccount` to an unauthorized identity, Entra ID rejects the federated token exchange because the AKS OIDC subject does not match the trust relationship.

## Advantages
- Completely eliminates static secrets and connection passwords inside Kubernetes pods.
- No privileged daemonsets intercepting node networking (unlike legacy AAD Pod Identity).
- Works cleanly with the official Azure SDKs via `DefaultAzureCredential`.
- Scales effectively across large clusters; token exchanges run over HTTPS to Entra ID without node-level bottlenecks.
- Fine-grained least privilege: every microservice receives its own isolated Azure identity.

## Disadvantages
- Requires configuring OIDC issuer federation on both AKS and Entra ID.
- Misconfigurations in namespace, service account name, or client ID manifest as runtime authentication exceptions that require inspecting federation logs to troubleshoot.
- Limited to targets that support Entra ID authentication.

---

# Passwordless Database Access

## What "Passwordless" Means

"Passwordless" does not mean connecting without parameters. The application still requires the database server address, database name, and encryption configuration.

What is eliminated are long-lived administrative passwords:
```text
// ELIMINATED:
User ID=dbadmin;Password=SuperSecretPassword123!;

// RETAINED (Configuration without secrets):
Server=tcp:orders-db.database.windows.net,1433;
Database=Orders;
Encrypt=True;
Authentication=Active Directory Default;
```

A more accurate term is **secretless connection configuration**.

## Authorization Layers

Enabling a Managed Identity on a pod does not grant it automatic access to the database tables. Authentication proves *who* the pod is; the database engine must still configure *what* it can do.

In Azure SQL, an administrator provisions an internal database user mapped directly to the Entra identity:

```sql
-- Run by DB Admin inside the target database:
CREATE USER [orders-api-identity] FROM EXTERNAL PROVIDER;

-- Grant least-privilege permissions:
ALTER ROLE db_datareader ADD MEMBER [orders-api-identity];
ALTER ROLE db_datawriter ADD MEMBER [orders-api-identity];
```

To complete defense-in-depth, configure network boundary controls:
- Enforce Azure Private Endpoints so database traffic stays on private subnets.
- Disable all public network access on the SQL Server resource.
- Restrict pod egress with Kubernetes `NetworkPolicy` to allow connections only to port 1433 on the SQL private endpoint IP.

## Operational Edge Case: Connection Pooling & Token Expiration
When using passwordless authentication with database connection poolers (e.g., ADO.NET, HikariCP for Java, or Npgsql for PostgreSQL), verify driver support for automated token refreshes. 

If a connection pooler initializes connections with an OAuth access token, those pooled physical TCP connections can fail or throw authentication exceptions when the initial token expires (usually after 60 minutes) unless the driver or connection pooler is configured to acquire fresh access tokens when recycling connections. Modern drivers (such as `Microsoft.Data.SqlClient` or updated `Npgsql` plugins) manage token lifecycles natively when using `Active Directory Default`.

## Advantages
- Eliminates database password rotation procedures in production.
- Prevents database credential leakage via config maps, environment variables, or application dumps.
- Enforces individual identities per application rather than a shared `sa` or `dbadmin` user.
- Database access can be revoked instantly in Entra ID without altering database schemas.

## Disadvantages
- Requires modern database drivers that support Entra token acquisition.
- Schema migration tools (Flyway, Liquibase, EF Core migrations) executed in CI/CD pipelines require their own federated identity or migration-specific credentials with DDL permissions.
- Database administrators must learn how to map external Entra providers to database principals.

---

# Custom JWT or Custom Security Token Service

## How It Works

Some large enterprises operate an internal Security Token Service (STS) to decouple workload authentication from public cloud providers.

Service A authenticates to the internal STS and requests a signed token for Service B:

```json
{
  "iss": "https://sts.company.internal",
  "aud": "inventory-api",
  "sub": "orders-api",
  "roles": ["inventory.reserve"],
  "exp": 1785980000,
  "iat": 1785976400
}
```

Service B validates the token signature against the internal STS public key set (JWKS endpoint).

## Advantages
- Complete independence from cloud vendor identity services.
- Full control over token claims, custom attributes, and token lifetimes.
- Uniform identity model spanning AWS, Azure, on-premise hardware, and legacy mainframes.

## Disadvantages
Operating a custom identity provider is a significant security responsibility. The platform team must handle:
- Workload credential verification
- Secure storage of private signing keys (typically requiring Hardware Security Modules / HSMs)
- Key rotation and JWKS distribution
- High availability (if the custom STS drops offline, all service-to-service communication fails)
- Revocation lists and token caching semantics
- Client SDK development, maintenance, and vulnerability patching

## Dangerous Antipattern: Shared Symmetric Secrets
Avoid designs where services share a symmetric secret to sign and verify tokens:

```text
// DANGEROUS:
Service A, B, and C all share: HMAC_SECRET = "super-secret-passphrase"
Service A signs its own token: jwt.sign({ sub: "orders-api" }, HMAC_SECRET)
```

If Service C is compromised, the attacker extracts the symmetric key and can mint arbitrary tokens impersonating any service, granting themselves administrative roles across the entire enterprise. 

**Always enforce asymmetric cryptography**: the identity provider holds the private key; consuming services receive only the public keys used for signature verification.

---

# Shared Secrets and API Keys

## How They Work

Service A includes a static, shared credential in every request:

```http
X-Api-Key: 9f82d8a4-5a21-4f8a-9e12-3b8c2d1e0f4a
```

Or passes HTTP Basic authentication headers, pre-shared connection strings, or static client certificates.

## Advantages
- Simple to implement; supported out of the box by virtually all frameworks.
- Minimal operational machinery required up front.
- Language and platform agnostic.

## Disadvantages
- **Credential Sprawl**: Static secrets often end up hardcoded in configuration files, Git repositories, CI/CD variables, and application logs.
- **Rotation Headaches**: Rotating a shared secret requires coordinating deployments between the caller and the receiver. Consequently, teams avoid rotating them for months or years.
- **Broad Blast Radius**: API keys are rarely bound to specific network locations or audiences; anyone who intercepts an API key can use it from any network location.
- **Weak Attribution**: Multiple instances of a service usually share one key, making detailed audit trails difficult.

## Best Fit
Use shared secrets only when integrating with legacy third-party systems that do not support modern token-based or PKI-based authentication. When secrets are unavoidable:
- Store them securely in Azure Key Vault.
- Mount them into applications dynamically using AKS Workload Identity and the Secrets Store CSI Driver, or fetch them via SDK.
- Establish an automated rotation schedule from day one.

---

# Scenario Implementations

## 1. Services Inside One Kubernetes Cluster

### Baseline Configuration
- Dedicated Kubernetes `ServiceAccount` per microservice.
- A default-deny `NetworkPolicy` across the namespace.
- Explicit allow rules for required pod-to-pod communication paths.
- Enforce TLS in application code where required.

```text
[ orders-api pod ] -- (L4 NetworkPolicy Allow) --> [ inventory-api pod:8080 ]
```

### High-Security Configuration
When hosting multi-tenant services, handling payment transactions, or working under strict compliance mandates:
- Add a service mesh (Istio) to enforce automatic mTLS and SPIFFE workload authentication.
- Write L7 authorization policies restricting methods and paths:

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

---

## 2. Communication Across Kubernetes Clusters

`NetworkPolicy` manifests cannot enforce rules across cluster boundaries; they apply only to local nodes managed by the cluster CNI.

```text
Cluster 1                                        Cluster 2
[ orders-api ] ---> [ Egress GW ] === Wire ===> [ Ingress GW ] ---> [ inventory-api ]
```

### Pattern A: Entra OAuth (Recommended for Azure Platforms)
- Service A acquires an Entra ID token scoped to Service B (`aud: api://inventory-api`).
- Traffic routes across a private VNet peering or VPN through an internal ingress controller.
- Service B validates the token signature and claims locally.
- *Advantage*: Works across disparate cloud hosting environments without configuring multi-cluster mesh peering.

### Pattern B: Multi-Cluster Service Mesh
- Federate mesh control planes (e.g., Istio Multi-Primary or Primary-Remote across networks).
- Trust roots are unified; pod identities are validated end-to-end via mTLS.
- *Trade-off*: High operational complexity; routing, DNS federation, and control-plane upgrades require ongoing platform maintenance.

---

## 3. AKS Calling Azure SQL

The recommended architecture relies on private routing and secretless credentials:

```text
[ AKS Pod (orders-api) ]
       |
       | 1. Workload Identity Token Exchange (OIDC)
       v
[ Microsoft Entra ID ]
       |
       | 2. Returns Access Token for "https://database.windows.net/"
       v
[ AKS Pod ] -- (Private Endpoint / TCP 1433) --> [ Azure SQL Server ]
                                                  - Validates Token with Entra
                                                  - Maps to [orders-api-identity]
                                                  - Applies db_datareader / db_datawriter
```

1. Deploy Azure SQL with public network access disabled.
2. Connect AKS to Azure SQL via an **Azure Private Endpoint** on the cluster VNet.
3. Apply a Kubernetes `NetworkPolicy` to restrict egress from `orders-api` pods to port 1433 on the database private endpoint IP.
4. Use AKS Workload Identity to obtain an Azure access token for the database connection.
5. Create an external provider user inside Azure SQL and assign least-privilege roles.

---

## 4. AKS Calling Azure Service Bus, Storage, or Key Vault

```text
[ AKS Pod ] 
    == AKS Workload Identity ==> [ DefaultAzureCredential ]
    == Token Request (Audience: Service Bus) ==> [ Microsoft Entra ID ]
    == Access Token ==> [ Service Bus Client SDK ]
    == Reads/Writes Messages ==> [ Azure Service Bus Namespace (Private Endpoint) ]
```

- Configure a User-Assigned Managed Identity federated to the pod's `ServiceAccount`.
- Assign specific Azure RBAC roles at the resource scope:
  - **Service Bus**: `Azure Service Bus Data Receiver` / `Sender`
  - **Storage**: `Storage Blob Data Contributor`
  - **Key Vault**: `Key Vault Secrets User`
- Route traffic through Azure Private Endpoints.
- Applications connect using the Azure SDK without storing secrets in Kubernetes manifests.

---

## 5. AKS Calling Azure App Service

```text
[ AKS Pod ]
    |
    | 1. Workload Identity requests token (aud: App Service Client ID)
    v
[ Microsoft Entra ID ]
    |
    | 2. Returns Entra JWT with App Roles
    v
[ AKS Pod ] --- HTTPS Bearer Token (VNet Integrated) ---> [ Azure App Service API ]
                                                            - Easy Auth / App Middleware
                                                            - Validates Signature & Roles
```

- Configure App Service with **VNet Integration** and Private Endpoints to ensure it is not exposed to the public internet.
- Secure the App Service using Entra ID authentication (either via built-in App Service Authentication / EasyAuth or custom application middleware).
- The AKS pod retrieves an Entra ID token using its Workload Identity, specifying the App Service's Application ID URI as the audience.
- The App Service validates the token and enforces authorization based on the claims.

---

## 6. AKS Calling an API on a Virtual Machine

### Pattern A: Entra OAuth (Azure Native)
- The VM runs an API configured to validate Entra ID JWTs (using ASP.NET Core JWT Bearer authentication, Spring Security, etc.).
- The AKS pod acquires a token scoped to the VM's application registration.
- Routing is secured over private VNets; network firewalls drop all unauthorized ports.

### Pattern B: SPIRE / Mutual TLS (Hybrid or Multi-Cloud)
- If the VM runs on-premise or in another cloud, deploy a SPIRE agent to the VM.
- Both the AKS pod and the VM obtain short-lived X.509 SVIDs from a unified SPIFFE trust domain.
- Mutual TLS is established directly between the pod and the VM service, validating client and server SANs.

---

## 7. Kubernetes Calling External SaaS Systems

When integrating with external third parties that do not support Microsoft Entra ID:

```text
Preferred Integration Hierarchy:
1. Workload Identity Federation (OIDC)   [Best: No secrets stored anywhere]
2. OAuth 2.0 Client Credentials Flow     [Good: Ephemeral tokens, client secret in Key Vault]
3. Client Certificate Authentication      [Acceptable: Cert stored in Key Vault, rotated via script]
4. Static Pre-Shared API Keys             [Fallback: Stored in Key Vault, mounted via CSI driver]
```

When static secrets are unavoidable:
- Store the secret in Azure Key Vault.
- Fetch the secret using AKS Workload Identity via the Azure SDK or the **Secrets Store CSI Driver**.
- Never commit secrets to Git, Helm values, or plain Kubernetes `Secret` resources without envelope encryption.
- Configure automated alerts for key expiration.

---

# User Context Is Separate from Service Identity

A common architectural error is conflating machine-to-machine authentication with end-user context:

```text
[ User Browser ] 
       |  Calls with User Token (User: Alice)
       v
[ Service A (Edge API) ]
       |  Calls Service B with... WHAT?
       v
[ Service B (Core Domain) ]
```

When Service A calls Service B, two distinct identities are at play:
1. **The Technical Caller (Machine Identity)**: Proves that Service A is authorized to talk to Service B.
2. **The Original Initiator (User Context)**: Indicates that user Alice requested the underlying business action.

### Antipattern: Forwarding the User's Browser Token
Forwarding the end-user's incoming browser token directly to internal downstream services introduces serious risks:
- The token's audience (`aud`) is typically configured for the edge API; downstream services should reject tokens that do not match their audience.
- If a downstream internal service is compromised, it can replay the user's high-privilege bearer token against unrelated systems.
- Asynchronous processes, batch jobs, and message queues break because user tokens expire quickly (typically within 60 minutes).

### Secure Pattern: Machine Identity with Context Headers
Service A uses its own identity (e.g., Workload Identity token or mTLS) to authenticate to Service B. It then propagates user and tenant context in standardized, tamper-evident metadata headers:

```http
POST /transfers HTTP/1.1
Host: payment-service.internal
Authorization: Bearer <Service-A-Machine-Token-Audience-PaymentService>
X-Correlation-ID: 7b3e6c1a-8f2d-4c3a-9e1b-2d4f6a8b0c2e
X-User-ID: usr_123456789
X-Tenant-ID: tnt_987654321
```

If Service B requires cryptographically verifiable proof of the user identity, use the **OAuth 2.0 On-Behalf-Of (OBO) Flow**. In this flow, Service A exchanges the incoming user token for a new token minted specifically for Service B, preserving user identity while strictly constraining the audience.

---

# Architecture Decision Matrix

| Scenario | Baseline Pattern | Preferred Production Architecture |
| :--- | :--- | :--- |
| **Pod to Pod (Single Cluster)** | Kubernetes `NetworkPolicy` (Default Deny) | Service Mesh mTLS with granular L7 `AuthorizationPolicy` |
| **Pod to Pod (Cross-Cluster)** | VNet Peering + L4 Firewall rules | Microsoft Entra OAuth (with Audience & App Roles) |
| **AKS to Azure SQL** | Static SQL User/Password in Key Vault | AKS Workload Identity + Azure SQL External User |
| **AKS to Azure Storage / Bus** | Shared Access Signatures (SAS) / Keys | AKS Workload Identity + Azure RBAC Assignments |
| **AKS to Azure App Service** | Pre-shared API Key in header | Private Endpoint + Entra OAuth Bearer Token |
| **AKS to VM in Azure** | Private Network NSG + Basic Auth | Private Endpoint + Entra OAuth Token Validation |
| **Hybrid (Kubernetes to On-Prem)**| VPN + Pre-shared Client Certificates | SPIFFE/SPIRE Federated Identity Infrastructure |
| **App Service to Azure SQL** | Connection string with username/password | System-Assigned Managed Identity + Azure SQL External User |
| **Kubernetes to External SaaS** | Static API Key in Kubernetes Secret | OIDC Federation (or Key Vault + Secrets Store CSI) |

---

# Red Flags & Antipatterns

Re-evaluate the architecture if any of the following patterns are present:

1. **Permissive Network Defaults**: Any pod in any namespace can open TCP connections to any other pod because no default-deny `NetworkPolicy` is enforced.
2. **Cluster-Wide Shared Identities**: All pods share a single cluster-level Managed Identity or Service Account, granting every microservice the combined permissions of the entire platform.
3. **Missing Audience Validation**: Service B validates only that an incoming JWT is signed by Entra ID, but neglects to check the `aud` claim. An attacker with a token for *any* internal API can reuse it against Service B.
4. **Shared Symmetric Keys**: Microservices share a single symmetric HMAC key to mint and verify their own tokens. Compromising one service compromises the whole fleet.
5. **Infrastructure Authority inside App Manifests**: Developers can grant arbitrary cloud permissions simply by editing a YAML manifest in their application repo, bypassing the platform team's infrastructure-as-code pipelines.
6. **Browser Token Forwarding**: Services blindly pass raw user identity tokens down deep internal microservice call chains without audience restriction or proper on-behalf-of delegation.
7. **Deploying a Service Mesh for Authentication Alone**: Adopting Istio solely for internal pod-to-pod identity when the team lacks the operational bandwidth to manage its proxies, control planes, and upgrade lifecycles.
8. **Static Connection Strings in Production**: Storing database passwords or storage access keys in config maps, environment variables, or Git repositories.

---

# Practical Rules for the Field

1. **Treat the cluster network as untrusted**. Pod IPs change constantly and provide zero proof of identity. Enforce default-deny `NetworkPolicy` rules as your starting baseline.
2. **Assign one dedicated Kubernetes Service Account to each workload**. Never run production application pods using the `default` service account.
3. **Prefer Managed Identity and AKS Workload Identity** for all communication with Azure resources. Decommission static passwords and API keys wherever native Entra ID support exists.
4. **Scope tokens to explicit audiences**. Every S2S token must contain an `aud` claim matching the receiving service. Service B must reject any token where `aud` does not match its own identifier.
5. **Validate tokens locally in-memory**. Service B must cache the identity provider's public signing keys (JWKS) to validate signatures locally without making an HTTP call to the IdP for every incoming request.
6. **Separate authentication from authorization**. Authenticating *who* the caller is does not mean they should have administrative access. Validate explicit scopes, app roles, or business rules on the target service.
7. **Keep infrastructure permissions out of application manifests**. Application YAML specifies *which* identity to use; Terraform or Bicep specifies *what* that identity can access.
8. **Adopt a service mesh only when the operational cost is justified**. If you are primarily on Azure and need S2S security across hybrid compute (AKS, App Service, VMs), Entra OAuth provides an identity model without the overhead of maintaining an L7 proxy mesh. Use a service mesh when you need transparent wire encryption, strict L7 policies, and uniform traffic telemetry inside Kubernetes.
9. **Use SPIFFE/SPIRE for multi-cloud and hybrid environments** where you must avoid lock-in to a single cloud provider's IAM and need a unified identity model across VMs, bare metal, and containers.
10. **Test authorization boundaries negatively**. Unit and integration tests must prove not only that allowed callers succeed, but that unauthorized callers and tokens with invalid audiences or missing roles are cleanly rejected with `401 Unauthorized` and `403 Forbidden`.

---

## Relationship to the Knowledge Graph

- **[[Service vs User Authorization Models]]**: Deep-dive into machine-to-machine authorization mechanics compared to user-delegated access patterns.
- **[[Service-to-Service Communication - How Service A Should Call Service B]]**: Applying workload identity to synchronous REST, gRPC, and asynchronous messaging architectures.
- **[[Propagating User Context Between Services]]**: Implementing OAuth 2.0 On-Behalf-Of exchanges and distributed context propagation across microservice chains.
- **[[Standardizing Service Infrastructure with Reusable Blocks]]**: Packaging workload identity SDKs, token caching, and certificate validation into standardized platform libraries.
- **[[User Context in Asynchronous Systems]]**: Managing caller identity, tenant isolation, and authorization state in detached message consumers and background workers.
