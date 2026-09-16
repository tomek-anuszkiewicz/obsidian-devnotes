#!/usr/bin/env python3
"""
_Restoration/generate_comparison.py

Generates a side-by-side Markdown/HTML table comparing the original input notes
with the restored notes produced by Gemini 3.8 Flash (High Thinking).
"""

import html
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RESTORATION_DIR = REPO_ROOT / "_Restoration"
ORIG_DIR = RESTORATION_DIR / "original_notes"
REST_DIR = RESTORATION_DIR / "restored_output"
OUTPUT_FILE = RESTORATION_DIR / "comparison_side_by_side.md"


def markdown_to_html_cell(text: str) -> str:
    """Converts a section of markdown into safe HTML for table cells."""
    lines = text.strip().splitlines()
    out = []
    in_code = False
    code_lines = []

    for line in lines:
        if line.startswith("```"):
            if in_code:
                escaped_code = html.escape("\n".join(code_lines))
                out.append(f"<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>{escaped_code}</code></pre>")
                in_code = False
                code_lines = []
            else:
                in_code = True
                code_lines = []
            continue

        if in_code:
            code_lines.append(line)
            continue

        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("### "):
            out.append(f"<h4 style='margin-top: 10px; margin-bottom: 4px; color: var(--text-accent);'>{html.escape(stripped[4:])}</h4>")
        elif stripped.startswith("## "):
            out.append(f"<h3 style='margin-top: 14px; margin-bottom: 6px; color: var(--text-accent);'>{html.escape(stripped[3:])}</h3>")
        elif stripped.startswith("# "):
            out.append(f"<h2 style='margin-top: 16px; margin-bottom: 8px; color: var(--text-accent);'>{html.escape(stripped[2:])}</h2>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            out.append(f"<li style='margin-left: 18px;'>{html.escape(stripped[2:])}</li>")
        elif re.match(r"^\d+\.\s+", stripped):
            content = re.sub(r"^\d+\.\s+", "", stripped)
            out.append(f"<li style='margin-left: 18px;'>{html.escape(content)}</li>")
        else:
            out.append(f"<p style='margin-bottom: 8px; line-height: 1.45;'>{html.escape(stripped)}</p>")

    if in_code and code_lines:
        escaped_code = html.escape("\n".join(code_lines))
        out.append(f"<pre style='background-color: var(--background-secondary); padding: 8px; border-radius: 4px; overflow-x: auto;'><code>{escaped_code}</code></pre>")

    return "\n".join(out)


def split_into_sections(content: str):
    """Splits markdown into major sections based on ## headings."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2].strip()

    sections = []
    current_title = "Overview / Introduction"
    current_body = []

    for line in content.splitlines():
        if line.startswith("## "):
            if current_body:
                sections.append((current_title, "\n".join(current_body).strip()))
                current_body = []
            current_title = line[3:].strip()
        else:
            current_body.append(line)

    if current_body:
        sections.append((current_title, "\n".join(current_body).strip()))

    return sections


def generate_comparison_markdown():
    orig_files = sorted(list(ORIG_DIR.glob("*.md")))
    md_output = []

    md_output.append("# Side-by-Side Restoration Comparison: Original vs. Restored Notes\n")
    md_output.append("> [!NOTE]\n")
    md_output.append("> This document provides a direct, row-by-row comparative evaluation of the reference notes.\n")
    md_output.append("> Left column: Original reference note (pre-deconstruction).\n")
    md_output.append("> Right column: Restored note synthesized by **Gemini 3.8 Flash (High Thinking)**.\n\n")

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

        md_output.append(f"\n---\n\n## Note: {title}\n")
        md_output.append(f"**Metrics**: Original: **{orig_words} words** | Restored: **{rest_words} words** | Compression: **-{reduction:.1f}%**\n\n")

        orig_sections = split_into_sections(orig_text)
        rest_sections = split_into_sections(rest_text)

        max_len = max(len(orig_sections), len(rest_sections))

        md_output.append("<table style='width: 100%; table-layout: fixed; border-collapse: collapse; margin-bottom: 24px;'>\n")
        md_output.append("  <tr style='background-color: var(--background-secondary-alt); border-bottom: 2px solid var(--background-modifier-border);'>\n")
        md_output.append(f"    <th style='width: 50%; padding: 10px; text-align: left; font-size: 1.05em;'>Original Input Note ({orig_words} words)</th>\n")
        md_output.append(f"    <th style='width: 50%; padding: 10px; text-align: left; font-size: 1.05em;'>Restored Note - Gemini Flash High-Thinking ({rest_words} words)</th>\n")
        md_output.append("  </tr>\n")

        for i in range(max_len):
            orig_sec = orig_sections[i] if i < len(orig_sections) else ("", "")
            rest_sec = rest_sections[i] if i < len(rest_sections) else ("", "")

            orig_cell_html = f"<strong style='color: var(--text-accent);'>{html.escape(orig_sec[0])}</strong><hr style='margin: 4px 0 8px 0;'>{markdown_to_html_cell(orig_sec[1])}" if orig_sec[1] else "<em>(No matching section)</em>"
            rest_cell_html = f"<strong style='color: var(--text-accent);'>{html.escape(rest_sec[0])}</strong><hr style='margin: 4px 0 8px 0;'>{markdown_to_html_cell(rest_sec[1])}" if rest_sec[1] else "<em>(No matching section)</em>"

            row_bg = "background-color: var(--background-primary);" if i % 2 == 0 else "background-color: var(--background-secondary);"

            md_output.append(f"  <tr style='{row_bg}; border-bottom: 1px solid var(--background-modifier-border);'>\n")
            md_output.append(f"    <td style='vertical-align: top; padding: 12px; border-right: 1px solid var(--background-modifier-border);'>\n{orig_cell_html}\n    </td>\n")
            md_output.append(f"    <td style='vertical-align: top; padding: 12px;'>\n{rest_cell_html}\n    </td>\n")
            md_output.append("  </tr>\n")

        md_output.append("</table>\n\n")

    OUTPUT_FILE.write_text("\n".join(md_output), encoding="utf-8")
    print(f"[SUCCESS] Generated side-by-side comparison file at: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_comparison_markdown()
