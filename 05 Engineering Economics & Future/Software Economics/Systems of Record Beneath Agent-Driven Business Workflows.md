---
title: "Systems of Record Beneath Agent-Driven Business Workflows"
tags:
  - enterprise-software
  - business-architecture
  - ai-agents
  - data-governance
  - software-architecture
aliases:
  - "Stable Enterprise Cores and Dynamic Workflows"
  - "Systems of Record Under Agent Interfaces"
  - "Enterprise Transactions Policies and Agent Coordination"
---

An employee asks an agent to prepare a purchase, check policy, request approval, and follow delivery. The conversational interaction may be new, while supplier records, spending limits, the order, and its audit trail still need clear owners and consistent state.

Separating that interaction from the core system exposes two responsibilities. The agent interprets and coordinates the task. The authoritative systems own records, permissions, rules, and the committed transactions. Replacing a form does not remove the requirements that made the system of record valuable.

The examples below follow ERP, HR, finance, procurement, legal work, and healthcare records. They also distinguish model interpretation from generated deterministic code and the capabilities that platforms need to expose. [[Unbundling of Enterprise Software]] develops the market and packaging consequences; [[Agents as Interfaces to Enterprise Analysis and Work]] follows the corresponding change in analysis and operational interaction.

## ERP: Stable Core, Dynamic Process Layer

ERP systems solve problems that are difficult to reproduce safely:

- accounting consistency;

- auditability;

- financial periods;

- permissions;

- tax rules;

- transaction history;

- multi-entity operations;

- inventory valuation;

- compliance;

- integration with banks and regulators.

These capabilities are likely to remain valuable.

What may change is the surrounding experience.

The ERP of the future may be less:

```text
thousands of screens
+ configuration panels
+ manually designed workflows
```

and more:

```text
trusted transactional core
+ business policies
+ callable capabilities
+ AI-generated processes
```

Companies may buy different core systems from different vendors while agents connect them into a company-specific operating model.

AI becomes the glue between stable transactional components.

The economic defensibility of the core ERP rests on strict invariant validation: general ledger double-entry balance, immutable transaction logs, fiscal period closing locks, and GAAP/IFRS compliance. These guarantees require ACID database transactions and deterministic code rather than probabilistic model generation.

## HR and Human Capital Systems

Core HR data will remain sensitive and regulated.

Systems will still need to store:

- employment records;

- payroll;

- benefits;

- leave;

- taxation;

- legal documents;

- access rules.

AI may absorb many surrounding workflows:

- onboarding;

- document preparation;

- policy questions;

- training recommendations;

- employee requests;

- organizational reporting.

An employee may express a goal rather than navigate several modules:

> I will work from another country for three weeks. Check the policy, prepare the required requests, and show me what needs approval.

The agent coordinates HR, payroll, compliance, calendar, and travel systems.

## Finance and Accounting

The financial core must remain deterministic and auditable.

AI is more likely to transform the work surrounding it:

- matching documents;

- classifying expenses;

- explaining discrepancies;

- preparing corrections;

- investigating unusual transactions;

- forecasting cash flow;

- communicating with suppliers.

The process may move from:

```text
human processes every item
→ system records it
```

toward:

```text
system processes normal items
→ human reviews exceptions
```

The accountant or controller spends less time entering data and more time evaluating anomalies and policy.

## Procurement and Supply Management

A procurement agent could interpret an objective such as:

> Purchase thirty laptops before the end of the month, comply with security standards, use existing supplier agreements, and stay within the budget.

It could:

- inspect approved catalogs;

- compare agreements;

- evaluate delivery risk;

- prepare an order;

- trigger approvals;

- monitor delivery.

The purchasing platform remains responsible for:

- suppliers;

- contracts;

- orders;

- policies;

- audit.

The agent coordinates the full outcome.

## Legal and Compliance Software

Document repositories and approval systems are likely to remain.

AI may handle:

- contract comparison;

- policy checks;

- clause suggestions;

- obligation extraction;

- deadline tracking;

- preparation of approval workflows.

The legal system becomes a controlled source of documents, rules, and decisions.

The agent performs the first layer of analysis and sends ambiguous or high-risk cases to specialists.

In this area, provenance, auditability, and access control become more important than interface design.

## Healthcare Systems

Medical records, prescriptions, billing, and access history cannot be replaced casually.

However, the interaction layer may change substantially.

A clinician may ask:

> Summarize the patient's history, identify new abnormal results, compare them with the previous visit, and prepare a draft note.

The system can generate a temporary clinical view instead of forcing navigation through many screens.

The medical record remains the authoritative source.

AI reorganizes it around the current clinical question.

## What Becomes More Valuable

If fixed screens and manual configuration lose importance, enterprise software will compete on different properties.

The valuable assets may become:

- trustworthy data;

- clear semantic models;

- reliable APIs;

- atomic capabilities;

- business policies;

- permissions;

- transaction guarantees;

- audit trails;

- domain-specific knowledge;

- portability;

- safe integration with agents.

A future enterprise product may be judged by how easily its capabilities can be:

```text
discovered
→ understood
→ composed
→ authorized
→ executed
→ audited
```

by both humans and agents.

This transition fundamentally breaks traditional per-seat SaaS monetization. When autonomous agents replace humans clicking through web forms, seat-based licensing collapses. Defensibility and revenue migrate toward API availability, consumption-based throughput, and the transactional guarantees of the underlying data engine.

At the infrastructure level, this demands robust fine-grained access control. Systems must enforce Attribute-Based Access Control (ABAC) and row-level security across automated callers, coupled with idempotent endpoints that guarantee safe retries and complete transaction rollbacks under network partitions.

## The Role of Generated Code

AI orchestration does not always require an LLM inside every production workflow.

Two approaches may coexist.

### LLM in the execution loop

Useful when the process requires:

- interpretation;

- classification;

- changing context;

- unstructured input;

- judgment among several safe options.

### Agent-generated deterministic code

Useful when the process becomes stable and requires:

- predictable behavior;

- low cost;

- high throughput;

- auditability;

- strong testing;

- strict failure handling.

A workflow may begin as an agentic prototype and later be compiled into ordinary code.

```text
natural-language process
→ agentic prototype
→ observed stable pattern
→ generated deterministic implementation
```

This may become a common lifecycle for business automation.

Compiling an agentic prototype into deterministic code eliminates runtime token overhead, removes stochastic latency variance, and protects hot execution paths from rate limits. Once an agent explores and stabilizes an operational pattern, converting it into typed, tested code ensures sub-millisecond execution and rock-solid error handling.

For an agent-mediated process, identify the authoritative record, the component permitted to change it, the rules that must hold, and the evidence retained after the action. Evaluate a simpler interface separately from any proposal to replace those underlying guarantees.

## Related Notes

- [[Unbundling of Enterprise Software]] — The economics of separating enterprise applications into composable layers.
- [[Agents as Interfaces to Enterprise Analysis and Work]] — Task-oriented analysis and operations over existing platforms.
- [[Workflow Orchestration in Agentic Systems]] — Maintaining the durable process around actions in several systems.
