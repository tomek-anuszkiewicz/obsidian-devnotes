## Context

In distributed systems, Service A may receive a request initiated by a user and then call Service B.

The full flow may look like:

```text
User U
→ Gateway
→ Service A
→ Service B
```

Service B may need to know:

- which service made the call,
    
- which user originally initiated the operation,
    
- which tenant the operation belongs to,
    
- which trace and correlation identifiers belong to the flow,
    
- whether the operation is authorized.
    

These concerns are related, but they are not the same.

A common mistake is to treat all of them as one generic request context.

A healthier model separates:

- service identity,
    
- user identity,
    
- authorization,
    
- audit context,
    
- trace context,
    
- business context.
    

---

## Core Principle

A useful responsibility model is:

> The calling service authenticates itself.  
> The user identifier is propagated as contextual metadata.  
> The service owning the resource decides how authorization should work.

In practical terms:

```text
userId tells Service B whose operation this is;

service identity tells Service B who is making the call;

authorization determines whether the operation is allowed.
```

These three concepts should not be treated as interchangeable.

---

## Do Not Forward Browser Cookies Between Services

Forwarding the original browser cookie from Service A to Service B is usually a poor general design.

Cookies may be:

- tied to a specific frontend domain,
    
- based on server-side session state,
    
- intended only for a gateway,
    
- broader than Service B requires,
    
- difficult to audit,
    
- incompatible with asynchronous processing,
    
- coupled to the current login mechanism.
    

Forwarding cookies also causes internal services to depend on how users authenticate at the system boundary.

A future change from:

```text
browser session
```

to:

```text
token-based authentication
```

may then require changes across many services.

Internal service communication should have its own explicit authentication and context-propagation mechanism.

---

## Do Not Blindly Forward the User Token

Forwarding the original user access token is not always appropriate either.

The token may:

- have the wrong audience,
    
- contain more permissions than Service B needs,
    
- expose unnecessary user claims,
    
- expire before asynchronous processing,
    
- appear in logs or dead-letter queues,
    
- allow Service B to act outside the intended operation.
    

A delegated token can be appropriate when Service B must independently authorize the user.

However, this should be an explicit delegation mechanism, not blind token forwarding.

The delegated token should ideally be:

- intended for Service B,
    
- limited in scope,
    
- short-lived,
    
- linked to the calling service,
    
- auditable.
    

When such delegation is not required, passing the user identifier may be sufficient.

---

## Propagating the User Identifier

Service A may pass a user identifier to Service B:

```http
X-Initiated-By-User-Id: user-123
```

or as part of an internal message context:

```json
{
  "initiatedByUserId": "user-123"
}
```

This can be useful for:

- audit logs,
    
- authorization lookup,
    
- incident analysis,
    
- tracing a business operation,
    
- determining ownership or tenant context.
    

However:

> A user identifier is not proof of identity and is not proof of authorization.

Service B must not trust an arbitrary `userId` from an unauthenticated caller.

---

## Authenticate the Calling Service Independently

Service B should verify the technical caller independently.

For example:

```text
Authenticated caller: Service A
Original initiator: User U
```

Possible service authentication mechanisms include:

- workload identity,
    
- mutual TLS,
    
- client credentials,
    
- signed service tokens,
    
- broker-level producer identity,
    
- a trusted service mesh.
    

Service B should know that the request genuinely came from Service A.

Only then may it decide whether Service A is allowed to provide user context.

A plain header such as:

```http
X-User-Id: user-123
```

should not be trusted when it can be supplied directly by an external caller.

The system boundary should remove, overwrite, or reject untrusted internal-context headers.

---

## Two Valid Authorization Models

There is no single correct authorization model for every service call.

The key question is:

> Which service owns the authorization rule?

---

## Model 1: Service B Authorizes Service A

In this model, Service A is authorized to perform the operation.

The user identifier is passed mainly for audit.

Example:

```text
Order Service
→ Inventory Service
```

Order Service has already checked whether the user may create the order.

Inventory Service only verifies:

```text
Order Service may reserve inventory.
```

It does not need to re-evaluate the user’s right to place an order.

The audit record may still contain:

```text
Technical actor: Order Service
Original initiator: User U
```

This model is useful when Service A owns the complete business use case and Service B provides an internal capability.

---

## Model 2: Service B Authorizes the User

In this model, Service B owns the protected resource or authorization rule.

Example:

```text
Portal Service
→ Document Service
```

Document Service owns the document and decides who may read or edit it.

Service A provides:

- its own authenticated service identity,
    
- the original user identifier,
    
- the target resource,
    
- tenant or other required context.
    

Service B independently evaluates:

```text
Can User U edit Document D?
```

For example:

```csharp
await authorizationService.AuthorizeAsync(
    userId,
    documentId,
    Permission.Edit,
    cancellationToken);
```

The authorization lookup may use:

- local permissions stored in B,
    
- a central authorization service,
    
- replicated role assignments,
    
- ownership relationships,
    
- tenant membership.
    

This model is useful when B is the authoritative owner of the resource and its access rules.

---

## Passing User ID Does Not Mean Impersonation

The preferred model is usually delegation, not impersonation.

### Impersonation

Service B behaves as though the user contacted it directly.

This may hide the fact that Service A made the technical call.

### Delegation

Service B understands:

```text
Service A is acting on behalf of User U.
```

This preserves both identities.

A good audit trail should be able to reconstruct:

```text
User U
→ Gateway
→ Service A
→ Service B
```

rather than recording only:

```text
User U called Service B.
```

The latter is incomplete and may be misleading.

---

## Audit Logging

Service B should normally log the technical actor and original initiator separately.

For example:

```json
{
  "callerService": "service-a",
  "initiatedByUserId": "user-123",
  "tenantId": "tenant-7",
  "operation": "document.update",
  "resourceId": "document-456",
  "authorizationDecision": "allowed",
  "traceId": "abc123"
}
```

Avoid recording only:

```json
{
  "userId": "user-123"
}
```

That makes it look as if the user called Service B directly.

A useful audit model is:

```text
Technical actor
Original initiator
Target resource
Requested operation
Authorization decision
Decision owner
Trace identifier
```

Sensitive identifiers should be logged according to privacy and retention rules.

---

## Trace Context Is Separate from User Context

Distributed tracing should use standard trace propagation.

For HTTP this normally includes:

```http
traceparent: ...
tracestate: ...
```

For messaging, trace context should be placed in standard message headers or attributes.

Trace context answers:

> Which technical operation does this call belong to?

User context answers:

> Who initiated the business operation?

They may travel together, but they are different contracts.

Similarly, a correlation or business operation identifier may be separate from the trace identifier:

```text
traceId        = technical execution chain
correlationId  = logical operation or request family
orderId        = business entity
userId         = original initiator
```

---

## Tenant Context

In multi-tenant systems, `tenantId` is often propagated together with `userId`.

This requires additional care.

Service B should not trust an arbitrary header:

```http
X-Tenant-Id: tenant-7
```

The tenant should be linked to a trusted identity or verified context.

For example:

- the tenant is present in a verified token,
    
- Service A is authenticated and authorized to propagate it,
    
- Service B verifies the user’s membership in the tenant,
    
- the context is cryptographically signed.
    

Otherwise, changing one header could result in cross-tenant access.

A strong rule is:

> Tenant context must be derived from or validated against a trusted identity.

---

## HTTP Context Propagation

For synchronous HTTP communication, Service A may send:

```text
Service authentication
User identifier
Tenant identifier
Trace context
Correlation identifier
Selected audit metadata
```

Example:

```http
Authorization: Bearer <service-token>
X-Initiated-By-User-Id: user-123
X-Tenant-Id: tenant-7
X-Correlation-Id: operation-456
traceparent: 00-...
```

The exact header names are less important than having:

- a defined contract,
    
- clear trust rules,
    
- validation,
    
- an explicit allowlist,
    
- consistent logging.
    

Do not copy every inbound header into the outbound request.

---

## Avoid Blind Header Propagation

A dangerous pattern is:

```text
copy all incoming headers
→ send them to every downstream service
```

This may propagate:

- cookies,
    
- tokens with the wrong audience,
    
- private user data,
    
- debug flags,
    
- routing headers,
    
- internal implementation details,
    
- attacker-supplied headers.
    

Instead, the platform should propagate only an allowlist such as:

```text
trace context
correlation ID
initiated-by user ID
tenant ID
approved audit fields
a delegated token intended for the target service
```

The context contract should be explicit and versioned.

---

## Context Propagation Through Queues

Asynchronous communication requires a different model.

A message may be processed:

- seconds later,
    
- hours later,
    
- after retries,
    
- by another region,
    
- after the original user token has expired.
    

Therefore, long-lived user tokens should generally not be placed in queue messages.

They may be:

- stored in the broker,
    
- copied into dead-letter queues,
    
- exposed to diagnostic tooling,
    
- invalid by the time processing begins,
    
- broader than the operation requires.
    

A queue message may instead include:

```json
{
  "messageType": "UpdateDocument",
  "documentId": "document-456",
  "context": {
    "producerService": "service-a",
    "initiatedByUserId": "user-123",
    "tenantId": "tenant-7",
    "correlationId": "operation-456"
  }
}
```

The consumer authenticates through its own service identity and verifies the message producer through the broker or message signature.

---

## Authorization Timing for Asynchronous Operations

For queued commands, it must be decided when authorization is evaluated.

### Authorization at acceptance time

Service A verifies the user and accepts the command.

It then publishes:

```text
The operation has been authorized and accepted.
```

The consumer trusts Service A’s decision.

This works when Service A owns the business use case and the message represents an accepted command.

### Authorization at execution time

The consumer re-checks current user permissions when the message is processed.

This may be necessary when:

- the consumer owns the resource,
    
- execution may happen much later,
    
- permissions may change,
    
- current authorization is required by policy.
    

In this case, the message may include:

```text
userId
tenantId
requested operation
resource ID
```

The consumer performs a fresh authorization lookup.

The system must deliberately decide whether permissions are evaluated:

```text
when the command is accepted
```

or:

```text
when the command is executed
```

These semantics should be documented because they may produce different business outcomes.

---

## Commands and Events

User context has different meaning for commands and events.

### Command

A command asks a specific consumer to perform an operation:

```text
ReserveInventory
UpdateDocument
GenerateInvoice
```

It may include:

- original initiator,
    
- accepting service,
    
- authorization metadata,
    
- tenant,
    
- correlation ID.
    

### Event

An event describes a fact that already occurred:

```text
OrderCreated
DocumentUpdated
InvoiceGenerated
```

Consumers usually do not need the user’s permission to accept the fact.

The event may still include audit information:

```text
Order was created by User U through Service A.
```

Putting an access token into an event is usually a warning sign.

---

## A Shared Context Contract

The platform may define an explicit context structure.

For example:

```csharp
public sealed record ExecutionContext(
    string CallerService,
    string? InitiatedByUserId,
    string? TenantId,
    string CorrelationId);
```

For richer audit requirements:

```csharp
public sealed record ActorContext(
    string TechnicalActor,
    string? OriginalUser,
    string? TenantId,
    string? DelegationChain);
```

The platform may provide:

- HTTP handlers that serialize the context,
    
- message middleware that adds it to headers,
    
- consumers that validate and restore it,
    
- log scopes,
    
- trace enrichment,
    
- standard authorization accessors.
    

The contract should remain small and intentional.

Avoid an untyped bag such as:

```csharp
Dictionary<string, object> Context
```

because it encourages uncontrolled propagation and undocumented dependencies.

---

## Automatic Context Extraction

Automatic extraction can be valuable.

For example, middleware may:

1. authenticate the calling service,
    
2. read trusted context headers,
    
3. validate required fields,
    
4. create an execution context,
    
5. add fields to the logging scope,
    
6. expose the context to authorization logic,
    
7. propagate selected values downstream.
    

This removes repetitive code from every service.

However, automatic propagation is safe only when:

- propagated fields are explicitly defined,
    
- untrusted client values are removed at the boundary,
    
- the calling service is authenticated,
    
- the context is not automatically treated as authorization,
    
- sensitive fields are not logged indiscriminately,
    
- downstream propagation uses an allowlist.
    

Automation should reduce boilerplate, not hide the security model.

---

## Avoid One Global Ambient Context

In .NET, request context is sometimes exposed through:

- `HttpContext`,
    
- static accessors,
    
- `AsyncLocal`,
    
- global `CurrentUser`,
    
- global `CurrentTenant`.
    

This can be convenient:

```csharp
CurrentUser.Id
CurrentTenant.Id
```

but it creates hidden dependencies.

Risks include:

- unclear input requirements,
    
- difficult unit testing,
    
- accidental propagation into background tasks,
    
- problems with parallel message processing,
    
- incorrect context lifetime,
    
- code that works only inside HTTP requests.
    

A shared context accessor may still be useful at infrastructure boundaries.

Business logic should preferably receive the values it actually requires through explicit arguments or explicit application abstractions.

For example:

```csharp
public Task UpdateDocumentAsync(
    DocumentId documentId,
    UserId initiatedBy,
    CancellationToken cancellationToken);
```

or through a narrow interface:

```csharp
public interface IOperationContext
{
    UserId? InitiatedBy { get; }
    TenantId? TenantId { get; }
}
```

The use of ambient context should be deliberate and limited.

---

## Who Owns What?

### Service A owns

- authentication of the original user at its boundary,
    
- the decision to call Service B,
    
- accurate propagation of user and tenant context,
    
- authorization rules that belong to A’s use case,
    
- avoiding propagation of untrusted headers,
    
- declaring whether it expects B to authorize the user.
    

### Service B owns

- authentication of Service A,
    
- validation of received context,
    
- authorization rules for resources owned by B,
    
- audit logging of both actor and initiator,
    
- correct handling of missing or invalid context,
    
- deciding whether user context is required for an operation.
    

### The platform owns

- service-to-service authentication mechanisms,
    
- standard trace propagation,
    
- correlation identifiers,
    
- the context contract,
    
- secure HTTP and message propagation,
    
- header and message allowlists,
    
- common log field names,
    
- token exchange where delegation is required,
    
- validation middleware.
    

---

## Failure Handling

Service B should reject a call when:

- the calling service is not authenticated,
    
- the caller is not allowed to invoke the operation,
    
- required user context is missing,
    
- the tenant cannot be verified,
    
- the user is not authorized for the resource,
    
- the context is malformed,
    
- the context contains conflicting identities.
    

These failures should be distinguishable.

For example:

```text
unauthenticated service
unauthorized service
missing user context
invalid tenant context
user access denied
```

Do not flatten all cases into:

```text
403 Forbidden
```

without stable machine-readable error codes and sufficient audit information.

---

## Recommended Patterns

### Service-level authorization

Use when Service A owns the business authorization:

```text
B authenticates A.
B authorizes A.
userId is recorded for audit.
```

### User-level authorization in B

Use when B owns the protected resource:

```text
B authenticates A.
B reads the propagated userId.
B independently authorizes the user.
B records both identities.
```

### Delegated user token

Use when B must validate a cryptographically protected delegated identity and scopes:

```text
B authenticates A.
B validates a token intended for B.
B sees both the user and the calling service.
```

### Queue command accepted by A

Use when authorization occurs before enqueueing:

```text
A authorizes the user.
A publishes an accepted command.
B trusts A as producer.
userId is preserved for audit.
```

### Queue command re-authorized by B

Use when authorization must reflect execution-time state:

```text
A publishes user and resource context.
B performs current authorization before execution.
```

---

## Warning Signs

The design may be unhealthy when:

- browser cookies are forwarded through the service chain,
    
- arbitrary inbound headers are copied downstream,
    
- `userId` alone grants access,
    
- Service B cannot identify the calling service,
    
- audit logs record only the user and hide the technical actor,
    
- a token is stored in every queue message,
    
- tenant context is trusted without verification,
    
- one generic context object mixes security, tracing, and business data,
    
- authorization semantics differ between services but are undocumented,
    
- ambient context is used everywhere in business logic,
    
- user context is propagated to services that do not need it,
    
- events contain access tokens or live credentials.
    

---

## Practical Rules

1. Authenticate the calling service independently.
    
2. Treat `userId` as contextual metadata, not as proof of authorization.
    
3. Let the service owning the protected resource own the authorization decision.
    
4. Record the technical actor and original user separately.
    
5. Prefer delegation over impersonation.
    
6. Do not blindly forward browser cookies.
    
7. Do not blindly forward user access tokens.
    
8. Use delegated tokens only when B genuinely needs to authorize the user cryptographically.
    
9. Propagate only an explicit allowlist of context fields.
    
10. Remove or overwrite untrusted internal headers at the system boundary.
    
11. Keep trace, audit, security, and business context separate.
    
12. Validate tenant context against trusted identity.
    
13. Do not store long-lived user credentials in queue messages.
    
14. Define whether asynchronous authorization occurs at acceptance time or execution time.
    
15. Use standard machine-readable error codes for context and authorization failures.
    
16. Keep automatic context propagation visible, limited, and auditable.
    
17. Avoid letting ambient context become a hidden dependency throughout the application.
    

---

## Mental Model

A service-to-service call may involve two different actors:

```text
Original initiator: User U
Technical caller: Service A
```

Service B must know:

- which actor it is authenticating,
    
- which actor it is authorizing,
    
- which actor it is recording for audit,
    
- whether Service A is trusted to propagate user context.
    

The preferred model is:

```text
Service A authenticates itself to Service B.

Service A propagates the original user ID as trusted context.

Service B decides whether it authorizes:
- Service A,
- User U,
- or both.

Service B logs both identities.
```

The central principle is:

> Propagate identity for context and audit.  
> Authenticate the service independently.  
> Authorize at the service that owns the relevant rule or resource.