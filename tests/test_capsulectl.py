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

    def test_install_creates_v11_navigation_and_validates(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            target.mkdir()
            result = self.run_cli("install", "--target", str(target), "--repository", "owner/repo", "--branch", "main")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            metadata = json.loads((target / ".context/capsule.json").read_text(encoding="utf-8"))
            manifest = json.loads((target / ".context/manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["version"], "1.1.0")
            self.assertEqual(manifest["schema"], "context-capsule-manifest")
            self.assertEqual(manifest["authoritative_branch"], "main")
            self.assertTrue((target / "AGENTS.md").exists())
            self.assertTrue((target / ".context/protocol.md").exists())
            self.assertTrue((target / ".context/dialogues/README.md").exists())

    def test_reinstall_refused(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            target.mkdir()
            first = self.run_cli("install", "--target", str(target), "--repository", "owner/repo")
            self.assertEqual(first.returncode, 0)
            second = self.run_cli("install", "--target", str(target), "--repository", "owner/repo")
            self.assertEqual(second.returncode, 2)

    def test_legacy_adoption_preserves_rich_structure(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            (target / ".context/rules").mkdir(parents=True)
            (target / ".context/current").mkdir(parents=True)
            (target / ".context/handoffs").mkdir(parents=True)
            (target / ".context/decisions").mkdir(parents=True)
            (target / ".context/dialogues").mkdir(parents=True)
            (target / "AI_CONTEXT.md").write_text("CUSTOM POINTER\n", encoding="utf-8")
            (target / ".context/ENTRYPOINT.md").write_text("CUSTOM ENTRYPOINT\n", encoding="utf-8")
            (target / ".context/rules/project.md").write_text("LEGACY RULES\n", encoding="utf-8")
            (target / ".context/current/state.md").write_text("LEGACY STATE\n", encoding="utf-8")
            (target / ".context/handoffs/latest.md").write_text("LEGACY HANDOFF\n", encoding="utf-8")
            (target / ".context/decisions/accepted.md").write_text("LEGACY DECISION\n", encoding="utf-8")
            (target / ".context/dialogues/episode.md").write_text("LEGACY DIALOGUE\n", encoding="utf-8")
            legacy_manifest = {
                "schema_version": 1,
                "repository": "owner/repo",
                "authoritative_branch": "main",
                "entrypoint": ".context/ENTRYPOINT.md",
                "latest_handoff": ".context/handoffs/latest.md",
                "current_state": ".context/current/state.md",
                "rules": [".context/rules/project.md"],
                "decisions": [".context/decisions/accepted.md"],
                "dialogues": [".context/dialogues/episode.md"],
                "custom_legacy_field": "keep-me",
            }
            (target / ".context/manifest.json").write_text(json.dumps(legacy_manifest), encoding="utf-8")
            result = self.run_cli("adopt", "--target", str(target), "--repository", "owner/repo")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual((target / ".context/ENTRYPOINT.md").read_text(encoding="utf-8"), "CUSTOM ENTRYPOINT\n")
            self.assertEqual((target / ".context/rules/project.md").read_text(encoding="utf-8"), "LEGACY RULES\n")
            manifest = json.loads((target / ".context/manifest.json").read_text(encoding="utf-8"))
            metadata = json.loads((target / ".context/capsule.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["rules"], [".context/rules/project.md"])
            self.assertEqual(manifest["custom_legacy_field"], "keep-me")
            self.assertEqual(metadata["adopted_from"], "legacy")
            self.assertFalse((target / ".context/rules/project-rules.md").exists())

    def test_repair_preserves_project_content_and_refreshes_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            target.mkdir()
            self.assertEqual(self.run_cli("install", "--target", str(target), "--repository", "owner/repo").returncode, 0)
            rule = target / ".context/rules/project-rules.md"
            rule.write_text("PROJECT DATA\n", encoding="utf-8")
            (target / "AGENTS.md").unlink()
            repaired = self.run_cli("repair", "--target", str(target))
            self.assertEqual(repaired.returncode, 0, repaired.stdout + repaired.stderr)
            self.assertEqual(rule.read_text(encoding="utf-8"), "PROJECT DATA\n")
            self.assertTrue((target / "AGENTS.md").exists())

    def test_upgrade_1_0_to_1_1(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            (target / ".context/current").mkdir(parents=True)
            (target / ".context/rules").mkdir(parents=True)
            (target / ".context/decisions").mkdir(parents=True)
            (target / ".context/handoffs").mkdir(parents=True)
            (target / ".context/history").mkdir(parents=True)
            (target / "AI_CONTEXT.md").write_text("# AI Context\n\nThis repository uses Context Capsule.\n\nStart recovery at:\n\n`.context/ENTRYPOINT.md`\n\nThe complete project context is stored in this repository. Do not look for a central copy of project context in Context Capsule Core.\n", encoding="utf-8")
            (target / ".context/ENTRYPOINT.md").write_text("# Context Capsule entrypoint\n\nRead in this order:\n\n1. `.context/capsule.json`\n2. `.context/rules/project-rules.md`\n3. `.context/current/state.md`\n4. `.context/decisions/`\n5. `.context/handoffs/latest.md`\n6. `.context/history/` only when deeper history is required\n\nThen verify the recovered state against the repository at the current commit.\n\nIf repository facts are newer than the capsule, treat repository facts as authoritative and update the capsule before continuing substantial work.\n\nNever send or synchronize project context back to Context Capsule Core.\n", encoding="utf-8")
            (target / ".context/current/state.md").write_text("state\n", encoding="utf-8")
            (target / ".context/rules/project-rules.md").write_text("rules\n", encoding="utf-8")
            (target / ".context/decisions/README.md").write_text("decisions\n", encoding="utf-8")
            (target / ".context/handoffs/latest.md").write_text("handoff\n", encoding="utf-8")
            (target / ".context/history/README.md").write_text("history\n", encoding="utf-8")
            meta = {
                "schema": "context-capsule",
                "version": "1.0.0",
                "source": "lvlaksim1/context-capsule",
                "installed_at": "2026-09-19",
                "repository": "owner/repo",
                "update_policy": "manual",
            }
            (target / ".context/capsule.json").write_text(json.dumps(meta), encoding="utf-8")
            result = self.run_cli("upgrade", "--target", str(target))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            metadata = json.loads((target / ".context/capsule.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["version"], "1.1.0")
            self.assertTrue((target / ".context/manifest.json").exists())
            self.assertTrue((target / ".context/protocol.md").exists())
            self.assertTrue((target / "AGENTS.md").exists())
            self.assertIn(".context/manifest.json", (target / ".context/ENTRYPOINT.md").read_text(encoding="utf-8"))
            self.assertEqual((target / ".context/current/state.md").read_text(encoding="utf-8"), "state\n")


if __name__ == "__main__":
    unittest.main()
