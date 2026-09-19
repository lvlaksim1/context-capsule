import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "installer" / "capsulectl.py"


class CapsuleCtlTests(unittest.TestCase):
    def _git(self, target, *args, check=True):
        return subprocess.run(
            ["git", *args],
            cwd=target,
            text=True,
            capture_output=True,
            check=check,
        )

    def _prepare_git_fixture(self, args):
        if not args or args[0] not in {"install", "adopt", "repair", "upgrade"}:
            return
        if "--target" not in args:
            return
        target = Path(args[args.index("--target") + 1])
        target.mkdir(parents=True, exist_ok=True)
        created = not (target / ".git").exists()
        if created:
            self._git(target, "init", "-b", "main")
            self._git(target, "config", "user.email", "test@example.com")
            self._git(target, "config", "user.name", "Context Capsule Test")
            if not self._git(target, "status", "--porcelain").stdout.strip():
                (target / ".test-anchor").write_text("fixture\n")
            self._git(target, "add", ".")
            self._git(target, "commit", "-m", "fixture")
            if "--branch" in args:
                desired = args[args.index("--branch") + 1]
                if desired != "main":
                    self._git(target, "checkout", "-b", desired)
        else:
            self._git(target, "config", "user.email", "test@example.com")
            self._git(target, "config", "user.name", "Context Capsule Test")
            status = self._git(target, "status", "--porcelain").stdout.strip()
            if status:
                self._git(target, "add", ".")
                self._git(target, "commit", "-m", "fixture update")

    def run_cli(self, *args, cwd=None, prepare=True):
        if prepare:
            self._prepare_git_fixture(args)
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            text=True,
            capture_output=True,
            cwd=cwd,
        )

    def test_install_creates_v13_structure(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            target.mkdir()
            result = self.run_cli(
                "install", "--target", str(target), "--repository", "owner/repo",
                "--branch", "main", "--discovery-branch", "main",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            metadata = json.loads((target / ".context/capsule.json").read_text(encoding="utf-8"))
            manifest = json.loads((target / ".context/manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["version"], "1.3.0")
            self.assertEqual(manifest["schema_version"], 3)
            self.assertEqual(manifest["branch_mode"], "single")
            self.assertEqual(manifest["project"]["identity"], ".context/project/identity.md")
            self.assertEqual(manifest["current"]["blockers"], ".context/current/blockers.md")
            self.assertTrue((target / ".context/current/next.md").exists())
            self.assertTrue((target / ".context/project/architecture.md").exists())
            self.assertTrue((target / ".context/resume.json").exists())
            self.assertTrue((target / ".context/index.json").exists())
            self.assertTrue((target / ".context/tools/capsule_runtime.py").exists())
            self.assertIn("managed_files", metadata)

    def test_reinstall_refused(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            target.mkdir()
            self.assertEqual(self.run_cli("install", "--target", str(target), "--repository", "owner/repo").returncode, 0)
            self.assertEqual(self.run_cli("install", "--target", str(target), "--repository", "owner/repo").returncode, 2)

    def test_fgis_style_legacy_adoption_preserves_rich_paths(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            for d in ["project", "current", "rules", "decisions", "dialogues", "handoffs"]:
                (target / ".context" / d).mkdir(parents=True, exist_ok=True)
            files = {
                ".context/project/identity.md": "identity\n",
                ".context/project/goals.md": "goals\n",
                ".context/project/architecture.md": "architecture\n",
                ".context/project/constraints.md": "constraints\n",
                ".context/current/state.md": "state\n",
                ".context/current/blockers.md": "blockers\n",
                ".context/current/next.md": "next\n",
                ".context/rules/user-rules.md": "user rules\n",
                ".context/rules/development-rules.md": "dev rules\n",
                ".context/rules/ai-rules.md": "ai rules\n",
                ".context/handoffs/latest.md": "handoff\n",
                ".context/decisions/DEC-1.md": "decision\n",
                ".context/dialogues/CHAT-1.md": "dialogue\n",
                ".context/ENTRYPOINT.md": "CUSTOM ENTRYPOINT\n",
                ".context/protocol.md": "CUSTOM PROTOCOL\n",
                "AI_CONTEXT.md": "CUSTOM POINTER\n",
                "AGENTS.md": "CUSTOM AGENTS\n",
            }
            for rel, content in files.items():
                p = target / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")
            legacy = {
                "schema_version": 1,
                "repository": "owner/repo",
                "default_branch": "main",
                "bootstrap_entrypoint": ".context/ENTRYPOINT.md",
                "active_handoff": ".context/handoffs/latest.md",
                "authoritative": {
                    "identity": ".context/project/identity.md",
                    "goals": ".context/project/goals.md",
                    "constraints": ".context/project/constraints.md",
                    "current_state": ".context/current/state.md",
                    "blockers": ".context/current/blockers.md",
                    "next": ".context/current/next.md",
                    "user_rules": ".context/rules/user-rules.md",
                    "development_rules": ".context/rules/development-rules.md",
                    "ai_rules": ".context/rules/ai-rules.md",
                },
                "custom_legacy_field": "keep-me",
            }
            (target / ".context/manifest.json").write_text(json.dumps(legacy), encoding="utf-8")
            result = self.run_cli("adopt", "--target", str(target), "--repository", "owner/repo")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            manifest = json.loads((target / ".context/manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["custom_legacy_field"], "keep-me")
            self.assertEqual(manifest["project"]["identity"], ".context/project/identity.md")
            self.assertEqual(manifest["current"]["next"], ".context/current/next.md")
            self.assertEqual(
                manifest["rules"],
                [
                    ".context/rules/user-rules.md",
                    ".context/rules/development-rules.md",
                    ".context/rules/ai-rules.md",
                ],
            )
            entrypoint = (target / ".context/ENTRYPOINT.md").read_text()
            self.assertIn("CUSTOM ENTRYPOINT", entrypoint)
            self.assertIn("context-capsule:begin", entrypoint)
            resume = json.loads((target / ".context/resume.json").read_text())
            self.assertIn(".context/ENTRYPOINT.md", resume["bootstrap_review"])
            self.assertFalse((target / ".context/rules/project-rules.md").exists())

    def test_ai_agent_style_branch_and_runtime_are_detected(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            (target / ".context/current").mkdir(parents=True)
            (target / ".context/handoffs").mkdir(parents=True)
            (target / ".context/rules").mkdir(parents=True)
            (target / ".agent").mkdir(parents=True)
            (target / ".context/current/state.md").write_text("state\n")
            (target / ".context/handoffs/latest.md").write_text("handoff\n")
            (target / ".context/rules/ai-rules.md").write_text("rules\n")
            (target / ".context/ENTRYPOINT.md").write_text("entry\n")
            (target / ".context/protocol.md").write_text("protocol\n")
            (target / "AI_CONTEXT.md").write_text("pointer\n")
            (target / "AGENTS.md").write_text("agents\n")
            legacy = {
                "repository": "owner/repo",
                "default_branch": "main",
                "authoritative_context_branch": "work-webhook-test",
                "active_handoff": ".context/handoffs/latest.md",
                "authoritative_files": {"live_runtime": ".agent/"},
            }
            (target / ".context/manifest.json").write_text(json.dumps(legacy), encoding="utf-8")
            result = self.run_cli(
                "adopt", "--target", str(target), "--repository", "owner/repo",
                "--branch", "work-webhook-test",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            manifest = json.loads((target / ".context/manifest.json").read_text())
            self.assertEqual(manifest["authoritative_branch"], "work-webhook-test")
            self.assertEqual(manifest["discovery_branch"], "main")
            self.assertEqual(manifest["branch_mode"], "redirect")
            self.assertIn(".agent/", manifest["runtime"]["authoritative_paths"])
            self.assertTrue(manifest["runtime"]["promote_semantic_changes_only"])

    def test_repair_preserves_project_content(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            target.mkdir()
            self.assertEqual(self.run_cli("install", "--target", str(target), "--repository", "owner/repo").returncode, 0)
            rule = target / ".context/rules/project-rules.md"
            rule.write_text("PROJECT DATA\n")
            (target / ".context/current/blockers.md").unlink()
            repaired = self.run_cli("repair", "--target", str(target))
            self.assertEqual(repaired.returncode, 0, repaired.stdout + repaired.stderr)
            self.assertEqual(rule.read_text(), "PROJECT DATA\n")
            self.assertTrue((target / ".context/current/blockers.md").exists())

    def test_upgrade_1_1_to_1_3_preserves_state(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            (target / ".context/current").mkdir(parents=True)
            (target / ".context/rules").mkdir(parents=True)
            (target / ".context/handoffs").mkdir(parents=True)
            (target / ".context/decisions").mkdir(parents=True)
            (target / ".context/dialogues").mkdir(parents=True)
            (target / ".context/history").mkdir(parents=True)
            for rel, content in {
                "AI_CONTEXT.md": "custom pointer\n",
                "AGENTS.md": "custom agents\n",
                ".context/ENTRYPOINT.md": "custom entry\n",
                ".context/protocol.md": "custom protocol\n",
                ".context/current/state.md": "IMPORTANT STATE\n",
                ".context/rules/project-rules.md": "IMPORTANT RULES\n",
                ".context/handoffs/latest.md": "IMPORTANT HANDOFF\n",
            }.items():
                p = target / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content)
            meta = {
                "schema": "context-capsule",
                "version": "1.1.0",
                "source": "lvlaksim1/context-capsule",
                "installed_at": "2026-09-19",
                "repository": "owner/repo",
                "update_policy": "manual",
            }
            manifest = {
                "schema": "context-capsule-manifest",
                "schema_version": 1,
                "repository": "owner/repo",
                "authoritative_branch": "main",
                "entrypoint": ".context/ENTRYPOINT.md",
                "capsule_metadata": ".context/capsule.json",
                "latest_handoff": ".context/handoffs/latest.md",
                "current_state": ".context/current/state.md",
                "protocol": ".context/protocol.md",
                "rules": [".context/rules/project-rules.md"],
                "decisions": [],
                "dialogues": [],
                "history": [],
                "updated_at": "2026-09-19",
            }
            (target / ".context/capsule.json").write_text(json.dumps(meta))
            (target / ".context/manifest.json").write_text(json.dumps(manifest))
            result = self.run_cli("upgrade", "--target", str(target))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            new_meta = json.loads((target / ".context/capsule.json").read_text())
            new_manifest = json.loads((target / ".context/manifest.json").read_text())
            self.assertEqual(new_meta["version"], "1.3.0")
            self.assertEqual(new_manifest["schema_version"], 3)
            self.assertEqual((target / ".context/current/state.md").read_text(), "IMPORTANT STATE\n")
            self.assertTrue((target / ".context/current/blockers.md").exists())
            self.assertTrue((target / ".context/project/identity.md").exists())

    def test_upgrade_1_0_chains_to_1_3(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            (target / ".context/current").mkdir(parents=True)
            (target / ".context/rules").mkdir(parents=True)
            (target / ".context/handoffs").mkdir(parents=True)
            (target / ".context/current/state.md").write_text("state\n")
            (target / ".context/rules/project-rules.md").write_text("rules\n")
            (target / ".context/handoffs/latest.md").write_text("handoff\n")
            meta = {
                "schema": "context-capsule",
                "version": "1.0.0",
                "source": "lvlaksim1/context-capsule",
                "installed_at": "2026-09-19",
                "repository": "owner/repo",
                "update_policy": "manual",
            }
            (target / ".context/capsule.json").write_text(json.dumps(meta))
            result = self.run_cli("upgrade", "--target", str(target))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("migrate 1.0.0 -> 1.1.0", result.stdout)
            self.assertIn("migrate 1.1.0 -> 1.2.0", result.stdout)
            self.assertIn("migrate 1.2.0 -> 1.3.0", result.stdout)
            self.assertEqual(json.loads((target / ".context/capsule.json").read_text())["version"], "1.3.0")

    def test_compactness_warning_is_non_fatal(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            target.mkdir()
            self.assertEqual(self.run_cli("install", "--target", str(target), "--repository", "owner/repo").returncode, 0)
            (target / ".context/current/state.md").write_text("x" * 13000)
            result = self.run_cli("audit", "--target", str(target))
            self.assertEqual(result.returncode, 0)
            self.assertIn("compact resolved/history material", result.stdout)

    def test_expected_head_cas_guard(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            target.mkdir()
            subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=target, check=True)
            (target / "README.md").write_text("x\n")
            subprocess.run(["git", "add", "."], cwd=target, check=True)
            subprocess.run(["git", "commit", "-m", "init"], cwd=target, check=True, capture_output=True)
            result = self.run_cli(
                "install", "--target", str(target), "--repository", "owner/repo",
                "--expected-head", "deadbeef",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CAS mismatch", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
