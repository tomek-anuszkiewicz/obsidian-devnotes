---
title: Evolving Service API Contracts Without Breaking Consumers
tags:
  - api-design
  - microservices
  - backward-compatibility
  - testing
  - distributed-systems
aliases:
  - Service API Backward Compatibility
  - API Contract Evolution
  - Schema and Semantic Compatibility
  - Compatibility Testing Across Service Releases
---

Service B adds `suspended` to a customer-status response. The JSON field is still a string, but an older generated client might reject the new value, and an older consumer might assume that every status other than `inactive` permits ordering. A small provider change can therefore break a consumer without removing an endpoint.

B owns the public API contract. Each consumer owns the business behavior that depends on it and can remain deployed on a different release. Compatibility has to preserve both the shape of exchanged data and the meaning consumers rely on.

This applies to handwritten adapters, generated clients, shared DTO packages, and official SDKs. A shared package gives consumers a compile-time view; it does not force every deployed process to update at once. [[Service-to-Service Communication — How Service A Should Call Service B]] explains those client and ownership choices.

## API Compatibility

Backward compatibility is required regardless of whether the client is:

- handwritten,

- generated,

- distributed as a NuGet,

- created locally,

- expressed through an RPC interface.

Service B must assume that consumers update at different times.

A deployed B may be called by:

- an old client,

- the current client,

- a future client during a rolling deployment.

The contract must tolerate version skew. Package versions and deployed API versions are separate facts. Record which released API contract and consumer behavior a candidate is checked against; comparing only the latest branches can miss an older consumer that is still receiving production traffic.

---

## Usually Safe Changes

Changes that are often backward compatible include:

- adding a new endpoint,

- adding an optional request field,

- adding an optional response field,

- adding a new error code when consumers handle unknown codes safely,

- adding a query parameter with a default behavior,

- adding metadata that old consumers ignore.

Even these changes should be tested because generated clients and strict serializers may behave differently.

---

## Common Breaking Changes

Typical breaking changes include:

- removing an endpoint,

- renaming a field,

- removing a field,

- changing a field type,

- making an optional field required,

- changing the meaning of `null`,

- changing status codes,

- changing error codes,

- changing enum behavior,

- changing authentication requirements,

- changing idempotency semantics,

- changing default sorting or filtering,

- changing retry-related behavior,

- changing the business meaning of an existing value.

A contract may remain structurally valid while becoming semantically incompatible.

For example:

```text
status = active
```

may previously mean:

```text
The customer may place an order.
```

Later it may mean:

```text
The customer record is not archived.
```

The JSON still deserializes, but the consumer behavior may become incorrect.

Backward compatibility must therefore cover both schema and meaning.

---

## Enum Compatibility

Enums are a frequent source of hidden breaking changes.

Suppose B initially returns:

```text
active
inactive
```

Later it adds:

```text
suspended
```

A generated .NET enum may fail deserialization or map the value incorrectly.

Safer approaches include:

- string-based values,

- an `Unknown` fallback,

- tolerant deserialization,

- explicit handling of unknown values.

Consumer code should avoid assuming that all possible values are permanently known.

Bad:

```csharp
return response.Status switch
{
    CustomerStatus.Active => true,
    CustomerStatus.Inactive => false
};
```

Better:

```csharp
return response.Status switch
{
    "active" => Eligibility.Allowed,
    "inactive" => Eligibility.Denied,
    _ => Eligibility.Unknown
};
```

The correct fallback depends on the business risk.

---

## Request Compatibility

Adding a required request field is normally breaking.

Instead, B should:

- add an optional field,

- define a default behavior,

- introduce a new endpoint or API version when semantics differ substantially.

Old consumers must still be able to send the previous request format.

B should avoid interpreting omitted fields differently without an explicit version change.

---

## Response Compatibility

Adding a response field is generally safe when consumers ignore unknown fields.

Removing or changing an existing field is breaking.

B should also avoid turning:

```json
"items": []
```

into:

```json
"items": null
```

unless the distinction was part of the original contract.

Changes in nullability frequently break generated clients even when handwritten clients continue to work.

---

## Error Compatibility

Error contracts are part of the public API.

Service B should maintain stable:

- status codes,

- machine-readable error codes,

- error categories,

- retryability semantics,

- correlation identifiers.

Changing:

```text
404 customer_not_found
```

to:

```text
400 invalid_customer
```

can break Service A even if the successful response contract is unchanged.

Human-readable messages should not be used as stable programmatic identifiers.

Bad:

```csharp
if (error.Message == "Customer was not found")
```

Better:

```csharp
if (error.Code == "customer_not_found")
```

---

## Versioning Strategies

### Compatible evolution

Prefer evolving the existing API through additive, backward-compatible changes.

This should be the default.

### Explicit API versioning

Use a new version when:

- semantics change significantly,

- old behavior cannot be preserved,

- the contract requires structural redesign,

- migration requires a transition period.

Examples:

```text
/api/v1/customers
/api/v2/customers
```

or negotiated media types.

### Parallel support

During migration, B may support both versions.

A consumers migrate independently.

B removes the old version only after:

- usage is known,

- consumers have migrated,

- a deprecation period has passed,

- production traffic confirms no remaining users.

Versioning does not replace backward compatibility discipline. Creating a new API version for every small change creates long-term maintenance overhead.

---

## Source of Truth

There should be one primary source of truth for the public contract.

Possible choices include:

- OpenAPI specification generated from B,

- contract-first OpenAPI maintained separately,

- protocol schema such as Protobuf,

- another machine-readable IDL.

Avoid maintaining several independent manual definitions:

```text
ServiceB.Contracts.dll
openapi.json
ServiceB.Client.dll
documentation
```

They can drift apart.

A better pipeline is:

```text
Source of truth: OpenAPI

Generated artifacts:
- .NET client
- TypeScript client
- API documentation
- compatibility report
```

The generated artifacts should not become competing contract definitions.

---

## Compatibility Testing

Compatibility should be automated.

### Schema compatibility tests

Service B compares the new API specification with the previous released version.

The pipeline should detect:

- removed endpoints,

- removed properties,

- changed types,

- changed required fields,

- incompatible enum changes,

- changed response codes.

Automated schema comparison tools such as `openapi-diff` can detect structural changes against the released contract used as the baseline. Consumer-driven contract tests, for example with Pact, exercise published consumer expectations. Neither proves that every business meaning is unchanged; semantic changes also need relevant behavioral tests and explicit review.

### Consumer-driven contract tests

Service A defines the subset of B behavior it depends on. A may deserialize only the fields it uses, but those fields, their nullability, their meaning, and the outcomes it handles still form a dependency. Consumer expectations should describe that dependency rather than copying B's entire internal model.

For example:

```text
A requires:
- GET /customers/{id}
- response fields: id, status
- 404 with code customer_not_found
- unknown status values must be possible
```

Service B validates those expectations before release.

This is especially useful when A uses only a small portion of a large API.

### Integration tests

Service A runs its adapter against:

- a real test instance of B,

- a compatible stub,

- or a contract test environment.

The test should validate:

- authentication,

- serialization,

- status codes,

- timeout behavior,

- trace propagation,

- error interpretation.

### Production or staging smoke tests

After deployment, verify:

- A can reach B,

- authentication works,

- telemetry is emitted,

- required endpoints behave correctly,

- the deployed API matches the expected contract.

---

## Keep Compatibility Evidence Tied to the Release

A schema report, provider check, adapter integration test, and deployment smoke test answer different questions. A schema comparison cannot establish that `active` still has the same business meaning. A test double cannot establish that production credentials or routing work. A passing current-client test cannot establish that an older consumer still behaves correctly.

Identify the provider candidate, the relevant deployed contract versions, and the consumer expectations covered by the evidence. When a change intentionally breaks behavior, support migration and parallel operation explicitly instead of relying on every consumer to upgrade with the provider. Remove old behavior only after the supported consumers and observed usage justify it.

## Warning Signs

- client versions and deployed B versions are unclear,
- nobody knows whether a field or endpoint can be safely changed.

## Practical Rules

- Service B owns the public API contract.
- Use one machine-readable source of truth for the contract.
- Prefer additive, backward-compatible API evolution.
- Treat error behavior and semantics as part of compatibility.
- Test compatibility automatically.
- Depend only on the subset of B that A actually needs.

The release boundary is the public behavior B has committed to support. Generated artifacts can make that contract easier to consume, while independent consumer releases make compatibility checks and migration ownership necessary.

## Related Notes

- [[Service-to-Service Communication — How Service A Should Call Service B]] — SDK, generated-client, shared-contract, and local-adapter choices.
- [[Remote Service Calls — Errors, Resilience, and Observability]] — How errors, timeouts, retries, and telemetry behave in a running integration.
- [[Scaling a Modular Monolith with Local-or-Remote Module Execution]] — Keeping module contracts valid when execution crosses process boundaries.
