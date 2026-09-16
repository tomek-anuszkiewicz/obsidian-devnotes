---
title: Explore — Ideas, Research Backlog, and Tools
tags:
  - inbox
  - ideas
  - backlog
  - tools
  - scratchpad
  - experiments
aliases:
  - Explore & Ideas
  - Research Backlog
---

# The 5-Layer System Stack & The 7 Canonical Hubs

The vault's knowledge graph is structured across **The 5-Layer System Stack for Agentic Software Engineering**, anchored by **7 Canonical Hub Notes (Single Sources of Truth)**:

* **Preamble & Empirical Scope**: [[Preamble]]
* **Charter**: [[The 5-Layer System Stack for Agentic Software Engineering]]

| Layer | Focus Domain | Canonical Hub Note | Core Architectural Mission |
| :--- | :--- | :--- | :--- |
| **Layer 1** | Architecture & Code | [[Optimizing Software Engineering and Code for Agents]] | Instruction cache density, 1:1 operation isolation, flat dispatch over dynamic OOP |
| **Layer 2** | Testing & Code Review | [[Agentic Coding Harness and Controlled Development Workflows]]<br>[[Testing in the Model, Agent, LLM Era]] | Deterministic test oracles, controlled state machines, runtime safety boundaries |
| **Layer 3** | Systems & Infrastructure | [[Embedding LLMs in Runtime Decision Paths and Operational Telemetry]] | Conversational telemetry, OpenTelemetry spans, autonomous canary probes |
| **Layer 4** | Prompts, Context & Models | [[Retrieval-Augmented Generation and Context Architecture]] | Context window compaction, hybrid retrieval, token budget management |
| **Layer 5** | Engineering Economics & Future | [[Developer Satisfaction, Identity, and Burnout in the Age of Coding Agents]]<br>[[Competitive Advantage in the Age of Commodity AI]] | The invariant director, deliberate coaching, software commoditization & moats |

---

# remote control
## control with voice
general - use voice to control my pc, or only vsc, dictation would be also good, 

### text2speech
i think i saw tools that you are talking and at the end whole text is structurized and formatted
wisprflow
superwhisper
my llm, mcp, app
can give voice commands to pc

browser automation and control
browser use
### Open Claw & Local Autonomous Agent Infrastructure
- Architectural Reference: [[Always-On Autonomous Agents - The 24-7 Local Operating System]]
- Hardware & TCO Foundations: [[Local vs Cloud and Hybrid Model Execution]]
- Inference Router & Gateway: [[Dynamic Model Routing and Inference Gateways]]
- Hosting locally in Docker or on dedicated UMA appliance (NVIDIA DGX Spark, Mac Studio, AMD Strix Halo)
- Connecting via local OpenAI-compatible endpoint (LiteLLM Proxy, vLLM, Ollama) or hybrid cloud fallback
- Daily workflows:
  - Curated news & intelligence feeds with positive/negative preference learning (see [[Finding Original Knowledge in an Internet Full of Repetition]])
  - Autonomous email triage, task extraction, and contextual draft generation
  - Private smart home orchestration and autonomous deal surveillance


Perplexity
CodeRabbit

rate limiting
retry, circuit breaker, polly
cqrs, read model, orchestrated command, single responsibility command, maybe we don't need services
dotnet aspire
kafka

https://github.com/github/awesome-copilot?utm_source=chatgpt.com
https://github.com/ai-boost/awesome-harness-engineering
https://github.com/VoltAgent/awesome-agent-skills
https://github.com/microsoft/azure-skills

app idea:
- olx buy/sell and earn
- expand it globally

app idea:
- very universal data exploration / drilling app, maybe with AI help to write customized queries
- with many connectors
- idea: first-level payments list, where I can zoom into a payment and see structured UI, but also zoom in to view raw logs, database objects, or zoom into a user to see user card. On the user view, show the list of payments—fractal navigation pattern.

app idea:
- manga / anime browser
  
Exercises:
- build a modern MCP server and use it from VS Code or local OpenAI, Gemini, Claude, etc.
- n8n / LangGraph + LangSmith / Flowise
- leverage the above for bidirectional Slack automation (e.g. exposing action links or interactive buttons inside Slack)
- [https://github.com/mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill)

mcp server / client / stateless / alternatives / skills / command line / discovery / using them across ChatGPT, Claude, and local copilot / execution flow when local and remote inference are combined

leetcode
C# technical interview review
design patterns
system design

https://www.aihero.dev/skills-wayfinder
additional tooling and resources from the repository

Automated Web Scraping and Doc Extraction:
- given an arbitrary web page, generate its documentation
- run automated code analysis to detect hidden buttons and UI elements (including client-side JS, not just static HTML)
- propose and apply updates to documentation
- run automated verification passes against generated documentation

Agent Harness:
- decision logs to trace and understand agent execution paths
- multi-workflow orchestration where processes run concurrently and influence each other

Process:
- agent implements code
- pull request review on GitHub
- peer review comments from specialized subagents
- automated remediation of feedback
- consensus reached: approval and merge
- conflict resolution / escalation when consensus is not reached
  
cloud agents

webmcp