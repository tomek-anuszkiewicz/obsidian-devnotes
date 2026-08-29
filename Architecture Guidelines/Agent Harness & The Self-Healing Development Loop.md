The core engine of autonomous software development is the **Agent Harness**—a deterministic execution environment that manages context, invokes tools, runs verification gates, and orchestrates iterative code repair before changes reach human review.

---

## 1. The Self-Healing Loop (Actor-Critic Architecture)

Instead of expecting an LLM to generate production-ready code in a single prompt, the harness runs a cyclic, self-correcting feedback loop.

```text
[Task Prompt / Issue]
        │
        ▼
┌─► [Agent Coder] ──(Generates Patch)──┐
│                                       │
│                                       ▼
│                             [Deterministic Verification]
│                             - Tests (pytest, jest)
│                             - Linters & Typecheck (mypy, eslint)
│                             - Build & Syntax Check
│                                       │
│                         ┌─────────────┴─────────────┐
│                      (Failed)                    (Passed)
│                         │                           │
│                         ▼                           ▼
│                  [Error Trace]             [Specialized Reviewers]
│                         │                  (Security, Architecture)
│                         │                           │
└─ (Iterate / Fix) ◄──────┴───────────────────────────┤
                                                      │ (All Passed)
                                                      ▼
                                            [Git Commit & Push]
```

### Key Loop Principles
* **Structured Error Feedback:** Fixers receive raw error outputs (stack traces, failed test names, line numbers) rather than vague re-prompts.
* **Hard Iteration Caps:** Enforce a maximum iteration threshold (e.g., N=3). If the agent cannot solve the issue within the budget, the loop aborts and triggers human escalation.
* **Atomic Operations:** Each cycle works in a dedicated Git worktree/branch. Failed attempts can be cleanly rolled back (`git reset --hard`).

---

## 2. Custom Python Harness vs. Interactive CLI Agents

There is a fundamental trade-off between interactive pair-programming tools (e.g., Claude Code, Cursor) and custom program-driven harnesses.

| Dimension | Interactive CLI / UI (Claude Code, Cursor) | Custom Python Harness |
| :--- | :--- | :--- |
| **Execution Mode** | Synchronous, interactive (human at keyboard). | Asynchronous, headless, event-driven (CI/CD, webhooks). |
| **Architecture** | Single-agent context handling tasks sequentially. | Multi-agent orchestration (distinct personas with isolated contexts). |
| **Escalation** | Prompts directly in the terminal interface. | Generates structured escalation artifacts (Draft PRs, inline diff comments). |
| **Control Flow** | Black-box logic governed by vendor abstractions. | Deterministic Python flow (`while`, `try...except`, custom state machines). |
| **Best For** | Feature exploration, ad-hoc refactoring, solo dev. | Background bug-fixing, batch repository migrations, strict CI gates. |

---

## 3. Skills as Python Functions (Beyond Simple Bash CLI)

While agents can run terminal commands, building skills as native Python functions provides safety, AST parsing, and direct API integration.

### Advantages of Native Python Skills
1. **Pre-filtering Context (AST Parsers):** Instead of dumping a 3000-line file into context, a Python skill uses `ast` or `tree-sitter` to extract only the target class or method signature.
2. **Direct SDK Integration:** Interacting with GitHub (`PyGithub`), cloud providers (`boto3`), or databases (`SQLAlchemy`) avoids fragile CLI stdout parsing.
3. **Deterministic Sandboxing:** Python skills manage local Docker containers or SQLite in-memory databases to validate migrations without side effects.

### Minimal Python Harness Skeleton

```python
import subprocess
from dataclasses import dataclass
from typing import Tuple

@dataclass
class HarnessState:
    task: str
    iteration: int = 0
    max_iterations: int = 3
    error_log: str = ""

def run_deterministic_tests() -> Tuple[bool, str]:
    """Runs test suite and returns pass status with stdout/stderr."""
    result = subprocess.run(["pytest", "tests/"], capture_output=True, text=True)
    return result.returncode == 0, result.stdout + result.stderr

def self_healing_loop(state: HarnessState):
    while state.iteration < state.max_iterations:
        state.iteration += 1
        
        # 1. Generate / Edit Code via LLM Tool Call
        apply_llm_patch(state)
        
        # 2. Deterministic Verification Gate
        tests_passed, test_output = run_deterministic_tests()
        if not tests_passed:
            state.error_log = test_output
            continue
            
        # 3. Static Analysis & Multi-Agent Gate
        if run_security_audit_agent():
            subprocess.run(["git", "commit", "-am", f"fix: {state.task}"])
            return {"status": "SUCCESS"}
            
    # 4. Limit Exceeded -> Escalate to Human
    return trigger_human_escalation(state)
```

---

## 4. Docs-as-Code Drift Prevention

An autonomous harness must enforce documentation synchronization as part of its **Definition of Done**.

```text
[Code Change Generated]
          │
          ▼
[Docs-Drift Agent]
  ├── Compares API signatures against /docs, OpenAPI specs, and README.md
  ├── Detects missing parameters or outdated return types
  └── Generates matching Markdown updates in the same branch commit
```

* **Atomicity:** Code changes, unit tests, and documentation diffs must live within the same pull request commit.
* **Gatekeeper Rule:** Architecture reviewers reject patches where public interfaces changed without corresponding updates in `/docs/*.md`.

---

## 5. Escalation: Passing Impasses to Humans

When the automated loop reaches its iteration ceiling without passing all gates, it must not dump uncontextualized code on the human reviewer.

```text
[Loop Aborted at Iteration 3]
              │
              ▼
[Escalation Artifact Generation]
  ├── Summary of disagreement / failing constraint
  ├── Diff evolution across attempts
  └── 2-3 Concrete Decision Options (A / B / C)
              │
              ▼
[Draft PR with Inline Comments on GitHub]
```

### Structure of an Escalation Inline Comment

> ⚠️ **HUMAN ARBITRATION REQUIRED** (Iteration limit reached)
> 
> **Conflict Summary:**
> * Security Reviewer flagged SQL query in loop (potential N+1).
> * Coder Agent attempted batching, but encountered missing foreign key constraint in SQLite test setup.
> 
> **Options for Developer:**
> - [ ] **Option A:** Add missing index migration and retry batch query.
> - [ ] **Option B:** Accept single-query fetch due to strict low-volume usage.
> - [ ] **Option C:** Revert module changes and revise high-level architecture.

The developer replies directly in the GitHub PR review thread, triggering a webhook that re-engages the harness with explicit human guidance.