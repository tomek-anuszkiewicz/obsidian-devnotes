---
title: "Reliable Kubernetes Logging with OpenTelemetry"
tags:
  - kubernetes
  - logging
  - opentelemetry
  - reliability
  - observability
aliases:
  - "Kubernetes Log Delivery and Durability"
  - "OpenTelemetry Log Failure Boundaries"
  - "Node-Level Collectors and Application Log Export"
---

An application writes a useful error message and then terminates. Whether that message reaches the backend depends on where it had reached before the failure: an application buffer, a pipe, a node-local file, a collector queue, or remote storage.

These are separate failure boundaries. A path that survives an application restart can still lose records when a node disappears. Exporting with OTLP describes a protocol; it does not by itself establish persistent buffering or a recovery guarantee. The deployment needs an explicit delivery and retention policy.

This article compares direct application export with Kubernetes stdout collection, then follows collector and node failures. It also preserves the wider signal-correlation and deployment picture so the log path can be evaluated independently. [[OpenTelemetry — Architecture, Signals, and Collector]] explains the general architecture, while [[Instrumenting .NET Applications with OpenTelemetry]] covers the application's instrumentation choices.

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

## Direct OTLP Logs

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

## Kubernetes Logging

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

## OTel Collector for Kubernetes Logs

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

## Log Durability

There are multiple failure boundaries.

#### Application failure

```text
App
 ↓
stdout
 ↓
node file
```

Logs already written to the node file normally survive the application process restarting.

#### Collector failure

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

#### Node failure

Node-local storage still has limits.

If an entire node is permanently lost before logs are forwarded:

```text
node dies
  ↓
local logs may disappear
```

If stronger guarantees are required, a replicated durable system such as a messaging system may be necessary.

---

## Sidecars vs Node-Level Collectors

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

For a concrete deployment, record which buffers persist, how readers resume, what retries can duplicate, and which storage is lost with a node. Test the failure boundary the team actually promises to tolerate; normal delivery alone does not demonstrate recovery.

## Related Notes

- [[OpenTelemetry — Architecture, Signals, and Collector]] — Signal transport, Collector processing, and backend responsibilities.
- [[Instrumenting .NET Applications with OpenTelemetry]] — Structured logs and trace correlation in application code.
- [[Standardizing Service Infrastructure with Reusable Blocks]] — Making log delivery and telemetry behavior part of a maintained service platform.
