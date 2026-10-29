---
title: "Instrumenting .NET Applications with OpenTelemetry"
tags:
  - opentelemetry
  - dotnet
  - observability
  - distributed-tracing
  - metrics
aliases:
  - "OpenTelemetry Instrumentation in .NET"
  - "ActivitySource and Metrics Instrumentation"
  - "Migrating Application Insights Instrumentation to OpenTelemetry"
---

An order request enters an API, calls a payment provider, and publishes a message. Useful instrumentation must describe that operation, connect its technical work, and expose aggregate behavior without turning every order identifier into a new metric series.

.NET application code has access to business meaning through its tracing, logging, and metric primitives. The SDK connects that instrumentation to exporters and processing. A Collector can apply infrastructure-wide transformations, while the backend supplies storage, queries, and visualization. The boundary determines where to add an attribute and where to configure an export destination.

The sections below cover custom and automatic spans, enrichment, asynchronous relationships, metrics, logs, and existing Application Insights integrations. [[OpenTelemetry — Architecture, Signals, and Collector]] explains the surrounding pipeline. [[Reliable Kubernetes Logging with OpenTelemetry]] covers the separate durability question for log delivery.

## OpenTelemetry in .NET

Modern .NET already contains primitives that map naturally to OpenTelemetry.

The most important are:

```text
System.Diagnostics.Activity
System.Diagnostics.ActivitySource
System.Diagnostics.Metrics
Microsoft.Extensions.Logging.ILogger
```

A useful mapping is:

```text
Activity        ≈ OpenTelemetry Span
ActivitySource  ≈ span producer
Meter           ≈ metrics producer
ILogger         ≈ logs
```

---

### Tracing in .NET

A custom span can be created using `ActivitySource`.

```csharp
private static readonly ActivitySource Source =
    new("Orders");

using var activity = Source.StartActivity("CreateOrder");

activity?.SetTag("order.id", order.Id);
activity?.SetTag("customer.type", customer.Type);
```

The code does not need to know whether the final backend will be:

```text
Azure Application Insights
Tempo
Jaeger
Elastic
Datadog
```

That decision can be made later.

---

### Automatic Instrumentation

Many spans can be created automatically.

For example:

```text
POST /payments                  automatic ASP.NET span
    │
    └── ProcessPayment          custom span
            │
            ├── SQL request     automatic instrumentation
            │
            └── HTTP request    automatic HttpClient span
```

Therefore we normally do not need to manually instrument every technical operation.

Manual spans are especially useful when they describe meaningful business operations.

---

## Influencing and Modifying Traces

Moving from classic Application Insights instrumentation to OpenTelemetry does not mean losing control over traces.

There are several levels where telemetry can be modified.

```text
application
    ↓
OpenTelemetry SDK
    ↓
Collector
    ↓
backend
```

### Application-level enrichment

The application has the best understanding of business information.

Example:

```csharp
Activity.Current?.SetTag("tenant.id", tenantId);
Activity.Current?.SetTag("order.id", orderId);
Activity.Current?.SetTag(
    "business.operation",
    "CreateOrder");
```

This is useful for information such as:

```text
tenant
order
payment type
business operation
customer category
```

---

### SDK Processors

Telemetry can also be intercepted through OpenTelemetry processors.

Conceptually:

```text
span generated
    ↓
processor
    ↓
exporter
```

This resembles the old Application Insights extensibility pipeline.

In .NET, custom processors inherit from `BaseProcessor<Activity>` and implement `OnEnd(Activity activity)`. These run synchronously on execution or batch dispatch threads, making them ideal for stripping known sensitive keys or adding thread-level diagnostic tags before data leaves memory.

---

### Collector-level transformation

Infrastructure-wide modifications often belong in the Collector.

For example:

```text
deployment.environment = production
cluster = warsaw-prod
region = westeurope
team = payments
```

This avoids repeating infrastructure configuration inside every application.

---

## Trace Relationships and Async Systems

Simple synchronous traces form parent-child hierarchies:

```text
HTTP request
   │
   ├── ValidateOrder
   │
   ├── ChargePayment
   │      └── HTTP provider
   │
   └── SaveOrder
```

Distributed asynchronous systems are more complicated.

A message handler is not necessarily simply a nested child operation of the request that originally produced the message.

OpenTelemetry supports span links for this purpose.

Conceptually:

```text
Trace A

HTTP request
   ↓
publish message
        \
         \ link
          \
Trace B   message handler
```

This provides a better representation of asynchronous workflows.

In asynchronous message processing (such as Kafka, RabbitMQ, or Azure Service Bus), making a consumer span a direct child of the publishing span introduces serious operational confusion. A message might sit in a queue for minutes or hours before processing; representing it as a parent-child span stretches the trace duration artificially and misrepresents system latency. When a worker pulls a batch of 50 messages, span links allow the consumer to reference all 50 distinct upstream traces without creating an unreadable, interleaved trace hierarchy.

---

## Metrics

OpenTelemetry metrics should not be confused with Prometheus.

OpenTelemetry provides:

```text
instrumentation
metric model
collection
transport
```

Prometheus provides:

```text
metric collection
time-series storage
PromQL
rules
alerting
```

Therefore the normal relationship is often:

```text
OpenTelemetry + Prometheus
```

rather than:

```text
OpenTelemetry vs Prometheus
```

---

### Traditional Prometheus Model

Historically, .NET applications frequently used libraries such as `prometheus-net`.

```text
.NET
 ↓
prometheus-net
 ↓
/metrics
 ↓
Prometheus
 ↓
Grafana
```

The application was directly instrumented using Prometheus concepts.

For example:

```csharp
var counter = Metrics.CreateCounter(
    "orders_created_total",
    "Number of created orders");

counter.Inc();
```

---

### Modern .NET Metrics

Modern .NET provides `System.Diagnostics.Metrics`.

Example:

```csharp
private static readonly Meter Meter =
    new("Payments");

private static readonly Counter<long> Payments =
    Meter.CreateCounter<long>("payments.completed");

Payments.Add(1);
```

OpenTelemetry can collect those measurements.

The final destination can still be Prometheus:

```text
.NET Meter
    ↓
OpenTelemetry
    ↓
Prometheus exporter
    ↓
/metrics
    ↓
Prometheus
```

Or metrics can be pushed via OTLP:

```text
.NET
 ↓
OTLP
 ↓
Collector
 ↓
metrics backend
```

---

## Metrics Cardinality

Metrics require special care regarding attributes.

For example:

```text
payment.count{
    payment_type="card"
}
```

has low cardinality.

But:

```text
payment.count{
    order_id="812938129"
}
```

may create a separate time series for every order.

This can become extremely expensive.

Therefore:

```text
low-cardinality dimensions
        ↓
metrics

high-cardinality diagnostic context
        ↓
traces / logs
```

For example:

```text
environment
region
payment type
status
```

may work well as metric attributes.

But:

```text
user ID
order ID
request ID
email address
```

usually should not become metric dimensions.

In time-series databases (like Prometheus or Grafana Mimir), each unique permutation of metric dimensions allocates a distinct time-series line in memory. Emitting high-cardinality values like user IDs or order numbers explodes the database's inverted index, saturates RAM, and eventually crashes the storage engine. High-cardinality context belongs exclusively in span attributes or structured log payloads, which are indexed differently and designed for arbitrary uniqueness.

---

## Logs

OpenTelemetry also defines a standard representation for logs.

Logs can contain structured attributes as well as tracing context.

For example:

```text
Payment provider returned 503

trace_id = 829a...
span_id  = 12f...
provider = Stripe
```

This allows logs and traces to be correlated.

Conceptually:

```text
Trace
 │
 ├── Payment span
 │      │
 │      └── log: provider returned 503
 │
 └── HTTP span
```

---

## Old .NET Approach: prometheus-net

Before OpenTelemetry became common, Prometheus-specific libraries were frequently used directly.

```text
.NET
  ↓
prometheus-net
  ↓
/metrics
  ↓
Prometheus
  ↓
Grafana
```

This works perfectly well, but application instrumentation becomes tied to Prometheus concepts.

The more modern architecture can be:

```text
.NET
 ↓
System.Diagnostics.Metrics
 ↓
OpenTelemetry
 ↓
Prometheus
```

The application-facing instrumentation becomes less backend-specific.

---

## Old .NET Approach: Application Insights SDK

Classic Application Insights provided both instrumentation and Azure-specific telemetry APIs.

Typical concepts included:

```text
TelemetryClient
StartOperation
RequestTelemetry
DependencyTelemetry
ITelemetryInitializer
ITelemetryProcessor
```

Applications could:

- create operations,

- modify telemetry,

- add custom properties,

- intercept the telemetry pipeline,

- correlate requests and dependencies.

Conceptually:

```text
application
    ↓
Application Insights SDK
    ↓
Azure Application Insights
```

---

## OpenTelemetry and Application Insights

Application Insights can now act as an OpenTelemetry backend.

Conceptually:

```text
.NET
 ↓
OpenTelemetry
 ↓
Azure Monitor exporter / Collector
 ↓
Application Insights
```

This changes the responsibility split.

Previously:

```text
Application Insights
=
instrumentation
+ telemetry model
+ transport
+ backend
+ UI
```

With OpenTelemetry:

```text
OpenTelemetry
=
instrumentation
+ telemetry model
+ transport

Application Insights
=
backend
+ storage/query
+ APM experience
+ Azure integration
```

This reduces coupling between application instrumentation and Azure.

---

## Mapping Classic Application Insights to OpenTelemetry

Approximate mappings include:

|Application Insights|OpenTelemetry / .NET|
|---|---|
|`TelemetryClient.StartOperation()`|`ActivitySource.StartActivity()`|
|RequestTelemetry|server span|
|DependencyTelemetry|client span|
|custom properties|span attributes|
|Operation.Id|TraceId|
|ParentId|ParentSpanId|
|TelemetryInitializer|enrichment / processor|
|TelemetryProcessor|processor / Collector processor|

The exact behavior is not always one-to-one, but the same architectural capabilities largely remain available.

---

### Instrumenting coding agent execution

An agent workflow can combine model requests, tool calls, subagent work, CI checks, repair attempts, and waits for a person. Collect facts from their owning components and correlate them with a durable task identifier. A long workflow may span several traces; a single trace should not be the only record of the business task.

The runtime reports operations and usage, while the orchestrator supplies phase, attempt, candidate commit, policy version, and the finding that triggered a repair. Native telemetry avoids rebuilding every event source, but it does not know all of the company's process meaning.

Keep token usage, cost estimates, and billing mode distinct. Check whether counters are per-call or cumulative and whether cache and reasoning categories overlap other totals. Missing usage should remain missing. Aggregate duration also differs from elapsed time when child work runs in parallel.

Avoid using per-task or per-customer identifiers as unbounded metric labels. Put detailed correlation in traces, logs, or an execution store, and aggregate metrics by controlled dimensions such as phase and outcome. Apply redaction, access, retention, and sampling policies to agent content as well as normal application telemetry.

Record the model, runtime, instructions, tools, and evaluation versions needed to compare runs. Do not interpret an agent's explanation of its own delay as measured internal reasoning. [[Observability and Controlled Improvement of Coding Agent Harnesses]] connects these observations to controlled process experiments.

Keep business meaning near the operation and infrastructure policy in the configured telemetry pipeline. Check the resulting spans, metric dimensions, and correlation on a representative execution rather than judging instrumentation only by registration code.

## Related Notes

- [[OpenTelemetry — Architecture, Signals, and Collector]] — Collector topology, sampling, backend integration, and vendor-neutral boundaries.
- [[Reliable Kubernetes Logging with OpenTelemetry]] — Choosing a delivery path for logs and understanding loss during failures.
- [[Observability and Controlled Improvement of Coding Agent Harnesses]] — Correlating agent operations and evaluating improvements from execution evidence.
