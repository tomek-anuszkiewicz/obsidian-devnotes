---
title: Model Access and Execution Infrastructure
tags:
  - infrastructure
  - cloud
  - llm
  - ai-agents
  - latency
  - cost-management
  - security
aliases:
  - LLM Infrastructure Architecture
  - Model Gateway and Execution Setup
---

Modern AI systems increasingly separate the **agent or application** from the **model that performs a given task**.

A useful way to think about this ecosystem is to distinguish several layers: enterprise AI platforms, model gateways, inference providers, and local model runtimes.

## Enterprise AI platforms

Platforms such as:

- Microsoft Foundry
    
- AWS Bedrock
    
- Google Vertex AI
    

provide much more than simple access to an LLM.

They typically combine:

- model catalogs,
    
- model deployment and inference,
    
- identity and access management,
    
- monitoring and observability,
    
- evaluations,
    
- guardrails,
    
- RAG and knowledge integration,
    
- prompt management,
    
- agent orchestration,
    
- governance and enterprise security.
    

Their role is similar to a cloud platform for AI applications.

An organization may therefore avoid integrating separately with every model provider. Instead, applications interact with an internal AI platform, while the platform decides which available models and services are used underneath.

Conceptually:

```text
AI application / agent
        ↓
Enterprise AI platform
 ├─ models
 ├─ agents
 ├─ RAG
 ├─ evaluation
 ├─ security
 ├─ observability
 └─ governance
        ↓
GPT / Claude / Gemini / Llama / Qwen / ...
```

The model becomes one resource among many managed by the platform.

## Model gateways and brokers

OpenRouter represents a somewhat different class of solution.

Its main abstraction is:

> one API in front of many models and model providers.

Instead of integrating directly with OpenAI, Anthropic, Google, Mistral, DeepSeek, and multiple inference providers, an application can integrate with a single gateway.

Conceptually:

```text
Application
    ↓
Model gateway
    ↓
 ┌──────────┬──────────┬─────────┐
 OpenAI   Anthropic   Google   others
```

A gateway can provide additional infrastructure features such as:

- provider selection,
    
- model aliases,
    
- automatic routing,
    
- fallbacks,
    
- retries,
    
- cost control,
    
- usage accounting,
    
- latency-aware routing,
    
- availability routing.
    

This introduces an important architectural possibility: the application does not necessarily need to know which provider actually executes the request.

For example:

```text
simple classification
    → cheap, fast model

code generation
    → coding-specialized model

architecture analysis
    → strong reasoning model

provider unavailable
    → fallback provider

sensitive workload
    → private deployment
```

The gateway becomes an abstraction layer over model execution.

Other systems, such as LiteLLM, can play a similar role, especially when organizations want to operate such a gateway themselves.

## Local model runtimes

Ollama belongs primarily to another category.

Its basic purpose is:

> run models on infrastructure controlled by the user.

Conceptually:

```text
Application
    ↓
Ollama API
    ↓
Local model
    ↓
CPU / GPU
```

This can be useful for:

- development,
    
- experimentation,
    
- privacy-sensitive workloads,
    
- offline operation,
    
- predictable infrastructure,
    
- avoiding external API dependencies,
    
- running smaller specialized models very cheaply once hardware already exists.
    

Related technologies include:

- vLLM,
    
- llama.cpp,
    
- LM Studio,
    
- Hugging Face TGI,
    
- NVIDIA NIM.
    

They differ substantially in production readiness and intended use, but they share the idea that model inference can be operated independently from the original model creator.

## Dedicated inference providers

There is also an important layer between local execution and large enterprise platforms.

Examples include providers such as:

- Together AI,
    
- Fireworks AI,
    
- Groq,
    
- Cerebras,
    
- Replicate,
    
- Hugging Face Inference Endpoints.
    

Their proposition is approximately:

> use open or third-party models without operating the GPU infrastructure yourself.

The same model may therefore be available through several execution paths:

```text
                   Llama / Qwen
                       │
          ┌────────────┼─────────────┐
          ↓            ↓             ↓
       Ollama       Fireworks      Together
      local GPU     cloud GPU      cloud GPU
```

A model gateway can then sit another layer above these providers.

```text
Application
     ↓
Model gateway
     ↓
 ┌────────┬──────────┬──────────┐
 Groq   Together   Fireworks   ...
     ↓
   Models
```

## A useful mental model

The ecosystem can therefore be represented approximately as:

```text
                       AI APPLICATION / AGENT
                                │
                     ┌──────────▼──────────┐
                     │ ENTERPRISE AI       │
                     │ PLATFORM            │
                     │ Foundry / Bedrock   │
                     │ Vertex AI           │
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │ MODEL GATEWAY       │
                     │ OpenRouter          │
                     │ LiteLLM             │
                     └──────────┬──────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
       MODEL PROVIDER      INFERENCE CLOUD      LOCAL
       OpenAI              Together             Ollama
       Anthropic           Fireworks            vLLM
       Google              Groq                 llama.cpp
              │                 │                 │
              └─────────────────┼─────────────────┘
                                ↓
                              MODEL
```

The boundaries are not strict.

For example, Bedrock combines elements of an enterprise AI platform, model gateway, and inference provider. Ollama increasingly supports both local and remote models. OpenRouter is also expanding beyond simple API aggregation into routing and infrastructure features.

The categories are therefore better understood as **architectural roles** rather than mutually exclusive product categories.

## Models as execution resources

The most interesting consequence is that an agent may stop being permanently associated with one model.

Instead, the model can become an execution resource selected dynamically for each step.

For example:

```text
Agent workflow

1. classify issue
   → small cheap model

2. inspect repository
   → coding model

3. reason about architecture
   → strong reasoning model

4. generate implementation
   → coding-specialized model

5. perform security review
   → independent reviewer model

6. summarize pull request
   → cheap model
```

The same task can also be executed by several models:

```text
Claude
GPT
Gemini
Qwen
   ↓
compare answers
   ↓
judge / rank
   ↓
select result
```

This creates an important separation:

```text
agent logic
≠
model
≠
model provider
≠
execution infrastructure
```

The agent defines the workflow.

The model provides intelligence for an individual step.

The provider exposes the model.

The inference infrastructure determines where and how the computation actually happens.

## Implication for agent architectures

This becomes especially important as agents gain longer-running workflows.

A coding agent, research agent, support agent, or operational agent may use many different models during a single execution.

Its architecture may therefore look more like:

```text
Agent runtime
    │
    ├─ tools
    ├─ memory
    ├─ skills
    ├─ context
    ├─ MCP / APIs
    └─ model router
            │
            ├─ local model
            ├─ cheap cloud model
            ├─ strong reasoning model
            ├─ coding model
            └─ specialist model
```

In such a system, model selection itself can become part of the agent's reasoning.

The agent may decide:

- how difficult the current problem is,
    
- how much money it is worth spending,
    
- whether data may leave the organization,
    
- whether latency matters,
    
- whether several independent opinions are useful,
    
- whether a local model is sufficient,
    
- whether another model should verify the result.
    

This suggests that systems such as Foundry, Bedrock, OpenRouter, Ollama, and dedicated inference clouds are not merely different ways of accessing an LLM.

Together they form an emerging **model execution infrastructure**.

In much the same way that cloud platforms and container orchestration abstracted where traditional software executes, this infrastructure may increasingly abstract where and by which model a unit of cognitive work is executed.
---

## Relationship to the Knowledge Graph

- **[[Agent Deployment and Execution Models]]**: The operational runtime topologies for hosting and scaling agent execution.
- **[[Exploring Agent Harnesses]]**: Evaluating CLI-based, cloud-hosted, and headless harness environments.
- **[[Agentic Coding Harness and Controlled Development Workflows]]**: The state-machine orchestration layer running on top of model execution infrastructure.
- **[[Introduction to Workflow Orchestration]]**: Managing long-running durable processes and agent retry policies across model providers.
- **[[Multi-Agent Software Development]]**: Routing tasks across heterogeneous frontier and specialized local models.
