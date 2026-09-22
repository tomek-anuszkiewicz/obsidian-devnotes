---
trigger: always_on
description: Keep persisted vault content in English and mirror the user's language in chat.
---

# Notes Language

- Write public and private vault files in English: titles, frontmatter, headings, prose, tables, diagrams, wikilinks, and code comments.
- Reply in the user's language. Do not mix languages within a response.
- For audio, follow `audio-transcription.md` before doing other work.
- Use `python scripts/check_polish.py <file>` or `--vault` to check persisted public notes. The checker keeps a technical whitelist to avoid false positives.
