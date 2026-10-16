---
trigger: always_on
description: Keep persisted vault content in English and mirror the user's language in chat.
---

# Notes Language

- Write files in this vault in English: titles, frontmatter, headings, prose, tables, diagrams, wikilinks, and code comments.
- Reply in the user's language. Do not mix languages within a response.
- Check repository-owned text with `python scripts/check_english.py`; its scope is defined in `scripts/check_english.json`. Report unknown words for a decision before correcting text or adding vocabulary exceptions.
