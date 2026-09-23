---
title: Refactoring Legacy Systems with AI Agents
tags:
  - legacy-code
  - refactoring
  - ai-agents
  - software-engineering
  - migration
  - testing
aliases:
  - Legacy Migration with Agents
  - AI-Driven Code Modernization
---

## Refactoring Legacy Code with Agents

Agents are useful for legacy modernization, but broad instructions are dangerous.

Avoid:

> Rewrite this module using clean architecture.

Prefer small, behavior-preserving steps:

1. map the current behavior,
    
2. add characterization tests,
    
3. rename ambiguous concepts,
    
4. move code without editing it,
    
5. extract pure functions,
    
6. introduce explicit types,
    
7. isolate side effects,
    
8. compare old and new outputs,
    
9. only then introduce new business behavior.
    

Characterization tests do not claim that the current behavior is correct. They record what the system currently does so that refactoring does not change it accidentally.

For pricing systems, run both implementations against historical data:

```text
old pricing result
vs.
new pricing result
```

During pure refactoring, results should remain identical, including rounding behavior.

---

## Use Multiple Reviewable Commits

Agents can be instructed to create a meaningful commit history.

A useful sequence is:

```text
1. Add characterization tests
2. Rename and move only
3. Extract types without behavior change
4. Extract calculation stages
5. Introduce the explicit domain model
6. Change the business rule
7. Remove obsolete code
```

Each commit should:

- have one purpose,
    
- compile independently,
    
- pass relevant tests,
    
- clearly state whether it changes behavior,
    
- avoid mixing mechanical and semantic changes.
    

Do not allow histories such as:

```text
add implementation
fix compilation
fix tests
cleanup
```

Those commits describe the agent's mistakes, not the evolution of the system.

A good history allows a reviewer to distinguish:

- existing behavior,
    
- structural preparation,
    
- the exact business change,
    
- later cleanup.
    

---

## Practical Working Rules

### For commits

- One purpose per commit.
    
- Every commit should compile and pass tests.
    
- Keep rename, move, formatting, refactoring, and behavior changes separate.
    
- Do not alter expected test values during behavior-preserving refactoring.
    
- Make the commit history explain the evolution of the system.
