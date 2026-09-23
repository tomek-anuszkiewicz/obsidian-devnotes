---
title: The Most Valuable Software Training Data May Be Private
tags:
  - training-data
  - proprietary-data
  - software-engineering
  - codebases
  - git-history
  - ai-moats
aliases:
  - Private Code as Premium Training Data
  - Git History Value for LLM Training
---

Large language models learn from available data, but in software engineering there is an important limitation: much of the most valuable knowledge is not public.

Public repositories contain enormous amounts of code, but code is mostly the **final artifact**.

In public git trees, squashed commits and scrubbed pull requests systematically strip away the exact signal an agent needs to learn causal reasoning: dead-end approaches, design debates, test failures, and emergency rollbacks. The public artifact reflects survivorship bias, while the actual debugging journey stays private.

Inside companies, there is a much richer record of how software was actually created.

A typical development history may contain:

```text
business requirement
→ meeting discussion
→ ticket or specification
→ initial implementation
→ code review
→ failed tests
→ corrections
→ production incident
→ root-cause analysis
→ refactoring
→ final implementation
```

This is not merely code.

It is a record of **how an organization reasoned its way toward a working solution**.

## The History of Code May Be More Valuable Than the Code

Consider two possible training datasets.

The first contains millions of correct C# methods.

The second contains examples such as:

```text
Problem:
A new payment workflow must support retries.

Attempt 1:
The developer implements the operation directly.

Review:
A reviewer notices that retries could execute the payment twice.

Attempt 2:
An idempotency mechanism is introduced.

Production:
A concurrency edge case still causes duplicate processing.

Final solution:
The transaction boundary and idempotency model are redesigned.
```

The second dataset teaches much more than syntax.

It teaches:

- which approaches looked reasonable but failed;
    
- which edge cases were initially missed;
    
- why reviewers rejected a design;
    
- which assumptions proved wrong in production;
    
- how the solution evolved;
    
- what trade-offs mattered.
    

This type of information is often absent from public code.

When models only train on final, clean commits, they learn what valid syntax looks like, but remain blind to how systems break under production load and how engineers isolate faults.

## Software Companies Possess Large Amounts of "Dark Knowledge"

A typical company may have years of information distributed across:

- source repositories;
    
- Git history;
    
- pull requests;
    
- code-review comments;
    
- Jira or other issue trackers;
    
- architectural decision records;
    
- documentation;
    
- Slack or Teams discussions;
    
- meeting recordings and transcripts;
    
- support tickets;
    
- production logs;
    
- incident reports;
    
- post-mortems;
    
- monitoring data.
    

Individually, these artifacts may appear mundane.

Together, they form a detailed history of:

> how real software engineering problems were discovered, misunderstood, discussed, solved, broken, and eventually improved.

Most of this information is private.

Foundation-model providers therefore cannot simply crawl it in the way they can crawl public repositories.

There may consequently be an enormous **dark dataset of software engineering experience** that general-purpose models do not have access to.

## Enterprise Agents May Know More Than Foundation Models

This creates an interesting separation.

A company may connect an AI agent to:

```text
foundation model
+
source code
+
documentation
+
tickets
+
meeting transcripts
+
production history
+
internal tools
```

The resulting agent may understand the company extremely well.

But that knowledge does not automatically become knowledge of the underlying foundation model.

We may therefore reach a situation where:

```text
general model
    <
company-specific agent
```

for many practical engineering problems inside that organization.

The general model understands software engineering broadly.

The company agent additionally understands:

- historical decisions;
    
- business rules;
    
- previous failures;
    
- organizational constraints;
    
- customer-specific requirements;
    
- unusual production edge cases.
    

This private context can become a major source of capability.

## Raw Corporate Data Does Not Necessarily Need to Be Shared

A company may never agree to provide an AI vendor with:

```text
its repositories
+ customer data
+ internal tickets
+ meetings
+ incident history
```

But useful training information might still be extracted without exposing the original material.

For example:

```text
private production incident
↓
extract the engineering lesson
↓
remove proprietary identifiers
↓
construct a synthetic equivalent
↓
use the generalized example for training
```

Instead of exposing:

> `CustomerSettlementService` caused duplicate payments for Client X because of retry behavior.

the resulting training example could become:

> A financial workflow uses at-least-once message delivery. The operation is not idempotent. Identify the failure mode and design a safer architecture.

The private implementation is gone.

The **lesson learned from it remains**.

This may become an important mechanism for extracting training value from private enterprise experience.

## Agent Trajectories May Become Especially Valuable

AI coding agents create another type of dataset that could be even more useful than traditional repositories.

A typical agent interaction may produce:

```text
task
→ agent attempt 1
→ test failure
→ agent correction
→ attempt 2
→ human review rejection
→ explanation
→ attempt 3
→ tests pass
→ human approval
```

This is an unusually rich training signal.

It contains:

- the original task;
    
- unsuccessful reasoning paths;
    
- objective test results;
    
- human feedback;
    
- corrections;
    
- final success.
    

Traditional repositories mostly preserve the final solution.

Agent systems can preserve the **entire path toward the solution**.

Unlike static code, an agent trajectory captures concrete runtime feedback—compiler errors, failing test assertions, and stack traces—alongside the corrective diffs applied to recover from intermediate failures. This provides dense, step-by-step supervision on fault isolation that static repositories cannot offer.

At sufficient scale, normal software development with agents could automatically generate enormous datasets describing how models fail and how those failures should be corrected.

## AI Usage Could Create a New Data Flywheel

This produces a possible feedback loop:

```text
better model
↓
companies give agents harder tasks
↓
agents encounter new failures
↓
tests and humans identify mistakes
↓
agents are corrected
↓
valuable trajectories are produced
↓
next models learn from those trajectories
↓
better model
```

This may eventually become more valuable than simply collecting more public code.

The important training material is no longer just:

> Here is good code.

It becomes:

> Here was the task.  
> Here is what the model tried.  
> Here is why it failed.  
> Here is the correction.  
> Here is what finally worked.

## But There Is a Fundamental Ownership Problem

The organizations generating these trajectories may not want to give them away.

They may consider them:

- intellectual property;
    
- security-sensitive information;
    
- competitive knowledge;
    
- customer-confidential information;
    
- proprietary business-process knowledge.
    

This creates a tension.

AI vendors want high-quality experience data.

Enterprises want increasingly capable models.

But the data that could improve those models may itself be strategically valuable.

The question becomes not merely:

> Who owns the source code?

but increasingly:

> Who owns the learning trajectory generated while an AI agent worked on the company's problems?

## New Data-Sharing Models May Appear

Today, enterprise AI products often emphasize that company data is not used for general model training by default.

That is attractive because companies want strong isolation.

In the future, however, additional arrangements could emerge.

For example:

```text
standard enterprise contract
→ no training

optional data partnership
→ selected trajectories
→ anonymization
→ abstraction
→ controlled contribution
→ financial or product benefit
```

Companies might receive:

- lower inference costs;
    
- access to better models;
    
- custom fine-tuning;
    
- priority capabilities;
    
- credits;
    
- research partnerships.
    

In exchange, they might contribute carefully sanitized training examples rather than raw corporate data.

## Organizational Knowledge May Become a Strategic Dataset

This changes the value of documentation.

Historically, documentation was created mainly so that another employee could understand a system later.

In an AI-heavy organization, documentation may also become:

> training and context data for future agents.

The same applies to:

- meeting transcripts;
    
- decision logs;
    
- incident reports;
    
- PR discussions;
    
- rejected approaches;
    
- business explanations;
    
- architectural rationale.
    

Organizations that systematically preserve this history may accumulate something similar to **AI knowledge capital**.

A company that has ten years of:

```text
requirements
+ decisions
+ implementations
+ incidents
+ corrections
+ agent interactions
+ human evaluations
```

may possess an extraordinarily valuable dataset for future internal AI systems.

The companies that recorded their reasoning may therefore have an advantage over companies that preserved only final artifacts.

## The Scarcity May Shift From Data to Experience Data

The early model-training paradigm was largely:

```text
crawl the internet
→ obtain more text and code
→ train a larger model
```

But the internet contains disproportionately large amounts of final output.

The next major bottleneck may be access to something different:

> high-quality records of how difficult real-world tasks were solved.

This includes mistakes, feedback, hidden constraints, failed attempts, and long-term consequences.

In software engineering, corporations generate this type of information continuously.

Most of it remains private.

## Mental Model

The evolution may look roughly like this:

```text
Public Internet
    ↓
models learn what software looks like

Public repositories
    ↓
models learn how software is implemented

Enterprise context
    ↓
agents learn how a particular organization works

Agent trajectories
    ↓
models could learn how difficult engineering problems are actually solved
```

The final step may be the most valuable one.

And it is also the step where access to data becomes the hardest.

The future limitation of LLM development may therefore not be a simple lack of data.

It may be:

> **a lack of access to the private experience data that records how organizations actually solve complex problems.**

---

## Related Notes

- [[What Should Organizations Preserve from AI-Assisted Development|What Should Organizations Preserve from AI-Assisted Development]] — Preserving the institutional intent, failed branches, review transcripts, and verification records behind generated code.
- [[Fresh Contact With Reality May Become the Training Bottleneck|Fresh Contact With Reality May Become the Training Bottleneck]] — Why grounded interactions with compilers, networks, production telemetry, and human judgment are essential to escape synthetic collapse.
- [[Improving AI Models - From Scaling to Agent-Generated Training Data|Improving AI Models - From Scaling to Agent-Generated Training Data]] — Generating verifiable post-training datasets through execution, search, and self-correction loops.
- [[LLM Agents and Institutional Memory|LLM Agents and Institutional Memory]] — Architecture for embedding past decisions, incident postmortems, and codebase idioms into durable agent memory.
- [[The 5-Layer System Stack for Agentic Software Engineering|The 5-Layer System Stack for Agentic Software Engineering]] — System-level governance connecting organizational telemetry, private data stores, and verified agent actions.
