"""Read-only MCP access to this vault's source in the shared rag_qdrant index."""

import json
import os
from pathlib import Path
import shutil
import subprocess

from fastmcp import FastMCP


VAULT_ROOT = Path(__file__).resolve().parent.parent
SOURCE = "devnotes"
mcp = FastMCP("devnotes-rag")


def index_state_file() -> str:
    """Use the same .env setting as update_rag_index.ps1."""
    env_file = VAULT_ROOT / ".env"
    try:
        lines = env_file.read_text(encoding="utf-8-sig").splitlines()
    except FileNotFoundError as exc:
        raise RuntimeError("Vault .env is missing; set RAG_CACHE_FILE before using RAG.") from exc

    for line in lines:
        name, separator, value = line.partition("=")
        if separator and name.strip() == "RAG_CACHE_FILE":
            value = value.strip()
            if not value:
                raise RuntimeError("RAG_CACHE_FILE is empty in vault .env.")
            return value
    raise RuntimeError("RAG_CACHE_FILE is missing from vault .env.")


def run_json(*arguments: str) -> object:
    command = "rag_qdrant.bat" if os.name == "nt" else "rag_qdrant"
    executable = shutil.which(command)
    if executable is None:
        raise RuntimeError(f"{command} is not available on PATH.")
    try:
        result = subprocess.run(
            [executable, *arguments, "--index-json", index_state_file(), "--json"],
            cwd=VAULT_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("rag_qdrant timed out after 120 seconds.") from exc
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise RuntimeError(f"rag_qdrant failed: {detail}")
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("rag_qdrant returned invalid JSON.") from exc
    if isinstance(response, dict) and isinstance(response.get("error"), str):
        raise RuntimeError(f"rag_qdrant failed: {response['error']}")
    return response


@mcp.tool()
def devnotes_search(query: str, limit: int = 5) -> list[dict]:
    """Find relevant devnotes passages by meaning; inspect source files before citing or editing."""
    if not query.strip():
        raise ValueError("Search query must not be empty.")
    if limit < 1:
        raise ValueError("Search limit must be at least 1.")
    results = run_json("search", query, "--source", SOURCE, "--limit", str(limit))
    if not isinstance(results, list) or any(not isinstance(hit, dict) for hit in results):
        raise RuntimeError("rag_qdrant search returned an unexpected JSON response.")
    if any(hit.get("source") != SOURCE for hit in results):
        raise RuntimeError("rag_qdrant returned a result outside the devnotes source.")
    return results


@mcp.tool()
def devnotes_list_sources() -> list[dict]:
    """Show whether devnotes is indexed, with its file and chunk counts."""
    sources = run_json("--list-sources")
    if not isinstance(sources, list) or any(not isinstance(item, dict) for item in sources):
        raise RuntimeError("rag_qdrant list-sources returned an unexpected JSON response.")
    return [item for item in sources if item.get("source") == SOURCE]


@mcp.tool()
def devnotes_status() -> dict:
    """Report connectivity and collection health for the shared Qdrant collection."""
    status = run_json("--status")
    if not isinstance(status, dict):
        raise RuntimeError("rag_qdrant status returned an unexpected JSON response.")
    return status


if __name__ == "__main__":
    mcp.run()
