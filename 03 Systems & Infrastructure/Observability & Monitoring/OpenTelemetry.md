---
title: "OpenTelemetry"
tags:
  - opentelemetry
  - observability
  - distributed-systems
  - monitoring
  - tracing
  - microservices
  - infrastructure
aliases:
  - OpenTelemetry Architecture
  - OTel Signals and Collector
  - Decoupling Telemetry Production from Storage Backends
  - Distributed Tracing and Context Propagation
---
  - "OpenTelemetry as the Runtime Truth for Autonomous Agents"

# OpenTelemetry

## 1. What OpenTelemetry Is

OpenTelemetry (OTel) is an open-source, vendor-neutral observability framework. It standardizes how applications and infrastructure:

- Generate telemetry (traces, metrics, logs, and continuous profiles).
- Describe telemetry through common metadata schemas and semantic conventions.
- Propagate tracing context across synchronous network boundaries and asynchronous messaging boundaries.
- Transport telemetry over wire protocols.
- Process, filter, enrich, and batch telemetry before it hits storage.

OpenTelemetry is **not** a database, a dashboard engine, or an observability backend. It does not store your time-series data or index your traces for querying. Instead, it sits between your running software and the downstream analytics systems:

```text
Application / Infrastructure
        ↓
OpenTelemetry Instrumentation (APIs & SDKs)
        ↓
OpenTelemetry Protocol (OTLP) / Collector
        ↓
Observability Backend
```

Typical backends include:

- Prometheus, Thanos, and Grafana Mimir (metrics)
- Grafana Loki (logs)
- Grafana Tempo and Jaeger (traces)
- Elasticsearch and OpenSearch (logs, traces)
- Azure Monitor / Application Insights
- Datadog, Dynatrace, New Relic, Splunk
- Any custom ingestion system that accepts OTLP natively

### The Signals

OpenTelemetry organizes observability into distinct signals:

```text
OpenTelemetry
├── Traces
├── Metrics
├── Logs
└── Profiles
```

- **Traces**: Document the causal, end-to-end path of an execution through a distributed system. Spans form a Directed Acyclic Graph (DAG) representing operations, dependencies, and latencies.
- **Metrics**: Aggregated numerical measurements (counters, up/down counters, gauges, histograms) tracking system throughput, error rates, saturations, and high-level service level indicators (SLIs).
- **Logs**: Structured, timestamped event records containing discrete diagnostic context. Crucially, in OpenTelemetry, logs carry `TraceId` and `SpanId` attributes, tying them directly into active trace paths.
- **Profiles**: Continuous call-stack samples attributing CPU, heap, and thread usage to specific runtime code paths. Profiles represent the newest signal and are still stabilizing across language SDKs.

Frontend, browser, and mobile telemetry are not separate signal types. They are standard telemetry sources running outside the datacenter that emit traces, metrics, and logs back to your ingestion layer via HTTP-based OTLP.

---

## 2. OTLP — OpenTelemetry Protocol

The OpenTelemetry Protocol (OTLP) defines the serialization formats and transport mechanisms used to move telemetry between producers, proxies, and storage backends. It is implemented primarily on top of Protocol Buffers (Protobuf) over either gRPC (HTTP/2) or HTTP/1.1 (Protobuf or JSON payloads).

The typical path starts at the application:

```text
.NET Application
      ↓ OTLP (gRPC / HTTP)
OTel Collector
```

However, OTLP is topology-agnostic. Senders and receivers do not care if they are communicating with an in-process SDK, an intermediate routing proxy, or a cloud backend:

```text
Collector A (Agent / DaemonSet)
    ↓ OTLP
Collector B (Central Cluster / Gateway)
    ↓ OTLP
Observability Backend
```

Because OTLP is an open specification, the Collector acts as a universal adapter. It can ingest multiple legacy and modern protocols, normalize them internally into the OpenTelemetry data model, and forward them via OTLP:

```text
Container stdout logs ────┐
                          │
Prometheus /metrics ──────┼──→ OpenTelemetry Collector ──► OTLP / Backends
                          │
OTLP traces (gRPC) ───────┘
```

---

## 3. OpenTelemetry Architecture

The framework consists of distinct architectural layers:

```text
OpenTelemetry
│
├── APIs
├── SDKs
├── Telemetry Data Model
├── Semantic Conventions
├── Context Propagation
├── OTLP (Wire Protocol)
└── OpenTelemetry Collector
```

### APIs vs. SDKs

OpenTelemetry strictly separates the API from the SDK:

- **API**: Contains only the interfaces and minimal types required to instrument code. It has zero transitive dependencies on transport libraries or exporters. If an application is instrumented with the API and no implementation (SDK) is registered at runtime, the API defaults to a complete no-op implementation with negligible CPU overhead.
- **SDK**: The concrete implementation of the API for a specific language runtime (e.g., .NET, Go, Java, Python). It handles state management, in-memory buffering, batch processing, sampler algorithms, and exporter dispatch.

### Semantic Conventions

A common issue in distributed observability is attribute fragmentation. One team tags their HTTP method as `http_method`, another uses `method`, a third uses `HTTPMethod`, and a gateway uses `request.method`. This fragmentation ruins cross-service querying, dashboarding, and alerting.

OpenTelemetry enforces **Semantic Conventions**: standard naming schemes and definitions for common operations across HTTP, databases, messaging queues, RPC systems, cloud infrastructure, and container runtimes. For example:

- `http.request.method`: `"POST"`
- `http.response.status_code`: `200`
- `db.system`: `"postgresql"`
- `db.statement`: `"SELECT * FROM orders WHERE id = ?"`
- `server.address`: `"api.internal.net"`
- `server.port`: `8080`

Adhering to semantic conventions ensures your dashboards and automated alerting rules work universally across all services, regardless of the language runtime that emitted the telemetry.

### Context Propagation

Context propagation is the mechanism that carries distributed tracing state across process and network boundaries. When an upstream service calls a downstream service over HTTP, gRPC, or an asynchronous message broker, it injects tracking identifiers into the request headers.

OpenTelemetry standardizes on the **W3C TraceContext** specification:

- `traceparent`: A single formatted header carrying the protocol version, the 16-byte `TraceId`, the 8-byte `ParentSpanId`, and trace flags (e.g., recorded/sampled status).
  - Example: `traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`
- `tracestate`: A comma-separated list of key-value pairs used to pass vendor-specific routing and filtering metadata without breaking generic trace correlation.
- **Baggage**: Key-value pairs propagated across the distributed context alongside the trace identifiers. Baggage makes business context (such as `tenant.id` or `account.tier`) accessible across downstream hops without re-querying a database, though it does not automatically turn into span attributes unless explicitly configured.

```text
Browser / Client
   ↓ (W3C traceparent injected)
Edge API Gateway
   ↓ (traceparent propagated)
Ordering Service
   ↓ (traceparent propagated via message broker)
Billing Service
```

Every service in the chain extracts the context from incoming headers, creates a child span linked to the caller's span ID, and injects the updated context into outgoing calls.

---

## 4. The OpenTelemetry Collector

The OpenTelemetry Collector is a vendor-neutral, out-of-process proxy designed to receive, process, and export telemetry. Deploying a Collector insulates application runtimes from backend-specific connection details, authentication secrets, network buffering, and schema changes.

Its internal pipeline architecture is strictly linear:

```text
Receivers ──► Processors ──► Exporters
```

A single Collector configuration can host multiple independent pipelines for traces, metrics, and logs, sharing components across them:

```text
Applications
     ↓
Collector
     ↓
[ Receivers ]   OTLP (gRPC/HTTP), Prometheus scrape, filelog
     ↓
[ Processors ]  memory_limiter → k8sattributes → filter → batch
     ↓
[ Exporters ]   OTLP, Azure Monitor, Prometheus, Elasticsearch
     ↓
Observability Backends
```

### Receivers

Receivers define how telemetry enters the Collector. They can be push-based (listening on a network socket) or pull-based (scraping target endpoints).

Common receivers:
- `otlp`: Ingests OTLP via gRPC (port 4317) and HTTP (port 4318).
- `prometheus`: Scrapes Prometheus-formatted metrics endpoints on schedule.
- `filelog`: Tails log files from local disk paths (critical for Kubernetes container logs).
- `hostmetrics`: Scrapes host-level CPU, memory, network, and disk metrics directly from the operating system.

Receivers allow legacy infrastructure that does not speak OTel to feed the same pipeline:

```text
Legacy App ──► Prometheus /metrics ──┐
                                     ├──► OTel Collector ──► Central Backend
Modern App ──► OTLP (gRPC) ──────────┘
```

### Processors

Processors manipulate, sanitize, batch, or filter telemetry as it passes through the pipeline. In Collector pipelines, **processor order matters**:

```yaml
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, k8sattributes, filter, transform, batch]
      exporters: [otlp]
```

Critical processors include:
- `memory_limiter`: Drops or pauses telemetry ingestion when the Collector process approaches its physical RAM ceiling. It must always be placed first in the pipeline to prevent out-of-memory crashes.
- `batch`: Groups individual telemetry items into larger compressed network payloads. This drastically reduces outbound network overhead and HTTP/gRPC round-trips.
- `k8sattributes`: Queries the local Kubernetes API or kubelet to enrich incoming telemetry with pod name, namespace, container name, and workload labels based on the client's IP address.
- `filter`: Discards spans, metrics, or log records based on defined conditions (e.g., drop healthy HTTP `200` calls to health-check endpoints like `/healthz`).
- `transform` (OTTLE - OpenTelemetry Transformation Language): Rewrites, extracts, renames, or drops attributes using a standard syntax.
- `tail_sampling`: Buffers spans in memory until an entire distributed trace completes, evaluating whether to keep or discard the trace based on errors, duration, or specific attributes.

```text
Raw Span
   ↓
[k8sattributes] ──► Adds: k8s.pod.name="orders-58bf9-xkz8l", k8s.namespace="prod"
   ↓
[transform]     ──► Masks: customer.credit_card = "REDACTED"
   ↓
[batch]         ──► Packs 1024 spans into a single compressed Protobuf frame
   ↓
To Exporters
```

### Exporters

Exporters translate internal OTel data models into external wire formats and transmit them over the network. They handle timeouts, connections, authentication, and retries.

A single pipeline can route to multiple destinations simultaneously:

```text
Collector Pipeline
        │
        ├──► Exporter A (OTLP) ────────► Grafana Tempo (Traces)
        ├──► Exporter B (Azure Monitor) ► Application Insights
        └──► Exporter C (Elasticsearch) ► Search / Audit Cluster
```

This multi-backend fanout lets engineering teams evaluate new observability platforms or run concurrent platforms during migrations without touching application code.

---

## 5. Direct Export vs. Collector Topology

When instrumenting a service, you have two basic deployment topologies: direct export or intermediate Collector.

### Direct Export

The application SDK transmits telemetry directly over the network to the observability backend:

```text
Application ──► OTLP / Vendor Protocol ──► Backend
```

- **Pros**: Fewer moving parts. Zero additional infrastructure to deploy, scale, and monitor. Excellent for small hobby projects, simple serverless functions (AWS Lambda, Azure Functions), or local development.
- **Cons**: Every application process must hold network credentials and target endpoints. Backpressure from a slow or unresponsive backend can consume application memory. Adding or switching backends requires redeploying application code.

### Collector Architecture

Applications emit telemetry to a local or intermediate Collector instance:

```text
Application ──► OTLP (localhost or cluster-local) ──► Collector ──► Backends
```

The Collector architecture is standard for production microservices because it provides:
- **Centralized Credential Management**: Applications don't need API keys or secrets for Datadog, Honeycomb, or Azure Monitor; only the Collector holds downstream credentials.
- **Resilience and Retries**: If a downstream backend experiences a brief outage, the Collector buffers data in memory or on local disk queues, protecting application processes from network stalling.
- **Resource Offloading**: Complex batch compression, attribute transformation, Kubernetes metadata enrichment, and tail sampling are offloaded from high-throughput application threads to a dedicated process.
- **Protocol Harmonization**: Allows diverse runtimes (Go, .NET, Java, legacy daemons) to output a uniform format before exporting.

---

## 6. OpenTelemetry Across Runtimes and Modern .NET

OpenTelemetry avoids proprietary wrappers by mapping directly to native runtime diagnostic primitives across programming languages:

| Ecosystem | Native Tracing Primitive | Native Metrics Primitive | Logging Integration | Context Propagation Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **.NET** | `System.Diagnostics.ActivitySource` / `Activity` | `System.Diagnostics.Metrics.Meter` | `Microsoft.Extensions.Logging.ILogger` | `AsyncLocal<T>` / `Activity.Current` |
| **Go** | `go.opentelemetry.io/otel/trace` | `go.opentelemetry.io/otel/metric` | `log/slog` / `uber-go/zap` | `context.Context` (explicit parameter) |
| **Rust** | `tracing` (`Span`, `Event`) | `metrics` crate | `tracing-subscriber` | `tracing::Span::current()` (task-local) |
| **Java** | `io.opentelemetry.api.trace` / Java Agent | Micrometer / OTel Metrics | SLF4J / Logback / Log4j2 | `ThreadLocal` / `io.opentelemetry.context.Scope` |
| **Python** | `opentelemetry.trace` | `opentelemetry.metrics` | `logging` stdlib module | `contextvars.ContextVar` |
| **TypeScript / Node** | `@opentelemetry/api` (`trace`) | `@opentelemetry/api` (`metrics`) | `pino` / `winston` | `AsyncLocalStorage` |

### Modern .NET Diagnostics Integration

Modern .NET (.NET 6+) natively incorporates OpenTelemetry design patterns directly into the Base Class Library (BCL):

```text
.NET BCL Primitive                 OpenTelemetry Equivalent
───────────────────────────────────────────────────────────
System.Diagnostics.Activity      ≈ OpenTelemetry Span
System.Diagnostics.ActivitySource≈ OpenTelemetry Tracer
System.Diagnostics.Metrics.Meter ≈ OpenTelemetry Meter
Microsoft.Extensions.Logging     ≈ OpenTelemetry Logging Bridge
```

This alignment means you can instrument a .NET library without adding a dependency on OpenTelemetry SDK packages. You instrument against `System.Diagnostics`, and when the application boots, the OpenTelemetry SDK attaches to those native sources.

#### Manual Tracing in .NET

```csharp
using System.Diagnostics;

public class OrderService
{
    // Define an ActivitySource for the component/library
    private static readonly ActivitySource OrderSource = new("Company.Orders.Service", "1.0.0");

    public async Task<OrderResult> CreateOrderAsync(OrderRequest request, CancellationToken ct)
    {
        // StartActivity creates an Activity (Span) only if an active listener (SDK) is registered
        using Activity? activity = OrderSource.StartActivity("CreateOrder", ActivityKind.Internal);

        // Add contextual tags (Span Attributes)
        activity?.SetTag("order.id", request.OrderId);
        activity?.SetTag("customer.id", request.CustomerId);
        activity?.SetTag("order.line_item_count", request.Items.Count);

        try
        {
            var result = await ProcessOrderInternalAsync(request, ct);
            activity?.SetTag("order.status", "Completed");
            return result;
        }
        catch (Exception ex)
        {
            // Record exception details according to semantic conventions
            activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
            activity?.RecordException(ex);
            throw;
        }
    }
}
```

The underlying code does not care if the telemetry lands in Azure Application Insights, Grafana Tempo, Datadog, or an in-memory test runner. The decision to capture and export these activities is deferred entirely to application startup:

```csharp
// Program.cs
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing => tracing
        .AddSource("Company.Orders.Service")
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddOtlpExporter(opt => opt.Endpoint = new Uri("http://otel-collector:4317")));
```

### Automatic Instrumentation

You don't need to write manual spans for every technical operation. Production SDK distributions provide automatic instrumentation via bytecode manipulation (Java), runtime monkey-patching (Python, Node.js), or native platform diagnostic hooks (.NET `DiagnosticSource`):

```text
[Incoming HTTP POST /payments]       ──► Automatic ASP.NET Core Span
      │
      └── [ProcessPayment Operation] ──► Custom Business Span (ActivitySource)
              │
              ├── [SQL: SELECT balance]──► Automatic Npgsql/SqlClient Span
              │
              └── [HTTP: POST /stripe]  ──► Automatic HttpClient Span
```

Manual spans should describe meaningful business boundaries and domain transactions. Let automatic instrumentation capture the underlying HTTP calls, database queries, and cache lookups.

---

## 7. Influencing and Modifying Traces

Telemetry must be shaped, sanitized, and enriched as it flows through the architecture:

```text
Application Logic ──► In-Process SDK Processors ──► Collector Pipelines ──► Backend
```

### 1. Application-Level Enrichment

The running application has direct access to execution context and domain variables. Use the application level to attach business metadata directly to the current span:

```csharp
// Enriching the active span from anywhere within the call hierarchy
Activity.Current?.SetTag("tenant.id", currentTenant.Id);
Activity.Current?.SetTag("payment.provider", "Stripe");
Activity.Current?.SetTag("feature_flag.checkout_v2", true);
```

Common attributes for application enrichment:
- Multi-tenant tenant IDs
- Customer account tiers (e.g., `enterprise`, `free`)
- High-level business operations
- Feature flag variants

### 2. In-Process SDK Processors

Within the application process, the OpenTelemetry SDK allows you to hook into the span lifecycle via `BaseProcessor<Activity>` or `CompositeProcessor`. 

This is the equivalent of classic Application Insights `ITelemetryInitializer` or `ITelemetryProcessor` hooks:

```csharp
public class CustomEnrichingProcessor : BaseProcessor<Activity>
{
    public override void OnEnd(Activity activity)
    {
        // Read async thread context, environment, or system states
        activity.SetTag("process.thread_id", Environment.CurrentManagedThreadId);
        
        // Strip sensitive data before it hits the SDK's internal queue
        if (activity.GetTagItem("user.email") != null)
        {
            activity.SetTag("user.email", "REDACTED");
        }
    }
}
```

SDK-level processors run synchronously on span execution threads or worker batch threads. Keep their logic non-blocking and minimal to prevent degrading application performance.

### 3. Collector-Level Transformation

Infrastructure-wide metadata and cross-cutting governance belong in the Collector. Instead of writing custom configuration inside 50 different microservices to discover cloud provider regions or Kubernetes namespaces, let the Collector add this information centrally:

```yaml
# OpenTelemetry Collector configuration
processors:
  transform:
    error_mode: ignore
    trace_statements:
      - context: span
        statements:
          - set(attributes["deployment.environment"], "production")
          - set(attributes["cloud.region"], "westeurope")
          - set(attributes["service.namespace"], "payments-core")
```

---

## 8. Trace Relationships and Asynchronous Systems

Simple synchronous RPC operations map to clear hierarchical parent-child trees:

```text
Client HTTP Request (TraceId: T1, SpanId: S1)
   │
   ├── OrderValidation (TraceId: T1, SpanId: S2, Parent: S1)
   │
   └── PaymentProcessing (TraceId: T1, SpanId: S3, Parent: S1)
          │
          └── Gateway Call (TraceId: T1, SpanId: S4, Parent: S3)
```

### Distributed Asynchronous Messaging and Span Links

Asynchronous messaging (e.g., Kafka, RabbitMQ, Azure Service Bus) breaks pure parent-child hierarchies. 

Consider a worker that consumes a message published minutes ago, or a batch handler that pulls 50 messages from a queue at once and processes them in a single database transaction. If the consumer span makes itself a direct child of the publishing span, the trace duration appears hours long, or a single consumer execution gets tangled with 50 unrelated parent traces.

OpenTelemetry handles this through **Span Links**. A span link declares a causal relationship between independent traces without nesting their timelines:

```text
[Trace A: Web API]
HTTP POST /order
   │
   └── Publish "OrderCreated" Message
             \
              \ (Trace A context serialized into message headers)
               \
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                \
                 ▼
[Trace B: Async Background Worker]
Consume Batch From Queue
   │
   ├── Process Message 1 ──► [Link: Trace A Span]
   │
   └── Process Message 2 ──► [Link: Trace X Span]
```

Links preserve causal context across asynchronous boundaries while keeping the execution traces cleanly isolated.

---

## 9. Sampling Strategies: Head vs. Tail Sampling

High-throughput systems generating hundreds of thousands of transactions per second cannot afford to store, index, and analyze every single trace. Sampling controls costs while preserving visibility into system behavior.

```text
Sampling Decision Trade-off:
-------------------------------------------------------------------------
Strategy    Where It Runs     Cost/Overhead     Diagnostic Precision
-------------------------------------------------------------------------
Head        In-Process SDK    Very Low          Low (Drops rare errors)
Tail        Collector Cluster High (Buffers RAM) Maximum (Keeps anomalies)
```

### Head Sampling

Head sampling makes the sampling decision at the very beginning of a trace—usually when the root span is initiated at the ingress edge or API Gateway:

```text
Incoming Request
      ↓
Sampling Algorithm (e.g., 5% random ratio)
      ├── Dropped (95%) ──► No child spans exported
      └── Kept (5%)     ──► traceparent flag set to 01 (Sampled); all downstreams export
```

- **Pros**: Inexpensive to run. Once the root span drops the trace, child services immediately read the unsampled flag from `traceparent` and bypass span generation entirely, saving CPU and network bandwidth across the entire fleet.
- **Cons**: Blind to the future. If a sampled-out request encounters an unhandled database timeout or HTTP 500 error 3 seconds later, that diagnostic information is lost forever.

### Tail Sampling

Tail sampling defers the retention decision until the distributed trace has finished executing. 

Spans are streamed to an intermediate OpenTelemetry Collector layer that buffers them in memory for a short evaluation window (e.g., 10 to 30 seconds). The Collector reconstructs the trace DAG and evaluates the entire sequence against dynamic rules:

```text
Spans Arrive at Collector ──► Buffered in In-Memory Trace Cache
                                      │
                         Trace Complete or Window Expires?
                                      │
                         Evaluate Rule Hierarchy:
                         ├── Did any span return HTTP >= 500?    ──► KEEP (100%)
                         ├── Did total trace duration exceed 2s? ──► KEEP (100%)
                         ├── Does span contain error = true?     ──► KEEP (100%)
                         └── Routine HTTP 200 OK operations      ──► SAMPLE (1%)
```

#### The Tail Sampling Routing Requirement
Tail sampling requires that **all spans belonging to the same `TraceId` arrive at the exact same Collector instance**. Because microservices emit spans independently over the network, you cannot place a standard round-robin load balancer in front of your tail-sampling Collectors. 

You must deploy a two-tier Collector architecture using the OpenTelemetry `loadbalancingexporter`. The first tier computes a consistent hash of the incoming `TraceId` and routes the span to a deterministic second-tier Collector node:

```text
Microservices Fleet
         ↓ (OTLP)
Tier 1: Gateway Collectors (Running loadbalancingexporter)
         │
         │ (Consistent hash on TraceId)
         ├── TraceId ending in 0-3 ──► Tier 2 Collector Instance A
         ├── TraceId ending in 4-7 ──► Tier 2 Collector Instance B
         └── TraceId ending in 8-f ──► Tier 2 Collector Instance C
                                       (Evaluates tail_sampling rules on complete DAGs)
```

---

## 10. Metrics: OpenTelemetry vs. Prometheus

OpenTelemetry is an instrumentation, data model, and transport framework. Prometheus is a time-series database, metrics scraper, PromQL query engine, and alerting manager. 

OpenTelemetry does not replace Prometheus. In production, you typically combine them:

```text
OpenTelemetry (Instrumentation & Collection) + Prometheus/Mimir (Storage & Querying)
```

### The Legacy Model: Prometheus-Net

Historically, .NET applications instrumented code using vendor-specific libraries like `prometheus-net`:

```csharp
// Legacy proprietary approach
using Prometheus;

public class OrderMetricsLegacy
{
    private static readonly Counter OrdersCreated = Metrics
        .CreateCounter("orders_created_total", "Number of created orders", 
            new CounterConfiguration { LabelNames = new[] { "status" } });

    public void RecordOrder(string status)
    {
        OrdersCreated.WithLabels(status).Inc();
    }
}
```

This required the application to expose an HTTP endpoint (`/metrics`) and tightly coupled application assemblies to the Prometheus data model.

### The Modern Model: System.Diagnostics.Metrics

Modern architectures instrument against native runtime meters:

```csharp
// Modern decoupled approach
using System.Diagnostics.Metrics;

public class OrderMetricsModern
{
    private static readonly Meter OrderMeter = new("Company.Orders.Service", "1.0.0");
    
    private static readonly Counter<long> OrdersCreated = OrderMeter
        .CreateCounter<long>("orders.created", unit: "{orders}", description: "Total orders created");

    public void RecordOrder(string status)
    {
        OrdersCreated.Add(1, new KeyValuePair<string, object?>("order.status", status));
    }
}
```

The application is decoupled from the storage backend. Telemetry collection can be routed in either direction via configuration:

```text
Option A: Scrape Model
System.Diagnostics.Metrics ──► OTel Prometheus Exporter ──► App: /metrics ◄── Prometheus Scrape

Option B: Push Model (OTLP)
System.Diagnostics.Metrics ──► OTel OTLP Exporter ──► OTel Collector ──► Grafana Mimir
```

---

## 11. Metrics Cardinality Governance

Cardinality refers to the number of unique combinations of metric attribute values (dimensions) that exist within a time-series database.

Every unique permutation of metric dimensions creates a distinct, stateful time-series line that consumes permanent memory in the indexing engine (Prometheus TSDB, Cortex, or Mimir).

```text
Bounded, Low Cardinality (Safe for Metrics):
http.server.request.duration {
    environment = "prod",          // ~3 values (dev, stage, prod)
    region      = "us-east-1",     // ~10 values
    http_method = "POST",          // ~5 values
    status_code = "200"            // ~20 values
}
// Permutations: 3 * 10 * 5 * 20 = 3,000 active time-series lines (Trivial overhead)

Unbounded, High Cardinality (Fatal to Metrics):
http.server.request.duration {
    user_id     = "usr_98a7fbc2",  // 1,000,000 unique values
    order_id    = "ord_20241019_1" // 50,000,000 unique values
}
// Permutations: Hundreds of millions of concurrent time series.
// Result: Exploded inverted indexes, severe memory saturation, and TSDB crashes.
```

Follow this rule when assigning attributes:

- **Low Cardinality $\rightarrow$ Metrics**: Use for dimensions that classify macro system behavior (`http.status_code`, `environment`, `deployment.region`, `error.type`). These support real-time dashboards and alerting aggregations.
- **High Cardinality $\rightarrow$ Traces and Logs**: High-cardinality values (`user_id`, `order_id`, `session_token`, `ip_address`) belong exclusively on Spans as Span Attributes or within structured log payloads. Traces and logs are indexed differently than time-series metrics and can handle arbitrary uniqueness without resource exhaustion.

---

## 12. Logs and Correlated Telemetry

OpenTelemetry brings structured logging into alignment with traces and metrics. Instead of treating logs as isolated strings printed to a screen, OpenTelemetry structures them as structured records containing:

- Timestamp
- Observed Timestamp
- Severity (LogLevel)
- Body (The log message)
- Attributes (Structured parameters)
- Contextual Identifiers: `TraceId`, `SpanId`, `TraceFlags`

```text
Distributed Trace: TraceId = a18f4...
 │
 ├── Span: CheckoutController (SpanId = 41a9e...)
 │
 └── Span: ProcessPayment (SpanId = 88c2b...)
        │
        └── Emitted Log: "Payment processor returned gateway error"
            ├── Severity = ERROR
            ├── TraceId  = a18f4... (Automated injection)
            ├── SpanId   = 88c2b... (Automated injection)
            └── Attributes = { gateway.error_code: 503, provider: "Stripe" }
```

This correlation changes how you troubleshoot. Clicking a log line in an observability UI like Grafana or Azure Monitor can instantly open the exact trace waterfall and span that generated it. Similarly, looking at a slow span allows you to view only the logs generated within that specific sub-operation.

---

## 13. Direct OTLP Logs and the In-Process Failure Trap

Modern application frameworks allow configuring an OTLP log exporter directly within the application's logging pipeline:

```csharp
// Direct in-process OTLP logging setup in .NET
builder.Logging.AddOpenTelemetry(logging =>
{
    logging.AddOtlpExporter(opt => opt.Endpoint = new Uri("http://otel-collector:4317"));
});
```

While clean and easy to configure, **direct in-process OTLP log export should not be relied upon as a durable logging pipeline**.

### The Vulnerability

To maintain application throughput, logging SDKs queue log records in an in-memory ring buffer, relying on a background thread to batch and transmit them over HTTP or gRPC to the Collector:

```text
Application Process
┌────────────────────────────────────────────────────────┐
│ ILogger.Log() ──► In-Memory Telemetry Queue [■ ■ ■ ■ ] │
└──────────────────────────┬─────────────────────────────┘
                           │ Network Flush (Async Thread)
                           ▼
                    OTel Collector
```

If the application crashes cleanly, runtime shutdown hooks can attempt to flush the internal buffer. However, modern production failure modes are rarely clean:

- The Linux kernel invokes the Out-Of-Memory Killer (`OOMKilled`, exit code 137).
- The platform orchestrator sends an uncatchable `SIGKILL`.
- The application suffers a low-level runtime crash (e.g., stack overflow or segmentation fault).
- The underlying container host loses power or disconnects from the network.

In every one of these scenarios, **the process terminates instantly. The in-memory buffer is wiped out, and the logs describing the critical failure are lost before they reach the network.**

---

## 14. Kubernetes Container Logging Architecture

Kubernetes provides native, crash-durable logging based on the UNIX standard streams (`stdout` and `stderr`).

Applications do not write logs to arbitrary files inside their container overlay file system. Instead, they format structured logs and write them to standard output:

```text
.NET Application (ILogger Console Formatter)
      ↓
Writes structured JSON to stdout
      ↓
Container Runtime (containerd or CRI-O)
      ↓
Streams captured and written to Host Disk:
/var/log/pods/<namespace>_<pod-name>_<pod-uid>/<container-name>/<retry-count>.log
```

This decoupling provides durability:

```text
Application Process
      ↓
stdout (Pipe buffer managed by Linux kernel)
      ↓
Node Disk (/var/log/pods/...)
      X [Application crashes / OOMKilled]
```

Because the write happens via the operating system's standard stream pipes, the container runtime commits the log line to the node's local filesystem almost instantaneously. 

When the application process terminates abruptly, the final log entry—including the stack trace or fatal memory condition—is already written to disk.

---

## 15. The OpenTelemetry Collector for Kubernetes Logs

To capture container logs safely, deploy the OpenTelemetry Collector as a **DaemonSet** (one Collector instance per Kubernetes worker node).

```text
Node 1 Worker
┌────────────────────────────────────────────────────────┐
│ Pod A ──stdout──┐                                      │
│ Pod B ──stdout──┼──► containerd ──► /var/log/pods/*.log│
│ Pod C ──stdout──┘                         │            │
│                                           ▼            │
│                 OpenTelemetry Collector (DaemonSet)    │
│                 ┌────────────────────────────────────┐ │
│                 │ Receiver:   filelog                │ │
│                 │ Processor:  k8sattributes, batch   │ │
│                 │ Exporter:   otlp / loki / elastic  │ │
│                 └─────────────────┬──────────────────┘ │
└───────────────────────────────────┼────────────────────┘
                                    ▼
                         Central Observability
```

The Collector uses the `filelog` receiver to discover and tail container logs from `/var/log/pods/`:

```yaml
receivers:
  filelog:
    include: [/var/log/pods/*/*/*.log]
    exclude: [/var/log/pods/opentelemetry_*/*/*.log] # Don't ingest Collector logs
    start_at: end
    fingerprint:
      strategy: device_and_inode
    processors:
      # Parse CRI-formatted logs into discrete timestamps, streams, and payloads
      - type: container
        format: cri
```

This configuration isolates responsibilities:
1. **The Application** writes structured log payloads to `stdout` with low latency and near-zero memory footprint.
2. **The Container Runtime** ensures crash-durable writes to node storage.
3. **The Collector DaemonSet** reads the log files, enriches them with Kubernetes cluster metadata via the `k8sattributes` processor, and batches them downstream.

---

## 16. Log Durability Boundaries

Telemetry architectures navigate distinct failure boundaries:

```text
Level 1: Application Crash
  App Process Dies ──► Logs already safe in /var/log/pods on host node.

Level 2: Collector Process Crash
  Collector Dies   ──► filelog receiver checkpoints file read offsets on disk.
                       Unsent data buffered via Collector persistent disk queues.

Level 3: Catastrophic Host Node Failure
  Physical Node Dies ──► Unshipped local logs on node disk are lost.
```

### Surviving Collector Outages

If the Collector DaemonSet restarts or loses connection to downstream storage, the `filelog` receiver saves its read pointers (checkpoints) to host-mounted disk paths. 

Once restored, it resumes reading from the exact byte offset it left off, preventing data loss.

For downstream export durability, configure the Collector's **persistent storage extension** for outbound queues:

```yaml
extensions:
  file_storage:
    directory: /var/lib/otelcol/file_storage

exporters:
  otlp:
    endpoint: "tempo:4317"
    sending_queue:
      enabled: true
      storage: file_storage # Disk-backed queue buffers data during network drops
```

### Surviving Node Loss

If an entire hypervisor, VM instance, or bare-metal server experiences catastrophic failure before the Collector tails the local disk, un-exported logs are lost with that hardware. 

If your compliance or audit requirements mandate absolute zero loss even during full machine destruction, you must treat your logs as high-durability audit records. In that case, bypass local logging and write events directly into a multi-AZ distributed write-ahead log like Apache Kafka or AWS Kinesis. 

For 99.9% of engineering systems, however, the combination of container runtime `stdout` + node disk + Collector DaemonSet strikes the right balance between performance, operational simplicity, and durability.

---

## 17. Architecture: Logging Sidecars vs. Node-Level Collectors

Teams often consider deploying an OpenTelemetry Collector as a sidecar container inside every single Kubernetes pod.

```text
Sidecar Architecture:
Pod
├── Application Container
└── OTel Collector Sidecar
```

While sidecars provide strict isolation, they are usually the wrong approach for logging.

```text
Comparison: Logging Sidecar vs. Node DaemonSet
-------------------------------------------------------------------------
Vector               Sidecar Model               DaemonSet Model
-------------------------------------------------------------------------
Memory Footprint     Multiplied by Pod Count     Fixed per Node (~1 instance)
Log Durability       Ties collector to app pod   Decoupled from pod lifecycle
Config Maintenance   High (Pod specs update)     Low (Cluster-wide config)
Network Connections  High (Every pod connects)   Low (Batched connections)
Use Case             Custom per-pod transforms   Standard production systems
```

Kubernetes already aggregates `stdout` across all local pods on the host node. Running a DaemonSet leverages this architecture, handling 50 pods on a single node through one Collector process with a shared memory budget.

Reserve sidecars for specialized scenarios, such as strict mTLS boundaries across zero-trust network zones or dedicated in-memory processing for isolated, high-volume ingest apps.

---

## 18. Legacy .NET: prometheus-net

Historically, .NET microservices depended directly on `prometheus-net`:

```text
Application Process
┌────────────────────────────────────────────────────────┐
│ [Domain Logic] ──► prometheus-net ──► /metrics Handler │
└───────────────────────────────────────────────▲────────┘
                                                │ Scrape
                                         Prometheus Server
```

This pattern worked, but tightly coupled the software to Prometheus:
- The application binary held a concrete dependency on third-party metric schemas.
- It required opening an internal HTTP port within the application container to handle scrapes.
- It could not ship those same metrics to other cloud-native formats without maintaining parallel instrumentation suites.

Instrumenting with `System.Diagnostics.Metrics` removes this coupling, allowing you to switch between Prometheus scrapes and pushed OTLP metrics through configuration changes alone.

---

## 19. Legacy .NET: The Classic Application Insights SDK

Before OpenTelemetry, Microsoft's observability model in .NET revolved around the `Microsoft.ApplicationInsights` SDK:

```text
Application Logic
      ↓
TelemetryClient
      ├── TrackTrace()
      ├── TrackMetric()
      ├── TrackException()
      └── StartOperation<RequestTelemetry>()
      ↓
ITelemetryInitializer (Enrichment)
      ↓
ITelemetryProcessor (Filtering / Sampling)
      ↓
Channel Ingestion Queue (In-Process Memory)
      ↓
Application Insights Service (Azure Cloud)
```

The classic SDK provided a comprehensive, closed ecosystem. It handled correlation, automatic tracking of SQL and HTTP operations, and outbound delivery. 

However, it locked application code to Azure APIs. Moving to another platform meant rewriting all custom instrumentation across the codebase.

---

## 20. Modern Architecture: OpenTelemetry with Application Insights

Azure Application Insights now supports OpenTelemetry as a first-class ingestion model. Microsoft provides the `Azure.Monitor.OpenTelemetry.Exporter` to bridge OTel pipelines directly to Azure Monitor:

```text
Modern Architecture:
Application Instrumentations (System.Diagnostics, ILogger)
      ↓
OpenTelemetry .NET SDK
      ↓
Azure Monitor OpenTelemetry Exporter (Or OTel Collector)
      ↓
Azure Application Insights / Azure Monitor Log Analytics
```

This changes the division of responsibilities:
- **OpenTelemetry** owns instrumentation APIs, data models, context propagation, and wire transport.
- **Application Insights** acts purely as a downstream backend, query interface (Kusto / KQL), and analytical UI.

Your developers write code against vendor-neutral .NET diagnostic APIs. If the organization later decides to migrate from Azure Monitor to a self-hosted Grafana stack, you change exporter dependencies without touching your business logic.

---

## 21. Mapping Application Insights to OpenTelemetry

Engineers familiar with the Application Insights SDK can map its concepts directly to OpenTelemetry and modern .NET primitives:

| Classic Application Insights (.NET) | Modern OpenTelemetry / .NET BCL Equivalent | Architectural Purpose |
| :--- | :--- | :--- |
| `TelemetryClient.StartOperation<RequestTelemetry>()` | `ActivitySource.StartActivity(..., ActivityKind.Server)` | Initiates a server-side boundary execution (root or child span) |
| `TelemetryClient.StartOperation<DependencyTelemetry>()` | `ActivitySource.StartActivity(..., ActivityKind.Client)` | Documents an outbound client call (HTTP, SQL, RPC) |
| `RequestTelemetry` | Server Span (`ActivityKind.Server`) | Represents incoming execution requests |
| `DependencyTelemetry` | Client / Producer / Consumer Span | Represents outgoing dependency calls |
| `telemetry.Context.Operation.Id` | `Activity.TraceId` (W3C standard) | Identifies the distributed trace execution |
| `telemetry.Context.Operation.ParentId` | `Activity.ParentSpanId` | Identifies the caller span |
| `telemetry.Properties["key"] = val` | `Activity.SetTag("key", val)` | Attaches metadata attributes to the span |
| `ITelemetryInitializer` | `BaseProcessor<Activity>.OnEnd()` or SDK Processors | In-process global enrichment hook run on telemetry generation |
| `ITelemetryProcessor` | OpenTelemetry Processor / Collector Processor | In-process or pipeline filtering, batching, and routing hook |

---

## 22. OpenTelemetry and Prometheus Coexistence

OpenTelemetry does not eliminate `/metrics` endpoints.

The two systems work together based on your deployment requirements:

```text
Pattern 1: Application-Level Prometheus Exporter
App (System.Diagnostics.Metrics) ──► OTel Prometheus Exporter ──► App: /metrics ◄── Prometheus

Pattern 2: Collector-Mediated Pull Architecture
App ──► OTLP (gRPC) ──► OTel Collector ──► Collector: /metrics ◄── Prometheus

Pattern 3: Collector-Mediated Push Architecture
App ──► OTLP (gRPC) ──► OTel Collector ──► OTLP / Remote Write ──► Grafana Mimir
```

When Prometheus scrapes an endpoint generated by OpenTelemetry, the Prometheus server cannot distinguish it from a native Prometheus library. 

OpenTelemetry automatically handles the translation between OTel metric types (like Histograms and Monotonic Counters) and the corresponding Prometheus exposition formats.

---

## 23. OpenTelemetry and the Grafana Ecosystem

Grafana Labs designs its observability stack around distinct, specialized storage engines tied together by the Grafana visualization UI:

```text
Grafana Stack Components:
├── Grafana Tempo     ──► Distributed Tracing (OTLP native)
├── Grafana Mimir     ──► Metrics (Prometheus / OTLP native)
├── Grafana Loki      ──► Logs (Structured streams)
└── Grafana Pyroscope ──► Continuous Profiling
```

The OpenTelemetry Collector acts as the universal ingestion gateway for this entire stack:

```text
                         Application Workload
                                  ↓ OTLP
                        OpenTelemetry Collector
                                  │
         ┌────────────────────────┼────────────────────────┐
         │ (traces)               │ (metrics)              │ (logs)
         ▼                        ▼                        ▼
   Grafana Tempo            Grafana Mimir             Grafana Loki
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  ▼
                     Unified Grafana Dashboards
```

### Note on Grafana Alloy
Grafana provides **Grafana Alloy**, an observability distribution based on the OpenTelemetry Collector codebase. It combines standard upstream OpenTelemetry components with native integrations for Prometheus discovery and Grafana Loki formatting. 

You can use either upstream OpenTelemetry Collector or Grafana Alloy; both speak standard OTLP and are compatible with the pipeline architecture described here.

---

## 24. OpenTelemetry and Elastic

Elasticsearch (and the Elastic Observability platform) ingests OpenTelemetry data directly. 

Elasticsearch stores traces, logs, and metrics as structured documents within Elasticsearch indices:

```text
Application ──► OTLP ──► OTel Collector ──► Elasticsearch / Elastic Cloud ──► Kibana
```

OpenTelemetry normalizes your telemetry to semantic conventions. When Elastic receives these payloads via OTLP, it maps those conventions directly into the Elastic Common Schema (ECS). 

This allows Kibana's APM views, trace waterfalls, and machine learning anomaly detection to work without proprietary Elastic agent software running inside your application processes.

---

## 25. The Reality of Vendor Neutrality

Vendor neutrality is one of the strongest selling points for OpenTelemetry:

```text
Today's Target:
Application ──► OTel Collector ──► Azure Monitor

Future Migration:
Application ──► OTel Collector ──► Grafana Cloud / OpenSearch
```

Switching backends becomes a DevOps configuration task in a Collector pipeline instead of an engineering sprint rewriting telemetry wrappers across dozens of microservices.

### Where Neutrality Ends

OpenTelemetry standardizes telemetry **generation, data models, and transport**. It does **not** make downstream observability backends interchangeable:

- **Query Dialects**: KQL (Azure Monitor), PromQL (Prometheus/Mimir), LogQL (Loki), TraceQL (Tempo), and Lucene/ES|QL (Elasticsearch) share no common standards. Migrating backends requires re-authoring dashboards, alert configurations, and automated runbooks.
- **Cost Architectures**: Some platforms charge per ingested gigabyte (Datadog, Azure Log Analytics), others charge per active time-series metric series (Grafana Cloud, AWS CloudWatch), and self-hosted clusters charge through raw infrastructure footprint. The structure of your telemetry impacts your cloud bill differently depending on the backend.
- **Proprietary Features**: Specialized application performance monitoring features—like automated distributed profiling, code-level execution analysis, and dynamic instrumentation—remain proprietary to individual commercial vendors.

OpenTelemetry eliminates lock-in at the application code layer. It lets you change your data destinations without paying the tax of re-instrumenting your software.

---

## 26. Security, PII, and Data Scrubbing

Telemetry frequently captures sensitive data by default:
- Authorization headers containing Bearer tokens
- Cookies containing session IDs
- URLs containing plaintext query parameters (`?token=secret&email=test@example.com`)
- Database statements containing un-parameterized SQL values
- Unchecked application exceptions printing user passwords or secrets

### The Layered Sanitization Pattern

Sanitizing sensitive data should happen at multiple layers in your telemetry architecture:

```text
Sanitization Layers:
1. Application Layer: Parameterize SQL queries; avoid logging raw inputs.
2. In-Process SDK:    Run processors to scrub known keys before serializing to network.
3. Collector Layer:   Apply cluster-wide regex masking to catch leaked PII globally.
```

The OpenTelemetry Collector provides a central boundary to enforce security and compliance policies:

```yaml
processors:
  transform:
    error_mode: ignore
    trace_statements:
      - context: span
        statements:
          # Scrub authorization headers
          - set(attributes["http.request.header.authorization"], "REDACTED")
          # Regex replace email patterns inside span attributes
          - replace_pattern(attributes["customer.email"], ".*@.*", "REDACTED")
          
  redaction:
    allow_all_keys: false
    allowed_keys: [http.method, http.status_code, db.system]
    blocked_values:
      - "(?i)bearer [a-z0-9-_.]+"
      - "[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}" # Credit card mask
```

This prevents sensitive data from leaving your corporate network boundary, ensuring compliance with data privacy regulations (such as GDPR, HIPAA, and PCI-DSS) without relying exclusively on every individual developer remembering to sanitize local variables.

---

## 27. Recommended Production Architecture

For containerized cloud-native environments (such as Kubernetes), deploy a dual-path architecture that separates telemetry by its operational durability requirements:

```text
                          Containerized Application (.NET / Polyglot)
                         /                                           \
                        /                                             \
       Traces & Metrics (In-Memory Queue)                   Logs (Structured JSON)
                     OTLP                                           ILogger
                      ↓                                               ↓
               Cluster Network                                  stdout / stderr
                      ↓                                               ↓
                      │                                 Container Runtime (containerd)
                      │                                               ↓
                      │                                Node File Storage (/var/log/pods/)
                      │                                               ↓
                      └───────────────────────┬───────────────────────┘
                                              ↓
                             OpenTelemetry Collector (DaemonSet)
                      ┌───────────────────────────────────────────────┐
                      │ 1. Receivers:                                 │
                      │    - otlp (gRPC :4317 / HTTP :4318)           │
                      │    - filelog (/var/log/pods/*/*.log)          │
                      │ 2. Processors:                                │
                      │    - memory_limiter (must be first)           │
                      │    - k8sattributes (enrich pod/namespace)     │
                      │    - transform (mask PII / scrub attributes)  │
                      │    - batch (pack and compress payloads)       │
                      │ 3. Exporters:                                 │
                      │    - otlp (Tempo / Loki / Mimir)              │
                      │    - azuremonitor (App Insights)              │
                      │    - elasticsearch                            │
                      └───────────────────────┬───────────────────────┘
                                              │
                      ┌───────────────────────┼───────────────────────┐
                      ▼                       ▼                       ▼
                Azure Monitor           Grafana Stack           Elasticsearch /
            (Application Insights)   (Tempo / Mimir / Loki)     OpenSearch Cluster
```

### Why This Works
1. **Application Decoupling**: Applications depend only on native diagnostics (`System.Diagnostics`, `slog`, `tracing`, `ILogger`). They do not load vendor SDKs into process memory.
2. **Crash Durability**: Traces and metrics are streamed via OTLP; logs are emitted to `stdout`. If a container process is terminated by an `OOMKilled` or `SIGKILL` event, the log documenting the crash is already written to the host filesystem and safely collected by the DaemonSet.
3. **Operational Simplicity**: Upgrading an exporter, fixing an authentication token, or adding a target backend is handled entirely through the Collector configuration without rebuilding and redeploying application containers.
4. **Metadata Parity**: The Collector enriches traces, metrics, and logs with matching infrastructure labels (`k8s.pod.name`, `k8s.namespace.name`, `deployment.environment`), ensuring all three signals correlate cleanly in downstream query engines.

---

## 28. Main Takeaways

- **OpenTelemetry is an interoperability framework, not a backend.** It provides standardized APIs, SDKs, semantic schemas, and pipelines to generate and route telemetry. Storage, indexing, visualization, and alerting belong to downstream backends.
- **The OpenTelemetry Collector is your operational safety valve.** It offloads batching, compression, retry logic, credential management, PII redaction, and tail sampling from your application processes.
- **Separate traces and metrics from logs in Kubernetes.** Stream low-latency traces and metrics over OTLP directly to the Collector. Emit logs as structured JSON to `stdout`/`stderr` to let the container runtime write them to disk, ensuring crash events survive unhandled process termination.
- **Govern metric cardinality aggressively.** Keep metric attributes bounded and low-cardinality. Push dynamic identifiers, user IDs, and unique transaction hashes to traces and logs.
- **Modern runtimes integrate natively with OpenTelemetry.** In .NET, use `System.Diagnostics.ActivitySource`, `System.Diagnostics.Metrics.Meter`, and `ILogger`. Avoid proprietary vendor SDKs inside application domain code.

---

## Related Knowledge Base References

- [[Standardizing Service Infrastructure with Reusable Blocks]]: Incorporating standardized OpenTelemetry pipelines into platform service templates.
- [[Service-to-Service Communication - How Service A Should Call Service B]]: Managing W3C context propagation across distributed microservices.
- [[Propagating User Context Between Services]]: Transporting distributed tracing IDs and baggage across synchronous and asynchronous boundaries.
- [[Embedding LLMs in Runtime Decision Paths and Operational Telemetry]]: Consuming structured traces and logs as diagnostic input for automated operations.
