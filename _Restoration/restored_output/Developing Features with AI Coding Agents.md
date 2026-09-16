## Agent Feature Workflow

```text
Analyze repo -> Write spec -> Build decision tables -> Write acceptance tests -> Human audit -> Build vertical slice -> Arch review -> Full build -> Skeptical review
```

### 1. Repository Analysis
Point the agent at the codebase before writing code.
Map data models, integration boundaries, transactions, and hidden constraints.
Keep code read-only during this phase.

### 2. Behavioral Specification
Define business rules, domain terms, negative paths, and out-of-scope boundaries.
Build decision tables for branching logic.
Models invent requirements when branch priorities stay ambiguous.

### 3. Test-First Setup
Write acceptance and contract tests before writing feature code.
Run tests to confirm they fail.
Failing tests prove the suite catches missing behavior.

### 4. Audit Test Semantics
Review test meaning, not syntax.
Check whether the agent hallucinated unstated requirements.
Ensure negative cases run.
Verify the tests reject accidental legacy behavior.

### 5. Freeze Test Contracts
Lock approved acceptance tests in git.
Block the agent from editing these tests while writing code.
Allow the agent to add internal unit tests only.
Review all changes to acceptance files manually.

### 6. Vertical Slice
Build one complete path from ingress to storage.
Validate architectural boundaries on this single slice.
Do not scaffold multiple files before this slice passes review.

### 7. Stop Circular Logic
Tests show examples. They do not capture intent.
Never let the agent write both tests and code unsupervised.
Self-authored tests confirm the agent's own misconceptions.
Anchor tests to explicit decision tables.

### Execution Checklist
- Inspect the repo before editing.
- Write explicit specs with decision tables.
- Freeze failing acceptance tests.
- Build one end-to-end slice first.
- Separate mechanical refactors from business changes.
- Review final output with a skeptical peer.
