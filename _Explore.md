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

* **Charter**: [[The 5-Layer System Stack for Agentic Software Engineering]]

| Layer | Focus Domain | Canonical Hub Note | Core Epistemological Mission |
| :--- | :--- | :--- | :--- |
| **Layer 1** | Substrate & Mechanical Sympathy | [[Software Engineering May Shift Toward Code Optimized for Agents]] | L1i cache density, 1:1 operation isolation, flat dispatch over dynamic OOP |
| **Layer 2** | Harness, Governance & Verification | [[Agentic Coding Harness and Controlled Development Workflows]]<br>[[Testing in the Model, Agent, LLM Era]] | Deterministic test oracles, controlled state machines, negative proof dilemma |
| **Layer 3** | Runtime Mesh & Observability | [[Embedding LLMs in Runtime Decision Paths and Operational Telemetry]] | Conversational telemetry, OpenTelemetry spans, autonomous canary probes |
| **Layer 4** | Model Cognition & Latent Space | [[Retrieval-Augmented Generation and Context Architecture]] | Context window compaction, hybrid retrieval, solution space bounding |
| **Layer 5** | Operator Psychology & Macro-Economics | [[Developer Satisfaction, Identity, and Burnout in the Age of Coding Agents]]<br>[[Competitive advantage in the age of commodity AI]] | The invariant director, deliberate coaching, software commoditization & moats |

---

# remote control
## control with voice
general -  use voice to control my pc, or only vsc, dictastion would be also good, 

### text2speach
i think i saw tools that you are talking and at the end whole text is structurized and formatted
wisprflow
superwhisper
my llm, mcp, app
can give voice commands to pc

sterowanie przegladarka 
browser use
### Open Claw Start
I need to host it or run locally in docker
But in general I need to connect it llm, directly or using open router

use llm to prepare news feed - filter our fakes, duplicates, keep only important news

On youtube there are planty video explaining how to use it in daily churns
- explore news and create my personal news feed
- assisst with my emails
- assists with work search

Perplexity
CodeRabbit

rate limiting
retry, circuit breaker, polly
cqrs, read model, orchastrated command, single resposibility commanfd, maybe we don't need services
dotnet aspire
kafka

verify,snapshoter

write instruction about techniques agent should you to write more performant code
- in / out/ ref
- class vs record
- span
- nolinq
- unrolling loops
- zero memory allocation
- others
- static lambda 
- regex
- optimal logs
- explicit specialized code instead of offline codegen/macros (The Death of the Code Generator) -> [[AI May Replace Some Source Generators with Explicit Generated Code]]

write doc about general guidlines
- define whether null is allowed in json
- other
- Software Entropy & The "Zero-Friction" Trap: mechanical isolation (1:1 file hierarchy, hard line limits like 800 lines, constrained touchpoints), agent refactoring vs human hacks, duplication as blast-radius protection, and the training paradox -> [[Software Entropy and the Zero-Friction Trap]]
- Emergence & Latent Space Synthesis: how targeted practitioner prompts act as crystallization seeds in the model's latent manifold -> [[Emergence, Latent Space Synthesis, and How Targeted Prompts Crystallize Insight]]
- Training models on corporate data lakes: Jira, Slack, meeting recordings, code archaeology, Conway's law, and the corporate decay prior -> [[LLM Agents and Institutional Memory]]
- Competitive advantage when code generation is cheap: leadership of questions vs tasks, forcing LLMs outside the Averaged Prior -> [[Competitive advantage in the age of commodity AI]]
- The Cognitive Inversion of the Engineer: from "overthinker" to epistemic catalyst, death of sunk-cost design meetings (asynchronous agentic RFCs & counter-prototyping), and overcoming developer cynicism -> [[AI Changes the Role and Training of Software Engineers]]
- The "Zero-Line Developer" Paradox: why building complex low-level systems without writing code demands deeper engineering mastery, the abstraction asymmetry between non-experts and engineers, and the barrier of unknown unknowns -> [[AI Changes the Role and Training of Software Engineers]]
- The Legacy Dilemma: maintaining with agents (complexity masking trap) vs automated straightening (automated strangler fig rewrite) -> [[Refactoring Legacy Systems with AI Agents]]
- Meta-Harnessing and Pattern Drift: how next-gen models will automate their own harnesses, rules, and subagent topologies -> [[Agentic Coding Harness and Controlled Development Workflows]]
- Agent-First APIs & The Pretraining Bottleneck: why API authors must ship native MCP servers and executable Agent Skills (`SKILL.md`) instead of human-only Swagger docs -> [[Designing APIs for LLM-Generated Integration Code]]
- Model Collapse vs. Verifiable Drift: how unverified synthetic code degrades neural networks (autophagous loop) and why deterministic verification gates (compilation, tests, mutation testing) are the only filter for evolutionary progress -> [[Agentic Coding Harness and Controlled Development Workflows]]
- WebMCP & In-Browser Agent Tools: turning websites into zero-cost APIs via `navigator.modelContext`, revolutionizing E2E testability, and empowering personal cross-site agent orchestration -> [[WebMCP - Turning Web Applications into Agent-Native Toolkits]]
- Unified Personal AI Subscriptions & Managed RAG: the convergence of consumer chat subscriptions, ambient personal cloud indexing (Drive/Gmail/Photos as zero-config RAG), and portable BYOB (Bring Your Own Brain) API keys powering third-party applications -> [[Personal AI Subscriptions May Unify Model Access, Managed RAG, and Portable APIs]]
- Vault-to-Vault Epistemic Diffing: how personal AI models will ingest external knowledge bases to filter repetition, extract novel insights, and highlight architectural contradictions for dialectical sparring -> [[How Personal AI Models Will Diff, Reconcile, and Challenge External Knowledge]]
- When Software Can Be Cloned in a Week: the death of the implementation moat via automated scraping and agentic cloning, and where defensibility shifts (state, distribution, real-world friction, iteration velocity) -> [[Software Itself Is No Longer a Moat When It Can Be Cloned in a Week]]
- LLMs in Runtime Decision Paths: embedding models into live production execution pipelines, conversational telemetry (eliminating the "dashboard stare" in Grafana), real-time security log triage, and consuming qualitative non-numeric business data -> [[Embedding LLMs in Runtime Decision Paths and Operational Telemetry]]
- Developer Satisfaction, Identity, and Burnout: the psychological transition from tactile coding to relentless cognitive vigilance, the asymmetric empathy trap ("one-way empathy" and the oblivious machine), the crisis of the syntactic craftsman, and new forms of vigilance burnout -> [[Developer Satisfaction, Identity, and Burnout in the Age of Coding Agents]]
- In-Flight Documentation as the Primary Framework: generating documentation concurrently during code creation, shifting scaffolding from code frameworks to documentation templates, imparting determinism to stochastic agent edits, and slashing token overhead -> [[In-Flight Documentation as the Primary Framework for Coding Agents]]
- Constraint Saturation & Rule Oscillation: the whack-a-mole trap when accumulating too many guidelines/drivers, attention fragmentation in transformers, hierarchical constraint tiering, dynamic rule scoping, and harness circuit breakers -> [[Constraint Saturation and Rule Oscillation in Coding Agents]]

rest api, graphql, grpc

how to organize topics for qeueu messages sub/pub
on per message type 
other alternatives

https://github.com/github/awesome-copilot?utm_source=chatgpt.com
https://github.com/ai-boost/awesome-harness-engineering
https://github.com/VoltAgent/awesome-agent-skills
https://github.com/microsoft/azure-skills

https://medium.com/@signadot/why-staging-doesnt-scale-for-microservice-testing-98892b936c38
czesc szerszego problemu jak wdrozyc sie na staging, przetestowac swoja zmiane i niczego nie rozwalic
also: env by branch
telepresence
feature test
run localla, test in cloud
https://www.signadot.com/

mini complete app
- system to simulte how to process credit card transactiisn
- grafana / kibana 
- azure insight
- sidecars - log http requests, gather output logs
- pulumi
- aks
- graphify
- durable function workflow
- some agentic workflow - bugs, problems, private data leaks in logs
- front - react, fully responsive for backend changes  - events be => fe, (sse, push, signalr)
	- making concurrent changes in data
- test
- agentic tests = must be run by agents
- modules - feature per folder, 
- create some docs
- use graphify, github nexus for code graph
- grafana alerts
- alerts base on trends
- system altetowania i eskalacji - jak w allegro
- front poc - create front dynamically base on user promp - front per user
- e2e tests - frontend tests, playright, use ai to fix broken tests, use ai to run broken test, find button to click with llm
- how to deploy  canary, revert
- multi reviewers
- agentic workflow for development
- aks, k8s - app service to observe and basic operations
- update nugets, frameworks, dotnet, dockers, tools, etc
	- investigate what's changes, what's break, what's new 
	- propose code changes
- istio, envoy
- open telemetry
- polly - retry, cicuit breaker
- graphql
- oauth
- pipelines
- deply to k8s
- try to use some task board, and use agent is the loop as often as possible

app idea:
- olx buy/sell and earn
- expand it globally

app idea:
- very universal drilling app, maybe with ai help to wrote customized queries
- with many connectors
- idea: first level payments list, i can zoom to payment, see some structured ui for payment, but i can zoom in to see raw logs, db objects, can zoom to user, and see user card. On the other hand on user i can see list of payments, so it is more like fractal, 

app idea:
- manga / anime browser
  
 Exercises
- build modern mcp server and use it from vsc or local openai, gemini, cloude etc
- use sql mcp data api builder, check if i can talk with model about database, or use this knowledge in agent workflow
- n8n / LangGraph + LangSmith / Flowise
- wykorzystanie powyzszego do sterowania slackiem jak i w druga strone (na slacku mozna np wystawic zbior linkow albo przyciskow)
- [https://github.com/mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill)

mcp server / client / stateless / alternatives / skills / commands line / how to discover  how use them in chatgpt / claude / local copilot / how flow is working when local is mixed with remote inference

leetcode
powtorka z c# pytan
wzorce projektowe
system design

https://www.aihero.dev/skills-wayfinder
i inne tam sa ciekawe rzeczy

majac jakas strone zrobic jej dokumnetacje,
zlecic analize kodu by wykryc ukryte przyciski etc, tez kodu js, nie tylko html
zrobic zmiane w dokumentacji
nakazac weryfikacje dokumentacji

agent harness
- log decyzyjny by zrozumiec jak dziala
- kilka workflowow pracujact wspolnie i nawzajem na siebie wplywajacych

process:
- agent koduje
- review na github
- inni agenvi komentuja
- ktos poprawia
- decyzja ze jest ok 
- brak konsensusu
  
cloud agents

webmcp