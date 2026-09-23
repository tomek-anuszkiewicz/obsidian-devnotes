---
title: The Minimal Frame Pattern - Proving System Topology on Atomic Slices
tags:
  - ai-agents
  - software-engineering
  - agentic-workflows
  - systems-architecture
  - verification
  - prototyping
aliases:
  - The Minimal Frame Pattern
  - Minimal Frame Rule
  - Proving System Topology on Atomic Slices
  - Atomic Slice Prototyping
  - Minimal Frame vs Vertical Slice
  - Upgrade the Harness Never Touch the Code
---

# The Minimal Frame Pattern - Proving System Topology on Atomic Slices

Ask an AI coding agent to build an entire stateful subsystem from a broad specification and you may get twenty-five files that compile and pass a few simple tests. Then you run the system for longer than a test case and discover that its components do not agree on timing or ownership. A wait state advances the wrong phase, bus users contend in the wrong order, a circular reference keeps memory alive, or a lock stalls the whole loop.

The Minimal Frame is a way to settle those questions before the agent builds the rest. Pick the smallest operation that can exercise the path you care about: one instruction, one queue transition, or one handoff between two users of a resource. Make its ownership, interfaces and state transitions work. Check it against a reliable external reference. Only then ask the agent to repeat the pattern.

The sequence is: inspect the system's constraints, work through the design with the agent, prove one operation, write down and test the resulting rules, then let the agent implement related operations. When it repeats a mistake, improve those rules and run it again.

## Architectural ground rules

1. **Do not delegate the whole subsystem in one pass.** An agent asked to build a coprocessor pipeline and bus arbiter together can spread a mistaken timing assumption, a hidden circular reference or an awkward abstraction across many files before anything runs.
2. **Prove the complete path with one operation.** The operation should expose memory layout, how execution progresses without blocking, and how errors are reported. This applies to an instruction emulator, a Raft node or an off-heap event broker, although the operation differs in each case.
3. **Record the pattern before delegating more work.** Once deterministic tests pass, put the contracts, layout and transition rules in `.agents/rules/`, the repeatable implementation procedure in `.agents/skills/`, and the checks in the test suite. The agent should follow that structure when implementing the remaining operations.
4. **Fix the instruction that produced a recurring mistake.** If the agent puts a file in the wrong place or skips an endianness conversion, find the missing rule or check. Update the harness and have the agent redo the work. A manual edit to one file leaves the same mistake ready to appear in the next forty.
5. **Separate design from repetition.** The architect and agent spend time arguing through one representative operation. Once that operation is verified, the agent can implement its siblings under the established tests.

## 1. Why a whole-subsystem prompt breaks down

For a business application, you can often give an agent a vertical slice: take an HTTP request through a service and ORM into a database table (see [[Developing Features with AI Coding Agents]]). The boundaries are familiar, and an error in one endpoint is comparatively contained.

A cycle-exact simulator, trading kernel, storage engine or embedded OS kernel gives the agent less room to guess. Every component depends on details that the others must get right. An underspecified prompt can produce code that compiles while hiding circular pointer handles, allocations in the execution loop, inconsistent clock phases, and events that arrive in the wrong order. Simple unit tests may miss all of them; sustained execution exposes the deadlock or the performance collapse.

Consider a memory wait state. The processor must pause the relevant instruction step without losing track of the clock. Functional units have to communicate without circular handles or locks in a hot loop. A pipeline also needs an explicit answer for a branch misprediction or an asynchronous interrupt. If those decisions are made independently in twenty files, untangling the result can take days. Start with one operation that crosses the necessary boundaries and make those decisions there.

## 2. What the Minimal Frame contains

A Minimal Frame is a small operation carried through the complete execution path. It might be an arithmetic instruction, a queue transition or a packet handshake. Small refers to the **amount of behavior implemented**, not to the number of design questions you leave unanswered.

For a clocked execution engine, follow the operation through its phases, resource arbitration and wait states, state capture and restoration, and status-flag updates. You can then ask concrete questions before multiplying the implementation:

- Can functional units communicate without circular references?
- Does the hot path avoid dynamic allocations?
- Does the timing state machine move correctly across clock sub-phases?
- Can you serialize and restore the complete state at any clock edge?

Keep the example easy to inspect: no custom macros that conceal control flow, clear ownership of files and state, and contiguous arrays where fragmented heap objects would obscure the layout. The point is to expose the path the remaining operations will follow.

## 3. Work through one frame in five stages

### Stage 1: Explore the constraints

Read the specifications, hardware manuals and protocol documentation before writing the operation. For a hardware-oriented system, map timing, memory layout, bus priorities, endianness and exception vectors. The agent can use local retrieval over the reference manuals and AST dependency graphs to find relevant material (see [[Retrieval-Augmented Generation and Context Architecture]]). These facts define what the design has to preserve.

### Stage 2: Debate the boundaries

Use the agent as a design partner, then challenge the proposed ownership and dispatch. Why put dynamic dispatch in an execution path if a static match table fits the operation? Why pass references between subsystems if one machine loop can decide who owns the bus? Check especially for shared mutable state, circular references and locks that would sit in the runtime path.

An agent might start with trait objects stored in a vector and a bus behind `Arc<Mutex<MemoryBus>>`:

```rust
// The agent's first instinct: Trait objects and heap allocation
pub trait Instruction {
    fn execute(&self, state: &mut SystemState) -> Result<Cycles, CpuError>;
}

pub struct Cpu {
    pipeline: Vec<Box<dyn Instruction>>, // Heap fragmentation, pointer indirection
    bus: Arc<Mutex<MemoryBus>>,          // Locking overhead on the hot path
}
```

That shape introduces pointer indirection and a runtime lock where the execution loop needs predictable progress. The alternative in this note keeps register state in an array and represents the current phase explicitly:

```rust
// The corrected topology: Contiguous memory, static dispatch, explicit phase progression
#[repr(C)]
pub struct Cpu {
    pub registers: [u32; 16],
    pub pc: u32,
    pub cycle_accumulator: u64,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq)]
pub enum MicroStep {
    Fetch,
    Decode,
    Execute,
    BusWait(u8),
    Writeback,
}

pub struct ExecutionFrame {
    pub step: MicroStep,
    pub opcode: u16,
    pub operand_a: u32,
    pub operand_b: u32,
}
```

This is a starting layout for the frame. It makes the phase and the state needed by that phase visible in one place.

### Stage 3: Prove the operation

Implement one primitive and compare its behavior with verified external captures or hardware test vectors. For the addition example, check fetching, phase changes, operands, status flags and cycles. The intended frame also needs to account for memory operands and bus waits when those are part of the operation.

```rust
impl Cpu {
    /// Step a single clock phase of the minimal frame (e.g., ADD register-to-register).
    /// Returns true when the instruction retires.
    #[inline(always)]
    pub fn step_add_primitive(&mut self, frame: &mut ExecutionFrame, bus: &mut [u8]) -> bool {
        match frame.step {
            MicroStep::Fetch => {
                // Read 16-bit opcode from memory using PC
                let addr = self.pc as usize;
                frame.opcode = u16::from_le_bytes([bus[addr], bus[addr + 1]]);
                self.pc += 2;
                frame.step = MicroStep::Decode;
                false
            }
            MicroStep::Decode => {
                let reg_a = (frame.opcode & 0x00F0) >> 4;
                let reg_b = frame.opcode & 0x000F;
                frame.operand_a = self.registers[reg_a as usize];
                frame.operand_b = self.registers[reg_b as usize];
                frame.step = MicroStep::Execute;
                false
            }
            MicroStep::Execute => {
                let (result, overflow) = frame.operand_a.overflowing_add(frame.operand_b);
                let dest = ((frame.opcode & 0x0F00) >> 8) as usize;
                self.registers[dest] = result;
                
                // Update condition flags: Zero, Negative, Carry/Overflow
                self.update_flags(result, overflow);
                
                frame.step = MicroStep::Writeback;
                false
            }
            MicroStep::Writeback => {
                // Instruction complete. Reset frame for next fetch.
                frame.step = MicroStep::Fetch;
                self.cycle_accumulator += 1;
                true
            }
            MicroStep::BusWait(_) => unreachable!("ALU add does not stall on memory bus"),
        }
    }

    #[inline(always)]
    fn update_flags(&mut self, result: u32, overflow: bool) {
        // Condition flag packing without heap overhead
    }
}
```

The sketch shows how a frame can advance from fetch through decode, execution and writeback. It is an illustration of the structure, not the validation itself: the tests must still establish cycle counts, flag behavior, memory access and any required bus wait. The execution path should stay free of heap allocation, and its state should remain inspectable at each step.

### Stage 4: Put the rules in the harness

After the frame passes its reference tests, record the structure in `.agents/rules/` and the implementation procedure in `.agents/skills/`. The note proposes a flat source layout with operation categories in files such as `src/ops/alu.rs` and `src/ops/branch.rs`. It also calls for inlining leaf ALU routines, keeping cold exception traps out of the hot instruction path, and banning dynamic allocations and unchecked panics in execution methods.

Automate what you can verify, including file size and forbidden calls. That gives the agent a specific pattern to follow and a test failure when it breaks one of its boundaries.

### Stage 5: Expand under the same checks

Now the agent can write the next fifty arithmetic or logical operations using the established phase layout. Each one still has to pass the relevant reference tests and architectural checks. The difficult design work happened on the first representative operation; the remaining work applies and verifies that decision repeatedly. When a new edge case exposes a gap, return to the rules and tests before continuing.

## 4. Minimal Frames and enterprise vertical slices

Both approaches cut down the amount of work you ask an agent to handle at once. They cut in different directions:

| Question | Enterprise vertical slice | Minimal operational frame |
| :--- | :--- | :--- |
| Where is it useful? | CRUD APIs, web services and business SaaS. | Simulation engines, performance-sensitive kernels and state machines. |
| What does one slice cross? | Application layers: HTTP → service → ORM → database. | Execution steps: clock phase → resource arbitration → state commit. |
| What can go wrong? | Business logic or API contracts do not line up. | Memory contention, pipeline stalls, circular handles or state that falls out of sync. |
| What verifies the work? | Unit tests with mocks and database fixtures. | External captures and hardware execution vectors. |
| What does it produce? | DTOs, controllers and database migrations. | Explicit phase machines, contiguous buffers and cycle-aware bus behavior. |

A vertical slice checks that a business operation works across application layers. A Minimal Frame checks that a small operation behaves correctly over time and across the resources it uses.

## 5. Upgrade the harness when the agent slips

During the repeated implementation phase, resist fixing the agent's code by hand. Suppose it writes an awkward helper, puts an operation in the wrong file or misses an endianness conversion. Correcting those lines solves the immediate case, but the next generated operation still has no reason to avoid the mistake.

Trace the error to a rule that was missing or too vague. Add a naming or file rule, a linter check, a reference test, or a validation step in `.agents/skills/`. Then ask the agent to run the task again with the updated constraint. This is how one failure improves the procedure used for the rest of the subsystem.

The note's example adds architectural checks alongside ordinary tests. One rejects `.unwrap()` and `panic!` in `src/ops`; another rejects operation files above 800 lines:

```rust
// tests/architecture_invariants.rs
use std::fs;
use std::path::Path;

#[test]
fn test_no_unwrap_or_panic_in_execution_path() {
    let ops_dir = Path::new("src/ops");
    for entry in fs::read_dir(ops_dir).unwrap() {
        let entry = entry.unwrap();
        let path = entry.path();
        if path.extension().and_then(|s| s.to_str()) == Some("rs") {
            let content = fs::read_to_string(&path).unwrap();
            
            // Forbid unchecked unwrap operations in hot execution code
            assert!(
                !content.contains(".unwrap()"),
                "File {:?} contains .unwrap()! Use explicit pattern matching or bubble errors.",
                path.file_name().unwrap()
            );
            
            // Forbid direct panic triggers
            assert!(
                !content.contains("panic!("),
                "File {:?} contains panic!()! Execution operations must return deterministic error states.",
                path.file_name().unwrap()
            );
        }
    }
}

#[test]
fn test_single_file_line_limits() {
    let ops_dir = Path::new("src/ops");
    for entry in fs::read_dir(ops_dir).unwrap() {
        let entry = entry.unwrap();
        let path = entry.path();
        if path.extension().and_then(|s| s.to_str()) == Some("rs") {
            let line_count = fs::read_to_string(&path).unwrap().lines().count();
            assert!(
                line_count <= 800,
                "File {:?} has {} lines. Operations must be split into flat, focused files (< 800 lines).",
                path.file_name().unwrap(),
                line_count
            );
        }
    }
}
```

These checks cover the specific patterns shown in the example. They do not themselves detect an allocation regression or prove that an instruction is correct; those still need their own checks. Their job is to keep a known mistake from returning as the agent adds more files.

## 6. Putting the pattern to work

First use the agent to explore constraints and make one complete operation work. Once that frame is verified against the system's real behavior, write its boundaries and checks into the harness. Then let the agent implement related operations under those same constraints. If the work exposes a missing case, improve the harness and repeat the affected work. That keeps architectural decisions in the small, inspectable frame while allowing the implementation to grow.

### Related notes

- **[[Developing Features with AI Coding Agents]]**: Vertical slices in business software and how they compare with minimal operational frames.
- **[[How AI Changes Prototyping and the Path from PoC to Production]]**: Disposable probes for proving a frame without keeping prototype debt.
- **[[The Conductor Pattern for High-Bandwidth Engineering]]**: The architect's role in setting constraints and challenging the agent's design.
- **[[Testing in the Model, Agent, LLM Era]]**: External reference tests for real system behavior.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: The rules and checks that keep repeated agent work within boundaries.
- **[[In-Flight Documentation as the Primary Framework for Coding Agents]]**: Recording specifications while proving the frame.
