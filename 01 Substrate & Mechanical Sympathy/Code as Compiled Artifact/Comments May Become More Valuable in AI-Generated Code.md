---
title: Comments May Become More Valuable in AI-Generated Code
tags:
  - ai-agents
  - software-engineering
  - documentation
  - code-review
  - maintainability
  - intent-specification
  - mechanical-sympathy
aliases:
  - Code Comments in AI Era
  - Semantic Value of Comments in AI Code
  - Comments as Local Context Retrieval
  - Negative Knowledge Comments in Agentic Code
---

# Comments May Become More Valuable in AI-Generated Code

## The Core Thesis: Comments as Physical Local Context Retrieval

In the era of autonomous AI coding agents, code comments undergo a radical functional transformation: **from passive human reading aids to high-priority, physically co-located context injection anchors**.

```text
HISTORICAL HUMAN PARADIGM:
  "Good code is self-documenting; the 'why' belongs in commit messages."
  Result: Comments explaining syntax are banned; business intent is exiled
          to Git history, Jira tickets, Slack threads, and unwritten tribal memory.

AGENTIC PARADIGM:
  Descriptive comments (what the code does) = ZERO VALUE (Agents reconstruct syntax instantly).
  Decisional comments (why the code was built this way) = MAXIMUM VALUE.
  Result: Comments are the ONLY organizational artifacts guaranteed to physically enter
          the agent's working context window alongside the code being modified without
          costly, speculative external tool calls.
```

When an agent enters a repository to modify a specific routine, it does not possess the historical tribal memory of the engineering team. It will never read the three-year-old Jira ticket, the buried Git commit message, the archived Slack debate, or the forgotten meeting notes that explain why a non-obvious conditional check exists. Nor will an agent proactively fall back to `git blame` to inspect every routine or line of code it modifies.

However, **any comment physically placed next to the implementation is guaranteed to be ingested into the model's context window**. Comments therefore act as a microscopic, zero-latency semantic cache—anchoring human architectural intent directly at the point of mutation, as explored in [[Developing Features with AI Coding Agents|developing features with AI coding agents]].

### The Decisional Inversion:
1. **The Death of Descriptive Comments**: Explaining *how* an algorithm steps through an array or formats an output is pure token noise. Foundation models parse syntactic control flow effortlessly.
2. **The Sovereign Value of Decisional Constraints**: Inline annotations that explain *why* an unusual business rule exists, *which* contract mandated it, and *what* intuitive simplifications are strictly prohibited represent the most valuable intellectual property in the repository.

---

## The Git History Fallacy: Why VCS Cannot Replace Inline Decisional Anchors

In traditional software engineering culture, developers often push back against comments by appealing to version control: *"If you want to understand why this line was written, check `git blame` and the commit message."*

While a deliberate human engineer might occasionally use `git blame` during deep investigation, relying on version control as an agent context mechanism completely collapses in practice due to four architectural dynamics:

1. **The Epistemic Blindspot (Zero Proactive Doubt)**:
   An agent only invokes tools like `git blame`, `git log -S`, or commit explorers during **forensic debugging** after a test or build has already failed. When an agent performs routine feature work, refactoring sweeps, or deduplication passes, it experiences **high completion confidence**. Seeing a redundant-looking guard or historical quirk, the model assumes the code is simply clumsy or dead—it experiences zero epistemic doubt to pause, suspect hidden context, and run a speculative `git blame` check.
2. **Context Latency and Tool-Call Multiplication**:
   Checking Git history is an external, tool-mediated operation. If an agent were instructed to inspect `git blame` for every function or line it intends to touch, the execution loop would instantly collapse under a deluge of tool round-trips (`git blame` $\rightarrow$ `git log` $\rightarrow$ `git show <hash>`), exploding token budgets and latency by orders of magnitude.
3. **Provenance Decay and Blame Erosion**:
   `git blame` is fragile. Automated style formatting passes, import reorderings, file renames, and prior agent cleanup sweeps frequently overwrite the surface commit line with cosmetic commits (`style: format with linter`). Digging multiple commits deep to discover the original domain decision requires recursive archaeological git navigation that agents cannot practically conduct on the fly.
4. **Preventative Guardrail vs. Forensic Autopsy**:
   Version control is fundamentally **forensic**—an autopsy instrument designed to investigate *how something broke after the fact*. Decisional comments are **preventative**—they reside physically inside the token stream, immediately intercepting the model's autoregressive generation *before* the invalid refactoring is written.

---

## Code is Syntactically Self-Documenting, Never Semantically

Even the cleanest, most idiomatic code cannot express business intent or historical constraints through naming alone:

```text
// CLEAN CODE (Syntactically obvious, semantically ambiguous):
apply_non_refundable_supplier_cancellation_fee(booking)
```

While clean, this signature fails to answer critical questions:
- *Why is this specific supplier exempt from standard cancellation policies?*
- *Is this behavior legally mandated by contract, or a temporary sales promotion?*
- *What unstated operational assumption breaks if an agent replaces this with standard hotel policy?*

### The Contrast in Comment Value:

```text
POOR COMMENT (Pure Noise / Mechanics Repetition):
// Charge 50% if booking starts in less than 3 days
if booking.start_date < clock.now() + 72.hours:
    fee = booking.total_price * 0.50

HIGH-VALUE DECISIONAL ANCHOR (Essential Context Protection):
// DOMAIN INVARIANT:
// Cancellations within 72 hours incur a 50% charge because Supplier X 
// refuses wholesale refunds beyond this threshold under Contract Schedule B.
// DO NOT refactor or consolidate this with the standard hotel cancellation policy.
if booking.start_date < clock.now() + 72.hours:
    fee = booking.total_price * 0.50
```

The high-value comment preserves context that cannot be derived from syntax. As detailed in [[Why Business Logic Is the Hardest Part of Agentic Coding|why business logic is the hardest part of agentic coding]], it actively protects intentional edge cases from being erased during automated refactorings.

---

## Negative Knowledge Comments: Fencing Off Intuitive Traps

When coding agents perform codebase-wide refactoring sweeps, their pretraining priors push them toward aggressive simplification and deduplication. If a condition looks strange or redundant, an unconstrained agent will naturally delete or "streamline" it.

To counteract this, modern codebases must utilize **Negative Knowledge Comments**—explicitly declaring what must *never* be done:

```text
// NEGATIVE KNOWLEDGE GUARD:
// Do not compute this total from payment.amount.
// Historical bookings imported prior to Q3 2025 already embed agency margins
// inside the gross amount; using payment.amount will cause double-counting.
net_total = calculate_historical_margin(booking)
```

```text
// CONCURRENCY GUARD:
// This check appears redundant with the database constraint, but upstream 
// inventory providers intermittently emit duplicate webhook events across 
// separate HTTP connections within 5ms windows. Keep in-memory deduplication active.
if idempotency_cache.contains(event.id):
    return Result.ALREADY_PROCESSED
```

### The Agentic Reasoning Inversion:
- **Without Comment**: An agent detects a seemingly redundant check $\rightarrow$ classifies it as dead code $\rightarrow$ deletes it $\rightarrow$ reintroduces a race condition.
- **With Negative Comment**: An agent detects the check $\rightarrow$ reads the explicit warning $\rightarrow$ recognizes an intentional domain constraint $\rightarrow$ preserves the invariant.

---

## The 4-Tier Documentation Architecture

Comments do not replace system-level documentation or architectural decision records (ADRs); they occupy the innermost operational tier:

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. SYSTEM SPECIFICATIONS                                    │
│    High-level user requirements, business goals, contracts. │
├─────────────────────────────────────────────────────────────┤
│ 2. ARCHITECTURAL DECISION RECORDS (ADRs) & REPO HISTORY     │
│    System-wide trade-offs, technology choices, commit logs. │
├─────────────────────────────────────────────────────────────┤
│ 3. DECISIONAL ANCHOR COMMENTS                               │
│    Local intent, negative knowledge, non-obvious invariants.│
├─────────────────────────────────────────────────────────────┤
│ 4. SOURCE CODE                                              │
│    The executable compilation target.                       │
└─────────────────────────────────────────────────────────────┘
```

An agent performing a small bugfix in three years will likely never be passed the full ADR repository or traverse the Git commit graph for every modified line. It **will** receive Tier 3 and Tier 4 directly in its working context window. 

---

## Context Engineering for Future Agents

When instructing agents to implement features, engineering teams should mandate that agents author their own future context:

> **The Agentic Invariant Instruction:**  
> *"Whenever implementing a non-obvious business rule, historical exception, or negative constraint that cannot be reconstructed purely from the code syntax, write a concise decisional comment directly above the implementation explaining WHY it must remain that way."*

This creates a self-reinforcing documentation loop:
```text
Task Specification ──► Active Coding Agent ──► [Executable Code + Decisional Comments]
                                                              │
                                                              ▼
                                               Future Agent Context (Preserved Intent)
```

The code satisfies immediate execution; the decisional comments protect future autonomous maintenance cycles from cognitive decay.

---

## Summary Principles

1. **Comments are Context Retrieval Anchors**: Inline comments are the only knowledge artifacts guaranteed to enter the model's context window alongside the code without requiring external tool calls.
2. **Ban Descriptive Comments**: Never write comments explaining *how* syntax works; agents parse control flow effortlessly.
3. **Mandate Decisional & Invariant Comments**: Explain *why* code violates common intuition and *which* requirements shaped it.
4. **The Git History Fallacy**: Version control history is forensic and tool-mediated; an agent will never proactively run `git blame` on every line during routine mutation turns.
5. **Fence Invariants with Negative Knowledge**: Explicitly warn against seemingly obvious simplifications that would break domain rules.
6. **Protect Future Agent Trajectories**: Treat high-signal comments as long-term context engineering for subsequent automated refactoring turns.

---

## Related Notes

- **[[Why Business Logic Is the Hardest Part of Agentic Coding]]**: Explains why comments must capture the "why" of intentional non-standard business rules.
- **[[Retrieval-Augmented Generation and Context Architecture]]**: Contrasts multi-hop tool-based retrieval (Git blame, issue tracking) with zero-latency co-located context injection.
- **[[What Should Organizations Preserve from AI-Assisted Development]]**: Capturing Business Decision Records (BDRs) and architectural guardrails alongside code.
- **[[AI-Generated Architectural Documentation from Code]]**: How semantic code comments feed living architectural models and agent context.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Generating in-flight documentation cards and semantic blueprints as deterministic agent frameworks.
- **[[Designing Software for AI Agents]]**: Protecting domain subtleties from being accidentally refactored away by coding agents.

---

## Relationship to the Knowledge Graph

- **[[Software Engineering May Shift Toward Code Optimized for Agents]]**: The shift from descriptive comments to decisional constraints.
- **[[Software Entropy and the Zero-Friction Trap]]**: Using negative comments to stop zero-friction agents from over-simplifying critical edge cases.
- **[[The 5-Layer System Stack for Agentic Software Engineering]]**: Anchoring decisional comments in Layer 1 (Code as Compiled Artifact) and Layer 4 (Model Context).
- **[[LLM Agents and Institutional Memory]]**: Preserving corporate tribal knowledge directly inside executable files.
