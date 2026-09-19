import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "installer" / "capsulectl.py"


def run(*args: str) -> subprocess.CompletedProcess:
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
        ".context/project/goals.md": "# Project goals\n\nDeliver deterministic repository-local project continuity.\n",
        ".context/project/architecture.md": "# Project architecture\n\nThe repository is the durable authority; runtime state is separate.\n",
        ".context/project/constraints.md": "# Project constraints\n\nPreserve project memory and never export it to Core.\n",
        ".context/current/state.md": "# Current state\n\nThe v1.3 capsule is installed and reconciled.\n",
        ".context/current/blockers.md": "# Current blockers\n\nNo known blockers.\n",
        ".context/current/next.md": "# Next actions\n\nContinue the requested implementation task.\n",
        ".context/handoffs/latest.md": "# Latest handoff\n\nInstallation and reconciliation completed; continue from current state.\n",
    }
    for rel, text in values.items():
        (target / rel).write_text(text, encoding="utf-8")


class RuntimeReadinessTests(unittest.TestCase):
    def test_install_is_structurally_valid_but_not_ready(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            init_repo(target)
            result = run(
                "install",
                "--target",
                str(target),
                "--repository",
                "owner/repo",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            audit = run("audit", "--target", str(target), "--ready")
            self.assertEqual(audit.returncode, 2, audit.stdout + audit.stderr)
            self.assertIn("CAPSULE_TODO", (target / ".context/project/identity.md").read_text())
            resume = json.loads((target / ".context/resume.json").read_text())
            self.assertEqual(resume["status"], "draft")

    def test_ready_checkpoint_survives_context_only_commit_and_detects_code_change(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            init_repo(target)
            installed = run(
                "install",
                "--target",
                str(target),
                "--repository",
                "owner/repo",
            )
            self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
            commit_all(target, "install capsule")

            fill_required_context(target)
            checkpoint = run(
                "checkpoint",
                "--target",
                str(target),
                "--summary",
                "Fixture capsule reconciled with repository evidence.",
                "--next-action",
                "Continue implementation from the recorded current state.",
                "--ready",
            )
            self.assertEqual(
                checkpoint.returncode,
                0,
                checkpoint.stdout + checkpoint.stderr,
            )
            commit_all(target, "ready context checkpoint")

            local_runtime = target / ".context/tools/capsule_runtime.py"
            ready = subprocess.run(
                [sys.executable, str(local_runtime), "check", "--ready"],
                cwd=target,
                text=True,
                capture_output=True,
            )
            self.assertEqual(ready.returncode, 0, ready.stdout + ready.stderr)

            recovery = subprocess.run(
                [
                    sys.executable,
                    str(local_runtime),
                    "resume",
                    "--task",
                    "continue implementation",
                ],
                cwd=target,
                text=True,
                capture_output=True,
            )
            self.assertEqual(
                recovery.returncode,
                0,
                recovery.stdout + recovery.stderr,
            )
            self.assertIn("# Repository recovery pack", recovery.stdout)
            self.assertIn("Fixture capsule reconciled", recovery.stdout)

            (target / "implementation.txt").write_text("changed\n", encoding="utf-8")
            commit_all(target, "implementation change")
            stale = subprocess.run(
                [sys.executable, str(local_runtime), "check", "--ready"],
                cwd=target,
                text=True,
                capture_output=True,
            )
            self.assertEqual(stale.returncode, 2, stale.stdout + stale.stderr)
            self.assertIn("implementation changed after checkpoint", stale.stdout)

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

            installed = run(
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
            blocked = run(
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

            accepted = run(
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

    def test_schema_validation_rejects_semver_lookalike(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            init_repo(target)
            installed = run(
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

            checked = run("validate", "--target", str(target))
            self.assertEqual(checked.returncode, 1)
            self.assertIn("invalid string format", checked.stdout)


if __name__ == "__main__":
    unittest.main()
