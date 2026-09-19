import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "installer" / "capsulectl.py"


class CapsuleCtlTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *args], text=True, capture_output=True)

    def test_install_validate_and_non_destructive_repair(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            target.mkdir()
            result = self.run_cli("install", "--target", str(target), "--repository", "owner/repo")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            metadata = json.loads((target / ".context/capsule.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["version"], (ROOT / "VERSION").read_text().strip())
            decision = target / ".context/decisions/README.md"
            decision.write_text("PROJECT DATA\n", encoding="utf-8")
            (target / "AI_CONTEXT.md").unlink()
            repaired = self.run_cli("repair", "--target", str(target))
            self.assertEqual(repaired.returncode, 0, repaired.stdout + repaired.stderr)
            self.assertEqual(decision.read_text(encoding="utf-8"), "PROJECT DATA\n")
            self.assertTrue((target / "AI_CONTEXT.md").exists())

    def test_reinstall_refused(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            target.mkdir()
            first = self.run_cli("install", "--target", str(target), "--repository", "owner/repo")
            self.assertEqual(first.returncode, 0)
            second = self.run_cli("install", "--target", str(target), "--repository", "owner/repo")
            self.assertEqual(second.returncode, 2)


if __name__ == "__main__":
    unittest.main()
