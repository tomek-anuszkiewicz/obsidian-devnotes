---
title: OpenTelemetry — Architecture, Signals, and Collector
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
---

## 1. What OpenTelemetry Is

OpenTelemetry is a vendor-neutral observability framework.

It standardizes how applications and infrastructure:

- produce telemetry,
    
- describe telemetry,
    
- propagate tracing context,
    
- transport telemetry,
    
- process telemetry before it reaches a backend.
    

It is not primarily a database, dashboard, or observability backend.

A useful mental model is:

```text
Application / Infrastructure
        ↓
OpenTelemetry instrumentation
        ↓
OpenTelemetry Protocol / Collector
        ↓
Observability backend
```

Typical backends include:

- Prometheus / Mimir,
    
- Loki,
    
- Tempo,
    
- Elasticsearch,
    
- Azure Monitor / Application Insights,
    
- Datadog,
    
- Splunk,
    
- other OTLP-compatible systems.
    

### Signals

The primary OpenTelemetry signals are:

```text
OpenTelemetry
├── traces
├── metrics
├── logs
└── profiles
```

Profiles are newer and less mature than the other three.

Frontend/browser/mobile telemetry is not a separate signal. Those are simply additional telemetry sources that can emit traces, metrics, logs, etc.

Under the hood, these signals serve distinct diagnostic purposes:
- **Traces** record the causal path of a request through a distributed system. Spans form a Directed Acyclic Graph (DAG) capturing operations, parent-child dependencies, and latencies.
- **Metrics** provide aggregated numerical counters, gauges, and histograms tracking throughput, error rates, and resource saturation over time.
- **Logs** capture discrete, structured event records. In OpenTelemetry, logs carry ambient `TraceId` and `SpanId` identifiers, linking them directly into distributed traces.
- **Profiles** capture continuous call-stack samples to attribute CPU allocations and thread contention directly to code paths.

---

## 2. OTLP — OpenTelemetry Protocol

One particularly important part of OpenTelemetry is OTLP.

OTLP standardizes communication between telemetry producers and receivers.

For example:

```text
.NET application
      ↓
     OTLP
      ↓
OTel Collector
```

But the sender and receiver do not have to be an application and a Collector.

Other valid architectures include:

```text
Collector A
    ↓ OTLP
Collector B
```

or:

```text
OTel Collector
      ↓ OTLP
Observability provider
```

This means OpenTelemetry creates an interoperability layer between observability components.

A system can therefore accept many kinds of telemetry:

```text
stdout logs ─────────┐
                     │
Prometheus metrics ──┼──→ Collector
                     │
OTLP traces ─────────┘
```

normalize them, and then forward them using OTLP or another supported protocol.

OTLP is serialized primarily with Protocol Buffers (Protobuf). In production, it runs over gRPC (HTTP/2) using standard port 4317, or over HTTP/1.1 with Protobuf/JSON payloads on port 4318.

---

## 3. OpenTelemetry Architecture

OpenTelemetry consists of several distinct layers.

```text
OpenTelemetry
│
├── APIs / SDKs
│
├── telemetry data model
│
├── semantic conventions
│
├── context propagation
│
├── OTLP
│
└── Collector
```

### APIs and SDKs

Applications use OpenTelemetry APIs or platform-native APIs integrated with OpenTelemetry to produce telemetry.

OpenTelemetry enforces a strict boundary between the API and the SDK:
- **API**: Contains only the instrumentation interfaces and data types. It has zero dependencies on network transports or exporters. If an application instruments code against the API and no SDK is registered at runtime, calls fall back to a zero-overhead no-op implementation.
- **SDK**: The runtime implementation (in .NET, Go, Java, etc.) that registers listeners, manages in-memory buffering, evaluates sampling rules, executes batch processors, and transmits payloads over the wire.

### Semantic conventions

OpenTelemetry tries to standardize attribute names and meanings.

Instead of different libraries inventing:

```text
HTTPMethod
http_method
request.method
method
```

telemetry can follow common conventions.

This is important for portability between observability providers.

Conventions cover standard keys across network boundaries: `http.request.method`, `http.response.status_code`, `db.system`, and `db.statement`. Adhering to these conventions guarantees that dashboards, alert queries, and APM views operate predictably regardless of which programming language or framework emitted the span.

### Context propagation

Tracing context can travel between services.

For example:

```text
Browser
   ↓
API
   ↓
Service
   ↓
Database
```

can participate in the same distributed trace.

Important concepts include:

```text
TraceId
SpanId
ParentSpanId
traceparent
```

Context propagation standardizes on the **W3C TraceContext** specification:
- `traceparent`: A single formatted header containing the protocol version, 16-byte `TraceId`, 8-byte `ParentSpanId`, and trace flags (for example, `01` indicating recorded/sampled).
- `tracestate`: Transports vendor-specific opaque routing and filtering metadata across hops without breaking trace continuity.
- **Baggage**: Key-value pairs propagated across the distributed call tree. It carries cross-cutting business context (such as `tenant.id`) across microservices without hitting an intermediate datastore, though it is not automatically converted to span attributes without explicit mapping.

---

# 4. OpenTelemetry Collector

The OpenTelemetry Collector is a separate process responsible for collecting and processing telemetry.

Its basic architecture is:

```text
receiver
   ↓
processor
   ↓
exporter
```

A Collector can therefore act as a telemetry pipeline.

Example:

```text
applications
     ↓
Collector
     ↓
filter
     ↓
enrich
     ↓
batch
     ↓
route
     ↓
backend
```

## Receivers

Receivers accept telemetry.

Examples:

```text
OTLP receiver
Prometheus receiver
filelog receiver
host metrics receiver
```

This is important because applications do not necessarily have to use OpenTelemetry themselves.

For example:

```text
legacy application
      ↓
Prometheus /metrics
      ↓
OTel Collector
```

or:

```text
application
   ↓ stdout
Kubernetes log file
   ↓
filelog receiver
```

## Processors

Processors modify telemetry before export.

They can be used for:

- filtering,
    
- enrichment,
    
- batching,
    
- removing attributes,
    
- renaming attributes,
    
- sampling,
    
- removing sensitive data,
    
- adding infrastructure metadata.
    

Example:

```text
span
 ↓
add:
  environment = production
  cluster = eu-prod
  team = payments
 ↓
backend
```

In Collector pipelines, **processor order matters strictly**. Telemetry flows sequentially through the declared list:
- `memory_limiter`: Drops or backs off ingestion when the Collector process approaches its physical RAM ceiling. It must be declared first in the pipeline to prevent unrecoverable out-of-memory crashes.
- `k8sattributes`: Enriches spans and logs with pod name, namespace, and workload labels resolved dynamically from the client's IP address.
- `transform`: Uses the OpenTelemetry Transformation Language (OTTL) to mutate, rename, or drop attributes via declarative statements before exporting.
- `batch`: Groups individual records into larger compressed network frames, slashing outbound HTTP/gRPC connection overhead and downstream network calls.

## Exporters

Exporters send telemetry to another system.

For example:

```text
Collector
 ├──→ Azure Monitor
 ├──→ Elastic
 ├──→ Tempo
 └──→ another Collector
```

This enables multi-backend routing.

---

# 5. Direct Export vs Collector

A simple architecture can export directly from the application:

```text
Application
    ↓ OTLP
Backend
```

or:

```text
Application
    ↓ OTLP
Collector
    ↓
Backend
```

The Collector becomes increasingly useful when we need:

- centralized configuration,
    
- filtering,
    
- enrichment,
    
- retries,
    
- routing,
    
- multiple destinations,
    
- sampling,
    
- durable queues,
    
- Kubernetes log collection,
    
- protocol conversion.
    

It also reduces vendor coupling inside applications.

Instead of:

```text
Application
   ↓
Azure-specific SDK
```

we can have:

```text
Application
   ↓ OTLP
Collector
   ├──→ Azure
   ├──→ Elastic
   └──→ Grafana ecosystem
```

Beyond vendor decoupling, the Collector acts as an operational buffer. Direct application export leaves application runtimes vulnerable: if a cloud backend stalls or drops connections, in-process queues fill up, forcing application threads to absorb memory pressure or stall on outbound sockets. An intermediate Collector decouples application thread health from backend availability, offloading batch compression, retry loops, and auth credential handling to a dedicated process.

---

# 6. OpenTelemetry in .NET

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

## Tracing in .NET

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

## Automatic Instrumentation

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

# 7. Influencing and Modifying Traces

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

## Application-level enrichment

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

## SDK Processors

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

## Collector-level transformation

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

# 8. Trace Relationships and Async Systems

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

# 9. Sampling

Distributed tracing can generate enormous amounts of data.

Sampling decides which traces should be retained.

There are two important conceptual approaches.

## Head sampling

The decision happens near the beginning of the trace.

```text
request starts
    ↓
keep?
yes / no
```

It is cheap, but the decision is made without knowing the final result.

## Tail sampling

The Collector can wait until more of the trace is available.

This enables decisions such as:

```text
keep all failed requests
keep all requests > 5 seconds
keep traces containing specific services
sample ordinary successful requests
```

Tail sampling is one of the reasons a central Collector can be valuable.

### The Tail Sampling Routing Invariant

Tail sampling introduces an architectural invariant: **all spans belonging to the same `TraceId` must arrive at the exact same Collector instance**. Because microservices emit spans independently across the network, standard round-robin load balancers will scatter spans across different Collector nodes, causing incomplete trace DAGs and broken sampling decisions.

Solving this requires a two-tier Collector topology. A front-facing routing tier uses the OpenTelemetry `loadbalancingexporter` to compute a consistent hash on the incoming `TraceId`. It deterministically forwards all spans for that trace to a specific second-tier Collector node, where the `tail_sampling` processor evaluates the completed trace against sampling rules.

---

# 10. Metrics

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

## Traditional Prometheus Model

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

## Modern .NET Metrics

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

# 11. Metrics Cardinality

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

# 12. Logs

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

# 13. Direct OTLP Logs

Applications can push logs directly.

```text
.NET ILogger
     ↓
OTel logging provider
     ↓
OTLP
     ↓
Collector
```

This avoids application-owned log files.

However, direct in-process OTLP exporting has an important limitation.

There is normally an in-memory batch or queue.

If the process suddenly dies:

```text
application
   ↓
in-memory telemetry buffer
   X process crashes
```

the remaining telemetry may disappear.

Therefore:

> Direct in-process OTLP log export should not be considered a durable logging mechanism.

Graceful shutdown can flush buffers, but this does not protect against:

- `SIGKILL`,
    
- OOM kills,
    
- runtime crashes,
    
- node failures,
    
- abrupt container termination.
    

---

# 14. Kubernetes Logging

Kubernetes already provides a useful mechanism for crash-resistant application logging.

Applications normally write logs to:

```text
stdout
stderr
```

The container runtime captures these streams and writes them to node-local log files.

Typical locations include:

```text
/var/log/pods/
/var/log/containers/
```

The exact layout depends on the Kubernetes/container runtime environment.

Therefore applications usually do not need to create their own application log files.

The typical architecture is:

```text
.NET application
      ↓
ILogger
      ↓
stdout / stderr
      ↓
container runtime
      ↓
node-local log files
      ↓
log collector
      ↓
central backend
```

A useful consequence is that logs already written to stdout can survive the application process crashing.

The pod itself is not responsible for maintaining those files. The container runtime/node logging infrastructure performs that job.

When an application writes to `stdout`, the write traverses an operating system pipe buffer managed directly by the Linux kernel. The container runtime (such as containerd or CRI-O) drains the pipe and appends the log record to the node's local disk. Even if the application process terminates violently due to an out-of-memory kill (`OOMKilled`, exit code 137) or a sudden segmentation fault, the fatal log entry describing the crash is already flushed to the host filesystem.

---

# 15. OTel Collector for Kubernetes Logs

The OpenTelemetry Collector can run as a node-level agent, commonly using a DaemonSet.

```text
Pod A ──stdout──┐
Pod B ──stdout──┼──→ node log files
Pod C ──stdout──┘
                        ↓
                OTel Collector
                        ↓
                   log backend
```

The Collector can use a file log receiver to tail Kubernetes container logs.

This produces a useful separation:

```text
application
   ↓
structured stdout

platform
   ↓
durable-enough local log file

collector
   ↓
central telemetry pipeline
```

---

# 16. Log Durability

There are multiple failure boundaries.

### Application failure

```text
App
 ↓
stdout
 ↓
node file
```

Logs already written to the node file normally survive the application process restarting.

### Collector failure

The Collector itself can have buffering and retry mechanisms.

For stronger durability, its sending queue can use persistent storage.

Conceptually:

```text
Kubernetes log
      ↓
Collector
      ↓
persistent queue
      ↓
backend
```

If the Collector restarts, telemetry remaining in persistent storage can be retried.

The `filelog` receiver tracks its read state by persisting file checkpoints (device ID, inode, and byte offset) to disk. If the Collector crashes and restarts, it resumes reading from the exact byte where it left off, avoiding duplicate or dropped records. Outbound exporters can be backed by the Collector's `file_storage` extension, creating an on-disk buffer that protects telemetry during downstream network outages.

### Node failure

Node-local storage still has limits.

If an entire node is permanently lost before logs are forwarded:

```text
node dies
  ↓
local logs may disappear
```

If stronger guarantees are required, a replicated durable system such as a messaging system may be necessary.

---

# 17. Sidecars vs Node-Level Collectors

A logging sidecar is possible:

```text
Pod
├── application
└── logging sidecar
```

But it should not normally be required simply to turn stdout into a file.

Kubernetes already captures container stdout/stderr.

For ordinary centralized logging, a node-level agent is generally simpler:

```text
Node
├── Pod A
├── Pod B
├── Pod C
└── OTel Collector DaemonSet
```

One Collector can therefore handle logs from many pods.

Sidecars are more appropriate when a particular application requires unusual per-pod processing or integration.

From a resource standpoint, a sidecar collector duplicates memory allocations across every pod in the cluster. Deploying a sidecar across 100 pods means maintaining 100 independent Collector memory buffers and 100 sets of outbound network connections. A node-level DaemonSet consolidates telemetry processing into a single shared process per host, lowering cluster-wide memory usage and connection churn.

---

# 18. Old .NET Approach: prometheus-net

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

# 19. Old .NET Approach: Application Insights SDK

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

# 20. OpenTelemetry and Application Insights

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

# 21. Mapping Classic Application Insights to OpenTelemetry

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

# 22. OpenTelemetry and Prometheus

OpenTelemetry does not replace Prometheus.

A typical architecture can still be:

```text
.NET
 ↓
OpenTelemetry
 ↓
Prometheus
 ↓
Grafana
```

Prometheus remains responsible for metric storage and querying.

OpenTelemetry becomes the common instrumentation and telemetry layer.

This also means `/metrics` does not automatically imply that OpenTelemetry is absent.

Both of these are possible:

```text
prometheus-net
    ↓
/metrics
```

and:

```text
OpenTelemetry Prometheus exporter
    ↓
/metrics
```

From Prometheus' perspective they can look very similar.

---

# 23. OpenTelemetry and Grafana

Grafana itself is primarily visualization.

Typical Grafana ecosystem components are:

```text
Mimir       metrics
Loki        logs
Tempo       traces
Pyroscope   profiles
Grafana     visualization
```

OpenTelemetry can feed those systems.

```text
Application
     ↓
OpenTelemetry
     ↓
Collector
     ├──→ Mimir
     ├──→ Loki
     └──→ Tempo
```

Grafana Alloy is another option at the collector/agent layer.

It is a Grafana-oriented OpenTelemetry distribution with additional integrations, particularly around the Prometheus/Grafana ecosystem.

It is not required to use Grafana.

Plain OpenTelemetry Collector can be used instead.

---

# 24. OpenTelemetry and Elastic

Elastic can similarly act as an observability backend.

Conceptually:

```text
Application
    ↓
OpenTelemetry
    ↓
Collector
    ↓
Elasticsearch / Elastic Observability
    ↓
Kibana
```

Again, OpenTelemetry is not replacing Kibana or Elasticsearch.

It is standardizing how telemetry gets there.

---

# 25. Vendor Neutrality

One of the strongest arguments for OpenTelemetry is reducing telemetry vendor coupling.

Instead of:

```text
application
 ↓
vendor SDK
 ↓
vendor backend
```

we can move toward:

```text
application
 ↓
OpenTelemetry
 ↓
Collector
 ↓
backend
```

Changing the destination can then become mostly an infrastructure decision.

For example:

```text
today:
OTel → Azure Monitor

later:
OTel → Grafana

migration:
OTel → Azure + Grafana
```

However, OpenTelemetry does not make observability backends interchangeable.

Backends still differ in:

- query languages,
    
- dashboards,
    
- retention,
    
- alerting,
    
- pricing,
    
- trace analysis,
    
- storage architecture,
    
- proprietary features.
    

OTel primarily reduces coupling at the telemetry generation and transport layer.

Query languages and alert rules remain tightly bound to specific storage engines. Standardizing on OpenTelemetry does not mean you can run a PromQL query against Azure Log Analytics, or a KQL statement against Grafana Loki or Tempo. Migrating backends still requires translating dashboards, recalculating alert thresholds, and adapting to different billing models (such as paying per ingested gigabyte versus paying per active metric time series). OpenTelemetry solves application-side lock-in, not backend query compatibility.

---

# 26. Security and Sensitive Data

Telemetry frequently contains more information than expected.

Potentially sensitive fields include:

```text
authorization headers
cookies
tokens
email addresses
user IDs
request bodies
SQL values
URLs with query parameters
```

This should be considered during instrumentation.

There are multiple places where filtering can happen:

```text
application
    ↓
SDK processor
    ↓
Collector processor
    ↓
backend
```

The Collector is particularly useful for enforcing organization-wide filtering or redaction policies.

However, sensitive values ideally should not be emitted unnecessarily in the first place.

The Collector can enforce sanitization rules centrally using the `transform` processor or dedicated redaction components. By configuring regex patterns to mask credit cards, tokens, or email addresses, and stripping sensitive headers like `Authorization` or `Cookie`, teams ensure compliance across all running microservices without having to rely on every developer remembering to sanitize local log outputs.

---

# 27. Recommended Architecture

A reasonable modern Kubernetes/.NET architecture is:

```text
                         .NET application
                        /               \
                       /                 \
             traces + metrics            logs
                  OTLP                   ILogger
                    ↓                       ↓
                    │                  stdout/stderr
                    │                       ↓
                    │              Kubernetes node logs
                    │                       ↓
                    └──────────────┬────────┘
                                   ↓
                         OTel Collector
                                   ↓
                     processing / filtering
                     enrichment / sampling
                     retry / persistent queue
                                   ↓
                 ┌─────────────────┼─────────────────┐
                 ↓                 ↓                 ↓
              Azure            Grafana            Elastic
             Monitor           ecosystem
```

This architecture gives several useful properties:

- application instrumentation is largely vendor-neutral,
    
- traces and metrics can use OTLP,
    
- logs can survive application crashes through Kubernetes node logging,
    
- telemetry processing is centralized,
    
- infrastructure metadata can be added outside application code,
    
- different backends can be selected later,
    
- multiple backends can coexist,
    
- logs and traces can share tracing context.
    

---

# 28. Main Takeaways

OpenTelemetry should not be thought of merely as:

> a library for sending traces and metrics.

It is better understood as an **observability interoperability layer**.

It provides:

```text
instrumentation
+
common telemetry model
+
semantic conventions
+
context propagation
+
standard protocol
+
collection and processing infrastructure
```

The evolution in .NET can be summarized as:

```text
Earlier:

prometheus-net
     ↓
Prometheus

Application Insights SDK
     ↓
Azure


Modern:

System.Diagnostics.Activity
System.Diagnostics.Metrics
ILogger
        ↓
OpenTelemetry
        ↓
Collector
        ↓
Prometheus / Azure / Elastic / Grafana / ...
```

The most important architectural distinction is therefore:

> **OpenTelemetry describes and transports telemetry. Observability backends store, query, analyze, alert on, and visualize it.**

And for Kubernetes logging specifically:

> **Applications normally log to stdout/stderr. Kubernetes/container runtime captures those streams into node-local log files, and a node-level collector can forward them. Direct in-process OTLP log export should not be relied upon when logs must survive abrupt application crashes.**
```
