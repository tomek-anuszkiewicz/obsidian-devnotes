---
title: Proactive Software — From Reactive Systems to Autonomous Agents
tags:
  - proactive-agents
  - autonomous-systems
  - software-architecture
  - ai-agents
  - system-design
  - user-experience
aliases:
  - Proactive Software - From Reactive Systems to Autonomous Agents
  - Reactive to Proactive Software
  - Autonomous Proactive Agents
---

Traditional software is mostly reactive.

A user clicks a button, submits a form, calls an API, creates a ticket, or triggers some predefined event. The system then executes a known procedure and returns a result.

The dominant interaction model has historically looked like this:

```text
human
  ↓
explicit request
  ↓
software
  ↓
predefined logic
  ↓
result
```

Even automation has usually followed the same philosophy.

A scheduled job may run every hour. A monitoring system may send an alert when CPU exceeds 90%. A workflow may execute when a new record appears in a database.

These systems can act without a human pressing a button, but their behavior is still highly predefined.

Agentic systems introduce a different possibility.

Software can continuously observe some part of the world, decide whether something interesting is happening, gather additional context, formulate hypotheses, propose actions, and sometimes execute them (see [[Workflow Orchestration in Agentic Systems]]).

The interaction model becomes closer to:

```text
observe
  ↓
detect something potentially important
  ↓
investigate
  ↓
evaluate
  ↓
decide whether action is justified
  ↓
act / recommend / escalate
  ↓
observe the result
```

This creates the possibility of **proactive software**: systems that do not merely wait for instructions, but continuously search for things worth doing.

---

## Reactive automation already exists

None of the individual building blocks are entirely new.

We already have:

- cron jobs,
    
- event-driven architectures,
    
- monitoring alerts,
    
- workflow engines,
    
- rules engines,
    
- scheduled reports,
    
- background workers,
    
- automated trading systems,
    
- recommendation systems,
    
- anomaly detection.
    

The difference is that these systems traditionally require humans to define relatively explicit conditions and procedures.

For example:

```text
IF error_rate > 5%
THEN send alert
```

or:

```text
EVERY Monday
RUN dependency report
```

An agent can receive a substantially less formal objective:

> Look for signs that production quality is deteriorating and investigate anything that appears meaningful.

There may be no single metric, threshold, or algorithm capable of expressing that requirement.

The agent can inspect several data sources, compare time periods, notice a novel pattern, investigate deployments, and decide whether the observation is likely to matter.

That expands the range of work that can be automated.

In production, a latency spike during a batch backfill is benign, but that exact same spike is fatal if paired with database connection pool exhaustion and a recent commit that modified connection acquisition logic. An agent can query telemetry, pull recent merge requests, and correlate distributed traces across service boundaries to determine whether the observed pattern warrants intervention.

---

# What proactive agents look for

Proactive agents can monitor change, detect anomalies, find opportunities or risks, investigate signals, and prepare action. A sales agent may look for promising customers while an SRE agent looks for a production problem, but both follow the same observe–investigate–evaluate loop. [[Patterns of Proactive Agent Behavior]] develops those recurring behaviors and domain examples. Detecting a signal is only the first step; the operating model must decide whether it deserves attention or action.

---

# Agents as organizational watchers

One possible future architecture is an organization containing many specialized watchers.

```text
watch production
watch customers
watch costs
watch security
watch dependencies
watch regulations
watch competitors
watch contracts
watch infrastructure
watch repositories
watch documentation
watch hiring
watch suppliers
```

Each watcher does not necessarily perform large autonomous tasks.

Its job may simply be to continuously observe one domain and produce structured signals.

Those signals can then flow into another layer.

```text
many observers
      ↓
candidate findings
      ↓
deduplication
      ↓
evidence validation
      ↓
priority assessment
      ↓
risk / cost / confidence
      ↓
ignore / record / recommend / act
```

This hierarchy may be more scalable than giving every agent complete autonomy.

Each watcher maintains a tight blast radius, continuously observing its subsystem and emitting structured events with high-fidelity context. Downstream aggregator services deduplicate alerts, correlate findings with deployment metadata, calculate confidence scores, and determine whether a finding warrants autonomous remediation, a staged pull request, or immediate human escalation.

---

# The new scarcity: attention

A critical problem appears immediately.

If autonomous agents become good at finding things worth doing, they may find far more things than humans can process.

Suppose:

```text
100 agents
×
5 findings per day
=
500 recommendations per day
```

The organization has not gained intelligence.

It has created another notification system.

Therefore proactive software requires aggressive filtering.

A useful agent should not merely answer:

> Can I find something?

It must answer:

> Is this important enough to interrupt someone?

This introduces concepts such as:

- confidence,
    
- expected value,
    
- urgency,
    
- reversibility,
    
- cost,
    
- risk,
    
- novelty,
    
- severity.
    

The ability to **ignore** may become as important as the ability to detect.

Silently discarding low-value findings is what separates a reliable proactive platform from an unmaintainable noise generator. If an agent surfaces 5 findings a day across 100 systems, engineers will simply mute the channels. Evaluating reversibility, operational blast radius, and whether the expected value exceeds the human review cost ensures the system protects engineering attention rather than consuming it.

---

# Autonomy levels

Not every proactive agent should have the same authority.

A practical architecture can define several levels.

## Observe

The agent only gathers information.

```text
observe → record
```

## Notify

The agent decides that something deserves human attention.

```text
observe → investigate → notify
```

## Recommend

The agent produces a proposed course of action.

```text
observe → investigate → recommend
```

## Prepare

The agent prepares the action but does not execute it.

Examples:

- draft an email,
    
- create a PR,
    
- prepare an infrastructure change,
    
- prepare a purchase order.
    

```text
observe → investigate → prepare → human approval
```

## Act

The agent executes within predefined limits.

```text
observe → decide → execute → verify
```

## Delegate

The agent can create work for another agent or human.

```text
observe
   ↓
investigate
   ↓
classify problem
   ↓
delegate to specialist
```

This model allows autonomy to increase gradually as confidence in a workflow grows.

Teams can grant Level 1 (Observe) authority immediately across all systems, promoting agents to Level 4 (Prepare) or Level 5 (Act) only after diagnostic accuracy and deterministic guardrails have proven reliable over time.

---

# Agents that create work for other agents

An especially interesting development is that one proactive agent does not need to solve everything itself.

Consider an operational watcher:

```text
production watcher
        ↓
detects regression
        ↓
investigation agent
        ↓
identifies probable code change
        ↓
coding agent
        ↓
creates candidate fix
        ↓
review agent
        ↓
PR
```

No single agent needs to understand the entire process.

The system behaves more like an organization of specialized workers.

This may eventually create software systems containing thousands of small, persistent responsibilities rather than a few giant universal agents.

Constraining each agent to a single boundary keeps the system reliable. The diagnostic watcher does not modify code, the remediation agent does not deploy to production, and deterministic CI test suites gate every step. This strict separation of concerns mirrors high-performing engineering teams.

---

# From explicit workflows to objectives

The deeper transition is from specifying procedures to specifying objectives.

Traditional automation:

> Every night at 01:00, query table X and alert if value Y exceeds 100.

Agentic automation:

> Keep an eye on this subsystem and tell us if its behavior appears to be deteriorating.

Traditional automation:

> Check whether package versions differ from this list.

Agentic automation:

> Keep this platform reasonably current and tell us when an upgrade becomes worthwhile.

Traditional automation:

> Search this database using these filters.

Agentic automation:

> Continuously look for potential customers that fit our business.

This does not eliminate deterministic software.

Quite the opposite.

Agents should still rely heavily on deterministic tools for execution and verification.

The change happens mainly at the decision layer.

```text
objective
   ↓
agent decides what to inspect
   ↓
deterministic tools provide facts
   ↓
agent interprets facts
   ↓
deterministic systems execute allowed actions
```

---

# Software that initiates work

Historically, humans have been the primary source of intent.

Humans decide:

- there is a problem,
    
- something should be investigated,
    
- an optimization is needed,
    
- a supplier should be changed,
    
- a customer should be contacted,
    
- a system should be upgraded.
    

Software then assists with execution.

With proactive agents, software can begin generating candidate intent itself.

It can say:

> I noticed something.

> I investigated it.

> I believe this matters.

> Here is what I think should happen.

This does not mean software should autonomously control every decision.

It means software is no longer restricted to waiting for humans to formulate every problem first.

The human role shifts from discovering raw symptoms and manually orchestrating fixes to evaluating hypotheses and acting as a policy governor over automated execution.

---

# The important boundary: agency versus uncontrolled activity

Proactivity has obvious failure modes.

An agent that is rewarded for finding optimizations will always find optimizations.

An agent searching for risks will always find risks.

A sales agent may contact too many people.

A maintenance agent may continuously propose unnecessary upgrades.

An optimization agent may make the system harder to understand in exchange for negligible savings.

An unconstrained agent will aggressively optimize for its narrow objective: flooding git logs with trivial refactoring pull requests, flagging theoretical security edge cases that cannot be exploited, or terminating idle compute instances that were intentionally pre-warmed for batch traffic.

Therefore agents need explicit stopping and filtering criteria.

The system should reason not only about:

> Can this be improved?

but also:

> Is improving it worth the disruption?

A mature proactive system therefore needs some equivalent of organizational judgment:

```text
potential action
      ↓
expected value
      ↓
confidence
      ↓
cost
      ↓
risk
      ↓
urgency
      ↓
reversibility
      ↓
priority
```

Without this layer, proactive software becomes hyperactive software.

---

# A broader implication

The major opportunity of agentic systems may not be that they let humans perform existing tasks faster.

It may be that they enable completely new classes of software behavior.

Traditional software waits.

Agentic software can watch.

Traditional software processes requests.

Agentic software can discover that a request should exist.

Traditional monitoring reports signals.

Agentic monitoring can investigate them.

Traditional automation follows procedures.

Agentic automation can decide which procedure is appropriate.

Traditional systems execute work.

Proactive systems can **find work worth doing**.

That may ultimately be one of the most important consequences of agentic computing:

> **Software changes from a passive tool operated by humans into an active participant that continuously observes its environment, identifies problems and opportunities, and initiates useful work** (see [[Embedding LLMs in Runtime Decision Paths and Operational Telemetry]]).

## Related notes

- **[[Patterns of Proactive Agent Behavior]]** — The recurring search, investigation, and proposal patterns behind proactive agents.
- **[[Workflow Orchestration in Agentic Systems]]** — Architecture for multi-step agent execution, fan-out, and checkpoints.
- **[[Embedding LLMs in Runtime Decision Paths and Operational Telemetry]]** — Integrating probabilistic models into live operational paths.
- **[[Building Determinism from Unpredictable Models]]** — Harness engineering to constrain agent behavior and enforce invariants.
- **[[OpenTelemetry — Architecture, Signals, and Collector]]** — Standardized distributed tracing and metrics that empower proactive diagnostic agents.
