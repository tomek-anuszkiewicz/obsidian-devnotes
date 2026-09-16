# Notes Language Rule

All notes, documentation, architectural guidelines, research logs, and markdown files in this workspace must be written exclusively in **English**.

## Requirements

1. **Exclusively English Notes**:
   - All note titles, headings, frontmatter metadata (titles, tags, aliases), body content, bullet points, tables, code comments, and quotes must be written in English.
   - Never write Polish or other non-English text directly into note files (except when documenting specific foreign-language proper nouns or citations where strictly necessary).

2. **User Input Translation & Spoken Audio Handling**:
   - **Spoken Audio Notes**: Whenever the user submits an audio recording or voice note, the agent must always start its response with a faithful transcription of the spoken audio in the original spoken language (e.g. Polish) per [`audio-transcription.md`](file:///d:/GoogleDrive/AI/Obsidian/Default/.agents/rules/audio-transcription.md).
   - **Translating into Notes**: All user input, notes, quotes, and thoughts provided in Polish (or another language) must be translated into clean, natural, idiomatic English before being incorporated into any vault document.

3. **Conversational Consistency & Language Mirroring**:
   - Chat dialogue must strictly mirror the language used by the user. When the user speaks or writes in Polish, the agent must converse and respond exclusively in Polish. When the user speaks in English, the agent responds in English.
   - Never switch or mix languages mid-dialogue. Conceptual exploration, Q&A, and brainstorming require cognitive cohesion; language-mixing creates mental friction and degrades the depth of the resulting context.
   - The English-only mandate applies strictly to persisted workspace notes and documentation files. Keep the conversational exploration 100% aligned with the user's spoken language, then translate and distill the refined concepts into English when creating or updating notes.

4. **Domain Abstraction (No Emulator or Hardware Leaks)**:
   - Always abstract low-level details (such as vintage computing, emulators, or CPU opcodes discussed in chat) into universal software engineering principles per [`language-agnostic-architecture.md`](file:///d:/GoogleDrive/AI/Obsidian/Default/.agents/rules/language-agnostic-architecture.md).

5. **Vault Cohesion & Reinforcing Established Thinking**:
   - Actively inspect existing notes across the 5-Layer Stack to maintain conceptual continuity and strengthen the knowledge graph with Obsidian `[[Note Title]]` links.

6. **Practitioner Voice & Tone**:
   - Adhere to [`practitioner-voice-and-tone.md`](file:///d:/GoogleDrive/AI/Obsidian/Default/.agents/rules/practitioner-voice-and-tone.md): write from the perspective of an experienced lead engineer and architect using the explanatory standard of an in-depth engineering blog post or technical video deep-dive.

7. **Verification Tooling**:
   - Compliance can be verified using the standalone script: `python scripts/check_polish.py --vault`.
