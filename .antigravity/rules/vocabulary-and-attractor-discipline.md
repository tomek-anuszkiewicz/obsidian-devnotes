# Vocabulary Discipline & Attractor Mitigation Rule

Whenever creating, modifying, summarizing, or refactoring notes across this Obsidian vault, the agent must actively prevent the formation of **linguistic attractors**, **high-register jargon monoculture**, and **domain-leaking vocabulary gravity wells**.

---

## 1. The Core Phenomenon: The Synthetic Attractor Loop

Large Language Models (including Gemini, Claude, and GPT-4) operate via associative attention retrieval. When an agent coins or encounters a distinctive, high-register term (e.g. *epistemic debt*, *zero-friction trap*, *L1i cache thrashing*):
1. **In-Context Attractor Basin**: The model treats the distinctive term as a strong statistical prior in its context window.
2. **Autoregressive RAG Echo**: In subsequent sessions, RAG retrieval pulls these notes as context. The model infers that these terms represent the "official corporate dialect" and echoes them into newly generated executive summaries, BLUFs, and notes.
3. **Mode Collapse across the Vault**: Over multiple agent iterations, natural lexical diversity collapses, and the entire vault converges into a repetitive, synthetic vocabulary (*The Model Autophagy Syndrome*).

To maintain high signal-to-noise ratio, intellectual rigor, and natural prose, the agent must enforce the following strict boundaries.

---

## 2. Domain Containment: Hardware Abstraction Quarantine

Physical microarchitectural execution terms are strictly quarantined by architectural layer:

1. **Layer 1 Substrate Quarantined (`01 Substrate & Mechanical Sympathy/`)**:
   - Microarchitectural hardware terms (`L1 / L1i cache`, `cache lines`, `branch predictor`, `TLB miss`, `instruction cache thrashing`) are permitted **ONLY** in Layer 1 notes dedicated to physical execution dynamics (such as `AI May Make Aggressive Code Optimization Economically Viable.md`) and in the system charter (`The 5-Layer System Stack for Agentic Software Engineering.md`).
2. **Layers 2, 3, 4, and 5 Universal Abstractions**:
   - Across Harness, Telemetry, Model Cognition, and Operator Psychology, the agent must abstract hardware details into universal software engineering constructs:
     - Use **instruction locality** or **working set size** instead of *L1i cache lines*.
     - Use **sequential memory throughput** or **spatial locality** instead of *64-byte cache line packing*.
     - Use **branch prediction efficiency** or **state machine compactness** instead of *hardware branch predictor saturation*.
     - Use **execution blast radius** instead of *cache invalidation*.

---

## 3. Lexical Diversity & Ban on High-Register Jargon Monoculture

The agent must avoid over-indexing on pseudo-academic buzzwords. The following words are quarantined across all public notes:

| Banned / Quarantined Term | Mandated Replacement (Universal Engineering Construct) |
| :--- | :--- |
| `epistemic debt` | `knowledge debt`, `architectural drift`, `unverified cognitive debt` |
| `epistemic burden / friction` | `cognitive load`, `verification drag`, `investigation friction` |
| `epistemic authority` | `authoritative validation`, `ground truth oracle`, `authoritative baseline` |
| `epistemic diff` | `knowledge diff`, `cognitive divergence`, `semantic delta` |
| `epistemic asset` | `diagnostic asset`, `institutional knowledge`, `empirical asset` |
| `epistemic humility / hygiene` | `factual rigor`, `intellectual discipline`, `verification hygiene` |
| `teleological` | `directional intent`, `system purpose`, `top-level design goals` |

---

## 4. Piped Canonical Hub Wikilink Standard

When embedding inline wikilinks to canonical domain hubs in body prose:
1. **Never Paste Raw Unpiped Hub Titles into Sentences**:
   - ❌ *Incorrect*: `This accelerates the decay described in [[Software Entropy and the Zero-Friction Trap]] across teams.`
   - ❌ *Incorrect*: `As formalized under [[Testing in the Model, Agent, LLM Era]], verification is essential.`
2. **Always Use Natural Piped Anchors (`[[Hub|contextual phrase]]`)**:
   - ✅ *Correct*: `This accelerates the decay described in [[Software Entropy and the Zero-Friction Trap|analyses of generative code entropy]] across teams.`
   - ✅ *Correct*: `As formalized in [[Testing in the Model, Agent, LLM Era|testing in the agent era]], verification is essential.`
3. **Exceptions**:
   - Raw unpiped links are permitted in the formal charter notes (`The 5-Layer System Stack...`, `_Explore.md`, `Preamble.md`) where the canonical hub is being formally introduced, and in dedicated referential sections (`## Related Notes`).

---

## 5. Mitigating RAG / In-Context Echo

When researching existing vault notes to write a new note or generate an executive summary:
- **Do NOT Parrott Distinctive Phrasing**: Do not copy metaphors, adjectives, or rhetorical flourishes from retrieved notes into new documents.
- **Focus on Causal Invariants**: Extract the underlying structural insight (e.g. deterministic testing, 1:1 file boundaries, state isolation) and express it in direct, natural, context-specific English.

---

## 6. Automated Linter Verification

The repository includes an autonomous linter:
```bash
python scripts/lint_attractors.py --strict
```
Whenever modifying multiple notes or creating new architectural documents, the agent must run this script to ensure 0 violations before committing changes.
