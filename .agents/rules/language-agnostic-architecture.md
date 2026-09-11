---
trigger: always_on
description: Enforce language-agnostic abstractions, ubiquitous engineering concepts, and multi-ecosystem examples instead of anchoring architectural notes to specific programming languages.
---

# Language-Agnostic Architecture & Generalized Technology Abstractions Rule

Whenever creating, updating, or refactoring architectural notes and documentation in this Obsidian vault, the agent must treat software architecture as **language-agnostic** and **concept-driven**.

---

## Core Requirements & Operating Principles

1. **Language-Agnostic Conceptual Framing**:
   - **Do not unnecessarily anchor general architectural principles to specific programming languages** (such as C#, C++, Rust, Go, Java, Python, or TypeScript).
   - Focus on universal software engineering paradigms, data flows, and runtime dynamics (e.g., state machines, transactional boundaries, serialization pipelines, memory layouts, AST transformations, declarative generation).
   - **Single-Language Exception**: Reference a specific language *only* when the architectural concept is fundamentally inherent to or unique to that specific language runtime or specification (e.g., Rust's affine types and borrow checker semantics, Go's M:N runtime goroutine scheduler, JVM class-loading verifiers, CLR tiered compilation).

2. **Ubiquitous Functional Terminology Over Proprietary Tool Brands**:
   - Use generalized, concept-level descriptions instead of single-ecosystem tools or proprietary library names:
     - Instead of *AutoMapper* $\rightarrow$ use **object mapping utilities** or **declarative model transformers**.
     - Instead of *Entity Framework* or *Hibernate* $\rightarrow$ use **persistence layers** or **Object-Relational Mappers (ORMs)**.
     - Instead of *Serde* or *Newtonsoft.Json* $\rightarrow$ use **serialization and deserialization pipelines**.
     - Instead of *Roslyn source generators* $\rightarrow$ use **compile-time metaprogramming** or **compiler-integrated code generators**.
   - Frame mechanisms by what they solve mathematically and architecturally, recognizing that nearly every major language ecosystem implements these patterns under different names.

3. **Multi-Ecosystem Breadth (When Concrete Tools Are Cited)**:
   - When concrete examples are necessary to ground an abstract concept, **never fixate on a single language or stack**.
   - Present a diverse, cross-cutting spectrum of examples across different language paradigms (e.g., systems programming with manual memory management, managed garbage-collected enterprise runtimes, modern statically typed ecosystems, dynamic runtimes).

4. **Avoid Language-Specific Code Snippets in Architectural Notes**:
   - Minimize or avoid language-specific implementation code snippets in high-level architectural notes.
   - Prefer:
     - **Conceptual pseudo-code** or **algorithmic descriptions**.
     - **ASCII architectural diagrams** and **data-flow schemas**.
     - **Mermaid flowcharts / statecharts**.
     - **Mathematical formulations** (e.g., complexity metrics, cost models, latency boundaries).
   - Reserve language-specific code strictly for low-level mechanical sympathy notes where compiler output, memory layout alignment, or explicit ISA execution dynamics are the exact subject being analyzed.
