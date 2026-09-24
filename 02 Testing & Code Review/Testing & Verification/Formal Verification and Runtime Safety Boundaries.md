---
title: Formal Verification and Runtime Safety Boundaries
tags:
  - formal-verification
  - neurosymbolic-ai
  - lean4
  - coq
  - software-testing
  - system-correctness
  - verification-oracles
aliases:
  - Formal Verification, Neurosymbolic AI, and the Negative Proof Dilemma
  - The Negative Proof Dilemma
  - Formal Proofs vs Dynamic Testing
  - Neurosymbolic Verification
  - Specification Incompleteness and Side Effects
  - The Frame Problem in Software Verification
---

# Formal Verification and Runtime Safety Boundaries

It is tempting to think we could run a theorem prover over critical code and know, with mathematical certainty, that it is safe to ship. Reasoning models can now help search for proofs in Lean 4, Coq, and Isabelle: they propose tactics, inspect failures, and try again while a proof checker decides whether the result is valid. That makes formal verification more practical to put in a CI/CD workflow.

But a proof answers the question we wrote down in the specification. If it says that a function returns the right result for a given input, it does not tell us whether the function leaks memory, ties up threads in a shared pool, runs out of file descriptors, or falls over under concurrent traffic. Those things need their own checks.

For critical code, I would pair proofs of the specified behavior with fuzzing, profiling, and measurements from a running system. The proof and the runtime checks cover different failure modes.

## What a proof covers, and what it leaves open

There are four limits to keep in view:

1. **A correct result does not imply harmless execution.** An algorithm can return exactly what the specification asks for while allocating far too much memory, making a blocking system call, or starting a background thread nobody monitors.
2. **The model leaves out much of the runtime.** Garbage collection pauses, cache misses, kernel context switches, socket buffers, and operating system state do not disappear because we left them out of a proof.
3. **A proof cannot repair a bad specification.** It establishes that code matches the formal rules. It does not establish that those rules capture the business requirement or its failure cases.
4. **The checks need to complement each other.** A theorem prover, TLA+, and type invariants can check specified logic; property-based fuzzing, memory profiling, and canary or shadow traffic can show what happens during execution.

| Check | Question it answers | Examples of what to inspect |
| :--- | :--- | :--- |
| Formal proof and static checks | Does the logic satisfy the stated rules? | Results, termination, state machine invariants |
| Runtime checks | How does the implementation behave while it runs? | Heap allocations, thread contention and deadlocks, latency under concurrency |

Passing one set of checks does not answer the other set of questions. Production readiness needs both.

## 1. Let the model search for proofs; let the kernel check them

Writing formal proofs by hand in Coq, Isabelle, or Lean has traditionally taken specialist knowledge and a great deal of time, even for a single critical module. A reasoning model can take over some of the search. When a tactic fails, it can read the proof state, backtrack, and try another route.

The important part is where the decision sits. Another LLM's approval is still a judgment from a model. A proof checker is a mechanical check: if its kernel accepts the proof, the stated claim follows under the assumptions of that formal system.

As discussed in [[Testing in the Model, Agent, LLM Era]], that clear pass signal can be misleading. An agent can write the code and obtain an accepted proof, and the team may read that as a sign that the whole feature is ready for production. The kernel checked the formal claim; it did not inspect every consequence of executing the code.

## 2. Where production behavior escapes the proof

Code runs on machines with finite memory, CPU time, sockets, and storage. Four kinds of failures are easy to miss when the model focuses on the result of a computation.

### Side effects the specification did not mention

The *frame problem* asks what must remain unchanged when an operation runs. Consider a sorting routine. We might prove that it returns the same elements in sorted order. That proof says nothing about whether it also starts a background thread that outlives the caller, reads environment variables, writes debug logs to disk, or sends telemetry through an unencrypted socket.

To rule out those actions with a proof, we would have to state the relevant boundaries and model the parts of the runtime involved. If the operating system, network, or other side effects sit outside the specification, the proof makes no claim about them.

### Memory use and execution cost

A verified algorithm can still allocate millions of short-lived objects. On a hot path, those allocations can trigger garbage collection pauses and sharp latency spikes. It can also have poor memory locality: cache misses or fragmented virtual memory may make it slower than a flat loop over an array. [[AI May Make Aggressive Code Optimization Economically Viable]] discusses that trade-off in more detail.

Even a termination proof leaves a performance question open. The function may always finish and still have hidden $O(N^2)$ behavior on the skewed inputs that actually arrive in production. We need to measure time, allocations, and memory use on representative inputs.

### Concurrency and memory ordering

Proofs often describe sequential steps or use a simplified concurrency model. A lock-free queue proven under sequential consistency can still have races or visibility bugs on a multicore machine if its barriers or acquire-release atomic operations are wrong for the hardware memory model.

The same issue appears at the service boundary. A business operation may be correct when run alone and still deadlock or produce a serialization anomaly when concurrent transactions run against PostgreSQL at its default `READ COMMITTED` isolation level. The proof has to cover the concurrency conditions we actually care about; otherwise we need to test them separately.

### A specification that misses the real requirement

The most convincing proof can be attached to the wrong specification. An agent can turn a vague request or a flawed PRD into formal rules, generate code, and prove that the code follows those rules. If the rules omit an operational edge case or misstate the business behavior, the proof will still pass.

**Code matches specification** does not necessarily mean **system matches business intent**. A green proof is useful evidence about the stated rules, not evidence that we stated every necessary rule.

## 3. Proofs and tests answer different questions

In 1969, Edsger Dijkstra wrote that testing can show the presence of bugs, but cannot show their absence. That remains a useful warning about tests. There is a matching warning for proofs: a proof can establish that specified invariants hold, but it cannot exclude runtime behavior the model never described.

| | Formal verification (Lean 4, TLA+) | Dynamic tests and fuzzing | Runtime telemetry |
| :--- | :--- | :--- | :--- |
| **Coverage** | The specified mathematical model | The inputs and execution conditions exercised | Traffic and conditions observed in production |
| **Likely findings** | Logic errors, incorrect state transitions, type mismatches | Edge-case crashes, memory corruption, panics | Races, leaks, latency spikes |
| **Runtime behavior** | Does not measure memory churn or stalls unless modeled | Can measure elapsed time and memory use | Shows contention, load, and latency in the running system |
| **Work to define checks** | Formalize the rules and assumptions | Write properties and assertions | Set up metrics, traces, and alert thresholds |
| **Tempting but unsafe conclusion** | “It is proven, so production cannot fail.” | “Ten thousand cases passed, so we found every edge case.” | “The metrics look healthy, so every future condition is covered.” |

[[Negative Knowledge and Explicit Architectural Dissents]] makes a related point: for reliable systems, we also need to state what code must *not* do. A proof of the positive requirement is valuable, but testing and telemetry help catch damage to the runtime that the formal requirement left out.

## 4. Put both kinds of checks in the agent workflow

When an agent proposes an implementation, I would check it in three stages:

1. **Check the specified behavior.** Use Lean 4 or Coq for suitable proofs, TLA+ for state machines, and static type invariants and compiler checks where they apply.
2. **Exercise and measure the implementation.** Run property-based fuzzing, track heap allocations and leaks, profile under concurrent load, and use mutation testing to check whether the test assertions catch changes they should catch.
3. **Watch it against real traffic.** Use shadow execution or a canary, correlate traces, and monitor latency and error rates before treating the change as ready.

Each stage can reject a change that passed the preceding one. The second stage checks the running implementation; the third exposes it to conditions that a test setup may have missed.

### Put an allocation budget next to a proof

If an agent submits a formally verified function on a hot path, check its allocation behavior as well. An automated test can enforce zero unexpected heap allocations or a bound on memory growth. In Go, the check might look like this:

```go
func TestVerifiedHotPathAllocations(t *testing.T) {
    input := generateStressPayload()

    allocs := testing.AllocsPerRun(1000, func() {
        output, err := ProcessVerifiedPayload(input)
        if err != nil {
            t.Fatalf("unexpected execution failure: %v", err)
        }
        _ = output
    })

    if allocs > 0 {
        t.Fatalf("Performance regression: expected 0 allocs/op, got %f", allocs)
    }
}
```

The proof checks the function's specified result. This test checks whether a change introduces heap allocations on the measured path. In Rust, leak sanitizers and heap profilers such as `jemalloc` or `dhat` can serve the same goal of checking resource use alongside a proof.

### Run the old and new paths side by side

When replacing a legacy algorithm with a formally verified implementation, send mirrored production traffic through both versions using [[Refactoring Legacy Systems with AI Agents|shadow execution]]. Compare their outputs on real inputs, including the awkward edge cases. Then compare p99 latency and CPU cycles: the verified path should be no worse than the old one. Context switches and time spent waiting on locks should remain flat too.

The new implementation can be logically correct and still make the service slower or create contention. Running the paths side by side gives us evidence on both behavior and cost.

### Let runtime measurements challenge the model

Static verification cannot predict every condition the deployed system will meet. [[Embedding LLMs in Runtime Decision Paths and Operational Telemetry|Runtime telemetry]] helps show what happens under live traffic. Distributed tracing spans and kernel-level measurements from tools such as eBPF or `perf` can expose latency and contention that the formal model did not cover.

If production measurements disagree with what we expected from the model, we need to revisit the model and its assumptions. An accepted proof does not override what the running system is doing.

## Related notes

- **[[Testing in the Model, Agent, LLM Era]]** — Deterministic test oracles and testing boundaries in agent workflows.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]** — Keeping specifications current alongside automated checks.
- **[[AI May Make Aggressive Code Optimization Economically Viable]]** — The cost of poor execution efficiency and memory locality in an otherwise correct algorithm.
- **[[Refactoring Legacy Systems with AI Agents]]** — Shadow execution and differential tests when rewriting critical code.
- **[[Embedding LLMs in Runtime Decision Paths and Operational Telemetry]]** — Tracing and runtime measurements after static checks end.
- **[[Negative Knowledge and Explicit Architectural Dissents]]** — Explicitly stating forbidden behavior and failure modes.
- **[[Software Engineering May Shift Toward Code Optimized for Agents]]** — Making architectures easier for agents and automated verifiers to inspect.
