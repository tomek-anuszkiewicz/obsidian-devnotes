---
title: Comments May Become More Valuable in AI-Generated Code
tags:
  - ai-agents
  - software-engineering
  - documentation
  - code-review
  - maintainability
  - intent-specification
  - code-comments
aliases:
  - Code Comments in AI Era
  - Semantic Value of Comments in AI Code
  - Comments as Local Context Retrieval
  - Negative Knowledge Comments in Agentic Code
---

# Comments May Become More Valuable in AI-Generated Code

## The Shift: From Explaining Syntax to Preserving "Why"

For years, the software engineering industry lived by the clean code mantra:  
> *"Good code is self-documenting. If you need a comment, your code is too complicated."*

That rule made complete sense when applied to comments that merely repeated what the code already said:
```text
// POOR COMMENT: Pure noise that repeats the syntax
// Increment the counter by one
counter += 1
```

AI coding agents parse syntax, types, and control flow effortlessly. Writing a comment that describes *what* an algorithm does is a complete waste of space.

However, in the era of autonomous coding agents, **comments that explain "WHY" something was built in a non-obvious way become the most valuable lines in your repository**.

```text
TRADITIONAL VIEW:
  Comments explain code syntax ──► Mostly useless (Good code is readable).
  Business intent lives in Jira, Slack, or developers' heads.

AGENTIC REALITY:
  Descriptive comments (what code does) = ZERO VALUE (AI reads syntax instantly).
  Contextual comments (why it was built this way) = MAXIMUM VALUE.
  Comments are the ONLY documentation guaranteed to be inside the agent's
  context window right next to the code it is modifying.
```

---

## Code is Self-Documenting Syntactically, Never Semantically

Clean, idiomatic code communicates execution structure, but it can never explain the invisible business or operational reasons behind it.

Consider this clean function call:
```text
ingest_telemetry_batch(records, batch_size = 250)
```

Syntactically, this is spotless. But it leaves critical questions unanswered:
- *Why 250 instead of 5,000 for maximum throughput?*
- *Is 250 an arbitrary default, or does it prevent an out-of-memory crash?*
- *What happens if an AI agent tries to "optimize" this by batching all records in a single database query?*

### The Contrast in Comment Value

```text
USELESS COMMENT (Describes syntax):
// Split records into chunks of 250 and insert into database
for chunk in records.chunk(250):
    database.bulk_insert(chunk)

HIGH-VALUE COMMENT (Explains the hidden constraint):
// WIRE PROTOCOL LIMIT:
// The underlying database driver allows a maximum of 65,535 query parameters.
// With 240 columns per telemetry record, any batch larger than 273 rows triggers 
// a silent driver buffer overflow. We cap at 250 for safety margin.
// DO NOT increase this batch size without changing the driver protocol.
for chunk in records.chunk(250):
    database.bulk_insert(chunk)
```

Without that comment, an AI agent asked to *"optimize database ingestion"* will see `250` as an inefficient bottleneck. It will naturally rewrite the code to send 5,000 rows at once, instantly crashing in production.

---

## Why Git History and Jira Can't Replace Inline Comments

Developers often argue: *"If someone wants to know why that line exists, they can check `git blame` or the original ticket."*

While a human engineer might do archaeological research during a complex debugging session, **AI agents almost never do this during routine feature development**:

1. **Zero Proactive Doubt**: When an agent refactors code, it generates code with high statistical confidence. If it sees an unusual check, it doesn't stop to think: *"Hmm, maybe there was an obscure production outage in 2024 that required this check; let me run `git log -S` and check Jira."* It simply assumes the code is redundant and deletes it.
2. **Context and Tool Latency**: Asking an agent to run `git blame`, fetch historical commit hashes, and query ticket systems for every function it touches would explode execution time, tool roundtrips, and token costs.
3. **Commit History Decays**: Reformatting with a linter, renaming files, or previous AI cleanup sweeps easily overwrite surface `git blame` lines with cosmetic commit messages (`style: format code`).
4. **Preventative vs. Post-Mortem**: Git history is an autopsy tool used *after* something breaks. An inline comment is a preventative guardrail that sits directly in the prompt *before* the agent generates the wrong code.

---

## Integration Quirks: The Third-Party API Trap

Another place where clean syntax masks reality is weird third-party API behavior:

```text
// THIRD-PARTY GATEWAY QUIRK:
// The payment clearinghouse gateway returns HTTP 200 OK even on terminal card declines,
// placing the error code inside an unescaped XML body payload.
// DO NOT refactor this to standard HTTP status checks (e.g., response.is_success).
if response.status == 200 and "ERR_DECLINED" in response.body:
    handle_failure(response)
```

To any modern programmer or AI model, checking for error strings inside an `HTTP 200 OK` block looks like amateur technical debt. An agent tasked with *"modernizing API error handling"* will instinctively replace it with `if response.is_success:`, accidentally converting failed credit card transactions into successful orders.

---

## Negative Knowledge Comments: Declaring What NOT to Do

When coding agents perform refactoring passes, they naturally try to simplify code and remove repetition. If a condition looks redundant, the model's instinct is to streamline it.

To protect critical edge cases, use **Negative Knowledge Comments** that explicitly forbid tempting simplifications:

```text
// NETWORK CONCURRENCY GUARD:
// Do not replace this sequential loop with parallel worker tasks.
// The downstream TLS endpoint drops connections if concurrent handshakes exceed 16.
// Throughput is bound by remote socket limits, not local CPU.
for endpoint in cluster_endpoints:
    establish_secure_session(endpoint)
```

```text
// DEDUPLICATION GUARD:
// This check looks redundant with the database unique constraint, but the upstream
// webhook provider occasionally sends duplicate events across separate connections
// within 5 milliseconds. Keep this in-memory check to prevent duplicate email alerts.
if idempotency_cache.contains(event.id):
    return Result.ALREADY_PROCESSED
```

### The Difference in Agent Reasoning:
* **Without the comment**: The agent sees a check that seems redundant with the database $\rightarrow$ classifies it as dead code $\rightarrow$ deletes it $\rightarrow$ reintroduces a race condition.
* **With the negative comment**: The agent reads the warning $\rightarrow$ recognizes the intentional constraint $\rightarrow$ preserves the protection.

---

## The 4 Tiers of System Documentation

Comments don't replace architectural documentation; they serve as the innermost guardrail:

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. SYSTEM SPECIFICATIONS                                    │
│    Business requirements, customer goals, API contracts.    │
├─────────────────────────────────────────────────────────────┤
│ 2. ARCHITECTURAL DECISION RECORDS (ADRs)                    │
│    System-wide design decisions, technology choices.        │
├─────────────────────────────────────────────────────────────┤
│ 3. INTENT & CONSTRAINT COMMENTS                             │
│    Local reasons, negative knowledge, non-obvious quirks.   │
├─────────────────────────────────────────────────────────────┤
│ 4. SOURCE CODE                                              │
│    The actual executable implementation.                    │
└─────────────────────────────────────────────────────────────┘
```

When an agent fixes a small bug two years from now, it will not read your entire company Confluence or 50 ADR documents. But it **will** receive Tier 3 comments directly alongside the code in its context window.

---

## Pre-Emptive Knowledge Rehydration: Mining Git for Comments

If legacy code doesn't have these comments, how do you add them without spending months writing them by hand?

You can use an **offline archaeology script**:
1. Search `git log` for commits with keywords like *"hotfix"*, *"workaround"*, *"vendor bug"*, *"race condition"*, or *"do not touch"*.
2. Have an AI model read the commit message and the associated PR discussion.
3. Have the model synthesize a 2-line comment explaining the non-obvious reason, and place it directly above the code.
4. Commit those comments back into the repo.

Now, whenever an agent opens that file in the future, the historical context is already sitting right there in the source code.

---

## Summary: How to Write Comments for the AI Era

1. **Delete Syntax Paraphrasing**: Never explain *how* code works; models read syntax effortlessly.
2. **Document Intent and Quirks**: Always explain *why* non-obvious rules, magic numbers, or weird API workarounds exist.
3. **Use Negative Comments**: Tell the agent what *not* to do (e.g., *"Do not replace with parallel execution"*, *"Do not simplify this status check"*).
4. **Comments are Local Context**: A comment inside the source file is the only piece of documentation guaranteed to enter the agent's context window during a task.
5. **Code explains what happens. Comments explain why it must happen that way.**

---

## Related Notes

- **[[Why Business Logic Is the Hardest Part of Agentic Coding]]**: Why comments must capture the intentional business reasons behind non-standard rules.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]**: The shift from human-centric code aesthetics toward machine-legible, explicit architectures.
- **[[Designing Software for AI Agents]]**: How to design repository structures that agents can navigate without getting lost.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Living Markdown specifications that guide agents alongside inline comments.
- **[[Testing in the Model, Agent, LLM Era]]**: Using deterministic test suites to lock down behavior that comments describe.
- **[[LLM Agents and Institutional Memory]]**: Preserving corporate tribal knowledge directly inside code repositories.

---

## Relationship to the Knowledge Graph

- **[[The 5-Layer System Stack for Agentic Software Engineering]]**: Situating living documentation and comments in [[The 5-Layer System Stack for Agentic Software Engineering|Layer 1 (Code Architecture & Hardware Execution)]].
- **[[Software Entropy and the Zero-Friction Trap]]**: Using negative comments to stop AI from over-simplifying critical edge cases.
- **[[What Should Organizations Preserve from AI-Assisted Development]]**: Capturing business decisions and domain context rather than just raw code.
