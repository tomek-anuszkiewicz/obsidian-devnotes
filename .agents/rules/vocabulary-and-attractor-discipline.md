# Vocabulary Discipline & Attractor Mitigation Rule

Whenever creating, modifying, summarizing, or refactoring notes across this Obsidian vault, the agent must actively prevent the formation of **linguistic attractors**, **pseudo-academic jargon**, and **hardware domain leaks**.

This rule provides the **enforceable lexical blacklist and linter contract** that complements the narrative standard defined in [`practitioner-voice-and-tone.md`](file:///d:/GoogleDrive/AI/Obsidian/Default/.agents/rules/practitioner-voice-and-tone.md).

---

## 1. Domain Containment: Hardware Abstraction Quarantine

Physical microarchitectural execution terms are strictly quarantined by architectural layer:

1. **Layer 1 Only (`01 Code Architecture & Hardware Execution/`)**:
   - Microarchitectural hardware terms (`L1 / L1i cache`, `cache lines`, `branch predictor`, `TLB miss`, `instruction cache thrashing`) are permitted **ONLY** in Layer 1 notes dedicated to physical execution dynamics and in the system charters.
2. **Layers 2, 3, 4, and 5 Universal Abstractions**:
   - Across Harness, Telemetry, Model Cognition, and Human Ergonomics, abstract hardware details into universal software constructs:
     - Use **instruction locality** or **working set size** instead of *L1i cache lines*.
     - Use **sequential memory throughput** or **spatial locality** instead of *64-byte cache line packing*.
     - Use **branch prediction efficiency** or **state machine compactness** instead of *hardware branch predictor saturation*.
     - Use **execution blast radius** instead of *cache invalidation*.

---

## 2. "Mechanical Sympathy" & Synthetic Mutant Attractor Ban

1. **`mechanical sympathy` Strict Layer Quarantine**:
   - Permitted **ONLY** in Layer 1 (`01 Code Architecture & Hardware Execution/`) and root system charters.
   - Strictly forbidden anywhere in Layers 2, 3, 4, and 5.
   - Must **NEVER** appear in any Markdown section heading (`#`, `##`, `###`) across any layer.
2. **Absolute Ban on `* sympathy` / `* empathy` Mutants**:
   - The terms `hardware sympathy`, `hardware-sympathetic`, `hardware empathy`, `hardware-empathetic`, `substrate sympathy`, `engine sympathy`, `cache sympathy`, and `execution sympathy` are **strictly prohibited** across all notes, tags, and headings.
   - Use **hardware-aligned**, **hardware reality**, **cache-conscious layout**, or **engine optimization**.

---

## 3. Quarantined Jargon & Banned Attractor Table

The following high-register and pseudo-academic terms are quarantined across all public notes:

| Banned / Quarantined Term | Mandated Replacement (Universal Engineering Construct) |
| :--- | :--- |
| `hardware sympathy / -sympathetic` | `hardware reality`, `hardware-aligned`, `direct hardware execution`, `low-level execution efficiency` |
| `hardware empathy / -empathetic` | `hardware-aligned code`, `cache-efficient layout`, `hardware-conscious implementation` |
| `substrate / engine / cache sympathy` | `direct engine alignment`, `engine efficiency`, `cache locality` |
| `substrate` | `hardware`, `CPU & memory`, `database engine`, `runtime environment`, `cloud platform`, `execution platform` |
| `epistemic debt` | `knowledge debt`, `architectural drift`, `unverified cognitive debt` |
| `epistemic burden / friction` | `cognitive load`, `verification drag`, `investigation friction` |
| `epistemic authority` | `authoritative validation`, `ground truth oracle`, `authoritative baseline` |
| `epistemic diff` | `knowledge diff`, `cognitive divergence`, `semantic delta` |
| `epistemic asset` | `diagnostic asset`, `institutional knowledge`, `empirical asset` |
| `epistemic humility / hygiene` | `factual rigor`, `intellectual discipline`, `verification hygiene` |
| `teleological` | `directional intent`, `system purpose`, `top-level design goals` |
| `bikeshedding / bikeshed` | `petty style debates`, `cosmetic nitpicking`, `superficial style arguments` |
| `friction boundary / boundaries` | `friction point`, `clash point`, `roadblock` |

---

## 4. Piped Canonical Hub Wikilink Standard

When embedding inline wikilinks to canonical domain hubs in body prose:
1. **Never Paste Raw Unpiped Hub Titles into Sentences**:
   - ❌ *Incorrect*: `This accelerates the decay described in [[Software Entropy and the Zero-Friction Trap]] across teams.`
2. **Always Use Natural Piped Anchors (`[[Hub|natural phrase]]`)**:
   - ✅ *Correct*: `This accelerates the decay described in [[Software Entropy and the Zero-Friction Trap|analyses of generative code entropy]] across teams.`
3. **Exceptions**:
   - Raw unpiped links are permitted only in formal root charters (`_Explore.md`, `Preamble.md`) and dedicated referential sections (`## Related Notes`).

---

## 5. Automated Linter Verification

All rules in this document are enforced via the autonomous repository linter:
```bash
python scripts/lint_attractors.py --strict
```
Always verify 0 violations before committing changes.
