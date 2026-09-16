---
title: Designing APIs for LLM-Generated Integration Code
tags:
  - api-design
  - ai-agents
  - software-architecture
  - integration
  - developer-experience
  - documentation
aliases:
  - Agent-Friendly API Design
  - APIs for LLM Integrations
---

## Goal

When you bring an LLM coding agent into your codebase, your goal is rarely to have the model fire off arbitrary HTTP calls directly against a raw network endpoint. 

Instead, you want the agent to operate the same way a disciplined software engineer does:

1. Understand the incoming business requirement.
2. Discover which downstream service or capability owns that domain operation.
3. Locate the corresponding generated, strongly typed client in the repository.
4. Select the precise client method designed for that operation.
5. Author clean, maintainable application code that invokes that client correctly.

Here is the operational mental model:

```text
Business requirement
        ↓
Discover business capability
        ↓
Find appropriate client
        ↓
Find appropriate operation
        ↓
Generate application code
        ↓
Generated client
        ↓
REST API
```

By structuring the workflow this way, the agent avoids dealing with transport-level mechanics and focuses entirely on domain logic.

---

## Internal vs External APIs

To make this pattern work across a large architecture, you need to draw a clear line between internal and external APIs.

### Internal APIs

Internal APIs sit inside a tight service boundary. They:

- Reflect the internal topology and database schema of a specific service.
- Expose implementation-specific primitives and transient data models.
- Use internal representations that make sense only to the team maintaining them.
- Change rapidly, often without formal deprecation cycles.
- Rely heavily on tribal knowledge and shared assumptions baked into the service's private codebase.

### External APIs

External APIs cross team, domain, or organizational boundaries. They must:

- Expose stable, backwards-compatible contracts.
- Encapsulate internal persistence models and service mechanics completely.
- Expose explicit business capabilities rather than generic data mutations.
- Maintain compatibility over long lifecycles.
- Use ubiquitous, domain-driven terminology that external consumers understand.

This boundary is critical when working with LLM agents. An internal endpoint named `POST /service-b/v1/sync-state` gives an agent zero domain context, increasing the likelihood of hallucinations or improper usage. Conversely, an externalized, business-aligned contract gives the model an unambiguous target. The clearer the business intent behind an operation, the more reliably an agent will choose it.

---

## OpenAPI as the Source of Truth

For REST APIs, an OpenAPI specification must be more than a list of routes and JSON payloads; it needs to document the operational semantics of the system.

Take this weak specification:

```yaml
/users/{id}/sessions:
  delete:
    operationId: deleteSessions
```

From an agent's perspective, this endpoint could mean anything from "log out the current device" to "nuke the entire user profile." 

Compare that to an explicit specification:

```yaml
/users/{userId}/sessions:
  delete:
    operationId: revokeUserSessions
    summary: Revoke all active sessions for a user
    description: |
      Revokes all active authentication sessions belonging
      to the specified user.

      Use this operation when access for the user must be
      immediately invalidated.

      This operation does not delete the user account.
```

High-quality API descriptions should directly answer several key operational questions:

- What does this operation accomplish in the domain?
- Under what specific conditions should an engineer (or agent) use it?
- When should it **not** be used?
- What preconditions must be satisfied before calling it?
- What side effects does it trigger across the system?
- What are the explicit failure modes?

Negative guidance is especially effective when directing coding agents. Because models operate on probabilistic pattern matching, a word like "delete" can easily trigger an agent to call a destructive endpoint when a non-destructive state transition was required.

Explicitly ruling out incorrect paths prevents this failure mode:

```yaml
description: |
  Permanently deletes a draft invoice.

  Only draft invoices can be deleted.

  Do not use this operation for issued invoices.
  Issued invoices must be cancelled using cancelInvoice.
```

With this context in place, the agent will not mistake a hard delete for a business cancellation simply because both operations imply removing an item from a view.

---

## Prefer Business-Oriented Operations

APIs should expose domain intent rather than generic state manipulation.

Prefer explicit, domain-driven operations:

```text
cancelInvoice
revokeUserSessions
reserveInventory
approveOrder
```

Avoid vague, anemic abstractions:

```text
updateEntity
executeAction
changeStatus
processRequest
```

Standard CRUD operations are entirely appropriate when the underlying domain requirement is fundamentally CRUD. For instance, hard-deleting an uncommitted draft is genuinely a deletion:

```http
DELETE /drafts/{id}
```

However, business-critical transitions—such as cancelling an issued invoice—carry legal, audit, and domain ramifications. Modeling that lifecycle change as a basic deletion or a generic patch creates ambiguity:

```http
POST /invoices/{id}/cancel
```

The underlying architectural rule is straightforward:

> Expose business capabilities through your API, not naked database mutations.

When your API exposes business capabilities, coding agents can directly map user stories and acceptance criteria to concrete operations without having to reverse-engineer side effects.

---

## Generate Strongly Typed Clients

Coding agents should not be generating raw HTTP network calls.

Do not let an agent produce unstructured I/O like this:

```csharp
await httpClient.DeleteAsync(
    $"/users/{userId}/sessions");
```

Instead, guide the agent toward an interface backed by a strongly typed, generated client:

```csharp
await identityClient.RevokeUserSessionsAsync(
    userId,
    cancellationToken);
```

You can generate these clients directly from your OpenAPI specifications using established tooling:

- **Microsoft Kiota** for clean, lightweight, highly idiomatic SDKs.
- **NSwag** for deep .NET and TypeScript integration.
- **OpenAPI Generator** for broad, multi-language ecosystem support.

The pipeline looks like this:

```text
OpenAPI
   ↓
Client generator
   ↓
Strongly typed client
   ↓
LLM-generated application code
```

This drastically shrinks the failure surface for the agent. By relying on a generated client, the agent no longer has to hand-craft:

- URL paths and route parameter interpolations.
- HTTP verbs and status code expectations.
- Serialization and deserialization logic.
- Request and response body contracts.
- Query string formatting and encoding.

If the agent gets a method name or argument wrong, the local compiler or type-checker flags it instantly, allowing the agent to self-correct before the code ever runs.

---

## Preserve Documentation in Generated Clients

A common breakdown occurs when the client generation pipeline strips out API documentation. Your generator should be configured to preserve OpenAPI descriptions as native docstrings—such as C# XML documentation, TypeScript JSDoc, or Go godoc.

```csharp
public interface IInvoicesClient
{
    /// <summary>
    /// Cancels an issued invoice while preserving it for audit.
    /// Do not use for draft invoices.
    /// </summary>
    Task CancelInvoiceAsync(
        Guid id,
        CancellationToken cancellationToken);

    /// <summary>
    /// Permanently deletes a draft invoice.
    /// Issued invoices cannot be deleted.
    /// </summary>
    Task DeleteDraftInvoiceAsync(
        Guid id,
        CancellationToken cancellationToken);
}
```

This directly optimizes context window usage. Instead of forcing the agent to ingest a massive, multi-megabyte `openapi.json` file, the agent only needs to read the generated interface file. The semantic intent, preconditions, and negative constraints are located right alongside the method signatures.

---

## Client Discoverability

Generating clean clients is only half the battle; the agent still needs to find them within the project tree.

Name your client interfaces after their business domains:

```text
IIdentityClient
IOrdersClient
IBillingClient
IInvoicesClient
```

Avoid grouping by transport, version, or arbitrary service divisions:

```text
IServiceAClient
IBackendClient
IApiV2Client
```

Method names should similarly lead with explicit domain intent:

```text
RevokeUserSessionsAsync
CancelInvoiceAsync
ReserveInventoryAsync
```

This naming strategy allows coding agents to locate dependencies via fast codebase symbol searches or semantic indexing:

```text
Requirement:
"When an employee is disabled, invalidate all login sessions."

↓ Search repository for:
session
revoke session
identity

↓ Discovers interface:
IIdentityClient

↓ Inspects method signatures:
RevokeUserSessionsAsync

↓ Generates correct integration:
await identityClient.RevokeUserSessionsAsync(...)
```

The repository’s type system effectively becomes a self-describing directory of external capabilities.

---

## Repository Guidance for Agents

You should explicitly instruct the agent on how to approach third-party and inter-service integrations. 

Add these rules directly to your project's `AGENTS.md`, `.cursorrules`, or local system prompt:

```text
When integrating with another service:

1. Search existing generated clients by business concept.
2. Inspect method names and documentation.
3. Prefer generated clients over direct HTTP calls.
4. If the correct operation is unclear, inspect the source OpenAPI specification.
5. Do not invent endpoint URLs or construct REST requests manually when a generated client exists.
```

This separates operational responsibilities cleanly:

- The **repository instructions** tell the agent how to discover and navigate internal abstractions.
- The **OpenAPI specifications** define what capabilities actually exist and govern their operational limits.

---

## OpenAPI Does Not Always Need to Be Read Directly

When your generated clients are well-named and include full docstrings, an agent rarely needs to read the raw `swagger.json` or `openapi.yaml` during day-to-day coding tasks.

The default workflow runs quickly and consumes minimal context tokens:

```text
Business requirement
        ↓
Search generated clients
        ↓
Inspect documented methods
        ↓
Generate code
```

The raw OpenAPI file serves as the underlying contract of record. The agent only needs to open it when resolving deeper edge cases:

- Inspecting detailed error response structures.
- Checking validation rules on optional or deeply nested query parameters.
- Reviewing complex object state lifecycles.
- Resolving edge-case behaviors not fully captured by typed client interfaces.

This establishes a clear hierarchy of information:

```text
OpenAPI
   ↓
Generated typed client
   ↓
Generated documentation/comments
   ↓
Coding agent
```

---

## Error Responses Should Also Be Semantic

Downstream services must communicate failures using domain semantics rather than generic, opaque status payloads.

Avoid uninformative error models:

```json
{
  "errorCode": 3817
}
```

Design errors that explain the state of the resource and point toward resolution:

```json
{
  "code": "invoice_already_issued",
  "message": "Issued invoices cannot be deleted.",
  "suggestedOperation": "cancelInvoice"
}
```

Semantic errors provide immediate feedback to both human engineers and LLM agents executing within an automated test-and-repair loop. If an agent writes an integration test that hits this failure mode, the error payload provides the exact path forward: switch from `delete` to `cancelInvoice`.

---

## The Same Principle Applies Beyond REST

This approach is not limited to HTTP and OpenAPI. The same mechanical pattern applies to any modern integration style.

### GraphQL

With GraphQL, leverage schema documentation and strong typing:

- Write explicit field and mutation descriptions in the schema.
- Name queries and mutations around domain workflows rather than generic data fetching.
- Rely on schema introspection.
- Generate typed clients and hooks using tools like GraphQL Code Generator.

```graphql
"""
Cancels an issued invoice while preserving it for audit.
Do not use for draft invoices.
"""
cancelInvoice(id: ID!): Invoice!
```

### Messaging

For asynchronous, event-driven architectures, apply the same rigor using message contracts and AsyncAPI.

Maintain a strict naming distinction between commands and events:

- `RevokeUserSessions` is an imperative command instructing a service to perform an action.
- `UserSessionsRevoked` is an immutable domain event stating that the operation has finished.

AsyncAPI specifications should document:

- Message envelopes and JSON/Avro/Protobuf payload schemas.
- Target channels, topics, or exchanges.
- Publishing versus consumption boundaries.
- Protocol headers, routing keys, and correlation identifiers.
- Broader operational semantics and processing guarantees.

With this structure in place, an agent can discover the appropriate command publisher or event handler without guessing message formats or topic naming rules.

---

## Preferred Architecture

A resilient integration architecture for LLM-assisted development follows this layout:

```text
                       Business requirement
                                ↓
                           Coding agent
                                ↓
                 Discover business capability
                                ↓
                     Strongly typed interface
                                ↓
           ┌────────────────────┼────────────────────┐
           │                    │                    │
        OpenAPI             GraphQL              AsyncAPI
           │                    │                    │
         REST                GraphQL             Messaging
```

The abstraction exposed to the coding agent should almost always be a **typed, semantically named client interface**. Wire protocols, transport serialization, and raw network mechanics should remain encapsulated beneath that boundary.

---

## Core Principle

When designing systems for human and AI collaboration, anchor on this rule:

> External integrations must expose well-documented formal contracts, compile down into strongly typed clients, and make those clients easy to discover by business capability.

When you establish this pipeline, coding agents will consistently use your generated clients instead of attempting to assemble raw transport calls from scratch.

A well-structured API contract is no longer just a machine-readable protocol definition. It becomes an integral part of the semantic environment that informs the LLM:

- What capabilities the system actually supports.
- Which operation maps cleanly to the requested business requirement.
- How to invoke that operation with the compiler's backing.
- Which similar, yet conflicting, operations must be avoided.
