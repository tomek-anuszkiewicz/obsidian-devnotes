---
title: Continuous Security Monitoring with Agents
tags:
  - security
  - ai-agents
  - observability
  - incident-response
  - anomaly-detection
  - monitoring
aliases:
  - AI Security Watchers
  - Always-On Security Agent
  - Agentic Security Monitoring
  - Continuous Security Triage with LLMs
---

# Continuous Security Monitoring with Agents

A login succeeds from a new device, a service account reads an unusual set of records, and an export job starts ten minutes later. Each event may look ordinary in isolation. A security agent can put them in order, retrieve the relevant policy and recent changes, and prepare a case for an analyst. This is the same sequence-based opportunity shown in [[Embedding LLMs in Runtime Decision Paths and Operational Telemetry]], extended into a continuous security workflow.

The agent is useful as a tireless investigator of *candidate* events, not as an infallible guard. It does not need to read every raw packet or camera frame through an LLM. Cheap collectors, access rules, signatures, and anomaly detectors can select events; the model then connects evidence across logs, identity systems, endpoints, cloud audit records, and network-flow summaries. Continuous coverage comes from the monitoring system's schedule and queues, not from a model that is somehow always thinking (see [[Patterns of Proactive Agent Behavior]]).

## Give the agent a bounded investigation loop

For each candidate, the agent should identify the triggering event, fetch a limited time window and relevant entities, compare them with expected behavior, and produce an evidence-backed finding. A useful finding names the user or service identity, affected resource, event times, source records, competing explanations, and the next check that would resolve uncertainty. It should link to the original events so an analyst can verify the story.

This can cover known patterns such as a privilege change followed by a data export, or unexpected combinations that a single threshold misses. Fixed rules still handle well-defined cases quickly and predictably. The model helps where relationships across systems or natural-language context matter. [CISA's logging guidance](https://www.cisa.gov/audiences/small-and-medium-businesses/secure-your-business/use-logging-on-business-systems) describes central collection and monitoring of activity from servers, firewalls, endpoints, and cloud services; [NIST's DevSecOps reference model](https://pages.nist.gov/nccoe-devsecops/notational-reference-model.html) treats AI log analysis as a way to surface abnormal results for human review.

## Physical signals need stronger evidence

An authorized security system might join a badge event, visitor schedule, door sensor, and camera alert. If someone enters when no visit is expected, the agent can assemble the timeline and ask an operator to check it. A camera image alone is weak evidence of identity: lighting, occlusion, look-alikes, and incomplete enrollment can all mislead the system. Do not let a model's visual guess automatically declare an employee an intruder or grant access. Physical monitoring also needs a clear purpose, restricted access, retention limits, and human handling of ambiguous cases.

## Keep detection separate from response

A read-oriented agent can gather evidence and recommend containment. Revoking an account, blocking an address, disabling a service, or calling emergency staff changes the world and needs a separate policy gate. Some narrow responses may be automated under preapproved deterministic rules; the model should not acquire broad administrative credentials just because it can explain why an event looks suspicious (see [[Security Boundaries for Agents, RAG, and MCP]]).

Security logs and tickets are also attacker-influenced input. A malicious URL, email subject, or log field can contain instructions addressed to the agent. Treat those fields as evidence, never as authority to run a command or send data. Scope the agent's read access and outbound channels, and avoid copying raw personal or confidential content into case summaries when an event reference is enough (see [[Agent-Assisted Sensitive Data Exposure Audits]]).

Measure the workflow against reviewed incidents and ordinary activity: what it missed, what it flagged unnecessarily, how long triage took, and whether analysts could verify each claim. When too many weak alerts arrive, the “tireless guard” merely moves the fatigue to the human team. The agent earns its place by making a smaller number of well-supported cases easier to investigate.

## Related notes

- **[[OpenTelemetry — Architecture, Signals, and Collector]]** — Collecting traces and logs that form part of the evidence stream.
- **[[Proactive Software — From Reactive Systems to Autonomous Agents]]** — Deciding when a detected signal deserves attention or action.
- **[[Always-On Autonomous Agents - The 24-7 Local Operating System]]** — Operating a persistent agent with bounded tools and cost.
- **[[Embedding LLMs in Runtime Decision Paths and Operational Telemetry]]** — Sequence-based security analysis and sensitive-log classification at runtime.
