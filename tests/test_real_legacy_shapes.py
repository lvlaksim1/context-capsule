import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "installer" / "capsulectl.py"


def command(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        text=True,
        capture_output=True,
    )


def git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )


def create_repo(root: Path, branch: str = "main") -> None:
    root.mkdir(parents=True)
    git(root, "init", "-b", "main")
    git(root, "config", "user.email", "test@example.com")
    git(root, "config", "user.name", "Legacy Shape Test")
    (root / "README.md").write_text("# legacy fixture\n", encoding="utf-8")
    git(root, "add", ".")
    git(root, "commit", "-m", "initial")
    if branch != "main":
        git(root, "checkout", "-b", branch)


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def commit(root: Path, message: str) -> None:
    git(root, "add", "-A")
    git(root, "commit", "-m", message)


class RealLegacyShapeTests(unittest.TestCase):
    """Regression fixtures derived from the three real pre-Core capsules."""

    def test_fgis_fsa_il_shape_is_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            create_repo(root)
            manifest = {
                "schema_version": 1,
                "context_version": "1.0",
                "project_name": "FGIS FSA IL",
                "repository": "lvlaksim1/fgis-fsa-il",
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
                    "decisions_index": ".context/decisions/index.md",
                    "dialogues_index": ".context/dialogues/index.md",
                },
                "capsule_installer_version": "1.0",
                "installed_from_main_sha": "244f3cdaee05fec5a36adcb72f8c8da67513b661",
                "last_context_update": "2026-09-18T13:26:00Z",
                "last_session_id": "CHAT-20260918-132600-blank-indicator-id-audit",
            }
            write(root, ".context/manifest.json", json.dumps(manifest))
            for rel in (
                ".context/project/identity.md",
                ".context/project/goals.md",
                ".context/project/architecture.md",
                ".context/project/constraints.md",
                ".context/current/state.md",
                ".context/current/blockers.md",
                ".context/current/next.md",
                ".context/rules/user-rules.md",
                ".context/rules/development-rules.md",
                ".context/rules/ai-rules.md",
                ".context/decisions/index.md",
                ".context/dialogues/index.md",
                ".context/handoffs/latest.md",
            ):
                write(root, rel, f"# {rel}\n\nverified legacy content\n")
            write(root, ".context/ENTRYPOINT.md", "# legacy fgis entrypoint\n")
            write(root, "AGENTS.md", "# legacy fgis agents\n")
            write(root, "AI_CONTEXT.md", "# legacy fgis discovery\n")
            commit(root, "legacy FGIS capsule")

            result = command(
                "adopt",
                "--target",
                str(root),
                "--repository",
                "lvlaksim1/fgis-fsa-il",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            new = json.loads((root / ".context/manifest.json").read_text())
            self.assertEqual(new["project_name"], "FGIS FSA IL")
            self.assertEqual(new["last_session_id"], manifest["last_session_id"])
            self.assertEqual(
                new["rules"],
                [
                    ".context/rules/user-rules.md",
                    ".context/rules/development-rules.md",
                    ".context/rules/ai-rules.md",
                ],
            )
            self.assertTrue((root / ".context/decisions/index.md").exists())
            self.assertIn(
                "legacy fgis agents",
                (root / "AGENTS.md").read_text(),
            )

    def test_telegram_receiver_shape_is_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            create_repo(root)
            manifest = {
                "schema_version": 1,
                "project": "telegram-receiver",
                "repository": "lvlaksim1/telegram-receiver",
                "authoritative_branch": "main",
                "entrypoint": ".context/ENTRYPOINT.md",
                "latest_handoff": ".context/handoffs/latest.md",
                "current_state": ".context/current/state.md",
                "protocol": ".context/protocol.md",
                "rules": [".context/rules/project.md"],
                "decisions": [
                    ".context/decisions/2026-09-19-direct-fifo.md",
                    ".context/decisions/2026-09-20-checkpoint-recovery.md",
                ],
                "dialogues": [
                    ".context/dialogues/2026-09-19.md",
                    ".context/dialogues/2026-09-20.md",
                ],
                "deprecated_runtime_branch": "receiver-runtime",
                "updated_at": "2026-09-20",
            }
            write(root, ".context/manifest.json", json.dumps(manifest))
            write(root, ".context/ENTRYPOINT.md", "# telegram receiver legacy entry\n")
            write(root, ".context/protocol.md", "# protocol\n\nDirect FIFO semantics.\n")
            write(root, ".context/current/state.md", "# state\n\nDirect FIFO is active.\n")
            write(root, ".context/handoffs/latest.md", "# handoff\n\nContinue direct FIFO.\n")
            write(root, ".context/rules/project.md", "# rules\n\nNo GitHub queue in hot path.\n")
            for rel in manifest["decisions"] + manifest["dialogues"]:
                write(root, rel, f"# {Path(rel).stem}\n\nlegacy evidence\n")
            write(root, "AGENTS.md", "# telegram custom agents\n\nDo not reintroduce queue.\n")
            write(root, "AI_CONTEXT.md", "# telegram custom discovery\n")
            commit(root, "legacy telegram capsule")

            result = command(
                "adopt",
                "--target",
                str(root),
                "--repository",
                "lvlaksim1/telegram-receiver",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            new = json.loads((root / ".context/manifest.json").read_text())
            self.assertEqual(new["deprecated_runtime_branch"], "receiver-runtime")
            self.assertEqual(new["rules"], [".context/rules/project.md"])
            for rel in manifest["decisions"]:
                self.assertIn(rel, new["decisions"])
            for rel in manifest["dialogues"]:
                self.assertIn(rel, new["dialogues"])
            self.assertIn("Do not reintroduce queue", (root / "AGENTS.md").read_text())

    def test_ai_agent_lab_redirect_runtime_shape_is_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            create_repo(root, branch="work-webhook-test")
            manifest = {
                "schema_version": 1,
                "project_name": "AI Agent Lab",
                "repository": "lvlaksim1/ai-agent-lab",
                "default_branch": "main",
                "authoritative_context_branch": "work-webhook-test",
                "context_version": "1.0",
                "installed_from": "Project Context Capsule Installer v1.0",
                "last_context_update": "2026-09-19T12:59:13Z",
                "last_session_id": "CHAT-20260919-project-audit-p0-stabilization",
                "active_handoff": ".context/handoffs/latest.md",
                "bootstrap_entrypoint": ".context/ENTRYPOINT.md",
                "authoritative_files": {
                    "project_context": ".context/",
                    "live_runtime": ".agent/",
                    "interactive_manager": ".agent/management/interactive-bootstrap.md",
                },
                "installation_status": "complete",
            }
            write(root, ".context/manifest.json", json.dumps(manifest))
            for rel in (
                ".context/project/identity.md",
                ".context/project/goals.md",
                ".context/project/constraints.md",
                ".context/current/state.md",
                ".context/current/blockers.md",
                ".context/current/next.md",
                ".context/rules/user-rules.md",
                ".context/rules/development-rules.md",
                ".context/rules/ai-rules.md",
                ".context/handoffs/latest.md",
            ):
                write(root, rel, f"# {rel}\n\nlegacy agent-lab context\n")
            write(root, ".context/ENTRYPOINT.md", "# agent lab branch entry\n")
            write(root, ".context/protocol.md", "# protocol\n\n.context durable; .agent volatile.\n")
            write(root, ".agent/state.json", "{}\n")
            write(root, "AGENTS.md", "# agent lab custom agents\n")
            write(root, "AI_CONTEXT.md", "# agent lab custom discovery\n")
            commit(root, "legacy agent lab capsule")

            result = command(
                "adopt",
                "--target",
                str(root),
                "--repository",
                "lvlaksim1/ai-agent-lab",
                "--branch",
                "work-webhook-test",
                "--discovery-branch",
                "main",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            new = json.loads((root / ".context/manifest.json").read_text())
            self.assertEqual(new["authoritative_branch"], "work-webhook-test")
            self.assertEqual(new["discovery_branch"], "main")
            self.assertEqual(new["branch_mode"], "redirect")
            self.assertIn(".agent/", new["runtime"]["authoritative_paths"])
            self.assertTrue(new["runtime"]["volatile"])
            self.assertTrue(new["runtime"]["promote_semantic_changes_only"])
            self.assertEqual(new["installation_status"], "complete")
            self.assertEqual(
                new["authoritative_files"]["interactive_manager"],
                ".agent/management/interactive-bootstrap.md",
            )


if __name__ == "__main__":
    unittest.main()
