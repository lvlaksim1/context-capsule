import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.capsule_runtime import inspect, recovery_pack

CLI = ROOT / "installer" / "capsulectl.py"
SCHEMAS = ROOT / "schemas"


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        text=True,
        capture_output=True,
    )


def git(target: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=target,
        text=True,
        capture_output=True,
        check=check,
    )


def init_repo(target: Path) -> None:
    target.mkdir(parents=True)
    git(target, "init", "-b", "main")
    git(target, "config", "user.email", "test@example.com")
    git(target, "config", "user.name", "Context Capsule Test")
    (target / "README.md").write_text("# Fixture\n", encoding="utf-8")
    commit_all(target, "initial")


def commit_all(target: Path, message: str) -> None:
    git(target, "add", "-A")
    if git(target, "status", "--porcelain").stdout.strip():
        git(target, "commit", "-m", message)


def fill_required_context(target: Path) -> None:
    values = {
        ".context/project/identity.md": "# Project identity\n\nFixture project owned by this repository.\n",
        ".context/project/goals.md": "# Project goals\n\nDeliver deterministic GitHub-hosted project continuity.\n",
        ".context/project/architecture.md": "# Project architecture\n\nGitHub repository is durable context authority.\n",
        ".context/project/constraints.md": "# Project constraints\n\nNo local Context Capsule runtime is required.\n",
        ".context/current/state.md": "# Current state\n\nThe v1.3 capsule is installed and reconciled.\n",
        ".context/current/blockers.md": "# Current blockers\n\nNo known blockers.\n",
        ".context/current/next.md": "# Next actions\n\nContinue the requested implementation task.\n",
        ".context/handoffs/latest.md": "# Latest handoff\n\nInstallation and reconciliation completed; continue from current state.\n",
    }
    for rel, text in values.items():
        (target / rel).write_text(text, encoding="utf-8")


class RuntimeReadinessTests(unittest.TestCase):
    def test_install_is_valid_but_not_ready_and_installs_no_runtime(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            init_repo(target)
            result = run_cli(
                "install",
                "--target",
                str(target),
                "--repository",
                "owner/repo",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((target / ".context/tools").exists())
            audit = run_cli("audit", "--target", str(target), "--ready")
            self.assertEqual(audit.returncode, 2, audit.stdout + audit.stderr)
            self.assertIn("CAPSULE_TODO", (target / ".context/project/identity.md").read_text())
            resume = json.loads((target / ".context/resume.json").read_text())
            self.assertEqual(resume["status"], "draft")

    def test_central_service_checks_ready_and_detects_implementation_change(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            init_repo(target)
            installed = run_cli(
                "install",
                "--target",
                str(target),
                "--repository",
                "owner/repo",
            )
            self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
            commit_all(target, "install capsule")

            fill_required_context(target)
            checkpoint = run_cli(
                "checkpoint",
                "--target",
                str(target),
                "--summary",
                "Fixture capsule reconciled with repository evidence.",
                "--next-action",
                "Continue implementation from the recorded current state.",
                "--ready",
            )
            self.assertEqual(checkpoint.returncode, 0, checkpoint.stdout + checkpoint.stderr)
            commit_all(target, "ready context checkpoint")

            ready = inspect(target, schemas=SCHEMAS)
            self.assertFalse(ready["errors"])
            self.assertFalse(ready["readiness"])

            pack = recovery_pack(target, task="continue implementation")
            self.assertIn("# Repository recovery pack", pack)
            self.assertIn("Fixture capsule reconciled", pack)

            (target / "implementation.txt").write_text("changed\n", encoding="utf-8")
            commit_all(target, "implementation change")
            stale = inspect(target, schemas=SCHEMAS)
            self.assertTrue(
                any(
                    "implementation changed after checkpoint" in item
                    for item in stale["readiness"]
                )
            )

    def test_custom_agents_is_preserved_and_requires_review(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            init_repo(target)
            custom = target / "AGENTS.md"
            custom.write_text(
                "# Existing project instructions\n\nNever remove this instruction.\n",
                encoding="utf-8",
            )
            commit_all(target, "project agent rules")

            installed = run_cli(
                "install",
                "--target",
                str(target),
                "--repository",
                "owner/repo",
            )
            self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
            agents = custom.read_text(encoding="utf-8")
            self.assertIn("Never remove this instruction.", agents)
            self.assertIn("context-capsule:begin", agents)
            resume = json.loads((target / ".context/resume.json").read_text())
            self.assertIn("AGENTS.md", resume["bootstrap_review"])

            commit_all(target, "install capsule")
            fill_required_context(target)
            blocked = run_cli(
                "checkpoint",
                "--target",
                str(target),
                "--summary",
                "Context reviewed.",
                "--next-action",
                "Continue.",
                "--ready",
            )
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("custom bootstrap still requires review", blocked.stderr)

            accepted = run_cli(
                "checkpoint",
                "--target",
                str(target),
                "--summary",
                "Context and preserved project instructions reviewed.",
                "--next-action",
                "Continue.",
                "--ready",
                "--clear-bootstrap-review",
            )
            self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)

    def test_known_v12_bootstrap_upgrades_without_false_review(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            init_repo(target)

            old_agents = """# Agent Instructions

Before substantial work, restore project context from `.context/ENTRYPOINT.md`.

Follow `.context/manifest.json` for the authoritative context branch and actual project-context paths. After recovery, reconcile stored context with live repository/CI/runtime evidence.

Do not copy volatile runtime state into durable context unless it changes project semantics.
Do not send project context to Context Capsule Core.
"""
            (target / "AGENTS.md").write_text(old_agents, encoding="utf-8")

            metadata = {
                "schema": "context-capsule",
                "version": "1.2.0",
                "source": "lvlaksim1/context-capsule",
                "installed_at": "2026-09-19",
                "repository": "owner/repo",
                "update_policy": "manual",
            }
            manifest = {
                "schema": "context-capsule-manifest",
                "schema_version": 2,
                "repository": "owner/repo",
                "authoritative_branch": "main",
                "discovery_branch": "main",
                "branch_mode": "single",
                "entrypoint": ".context/ENTRYPOINT.md",
                "capsule_metadata": ".context/capsule.json",
                "protocol": ".context/protocol.md",
                "latest_handoff": ".context/handoffs/latest.md",
                "project": {
                    "identity": ".context/project/identity.md",
                    "goals": ".context/project/goals.md",
                    "architecture": ".context/project/architecture.md",
                    "constraints": ".context/project/constraints.md",
                },
                "current": {
                    "state": ".context/current/state.md",
                    "blockers": ".context/current/blockers.md",
                    "next": ".context/current/next.md",
                },
                "current_state": ".context/current/state.md",
                "rules": [".context/rules/project-rules.md"],
                "decisions": [],
                "dialogues": [],
                "history": [],
                "runtime": {
                    "authoritative_paths": [],
                    "volatile": False,
                    "promote_semantic_changes_only": False,
                },
                "sync_policy": {
                    "semantic_only": True,
                    "volatile_runtime_excluded": True,
                    "cas_required_when_expected_head_supplied": True,
                },
                "updated_at": "2026-09-20",
            }
            (target / ".context").mkdir()
            (target / ".context/capsule.json").write_text(
                json.dumps(metadata), encoding="utf-8"
            )
            (target / ".context/manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            for rel in (
                ".context/project/identity.md",
                ".context/project/goals.md",
                ".context/project/architecture.md",
                ".context/project/constraints.md",
                ".context/current/state.md",
                ".context/current/blockers.md",
                ".context/current/next.md",
                ".context/rules/project-rules.md",
                ".context/handoffs/latest.md",
            ):
                path = target / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"# {rel}\n\nlegacy content\n", encoding="utf-8")
            commit_all(target, "v1.2 fixture")

            upgraded = run_cli("upgrade", "--target", str(target))
            self.assertEqual(upgraded.returncode, 0, upgraded.stdout + upgraded.stderr)
            resume = json.loads((target / ".context/resume.json").read_text())
            self.assertNotIn("AGENTS.md", resume["bootstrap_review"])
            self.assertFalse((target / ".context/tools").exists())

    def test_schema_validation_rejects_semver_lookalike(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            init_repo(target)
            installed = run_cli(
                "install",
                "--target",
                str(target),
                "--repository",
                "owner/repo",
            )
            self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
            metadata_path = target / ".context/capsule.json"
            metadata = json.loads(metadata_path.read_text())
            metadata["version"] = "abc.def.ghi"
            metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")

            checked = run_cli("validate", "--target", str(target))
            self.assertEqual(checked.returncode, 1)
            self.assertIn("invalid string format", checked.stdout)


if __name__ == "__main__":
    unittest.main()
