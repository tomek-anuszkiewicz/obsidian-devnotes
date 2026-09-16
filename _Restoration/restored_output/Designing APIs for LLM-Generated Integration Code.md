## Core Integration Flow

Coding agents must not construct raw HTTP requests. The agent discovers capabilities, selects typed clients, and generates calling code.

```text
Requirement -> Discover Client -> Select Method -> Generate Code -> Typed Client -> API
```

## Business Intent Over Generic CRUD

External APIs must expose stable domain capabilities. Never expose internal database schemas or internal mechanics. Express intent directly in endpoint names. Prefer `cancelInvoice` over `updateEntity`. 

For actual deletions, standard CRUD works:
```http
DELETE /drafts/{id}
```

For state transitions, use explicit action routes:
```http
POST /invoices/{id}/cancel
```

## OpenAPI Semantic Contracts

OpenAPI specs define runtime semantics, not just routes.

Weak spec:
```yaml
/users/{id}/sessions:
  delete:
    operationId: deleteSessions
```

Strong spec:
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

Add negative constraints to descriptions:
```yaml
description: |
  Permanently deletes a draft invoice.

  Only draft invoices can be deleted.

  Do not use this operation for issued invoices.
  Issued invoices must be cancelled using cancelInvoice.
```
Negative constraints stop agents from picking wrong endpoints.

## Strongly Typed Clients

Generate typed clients with Kiota, NSwag, or OpenAPI Generator. Typed clients eliminate route typos and JSON parse bugs.

Do not let agents generate manual HTTP requests:
```csharp
await httpClient.DeleteAsync(
    $"/users/{userId}/sessions");
```

Direct agents to call typed client methods:
```csharp
await identityClient.RevokeUserSessionsAsync(
    userId,
    cancellationToken);
```

## Preserve Documentation in Generated SDKs

Configure generators to emit OpenAPI descriptions as client docstrings. Docstrings put domain rules directly into the agent context window.

```csharp
public interface IInvoicesClient {
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

## Interface Discoverability

Name client interfaces by business domain, not infrastructure.
* Prefer: `IIdentityClient`, `IOrdersClient`, `IBillingClient`, `IInvoicesClient`
* Avoid: `IServiceAClient`, `IBackendClient`, `IApiV2Client`

Domain names let agents locate tools through repository search.

## Repository Guidance (`AGENTS.md`)

Add integration rules to `AGENTS.md`:
```text
When integrating with another service:
1. Search generated clients by business domain.
2. Inspect method names and docstrings.
3. Call generated clients instead of raw HTTP clients.
4. Read the OpenAPI schema only to resolve parameter ambiguity.
5. Never construct raw URLs manually.
```

## Semantic Errors

Return machine-readable errors with recovery hints. Avoid opaque numeric codes:
```json
{
  "errorCode": 3817
}
```

Provide semantic error payloads with recovery paths:
```json
{
  "code": "invoice_already_issued",
  "message": "Issued invoices cannot be deleted.",
  "suggestedOperation": "cancelInvoice"
}
```
Agents use `suggestedOperation` to trigger fallback calls automatically.

## Beyond REST

Apply these rules across all integration patterns.

### GraphQL
Write explicit mutation names and docstrings:
```graphql
"""
Cancels an issued invoice while preserving it for audit.
Do not use for draft invoices.
"""
cancelInvoice(id: ID!): Invoice!
```

### Messaging
Document message contracts with AsyncAPI. Distinguish commands from events by name:
* Command: `RevokeUserSessions`
* Event: `UserSessionsRevoked`

Commands execute tasks; events report state changes. Keep transport protocols below a typed, semantically named client interface.
