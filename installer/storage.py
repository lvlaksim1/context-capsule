"""Transactional storage for Context Capsule lifecycle mutations.

The transaction boundary covers files owned or indexed by the capsule:
AGENTS.md, AI_CONTEXT.md and .context/**. It protects cooperating writers,
detects concurrent edits, journals preimages in Git metadata, performs
same-directory atomic replacement, and can roll back interrupted operations.
"""
from __future__ import annotations

import base64
import contextlib
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CORE_ROOT = Path(__file__).resolve().parents[1]
if str(CORE_ROOT) not in sys.path:
    sys.path.insert(0, str(CORE_ROOT))

from runtime.contracts import safe_path

ROOT_FILES = ("AGENTS.md", "AI_CONTEXT.md")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def git(root: Path, *args: str, required: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
    )
    if required and result.returncode:
        message = result.stderr.strip() or result.stdout.strip()
        raise ValueError(f"Git {' '.join(args[:2])}: {message}")
    return result.stdout.strip() if result.returncode == 0 else ""


def assert_mutable_path(rel: str) -> None:
    if rel in ROOT_FILES:
        return
    if rel.startswith(".context/") and rel != ".context/":
        return
    raise ValueError(f"lifecycle operation cannot mutate path outside capsule scope: {rel}")


def inventory(root: Path) -> dict[str, bytes]:
    """Return a byte snapshot of every lifecycle-managed target file."""
    root = root.resolve()
    result: dict[str, bytes] = {}
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


def _fsync_directory(path: Path) -> None:
    """Best-effort durability barrier for directory entry changes."""
    if os.name == "nt":
        return
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write(root: Path, rel: str, data: bytes) -> None:
    """Replace one file atomically without following repository symlinks."""
    path = safe_path(root, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_path(root, rel)

    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent,
            prefix=".capsule-",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, mode)
        safe_path(root, rel)
        os.replace(temporary, path)
        temporary = None
        _fsync_directory(path.parent)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _journal_path(gitdir: Path) -> Path:
    path = gitdir / "context-capsule-transaction.json"
    if path.is_symlink():
        raise ValueError("unsafe transaction journal")
    return path


def _lock_path(gitdir: Path) -> Path:
    path = gitdir / "context-capsule.lock"
    if path.is_symlink():
        raise ValueError("unsafe lock path")
    return path


def _validate_sha(value: object, *, nullable: bool) -> bool:
    if value is None:
        return nullable
    return isinstance(value, str) and HEX64.fullmatch(value) is not None


def _validate_journal(payload: object, root: Path) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("invalid transaction journal root")
    if payload.get("root") != str(root.resolve()):
        raise ValueError("transaction journal belongs to another worktree")
    if payload.get("state") not in ("prepared", "committed"):
        raise ValueError("invalid transaction journal state")

    changes = payload.get("changes")
    created_dirs = payload.get("created_dirs", [])
    if not isinstance(changes, list) or not isinstance(created_dirs, list):
        raise ValueError("invalid transaction journal collections")

    for rel in created_dirs:
        if not isinstance(rel, str):
            raise ValueError("invalid transaction directory entry")
        assert_mutable_path(rel + "/placeholder")
        safe_path(root, rel)

    for item in changes:
        if not isinstance(item, dict):
            raise ValueError("invalid transaction change entry")
        rel = item.get("path")
        before = item.get("before")
        before_sha = item.get("before_sha256")
        after_sha = item.get("after_sha256")
        if not isinstance(rel, str):
            raise ValueError("invalid transaction path")
        assert_mutable_path(rel)
        safe_path(root, rel)
        if before is not None and not isinstance(before, str):
            raise ValueError(f"invalid journal preimage for {rel}")
        if not _validate_sha(before_sha, nullable=True) or not _validate_sha(after_sha, nullable=False):
            raise ValueError(f"invalid journal digest for {rel}")
        if before is None and before_sha is not None:
            raise ValueError(f"unexpected preimage digest for {rel}")
        if before is not None:
            try:
                decoded = base64.b64decode(before, validate=True)
            except Exception as exc:
                raise ValueError(f"invalid journal base64 for {rel}") from exc
            if digest(decoded) != before_sha:
                raise ValueError(f"journal preimage digest mismatch for {rel}")
    return payload


def _save_journal(gitdir: Path, payload: dict) -> None:
    # Journal lives in this target's Git metadata, never in Core or project context.
    atomic_write(
        gitdir,
        "context-capsule-transaction.json",
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8"),
    )
    os.chmod(_journal_path(gitdir), 0o600)


def recover(root: Path, gitdir: Path) -> bool:
    """Recover an interrupted cooperating-writer transaction.

    A prepared transaction is rolled back only when every changed file still
    matches either its before or after digest. An arbitrary concurrent edit
    causes recovery to stop and retain the journal for manual reconciliation.
    """
    root = root.resolve()
    gitdir = gitdir.resolve()
    journal = _journal_path(gitdir)
    if not journal.exists():
        return False
    if not journal.is_file():
        raise ValueError("transaction journal is not a regular file")

    try:
        payload = json.loads(journal.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError("invalid transaction journal JSON") from exc
    data = _validate_journal(payload, root)

    if data["state"] != "committed":
        for item in data["changes"]:
            path = safe_path(root, item["path"])
            actual = digest(path.read_bytes()) if path.exists() else None
            if actual not in (item["before_sha256"], item["after_sha256"]):
                raise ValueError(
                    f"recovery conflict in {item['path']}; journal retained for review"
                )

        for item in reversed(data["changes"]):
            path = safe_path(root, item["path"])
            if item["before"] is None:
                path.unlink(missing_ok=True)
                _fsync_directory(path.parent)
            else:
                atomic_write(
                    root,
                    item["path"],
                    base64.b64decode(item["before"], validate=True),
                )

        for rel in sorted(
            data.get("created_dirs", []),
            key=lambda value: len(Path(value).parts),
            reverse=True,
        ):
            try:
                safe_path(root, rel).rmdir()
            except (FileNotFoundError, OSError):
                pass

    journal.unlink()
    _fsync_directory(gitdir)
    return True


@contextlib.contextmanager
def locked(root: Path):
    """Acquire a repository-local OS lock stored in Git metadata."""
    gitdir_text = git(root, "rev-parse", "--absolute-git-dir")
    gitdir = Path(gitdir_text).resolve()
    lock = _lock_path(gitdir)
    lock.parent.mkdir(parents=True, exist_ok=True)

    with lock.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
            os.fsync(handle.fileno())
        handle.seek(0)

        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise ValueError(
                "another capsule operation holds the repository lock"
            ) from exc

        try:
            yield gitdir
        finally:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def apply(
    root: Path,
    gitdir: Path,
    before: dict[str, bytes],
    after: dict[str, bytes],
    head: str,
    branch: str,
) -> None:
    """Apply a complete mutation plan or restore its complete preimage."""
    root = root.resolve()
    gitdir = gitdir.resolve()
    for rel in before.keys() | after.keys():
        assert_mutable_path(rel)

    if (
        inventory(root) != before
        or git(root, "rev-parse", "HEAD", required=False) != head
        or git(root, "branch", "--show-current") != branch
    ):
        raise ValueError(
            "repository changed while preparing the plan; no files written"
        )

    changes: list[dict] = []
    directories: set[str] = set()
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

        changes.append(
            {
                "path": rel,
                "before": (
                    base64.b64encode(before[rel]).decode("ascii")
                    if rel in before
                    else None
                ),
                "before_sha256": digest(before.get(rel)),
                "after_sha256": digest(after[rel]),
            }
        )

    if not changes:
        return

    journal = {
        "root": str(root.resolve()),
        "state": "prepared",
        "changes": changes,
        "created_dirs": sorted(directories),
    }
    _save_journal(gitdir, journal)

    try:
        for item in changes:
            rel = item["path"]
            path = safe_path(root, rel)
            actual = digest(path.read_bytes()) if path.exists() else None
            if actual != item["before_sha256"]:
                raise ValueError(f"concurrent edit in {rel}; refusing overwrite")
            atomic_write(root, rel, after[rel])

        journal["state"] = "committed"
        _save_journal(gitdir, journal)
    except BaseException:
        recover(root, gitdir)
        raise

    _journal_path(gitdir).unlink()
    _fsync_directory(gitdir)
