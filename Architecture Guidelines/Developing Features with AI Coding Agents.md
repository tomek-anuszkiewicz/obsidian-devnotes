## A Strong Workflow for Larger Features

A useful process is:

```text
repository analysis
→ behavioral specification
→ examples and decision tables
→ acceptance tests
→ human review
→ implementation of one vertical slice
→ architectural review
→ full implementation
→ independent skeptical review
→ documentation update
```

### Step 1: Repository Analysis

The agent should first locate:

- existing business flows,
    
- data models,
    
- integration points,
    
- transactions,
    
- existing tests,
    
- compatibility risks,
    
- hidden assumptions.
    

It should not modify the code yet.

### Step 2: Behavioral Specification

The specification should include:

- business objective,
    
- terminology,
    
- rules,
    
- exceptions,
    
- negative cases,
    
- side effects,
    
- compatibility requirements,
    
- non-functional constraints,
    
- explicit out-of-scope items.
    

### Step 3: Tests Before Implementation

The agent can prepare:

- business-rule tests,
    
- acceptance tests,
    
- regression tests,
    
- API contract tests,
    
- integration tests.
    

New tests may initially fail. That confirms that they detect the missing behavior.

### Step 4: Human Review of Meaning

The reviewer should not focus only on test implementation quality.

The main questions are:

- Does the test describe the correct business behavior?
    
- Did the agent invent an unstated rule?
    
- Are negative cases present?
    
- Are priorities between rules correct?
    
- Is the test coupled to one implementation unnecessarily?
    
- Does the test preserve an accidental legacy behavior?
    

### Step 5: Freeze the Acceptance Contract

The implementing agent should not freely modify approved acceptance tests.

It may add technical tests, but changes to the accepted business contract require another review.

### Step 6: Implement a Small Vertical Slice

Instead of generating the whole feature at once, implement one full path from entry point to result.

This reveals whether the architecture is appropriate before dozens of files are created.

---

## Tests Are Executable Specifications, but Not Complete Specifications

A test demonstrates an expected example.

It does not always explain:

- why the rule exists,
    
- what a domain term means,
    
- what must not be simplified,
    
- why two similar cases differ,
    
- which behavior is historical but still required.
    

The strongest combination is:

```text
business decision
+ examples or decision table
+ acceptance tests
+ explicit implementation
```

The agent should not be allowed to define both the implementation and the meaning of correctness without independent human review.

Otherwise, it can write tests that confirm its own incorrect interpretation.

---

## Practical Working Rules

### For feature development

- Analyze before modifying.
    
- Write or approve the behavioral specification.
    
- Use examples and decision tables.
    
- Review acceptance tests before implementation.
    
- Freeze approved business tests.
    
- Implement one vertical slice first.
    
- Separate mechanical changes from business changes.
    
- Require a skeptical second review.
