import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from installer import storage

CLI = ROOT / "installer" / "capsulectl.py"


def git(target: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=target,
        text=True,
        capture_output=True,
        check=check,
    )


def init_repo(target: Path, branch: str = "main") -> None:
    target.mkdir(parents=True, exist_ok=True)
    git(target, "init", "-b", branch)
    git(target, "config", "user.email", "test@example.com")
    git(target, "config", "user.name", "Context Capsule Test")
    (target / ".anchor").write_text("fixture\n", encoding="utf-8")
    commit_all(target, "initial fixture")


def commit_all(target: Path, message: str) -> None:
    git(target, "add", "-A")
    status = git(target, "status", "--porcelain").stdout.strip()
    if status:
        git(target, "commit", "-m", message)


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        text=True,
        capture_output=True,
    )


class HardeningTests(unittest.TestCase):
    def test_wrong_authoritative_branch_refuses_without_writes(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            init_repo(target)
            result = run_cli(
                "install",
                "--target",
                str(target),
                "--repository",
                "owner/repo",
                "--branch",
                "other",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("wrong checkout branch", result.stderr)
            self.assertFalse((target / ".context").exists())
            self.assertFalse((target / "AI_CONTEXT.md").exists())

    def test_malformed_legacy_manifest_leaves_no_partial_adoption(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            init_repo(target)
            (target / ".context").mkdir()
            (target / ".context/manifest.json").write_text(
                "{ definitely not json",
                encoding="utf-8",
            )
            (target / ".context/current").mkdir()
            (target / ".context/current/state.md").write_text(
                "legacy state\n",
                encoding="utf-8",
            )
            commit_all(target, "legacy fixture")

            result = run_cli(
                "adopt",
                "--target",
                str(target),
                "--repository",
                "owner/repo",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((target / ".context/capsule.json").exists())
            self.assertFalse((target / "AI_CONTEXT.md").exists())
            self.assertFalse((target / "AGENTS.md").exists())
            self.assertEqual(
                (target / ".context/manifest.json").read_text(encoding="utf-8"),
                "{ definitely not json",
            )

    def test_repair_preserves_unknown_nested_fields_and_external_index(self):
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

            notes = target / "notes"
            notes.mkdir()
            (notes / "decision.md").write_text("external decision\n", encoding="utf-8")
            manifest_path = target / ".context/manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["custom_top"] = {"keep": 1}
            manifest["project"]["custom_project"] = "keep-project"
            manifest["current"]["custom_current"] = "keep-current"
            manifest["runtime"]["custom_runtime"] = {"keep": True}
            manifest["sync_policy"]["custom_sync"] = "keep-sync"
            manifest["decisions"].append("notes/decision.md")
            manifest_path.write_text(
                json.dumps(manifest, indent=2) + "\n",
                encoding="utf-8",
            )
            commit_all(target, "custom semantic navigation")

            repaired = run_cli("repair", "--target", str(target))
            self.assertEqual(repaired.returncode, 0, repaired.stdout + repaired.stderr)
            updated = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(updated["custom_top"], {"keep": 1})
            self.assertEqual(updated["project"]["custom_project"], "keep-project")
            self.assertEqual(updated["current"]["custom_current"], "keep-current")
            self.assertEqual(updated["runtime"]["custom_runtime"], {"keep": True})
            self.assertEqual(updated["sync_policy"]["custom_sync"], "keep-sync")
            self.assertIn("notes/decision.md", updated["decisions"])

    def test_dirty_context_is_refused_without_overwrite(self):
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

            state = target / ".context/current/state.md"
            state.write_text("UNCOMMITTED USER STATE\n", encoding="utf-8")
            repaired = run_cli("repair", "--target", str(target))
            self.assertNotEqual(repaired.returncode, 0)
            self.assertIn("uncommitted changes", repaired.stderr)
            self.assertEqual(
                state.read_text(encoding="utf-8"),
                "UNCOMMITTED USER STATE\n",
            )

    @unittest.skipIf(os.name == "nt", "symlink creation requires elevated Windows policy")
    def test_symlink_escape_is_rejected_before_adoption(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "repo"
            outside = root / "outside"
            init_repo(target)
            outside.mkdir()
            (outside / "secret.md").write_text("outside\n", encoding="utf-8")
            (target / ".context").mkdir()
            (target / ".context/manifest.json").write_text("{}\n", encoding="utf-8")
            os.symlink(outside / "secret.md", target / ".context/escape.md")
            commit_all(target, "unsafe legacy fixture")

            result = run_cli(
                "adopt",
                "--target",
                str(target),
                "--repository",
                "owner/repo",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("symlink is not allowed", result.stderr)
            self.assertFalse((target / ".context/capsule.json").exists())

    def test_validate_rejects_manifest_path_traversal(self):
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

            manifest_path = target / ".context/manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["project"]["identity"] = "../outside.md"
            manifest_path.write_text(
                json.dumps(manifest, indent=2) + "\n",
                encoding="utf-8",
            )

            checked = run_cli("validate", "--target", str(target))
            self.assertNotEqual(checked.returncode, 0)
            self.assertIn("unsafe project.identity", checked.stdout)

    def test_transaction_detects_edit_after_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            init_repo(target)
            (target / ".context").mkdir()
            tracked = target / ".context/state.md"
            tracked.write_text("before\n", encoding="utf-8")
            commit_all(target, "context fixture")

            with storage.locked(target) as gitdir:
                storage.recover(target, gitdir)
                before = storage.inventory(target)
                head = storage.git(target, "rev-parse", "HEAD")
                branch = storage.git(target, "branch", "--show-current")
                after = dict(before)
                after[".context/state.md"] = b"planned\n"

                tracked.write_text("concurrent\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "repository changed"):
                    storage.apply(target, gitdir, before, after, head, branch)

            self.assertEqual(tracked.read_text(encoding="utf-8"), "concurrent\n")

    def test_recover_restores_interrupted_prepared_transaction(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            init_repo(target)
            (target / ".context").mkdir()
            tracked = target / ".context/state.md"
            tracked.write_text("before\n", encoding="utf-8")
            commit_all(target, "context fixture")

            with storage.locked(target) as gitdir:
                before = tracked.read_bytes()
                after = b"after crash\n"
                journal = {
                    "root": str(target.resolve()),
                    "state": "prepared",
                    "changes": [
                        {
                            "path": ".context/state.md",
                            "before": __import__("base64").b64encode(before).decode("ascii"),
                            "before_sha256": storage.digest(before),
                            "after_sha256": storage.digest(after),
                        }
                    ],
                    "created_dirs": [],
                }
                storage._save_journal(gitdir, journal)
                storage.atomic_write(target, ".context/state.md", after)

            self.assertEqual(tracked.read_bytes(), b"after crash\n")
            with storage.locked(target) as gitdir:
                recovered = storage.recover(target, gitdir)
                self.assertTrue(recovered)
            self.assertEqual(tracked.read_bytes(), before)
            self.assertFalse(
                (gitdir / "context-capsule-transaction.json").exists()
            )

    def test_transaction_rolls_back_after_mid_apply_failure(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "repo"
            init_repo(target)
            with storage.locked(target) as gitdir:
                storage.recover(target, gitdir)
                before = storage.inventory(target)
                head = storage.git(target, "rev-parse", "HEAD")
                branch = storage.git(target, "branch", "--show-current")
                after = dict(before)
                after[".context/a.md"] = b"A\n"
                after[".context/b.md"] = b"B\n"

                original = storage.atomic_write
                target_writes = {"count": 0}

                def flaky(root: Path, rel: str, data: bytes):
                    if root.resolve() == target.resolve():
                        target_writes["count"] += 1
                        if target_writes["count"] == 2:
                            raise OSError("simulated write failure")
                    return original(root, rel, data)

                with mock.patch.object(storage, "atomic_write", side_effect=flaky):
                    with self.assertRaisesRegex(OSError, "simulated write failure"):
                        storage.apply(target, gitdir, before, after, head, branch)

                self.assertEqual(storage.inventory(target), before)
                self.assertFalse(
                    (gitdir / "context-capsule-transaction.json").exists()
                )


if __name__ == "__main__":
    unittest.main()
