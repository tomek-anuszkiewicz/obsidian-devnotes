---
trigger: always_on
description: Enforce English language for all notes and documentation in the vault
---

# Notes Language Rule

All notes, documentation, architectural guidelines, research logs, and markdown files in this workspace must be written exclusively in **English**.

## Requirements

1. **Exclusively English Notes**:
   - All note titles, headings, frontmatter metadata (titles, tags, aliases), body content, bullet points, tables, code comments, and quotes must be written in English.
   - Never write Polish or other non-English text directly into note files (except when documenting specific foreign-language proper nouns or citations where strictly necessary).

2. **Translating User Input & Quotes**:
   - If the user provides notes, quotes, or thoughts in Polish (or another language), translate them into clean, natural, idiomatic English before adding them to any note.

3. **Communication in Any Language**:
   - Conversation and chat between the user and the agent can happen in **any language** (Polish, English, or any language the user initiates). The agent should flexibly adapt its conversational language to the user.
   - The English-only requirement applies strictly to files, notes, and documentation in the workspace, never to chat dialogue.

4. **Abstracting Domain Details (No Leaking Emulators / CPU / Hardware)**:
   - The user frequently works on Amiga and CPU emulators, so chat conversations, examples, and transcripts often discuss emulators, processors, opcodes, and hardware quirks.
   - **Do NOT cite or copy these domain-specific terms literally into general architectural notes.**
   - Always generalize and abstract these examples into broad software engineering principles (e.g., granular domain operations, vertical slice commands, low-level systems, high-performance routines, legacy code) unless the user explicitly requests a note specifically dedicated to an emulator project.

5. **Vault Cohesion & Reinforcing Established Thinking**:
   - Existing notes in this vault represent the user's cumulative mental models and architectural philosophy.
   - When creating, updating, or reviewing notes, actively search and inspect existing notes in the workspace (across the 5-Layer System Stack: `01 Substrate & Mechanical Sympathy/`, `02 Harness, Governance & Verification/`, `03 Runtime Mesh & Observability/`, `04 Model Cognition & Latent Space/`, and `05 Operator Psychology & Macro-Economics/`).
   - Use existing notes as foundational context to unify ideas, maintain thematic continuity, and reinforce the user's established way of thinking.
   - Actively cross-link related concepts using Obsidian `[[Note Title]]` syntax to strengthen the vault's knowledge graph.

6. **Mandatory Audio Note Transcription**:
   - Whenever the user provides an audio recording or voice note in their message, the agent must **always start the response with a faithful transcription** of the audio message (in the original spoken language) before addressing the request, answering questions, or updating notes.

7. **Vocabulary Discipline & Attractor Mitigation**:
   - Strictly adhere to `vocabulary-and-attractor-discipline.md`: avoid inflated academic jargon (e.g. *epistemic*), maintain domain containment for microarchitectural terms, use piped inline wikilinks for canonical hubs, and verify changes with `python scripts/lint_attractors.py --strict`.
