#!/usr/bin/env python3
"""Codex PreToolUse adapter for the repository language audit."""

import json
import re
import runpy
import sys
from pathlib import Path


repo_root = Path(__file__).resolve().parents[2]
target = repo_root / "scripts" / "check_polish.py"

if not target.exists():
    print(f"Error: {target} not found", file=sys.stderr)
    raise SystemExit(1)

module = runpy.run_path(str(target), run_name="check_polish_hook")
detect_polish_in_text = module["detect_polish_in_text"]

try:
    payload = json.load(sys.stdin)
except Exception:
    raise SystemExit(0)

if payload.get("tool_name") != "apply_patch":
    raise SystemExit(0)

command = payload.get("tool_input", {}).get("command", "")
targets = re.findall(r"^\*\*\* (?:Add|Update) File: (.+)$", command, re.MULTILINE)
public_markdown_targets = [target for target in targets if target.lower().endswith(".md")]

if not public_markdown_targets:
    raise SystemExit(0)

additions = [line[1:] for line in command.splitlines() if line.startswith("+") and not line.startswith("+++")]
violations = detect_polish_in_text("\n".join(additions))

if violations:
    words = ", ".join(repr(item[1]) for item in violations[:5])
    reason = f"Polish language detected in public note edit for {', '.join(public_markdown_targets)}: [{words}]. Translate the persisted note text into English before proceeding."
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}))
