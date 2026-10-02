---
title: AI Changes the Economics of Technical Debt
tags:
  - technical-debt
  - economics
  - ai-agents
  - software-engineering
  - refactoring
  - maintenance
aliases:
  - Technical Debt in the AI Era
  - Economics of Automated Refactoring
---

## Agents Can Reduce or Accelerate Technical Debt

Agents can continuously:

- update dependencies,
    
- migrate deprecated APIs,
    
- remove warnings,
    
- improve tests,
    
- identify dead code,
    
- update documentation,
    
- prepare framework upgrades,
    
- perform mechanical refactors.
    

But they can also generate debt much faster:

- duplicated mechanisms,
    
- unnecessary abstractions,
    
- excessive classes,
    
- inconsistent local patterns,
    
- tests validating incorrect assumptions,
    
- large amounts of code nobody has deeply reviewed.
    

Cheaper code production lowers the effort required to introduce both useful changes and unnecessary structure. An agent can duplicate a validation routine or add speculative adapter layers faster than a team can review their long-term consequences. Compilation and passing local tests do not establish that these additions are needed.

Additional productivity should be divided between:

```text
new features
technical maintenance
quality and risk reduction
experimentation
```

Using all additional capacity only for feature production can make the system deteriorate faster than before.

If feature production grows faster than review and maintenance capacity, coupling and duplicated mechanisms can make subsequent tasks harder. This is a failure scenario to monitor, not a prediction that every agent-assisted project will deteriorate within a fixed number of months.

---

## Technical Maintenance Gains a Direct Business Justification

A framework upgrade or refactoring may not directly generate revenue.

However, poor architecture reduces agent effectiveness through:

- larger context requirements,
    
- more failed attempts,
    
- larger diffs,
    
- longer review,
    
- weaker test isolation,
    
- more regressions,
    
- lower agent autonomy.
    

Technical debt can therefore be expressed operationally. An illustrative diagnosis might be:

```text
The Pricing module:
- requires three times more review,
- has a high agent failure rate,
- produces large cross-module diffs,
- prevents independent testing,
- slows every new pricing feature.
```

Modernization is no longer only about code aesthetics. It becomes an investment in development throughput, safety, and the effective use of agents.

Architecture influences how much context an agent needs and how much verification a change requires. A calculation mixed with database access and global state can require broader inspection than the same calculation behind an explicit boundary. Measure whether a refactoring reduces repair attempts, review effort, or integration failures; shorter files or fewer tokens alone do not establish a business benefit.

## Small Readability Changes Are a Useful Maintenance Category

A repository-wide maintenance process does not have to mean a repository-wide rewrite. It can find candidates across the repository, then produce small changes with one purpose: name a repeated domain constant, give a condition a meaningful name, flatten nesting with guard clauses, or separate a calculation into stages that a reader can follow.

The distinction between discovery scope and edit scope matters. An agent can inspect many modules while each proposed patch remains local and independently reviewable. Prefer a concrete instruction such as “make the eligibility rule easier to read while preserving evaluation order and outcomes” over “apply clean code everywhere.”

More functions are not automatically clearer. A helper that hides one obvious comparison may make the reader jump around; a helper that names a domain rule can remove the need to reconstruct that rule from several conditions. Similarly, replace a magic number with a name that explains its meaning, rather than a generic `VALUE_30`. [[Refactoring Legacy Systems with AI Agents]] gives a behavior-preserving example.

There is published evidence for this kind of work. A study of agent-generated Java changes found common local refactorings such as variable and parameter renaming. That establishes existing practice, not an unattended cleanup method for every repository. [Agentic Refactoring: An Empirical Study of AI Coding Agents](https://arxiv.org/abs/2511.04824)

CodeScene describes a larger experiment using small refactoring recipes, including function extraction and guard clauses, with replay comparisons against a game implementation. Its reported code-health improvement is a tool metric; replay coverage bounds the behavioral evidence. It does not prove that every change improved human comprehension or that all possible behavior was preserved. [CodeScene's refactoring case study](https://codescene.com/blog/case-study-refactoring-at-scale-with-agents)

Another study of readability-related agent commits found that maintainability and complexity metrics often moved in an unfavorable direction. These metrics are not direct measurements of reader comprehension either, but they challenge the assumption that a readability prompt reliably improves the code. Review the resulting explanation and diff, not merely the agent's description of its intent. [Do AI Agents Really Improve Code Readability?](https://arxiv.org/abs/2603.13723)

## Dead Code and Unnecessary Live Code Need Different Evidence

An unreachable method and a redundant step on an active path are different cleanup tasks. For dead-code candidates, examine callers, registration, configuration, reflection, external consumers, and observed execution. For redundant live code, establish why removing or replacing the step preserves the required behavior.

Tests do not require the smallest possible implementation. An unnecessary branch can survive because it does not affect asserted outputs; a needed rare branch can disappear because no test exercises it. Passing tests therefore neither proves that all debt was removed nor proves that a deletion was safe.

A published account of agent-assisted deletion used references and Git history to propose candidates, human selection to approve them, and builds to catch mistakes. Its stated exclusions for reflective and annotation-driven behavior are part of the method. Successful compilation is useful evidence, but it does not establish runtime equivalence. [I Used an AI Agent to Delete 5,000 Lines of Dead Code](https://yunjeongiya.github.io/posts/035-en/)

Record the reason for a deletion: unreachable under the supported configuration, behavior explicitly retired, or equivalent behavior retained elsewhere. Runtime silence during an observation window is a candidate signal; seasonal jobs and recovery paths may simply not have run. Removing a failing test requires a reviewed decision that its behavior is obsolete, rather than treating the failure as cleanup noise.

---

## Operational Guardrails for Agent Workflows

To use automated cleanup productively, connect candidate discovery to bounded edits and explicit acceptance checks:

### Use Size and Coupling as Review Signals
File-size checks can flag modules that deserve inspection, but no universal line ceiling guarantees sufficient context or good model behavior. Split around responsibilities and dependency boundaries when that improves local reasoning. Do not replace one coherent file with many tightly coupled fragments merely to satisfy a number.

### Bound Task Blast Radius
Declare the allowed scope of each task and inspect unexpected expansion before continuing. A rename may legitimately touch many callers; a local calculation change that unexpectedly modifies persistence needs an explanation. File count is a signal, not a diagnosis of architectural failure.

### Run Automated Background Maintenance Loops
A recurring job can identify candidates, select one accepted recipe, apply it in an isolated workspace, run the relevant checks, and prepare a self-contained PR. Keep dependency upgrades, readability changes, and deletions separate because their verification needs differ. Limit the queue to the team's review capacity; hundreds of unreviewed cleanup patches are another maintenance burden.

Use deterministic refactoring tools when they can perform the operation. The agent can choose a meaningful name or extraction boundary while an IDE engine resolves symbol references and applies the edit. JetBrains describes this division in its agent-facing refactoring skill. The tool reduces mechanical mistakes; integration and behavioral checks are still needed. [Rider's refactoring-code skill](https://blog.jetbrains.com/dotnet/2026/08/19/rider-refactoring-code-skill/)

### Track Agent Friction as an Architectural Metric
Monitor repeated repair loops, review rejection, context requirements, and regressions (see [[Token Optimization and Context Economics in Agentic Workflows]]). Investigate the cause before prescribing a refactoring: unclear requirements or inadequate tools can create the same symptoms as poor structure. Evaluate cost per accepted change, including review and verification, rather than lines modified.

Large language migrations use some of the same mechanisms but require additional boundary, deployment, and ownership decisions. [[Large-Scale Code Migration with AI Agents]] keeps that larger workflow separate from routine maintenance.

## Related Notes

- [[Software Decay and the Hidden Costs of Frictionless AI Code]] — How frictionless code generation introduces subtle long-term architectural decay.
- [[Token Optimization and Context Economics in Agentic Workflows]] — Managing token burn, prompt headroom, and attention budgets.
- [[Refactoring Legacy Systems with AI Agents]] — Practical strategies for incremental modernization with agents.
- [[Executable Architecture Tests for Coding Agent Guardrails]] — Enforcing explicit architectural boundaries with executable checks.
- [[Large-Scale Code Migration with AI Agents]] — Translation, staged integration, and ownership after a port.
