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
  - Decoupling Telemetry Production from Storage Backends
  - Distributed Tracing and Context Propagation
---

# OpenTelemetry — Architecture, Signals, and Collector

> [!IMPORTANT]
> **The Telemetry Decoupling Axiom**: Distributed microservices and autonomous agent meshes require strict decoupling of application instrumentation from vendor storage backends:
> $$\text{Unified Observability Mesh} = \text{Correlated Signals (Traces, Metrics, Logs, Profiles)} \times \text{W3C Context Propagation} \times \text{Vendor-Neutral OTLP}$$
> OpenTelemetry is not an observability database, dashboard, or proprietary monitoring agent. It is a vendor-neutral standard specification, API/SDK ecosystem, and telemetry proxy pipeline (**OpenTelemetry Collector**) that standardizes how distributed software generates, describes, enriches, and transports diagnostic signals. Standardizing on the **OpenTelemetry Protocol (OTLP)** and leveraging W3C TraceContext propagation across synchronous RPCs and asynchronous message queues eliminates proprietary SDK lock-in, enables dynamic tail sampling, and provides the correlated semantic trace graph required for automated root-cause analysis.

```text
Application Microservices (Heterogeneous Polyglot Runtimes)
       │ (Native Diagnostic Primitives: Diagnostics API, Spans, Structured Logs)
       ├── Traces & Metrics ──► OTLP (gRPC / Protobuf) ────────┐
       └── Logs ──────────────► Structured stdout/stderr ─────┐│
                                                              ││
                                Container Runtime File Logs   ││
                                                              ││
                                                              ▼▼
                                                   OpenTelemetry Collector
                                            ┌─────────────────────────────────────┐
                                            │ Receivers  (OTLP, filelog, metrics) │
                                            │ Processors (Filter, Batch, Sample)  │
                                            │ Exporters  (OTLP, Azure, Prometheus)│
                                            └──────────────────┬──────────────────┘
                                                               │
                                  ┌────────────────────────────┼────────────────────────────┐
                                  ▼                            ▼                            ▼
                            Azure Monitor              Grafana Ecosystem           Elasticsearch / Kibana
                        (Application Insights)       (Tempo, Mimir, Loki)
```

---

## Executive Summary & Core Architectural Invariants

OpenTelemetry establishes a standardized observability interoperability layer across modern software architectures, serving as a core component of [[Standardizing Service Infrastructure with Reusable Blocks|reusable service infrastructure]]:

1. **Decoupling Generation from Storage**: OpenTelemetry describes, enriches, and transports telemetry; external observability backends store, index, query, and visualize it. Applications instrument against vendor-neutral OTel APIs without taking dependencies on Datadog, Dynatrace, Azure Monitor, or AWS X-Ray.
2. **The Four Core Telemetry Signals**:
   - **Traces**: Directed Acyclic Graphs (DAGs) of spans documenting end-to-end causal execution paths across distributed network hops.
   - **Metrics**: Aggregated numerical measurements (counters, gauges, histograms) tracking macro system performance and SLI/SLAs.
   - **Logs**: Timestamped structured event records containing contextual debugging detail, correlated with active traces via `TraceId` and `SpanId`.
   - **Profiles**: Continuous call-stack samples attributing CPU and heap allocations to runtime execution paths.
3. **The Collector as an Ingestion Pipeline**: The OpenTelemetry Collector operates as a proxy pipeline consisting of **Receivers** (accepting OTLP, Prometheus, or logs), **Processors** (filtering, batching, scrubbing sensitive PII, and sampling), and **Exporters** (routing to one or multiple destinations).
4. **Native Language Integration**: OpenTelemetry binds directly to native runtime primitives across ecosystems (such as asynchronous local storage, runtime diagnostic event sources, thread-local contexts, and task-scoped variables).
5. **The Cardinality Governance Rule**: Metric dimension attributes must maintain low cardinality (`environment`, `region`, `status_code`). High-cardinality values (`user_id`, `order_id`, `request_id`) must never be added as metric tags—they belong exclusively in traces and structured logs to prevent time-series database crashes.
6. **The Direct In-Process OTLP Log Trap**: Directly exporting logs from application memory via OTLP is dangerous: unhandled process crashes (`SIGKILL`, OOM exceptions) destroy in-memory telemetry buffers. Production workloads log structured JSON to `stdout`/`stderr`, relying on container runtimes and node-level Collector DaemonSets for durable ingestion.
7. **W3C Context Propagation Across Boundaries**: Distributed transactions propagate identity across network boundaries using standardized W3C TraceContext headers (`traceparent`, `tracestate`), allowing spans to link across HTTP, gRPC, and message brokers.
8. **Head vs. Tail Sampling Economics**: High-throughput systems cannot afford to store 100% of traces. While head sampling makes early probabilistic drop decisions, Collector-based **tail sampling** buffers entire trace graphs in memory to guarantee 100% retention of errors, timeouts, and anomalous transactions.

---

## The Recommended Production Reference Architecture

A resilient, cloud-native architecture separates telemetry pathways by durability and performance requirements:

```text
                         Application Runtime (Containerized Workload)
                         /                                    \
                        /                                      \
              Traces + Metrics                                Structured Logs
          (OTLP gRPC / In-Memory Queue)                      (stdout / stderr)
                        ↓                                      ↓
                        │                            Container Runtime (containerd)
                        │                                      ↓
                        │                            Node Local Storage (/var/log/pods/)
                        │                                      ↓
                        └───────────────────┬──────────────────┘
                                            ↓
                            OpenTelemetry Collector (DaemonSet)
                                            │
                               ┌────────────┴────────────┐
                               │ 1. Receivers:           │
                               │    - OTLP (port 4317)   │
                               │    - filelog (/var/log) │
                               │ 2. Processors:          │
                               │    - memory_limiter     │
                               │    - k8sattributes      │
                               │    - filter (strip PII) │
                               │    - tail_sampling      │
                               │    - batch              │
                               │ 3. Exporters:           │
                               │    - otlp (Tempo/Loki)  │
                               │    - prometheus (Mimir) │
                               │    - azuremonitor       │
                               └────────────┬────────────┘
                                            │
                     ┌──────────────────────┼──────────────────────┐
                     ▼                      ▼                      ▼
               Azure Monitor         Grafana Stack            Elasticsearch
```

This reference topology delivers critical production guarantees:
- **Zero Application Vendor Lock-in**: Changing backends requires editing Collector YAML without recompiling application binaries.
- **Crash Durability**: Logs written to `stdout` are preserved on node disk by the container runtime even if the application suffers an immediate kernel panic.
- **Centralized Data Sanitization**: Authorization tokens, customer PII, and connection strings are scrubbed at the Collector boundary before data leaves corporate perimeters.

---

## Runtime Integration Across Language Ecosystems

OpenTelemetry avoids proprietary wrappers by mapping directly to native runtime diagnostic primitives:

| Ecosystem | Native Tracing Primitive | Native Metrics Primitive | Logging Integration | Context Propagation Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **Go** | `go.opentelemetry.io/otel/trace` | `otel/metric` | `slog` / `zap` | `context.Context` explicit passing |
| **Rust** | `tracing` (`Span`, `Event`) | `metrics` crate | `tracing-subscriber` | `tracing::Span::current()` implicit |
| **Java** | `io.opentelemetry.api.trace` / Java Agent | Micrometer / OTel Metrics | SLF4J / Logback | ThreadLocal / `Scope` object |
| **Python** | `opentelemetry.trace` / WSGI middleware | `opentelemetry.metrics` | `logging` stdlib module | ContextVars / async task-local |
| **TypeScript** | `@opentelemetry/api` | `@opentelemetry/api-metrics` | `winston` / `pino` | `AsyncLocalStorage` |
| **.NET** | `System.Diagnostics.ActivitySource` | `System.Diagnostics.Metrics.Meter` | `ILogger` | `AsyncLocal<T>` / `Activity.Current` |

### Conceptual Span Creation Pattern
Application code creates spans reflecting business operations without coupling to telemetry backends:

```text
// Conceptual decoupled instrumentation pattern
tracer = getTracer("OrdersService")

with span = tracer.startSpan("CreateOrder"):
    span.setAttribute("order.id", order.id)
    span.setAttribute("customer.type", customer.type)
    
    // Execute domain operation
    executeOrderCreation(order)
```

The application remains completely agnostic to whether downstream telemetry is stored in Azure Application Insights, Grafana Tempo, Jaeger, or Elasticsearch.

---

## Metrics Cardinality & Governance

Metrics require strict governance over dimension attributes:

```text
Safe Low-Cardinality Metric Attributes:
payment.count {
    environment = "production",
    region      = "us-east-1",
    payment_type= "credit_card",
    status      = "success"
}
(Produces bounded, predictable time-series lines)

Dangerous High-Cardinality Explosion:
payment.count {
    order_id = "89127491823",
    user_id  = "usr-481923"
}
(Creates a unique time-series per transaction; exhausts memory and crashes Prometheus/Mimir)
```

**Rule of Thumb**:
- **Low-Cardinality Dimensions** $\rightarrow$ Metrics (aggregated gauges, counters, histograms for alerts and SLIs).
- **High-Cardinality Dimensions** $\rightarrow$ Distributed Traces and Structured Logs (investigatory context correlated by `TraceId`).

---

## Log Durability and The In-Process OTLP Trap

Applications can technically push logs directly to a network endpoint using in-process OTLP logging providers:

```text
Application Process ──► In-Memory Buffer ──► OTLP HTTP/gRPC Export ──► Collector
```

**The Fatal Vulnerability**: If the container process experiences an out-of-memory kill (`OOMKilled`), fatal hardware fault, or unhandled runtime panic, **the in-memory buffer is annihilated before data reaches the network**.

### The Cloud-Native Container Logging Standard
In resilient production systems, applications emit structured logs directly to `stdout`/`stderr`:
1. The container runtime captures standard output and writes it to node-local log files (`/var/log/pods/`).
2. An OpenTelemetry Collector DaemonSet tails these local files using a `filelog` receiver.
3. If the application crashes, the log explaining the crash is already safe on node disk, ready for batch collection.

---

## Sampling Strategies: Head vs. Tail Sampling

High-throughput systems emitting hundreds of thousands of transactions per second cannot afford to transmit and store every span.

```text
Head Sampling:
Request Starts  ──►  Evaluate Probability (e.g., 5% random)  ──►  Record or Drop Immediately
(Fast, zero memory buffer required; misses rare, intermittent errors occurring in the dropped 95%)

Tail Sampling:
Request Starts  ──►  Buffer All Spans in Collector Memory  ──►  Evaluate Complete Trace
                                                                    ├── Error Detected? ──► Keep 100%
                                                                    ├── Latency > 2s?   ──► Keep 100%
                                                                    └── Routine 200 OK? ──► Sample 1%
```

Tail sampling requires routing all spans of a distributed trace to the same Collector instance (via load-balancing exporters), enabling intelligent retention policies that preserve 100% of anomalies while pruning routine noise.

---

## Relationship to the Knowledge Graph

- **[[AI Productivity Is Limited by the Delivery System]]**: Observability as the mandatory feedback loop validating agentic deployments in production.
- **[[Embedding LLMs in Runtime Decision Paths and Operational Telemetry]]**: Using OpenTelemetry spans, metrics, and logs as runtime inputs for supervisory conversational agents.
- **[[Service-to-Service Communication -  How Service A Should Call Service B]]**: Propagating W3C trace context across distributed HTTP, gRPC, and message brokers.
- **[[Standardizing Service Infrastructure with Reusable Blocks]]**: Injecting zero-code telemetry and collectors into service runtime templates.
- **[[Scaling a Modular Monolith with Local-or-Remote Module Execution]]**: Tracing workflows as they transition between local in-memory calls and distributed queues.
- **[[Propagating User Context Between Services]]**: Managing baggage and distributed trace headers across heterogeneous microservice meshes.
