---
title: The 5-Layer System Stack for Agentic Software Engineering - Practitioner Rewrite
tags:
  - system-architecture
  - agentic-engineering
  - system-stack
  - mechanical-sympathy
  - verification-harness
  - runtime-observability
  - context-architecture
  - developer-ergonomics
aliases:
  - The 5-Layer System Stack
  - 5-Layer Agent Architecture
  - System Stack for Autonomous Coding
  - From Silicon to Developer Ergonomics
  - Architectural Taxonomy of Agentic Engineering
---

# The 5-Layer System Stack for Agentic Software Engineering

Putting a reasoning model in an IDE is the easy part. Once agents start writing implementation code, we also have to decide how they will see the system, check their work, and handle failures after deployment. That changes the work of the engineer as well as the shape of the software.

Many familiar design choices reflect human constraints: we can hold only so much code in working memory, typing takes time, and teams divide ownership along organizational lines. Those choices deserve another look when agents produce much of the implementation. The following five layers connect the code they write to the tests, runtime, context, and engineering decisions around it.

| Layer | What it covers |
| :--- | :--- |
| **5. Engineering economics and future** | Engineering roles; autonomous news, dependency, and browser workflows; commodity code and private operational knowledge. |
| **4. Prompts, context, and models** | Context pruning and attention budgets; AST-based code graphs with Graphify, GitNexus, and Obsidian export; MCP and SQL Data API Builder. |
| **3. Systems and infrastructure** | AKS, Istio, Envoy, CQRS, sagas, and event topology; Polly policies and rate limits; OpenTelemetry, trend alerts, and conversational diagnosis. |
| **2. Testing and code review** | Unit, snapshot, fuzz, and end-to-end tests; executable architecture rules; branch environments and several-agent PR review. |
| **1. Architecture and code** | Memory layout and allocation on hot paths; one operation per feature slice; CPU-aware execution and source generation. |

The layers affect one another. Engineers set goals and boundaries; an agent loads relevant context and proposes code; tests check that code; production telemetry shows what actually happened and feeds the next decision.

---

## Layer 1: Architecture and code

Start with the code that runs on actual hardware. CPU pipelines, caches, heap allocations, and database query planners still determine latency, even if an agent wrote the source.

An agent trained on public repositories can readily produce deep inheritance trees, runtime reflection, many heap allocations, or several layers of dependency injection. Those patterns are common in examples, but they can be expensive on a hot path. Give the agent explicit performance constraints when throughput or latency matters, then check the result against the runtime.

### 1. Keep a business operation together

A conventional enterprise layout puts a controller, interface, service implementation, and repository wrapper in separate places. To change one operation, an agent has to find and load each piece. Missing one contract or validator makes it easier to guess incorrectly.

Organize related code as a vertical slice: one feature folder per operation, with a clear handler instead of a broad `PaymentService`:

```text
src/
└── Features/
    └── ProcessPayment/
        ├── ProcessPaymentCommand.cs
        ├── ProcessPaymentHandler.cs
        ├── ProcessPaymentValidator.cs
        └── ProcessPaymentEndpoint.cs
```

The command, validation, endpoint, execution logic, and response models stay near the operation they belong to. The agent can read the relevant slice and make a smaller change, with less chance of touching unrelated features.

### 2. Give the agent concrete .NET guidance for hot paths

When an operation has a real performance budget, specify the primitives and behaviors you expect.

#### Memory and value semantics

- Use `Span<T>` and `ReadOnlySpan<T>` to work on contiguous parts of strings or byte buffers without making copies.
- Rent temporary buffers from `ArrayPool<T>.Shared` for intermediate payload transformations; return them in a `finally` block.
- Use `stackalloc byte[256]` for a small fixed buffer that remains inside the current stack frame.
- Use a `readonly record struct` for small immutable values such as `PaymentId` or `Money`, where value semantics and avoiding an additional object allocation help. Use a `class` for a larger entity with identity and a longer lifetime. Watch the generated equality and cloning work of `record class` on hot paths.
- Pass large readonly structs with `in` to avoid copies, and use `ref readonly` when exposing an internal element without copying it.

#### Execution in tight loops

- In a performance-critical loop, inspect what `.Select()`, `.Where()`, and `.ToList()` allocate and dispatch. An explicit `for` or `foreach` over `Span<T>` can avoid that overhead.
- For fixed-size operations such as checksum validation or financial parsing, consider loop unrolling where it helps branch prediction or SIMD vectorization.
- Mark lambdas `static` where they must not capture local state, for example `static (state, item) => ...`. The compiler then rejects an accidental capture and its closure allocation.
- Generate regular expressions at build time with `[GeneratedRegex]` instead of constructing them during execution:

```csharp
[GeneratedRegex(@"^[A-Z]{3}-\d{6}$", RegexOptions.Compiled | RegexOptions.CultureInvariant)]
private static partial Regex OrderCodeMatcher();
```

- Avoid interpolating strings inside `ILogger` calls, such as `logger.LogInformation($"Processing {orderId}")`. A `[LoggerMessage]` method provides structured logging while avoiding formatting and boxing work in the call:

```csharp
public static partial class LogExtensions
{
    [LoggerMessage(EventId = 1001, Level = LogLevel.Information, Message = "Processing payment {TransactionId} for {Amount} {Currency}")]
    public static partial void LogPaymentProcessing(this ILogger logger, Guid transactionId, decimal amount, string currency);
}
```

#### API payloads and protocols

Decide explicitly whether each payload permits `null`. Where omitted null fields are part of the contract, `JsonIgnoreCondition.WhenWritingNull` reduces the payload and makes that choice visible:

```csharp
var jsonOptions = new JsonSerializerOptions
{
    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
};
```

Choose the protocol for the actual caller and traffic: gRPC/Protobuf for high-throughput, low-latency internal calls and streaming; REST/JSON for public APIs and third-party webhooks; GraphQL when a complex frontend needs to shape data across several entities without a growing list of backend routes.

---

## Layer 2: Testing and code review

An agent can produce plausible code that breaks a contract. Give it checks with definite outcomes, and feed failures back into the coding loop.

```text
Task → Agent writes code → Compiler and architecture checks
  ↑                              │ pass
  │                              ▼
  ├── failures ← Unit and snapshot tests
  │                              │ pass
  │                              ▼
  └── failures ← Fuzzing and Playwright E2E
                                 │ pass
                                 ▼
                       Candidate commit
```

### 1. Check outputs and test the tests

Model-based judgments alone cannot confirm that a program works. Capture complex outputs such as database state, serialized payloads, and generated files with snapshots, for example `Verify.Xunit`. After an internal refactor, compare the output with the approved snapshot, including its wire format.

Property-based tests with FsCheck or QuickCheck can exercise contracts across many inputs. Mutation tests with Stryker.NET then change the program deliberately to see whether the new tests catch a fault.

### 2. Make architecture rules executable

Put boundaries into build checks using `NetArchTest`, reflection, or a Roslyn analyzer. An agent that crosses a prohibited boundary should see a failing check immediately. The following sketch checks handler length and calls out LINQ on marked hot paths:

```csharp
[Fact]
public void CommandHandlers_Must_Not_Exceed_Line_Limit_And_Have_No_LINQ()
{
    var handlers = Types.InAssembly(typeof(ProcessPaymentHandler).Assembly)
        .That().HaveNameEndingWith("Handler")
        .GetTypes();

    foreach (var handler in handlers)
    {
        // Enforce operation-to-file size bounds (e.g., <= 400 lines)
        var lineCount = File.ReadAllLines(GetSourcePath(handler)).Length;
        Assert.True(lineCount <= 400, $"Handler {handler.Name} exceeds 400 lines: {lineCount}");

        // Enforce no dynamic LINQ references in hot paths
        var usesLinq = handler.GetMethods()
            .Any(m => m.GetCustomAttributes(typeof(HotPathAttribute), false).Any()
                   && MethodUsesLinq(m));
        Assert.False(usesLinq, $"Hot path in {handler.Name} contains LINQ allocations.");
    }
}
```

The sketch uses a 400-line handler limit. The broader rule in this stack sets an 800-line ceiling for implementation files and asks the agent to split a file that exceeds it. Other checks ban `.Result`, `.Wait()`, and unvalidated nullable dereferences (`!`). A feature module should reach another domain through an explicit contract or integration event, not by referring directly to its internal models.

### 3. Give each branch a testable environment

A shared staging environment becomes unreliable when many agents and engineers change it at once. Signadot and Telepresence can run a changed workload locally or in a lightweight branch environment. A request header routes test traffic to that version while other services remain shared:

```text
Gateway
├── Normal request ───────────────► Shared staging Service A ──► Service B
└── x-branch=feat-2 ─────────────► Preview Service A' ────────► Shared Service B
```

This lets a branch run an integration check against existing cloud dependencies without copying all infrastructure.

### 4. Repair Playwright tests using the failure evidence

Selectors such as `#submit-btn-v2` change as the UI changes. Run Playwright end-to-end tests inside the agent loop. When a test fails, pass the DOM, trace, and screenshot to the agent. It can find the current control using roles, accessibility attributes, and the page structure, then propose a PR that fixes the UI and the test selector together.

### 5. Review agent-written changes from several angles

The coding agent implements the task, formats the code, and runs local tests. A security reviewer checks credential exposure, SQL injection, unsafe deserialization, and logs containing PAN, CVV, or passwords. A performance and architecture reviewer checks contention, allocations, and domain boundaries.

A final review step reconciles their comments. If the reviewers disagree or an invariant remains broken, the loop stops and hands a human engineer the diff and failure log before production deployment.

---

## Layer 3: Systems and infrastructure

After deployment, the system has to cope with partial failures and leave enough evidence to explain them. Consider a card transaction path with an ingress gateway, payment intake, a durable saga, a card network connector, and Kafka events. AKS hosts the services; Envoy sidecars send telemetry through an OpenTelemetry collector to Grafana or Kibana.

```text
API clients → Gateway / mTLS / Envoy → Payment intake → Durable saga
                                          │                 │
                                          ▼                 ▼
                                      Kafka events ← Card network connector

Envoy sidecars → OpenTelemetry collector → Grafana / Kibana
```

### 1. Make transaction processing resilient

Pulumi can provision the AKS cluster, managed Kafka topics, and Azure Application Insights. Istio and Envoy handle mTLS, sidecar HTTP access logs, and service routing.

At the card network boundary, configure Polly for the failures the service can observe. The example policy opens a circuit if downstream 5xx responses or timeouts exceed 5% of requests over ten seconds. Retries use exponential backoff with jitter so recovering endpoints do not receive a simultaneous wave of requests. Bulkhead limits cap concurrent external calls so one failing provider does not consume the service thread pool.

### 2. Separate commands, read models, and long transactions

Commands such as `ProcessPaymentCommand` and `RefundTransactionCommand` validate the business rules, append to a transaction ledger, and emit domain events. Read models are projected asynchronously into indexed PostgreSQL or Redis, letting clients query without locking transactional tables.

For a sequence such as authorizing a card, reserving inventory, and capturing funds, use a durable saga in Durable Functions or a temporal state machine. If capture fails, the workflow runs the defined compensation steps rather than depending on one broad distributed transaction.

### 3. Choose a Kafka topic layout deliberately

| Pattern | Structure | Benefit | Cost | Suitable use |
| :--- | :--- | :--- | :--- | :--- |
| Topic per message type | `payments.authorized`, `payments.captured`, `payments.refunded` | Separate consumer access, fine-grained RBAC, and deserialization by type. | More broker partitions and harder ordering across event types. | Transaction events with different consumer groups. |
| Consolidated event stream | `payments.events` with `eventType`, `schemaVersion`, and `payload` in an envelope. | Simpler infrastructure and ordered events for an entity. | Consumers filter unwanted events and pay for envelope dispatch. | Entity audit logs, event sourcing, and CDC. |

### 4. Send changing state to the frontend

Use Server-Sent Events when the backend only needs to push transaction status, build output, or agent output to the browser. Use SignalR or WebSockets for genuinely bidirectional work such as collaborative editing or interactive canvas controls.

For concurrent changes, the backend can use optimistic locking and version vectors, then push patches to the UI so clients can resolve state conflicts.

### 5. Trace a request across services

Instrument the services with OpenTelemetry and propagate `traceparent` through HTTP, gRPC, and Kafka envelopes. An agent can inspect related spans and logs instead of asking an engineer to read 50 GB of daily logs.

Alert on changes in error ratios and p99 latency trends, including sudden changes in their rate, as well as on fixed thresholds such as CPU above 85%. Feed anomalous span graphs and correlated logs to an LLM diagnostics service to investigate which commit or configuration change caused the problem.

---

## Layer 4: Prompts, context, and models

The agent can work only with the context it loads. A long prompt containing every rule, old debate, and unrelated file costs tokens and makes the relevant contracts harder to find. Keep context tied to the current change.

### 1. Retrieve code by its relationships

Naive text chunks can cut through a syntax tree or separate a caller from the interface it uses. Build an AST-based code graph with tools such as Graphify and GitNexus. Track symbols, implementations, inheritance, imports, and call paths.

Export dependency maps to Markdown and Obsidian for human navigation. When the agent changes `IPaymentProcessor`, load the nearby implementations, callers, and tests into its context:

```text
Repository → Tree-Sitter / Roslyn parsing → Code dependency graph
                                         ├── Types, functions, interfaces
                                         ├── Implements, calls, imports
                                         ├── Obsidian export for people
                                         └── Relevant subgraph for the agent
```

### 2. Expose tools and data through explicit interfaces

MCP gives the agent a common way to call internal tools. A small MCP server in Docker or over stdio/SSE could expose `query_database_schema(table_name)`, `profile_query_execution_plan(sql_query)`, and `fetch_service_logs(service_name, trace_id)`.

A schema-aware REST or GraphQL layer such as Azure Data API Builder can expose selected database objects. The agent can inspect schemas, issue parameterized queries, and reason about indexes without unrestricted, untracked administrative access to the database.

### 3. Keep rules and working context under control

Too many simultaneous instructions can make the agent alternate between conflicting rules: it fixes one requirement and breaks another. Keep the primary system prompt below 1,500 tokens in this setup, and load task-specific guidance as modular skills, for example `awesome-agent-skills`, `azure-skills`, or `Wayfinder`.

As the work progresses, remove completed tasks and old agent debates from the active context. Retain the user's original goal, the current state of edited files, compiler failures, and the tests that decide whether the change works.

---

## Layer 5: Engineering economics and future

This layer concerns the engineer's day-to-day interface, work agents can do in the background, and the value of the software they help produce.

```text
Voice input → WisprFlow / Whisper → Structured engineering notes
RSS / web news → Deduplicate and verify → Filtered briefing
Package feeds / Renovate → Upgrade, test, fix → PR with breaking changes handled
```

### 1. Make it easier to express and check a task

Connect local or edge speech-to-text tools such as `SuperWhisper` or `WisprFlow` to IDE commands. An engineer can dictate an implementation goal, and the transcription workflow can turn the spoken explanation into a structured prompt.

Use a browser automation agent such as `browser-use` to navigate applications, check a production deployment, test a third-party integration, or collect research references.

### 2. Run routine work in the background

An information agent can read engineering blogs, release notes, and social feeds, remove duplicates and marketing noise, and prepare a weekly technical briefing.

For dependency upgrades, go beyond a Renovate or Dependabot PR that only changes a version. The agent detects a new NuGet package, .NET runtime, or Docker base image; reads the changelog and breaking changes; compiles the project; repairs deprecated calls or broken APIs; runs the Layer 2 test suite; and opens a passing PR.

A local model can also act as a rehearsal partner before a design review, salary negotiation, or difficult architecture discussion. It can point out weak technical explanations, defensive phrasing, and gaps in the argument before the conversation with the team.

### 3. Know where the value moves

Models can generate common CRUD services, algorithms, a Redis-backed cache, or an OAuth flow quickly. Public syntax and familiar architecture are therefore easier to reproduce.

The harder-to-copy parts of a company's system are its private domain material, production history, execution data, database states, and the delivery checks that encode business rules. The engineer's job increasingly includes setting system boundaries, specifying its topology, defining invariants, strengthening tests, and checking that agent-written changes remain safe and maintainable.

---

## Four practical spikes

These projects exercise the layers in a concrete setting.

### Spike 1: Explore a transaction from overview to runtime

Build a diagnostic dashboard for card transactions. Start with a list showing status, amount, latency, and failure rate. Clicking a transaction reveals the cardholder, risk score, and merchant. A deeper view shows SQL rows, lock wait times, and Kafka payloads with offsets. The last level shows OpenTelemetry spans, Envoy access logs, and allocation profiles for that request.

Navigation should also work in reverse: open a user profile and see all related payment events. That is the proposed “Fractal UI” browsing pattern.

```text
Payments list
  ↓ select transaction
Payment, user, merchant
  ↓ inspect data
SQL rows, Kafka envelopes
  ↓ inspect execution
OpenTelemetry spans, allocation profile, Envoy logs
```

### Spike 2: Build an MCP server for database inspection

1. Write a local MCP server in C# or Node.js that runs over stdio.
2. Connect it to Azure Data API Builder or a local SQLite database.
3. Configure VS Code Copilot or Claude Desktop to use the server.
4. Ask the model to inspect table relationships, suggest indexes, and verify schema migrations in conversation.

### Spike 3: Repair a failing test with a Slack workflow

1. Build the workflow in LangGraph or n8n.
2. Add an interactive Slack interface with Block Kit buttons and dropdowns.
3. Connect it to a Playwright end-to-end runner.
4. On a CI/CD failure, post the trace and proposed patch to Slack.
5. Let a team member choose “Approve and Merge” there; apply the patch, rerun the build, and close the issue.

### Spike 4: Generate a UI for an operational query

1. Connect a React application to a backend agent through Server-Sent Events.
2. Give the user this input: *“Build a query tool to inspect failed card transactions over $500 in Poland with bank decline code 05.”*
3. Have the backend generate a JSON component schema as it works.
4. Let React read the SSE stream and render the form, table, and charts for that query.
