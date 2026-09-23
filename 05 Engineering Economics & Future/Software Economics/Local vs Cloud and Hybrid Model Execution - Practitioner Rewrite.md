---
title: Local vs Cloud and Hybrid Model Execution
tags:
  - hardware-architecture
  - software-economics
  - local-models
  - unified-memory
  - tco
  - data-sovereignty
  - agentic-engineering
aliases:
  - Local vs Cloud Model Execution
  - Desktop AI Appliances
  - Inference Economics and Hardware Tiers
  - UMA vs dGPU for Agentic Engineering
  - The Excavator vs The Shovel
---

# Local vs Cloud and Hybrid Model Execution

> [!IMPORTANT]
> **Use local and cloud models for different jobs.** A compact machine with unified memory can run frequent background work: indexing a repository, applying AST transformations, checking code, and keeping a personal agent running around the clock. A frontier cloud model is a better fit for difficult architectural decisions, changes spanning several repositories, and ambiguous problems that need stronger reasoning or a very large context window.
>
> Systems such as Apple Silicon, NVIDIA DGX Spark, and AMD Strix Halo make it possible to run large models, including 70B-class models, on a quiet desktop machine with much more memory available to the GPU than on a typical 24 GB consumer card. That gives you another option besides a hot, noisy multi-GPU workstation. It also lets you keep sensitive data and routine execution under your own control.

| | Local machine with unified memory | Frontier cloud API |
| :--- | :--- | :--- |
| Running cost | No charge per token; electricity and hardware still cost money | Charge per token or usage tier |
| Data | Can stay on a machine disconnected from external services | Crosses the provider's trust boundary |
| Tool calls | Local IPC can take less than a millisecond | Network round trips in the note's 150–400 ms range |
| Execution | You control the model version and its behavior | Provider changes, outages, limits, and refusals can affect a workflow |
| Capacity | Quiet operation around 100–150 W in the compact systems discussed here | Large multi-GPU clusters and much greater parallel capacity |
| Typical work | Continuous indexing and RAG; background agents; AST edits, formatting, lint and test fixes; handling sensitive telemetry and personal data | Architecture across subsystems; difficult refactors and edge cases; very large, million-token-class inputs |

## 1. The shovel and the excavator: how the workflow changes

Using a model only through a browser chat is like digging a foundation with a hand shovel. You copy code into the chat, wait for the response, paste it back, format the result, and repeat. Usage tiers and rate limits can interrupt the work. The interaction is occasional and manual.

A local machine connected to the shell, file watchers, background processes, and build tools can keep working while you do something else. It can inspect files without uploading them, run agents around the clock, maintain a repository index, and triage email or telemetry. Those capabilities change both how often you can use an agent and how much work you can hand it.

There is another benefit to running this yourself: you learn what actually limits the system. You see what happens when memory bandwidth becomes the bottleneck, how quantization affects model size and quality, how many requests an inference server can handle, and where tool calls slow an agent down. A browser chat hides most of those details. The analogy is the early engineers who learned networking and Unix by running their own servers: hands-on experience with the machinery built intuition they could later use on larger systems.

## 2. Heat, noise, and power matter at a desk

Peak FLOPS and synthetic benchmarks do not tell you what it is like to leave a machine running next to you all day. Power draw, heat, fan noise, and size affect whether a background agent can realistically run overnight in a home office.

| | Workstation with two consumer GPUs, such as RTX 4090s | Compact unified-memory machine, such as a Mac Studio or DGX Spark |
| :--- | :--- | :--- |
| Peak power in the note's comparison | 700–900 W; a dedicated 1,200 W or larger PSU | 100–150 W; compact power supply |
| Heat | Roughly 800 W under heavy load; the note estimates a 4–6°C rise in a closed room | Much less heat at the desk; warm chassis and slower or passive cooling |
| Noise | 45–55 dB from GPU and case fans | Under 25 dB in the note's comparison |
| Electricity when used continuously | Estimated $35–$60 a month | Estimated $4–$8 a month |
| Size | Full tower, over 25 kg | Small desktop, approximately 150 × 150 × 50 mm and 1.2–3 kg |

An 800 W workstation releases that power as heat into the room. In warm weather, a long-running agent can mean running air conditioning as well. The fans also make it harder to work beside the machine for hours. A compact unified-memory system is easier to leave under a desk for background indexing, agent jobs, and repeated test-fix cycles.

## 3. Four kinds of hardware for local models

The amount of memory available to a model is only part of the decision. Memory bandwidth, software support, power, and the work you want to run matter too.

| Tier | Examples | Memory and bandwidth in the note | Main trade-off |
| :--- | :--- | :--- | :--- |
| Consumer discrete GPU | RTX 3090, 4090, 5090 | 16–24 GB per card; roughly 1,000 GB/s on a high-end card | Fast CUDA execution, but a hard limit on VRAM per card |
| Apple unified memory | Mac Studio, Mac Pro | 64–192 GB; 400–800 GB/s | Large memory pool at low power; no native CUDA |
| Compact edge system | NVIDIA DGX Spark, AMD Strix Halo | Up to 128 GB LPDDR5X; around 270–300 GB/s in the comparison | Desktop-sized systems with different software stacks |
| Datacenter accelerator | H100, H200, B200; AMD Instinct MI300X | 80–192 GB HBM per card, with bandwidth above 3,350 GB/s in the examples | High cost, power, cooling, and operational demands |

### Tier 1: consumer GPUs

A conventional x86 workstation connects its GPUs through PCIe. A card such as the RTX 4090 offers about 1,008 GB/s of memory bandwidth, and CUDA support makes it straightforward to use runtimes such as `vLLM`, `TensorRT-LLM`, and `PyTorch`. When a model fits in VRAM, the first token arrives quickly and generation is fast.

The 24 GB VRAM limit is the problem for larger models. A 70B model does not fit on one such card even at 4-bit quantization. Splitting it across cards adds communication over PCIe, uses more power, and puts more heat into the room.

### Tier 2: Apple Silicon

On Apple Silicon, the CPU, GPU, and Neural Engine share one LPDDR5 memory pool. The note describes Ultra configurations with up to 192 GB and 800 GB/s of bandwidth. That is enough room for 70B models and quantized 120B-plus models without building a multi-GPU desktop.

The software constraint is CUDA. Apple systems use Metal, `MLX`, and `llama.cpp`. Research projects with custom Triton kernels or distributed inference frameworks may need substantial changes when they have no Metal implementation.

### Tier 3: compact edge systems

**NVIDIA DGX Spark** combines a 20-core ARM CPU and a Blackwell GPU in the GB10 Grace Blackwell chip. It has 128 GB of coherent LPDDR5X memory and a power envelope around 140 W. Its attraction is the native NVIDIA stack: DGX OS, CUDA, NIM, and TensorRT-LLM. Work developed on the desktop can use the same software stack in a datacenter. A 200 Gbps ConnectX-7 network interface also lets two units work together on models described here as large as 405B without relying on ordinary desktop networking.

**AMD Strix Halo (Ryzen AI Max+)** combines Zen 5 CPU cores, RDNA 3.5 graphics, and an XDNA 2 NPU on an x86 machine. It supports up to 128 GB of unified LPDDR5X memory at roughly 270 GB/s. The same computer can handle normal development work and local inference with ROCm acceleration.

### Tier 4: datacenter systems

Servers with H100, H200, B200, or MI300X accelerators use large HBM pools and high-bandwidth links such as NVLink. The note puts memory at 80–192 GB per card, bandwidth above 3,350 GB/s, and hardware cost at $30,000–$100,000 or more per card. These installations can draw kilowatts, need three-phase power, demanding cooling, and dedicated operations staff. They make sense for large training runs, serving many requests at once, or regulated environments with strict infrastructure requirements.

## 4. Why connecting desktop machines does not make one big GPU

It is tempting to join several inexpensive mini-PCs and split a large model among them. The connection between machines is much slower than the memory connection inside one machine.

| Connection | Bandwidth and latency quoted in the note |
| :--- | :--- |
| On-chip coherent unified memory | 300–800 GB/s; under 50 ns |
| Ordinary Ethernet or USB4 at 10–40 Gbps | About 1.2–5 GB/s; roughly 0.5–5 ms |

With **pipeline parallelism**, one machine processes an early group of layers and passes intermediate activations to the next. While the second machine runs its layers, the first can be idle. Each transfer crosses the network. With **tensor parallelism**, machines split work inside a layer and have to synchronize at every transformer layer. Both approaches make the interconnect part of the critical path.

A 10 GbE or USB4 link offers roughly 1.25–4 GB/s for these transfers in the note's comparison, against hundreds of GB/s within a unified-memory system. The note illustrates the possible effect as a drop from 25 tokens per second to 2–4 tokens per second. The exact speed depends on the model and setup, but the mechanism is the same: more compute nodes do not help if they spend their time exchanging data or waiting.

A fast RDMA connection changes the calculation. DGX Spark's 200 Gbps ConnectX-7 interface can move data between two units with much lower overhead by avoiding the normal network stack. That makes the two-machine setup described above more practical than joining ordinary desktops over consumer links.

## 5. When local hardware pays for itself

A local system has an upfront price, electricity costs, maintenance, and a limited useful life. An API avoids the hardware purchase and infrastructure work, but each agent step consumes paid usage and the provider can change its service.

| | Local unified-memory system | Cloud API |
| :--- | :--- | :--- |
| Initial hardware | $3,000–$4,700 in the note's comparison | No local hardware purchase |
| Monthly running expense | Electricity estimated at $5–$10, plus your maintenance time | Variable usage, illustrated as $50–$300 per month |
| Upkeep | OS, drivers, inference server | Provider runs the infrastructure; your workflow still depends on its API |
| Longer-term constraint | Hardware depreciation over two to three years | Token charges, service changes, and model deprecations |
| Extra tokens | No per-token bill after buying the hardware | Each additional step can add cost |

### The break-even point depends on how often agents run

For 10–30 interactive coding prompts a day, the cloud is cheaper in the example. At $30–$60 of API usage per month, it would take 6–10 years of token savings to recover the price of a $4,500 local machine. That is longer than the hardware's expected useful life.

Continuous agents change the volume. A process that watches repositories, summarizes new issues, reads execution logs, and repeatedly runs lint and tests can consume 15–50 million tokens a month. The note estimates $300–$1,000 or more per month at frontier API rates for that workload. On a local machine it estimates about $6 a month in electricity to process 50 million tokens, after the hardware purchase. At sustained volumes of that kind, it estimates a six- to twelve-month payback. These are workload-dependent estimates, not a universal price comparison.

### Software improvements can keep the same hardware useful longer

A fixed memory pool does not necessarily mean a fixed class of models and context sizes forever. The note points to four ways inference software or model design can make better use of it:

1. **BitNet 1.58b:** Weights restricted to $\{-1, 0, 1\}$ allow additions in place of some expensive floating-point multiplication. The example gives a 70B BitNet model a memory footprint of about 15–18 GB rather than 35–70 GB, bringing larger models within reach of machines with 64 or 128 GB.
2. **Sparse mixture of experts:** Models such as DeepSeek-V3 and R1 hold many parameters in memory but use only some for each token. The example activates 37B of 671B parameters per pass. A large unified-memory pool can hold the model while each token needs only part of its compute.
3. **4-bit KV cache and context eviction:** Reducing cache precision can cut the memory used by long conversations by as much as 75% in the note's example. That can make a 64k-plus-token context fit without running out of memory.
4. **Speculative decoding:** A small 1B–3B draft model proposes tokens that a larger 70B model checks. The note describes a possible two- to threefold generation speedup on the same hardware without lowering output quality.

## 6. Keeping data and execution under your control

Cost is only one reason to run a model locally. The location of source code, internal schemas, postmortems, telemetry, and agent state matters too.

### Keep the operational context on your side

In a hosted service, the vendor owns the platform where your work runs. With local agents, the repository, data, and execution history can stay inside your security boundary, while the model is a component you can replace. You can switch checkpoints or choose to send a particular task to an external API without moving the entire working context to a provider.

### Avoid unexpected changes to unattended work

A provider can update a model, change its system instructions or backend, retire an API, or suspend an account. A pipeline that passed integration tests in January could behave differently in March after a model change. A false positive in an account safety system or a service outage could stop background jobs with little warning.

Keeping a specific checkpoint locally gives you control over which model version runs. That gives you a stable model version for reproducing earlier runs and removes one source of unannounced provider change.

### Refusals can interrupt technical jobs

Cloud safety filters may reject legitimate engineering inputs: vulnerability dumps, suspicious binaries, attack payloads, or logs that contain offensive user text. An agent running low-level commands such as `rm -rf`, changing `iptables`, or editing partition tables may also trigger a refusal and stop an unattended workflow.

The note also describes **abliterated local models**, whose refusal-related directions in the weights have been altered. Such models can be used for security analysis, reverse engineering, and systems administration without the provider's refusal layer interrupting the work. This gives the operator more control over those workflows.

## 7. Put the two execution paths together

A task router can send frequent, sensitive, and repeatable work to a local unified-memory machine. That includes background agents, repository indexing and RAG, AST edits, linting, and reviews of proprietary code. It can send a difficult multi-subsystem design question, a complex refactor, ambiguous debugging, or a million-token-class input to a frontier cloud model.

The routing decision follows the task. Continuous local work avoids a per-token charge and keeps selected data close to the tools that use it. Cloud calls remain available when the task needs more reasoning capacity or context than the local model can provide.

## Related Notes

- [[Agent Deployment and Execution Models]]: Separating model inference, agent orchestration, and the environment where tools run.
- [[Agentic Coding Harness and Controlled Development Workflows]]: Boundaries and safeguards for autonomous local execution.
- [[Competitive Advantage in the Age of Commodity AI]]: The value of operational data and feedback loops when models are interchangeable.
- [[Finding Original Knowledge in an Internet Full of Repetition]]: Filtering repeated synthetic material from an agent's source pipeline.
- [[The Most Valuable Software Training Data May Be Private]]: Private traces, incident reports, and git history as specialized engineering data.
- [[The 5-Layer System Stack for Agentic Software Engineering]]: Hardware, inference servers, agent controls, and developer interfaces.
