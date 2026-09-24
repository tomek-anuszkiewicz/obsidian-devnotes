"""Focused contract checks without a live MCP client or Qdrant instance."""

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


class FakeFastMCP:
    def __init__(self, name):
        self.name = name

    def tool(self):
        return lambda function: function


fastmcp_stub = types.ModuleType("fastmcp")
fastmcp_stub.FastMCP = FakeFastMCP
with patch.dict(sys.modules, {"fastmcp": fastmcp_stub}):
    path = Path(__file__).with_name("devnotes_rag_mcp_server.py")
    spec = importlib.util.spec_from_file_location("devnotes_rag_mcp_server", path)
    server = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server)


class DevnotesRagMcpTests(unittest.TestCase):
    def test_search_always_scopes_to_devnotes(self):
        with patch.object(server, "run_json", return_value=[]) as cli:
            self.assertEqual(server.devnotes_search("same mechanism", 3), [])
        cli.assert_called_once_with(
            "search", "same mechanism", "--source", "devnotes", "--limit", "3"
        )

    def test_search_rejects_out_of_scope_results(self):
        with patch.object(server, "run_json", return_value=[{"source": "amiga"}]):
            with self.assertRaisesRegex(RuntimeError, "outside the devnotes source"):
                server.devnotes_search("something")

    def test_list_sources_filters_shared_collection(self):
        sources = [{"source": "amiga"}, {"source": "devnotes", "files_count": 2}]
        with patch.object(server, "run_json", return_value=sources):
            self.assertEqual(server.devnotes_list_sources(), [sources[1]])

    def test_cli_uses_vault_env_and_json_contract(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / ".env").write_text("RAG_CACHE_FILE=shared-state.json\n", encoding="utf-8")
            completed = types.SimpleNamespace(returncode=0, stdout=json.dumps({"ok": True}), stderr="")
            with patch.object(server, "VAULT_ROOT", root), patch.object(
                server.shutil, "which", return_value="rag_qdrant.bat"
            ), patch.object(server.subprocess, "run", return_value=completed) as runner:
                self.assertEqual(server.run_json("--status"), {"ok": True})
            arguments, keywords = runner.call_args
            self.assertEqual(
                arguments[0],
                ["rag_qdrant.bat", "--status", "--index-json", "shared-state.json", "--json"],
            )
            self.assertEqual(keywords["cwd"], root)


if __name__ == "__main__":
    unittest.main()
