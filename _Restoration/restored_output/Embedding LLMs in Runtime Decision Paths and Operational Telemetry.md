---
title: Embedding LLMs in Runtime Decision Paths and Operational Telemetry
tags:
  - software-architecture
  - runtime-ai
  - observability
  - opentelemetry
  - security
  - telemetry
  - log-analysis
  - decision-systems
aliases:
  - LLMs in Live Execution Pipelines
  - Runtime AI Decision Paths
  - Conversational Observability and Security Triage
  - Semantic Telemetry and Qualitative Analysis
  - The In-Line Telemetry Supervisor
---

# Embedding LLMs in Runtime Decision Paths and Operational Telemetry

While the industry remains obsessed with build-time code generation, the far more significant architectural shift is happening in production runtimes: embedding language models directly into live execution pathways and operational telemetry meshes.

$$\text{Raw Telemetry / Input Stream} \xrightarrow{\text{Statistical Filter}} \text{Supervisory LLM} \xrightarrow{\text{Invariant Verification}} \text{Deterministic Decision Envelope} \xrightarrow{\text{Gated Execution}} \text{System State}$$

In this model, LLMs act as probabilistic runtime decision components. They synthesize multi-service causal chains to eliminate manual dashboard triage, parse qualitative domain data into strongly typed data structures, catch contextual PII leaks, and spin up autonomous canary probes. 

However, running an unpredictable model in a live environment requires a strict design rule: **the deterministic envelope**. The model should only ever produce advisory proposals. Before any system state mutates or external APIs fire, deterministic validators must enforce hard transactional rules, schema constraints, and business invariants.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        BUILD-TIME AI vs. RUNTIME AI                    │
│                                                                        │
│   BUILD-TIME (OFFLINE):                                                │
│   Engineer ──► Prompt ──► LLM ──► Static Source Code ──► Compiler      │
│                                                                        │
│   RUNTIME (ONLINE / PRODUCTION):                                       │
│   Incoming Request / Stream ──► Runtime Envelope ──► In-Line LLM       │
│                                           │              │             │
│                                           ▼              ▼             │
│                                 Deterministic Rule   Structured Decision│
│                                 Validation & Gate    Object (JSON)     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Architectural Principles for Runtime LLMs

Deploying language models within live execution pipelines and observability streams changes how we handle distributed systems monitoring and operational triage.

### 1. The Shift from Build-Time to Runtime Intelligence
Build-time tools assist human developers writing static code. Runtime models execute as active computational components inside production service meshes. Their job is translating high-entropy, ambiguous signals—like scattered log traces, raw user inputs, or unstructured third-party payloads—into strongly typed, machine-actionable decisions.

### 2. Eliminating the "Dashboard Stare"
During an incident, engineering teams routinely lose 30 to 45 minutes visually correlating metrics across dozens of disconnected Grafana dashboards. Operational supervisory agents sit downstream of OpenTelemetry span collectors, metric aggregators, and log pipelines. Instead of waiting for a human to notice a pattern, they continuously synthesize multi-service causal chains directly against codified business invariants.

### 3. Solving the Tri-State Monitoring Problem
Traditional monitoring breaks down into two failure modes:
* **Zombie Green**: Infrastructure metrics look nominal (CPU at 20%, memory flat, HTTP 200s returning), while background workers silently drop messages, serialization failures poison queues, or downstream database rows fail to write.
* **False Red**: A nightly batch job spikes queue depth past an arbitrary threshold, paging on-call engineers at 3:00 AM even though end-user latency and business SLAs are completely unaffected.

Semantic supervisors evaluate system health by checking whether transactional business invariants hold across service boundaries, rather than relying solely on decoupled scalar thresholds.

### 4. The Deterministic Envelope Pattern
Never give an LLM unconstrained database credentials, arbitrary code execution privileges, or direct access to mutation APIs. The model produces a structured JSON proposal. That proposal must pass schema validation (e.g., via Pydantic or Zod) and clear a series of deterministic state-machine assertions before anything commits to storage or touches an external network interface.

### 5. Cadence-Based Asynchronous Telemetry Inspection
Piping 100,000 raw events per second into an LLM will instantly blow past rate limits and exhaust your budget. Production pipelines run high-throughput data through deterministic sliding-window filters (e.g., Redis, Apache Flink, or PromQL aggregations) to compute baseline statistics. Only anomalous, topologically correlated trace clusters get forwarded to the reasoning model, typically on a 5- to 15-minute evaluation cadence.

### 6. Autonomous Canary Diagnostic Probes
For intermittent, non-deterministic bugs—race conditions or memory leaks that trigger once every 50,000 requests—supervisory agents automate diagnostic capture. When a trace exhibits an unmapped error profile, the agent provisions a temporary eBPF-instrumented canary node, routes a small slice of mirrored traffic to it, captures a full execution profile, and packages the data for offline analysis.

### 7. Semantic Security and Contextual PII Hunting
Static regex scanners catch explicit credit card numbers or Social Security patterns, but they fail on contextual leaks—such as account balances serialized inside debug stack traces or customer home addresses split across custom payload fields. An asynchronous supervisory agent audits raw event logs to flag contextual privacy violations that regex patterns miss.

### 8. Qualitative Decision Engines
Historically, software required strict, quantitative data: booleans, integers, enums, and normalized relational schemas. However, real-world business logic frequently involves qualitative, narrative inputs—such as insurance dispute forms, regulatory circulars, or unstructured customer notes. The runtime LLM operates as an adapter, translating qualitative narrative text into typed payloads that standard state machines can execute.

### 9. Telemetry Hygiene and Preserving Operational Intuition
Relying entirely on AI-generated summaries introduces a subtle failure mode: dashboard query rot and the erosion of an engineer's operational instincts. Resilient organizations pair supervisory agents with scheduled chart reviews to audit operational queries, while ensuring engineers still spend time inspecting raw traces and metric distributions.

---

## Conversational Observability: Eliminating the "Dashboard Stare"

Distributed architectures generate an overwhelming volume of telemetry: Prometheus time-series counters, structured JSON logs, and distributed trace graphs powered by [[OpenTelemetry as the Runtime Truth for Autonomous Agents]].

### The Pathology of the Dashboard Stare
When an incident fires across a service mesh, the triage process typically breaks down like this:
* Engineers open dozens of browser tabs, comparing CPU, memory, and latency spikes across multiple services.
* They manually correlate whether a 5% latency jump in Service A stems from connection pool exhaustion in Service B or lock contention in a shared database.
* They battle alert fatigue. Static alerts (`CPU > 85%` or `HTTP 500 rate > 1%`) fire during predictable batch jobs, yet stay silent during slow-burning data corruption bugs that still return HTTP 200 OK.

```text
                       ┌─────────────────────────────────────┐
                       │ Telemetry & Log Ingestion Pipeline  │
                       │ (OpenTelemetry Spans, Metrics, Logs)│
                       └──────────────────┬──────────────────┘
                                          │ Continuous semantic
                                          │ stream inspection
                                          ▼
                       ┌─────────────────────────────────────┐
                       │ Operational Supervisory Agent       │
                       │ - Knows service topology & contracts│
                       │ - Holds operational invariants      │
                       │ - Ingests historical incident data  │
                       └──────────────────┬──────────────────┘
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
         PROACTIVE ALERT SYNTHESIS                       CONVERSATIONAL QUERY
     "Checkout failure rate is 0.4%,             Engineer: 'Is order settlement healthy?'
      but payment gateway retry latency           Agent: 'Settlement is clearing, but
      surged 400ms following deploy #42.          DB lock contention on Table X has
      Correlated trace ID: #a78f2c.               tripled in the last 15 minutes.
      Root cause: unindexed query in Service C."  No SLA breach yet, but exhaustion 
                                                  projected in ~40 minutes.'"
```

By maintaining an up-to-date map of service dependencies, active deployment tags, and interface contracts, a supervisory agent correlates telemetry across system boundaries. It shifts the operational workflow from manually hunting for metric anomalies to verifying specific architectural hypotheses.

---

## The "Traffic Light" Dilemma: Why Green/Amber/Red Fails

Engineering leadership often wants operational health boiled down to a simple status light: **Green (Healthy), Amber (Degraded), and Red (Critical)**. In complex distributed systems, static thresholds make this model borderline useless.

### 1. The "Zombie Green" Illusion
A service can appear completely healthy on an infrastructure dashboard while being fundamentally broken:
* A worker service consumes messages from a Kafka topic at a steady rate, maintaining normal CPU and memory usage.
* Due to an unhandled schema change, the deserialization handler drops every message into an unmonitored dead-letter queue or silently swallows the error.
* Infrastructure monitors show green across the board, but zero business operations are actually succeeding.

### 2. The "False Red" Alarm Storm
Thresholds lack operational context:
* A scheduled batch reconciliation job spins up 64 concurrent workers, driving database connection utilization to 98% and worker queue depth past 20,000 items.
* Alerts fire across Slack, paging engineers for database load, queue depth, and memory consumption.
* However, end-user API endpoints show zero latency degradation, payment processing rates remain steady, and the batch job finishes cleanly within its allotted window.

### 3. Topology-Blind Scalar Thresholds
Traditional monitoring setups evaluate metrics as isolated data points. They have no understanding of the system's underlying directed acyclic graph (DAG):

```text
           [ Edge API Gateway ]
              /            \
             ▼              ▼
   [ Checkout Service ]   [ Recommendation Service ]
           |                       |
           ▼                       ▼
   [ Payment Ledger ]     [ Vector Search Cache ]
      (CRITICAL)               (BEST-EFFORT)
```

A 5% packet loss rate on the vector search cache path triggers the same alerting severity as a 5% packet loss rate on the payment ledger path, even though the recommendation failure can be masked with a simple fallback.

### Invariant-Aware Conversational Queries
When an operational supervisor understands service dependencies and codified business rules, engineers can query the system based on operational guarantees rather than individual metrics:

```text
Engineer:
"Are all business invariants holding across the checkout-to-settlement pipeline after the 14:00 release?"

Telemetry Agent:
"Status: AMBER.
Invariant Violation: Invariant #4 ('OrderAuthorized must emit PaymentReserved within 90 seconds') is degrading.
Details: Over the last 15 minutes, 3.2% of transactions took longer than 90 seconds (p99 spiked from 12s to 118s).
Causal Path: Thread pool starvation in BillingService.Worker caused by connection pool limits on the PostgreSQL replica.
Downstream Impact: Financial ledger invariants remain consistent (GREEN). No data dropped.
Primary Trace Context: trace_id=4bf92f3577b34da6a3ce929d0e0e4736, span_id=00f067aa0ba902b7."
```

---

## Cadence-Based Asynchronous Telemetry & Autonomous Canary Probes

To make telemetry analysis computationally viable and cost-effective, high-throughput systems separate raw collection from model inference.

```text
High-Volume Raw Telemetry Stream (100k events/sec)
                      │
                      ▼
       ┌──────────────────────────────┐
       │ Statistical Anomaly Filter   │ (Prometheus / OpenTelemetry Collector)
       │ & Sliding Window Aggregator  │
       └──────────────┬───────────────┘
                      │ Batched summaries every 5–15 mins
                      │ OR immediate trigger on statistical anomaly (p99 spike)
                      ▼
       ┌──────────────────────────────┐
       │ Asynchronous Reasoning Agent │
       │ - Evaluates correlated spans │
       │ - Maps dependencies          │
       │ - Compares against baseline  │
       └──────────────┬───────────────┘
                      ▼
       High-Signal Operational Intelligence at a Fraction of the Token Cost
```

### Implementing Cadence-Based Telemetry Ingestion
Instead of streaming every trace to an LLM, use an OpenTelemetry Collector pipeline coupled with an asynchronous worker. The collector uses a sliding window to identify latency shifts or error rate spikes, forwarding only anomalous trace structures:

```python
from pydantic import BaseModel, Field
from typing import List, Optional
import json

class AnomalyContext(BaseModel):
    service_name: str
    metric_name: str
    observed_value: float
    threshold_value: float
    window_duration_seconds: int
    exemplar_trace_ids: List[str]

class OperationalDiagnosis(BaseModel):
    root_cause_hypothesis: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    affected_services: List[str]
    suggested_mitigation: str
    requires_human_approval: bool
    diagnostic_invariants_violated: List[str]

def evaluate_telemetry_anomaly(anomaly: AnomalyContext, span_graph_summary: dict) -> OperationalDiagnosis:
    """
    Asynchronously called when the statistical aggregator detects an anomaly.
    Uses an LLM to evaluate the topology graph and trace exemplars.
    """
    system_prompt = (
        "You are an expert site reliability engineer. Evaluate the following distributed trace "
        "anomaly and span topology. Provide a structured causal analysis. Return strictly valid JSON "
        "matching the OperationalDiagnosis schema."
    )
    
    user_payload = {
        "anomaly": anomaly.model_dump(),
        "topology_context": span_graph_summary
    }

    # Low temperature inference to minimize variance
    raw_response = call_llm(
        system=system_prompt,
        user=json.dumps(user_payload),
        temperature=0.0,
        response_format={"type": "json_object"}
    )
    
    # Strictly validate the model's output before passing it down the pipeline
    return OperationalDiagnosis.model_validate_json(raw_response)
```

### Autonomous Canary Diagnostic Probes
For subtle, non-deterministic bugs—like a thread-safety issue that only triggers under specific memory pressure—supervisory agents automate diagnostic capture:

1. **Automated Triage Dossier**: When an uncaught exception spikes in production, the agent pulls the trace context, inspects recent Git commits to the associated repository, flags changed lines, and generates an incident report containing the offending stack trace and relevant diffs.
2. **Autonomous Canary Deployment**: If an error pattern resists offline diagnosis, the agent provisions an isolated canary pod instrumented with extended profiling tools:
   * Attaches dynamic eBPF tracepoints (`kprobe`, `uprobe`) to track internal function arguments and system calls without changing application source code.
   * Configures automatic heap dumps or process memory dumps if latency spikes past a set limit.
   * Mirrors a small percentage of sanitized production traffic to the canary instance to capture reproduction payloads safely.

```text
Production Traffic
       │
       ├──► Normal Cluster Pods (99%)
       │
       └──► Canary Pod (1% Mirrored)
                 │
                 ├── eBPF Dynamic Tracing (Tracing syscalls/allocations)
                 ├── Memory Threshold Trigger ──► Core Dump / Heap Profile
                 └── Isolation Boundary ──► DB writes redirected to mock sandbox
```

---

## Semantic Security Log Triaging and Threat Hunting

Standard Security Information and Event Management (SIEM) tools rely on deterministic signatures and static thresholds (e.g., `Failed Logins > 5 in 60s → Flag IP`). Attackers regularly bypass these checks by running slow, distributed credential-stuffing attacks across thousands of IP addresses.

A semantic security analyzer looks at the behavioral intent across user event streams rather than matching isolated string signatures:

### 1. Fuzzy Sequence Analysis
Consider an authenticated user session executing the following API calls over two hours:
* `GET /api/v1/users/me`
* `GET /api/v1/organizations/12/members?page=1&limit=5`
* `GET /api/v1/organizations/12/members?page=2&limit=5`
* `GET /api/v1/reports/export?format=csv&range=custom`

Each call returns an HTTP 200 OK and falls well within normal rate limits. A standard SIEM sees nothing wrong. However, an LLM evaluating the sequence can recognize the pattern: an account enumerating users and exfiltrating data right after an unexpected session token refresh.

### 2. Detecting Contextual PII and Data Leaks
Regex scanners are great at finding explicit patterns like standard credit card numbers or Social Security formats. They fail completely when the data leak is contextual:

```text
[2024-10-24 16:42:10.102] DEBUG billing_reconciler.go:88 
Payload unmarshal failed for customer reference. 
Context dump: {
  account_id: "acc_8921", 
  raw_memo: "Transferring remaining balance of $42,500.00 from offshore escrow account to Jane Doe, pending final divorce decree settlement."
}
```

A standard regex scanning for credit card formats sees this as normal text. A semantic supervisor processing log batches flags the payload immediately:

```json
{
  "log_event_id": "log_99a82b",
  "contains_pii": true,
  "data_category": "ConfidentialFinancialAndLegalDetail",
  "confidence": 0.98,
  "redaction_target": "Transferring remaining balance of $42,500.00 from offshore escrow account to Jane Doe, pending final divorce decree settlement.",
  "justification": "Log event exposes explicit financial values tied to named individuals and legal proceedings within an unencrypted debug field."
}
```

---

## Consuming Unstructured Qualitative Data: The Runtime Decision Engine

Historically, computers required clean, structured inputs to make decisions. But much of the information businesses handle is messy, qualitative narrative: insurance claims, regulatory updates, dispute descriptions, and contract clauses.

A common anti-pattern is letting an LLM make an end-to-end decision and directly trigger downstream actions. A much safer approach uses the LLM as a translation layer: it parses the messy, qualitative text into a strongly typed, validated schema, which a deterministic state machine then evaluates against business rules.

```text
Incoming Unstructured Narrative
(e.g., complex insurance claim description / regulatory amendment)
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│  Runtime LLM Evaluator                                 │
│  - Prompt contains strict domain invariants            │
│  - Few-shot examples of boundary decisions             │
│  - Temperature = 0.0 (deterministic inference)         │
└───────────────────┬────────────────────────────────────┘
                    │ Structured JSON Output
                    ▼
┌────────────────────────────────────────────────────────┐
│  Deterministic Execution Envelope                      │
│  - Validates schema against strict Pydantic/Zod types  │
│  - Executes business invariants                        │
│  - Rejects execution if invariant validation fails     │
└───────────────────┬────────────────────────────────────┘
                    │
                    ▼
Deterministic Business Workflow Engine (Saga / State Machine)
```

### Implementing the Decision Envelope

Here is an example showing how an unstructured dispute description is parsed into a structured decision, passed through a validation envelope, and then executed within a deterministic state machine:

```python
from enum import Enum
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional

class DisputeReason(str, Enum):
    UNAUTHORIZED_CHARGE = "UNAUTHORIZED_CHARGE"
    MERCHANDISE_NOT_RECEIVED = "MERCHANDISE_NOT_RECEIVED"
    INCORRECT_AMOUNT = "INCORRECT_AMOUNT"
    SUBSCRIPTION_CANCELED = "SUBSCRIPTION_CANCELED"
    UNCATEGORIZED = "UNCATEGORIZED"

class ClaimProposal(BaseModel):
    """Structured proposal generated by the LLM."""
    dispute_reason: DisputeReason
    claimed_amount_cents: int = Field(gt=0, description="Amount in cents, must be positive.")
    merchant_contacted: bool
    incident_date_iso: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    extracted_summary: str = Field(max_length=500)

class GatedExecutionResult(BaseModel):
    approved_for_auto_refund: bool
    requires_human_escalation: bool
    rejection_reason: Optional[str] = None
    applied_rules: List[str]

def process_dispute_envelope(raw_user_narrative: str, transaction_amount_cents: int) -> GatedExecutionResult:
    """
    Executes the Deterministic Decision Envelope pattern:
    1. Extracts structured proposal from unstructured text via an LLM.
    2. Validates schema strictly (rejecting hallucinated/malformed types).
    3. Runs deterministic invariant checks against backend transaction records.
    """
    # Step 1: LLM Inference
    raw_llm_json = invoke_llm_extractor(raw_user_narrative)

    # Step 2: Strict Schema Parsing
    try:
        proposal = ClaimProposal.model_validate_json(raw_llm_json)
    except ValidationError as e:
        # If the model fails to return a valid schema, fail safely to human review
        return GatedExecutionResult(
            approved_for_auto_refund=False,
            requires_human_escalation=True,
            rejection_reason=f"Schema validation failure: {str(e)}",
            applied_rules=["SAFETY_FALLBACK_SCHEMA_ERROR"]
        )

    applied_rules = []
    
    # Step 3: Enforce Deterministic Invariants
    # Rule 1: The claimed amount cannot exceed the original transaction value
    if proposal.claimed_amount_cents > transaction_amount_cents:
        return GatedExecutionResult(
            approved_for_auto_refund=False,
            requires_human_escalation=True,
            rejection_reason="Claimed amount exceeds the original transaction value.",
            applied_rules=["INVARIANT_AMOUNT_CEILING_EXCEEDED"]
        )
    applied_rules.append("INVARIANT_AMOUNT_CEILING_PASSED")

    # Rule 2: Low-confidence proposals must always be reviewed by a human
    if proposal.confidence_score < 0.85:
        return GatedExecutionResult(
            approved_for_auto_refund=False,
            requires_human_escalation=True,
            rejection_reason="Model confidence score below automated clearing threshold.",
            applied_rules=["CONFIDENCE_THRESHOLD_UNMET"]
        )
    applied_rules.append("CONFIDENCE_THRESHOLD_PASSED")

    # Rule 3: Direct automated refunds are capped at $50.00 (5000 cents)
    MAX_AUTO_REFUND_CENTS = 5000
    if proposal.claimed_amount_cents <= MAX_AUTO_REFUND_CENTS and proposal.dispute_reason == DisputeReason.UNAUTHORIZED_CHARGE:
        applied_rules.append("FAST_TRACK_REFUND_ALLOWED")
        return GatedExecutionResult(
            approved_for_auto_refund=True,
            requires_human_escalation=False,
            rejection_reason=None,
            applied_rules=applied_rules
        )

    # Default: route to standard human review workflows
    applied_rules.append("STANDARD_REVIEW_ROUTING")
    return GatedExecutionResult(
        approved_for_auto_refund=False,
        requires_human_escalation=True,
        rejection_reason=None,
        applied_rules=applied_rules
    )

def invoke_llm_extractor(text: str) -> str:
    # Stub representing deterministic, low-temperature LLM generation
    return """
    {
      "dispute_reason": "UNAUTHORIZED_CHARGE",
      "claimed_amount_cents": 2499,
      "merchant_contacted": true,
      "incident_date_iso": "2024-10-23T14:30:00Z",
      "confidence_score": 0.94,
      "extracted_summary": "User noticed an unauthorized $24.99 charge from a subscription service they canceled last month."
    }
    """
```

In this architecture, the LLM does not decide to issue the refund. It simply extracts the facts from the messy narrative. The code then deterministically verifies those facts against the transaction database and business policies, deciding whether to auto-refund, route to a manual queue, or reject the claim.

---

## Operational Lessons: Telemetry Hygiene and the "Tacit Knowledge" Risk

Deploying supervisory agents into production environments reveals several hard lessons about telemetry pipelines and team dynamics:

### 1. The Broken Window Effect in Logs
LLMs are sensitive to noise. If your microservices continuously emit meaningless warning logs, noisy unhandled exceptions, and abandoned trace spans, the agent's context window fills up with garbage. Implementing an operational agent usually forces teams to clean up their telemetry: fixing broken log levels, consolidating trace spans, and removing uninformative logs.

### 2. Dashboard Query Drift
Teams that rely entirely on conversational agents often stop looking at their Grafana dashboards. Over time, those queries rot: metric names change, dashboards reference deprecated labels, and alert configurations drift out of date. To prevent this:
* Treat dashboards as code, storing definitions alongside service implementations in Git.
* Run monthly **Chart Reviews** where the team walks through operational dashboards to verify that queries, alerts, and SLO mappings still match the live architecture.

### 3. Preserving Operational Intuition
If junior engineers only ever read AI-generated summaries, they struggle to build an intuitive mental model of how the system behaves under load. High-performing teams address this by having on-call engineers spend time inspecting raw traces, profiling real requests, and verifying the supervisory agent's reasoning against raw telemetry.

---

## Summary of System Interactions

| Architectural Boundary | Input Data Type | Processing Mechanism | Safety Gate | Terminal Output |
| :--- | :--- | :--- | :--- | :--- |
| **Conversational Observability** | Raw OTel traces, Prometheus metrics, system logs | Asynchronous batch reasoning (5–15 min sliding window) | Static topology assertion & span correlation | Natural-language incident summaries & exemplar trace links |
| **Autonomous Canary Diagnostics** | Unmapped exceptions & edge-case latency spikes | Automated eBPF probe provisioning & canary deployment | Sandboxed execution; mocks all external mutations | Full heap dumps, system call profiles, and reproduction traces |
| **Semantic Security Hunting** | Authenticated session logs & distributed event streams | Sequence-aware semantic evaluation | Deterministic SIEM block-lists & schema validation | Prioritized incident dossiers and contextual PII redaction alerts |
| **Runtime Decision Engine** | Unstructured narrative text (claims, disputes) | Low-temperature structured extraction (`temperature=0.0`) | Strict schema parsing (Pydantic) & deterministic invariant validation | Typed payloads driving deterministic state machines (Sagas) |

---

## Architectural Graph References

* **[[OpenTelemetry as the Runtime Truth for Autonomous Agents]]**: The underlying distributed tracing, metrics, and log context structures that feed supervisory agents.
* **[[Service-to-Service Communication - How Service A Should Call Service B]]**: Network protocols, retries, and circuit-breaking patterns that shape runtime telemetry graphs.
* **[[Designing Software for AI Agents]]**: Interface contracts, structured tool definitions, and isolation patterns for operational models.
* **[[Workflow Orchestration in Agentic Systems]]**: State machines, sagas, and long-running execution engines that consume structured decision payloads.
* **[[Formal Verification and Runtime Safety Boundaries]]**: Deterministic assertions and runtime invariant checks that constrain probabilistic models in production.
* **[[Proactive Software - From Reactive Systems to Autonomous Agents]]**: Moving from passive metric dashboards to proactive supervisory systems monitoring production state.
