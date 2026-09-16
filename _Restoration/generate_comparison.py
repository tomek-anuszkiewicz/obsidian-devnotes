#!/usr/bin/env python3
"""
_Restoration/generate_comparison.py

Generates a native Markdown comparison table for Obsidian:
Original reference notes vs. Restored notes produced by Gemini 3.8 Flash (High Thinking).
Uses native Markdown pipe tables with <br> and <pre><code> so Obsidian renders perfectly in all modes.
"""

import html
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RESTORATION_DIR = REPO_ROOT / "_Restoration"
ORIG_DIR = RESTORATION_DIR / "original_notes"
REST_DIR = RESTORATION_DIR / "restored_output"
OUTPUT_FILE = RESTORATION_DIR / "comparison_side_by_side.md"


def strip_frontmatter(content: str) -> str:
    """Strip YAML frontmatter from document."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return content.strip()


def split_into_blocks(content: str):
    """Split content into heading-based sections."""
    text = strip_frontmatter(content)
    sections = []
    current_title = "Overview & Core Premise"
    current_lines = []

    heading_regex = re.compile(r"^(#{1,3})\s+(.+)$")

    for line in text.splitlines():
        match = heading_regex.match(line.strip())
        if match:
            if current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
                current_lines = []
            current_title = match.group(2).strip()
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))

    return sections


def format_table_cell(text: str) -> str:
    """Format a block of text to be completely safe inside a Markdown pipe table cell."""
    if not text:
        return "*(No matching section)*"

    lines = text.strip().splitlines()
    out = []
    in_code = False
    code_buf = []

    for line in lines:
        stripped = line.strip()

        # Handle code blocks
        if stripped.startswith("```"):
            if in_code:
                code_text = html.escape("\n".join(code_buf)).replace("\n", "<br>")
                out.append(f"<pre><code>{code_text}</code></pre>")
                in_code = False
                code_buf = []
            else:
                in_code = True
                code_buf = []
            continue

        if in_code:
            code_buf.append(line)
            continue

        if not stripped:
            continue

        # Handle lists
        if stripped.startswith("- ") or stripped.startswith("* "):
            clean_item = stripped[2:].replace("|", "&#124;")
            out.append(f"&bull; {clean_item}")
        elif re.match(r"^\d+\.\s+", stripped):
            clean_item = stripped.replace("|", "&#124;")
            out.append(clean_item)
        else:
            clean_line = stripped.replace("|", "&#124;")
            out.append(clean_line)

    if in_code and code_buf:
        code_text = html.escape("\n".join(code_buf)).replace("\n", "<br>")
        out.append(f"<pre><code>{code_text}</code></pre>")

    return "<br><br>".join(out)


def generate_comparison():
    orig_files = sorted(list(ORIG_DIR.glob("*.md")))
    md_lines = []

    md_lines.append("# Side-by-Side Restoration Comparison: Original vs. Restored Notes\n")
    md_lines.append("> [!NOTE]")
    md_lines.append("> Row-by-row comparative evaluation of the 6 reference notes.")
    md_lines.append("> Left column: Original reference note (ChatGPT baseline).")
    md_lines.append("> Right column: Restored note synthesized by **Gemini 3.8 Flash (High Thinking)**.\n")

    for orig_path in orig_files:
        rest_path = REST_DIR / orig_path.name
        if not rest_path.exists():
            continue

        orig_text = orig_path.read_text(encoding="utf-8", errors="ignore")
        rest_text = rest_path.read_text(encoding="utf-8", errors="ignore")

        orig_words = len(orig_text.split())
        rest_words = len(rest_text.split())
        reduction = ((orig_words - rest_words) / orig_words) * 100 if orig_words > 0 else 0

        title = orig_path.stem

        md_lines.append(f"## Note: {title}\n")
        md_lines.append(f"**Metrics**: Original: **{orig_words} words** | Restored: **{rest_words} words** | Compression: **-{reduction:.1f}%**\n")

        orig_blocks = split_into_blocks(orig_text)
        rest_blocks = split_into_blocks(rest_text)

        max_len = max(len(orig_blocks), len(rest_blocks))

        md_lines.append(f"| Original Note ({orig_words} words) | Restored Note - Gemini Flash ({rest_words} words) |")
        md_lines.append("| :--- | :--- |")

        for i in range(max_len):
            orig_title, orig_body = orig_blocks[i] if i < len(orig_blocks) else ("", "")
            rest_title, rest_body = rest_blocks[i] if i < len(rest_blocks) else ("", "")

            orig_cell = f"**{orig_title.replace('|', '&#124;')}**<br><br>{format_table_cell(orig_body)}" if orig_title or orig_body else "*(End of original note)*"
            rest_cell = f"**{rest_title.replace('|', '&#124;')}**<br><br>{format_table_cell(rest_body)}" if rest_title or rest_body else "*(End of restored note)*"

            # Must be a single line per table row in Markdown
            md_lines.append(f"| {orig_cell} | {rest_cell} |")

        md_lines.append("\n---\n")

    OUTPUT_FILE.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"[SUCCESS] Generated native markdown table at: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_comparison()
