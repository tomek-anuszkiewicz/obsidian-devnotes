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

# Designing APIs for LLM-Generated Integration Code

> [!IMPORTANT]
> **The Agent-Native Interface Bundle Axiom**: In the agentic era, external APIs and microservices are primarily consumed and integrated by **autonomous coding agents and LLM orchestration engines**, rather than humans manually reading HTML documentation. Exposing raw, untyped HTTP endpoints forces models to guess path parameters, serialization conventions, and side effects—drastically increasing integration hallucination rates. Modern service interfaces must publish an **Agent-Native Interface Bundle**: pairing formal schema contracts (OpenAPI, AsyncAPI, GraphQL) with **strongly typed generated clients**, **first-class tool servers (MCP)**, **machine-executable operational instructions (`SKILL.md`)**, and **deterministic sandbox test suites**.

```text
Traditional API Publishing:
OpenAPI Spec + HTML Swagger Docs ──► Human Reads in Browser ──► Manually Writes Integration Code

Agent-Native Interface Bundle:
OpenAPI / AsyncAPI Contract
  ├── Strongly Typed Generated Client (Constrains action space to typed methods)
  ├── Native MCP Server (Exposes runtime tool invocation & parameter schemas)
  ├── Executable Skill / Rulebook (Encodes auth, idempotency & retry workflows)
  └── Deterministic Sandbox Oracle (Provides instant pass/fail compilation & tests)
              │
              ▼
Autonomous Agent Synthesizes Verified Integration Code in Minutes
```

---

## Executive Summary & Core Architectural Invariants

Designing APIs for automated generation by coding agents operating inside an [[Agentic Coding Harness and Controlled Development Workflows|agentic harness]] inverts traditional API design assumptions:

1. **Constraining the Model's Action Space**: Never force an agent to manually construct raw HTTP requests (`http.post("/api/v1/...")`). Generating transport-level strings invites URL hallucinations, header mistakes, and serialization bugs. Providing a **strongly typed client SDK** collapses the agent's action space to valid, compiler-verified methods.
2. **The Agent-Native Interface Bundle**: High-trust services ship four interconnected artifacts: the **Formal Contract** (OpenAPI 3.1, AsyncAPI, GraphQL), the **Typed Client SDK** (generated via Kiota, OpenAPI Generator, or buf), a **First-Class MCP Server** (for runtime tool discovery), and an **Executable Skill** (`SKILL.md` detailing auth, workflows, and edge cases).
3. **Intent-Revealing Business Operations Over Generic CRUD**: APIs must expose explicit domain operations (`cancelInvoice`, `revokeUserSessions`, `reserveInventory`) rather than generic database mutations (`updateEntity`, `changeStatus`). Explicit intent prevents agents from mistaking cancellation for deletion.
4. **Negative Documentation as Hallucination Defenses**: Schema descriptions must explicitly declare preconditions and counter-indications—stating what an operation *does not* do and which alternative operation must be selected instead.
5. **Docstring Preservation in Generated SDKs**: Client generators must propagate OpenAPI summaries, parameter constraints, and markdown descriptions directly into code comments (JSDoc, XML comments, docstrings). Agents reason over local in-file comments rather than parsing raw JSON schemas for every prompt.
6. **Machine-Actionable Semantic Error Contracts**: Runtime error payloads must not return opaque status codes or unformatted strings. They must return machine-readable resolution hints (e.g., `{"code": "invoice_already_issued", "suggestedOperation": "cancelInvoice"}`) allowing autonomous agents to self-heal integration logic.
7. **Protocol-Agnostic Contract Governance**: The same discipline applies across all integration topologies: REST with OpenAPI, GraphQL with typed introspection schemas, and asynchronous event-driven messaging with AsyncAPI message contracts.
8. **Repository-Level Discovery Ergonomics**: Client classes must use domain-oriented names (`IOrdersClient`, `IIdentityClient`) rather than transport or team labels (`IServiceAClient`, `IApiV2Client`). Coding agents discover capabilities by matching business concepts against typed interface definitions.

---

## The Preferred Integration Architecture

The goal when steering a coding agent is not merely for the model to execute an API call, but to synthesize durable, maintainable application code that cleanly interfaces with external capabilities:

```text
                       Business Requirement
                                │
                          Coding Agent
                                │
                   Discover Business Capability
                                │
                     Strongly Typed Interface
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
         OpenAPI             GraphQL             AsyncAPI
            │                   │                   │
          REST                GraphQL            Messaging
```

The critical abstraction presented to the coding agent must always be a **typed, semantically named client interface**. Low-level transport mechanics—HTTP serialization, TLS handshakes, multiplexing, and headers—must remain hidden beneath the generated SDK.

---

## The Agent-Native Interface Bundle: Beyond Swagger UI

In the agentic era, documenting an API solely for human developers reading HTML in browser tabs is obsolete. When an enterprise or public platform exposes services, the primary consumers are increasingly **autonomous coding agents and LLM orchestration loops**.

Platform creators should ship an **Agent-Native Interface Bundle** (a pattern closely aligned with [[WebMCP - Turning Web Applications into Agent-Native Toolkits|WebMCP and agent-native toolkits]]):

### 1. First-Class Model Context Protocol (MCP) Servers
Instead of forcing an agent to write boilerplate HTTP request handlers from scratch, services provide a native MCP server:
- The MCP server exposes the API's business operations as **discrete, typed tools** with explicit parameters, deterministic outputs, and rich error structures.
- Agents can either invoke the MCP tools directly during runtime execution or use the MCP schemas as ground truth to generate verified integration code.

### 2. Bundling Executable Agent Skills (`SKILL.md`)
Traditional documentation relies on human intuition to navigate pagination, rate-limiting backoffs, or OAuth token refresh flows. An **Agent Skill** bundles these operational rules as explicit markdown instructions with frontmatter. It tells the agent:
- Exactly how to authenticate and refresh credentials,
- How to handle pagination and idempotency keys,
- Which endpoints must be called sequentially (workflows),
- How to interpret domain-specific error codes.

### 3. Pre-Packaged Verification Sandboxes
An agent cannot reliably verify integration code without an execution loop:
- Platforms should provide deterministic sandbox endpoints or mock test suites that agents can immediately run locally in their verification step.
- This creates an immediate pass/fail compiler and runtime feedback loop.

---

## Contract Engineering: OpenAPI, Business Semantics & Negative Guidance

For REST APIs, OpenAPI must describe not only the transport contract, but also the business semantics and lifecycle preconditions of the operation.

### Intent-Revealing Operations vs. Vague CRUD
Operations should clearly express domain intent:

```text
Prefer:
cancelInvoice
revokeUserSessions
reserveInventory
approveOrder

Avoid:
updateEntity
executeAction
changeStatus
processRequest
```

CRUD operations are appropriate only when the business operation is genuine database storage (e.g., `DELETE /drafts/{id}`). But a business operation such as cancelling an issued invoice must be represented explicitly (`POST /invoices/{id}/cancel`) rather than pretending that cancellation is equivalent to deletion.

### Negative Guidance as a Guardrail
Models frequently hallucinate operations based on superficial lexical matching (e.g., choosing `delete` whenever encountering words like "remove", "invalidate", or "cancel"). 

Authoritative schema descriptions must inject **negative guidance**:

```yaml
/users/{userId}/sessions:
  delete:
    operationId: revokeUserSessions
    summary: Revoke all active sessions for a user
    description: |
      Revokes all active authentication sessions belonging to the specified user.
      Use this operation when access for the user must be immediately invalidated.
      
      Preconditions:
      - User must exist and have active sessions.
      
      Side Effects:
      - Drops all active JWT tokens across all devices.
      
      Negative Guidance:
      - This operation DOES NOT delete or deactivate the user account.
      - To disable a user account, call disableUser.
```

```yaml
/invoices/{id}:
  delete:
    operationId: deleteDraftInvoice
    summary: Permanently delete a draft invoice
    description: |
      Permanently deletes a draft invoice from persistence.
      
      Preconditions:
      - Invoice status must be 'Draft'.
      
      Negative Guidance:
      - DO NOT use this operation for issued invoices.
      - Issued invoices are immutable legal documents and must be cancelled using cancelInvoice.
```

Explicitly stating when an operation *must not* be used prevents the agent from making disastrous integration errors.

---

## Client Synthesis & Strongly Typed SDKs

A coding agent should never construct HTTP requests manually:

```text
// Anti-pattern: Handcrafted transport assembly (error-prone, URL hallucination risk)
await http.delete("/users/" + userId + "/sessions");

// Preferred: Strongly typed domain client method (compiler-verified)
await identityClient.revokeUserSessions(userId, context);
```

Clients are compiled from API contracts using modern contract-first client generators:
- **Declarative HTTP/REST Client Generators** emitting strongly typed client interfaces across language ecosystems,
- **Protocol Buffer and RPC Compilers** providing binary serialization and schema validation,
- **OpenAPI and AsyncAPI SDK Emitters**.

```text
OpenAPI / AsyncAPI Contract  ──►  Client Generator  ──►  Strongly Typed SDK  ──►  Agent Application Code
```

This drastically collapses the agent's error surface. The agent no longer needs to deduce URLs, HTTP verbs, serialization conventions, query string formatting, or header names—it selects a typed, compiler-validated method.

### Preserving Documentation in Generated Clients
Descriptions from API specifications must be carried directly into generated docstrings and interface comments:

```text
interface InvoicesClient:
    """
    Cancels an issued invoice while preserving it for audit.
    Precondition: Invoice status must be 'Issued'.
    Do not use for draft invoices (use delete_draft_invoice instead).
    """
    function cancel_invoice(id: UUID, context: ExecutionContext) -> InvoiceReceipt

    """
    Permanently deletes a draft invoice.
    Precondition: Invoice status must be 'Draft'.
    Issued invoices cannot be deleted.
    """
    function delete_draft_invoice(id: UUID, context: ExecutionContext) -> Void
```

Because agents reason over local repository context, placing semantic descriptions directly above method signatures enables the model to select the correct method without needing to parse multi-megabyte external OpenAPI specifications on every turn.

---

## Semantic Error Payloads & Self-Healing Workflows

When an API call fails, the response payload must provide structured, machine-actionable diagnosis rather than raw HTTP status codes or generic strings:

```json
// Anti-pattern: Opaque error code
{
  "errorCode": 3817
}

// Preferred: Machine-actionable semantic error payload
{
  "code": "invoice_already_issued",
  "message": "Issued invoices cannot be deleted.",
  "status": 409,
  "suggestedOperation": "cancelInvoice",
  "documentationUrl": "https://api.domain.internal/errors/invoice_already_issued"
}
```

When an agent encounters `suggestedOperation: "cancelInvoice"`, its error recovery loop can immediately self-correct: replacing `deleteDraftInvoice` with `cancelInvoice` and re-running the test suite without human intervention.

---

## Protocol Agnosticism: GraphQL and AsyncAPI

The same contract-first principles govern non-REST protocols:

### GraphQL
- Use rich schema descriptions on types and fields,
- Expose explicit mutations (`cancelInvoice(id: ID!): Invoice!`) rather than generic update mutations,
- Generate typed GraphQL clients via code generators to eliminate syntax errors in query documents.

### Event-Driven Messaging (AsyncAPI)
- Clearly distinguish commands from domain events:
  - `RevokeUserSessions` (Command sent by application to initiate state change),
  - `UserSessionsRevoked` (Event emitted after successful execution).
- Use **AsyncAPI** to define message schemas, topic topologies, header propagation, and delivery guarantees.
- Provide strongly typed message publisher and consumer wrappers so agents publish typed events rather than raw message envelopes.

---

## Relationship to the Knowledge Graph

- **[[WebMCP - Turning Web Applications into Agent-Native Toolkits]]**: Extends API contracts directly into browser DOM environments via `navigator.modelContext`.
- **[[Applications May Shift from Fixed Features to Agent-Extensible Primitives]]**: Exposing domain primitives and validation invariants rather than monolithic UI features.
- **[[Designing Software for AI Agents]]**: General architectural principles for making software discoverable, verifiable, and navigable for coding agents.
- **[[Service-to-Service Communication - How Service A Should Call Service B]]**: Inter-service contract governance, synchronous vs. asynchronous topologies, and dependency boundaries.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Providing native MCP servers and sandbox test suites alongside API contracts.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]**: How application integration paradigms evolve when agents write and maintain client code.
