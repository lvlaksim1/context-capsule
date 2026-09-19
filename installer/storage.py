"""Local, cooperating-writer transactions. No target context leaves its repository."""
from __future__ import annotations

import base64
import contextlib
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from contracts import safe_path

ROOT_FILES = ("AGENTS.md", "AI_CONTEXT.md")


def git(root: Path, *args: str, required: bool = True) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if required and result.returncode:
        raise ValueError(f"Git {' '.join(args[:2])}: {result.stderr.strip()}")
    return result.stdout.strip() if result.returncode == 0 else ""


def inventory(root: Path) -> dict[str, bytes]:
    result = {}
    for rel in ROOT_FILES:
        path = safe_path(root, rel)
        if path.exists():
            result[rel] = safe_path(root, rel, exists=True).read_bytes()
    context = safe_path(root, ".context")
    if context.exists():
        if not context.is_dir():
            raise ValueError(".context must be a directory")
        for path in sorted(context.rglob("*")):
            rel = path.relative_to(root).as_posix()
            safe_path(root, rel)
            if path.is_file():
                result[rel] = path.read_bytes()
    return result


def digest(data: bytes | None) -> str | None:
    return hashlib.sha256(data).hexdigest() if data is not None else None


def atomic_write(root: Path, rel: str, data: bytes) -> None:
    path = safe_path(root, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".capsule-", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, mode)
        safe_path(root, rel)
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _journal_path(gitdir: Path) -> Path:
    path = gitdir / "context-capsule-transaction.json"
    if path.is_symlink():
        raise ValueError("unsafe transaction journal")
    return path


def _save_journal(gitdir: Path, payload: dict) -> None:
    # Journal lives in this target's Git metadata, never in Core.
    atomic_write(gitdir, "context-capsule-transaction.json", json.dumps(payload).encode())
    os.chmod(_journal_path(gitdir), 0o600)


def recover(root: Path, gitdir: Path) -> bool:
    journal = _journal_path(gitdir)
    if not journal.exists():
        return False
    data = json.loads(journal.read_text())
    if data.get("root") != str(root.resolve()):
        raise ValueError("transaction journal belongs to another worktree")
    if data.get("state") != "committed":
        # Check every operand BEFORE reverting any, so a concurrent edit is preserved.
        for item in data["changes"]:
            path = safe_path(root, item["path"])
            actual = digest(path.read_bytes()) if path.exists() else None
            if actual not in (item["before_sha256"], item["after_sha256"]):
                raise ValueError(f"recovery conflict in {item['path']}; journal retained for review")
        for item in reversed(data["changes"]):
            path = safe_path(root, item["path"])
            if item["before"] is None:
                path.unlink(missing_ok=True)
            else:
                atomic_write(root, item["path"], base64.b64decode(item["before"]))
        for rel in sorted(data.get("created_dirs", []), key=lambda p: len(Path(p).parts), reverse=True):
            try:
                safe_path(root, rel).rmdir()
            except (FileNotFoundError, OSError):
                pass
    journal.unlink()
    return True


@contextlib.contextmanager
def locked(root: Path):
    gitdir = Path(git(root, "rev-parse", "--absolute-git-dir"))
    lock = gitdir / "context-capsule.lock"
    if lock.is_symlink():
        raise ValueError("unsafe lock path")
    with lock.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise ValueError("another capsule operation holds the repository lock") from exc
        try:
            yield gitdir
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def apply(root: Path, gitdir: Path, before: dict[str, bytes], after: dict[str, bytes], head: str, branch: str) -> None:
    if inventory(root) != before or git(root, "rev-parse", "HEAD", required=False) != head or git(root, "branch", "--show-current") != branch:
        raise ValueError("repository changed while preparing the plan; no files written")
    changes = []
    directories = set()
    for rel in sorted(before.keys() | after.keys()):
        if before.get(rel) == after.get(rel):
            continue
        if rel not in after:
            raise ValueError("lifecycle operations cannot delete project files")
        path = safe_path(root, rel)
        parent = path.parent
        while parent != root and not parent.exists():
            directories.add(parent.relative_to(root).as_posix())
            parent = parent.parent
        changes.append({"path": rel, "before": base64.b64encode(before[rel]).decode() if rel in before else None,
                        "before_sha256": digest(before.get(rel)), "after_sha256": digest(after[rel])})
    if not changes:
        return
    journal = {"root": str(root.resolve()), "state": "prepared", "changes": changes, "created_dirs": sorted(directories)}
    _save_journal(gitdir, journal)
    try:
        for item in changes:
            rel = item["path"]
            actual = safe_path(root, rel)
            if digest(actual.read_bytes() if actual.exists() else None) != item["before_sha256"]:
                raise ValueError(f"concurrent edit in {rel}; refusing overwrite")
            atomic_write(root, rel, after[rel])
        journal["state"] = "committed"
        _save_journal(gitdir, journal)
    except BaseException:
        recover(root, gitdir)
        raise
    _journal_path(gitdir).unlink()
