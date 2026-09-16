---
trigger: always_on
description: Enforce language-agnostic abstractions, ubiquitous engineering concepts, avoidance of concrete source code snippets, and multi-ecosystem breadth across notes.
---

# Language-Agnostic Architecture & Generalized Technology Abstractions Rule

Whenever creating, updating, or refactoring architectural notes and documentation across this Obsidian vault, the agent must treat software architecture as **language-agnostic**, **concept-driven**, and **grounded in universal software engineering abstractions**. Notes in this vault document durable system physics, transactional invariants, and memory hierarchies—not transient framework idioms.

---

## 1. Core Operating Principle: Architecture Above Implementation

Frameworks, libraries, and vendor branding decay rapidly; fundamental systems dynamics remain invariant. Architectural documentation must decouple runtime physics from implementation-specific baggage:

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. UNIVERSAL ARCHITECTURAL ABSTRACTIONS                     │
│    Data flows, transactional boundaries, memory hierarchy. │
├─────────────────────────────────────────────────────────────┤
│ 2. AGNOSTIC REPRESENTATION FORMATS                          │
│    ASCII flowcharts, Mermaid statecharts, pseudocode.       │
├─────────────────────────────────────────────────────────────┤
│ 3. MULTI-ECOSYSTEM EQUILIBRIUM                              │
│    Balanced grounding across systems, managed & dynamic.    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Abstraction Mapping & Universal Primitives

Always frame architectural discussions around universal software engineering concepts rather than platform-specific implementations:

| Avoid Specific Implementation / Vendor Branding | Prefer Universal Engineering Abstraction |
| :--- | :--- |
| *Entity Framework*, *Hibernate*, *Prisma* | **Persistence Layer / Object-Relational Mapping (ORM)** |
| *AutoMapper*, *MapStruct* | **Object Projection Utility / Declarative Data Transformer** |
| *Newtonsoft.Json*, *Serde*, *Jackson* | **Serialization & Deserialization Pipeline** |
| *Roslyn Source Generators*, *Java Annotation Processors* | **Compile-Time Metaprogramming / Integrated Code Generators** |
| *Stryker.NET*, *PIT Mutation* | **Mutation Testing Harness** |
| *ASP.NET Core*, *Spring Boot*, *Express* | **Application Runtime / HTTP Service Mesh / Host Process** |
| *Postgres*, *SQL Server*, *Oracle* | **Relational Database Engine / ACID Transaction Manager** |
| *Redis*, *Memcached* | **In-Memory Key-Value Cache / Ephemeral State Store** |
| *AWS SQS*, *Kafka*, *RabbitMQ* | **Distributed Log / Partitioned Streaming Bus / Message Broker** |

---

## 3. Code Presentation Standards

### 1. Rejection of Language-Specific Implementation Dumps
- Unless a note is explicitly dedicated to a low-level compiler optimization, instruction set analysis, or byte layout study, **avoid presenting concrete source code snippets in specific languages (such as C#, Java, Python, Go, Rust, or C++)**.
- Language-specific syntax dates quickly, introduces syntactical bike-shedding, and triggers cognitive bias toward particular vendor stacks.

### 2. Preferred Agnostic Mediums
Instead of concrete source code, express technical mechanisms through:
- **Conceptual Pseudo-code**: Algorithmic step descriptions using clean, language-neutral syntax without framework imports.
- **ASCII Architectural Diagrams**: Explicit data-flow topologies, transactional boundaries, and state transitions.
- **Mermaid Diagrams**: Flowcharts, statecharts, and sequence flows illustrating invariant lifecycles.
- **Mathematical Formulations**: Complexity metrics ($O(N)$ bounds), queueing models, latency percentiles (p99/p99.9), and cost ratios.

### 3. Multi-Ecosystem Breadth (When Citing Real Tools)
When grounding abstract concepts with real-world industry examples, **never fixate on a single language or ecosystem** (specifically avoiding singular `.NET` / `C#` bias). Always present a balanced spectrum across distinct computational paradigms:
- **Systems & Bare-Metal Programming**: Manual memory management, zero-cost abstractions, static compilation.
- **Managed Enterprise Runtimes**: Garbage-collected, JIT-compiled runtimes with rich standard libraries.
- **Modern Statically Typed Languages**: Expressive type systems, structural concurrency, immutable defaults.
- **Dynamic & Distributed Environments**: Scripting runtimes, event-loop engines, distributed actor systems.
