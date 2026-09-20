"""GitHub-runner checkout storage helpers for Context Capsule.

Context Capsule is a GitHub-only service. These helpers operate on the ephemeral
repository checkout used by the GitHub workflow. Remote publication is a later
Git commit/push step, so local OS locking, crash journals and cross-platform
desktop recovery are intentionally out of scope.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CORE_ROOT = Path(__file__).resolve().parents[1]
if str(CORE_ROOT) not in sys.path:
    sys.path.insert(0, str(CORE_ROOT))

from runtime.contracts import safe_path

ROOT_FILES = ("AGENTS.md", "AI_CONTEXT.md")


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
    raise ValueError(
        f"lifecycle operation cannot mutate path outside capsule scope: {rel}"
    )


def inventory(root: Path) -> dict[str, bytes]:
    """Return the capsule/discovery snapshot from the GitHub workflow checkout."""
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
            if path.is_dir():
                continue
            rel = path.relative_to(root).as_posix()
            safe_path(root, rel)
            result[rel] = path.read_bytes()
    return result


def apply(
    root: Path,
    before: dict[str, bytes],
    after: dict[str, bytes],
    head: str,
    branch: str,
) -> None:
    """Apply a prevalidated plan to the ephemeral GitHub workflow checkout.

    The workflow must publish these changes with normal Git/GitHub concurrency
    protection. If this function fails, no remote repository state has changed.
    """
    root = root.resolve()

    for rel in before.keys() | after.keys():
        assert_mutable_path(rel)

    if inventory(root) != before:
        raise ValueError(
            "repository checkout changed while preparing the plan; no files written"
        )
    if git(root, "rev-parse", "HEAD", required=False) != head:
        raise ValueError(
            "repository HEAD changed while preparing the plan; no files written"
        )
    if git(root, "branch", "--show-current") != branch:
        raise ValueError(
            "repository branch changed while preparing the plan; no files written"
        )

    for rel in sorted(before.keys() | after.keys()):
        if before.get(rel) == after.get(rel):
            continue
        if rel not in after:
            raise ValueError("lifecycle operations cannot delete project files")

        path = safe_path(root, rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        safe_path(root, rel)
        path.write_bytes(after[rel])
