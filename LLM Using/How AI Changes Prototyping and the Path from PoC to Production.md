Agents dramatically reduce the cost of answering technical and product questions.

They can quickly:

- build a vertical prototype,
    
- modify an existing codebase aggressively on a temporary branch,
    
- create several architectural variants,
    
- prepare benchmarks,
    
- integrate an unfamiliar library,
    
- build a clickable user flow,
    
- reveal the actual scope of a proposed change.
    

The primary result of a prototype is knowledge, not reusable code.

Examples of useful questions:

- Can this integration work at all?
    
- Is performance sufficient?
    
- Do users understand this workflow?
    
- Which architecture is simpler in practice?
    
- How many parts of the current system would be affected?
    
- Is this direction worth further investment?
    

The ability to cheaply reach a negative answer is extremely valuable.

---

## Prototypes Will Still Reach Production

Agents will not eliminate the phrase:

> The PoC became production.

They may make the problem worse because prototypes will look more complete:

- polished UI,
    
- working backend,
    
- basic tests,
    
- realistic data,
    
- professional structure.
    

The business may conclude that the system is nearly finished.

A prototype may still lack:

- security,
    
- concurrency handling,
    
- migrations,
    
- auditability,
    
- failure recovery,
    
- monitoring,
    
- backward compatibility,
    
- scalability,
    
- regulatory compliance.
    

Before starting, define one of two outcomes:

```text
Disposable prototype:
The implementation will be deleted after the experiment.
```

or:

```text
Evolutionary prototype:
The implementation may become production, so minimum production foundations apply immediately.
```

With cheaper implementation, it may become rational to preserve the lessons, contracts, tests, and benchmark results while discarding the prototype code and building the production version again.

---

## Practical Working Rules

### For prototypes

- Define the research question.
    
- Define what the prototype does not test.
    
- Decide whether the code is disposable before starting.
    
- Use safe data and isolated environments.
    
- Preserve knowledge, not necessarily implementation.
    
- Do not confuse a polished demo with production readiness.
