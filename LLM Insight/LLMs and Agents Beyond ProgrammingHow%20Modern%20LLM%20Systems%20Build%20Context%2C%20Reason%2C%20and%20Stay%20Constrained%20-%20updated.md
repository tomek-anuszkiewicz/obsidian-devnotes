LLMs and agents can be useful far beyond code generation. Their strongest role is often in tasks that require **interpretation, semantic consistency, contextual reasoning, hypothesis generation, and working across multiple information sources**.

## Potential use cases

- **UI analysis and testing**
    
    - Analyze screenshots and detect visual inconsistencies.
        
    - Compare multiple screens and identify elements that do not match the rest of the application.
        
    - Evaluate wording, layout, navigation, error states, accessibility, and overall UX consistency.
        
    - Perform semantic UI testing where exact pixel matching is not sufficient.
        
- **User behavior analysis**
    
    - Analyze how users navigate through an application.
        
    - Detect confusing flows, repeated actions, abandoned forms, unnecessary backtracking, or unclear interactions.
        
    - Reconstruct user journeys from events, logs, session recordings, and telemetry.
        
    - Simulate different user personas and attempt to complete tasks through the UI.
        
- **Browser-based agents**
    
    - Give an agent access to a browser and let it explore the application directly.
        
    - Ask it to follow specific workflows, inspect available functionality, and capture screenshots.
        
    - Use the running application as an empirical source of truth rather than relying only on code or specifications.
        

## Documentation generation and maintenance

A browser-capable agent could:

1. Open the application.
    
2. Navigate through important workflows.
    
3. Observe current UI and behavior.
    
4. Compare the result with existing documentation.
    
5. Identify outdated sections.
    
6. Generate or update documentation.
    
7. Verify that the updated documentation matches the current application.
    

This creates a useful feedback loop between:

- what the documentation says,
    
- what the configuration says,
    
- what the code suggests,
    
- and what the system actually does.
    

The agent can therefore be used not only to **create documentation**, but also to continuously check whether it is still accurate.

## Incident and failure analysis

An agent can correlate information from multiple systems:

- logs,
    
- traces,
    
- metrics,
    
- deployments,
    
- commits,
    
- feature flags,
    
- configuration,
    
- tickets,
    
- previous incidents.
    

Instead of simply searching logs, it can iteratively generate and test hypotheses:

```text
Metrics
  ↓
Suspicious service
  ↓
Trace
  ↓
Logs
  ↓
Recent deployment
  ↓
Commit diff
  ↓
Feature flag
  ↓
Hypothesis
  ↓
Verification
```

The goal is not just to find matching text, but to answer questions such as:

- What most likely caused the incident?
    
- What changed just before the failure?
    
- Which users are affected?
    
- What should be checked next?
    
- What is the safest mitigation?
    

## Semantic testing

Many useful tests cannot be expressed as strict deterministic rules.

Traditional test:

```text
expected == actual
```

LLM-based test:

```text
Does this result satisfy the user's intent?
```

Examples:

- Is the error message understandable?
    
- Does this screen look consistent with the rest of the application?
    
- Does the generated document look professional?
    
- Are two UI versions functionally equivalent?
    
- Does this workflow make sense to a first-time user?
    
- Is the response complete and useful?
    

In such cases, the model acts as a **semantic judge** rather than a deterministic assertion engine.

## UI consistency as an inferred property

LLMs appear to have a useful sense of visual and semantic consistency.

Given multiple screenshots from the same application, a model can often infer patterns such as:

- button placement,
    
- heading hierarchy,
    
- spacing,
    
- terminology,
    
- icon usage,
    
- navigation patterns,
    
- error presentation,
    
- form behavior,
    
- visual emphasis.
    

It can then identify screens or components that do not fit the established pattern.

The important point is that the pattern does not always need to be explicitly defined beforehand.

The model can infer:

> "Most of the application follows pattern X, while this screen behaves or looks differently."

This complements strict design-system validation.

## Connection with Infrastructure as Code

Agent-based analysis fits particularly well with the broader **Everything as Code** trend.

More and more parts of a system are represented as structured, version-controlled artifacts:

- Infrastructure as Code
    
- Configuration as Code
    
- Policy as Code
    
- Observability as Code
    
- CI/CD as Code
    
- OpenAPI specifications
    
- database migrations
    
- feature flag configuration
    
- dashboards
    
- alerts
    
- documentation
    

This makes a much larger part of the system machine-readable.

An agent can therefore reason across these layers instead of analyzing each one independently.

For example:

```text
Terraform:
Load balancer timeout = 30 s

Kubernetes:
Application timeout = 45 s

Grafana:
Alert threshold = 40 s

Runbook:
"Requests may take up to 60 seconds"

Client documentation:
"Maximum operation time: 45 seconds"
```

Every individual artifact may be syntactically valid.

However, the system as a whole is inconsistent.

An agent can detect that:

> The load balancer may terminate a request before the application reaches its own timeout, while the runbook is also outdated.

This is a **semantic system-level error**, not a syntax error.

## A broader idea: System as Code

Infrastructure as Code and related approaches make increasingly large parts of an organization explicitly describable.

This suggests a broader concept:

**System as Code** or even **Organization as Code**.

An agent could have access to:

```text
Repositories
+ Infrastructure
+ Configuration
+ CI/CD
+ Monitoring
+ Logs
+ Documentation
+ Tickets
+ Running UI
+ Historical incidents
```

It could continuously compare three different views of reality:

### What we say the system does

Documentation, requirements, runbooks, architecture descriptions.

### What the system is configured to do

Code, infrastructure, policies, configuration, feature flags.

### What the system actually does

Runtime behavior, telemetry, browser interaction, logs, user behavior.

A powerful role for agents is therefore to continuously detect inconsistencies between:

```text
Intent
↕
Implementation
↕
Configuration
↕
Observed behavior
↕
Documentation
```

## What an LLM contributes

A useful way to think about the capabilities is:

1. **Perception** — understand screenshots, logs, diagrams, documents.
    
2. **Interpretation** — determine what the information means.
    
3. **Correlation** — connect information from multiple sources.
    
4. **Evaluation** — judge whether something is correct, useful, or consistent.
    
5. **Hypothesis generation** — propose explanations.
    
6. **Planning** — decide what to inspect next.
    
7. **Action** — use tools to perform the next step.
    
8. **Verification** — check whether the action solved the problem.
    

Steps 6–8 are especially important because they distinguish an **agent** from a simple one-shot LLM query.

## Key idea

The most interesting application of agents may not be:

> "AI performs a human task faster."

It may instead be:

> **AI combines many previously disconnected sources of information into one continuous reasoning process.**

As more of the system becomes declarative, version-controlled, observable, and machine-readable, this becomes increasingly practical.