---
title: Tests Are for Verification, Not Architectural Navigation
tags:
  - testing
  - software-architecture
  - ai-agents
  - verification
  - knowledge-management
  - system-maintenance
aliases:
  - Why Tests Are Insufficient for System Maintenance
  - Tests as Verification Oracles vs Navigation Maps
  - The Limits of Tests in Agentic Software Maintenance
  - Verification vs Navigation in Software Evolution
---

# Tests Are for Verification, Not Architectural Navigation

> [!IMPORTANT]
> Tests check whether code behaves as expected. They do not tell an agent where to put a change, which component owns the data, or which boundaries the change must respect. A thorough test suite can make it relatively easy to rewrite a module behind a stable interface. Maintaining a larger system also requires a way to understand its architecture before changing it.

The workflow has three parts: architectural documentation helps the agent find the right place for a change and understand the boundaries; the agent makes the change; tests check the resulting behavior.

## What tests can tell an agent

Developers sometimes say that clean code and comprehensive unit tests document themselves. That may help when you are working inside a small, familiar module. It is not enough when an agent has to change a production system it does not know.

Before editing, the agent needs to understand which service owns a table, how requests and asynchronous events move between components, where shared utilities belong, and which layers must not depend on each other. After editing, it needs to check that the change satisfies its functional contract and does not break existing behavior. These are different jobs.

Tests are good at the second job. A failed assertion points to behavior that did not match an expectation. It does not explain whether the agent put business logic in the wrong layer or broke domain encapsulation to get a passing result.

## Why a rewrite is easier than ongoing maintenance

If you build a new module or replace an old subsystem behind a stable interface, a comprehensive test suite gives the agent a clear target (see [[Testing in the Model, Agent, LLM Era|disposable code rewrites]]). It can work from the interface and the expected results, discard an implementation that does not work, and keep iterating until the tests pass. It does not need to reconstruct twenty years of organizational history to do that contained job.

The mistake is to carry that conclusion over to everyday maintenance. When tests are the only guide, four problems appear.

### 1. All tests pass while the architecture gets worse

A test can check that `calculate_tax(order)` returns `15.50`. It may say nothing about how the code reached that value.

An agent could import `db_session` into an API controller and read another bounded context's private table instead of going through the domain repository. It could copy pricing rules into an HTTP handler because that is quicker than finding the shared pricing service. Or it could make a blocking HTTP request while a database transaction is open. An in-memory test may pass, while the production request holds row locks longer and exhausts the connection pool under load.

Unit tests often isolate a function and check its return value or mocked side effects. They can stay green through all of these changes while the system becomes harder to maintain (see [[AI Changes the Economics of Technical Debt]]).

### 2. Existing tests do not locate a new feature

Much of maintenance means adding behavior that does not exist yet. Existing tests protect the old behavior, but they do not say which module should own new state, whether a new step should emit an asynchronous domain event or make a synchronous RPC, or where validation rules belong.

You can write tests for the new feature once you have decided what to build. Those tests still do not make the architectural decision for you. Without documentation, the agent has to guess before it starts editing.

### 3. Trial and error costs time and context

Without an architectural guide, the agent may guess a file, make a change, run tests, read failures and stack traces, then guess again. Repeated runs consume tokens and fill the working context with failed diffs and diagnostic output (see [[How LLM Systems Build Context]]).

A short Operation Card or C4 component map can tell the agent where to start, which files matter, and which boundaries to keep intact. A 30-line card can save that exploration and improve the chance that the first change lands in the right place (see [[AI-Generated Architectural Documentation from Code]]).

### 4. Mocks hide production behavior

Unit tests often replace a payment gateway, message broker, or transactional database with `unittest.mock`, `jest.fn()`, or an in-memory SQLite database. They may turn eventual consistency into an immediate call and remove network timeouts, connection resets, temporary 503 responses, and races between services.

If an agent sees only those tests, it can assume a network call always succeeds immediately. It may omit retries or idempotency keys, or miss the need for a transactional outbox, exponential backoff, and a dead-letter queue. The tests describe the controlled test environment; they do not, by themselves, describe all the failure conditions in production.

## Use documentation before the change and tests after it

Teams need both an architectural description and automated checks. They answer different questions:

| | Architectural documentation | Automated tests |
| :--- | :--- | :--- |
| **Main job** | Show where code belongs and which boundaries to respect | Check behavior and catch regressions |
| **When the agent uses it** | Before changing code, while locating and planning the work | After changing code, while validating it |
| **What it records** | Why components exist, where responsibilities live, and who owns them | Which results particular inputs and actions should produce |
| **What can go wrong** | It becomes outdated if it does not change with the code | Tests pass even though structural boundaries have been broken |
| **How it helps the agent** | Helps it make the first change in the right place | Catches logic mistakes before the change reaches production |

Documentation can guide an agent toward the right implementation. Tests can reject an implementation whose behavior is wrong. Neither replaces the other.

## Rules for a team using coding agents

1. **Document ownership and boundaries alongside the code.** Keep concise Operation Cards for modules: who owns the data, which public entry points to use, what downstream dependencies exist, and which imports are forbidden (see [[In-Flight Documentation as the Primary Framework for Coding Agents]]).
2. **Review the shape of the change as well as the test results.** In an agent's pull request, check the files it touched, its imports, and how it accesses the database. Passing CI does not show that the change respects the architecture.
3. **Test behavior through public contracts.** Use tests to verify what the system does, rather than tying tests to private helper functions in an attempt to explain where code belongs.
4. **Make architectural boundaries executable where possible.** Use dependency checks such as `import-linter`, ArchUnit, or ESLint boundary plugins in CI. They can fail a build when a change crosses a forbidden layer or bypasses a service to query a database directly; ordinary runtime unit tests are not a reliable way to catch that violation.

## Related notes

- **[[Testing in the Model, Agent, LLM Era]]**: Disposable implementations and the Frozen Oracle Rule.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Writing architectural guides while building the code they describe.
- **[[AI-Generated Architectural Documentation from Code]]**: Extracting system models and Operation Cards from existing code.
- **[[AI Changes the Economics of Technical Debt]]**: How hidden coupling slows down agents even when tests pass.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: Combining architectural guidance with automated CI checks.
- **[[How LLM Systems Build Context]]**: Managing the agent's working context during a change.
