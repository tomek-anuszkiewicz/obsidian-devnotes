# Devnotes RAG MCP server

`devnotes_rag_mcp_server.py` is a small, read-only MCP server for this vault. It
starts over standard input/output when an MCP client launches it. It calls the
`rag_qdrant` command for every request; the CLI handles Qdrant connection,
embeddings, and the shared `projects_docs` collection. The server does not run
indexing or connect to Qdrant directly.

## Tools

| MCP tool | CLI call | Result |
| --- | --- | --- |
| `devnotes_search(query, limit=5)` | `search QUERY --source devnotes --limit N --index-json FILE --json` | Matching passages with scores and source locations; `[]` means no match above the CLI threshold. |
| `devnotes_list_sources()` | `--list-sources --index-json FILE --json` | Only the `devnotes` entry, with indexed file and chunk counts; `[]` means it is absent. |
| `devnotes_status()` | `--status --index-json FILE --json` | Connection and health data for the shared Qdrant collection, including totals across all sources. |

Search never accepts a source parameter, so a caller cannot accidentally search
the other projects in the shared collection. The server passes JSON results
through without changing the CLI's ranking or score threshold. It does not
provide a reindex tool: use `scripts/update_rag_index.ps1` for that operation.

## Setup

1. Use a Python environment with the MCP dependency installed:

   ```powershell
   python -m pip install -r scripts/requirements-rag-mcp.txt
   ```

2. Make sure the same environment can launch `rag_qdrant.bat` on Windows (or
   `rag_qdrant` on other systems), and that the CLI can reach Qdrant.
3. Set `RAG_CACHE_FILE` in the vault-root `.env`. Use the same index state file
   as `scripts/update_rag_index.ps1`; the server reads this setting on every
   request. The CLI must be able to read that file.

Register the server with an MCP client using the vault root as its working
directory. For clients using an `mcpServers` JSON object:

```json
{
  "mcpServers": {
    "devnotes-rag": {
      "command": "python",
      "args": ["scripts/devnotes_rag_mcp_server.py"]
    }
  }
}
```

Configure the client to start it from the vault root, or resolve the script path
relative to the client's project directory. Restart the client after adding
the server. Startup requires FastMCP; individual tools report a missing CLI,
missing `.env` setting, timeout, or malformed CLI response as MCP errors.

## Use for vault work

Use `devnotes_search` to discover notes about a concept when the wording may differ
from the query. Search exact titles, identifiers, and literal terms in the files.
Open candidate notes and verify claims, links, and current text before editing
or citing them. The index can lag behind uncommitted edits or a failed indexing
run, and an empty result does not prove that an idea is absent from the vault.
