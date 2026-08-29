## Goal

When using an LLM coding agent, the goal is not necessarily for the agent to call an API directly.

Instead, the agent should be able to:

1. understand the requested business operation,
    
2. discover which external API capability provides it,
    
3. find the correct generated client,
    
4. choose the correct client method,
    
5. generate application code that uses that method correctly.
    

A useful mental model is:

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

## Internal vs External APIs

It is useful to distinguish between internal and external APIs.

### Internal APIs

Internal APIs may:

- reflect internal service architecture,
    
- expose implementation-specific concepts,
    
- use internal data representations,
    
- change relatively freely,
    
- depend on concepts already understood inside the system.
    

### External APIs

External APIs should:

- provide stable contracts,
    
- avoid leaking internal implementation details,
    
- expose business concepts rather than internal mechanics,
    
- remain compatible over time,
    
- use terminology meaningful to consumers.
    

This distinction becomes even more important for LLM-generated code.

The easier it is to understand the business meaning of an operation, the easier it is for an agent to select it correctly.

---

## OpenAPI as the Source of Truth

For REST APIs, OpenAPI should describe not only the HTTP contract, but also the semantics of the operation.

A weak specification:

```yaml
/users/{id}/sessions:
  delete:
    operationId: deleteSessions
```

A better specification:

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

The description should answer questions such as:

- What does this operation do?
    
- When should it be used?
    
- When should it not be used?
    
- What are the preconditions?
    
- What side effects does it have?
    
- What are the important failure modes?
    

Negative guidance can be especially useful.

For example:

```yaml
description: |
  Permanently deletes a draft invoice.

  Only draft invoices can be deleted.

  Do not use this operation for issued invoices.
  Issued invoices must be cancelled using cancelInvoice.
```

This helps the agent choose the correct business operation rather than matching only on words such as "delete".

---

## Prefer Business-Oriented Operations

Operations should clearly express intent.

Prefer:

```text
cancelInvoice
revokeUserSessions
reserveInventory
approveOrder
```

over vague operations such as:

```text
updateEntity
executeAction
changeStatus
processRequest
```

CRUD operations are perfectly fine when the business operation really is CRUD.

For example:

```http
DELETE /drafts/{id}
```

is appropriate if the object is actually deleted.

But a business operation such as cancelling an issued invoice should probably be represented explicitly:

```http
POST /invoices/{id}/cancel
```

rather than pretending that cancellation is equivalent to deletion.

The important principle is:

> The API should expose business capabilities, not merely database mutations.

---

## Generate Strongly Typed Clients

The coding agent should normally not construct HTTP requests manually.

Instead of generating:

```csharp
await httpClient.DeleteAsync(
    $"/users/{userId}/sessions");
```

prefer a generated typed client:

```csharp
await identityClient.RevokeUserSessionsAsync(
    userId,
    cancellationToken);
```

The client can be generated from OpenAPI using tools such as:

- Kiota,
    
- NSwag,
    
- OpenAPI Generator.
    

The flow becomes:

```text
OpenAPI
   ↓
Client generator
   ↓
Strongly typed client
   ↓
LLM-generated application code
```

This significantly reduces the space in which the agent can make mistakes.

It no longer needs to reconstruct:

- the URL,
    
- HTTP method,
    
- serialization format,
    
- request schema,
    
- response schema,
    
- query parameter names.
    

Instead, it chooses a typed method.

---

## Preserve Documentation in Generated Clients

Ideally, descriptions from OpenAPI should become XML documentation or equivalent comments in the generated client.

For example:

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

This is particularly useful for coding agents because the most relevant semantic information is available directly next to the methods they are expected to use.

If the generated client loses all API descriptions, much of the semantic value of OpenAPI is lost.

---

## Client Discoverability

Having good generated clients is not enough.

The agent must also be able to discover which client provides a given capability.

Prefer domain-oriented names:

```text
IIdentityClient
IOrdersClient
IBillingClient
IInvoicesClient
```

instead of implementation-oriented names:

```text
IServiceAClient
IBackendClient
IApiV2Client
```

Likewise, operation names should expose intent clearly:

```text
RevokeUserSessionsAsync
CancelInvoiceAsync
ReserveInventoryAsync
```

This allows a coding agent to search the repository by business concepts.

Example reasoning:

```text
Requirement:
"When an employee is disabled, invalidate all login sessions."

↓ search for:
session
revoke session
identity

↓ find:
IIdentityClient

↓ inspect methods:
RevokeUserSessionsAsync

↓ generate:
await identityClient.RevokeUserSessionsAsync(...)
```

The repository itself becomes a semantic index of available capabilities.

---

## Repository Guidance for Agents

The agent should be explicitly told how external integrations are organized.

For example, an `AGENTS.md`, repository instruction, or coding skill may contain:

```text
When integrating with another service:

1. Search existing generated clients by business concept.
2. Inspect method names and documentation.
3. Prefer generated clients over direct HTTP calls.
4. If the correct operation is unclear, inspect the source OpenAPI specification.
5. Do not invent endpoint URLs or construct REST requests manually when a generated client exists.
```

The instruction tells the agent **how to discover and use capabilities**.

The OpenAPI specification tells it **which capabilities exist and what they mean**.

These are different responsibilities.

---

## OpenAPI Does Not Always Need to Be Read Directly

If the generated client is well named and well documented, the coding agent may not need to inspect `swagger.json` for every task.

In the common case:

```text
Business requirement
        ↓
Search generated clients
        ↓
Inspect documented methods
        ↓
Generate code
```

OpenAPI remains the authoritative contract and can be consulted when additional details are needed.

For example:

- detailed error responses,
    
- optional parameters,
    
- lifecycle constraints,
    
- response schemas,
    
- operation semantics not fully exposed by the generated client.
    

Therefore, a useful hierarchy is:

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

Avoid responses such as:

```json
{
  "errorCode": 3817
}
```

Prefer errors that expose the state and possible resolution:

```json
{
  "code": "invoice_already_issued",
  "message": "Issued invoices cannot be deleted.",
  "suggestedOperation": "cancelInvoice"
}
```

This is useful both for generated application code and for an LLM trying to understand the intended workflow.

---

## The Same Principle Applies Beyond REST

The same architecture can be applied to other integration styles.

### GraphQL

Use:

- well-described schema fields,
    
- meaningful query and mutation names,
    
- introspection,
    
- generated typed GraphQL clients.
    

Example:

```graphql
"""
Cancels an issued invoice while preserving it for audit.
Do not use for draft invoices.
"""
cancelInvoice(id: ID!): Invoice!
```

### Messaging

Use message contracts plus AsyncAPI.

For example:

```text
RevokeUserSessions
```

should be clearly distinguishable from:

```text
UserSessionsRevoked
```

The first may be a command that application code sends.

The second is an event produced as a result of processing that command.

AsyncAPI can describe:

- messages,
    
- payload schemas,
    
- channels/topics,
    
- send/receive direction,
    
- headers,
    
- operation semantics.
    

A coding agent can then generate or discover the correct publisher abstraction.

---

## Preferred Architecture

A good integration architecture for LLM-generated code is:

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

The important abstraction presented to the coding agent should usually be a **typed, semantically named application client**.

Transport details should remain underneath it.

---

## Core Principle

A useful rule is:

> External integrations should expose well-documented formal contracts, generate strongly typed clients from those contracts, and make those clients easy for coding agents to discover by business capability.

The coding agent should prefer those generated clients over constructing transport-level calls directly.

A well-designed API therefore becomes more than a machine-readable protocol description.

It becomes part of the semantic environment from which the LLM can infer:

- what capabilities exist,
    
- which capability matches the requested business operation,
    
- how it should be called,
    
- and which operations must not be confused with one another.