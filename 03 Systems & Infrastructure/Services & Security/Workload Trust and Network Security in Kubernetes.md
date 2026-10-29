---
title: "Workload Trust and Network Security in Kubernetes"
tags:
  - kubernetes
  - network-security
  - workload-identity
  - mtls
  - distributed-systems
aliases:
  - "Kubernetes Workload Trust"
  - "Service Mesh and SPIFFE Trust Boundaries"
  - "NetworkPolicy and Service Identity"
---

Two pods can reach each other through a Kubernetes Service while still lacking a trustworthy answer to who is calling or what that caller may do. Network routing, traffic admission, workload authentication, and application authorization have to be designed together.

A network policy can constrain connectivity. A mesh or workload identity system can add authenticated identities and transport protection. The receiving application still needs rules for the actions and resources it exposes. Moving to another cluster adds routing and trust decisions rather than automatically extending the guarantees of the first cluster.

The comparison below follows those responsibilities through NetworkPolicy, mTLS, SPIFFE/SPIRE, and single-cluster and multicluster scenarios. [[Service-to-Service Authentication and Authorization in Azure and Kubernetes]] retains the overall selection framework. [[Workload Identity and Azure Resource Access from Services]] develops the token and resource-access path when an Azure identity is part of the solution.

## Kubernetes NetworkPolicy

### What It Does

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

### Advantages

- declarative YAML configuration,

- no authentication code in the application,

- low runtime overhead,

- useful protection against lateral movement,

- good visibility of intended network flows,

- natural fit for Kubernetes,

- no application secrets required.

### Disadvantages

- mainly a network-level control,

- does not normally provide cryptographic workload identity,

- Service B may not know with certainty that the caller is A,

- does not automatically encrypt traffic,

- usually cannot express business operations,

- does not naturally work across cluster boundaries,

- depends on a CNI implementation that enforces the policies,

- labels and namespace structure become security-relevant.

### Best Fit

Use it as a baseline for traffic inside a Kubernetes cluster.

It is particularly useful for:

- reducing unnecessary pod-to-pod access,

- limiting database egress,

- separating namespaces or domains,

- protecting internal services from unrelated workloads.

It should not normally be the only protection for highly privileged APIs.

---

## Service Mesh and mTLS

### What It Does

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

### Advantages

- strong cryptographic workload identity,

- encrypted pod-to-pod traffic,

- no bearer tokens handled by application code,

- short-lived and automatically rotated credentials,

- policies based on workload identity rather than only IP,

- possible HTTP method and path authorization,

- common traffic telemetry,

- can support multiple clusters.

### Disadvantages

- significant DevOps complexity,

- additional proxies or ambient data-plane components,

- more difficult networking diagnostics,

- extra CPU, memory, and latency,

- control-plane and certificate-management responsibilities,

- interactions between Kubernetes networking and mesh routing,

- does not replace business-level authorization,

- can be disproportionate for a small system.

### Best Fit

Consider a mesh when:

- Kubernetes is the primary application platform,

- many teams share the platform,

- workloads require strong mutual identity,

- internal traffic must be encrypted,

- there are many service-to-service policies,

- a multi-cluster Kubernetes platform needs one identity model.

---

## SPIFFE and SPIRE

### What They Do

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

### Advantages

- cloud-neutral workload identity,

- strong cryptographic authentication,

- no long-lived application secrets,

- suitable for Kubernetes, VMs, and hybrid environments,

- supports multiple clusters and trust-domain federation,

- avoids tying workload identity to one cloud provider.

### Disadvantages

- the organization operates its own identity infrastructure,

- requires SPIRE servers, agents, registration, and trust management,

- authorization still needs a separate design,

- higher operational and conceptual complexity,

- fewer developers and operators may be familiar with it,

- integration may require proxies or application changes.

### Best Fit

SPIFFE/SPIRE is attractive when:

- the organization is multi-cloud,

- Kubernetes and VMs must share one workload identity model,

- cloud-provider independence is important,

- the organization can maintain an internal identity platform.

---

## Scenario: Services Inside One Kubernetes Cluster

### Minimal Practical Baseline

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

#### Benefits

- relatively simple,

- no identity infrastructure required for every request,

- useful reduction of lateral movement,

- easy to represent as YAML.

#### Limitations

- network policy alone does not provide strong caller identity,

- access is tied to network placement and selectors,

- difficult to extend directly outside the cluster.

### Stronger Model

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

### Azure-Consistent Model

Use Entra OAuth even between pods when one uniform identity model is desired across:

- AKS,

- multiple clusters,

- App Service,

- VMs.

This may be more configuration than necessary for simple internal communication, but it avoids changing the authentication model when a service later moves outside the cluster.

---

## Scenario: Communication Between Kubernetes Clusters

### NetworkPolicy Alone

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

### Available Models

#### Entra OAuth

Good when clusters run in Azure or services already use Entra.

Advantages:

- identity survives cluster boundaries,

- no shared mesh required,

- works with non-Kubernetes targets.

Disadvantages:

- network routing and TLS remain separate,

- every API must validate tokens,

- role assignments must be administered.

#### Multicluster Service Mesh

Good when Kubernetes is the dominant platform.

Advantages:

- common service discovery,

- workload identity,

- mTLS,

- routing and authorization policies.

Disadvantages:

- complex gateways, trust domains, routing, and operations,

- large failure and upgrade surface.

#### SPIFFE Federation

Good for multi-cloud and hybrid infrastructure.

Advantages:

- portable workload identity,

- supports Kubernetes and VMs,

- avoids cloud-provider lock-in.

Disadvantages:

- self-operated identity control plane,

- separate authorization design.

---

Evaluate the complete path: reachable endpoint, accepted workload identity, transport protection, and permitted application action. Introducing a mesh or identity issuer should make those responsibilities clearer and testable.

## Related Notes

- [[Service-to-Service Authentication and Authorization in Azure and Kubernetes]] — Choosing a service-security model and separating workload identity from user context.
- [[Workload Identity and Azure Resource Access from Services]] — Azure federation, token audiences, and resource grants.
- [[Service vs User Authorization Models]] — Deciding whether an operation authorizes the service, the user, or both.
