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

Most discussion of AI in software still focuses on generating code before deployment. There is another architectural shift worth examining: using a language model while the system runs, to inspect telemetry or interpret input that ordinary rules cannot easily classify.

The path is straightforward: collect an input or telemetry stream, filter it with ordinary code, ask the model for a structured assessment, check that assessment against fixed rules, and only then let the system act. The model can correlate events across services, extract facts from narrative input, spot sensitive information in logs, or suggest a diagnostic probe. It must not be the component that commits a transaction or calls a mutation API on its own.

That last boundary matters. A model's output is a proposal. Schema checks, transaction rules, and business invariants decide whether the proposal can change state or trigger an external call. Code generated before deployment still goes through a compiler and the usual release path; a model invoked during a live request or telemetry review needs those checks at runtime.

## What changes when the model runs in production

### Turn scattered signals into structured input

A build-time assistant helps an engineer write code. A runtime model receives logs, traces, user text, or third-party payloads and turns ambiguous input into a typed result that another component can use. That makes it an active part of a production workflow, so its failures and permissions become architectural concerns.

### Spend less incident time switching between dashboards

During an incident, engineers may spend 30–45 minutes comparing metrics across many Grafana dashboards. An operational agent can work downstream of OpenTelemetry collectors, metric aggregators, and log pipelines. With the service topology and business rules in view, it can connect signals across services and present a specific hypothesis for an engineer to verify.

### Check business outcomes alongside infrastructure metrics

Two familiar monitoring failures show why a single health light is misleading:

- **Zombie green:** CPU sits at 20%, memory is stable, and requests return HTTP 200, while a worker drops messages, serialization failures poison a queue, or database rows never get written.
- **False red:** A nightly batch pushes queue depth past a threshold and pages someone at 3:00 AM, while user latency and business SLAs remain unaffected.

The useful question is whether the required business transactions still complete across service boundaries. Infrastructure thresholds remain signals, but they do not answer that question alone.

### Keep the model inside a checked execution path

Do not give the model unrestricted database credentials, arbitrary code execution, or direct access to APIs that change state. Have it return a structured JSON proposal. Validate the schema with a tool such as Pydantic or Zod, then check the relevant state-machine rules and business invariants before writing data or calling an external service.

### Filter telemetry before inference

Sending 100,000 raw events per second to a model would overwhelm rate limits and cost. A sliding-window filter can first compute baselines and find anomalies, using Redis, Apache Flink, or PromQL aggregations. Send the model correlated trace groups that warrant analysis, typically every 5–15 minutes; a statistical anomaly such as a p99 spike can also trigger an immediate review.

### Capture evidence for hard-to-reproduce failures

A race or leak that occurs once in 50,000 requests is difficult to diagnose from routine logs. When a trace shows an unfamiliar error pattern, an agent can prepare an isolated, instrumented canary, mirror a small amount of traffic to it, capture execution data, and package that evidence for offline analysis.

### Look for leaks that have no simple string pattern

Regex rules catch recognizable credit card or Social Security number formats. They may miss an account balance inside a debug trace or an address spread across custom payload fields. An asynchronous review of event logs can flag these contextual exposures.

### Parse narrative input for ordinary business code

Insurance disputes, regulatory notices, and customer notes do not arrive as booleans and enums. A model can extract typed fields from those narratives. A conventional state machine then applies the business rules to those fields.

### Keep dashboards and human judgment in use

If the team reads only model summaries, dashboard queries can drift and engineers can lose familiarity with raw system behavior. Review charts and queries on a schedule, and keep checking traces and metric distributions directly.

## Investigating incidents through telemetry

Distributed systems produce Prometheus time series, structured JSON logs, and trace graphs linked by [[OpenTelemetry — Architecture, Signals, and Collector]]. During an incident, engineers open several dashboards and try to work out whether, for example, a 5% latency increase in Service A comes from Service B's connection pool or contention in a shared database. Static alerts such as `CPU > 85%` and `HTTP 500 rate > 1%` may fire during a predictable batch while missing data corruption behind successful HTTP responses.

An operational agent can use service dependencies, deployment tags, interface contracts, business invariants, and incident history to put those signals in context. Instead of asking an engineer to search for a matching chart, it can point to a trace and a likely path through the services. For example, it might report a 0.4% checkout failure rate, a 400 ms rise in payment gateway retry latency after deploy #42, trace `#a78f2c`, and an unindexed query in Service C as its root-cause hypothesis. An engineer could also ask whether order settlement is healthy and receive a report that settlement still clears, but lock contention on Table X has tripled in 15 minutes, with pool exhaustion projected in about 40 minutes. Those conclusions remain hypotheses to check against the traces.

## Why a green, amber, or red light can mislead

Leadership may want one status for the whole system. Static thresholds cannot represent what matters on every dependency path.

### Green infrastructure, failed work

A Kafka worker may consume at a normal rate with ordinary CPU and memory use. After a schema change, its deserializer may send every message to an unmonitored dead-letter queue or swallow the error. The infrastructure dashboard stays green while no business operation succeeds.

### Red metrics, healthy service

A scheduled reconciliation job may start 64 workers, drive database connection use to 98%, and push the queue above 20,000 items. Slack alerts page engineers about the database, queue, and memory. Yet user-facing API latency does not change, payments continue at the normal rate, and the batch finishes within its window.

### The same metric on different paths

Consider an edge gateway leading to a checkout service and payment ledger on one branch, and a recommendation service and vector search cache on another. Five percent packet loss on the ledger path is much more serious than five percent loss on the cache path, where a fallback can cover the failure. A threshold that sees only the number assigns the same severity to both.

When a supervisor has the dependency map and explicit rules, an engineer can ask about guarantees instead of individual counters:

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

That response ties a broken timing rule to a specific path while saying what still holds: settlement is slow, but the ledger remains consistent and no data was dropped. It gives the engineer trace and span IDs to inspect.

## Inspect telemetry in batches and capture difficult failures

Keep raw collection separate from model inference. An OpenTelemetry Collector pipeline and an asynchronous worker can identify latency shifts or error spikes in a sliding window and forward the relevant trace groups. At a volume of 100,000 events per second, the model sees periodic summaries or an immediate anomaly trigger instead of the entire stream.

The following example passes an anomaly and a span-graph summary to a model, asks for a structured diagnosis, and validates the JSON before the result moves through the pipeline:

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

The `confidence_score` is part of the returned diagnosis, while schema validation ensures that downstream code receives the expected fields and types.

### Build a dossier, then use an isolated canary if needed

When uncaught exceptions rise, an agent can gather trace context, inspect recent Git commits in the relevant repository, mark changed lines, and assemble the stack trace and diffs into an incident report. If that does not explain a failure that appears only under particular memory pressure or timing, it can prepare a canary pod with extra instrumentation:

1. Attach eBPF `kprobe` or `uprobe` tracepoints to inspect function arguments and system calls without changing application source.
2. Trigger a heap or process-memory dump when latency exceeds a set limit.
3. Mirror a small share of sanitized production traffic to the canary to capture a reproduction.

The original example sends 99% of production traffic to normal pods and mirrors 1% to the canary. The canary captures system calls and allocations, and redirects database writes to a mock sandbox. The result is a profile and reproduction evidence for offline analysis.

## Review security events as sequences

SIEM rules often use fixed signatures, such as `Failed Logins > 5 in 60s → Flag IP`. Slow credential-stuffing spread across thousands of IP addresses can stay below a rule like that. A model can review a sequence of events in context rather than treating each request as an isolated string match.

For example, an authenticated session makes these requests over two hours:

- `GET /api/v1/users/me`
- `GET /api/v1/organizations/12/members?page=1&limit=5`
- `GET /api/v1/organizations/12/members?page=2&limit=5`
- `GET /api/v1/reports/export?format=csv&range=custom`

Each returns HTTP 200 and stays below normal rate limits. A rule checking individual calls may see nothing. In sequence, especially after an unexpected session-token refresh, the calls may indicate user enumeration followed by data export.

[[Continuous Security Monitoring with Agents]] extends this example into a running triage loop across identity, endpoint, cloud, and network signals, with evidence for an analyst to verify.

### Find private information from its context

A scanner looking for credit card formats will not recognize every sensitive log entry. Consider this debug event:

```text
[2024-10-24 16:42:10.102] DEBUG billing_reconciler.go:88 
Payload unmarshal failed for customer reference. 
Context dump: {
  account_id: "acc_8921", 
  raw_memo: "Transferring remaining balance of $42,500.00 from offshore escrow account to Jane Doe, pending final divorce decree settlement."
}
```

The sensitive content is the combination of a named person, an account amount, and legal context. A model reviewing batches could flag it with a structured result:

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

This checks one telemetry destination. [[Agent-Assisted Sensitive Data Exposure Audits]] follows the same kind of field through API responses, logs, and storage against an explicit data-flow policy.

## Convert narrative claims into checked decisions

Insurance claims, dispute descriptions, regulatory changes, and contract clauses often arrive as free text. Let the model extract a proposal from that text. Then validate its types and apply business rules in ordinary code. A state machine or Saga can consume the validated result; the model does not get to issue the refund itself.

The original flow gives the model domain rules, examples of boundary decisions, and a low temperature setting. It asks for JSON, validates that JSON with Pydantic or Zod, rejects invalid input, and then passes the result to a deterministic workflow. A low temperature setting reduces variation; the checks after inference are still necessary.

### An example: a customer dispute

This example classifies a dispute and extracts the claimed amount, date, and other fields. If JSON parsing fails, it sends the case to human review. Code then compares the claimed amount with the original transaction, routes proposals below a confidence threshold of 0.85 to review, and allows an automatic refund of at most $50 only for an unauthorized charge. Other cases go to the standard review workflow.

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

The model extracts facts from the customer's story. The transaction record and business policy determine whether the claim can be refunded automatically, needs review, or should be rejected.

## Keep the telemetry useful and the team familiar with it

### Clean up noisy logs

If services produce meaningless warnings, repeated unhandled exceptions, and abandoned spans, those entries consume the model's context and obscure useful evidence. An operational agent makes that problem hard to ignore: fix log levels, consolidate spans, and remove messages that do not help explain behavior.

### Check dashboard queries

When teams stop opening Grafana, metric names change while queries keep referring to old labels and alerts drift out of date. Store dashboard definitions with service code in Git. In a monthly chart review, check that queries, alerts, and SLO mappings still match the running architecture.

### Read the raw evidence

Engineers who only see generated summaries have less opportunity to learn how the system behaves under load. On-call work should still include reading traces, profiling actual requests, inspecting metric distributions, and checking the agent's explanation against the underlying data.

## How the four uses fit together

| Use | Input and model work | Check before use | Result |
| :--- | :--- | :--- | :--- |
| **Incident investigation** | OTel traces, Prometheus metrics, and logs; batch analysis every 5–15 minutes | Check service topology and correlated spans | Incident explanation and links to example traces |
| **Canary diagnostics** | Unfamiliar exceptions or latency spikes; instrument an isolated canary with eBPF | Sandbox execution and mock external mutations | Heap dumps, system-call profiles, and reproduction traces |
| **Security and log review** | Session events and log streams; inspect sequences and contextual leaks | SIEM blocklists and schema validation | Prioritized incident reports and PII redaction alerts |
| **Business decisions from text** | Claims or disputes; extract typed fields at low temperature | Parse the schema and enforce business invariants | Validated input for a state machine or Saga |

## Related notes

- **[[OpenTelemetry — Architecture, Signals, and Collector]]**: Trace, metric, and log context used by operational agents.
- **[[Service-to-Service Communication — How Service A Should Call Service B]]**: Protocols, retries, and circuit breakers that shape traces across services.
- **[[Designing Software for AI Agents]]**: Contracts, structured tools, and isolation for operational models.
- **[[Workflow Orchestration in Agentic Systems]]**: State machines, Sagas, and long-running workflows that consume structured proposals.
- **[[Formal Verification and Runtime Safety Boundaries]]**: Assertions and invariant checks around model output.
- **[[Proactive Software — From Reactive Systems to Autonomous Agents]]**: Moving from passive dashboards to operational agents that monitor production state.
- **[[Agent-Assisted Sensitive Data Exposure Audits]]**: Tracing sensitive fields through APIs, logs, and storage against an explicit data-flow policy.
