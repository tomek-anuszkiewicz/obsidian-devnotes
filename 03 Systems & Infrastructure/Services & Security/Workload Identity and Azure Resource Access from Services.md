---
title: "Workload Identity and Azure Resource Access from Services"
tags:
  - azure
  - workload-identity
  - authentication
  - authorization
  - kubernetes
aliases:
  - "Azure Service Workload Identity"
  - "AKS Identity and Resource Permissions"
  - "Managed Identity Across Service Boundaries"
---

An AKS service needs to query Azure SQL and send a message without keeping database passwords or long-lived cloud credentials in its deployment. It still needs an identity, an explicit trust relationship, network reachability, and permissions at each target. Removing a secret does not remove those responsibilities.

Kubernetes configuration identifies the workload. Azure configuration establishes federation and grants resource access. The target validates the credential and decides which operations are allowed. Keeping those changes separately owned prevents an application deployment from silently granting itself new privileges.

The mechanisms and deployment scenarios below connect that chain from caller to resource. [[Service-to-Service Authentication and Authorization in Azure and Kubernetes]] provides the wider choice of service-security models; [[Workload Trust and Network Security in Kubernetes]] explains the distinct network and certificate trust boundaries. User delegation remains a separate decision from proving the machine caller's identity.

## Microsoft Entra OAuth for S2S

### How It Works

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

### Advantages

- strong service identity,

- standard OAuth and JWT mechanisms,

- audience-restricted tokens,

- app roles and application permissions,

- works across clusters,

- works between AKS, App Service, VMs, and other hosts,

- central key rotation and token issuance,

- no need to maintain a custom token issuer,

- good auditability.

### Disadvantages

- requires Entra configuration,

- APIs and caller identities must be registered,

- app-role assignments require management,

- token acquisition and caching must be configured,

- routing and TLS are still separate concerns,

- introduces dependency on Entra for issuing new tokens,

- may feel administratively heavy for a very small internal system.

### Best Fit

Entra OAuth is a natural default when:

- the environment is strongly Azure-based,

- services run on different hosting platforms,

- services communicate across cluster boundaries,

- a consistent identity model is required for AKS, App Service, and VMs.

---

## Managed Identity

### What It Is

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

### System-Assigned Identity

A system-assigned identity belongs to the lifecycle of one Azure resource.

It is natural for:

- App Service,

- Azure Functions,

- VMs,

- other directly managed Azure resources.

Deleting the Azure resource deletes the identity.

### User-Assigned Identity

A user-assigned identity is an independent Azure resource.

It can be attached or federated to workloads.

This is commonly useful for AKS because Kubernetes pods are dynamic and are not themselves persistent Azure resources.

### Advantages

- removes long-lived client secrets,

- Azure manages the identity lifecycle and credentials,

- short-lived access tokens,

- good integration with Azure SDKs,

- centralized role assignment,

- one identity can access several Azure resource types,

- supports least-privilege permissions per workload.

### Disadvantages

- Azure-specific,

- role assignments can become difficult to inventory,

- accidental identity sharing can create excessive permissions,

- not all resources support Entra authentication,

- local development uses a different identity source,

- application and database permissions may require separate configuration.

---

## AKS Workload Identity

### How It Works

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

### Kubernetes Configuration

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

### Important Responsibility Boundary

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

### Advantages

- no client secret in Kubernetes,

- identity aligned with Kubernetes Service Accounts,

- separate identity per application,

- reusable for APIs, databases, queues, and storage,

- integrates with `DefaultAzureCredential`,

- works across pod restarts and replicas,

- suitable for fine-grained least privilege.

### Disadvantages

- requires federation configuration between AKS and Entra,

- debugging issuer, subject, and audience errors can be difficult,

- incorrect Service Account or annotation configuration causes runtime failures,

- Azure role assignment and resource-specific permissions are still required,

- remains tied to Entra and Azure-supported targets.

---

## Passwordless Database Access

### What “Passwordless” Means

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

### Authorization Layers

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

### Advantages

- no database password to distribute,

- no password rotation in Kubernetes,

- separate identity per service,

- centralized access revocation,

- short-lived credentials,

- improved least privilege and auditability.

### Disadvantages

- requires database and driver support,

- token refresh must work correctly with connection pooling,

- database migrations may use a different identity,

- CI/CD requires its own access model,

- diagnosing token and database-principal problems can be harder than checking a password,

- Azure RBAC does not always replace grants inside the database.

### Connection Pooling and Token Expiration

When using secretless authentication with database connection poolers (such as ADO.NET, HikariCP, or Npgsql), verify driver support for automated token refreshes.

If a connection pooler initializes physical TCP connections with an OAuth access token, those pooled connections can fail or throw authentication exceptions when the initial token expires (typically after 60 minutes) unless the driver or pooler actively retrieves fresh tokens when validating or opening connections. Modern drivers (such as `Microsoft.Data.SqlClient` or modern `Npgsql` plugins) manage token lifecycles natively when configured for Active Directory Default authentication.

---

## Scenario: AKS Workload Calling Azure SQL

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

## Scenario: AKS Calling Azure Service Bus, Storage, or Key Vault

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

## Scenario: AKS Calling App Service

### Preferred Azure Model

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

### Advantages

- same identity model across different hosting environments,

- no shared API key,

- caller identity and roles are visible,

- does not depend on a common Kubernetes cluster.

### Disadvantages

- API registration and role assignment are required,

- private routing requires additional Azure networking,

- token validation must be configured correctly.

---

## Scenario: AKS Calling a Service on a VM

### Entra OAuth

Appropriate when the VM and API are part of the Azure identity environment.

The VM-hosted API validates Entra JWTs.

Advantages:

- unified identity model,

- no custom issuer,

- application roles and audience.

Disadvantages:

- the VM application must configure token validation,

- TLS, routing, and firewalls remain the operator’s responsibility.

### mTLS or SPIFFE

Appropriate for hybrid or multi-cloud systems.

Advantages:

- strong workload identity,

- cloud-independent,

- encryption and authentication together.

Disadvantages:

- certificate and trust infrastructure,

- higher operational complexity.

### Custom JWT

Use only when a mature internal STS exists.

---

## Scenario: App Service or VM Calling Azure Resources

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

Choose the workload identity first, identify the audience and resource permissions separately, and verify the flow from the deployed caller. A successful token acquisition alone does not show that the network path or database grants are correct.

## Related Notes

- [[Service-to-Service Authentication and Authorization in Azure and Kubernetes]] — Comparing service identity, transport protection, authorization, and user delegation.
- [[Workload Trust and Network Security in Kubernetes]] — Network reachability and workload trust across Kubernetes boundaries.
- [[Remote Service Calls — Errors, Resilience, and Observability]] — Attaching authentication to an explicit communication pipeline.
