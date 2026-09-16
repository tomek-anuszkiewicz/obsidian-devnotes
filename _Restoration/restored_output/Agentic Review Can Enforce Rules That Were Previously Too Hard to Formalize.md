### Executable Architecture Policies

Traditional static analysis handles deterministic invariants:

```text
Domain must not reference Infrastructure.
Every public endpoint must require authorization.
Result must never be negative.
All handlers must implement a particular interface.
```

Deterministic checkers enforce syntax, AST patterns, and types well.
However, critical architectural rules rely on context and semantic intent:
- Avoid premature abstractions.
- Keep controllers thin without redundant mapping layers.
- Prevent domain logic leaks into infrastructure helpers.
- Restrict cross-module communication to public contracts.

Encoding these semantic rules into linters costs too much time.
Reviewers traditionally enforced these standards from memory.

### Agent Runtime for Natural-Language Rules

Feed architecture documentation directly into the review agent context:

```text
docs/architecture/principles.md
docs/domain/invariants.md
docs/security/guidelines.md
ADRs/
```

Prompt the agent to inspect incoming pull requests:
1. Pinpoint the violating lines.
2. Cite the breached policy or ADR.
3. Explain the architectural conflict.
4. Suppress output when confidence falls below threshold.

### Three-Tier Quality Stack

```text
Human Review       -> Strategic architectural trade-offs
Agentic Review     -> Semantic policy and intent checks
Deterministic CI   -> Types, linters, unit tests, analyzers
```

Review agents eliminate manual auditing fatigue.
They audit 100-file pull requests without skimming.
They evaluate rarely violated rules on every commit.

### Deterministic Tests vs. Semantic Inspection

Never replace fast deterministic checks with LLM prompts.
Deterministic checks remain authoritative, cheap, and reproducible:

```csharp
Assert.True(result >= 0);
```

Reserve agents for rules where formalization costs too much.
Use agents to catch semantic bypasses of formal rules.

#### Case 1: Invariant Circumvention
A price invariant states that values cannot fall below zero.
A developer clamps negative inputs to zero.
The deterministic unit test passes:

```csharp
// Unit test passes
Assert.True(price >= 0);
```

The agent flags the bug: Clamping silently masks invalid domain state.

#### Case 2: Structural Decoupling Evasion
An architecture test forbids importing Module B from Module A.
The test passes because Module A copies Module B internal schemas directly.
The agent flags semantic coupling despite zero direct project references.

### Bidirectional Feedback Loop

#### 1. Promote Agent Findings to Deterministic Analyzers
Track repeated agent detections.
If an agent repeatedly catches infrastructure imports in domain code, write an AST analyzer.
Automate the check permanently.
Free the agent context for novel patterns:

```text
Informal Principle -> Agent Audits PRs -> Pattern Stabilizes -> Static Analyzer Rule Added
```

#### 2. Explain Deterministic Failures
Use agents to explain static analysis failures.
A linter flags: `Namespace X references Namespace Y`.
The agent provides context:
`Namespace Y contains raw database entities. Use CustomerContract instead.`

### Ephemeral Investigative Tests

Agents can generate throwaway tests to validate hypotheses during review.
An agent suspects a race condition in a cache implementation.
It writes a temporary test and executes it:

```text
Agent Generates Test -> Reproduces Concurrency Bug -> Promotes to Regression Suite
```

If the race reproduces, promote the test to the regression suite.
Otherwise, discard the scratchpad test.

### Continuous Architecture Checklist

Run these semantic checks on every pull request:
- Does this diff introduce a one-off generic framework?
- Does domain logic leak into infrastructure adapters?
- Does this change contradict recorded ADR decisions?
- Does the new abstraction justify its operational cost?
