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
  - OpenTelemetry
  - OpenTelemetry Architecture
  - OTel Signals and Collector
---

A service emits traces and metrics, a Collector processes them, and a backend stores and queries them. Deciding which component owns each step makes it easier to change the transport or destination without confusing instrumentation with storage and analysis.

This article explains that architecture, including collection, sampling, backend integration, and the limits of vendor neutrality. [[Instrumenting .NET Applications with OpenTelemetry]] follows application-level tracing, metrics, enrichment, and migration in .NET. [[Reliable Kubernetes Logging with OpenTelemetry]] examines where log records wait and which failures can still lose them. These are complementary views of the same telemetry path.

## What OpenTelemetry Is

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

## OTLP — OpenTelemetry Protocol

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

## OpenTelemetry Architecture

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

## OpenTelemetry Collector

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

### Receivers

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

### Processors

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

### Exporters

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

## Direct Export vs Collector

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

## Sampling

Distributed tracing can generate enormous amounts of data.

Sampling decides which traces should be retained.

There are two important conceptual approaches.

### Head sampling

The decision happens near the beginning of the trace.

```text
request starts
    ↓
keep?
yes / no
```

It is cheap, but the decision is made without knowing the final result.

### Tail sampling

The Collector can wait until more of the trace is available.

This enables decisions such as:

```text
keep all failed requests
keep all requests > 5 seconds
keep traces containing specific services
sample ordinary successful requests
```

Tail sampling is one of the reasons a central Collector can be valuable.

#### The Tail Sampling Routing Invariant

Tail sampling introduces an architectural invariant: **all spans belonging to the same `TraceId` must arrive at the exact same Collector instance**. Because microservices emit spans independently across the network, standard round-robin load balancers will scatter spans across different Collector nodes, causing incomplete trace DAGs and broken sampling decisions.

Solving this requires a two-tier Collector topology. A front-facing routing tier uses the OpenTelemetry `loadbalancingexporter` to compute a consistent hash on the incoming `TraceId`. It deterministically forwards all spans for that trace to a specific second-tier Collector node, where the `tail_sampling` processor evaluates the completed trace against sampling rules.

---

## OpenTelemetry and Prometheus

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

## OpenTelemetry and Grafana

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

## OpenTelemetry and Elastic

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

## Vendor Neutrality

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

## Security and Sensitive Data

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

[[Agent-Assisted Sensitive Data Exposure Audits]] traces a field from an API or database into telemetry and checks whether that destination should receive it at all.

The Collector can enforce sanitization rules centrally using the `transform` processor or dedicated redaction components. By configuring regex patterns to mask credit cards, tokens, or email addresses, and stripping sensitive headers like `Authorization` or `Cookie`, teams ensure compliance across all running microservices without having to rely on every developer remembering to sanitize local log outputs.

---

## Recommended Architecture

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

## Main Takeaways

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

> **Applications normally log to stdout/stderr. Kubernetes/container runtime captures those streams into node-local log files, and a node-level collector can forward them. Direct in-process OTLP log export should not be relied upon when logs must survive abrupt application crashes.** (See [[Embedding LLMs in Runtime Decision Paths and Operational Telemetry]] and [[Propagating User Context Between Services]]).

## Related Notes

- [[Embedding LLMs in Runtime Decision Paths and Operational Telemetry]] — Correlating distributed telemetry traces with real-time AI diagnosis.
- [[Propagating User Context Between Services]] — Passing traceparent, security principal, and tenancy across microservices.
- [[Remote Service Calls — Errors, Resilience, and Observability]] — Shared HTTP instrumentation, trace propagation, and service-specific telemetry enrichment.
- [[Standardizing Service Infrastructure with Reusable Blocks]] — Packaging OpenTelemetry collectors and logging pipelines into shared service blocks.
