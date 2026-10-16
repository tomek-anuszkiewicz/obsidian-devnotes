"""Focused checks for the English scanner's encoding diagnostics."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCANNER = Path(__file__).with_name("check_english.py")


class EncodingDamageTests(unittest.TestCase):
    def scan(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.md"
            path.write_text(text, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCANNER), str(path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

    def test_corrupted_quotes_have_explicit_diagnostic(self):
        broken = "An unconstrained \u00e2\u20ac\u0153keep trying until tests pass\u00e2\u20ac  loop.\n"
        result = self.scan(broken)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Suspected encoding damage", result.stdout)
        self.assertIn("1 damaged-encoding lines", result.stdout)

    def test_valid_curly_quotes_are_accepted(self):
        clean = "An unconstrained \u201ckeep trying until tests pass\u201d loop.\n"
        result = self.scan(clean)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("0 damaged-encoding lines", result.stdout)

    def test_corrupted_arrows_and_box_lines_have_explicit_diagnostic(self):
        broken = "a \u00e2\u2020\u201c b \u00e2\u201d\u20ac c\n"
        result = self.scan(broken)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Suspected encoding damage", result.stdout)
        self.assertIn("1 damaged-encoding lines", result.stdout)

    def test_escape_patterns_do_not_become_unknown_glyphs(self):
        source = r'pattern = r"\u00e2\u20ac\u0153|\u00f0\u0178"' + "\n"
        result = self.scan(source)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_escaped_word_is_still_checked(self):
        source = r'word = "\u0070\u006f\u006c\u0073\u006b\u0061"' + "\n"
        result = self.scan(source)
        self.assertEqual(result.returncode, 1)
        self.assertIn("[polska]", result.stdout)


if __name__ == "__main__":
    unittest.main()
