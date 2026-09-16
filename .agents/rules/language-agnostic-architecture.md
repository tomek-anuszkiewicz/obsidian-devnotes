---
trigger: always_on
description: Enforce language-agnostic abstractions, ubiquitous engineering concepts, avoidance of concrete source code snippets, and multi-ecosystem breadth across notes.
---

# Language-Agnostic Architecture & Generalized Technology Abstractions Rule

Whenever creating, updating, or refactoring architectural notes and documentation in this Obsidian vault, the agent must treat software architecture as **language-agnostic**, **concept-driven**, and **grounded in universal abstractions**.

---

## Core Requirements & Operating Principles

1. **Operate on Universal Abstractions**:
   - Frame systems around ubiquitous software engineering concepts rather than platform-specific implementations:
     - Use **databases** (relational, document, key-value) instead of specific database engines.
     - Use **cloud platforms** or **compute providers** instead of vendor-specific branding.
     - Use **services**, **application runtimes**, and **service meshes** instead of framework-bound servers.
     - Use **persistence layers** or **Object-Relational Mappers (ORMs)** instead of *Entity Framework* or *Hibernate*.
     - Use **object mapping utilities** or **declarative transformers** instead of *AutoMapper* or *MapStruct*.
     - Use **serialization / deserialization pipelines** instead of *Serde* or *Newtonsoft.Json*.
     - Use **compile-time metaprogramming** or **compiler-integrated code generators** instead of *Roslyn source generators*.
     - Use **mutation testing harnesses** instead of *Stryker.NET*.
   - Treat systems as composable data flows, state machines, transactional boundaries, memory hierarchies, and messaging topologies.

2. **Avoid Concrete Language-Specific Source Code Snippets**:
   - Unless a note is explicitly dedicated to a low-level systems analysis where exact compiler output or byte layout is the core subject, **avoid presenting concrete source code snippets in specific languages (such as C#, Java, Python, Go, Rust, or C++)**.
   - Instead of language-specific implementation code, prefer:
     - **Conceptual pseudo-code** or **algorithmic step descriptions**.
     - **ASCII architectural diagrams** and **data-flow schemas**.
     - **Mermaid flowcharts / statecharts**.
     - **Mathematical formulations** (e.g., complexity metrics, cost models, latency envelopes).
   - If code is unavoidable, keep it strictly agnostic pseudo-code without language-specific syntax or library imports.

3. **Multi-Ecosystem Breadth (When Concrete Tools Must Be Cited)**:
   - When grounding an abstract concept with real-world examples, **never fixate on a single language or ecosystem** (especially avoiding `.NET` / `C#` bias).
   - Always present a balanced spectrum across distinct language paradigms:
     - Systems programming (manual memory / static compilation).
     - Managed garbage-collected enterprise runtimes.
     - Modern statically typed ecosystems.
     - Dynamic and distributed runtimes.
