---
name: check-english
description: Check repository-owned text against an English dictionary and reviewed technical vocabulary when editing notes, auditing language, or preparing a commit.
---

# Check English

Run `python scripts/check_english.py` from the vault root to scan tracked text files and nonignored new text files. The file types and exclusions are defined in `scripts/check_english.json`. Use `python scripts/check_english.py "path/to/file.md"` for a focused check; explicit file paths bypass scope exclusions.

The scanner reports words absent from the English dictionary and the reviewed lists in `scripts/english_words/`. It separately reports common damaged Unicode sequences, such as broken smart quotes. An unknown word is a finding, not proof that it is non-English. Inspect the source line and report likely corrections or a possible vocabulary addition for the user's decision. Do not automatically correct text or add exceptions. Keep deliberate invalid examples confined to the owning file through `file_words` in the scope JSON. Do not suppress findings by excluding authored content.

The full scan may report existing findings. State the command, result, and limits accurately; do not describe an unrun or failing check as clean. Install the pinned dependency with `python -m pip install -r scripts/requirements-check-english.txt` if needed.
