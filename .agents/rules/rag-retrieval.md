---
trigger: always_on
description: Use the local devnotes RAG MCP server for semantic discovery when available, then verify against vault files.
---

# RAG Retrieval

For cross-references, related notes, or arguments described in different words,
try the local `devnotes-rag` MCP `devnotes_search` tool when it is available. Use
literal file search for exact titles, terms, identifiers, and link targets.

RAG results are candidates, not evidence by themselves. Read the current note
and verify its claim and link target before citing or editing it. If the MCP
server is unavailable, returns no useful result, or the index may be stale,
continue with direct whole-vault file searches. Do not infer that a claim is
absent solely from an empty RAG result.
