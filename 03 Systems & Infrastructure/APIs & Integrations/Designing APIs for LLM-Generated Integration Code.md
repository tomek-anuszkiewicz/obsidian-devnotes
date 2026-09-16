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
  - Shipping MCP Servers and Agent Skills Alongside APIs
  - Agent-Native Interface Bundles
---

When you use an LLM coding agent to build an integration, the goal is rarely for the model to hand-roll raw HTTP requests or guess endpoint paths. 

Instead, a well-structured system allows the agent to:
1. Understand the requested business operation,
2. Discover which external API capability provides it,
3. Locate the correct generated client in the codebase,
4. Select the appropriate client method, and
5. Write clean application code that uses that method correctly.

The workflow should look like this:

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
REST / GraphQL / Messaging API
```

If you leave an agent with an empty HTTP client and a raw endpoint, you force it to guess path parameters, serialization conventions, query string formatting, and header requirements. That dramatically widens the surface area for hallucinations. The job of the API designer is to collapse that action space.

---

## Internal vs. External APIs

When structuring systems for agent-driven development, the distinction between internal and external APIs becomes critical.

### Internal APIs
Internal APIs are typically tightly coupled to a specific service boundary:
- They reflect internal service architecture and storage schemas.
- They expose implementation-specific concepts.
- They rely on internal data representations and implicitly shared domain knowledge.
- They change frequently as the underlying service evolves.

### External APIs
External APIs, whether published to third parties or shared across distinct domain boundaries within an enterprise, require much tighter discipline:
- They must provide stable, versioned contracts.
- They avoid leaking internal storage or implementation mechanics.
- They expose business concepts rather than raw database mutations.
- They maintain backwards compatibility over time.
- They use domain terminology meaningful to consumers.

When an LLM writes integration code, this distinction is magnified. A human engineer might wade through internal slack channels or decode confusing variable names to figure out how a service works. An agent relies on the clarity of the contract. The more directly an operation maps to an identifiable business concept, the more reliably an agent will select and configure it.

---

## The Shift in API Consumption: What Services Need to Ship

Traditionally, API design focused on human developers reading Swagger UI or HTML documentation in a browser, then manually typing boilerplate integration code. In an environment where coding agents and LLM orchestration loops write and maintain integration logic, that assumption breaks down.

To make a service reliably consumable by an autonomous agent, the service interface should ideally publish a cohesive bundle of assets:

1. **A Formal Schema Contract**: OpenAPI 3.1 for REST, AsyncAPI for event-driven messaging, or an introspectable GraphQL schema.
2. **A Strongly Typed Client SDK**: Pre-generated client libraries (via Kiota, NSwag, or OpenAPI Generator) that expose compiler-validated methods.
3. **Runtime Tool Surfaces (MCP)**: If the agent needs to invoke the API dynamically during runtime execution, exposing a native Model Context Protocol (MCP) server lets the agent discover endpoints as discrete, structured tools with typed parameter schemas.
4. **Repository and Operational Guidance (`AGENTS.md` / `SKILL.md`)**: Concrete rules describing how to authenticate, handle token refreshes, manage pagination, and pass idempotency keys.
5. **Deterministic Sandbox Environments**: Mock servers or sandbox endpoints that provide immediate pass/fail feedback when the agent runs its verification test suite.

---

## OpenAPI as the Source of Truth

For REST APIs, an OpenAPI document must describe far more than paths, HTTP methods, and status codes. It needs to describe the *semantics* of the operations.

Consider a minimal specification:

```yaml
/users/{id}/sessions:
  delete:
    operationId: deleteSessions
```

This gives an agent almost nothing to go on. Is `id` a user ID or a session ID? Does it delete one session or all of them? Does it log the user out, or does it purge their history?

A much better specification provides clear semantic boundaries:

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

A good operation description answers several concrete questions:
- What does this operation do?
- When should it be used?
- When should it **not** be used?
- What preconditions must be met before calling it?
- What side effects does it trigger?
- What are the primary failure modes?

### Negative Guidance Prevents Semantic Collisions

LLMs are prone to superficial lexical matching. If a model sees the word "delete" or "remove" in a prompt, its first impulse is to find an endpoint with `DELETE` or `delete` in the name. Negative guidance explicitly breaks this tendency.

```yaml
/invoices/{id}:
  delete:
    operationId: deleteDraftInvoice
    summary: Permanently delete a draft invoice
    description: |
      Permanently deletes a draft invoice.

      Preconditions:
      - Only draft invoices can be deleted.

      Negative Guidance:
      - Do not use this operation for issued invoices.
      - Issued invoices are immutable legal documents and must be cancelled using cancelInvoice.
```

By explicitly stating what an operation *must not* be used for, you prevent the agent from mistaking invoice cancellation for draft deletion.

---

## Prefer Business-Oriented Operations Over Generic CRUD

Operations should express clear business intent.

Prefer domain-explicit operations:
```text
cancelInvoice
revokeUserSessions
reserveInventory
approveOrder
```

Avoid vague, generic mutations:
```text
updateEntity
executeAction
changeStatus
processRequest
```

CRUD operations are entirely appropriate when the underlying domain concept really is basic data storage:

```http
DELETE /drafts/{id}
```

If a draft is simply being removed from the database, `DELETE` makes sense. But an operation like cancelling an issued invoice involves auditing, balance adjustments, and lifecycle state changes. Representing that as an explicit action:

```http
POST /invoices/{id}/cancel
```

is vastly superior to treating cancellation as a generic entity update (`PATCH /invoices/{id}` with `{"status": "cancelled"}`) or pretending it is a deletion. 

Expose business capabilities, not merely database mutations.

---

## Generate Strongly Typed Clients

A coding agent working in an application codebase should rarely write raw HTTP transport logic.

Avoid having the agent generate code like this:

```csharp
await httpClient.DeleteAsync($"/users/{userId}/sessions");
```

Instead, steer the agent toward a strongly typed, generated client:

```csharp
await identityClient.RevokeUserSessionsAsync(
    userId,
    cancellationToken);
```

You can generate typed clients directly from OpenAPI specs using tools such as:
- Microsoft Kiota,
- NSwag,
- OpenAPI Generator.

```text
OpenAPI Spec
     ↓
Client Generator (Kiota, NSwag, etc.)
     ↓
Strongly Typed Client
     ↓
LLM-Generated Application Code
```

This collapses the agent's failure surface. The agent no longer has to deduce:
- The base URL and route structure,
- The HTTP method,
- The serialization format (JSON, form-encoded, protobuf),
- Request and response body schemas,
- Query parameter string formatting,
- Required headers.

Instead, the agent picks an existing, typed method signature. If it gets the method name or parameters wrong, the compiler or language server immediately flags the error, giving the agent a clean diagnostic error to fix during its verification loop.

---

## Preserve Documentation in Generated Clients

If your client generator strips out descriptions, summaries, and constraints, you throw away most of the value of your OpenAPI contract.

Client generators must be configured to emit docstrings or XML comments directly onto the generated interfaces and methods:

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

This is critical because of how coding agents interact with codebases. An agent rarely reads a 10,000-line `swagger.json` file in its entirety—doing so consumes massive amounts of context window and dilutes attention. 

Instead, the agent inspects local files, runs semantic code searches, and relies on Language Server Protocol (LSP) definitions. When the semantic rules, preconditions, and negative warnings live directly in the interface comments, the model sees them at the exact moment it inspects the method signature.

---

## Client Discoverability in the Codebase

Generating strong clients is only half the battle; the agent must also be able to find them when given a requirement.

Use domain-oriented client names:
```text
IIdentityClient
IOrdersClient
IBillingClient
IInvoicesClient
```

Avoid grouping clients by internal architecture, teams, or transport versions:
```text
IServiceAClient
IBackendClient
IApiV2Client
```

Similarly, ensure the method names mirror recognizable business tasks:
```text
RevokeUserSessionsAsync
CancelInvoiceAsync
ReserveInventoryAsync
```

This enables effective semantic searching across the repository:

```text
Requirement:
"When an employee is disabled, invalidate all login sessions."

        ↓ agent searches codebase for:
"session", "revoke session", "identity"

        ↓ finds:
IIdentityClient

        ↓ inspects methods:
RevokeUserSessionsAsync

        ↓ generates:
await identityClient.RevokeUserSessionsAsync(userId, cancellationToken);
```

When naming aligns with domain capabilities, the repository's type system serves as an accurate index for the agent.

---

## Repository Guidance for Agents (`AGENTS.md` / `SKILL.md`)

Do not assume the agent will automatically guess your architectural conventions. Provide explicit instructions in an `AGENTS.md`, a repository rulebook, or an agent skill definition.

A concise set of instructions looks like this:

```text
When integrating with an external service or internal microservice:

1. Search existing generated clients in `src/Clients/` by business concept.
2. Inspect the interface method signatures and XML/JSDoc comments.
3. Prefer generated clients over direct HTTP calls. Never use HttpClient directly if a generated client exists.
4. If an operation requires idempotency or specific retry semantics, check the method parameters before implementing manual headers.
5. If the correct operation or payload constraints are ambiguous, inspect the source OpenAPI specification in `specs/`.
6. Do not invent endpoint URLs or hand-craft REST requests when a typed client exists.
```

This guidance separates concerns cleanly:
- The **repository instructions** tell the agent *how to navigate, discover, and use* capabilities.
- The **OpenAPI contract** tells the agent *what capabilities exist and what their technical boundaries are*.

For complex flows (such as multi-step OAuth handshakes, cursor-based pagination loops, or handling distributed saga compensations), the repository instructions or skills should outline the standard operational workflow so the model does not have to invent one.

---

## OpenAPI Does Not Always Need to Be Read Directly

When client interfaces are well-named and carry complete docstrings, the coding agent rarely needs to read the raw OpenAPI spec for routine tasks.

The standard execution path remains lightweight:

```text
Business requirement
        ↓
Search generated clients
        ↓
Inspect documented methods
        ↓
Generate code
```

The raw OpenAPI contract remains the authoritative source of truth, but it serves as an escalation target. The agent only needs to parse the underlying YAML or JSON when it encounters complex edge cases:
- Parsing polymorphic response schemas,
- Checking detailed regex constraints on fields,
- Reviewing nuanced error response models,
- Inspecting lifecycle preconditions not fully surfaced by the client generator.

This establishes a clear hierarchy of detail:

```text
OpenAPI Contract (Authoritative Ground Truth)
        ↓
Generated Typed Client (Compiler Guardrails)
        ↓
Preserved Comments / Docstrings (In-Context Semantics)
        ↓
Coding Agent (Code Synthesis)
```

---

## Semantic Error Responses and Self-Healing Loops

Integration code inevitably fails during development and testing. When a call fails, the structure of the error payload determines whether an agent can fix the issue automatically or get stuck in a hallucination loop.

Opaque status codes and vague strings offer no path forward:

```json
{
  "errorCode": 3817
}
```

Or generic error blobs:

```json
{
  "error": "Conflict",
  "message": "Operation cannot be performed on entity in current state."
}
```

Instead, return structured, machine-actionable error payloads that explain the failure state and suggest a remediation path:

```json
{
  "code": "invoice_already_issued",
  "message": "Issued invoices cannot be deleted.",
  "status": 409,
  "suggestedOperation": "cancelInvoice",
  "documentationUrl": "https://api.domain.internal/errors/invoice_already_issued"
}
```

When an agent runs an integration test in its sandbox harness and encounters this error, the remediation is trivial. The agent parses `suggestedOperation: "cancelInvoice"`, locates `CancelInvoiceAsync` on its typed client, updates the calling code, and reruns the test suite—resolving the failure without human intervention.

---

## Applying the Principles Beyond REST

This contract-first, type-safe architecture applies directly to other communication protocols.

### GraphQL

In GraphQL, schemas naturally provide type safety, but the same semantic rules apply:
- Provide comprehensive docstrings on schema types, queries, and mutations.
- Expose intent-revealing mutations rather than broad catch-all mutations.
- Generate typed clients using tools like GraphQL Code Generator to prevent malformed query strings.

```graphql
"""
Cancels an issued invoice while preserving it for audit.
Precondition: Invoice status must be 'Issued'.
Do not use for draft invoices (use deleteDraftInvoice instead).
"""
cancelInvoice(id: ID!): Invoice!
```

### Event-Driven Messaging and AsyncAPI

For asynchronous, message-driven architectures, rely on AsyncAPI alongside schema registries (Protobuf, Avro, JSON Schema).

Distinguish commands from events clearly in message names:
- `RevokeUserSessions`: A command sent to a specific service requesting state change.
- `UserSessionsRevoked`: A domain event emitted after the session invalidation has occurred.

AsyncAPI specifies:
- Message payloads and schema definitions,
- Channels and topic topologies,
- Message routing and header conventions,
- Delivery guarantees and serialization protocols.

From an AsyncAPI specification, you can generate strongly typed message publishers and consumers. The agent then simply invokes `publisher.PublishAsync(new RevokeUserSessions(...))` instead of manually constructing raw message broker envelopes, managing partition keys, or serializing raw byte arrays.

---

## Preferred Architecture

A maintainable integration architecture for LLM-generated code positions the typed client as the primary boundary:

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
          REST               GraphQL             Messaging
```

The agent should interact with a typed, semantically rich interface. All low-level transport details—HTTP verbs, route parameters, serialization, connection pooling, and message envelope packing—remain sealed inside the generated client layer.

---

## Core Principle

> External integrations should expose well-documented formal contracts, generate strongly typed clients from those contracts, and make those clients easy for coding agents to discover by business capability.

When an API is built this way, it serves as more than an endpoint catalog. It becomes an active part of the agent's semantic context, providing the model with the exact constraints it needs to determine:
- Which capabilities exist across the infrastructure,
- Which method fulfills the specific business requirement,
- How to invoke it with full compile-time safety, and
- Which operations must not be confused with one another.
