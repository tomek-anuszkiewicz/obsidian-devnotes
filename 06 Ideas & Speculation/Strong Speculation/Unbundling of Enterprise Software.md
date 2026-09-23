---
title: Unbundling of Enterprise Software
tags:
  - enterprise-software
  - unbundling
  - saas
  - economics
  - custom-software
  - business-architecture
aliases:
  - Enterprise Software Disruption
  - SaaS Unbundling by AI Agents
---

ERP and business intelligence are only two examples of a broader transformation in enterprise software.

The common pattern is a separation between:

- durable systems of record;
    
- business rules and permissions;
    
- analytical and operational capabilities;
    
- workflow orchestration;
    
- user interfaces generated for a specific task.
    

AI may reduce the importance of large, permanently configured applications without eliminating the systems that store data, enforce policy, and execute transactions.

The future may be less about replacing every enterprise platform and more about changing how these platforms are composed and used.

## The Current Enterprise Software Model

Traditional enterprise software is usually packaged as a complete application.

It includes:

- a data model;
    
- transaction processing;
    
- business rules;
    
- permissions;
    
- configuration screens;
    
- dashboards;
    
- forms;
    
- reports;
    
- workflow designers;
    
- user interfaces for many roles and scenarios.
    

The product must support many organizations through one shared model.

As a result, it often becomes:

- very broad;
    
- highly configurable;
    
- difficult to learn;
    
- expensive to implement;
    
- dependent on specialists;
    
- full of functionality that an individual customer does not use.
    

A company buys not only the capabilities it needs, but also a large interface and configuration framework designed to cover thousands of possible cases.

AI may weaken the economic value of that packaging.

## The Emerging Architecture

A possible future architecture is:

```text
systems of record
    ERP, CRM, finance, HR, warehouse, ticketing

semantic and policy layer
    domain definitions, metrics, permissions, business rules

capability layer
    APIs, commands, queries, transactional operations

AI orchestration layer
    intent interpretation, planning, workflow composition

generated interface
    temporary forms, dashboards, reports, explanations
```

The stable lower layers remain important.

The upper layers become dynamic.

Instead of forcing the user to navigate a permanent application, the system can assemble the process and interface required for the current task.

## Three Main Transformation Paths

Different software categories may follow different paths.

## 1. Replacement by Small Specialized Software

A large platform may be replaced for a narrow process by a smaller application generated or maintained with AI.

This is most plausible when:

- the process is limited in scope;
    
- regulation is weak;
    
- integration requirements are manageable;
    
- the existing platform is unnecessarily broad;
    
- the organization has unusual workflows;
    
- the cost of customization exceeds the value of the product.
    

Examples include:

- small internal tools;
    
- local workflow systems;
    
- narrow operational applications;
    
- custom reporting;
    
- lightweight inventory tools;
    
- specialized customer processes.
    

The replacement does not need to reproduce the entire enterprise suite.

It only needs to solve the part that the organization actually uses.

This shift accelerates the viability of [[A New Market for Small, Custom Business Software|small, custom business software]]. When an internal engineering team can build and maintain a dedicated micro-app in days, the economic justification for buying a massive, generic SaaS module evaporates. The software itself stops acting as a defensive moat when a tailored alternative can be assembled quickly around concrete operational needs.

## 2. AI Configures the Existing Platform

The system remains, but people stop configuring it manually.

Today, an ERP or workflow specialist may need to:

- navigate configuration screens;
    
- create rules;
    
- map fields;
    
- define approval paths;
    
- modify forms;
    
- write formulas;
    
- test multiple variants.
    

In an AI-assisted model, a domain expert may describe the intended process:

> Add a second approval for purchases above this threshold, except for strategic suppliers. Simulate the effect on last quarter's transactions before enabling it.

The agent can:

- translate the request into platform configuration;
    
- identify affected rules;
    
- generate tests;
    
- simulate the result;
    
- explain conflicts;
    
- prepare a controlled deployment.
    

The platform keeps its value as a secure and auditable runtime.

Its manual configuration layer becomes less important.

## 3. The Platform Becomes Invisible Infrastructure

The system continues to store data and execute operations, but users no longer interact with its primary interface.

Instead of opening separate applications for CRM, ERP, reporting, and support, the user communicates with an agent.

```text
human
→ agent
→ several enterprise systems
→ completed business operation
```

The agent becomes the visible workspace.

The underlying platforms become systems of record and execution.

This may be the strongest long-term path for large enterprise systems.

This architecture turns legacy vendors into headless backends. For established platforms with complex regulatory compliance and deep transactional state, this shift protects their core database and business logic while stripping away the defensibility of their web portals. Interaction migrates to [[Designing APIs for LLM-Generated Integration Code|well-structured tool interfaces]], where agents query schemas and execute state changes programmatically.

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

## Business Intelligence: From Permanent Dashboards to On-Demand Analysis

Traditional BI is centered on reports and dashboards.

An analyst:

- prepares a semantic model;
    
- writes formulas;
    
- selects visualizations;
    
- creates report pages;
    
- defines drill-down paths;
    
- publishes and maintains the result.
    

But the user usually does not want a dashboard for its own sake.

The user wants an answer:

- Why did margin fall?
    
- Which customers caused the change?
    
- Is the problem caused by volume, price, or product mix?
    
- Which production line behaves differently?
    
- What changed after the last release?
    

AI can generate a temporary analytical view for the question being asked.

```text
business question
→ metric selection
→ data query
→ appropriate visualization
→ explanation
→ follow-up analysis
```

A large library of permanent dashboards may be replaced partly by dynamic analysis.

The analyst's role moves toward:

- metric definitions;
    
- semantic modeling;
    
- data quality;
    
- validation;
    
- causal reasoning;
    
- identifying misleading questions;
    
- explaining business consequences.
    

The chart becomes cheap.

Reliable meaning remains difficult.

Dynamic analytical pipelines rely on automated schema discovery and prompt-to-SQL synthesis. However, without clean metric layers and strict data contracts, generated queries fail on subtle join errors, fan-out bugs, or incorrect aggregation granularities. The analyst guarantees that the underlying relational logic reflects operational reality.

## CRM: From Manual Data Entry to Process Observation

CRM systems often require users to maintain a parallel representation of reality.

Salespeople must manually:

- update opportunity stages;
    
- enter notes;
    
- schedule follow-ups;
    
- classify contacts;
    
- record activity;
    
- maintain forecasts.
    

An agent can infer much of this from:

- email;
    
- meetings;
    
- documents;
    
- call transcripts;
    
- calendar events;
    
- commercial systems.
    

The CRM may change from a system that users continuously update into a system that observes the sales process and asks for confirmation only when necessary.

```text
today:
salesperson performs work
+ manually updates CRM

future:
agent observes work
+ updates CRM
+ asks for decisions or corrections
```

The CRM remains a system of record, but its forms and dashboards become less central.

## Customer Support: From Ticket Handling to Problem Resolution

Traditional support software organizes work around tickets.

```text
request
→ category
→ queue
→ support agent
→ response
→ escalation
```

AI can organize the process around the actual customer outcome.

An agent may:

- identify the customer;
    
- collect history from several systems;
    
- diagnose a known issue;
    
- check an order;
    
- initiate a refund;
    
- update account data;
    
- send an explanation;
    
- escalate only unusual cases.
    

The ticketing platform may remain necessary for:

- audit;
    
- SLA tracking;
    
- ownership;
    
- reporting;
    
- legal evidence.
    

But the human may no longer work through every ticket manually.

The operational boundary here is policy enforcement and blast radius control. Autonomous resolution only works when the agent operates against strict idempotency keys and clear programmatic guardrails—such as refund caps, rate limits, and step-up authentication before mutating financial or account state.

## ITSM and Incident Management

IT service systems contain valuable operational structures:

- incident ownership;
    
- change history;
    
- CMDB;
    
- service catalogs;
    
- approvals;
    
- runbooks;
    
- escalation paths.
    

AI can interpret an operational problem and coordinate several tools:

> Login failures increased after the latest deployment. Identify the affected services, correlate the change, prepare a rollback, open an incident, and notify the owners.

The agent can:

- inspect logs and metrics;
    
- compare deployments;
    
- find similar incidents;
    
- update the ticket;
    
- execute an approved runbook;
    
- prepare a timeline.
    

The ITSM platform remains the control and audit layer.

The agent becomes the operational interface.

In practice, the agent correlates telemetry across observability pipelines (Prometheus, Datadog) with git deployment metadata and change requests. By assembling the blast-radius estimate and linking past post-mortems directly inside the incident ticket, it compresses Mean Time to Resolution (MTTR) while leaving the formal ITSM platform intact as the compliance audit log.

## Workflow, BPM, and RPA

Classical workflow and RPA systems depend heavily on:

- visual diagrams;
    
- rules;
    
- selectors;
    
- field mappings;
    
- manually defined branches;
    
- deterministic input formats.
    

LLMs are better at interpreting:

- documents;
    
- messages;
    
- ambiguous requests;
    
- semi-structured data;
    
- unusual cases.
    

However, deterministic execution still matters for:

- transactions;
    
- payments;
    
- retries;
    
- idempotency;
    
- compliance;
    
- irreversible operations.
    

The most likely architecture is hybrid:

```text
LLM:
understand intent
classify input
select a path
handle ambiguity

workflow or code:
execute deterministically
validate
retry
record
audit
```

AI may generate or choose the workflow rather than directly improvising every action.

## Low-Code and No-Code

Low-code platforms attempted to let business users build applications without traditional programming.

In practice, users still had to understand:

- the platform's component model;
    
- formulas;
    
- data structures;
    
- deployment;
    
- permissions;
    
- platform-specific limitations.
    

AI may finally make the interface more natural:

> Describe the process, show sample data, and explain the rules.

Two outcomes are possible.

### AI strengthens low-code

The platform provides:

- governance;
    
- identity;
    
- deployment;
    
- connectors;
    
- monitoring;
    
- safe execution.
    

AI generates the application inside this controlled environment.

### AI weakens low-code

Agents generate ordinary maintainable code directly.

The visual platform becomes an unnecessary intermediate abstraction.

The long-term value of low-code may therefore lie less in its visual editor and more in its governed runtime.

When an agent can output idiomatic TypeScript or Python targeting standard cloud primitives, proprietary drag-and-drop canvases become maintenance liabilities. A visual flowchart engine simply adds an opaque layer between the developer and the runtime, without providing better debugging, version control, or execution speed than standard code.

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

## Engineering, CAD, and Technical Design

Engineering software may evolve differently from transaction systems.

The core products remain valuable because they provide:

- geometric models;
    
- simulations;
    
- material databases;
    
- manufacturing constraints;
    
- verified solvers.
    

AI can transform them into environments for guided experimentation.

An engineer may specify:

> Reduce the weight while preserving strength, current dimensions, and compatibility with the existing manufacturing process.

The agent can:

- generate variants;
    
- modify parameters;
    
- run simulations;
    
- compare tradeoffs;
    
- prepare documentation.
    

The software becomes less a manual drawing tool and more an executable design laboratory.

## Developer Tools and Operations

The same transformation applies to:

- CI/CD;
    
- observability;
    
- cloud consoles;
    
- security scanners;
    
- container platforms;
    
- infrastructure management.
    

Operators currently need to understand many query languages, dashboards, and configuration formats.

A future interaction may be:

> Errors increased after the 14:20 deployment. Identify the shared cause, estimate the impact, and prepare the safest rollback.

The agent queries logs, traces, metrics, deployment history, and source code.

The underlying tools remain.

Their interfaces become callable capabilities.

Platform engineers spend significant time translating operational intent into domain-specific query languages like PromQL, LogQL, or vendor-specific trace filters. Wrapping these observability systems in agent-callable primitives allows an operator to diagnose connection pool exhaustion, p99 latency spikes, or cross-service cascading failures without context-switching between half a dozen browser dashboards.

## Project and Work Management

Project management systems often contain a manually maintained model of work.

People update:

- tickets;
    
- statuses;
    
- blockers;
    
- dependencies;
    
- estimates;
    
- reports.
    

AI can infer much of this from:

- conversations;
    
- pull requests;
    
- documents;
    
- deployments;
    
- calendars;
    
- decisions.
    

The system may remain useful as a durable representation of plans and commitments, but manual synchronization may decline.

Some project management software exists partly because machines could not previously understand unstructured work.

AI weakens that assumption.

## The Common Transformation Patterns

Across these categories, several paths repeat.

### Full replacement

A small generated system replaces an unnecessarily broad application.

### AI-generated configuration

The existing platform remains, but AI creates its rules, forms, and workflows.

### Agent orchestration

The agent uses several platforms in the background to complete one business outcome.

### Generated interface

A form, report, dashboard, or control panel is created for one task and may disappear afterward.

### Exception-based work

The system handles normal cases and sends only ambiguous or high-risk cases to humans.

### Stable core with dynamic edges

The transactional core remains durable, while workflows and interfaces become flexible and generated.

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

## A Market of Systems and Capabilities

The software market may gradually shift from complete applications toward composable layers.

Companies may buy:

- accounting from one provider;
    
- warehouse management from another;
    
- identity from a third;
    
- communication from another;
    
- models from several vendors.
    

AI then connects these systems into a company-specific process.

The organization is no longer forced to buy one enormous suite merely to obtain a coherent workflow.

The workflow becomes an owned layer above several systems of record.

This could weaken suite vendors while strengthening vendors that provide:

- reliable core systems;
    
- strong APIs;
    
- clear semantics;
    
- safe agent interfaces;
    
- excellent interoperability.

This architectural shift directly favors [[Shifting from Fixed Features to Agent-Extensible Primitives|agent-extensible primitives]] over monolithic suites. When integration glue is written and maintained dynamically by agents, the historical lock-in created by suite vendors—who relied on mediocre sub-products bundled together with single sign-on—evaporates. Organizations can reassert ownership over their operational workflows while buying best-of-breed transactional backends.

## Risks

This model introduces new problems.

### Semantic inconsistency

Different systems may use the same term differently.

The agent needs a trusted semantic layer.

For example, an "active customer" means an account with an open contract in Salesforce, a tenant with an active card on file in Stripe, and a user with an open ticket in Zendesk. Without a verified semantic reconciliation layer, an agent orchestrating cross-system updates will silently corrupt downstream state.

### Security

Broad agent access can connect previously isolated systems.

Permission design becomes critical.

Granting an agent wide operational privileges tears down departmental network and system boundaries. An unhandled exception, model hallucination, or prompt injection in one low-priority tool can rapidly propagate destructive mutations across financial ledgers, customer records, and identity providers.

### Hidden coupling

A generated workflow may depend on many APIs and undocumented assumptions.

Generated workflows and dynamic scripts often anchor against undocumented edge cases, implicit response formats, or ephemeral API behaviors. If an upstream team changes a payload schema or rate-limit policy without strict contract testing, brittle agentic integrations fail silently in production.

### Auditability

Organizations must know why an action occurred and which data informed it.

When an autonomous agent mutates state across four separate databases, standard application logs are insufficient. Debugging and compliance require immutable execution traces recording the exact system prompts, retrieved context, tool invocations, parameters, and authorization grants that produced each transaction.

### Vendor dependence

Agent workflows may become tied to one model or orchestration platform.

### Excessive complexity

AI may make it easy to connect many systems without simplifying the underlying organization.

### Uncontrolled end-user development

Domain users may create business-critical processes without adequate tests, ownership, or governance.

The ability to generate a process does not automatically make the process safe.

When domain experts can generate business logic on demand, organizations face a resurgence of unmonitored shadow IT. Workflows running critical operational paths without automated test suites, CI/CD promotion pipelines, SLA monitoring, or clear team ownership create catastrophic operational blind spots.

## Working Hypothesis

> Enterprise software will increasingly separate stable systems of record from dynamic workflows, analysis, and user interfaces generated by AI.

A stronger version is:

> Large platforms may survive, but their value will move away from permanent screens and manual configuration toward data, rules, permissions, transactions, and callable capabilities.

The likely future is not simply:

```text
AI replaces ERP, CRM, BI, and workflow software
```

It is more likely:

```text
stable enterprise systems
+ shared semantics and policies
+ AI orchestration
+ generated workflows or deterministic code
+ temporary task-specific interfaces
```

## Mental Model

Enterprise applications were designed for a world in which humans had to learn how to operate each system directly.

AI introduces another possibility:

> Humans express intent, while agents learn how to operate the systems.

The application may therefore stop being the primary unit of enterprise software.

The new unit may be the capability:

- query this data;
    
- create this transaction;
    
- validate this rule;
    
- approve this request;
    
- generate this analysis;
    
- execute this operation.
    

Agents compose those capabilities into the process required at a particular moment.

The system remains.

The fixed application around it becomes optional.

## Related notes

- **[[A New Market for Small, Custom Business Software]]** — How lower implementation costs enable bespoke, single-tenant enterprise tools.
- **[[Designing APIs for LLM-Generated Integration Code]]** — Structuring API contracts and capability interfaces so LLMs can generate reliable integration workflows.
- **[[Shifting from Fixed Features to Agent-Extensible Primitives]]** — Moving from monolithic UI features to flexible, agent-composable platform primitives.
- **[[Software Implementation Is Becoming a Weaker Moat]]** — Why data gravity, business relationships, and core transactional engines matter more than application wrappers.
- **[[Workflow Orchestration in Agentic Systems]]** — Composing underlying enterprise capabilities into multi-step agent execution workflows.
