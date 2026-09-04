---
title: Applications May Shift from Fixed Features to Agent-Extensible Primitives
tags:
  - malleable-software
  - ai-agents
  - software-architecture
  - webmcp
  - plugin-architecture
  - end-user-programming
  - generative-ui
aliases:
  - Agent-Extensible Applications
  - Malleable Software in the Agent Era
  - From Monolithic Apps to Agent Primitives
---

Historically, software development has operated under a central assumption:

> The developer must anticipate every feature, host the necessary models and data, and hardcode every user flow into the interface.

This model created the modern SaaS application:

```text
developer
    ↓
hosts database & backend
    ↓
runs domain models & AI
    ↓
designs rigid UI & buttons
    ↓
user consumes fixed feature set
```

If a user needs something outside the predefined feature set, they face a familiar dilemma: wait months for the developer to prioritize the request, build a fragile external workaround, or accept that the software cannot adapt to their life.

AI agents, protocols like MCP (Model Context Protocol) and WebMCP, and on-device machine learning suggest another architecture:

```text
application
(provides core semantic primitives, domain validation, and exposed APIs)
    +
user's personal environment
(supplies on-device models, personal data stores, and private context)
    +
personal agent
(generates custom workflows, UI widgets, and extensions on demand)
```

Applications may gradually transition from **closed feature silos** into **agent-extensible primitives**.

---

# The Problem: Bloatware vs. The Unserved Long Tail

Consider a familiar application: a mobile nutrition and calorie tracker.

Under the traditional model, the developer must:

- maintain a proprietary nutritional database;
- license or host a multimodal computer vision model to recognize food from photos;
- design menus, charts, macros, and input flows;
- continuously add new niche features requested by segments of users:
  - intermittent fasting timers,
  - ketogenic net carb calculators,
  - glycemic index estimators,
  - inflammatory ingredient warnings,
  - custom exports for personal coaches.

This creates a structural conflict:

```text
few universal features (e.g., log meal, track calories)
                     ↓
hundreds of niche, idiosyncratic requirements (the long tail)
                     ↓
app either becomes bloated with complex menus
                     OR
app ignores 80% of niche user needs
```

No single product team can design for every personal quirk, medical condition, or workflow variation.

As software attempts to cover the long tail, interfaces become crowded, development cycles slow down, and infrastructure maintenance costs balloon.

---

# The Decoupling of Models, Data, and Interfaces (BYOM and BYOD)

For years, developers had to host the machine learning models and centralize user data because consumer devices lacked the compute power and standardization to do otherwise.

That technical necessity is dissolving.

### 1. On-Device Intelligence (Bring Your Own Model)

Modern mobile processors increasingly integrate dedicated Neural Processing Units (NPUs). Small, highly capable multimodal models can execute directly on the user's phone or laptop.

When a user snaps a photo of a meal:

- the application does not need to send the image to an expensive proprietary cloud endpoint;
- the operating system or the user's local model can parse the image into semantic entities (e.g., *grilled salmon, steamed broccoli, olive oil*);
- the developer is freed from bearing the ongoing compute costs of every photo processed.

The application ceases to be an AI host and becomes a consumer of intelligence provided by the user's own device.

### 2. Personal Data Vaults (Bring Your Own Data)

Similarly, user records have historically been fragmented across dozens of cloud databases. A health app stores calories in its database; a fitness watch stores workouts in another; a grocery app stores food purchases in a third.

In a **Bring Your Own Data (BYOD)** architecture:

```text
traditional:
app A [UI + Private DB] ─── silo
app B [UI + Private DB] ─── silo
app C [UI + Private DB] ─── silo

decoupled:
app A [UI] ──┐
app B [UI] ──┼──→ [ OS / Personal Data Vault / Local Storage ]
app C [UI] ──┘
```

The application requests access to write and read from a standardized personal data layer. If the user decides to switch to a different interface tomorrow, their entire nutritional history remains intact in their personal vault.

---

# WebMCP and the Rise of Malleable Software

When applications are relieved of the need to host closed data and models, their primary purpose shifts.

An application becomes a provider of **domain-specific primitives**:

- core business logic and invariants;
- domain validation rules (e.g., what constitutes a valid nutritional entry);
- interaction protocols and live state synchronization.

To make these primitives accessible to AI, platforms are adopting semantic protocols like **MCP (Model Context Protocol)** and its browser-native counterpart, **WebMCP**.

Instead of only exposing visual buttons meant for human fingers:

```text
[ Button: Log Meal ]
[ Button: View Weekly Average ]
```

The application publishes machine-discoverable capabilities directly to the runtime:

```typescript
// Exposed WebMCP / Tool Definition
interface NutritionAppPrimitives {
  getMealHistory(range: DateRange): Promise<MealEntry[]>;
  recordMeal(entry: ValidatedMeal): Promise<Receipt>;
  calculateMetrics(formula: MetricFormula): Promise<MetricResult>;
  registerCustomView(slot: "dashboard_card" | "sidebar", widget: GenerativeWidget): void;
}
```

This transforms software from a rigid monolith into **malleable software**—software that can be reshaped at runtime by the person using it.

---

# End-User Runtime Extensibility

In a malleable system, the user is no longer a passive recipient of whatever UI the developer decided to ship.

When a user encounters a missing feature, the workflow changes:

```text
traditional workflow:
want feature
  ↓
check settings
  ↓
feature does not exist
  ↓
submit support ticket or give up

malleable workflow:
want feature
  ↓
instruct personal agent
  ↓
agent inspects application's exposed primitives (WebMCP / APIs)
  ↓
agent writes a micro-extension or generative UI component
  ↓
extension mounts inside application runtime
  ↓
custom feature is immediately usable
```

### An Example of Just-In-Time Features

Suppose a user wants to calculate the ratio of omega-3 to omega-6 fats from their meals and automatically send a weekly summary to their nutritionist's private Google Sheet.

In the old paradigm, this feature would never be built by the application creator—it is too niche to justify developer hours.

In the agent-extensible paradigm:

1. The user tells their agent: *"Track my omega-3 to omega-6 ratio on the dashboard and sync weekly reports to my coach's sheet."*
2. The user's agent discovers the application's `getMealHistory` and `registerCustomView` tools via WebMCP.
3. The agent generates a lightweight React or Web Component card displaying the ratio.
4. The agent creates a background task that connects the application's output to the external Google Sheet tool.
5. The dashboard now permanently features the custom metric.

The application provided the core domain primitives; the user's agent provided the bespoke integration.

---

# Architectural and Security Implications

Making client applications extensible by arbitrary agent-generated code introduces non-trivial architectural challenges.

### 1. Sandboxing and Execution Boundaries

If an agent can inject code into an application, how does the system prevent security catastrophes?

- **Declarative Primitives over Arbitrary Code:** Rather than executing raw JavaScript directly within privileged contexts, applications will likely expose declarative schemas (e.g., structured UI widgets, isolated iframes, or WebAssembly sandboxes).
- **Capability-Based Permissions:** The application can restrict what an injected plugin may do (e.g., *can render a chart based on read-only meal data, but cannot initiate network calls outside authorized endpoints*).

### 2. The Shift in Software Monetization

If users bring their own models, store their own data, and generate their own custom features, what does the software developer sell?

```text
old value proposition:
"Pay $10/month for our closed features, our cloud hosting, and our pre-made buttons."

emerging value proposition:
"Pay for our rock-solid domain integrity, certified data models, verified compliance, and dependable semantic primitives."
```

Developers transition from selling **rigid feature bundles** to selling **high-trust platforms and domain engines**. A medical or financial tracking app wins not because it has a pretty button for one specific calculation, but because its domain primitives are mathematically rigorous, legally compliant, and seamlessly extensible by any agent.

---

# The Long-Term Horizon

Software history can be viewed as an ongoing progression toward greater malleability:

```text
mainframes with hardwired programs
               ↓
compiled desktop software with static updates
               ↓
cloud SaaS with vendor-controlled releases
               ↓
agent-extensible malleable software with runtime personalization
```

When applications stop trying to be everything to everyone, they can become smaller, faster, and more robust.

They provide the foundational primitives of their domain, while the user's personal agent tailors the interface, logic, and integrations to the exact shape of that individual's life.
