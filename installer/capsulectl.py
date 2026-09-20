#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from installer.legacy import adopt_known_legacy_changes
from installer.model import (
    CapsuleModelError,
    VERSION,
    build_recovery_pack,
    clean_install_changes,
    readiness_snapshot,
    repair_changes,
    validate_snapshot,
)
from installer.safety import CapsuleSafetyError, confined_local_path, validate_core_commit

CORE_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = CORE_ROOT / "templates"


def target_root(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.exists() or not path.is_dir():
        raise SystemExit(f"target does not exist or is not a directory: {path}")
    return path


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise SystemExit(f"Context Capsule expected UTF-8 text at {path}") from exc


def load_snapshot(target: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for rel in ("AI_CONTEXT.md", "AGENTS.md"):
        path = target / rel
        if path.exists():
            if path.is_symlink():
                confined_local_path(target, rel)
            if path.is_file():
                files[rel] = _read_text(path)

    context = target / ".context"
    if context.exists():
        if context.is_symlink():
            confined_local_path(target, ".context")
        if not context.is_dir():
            raise SystemExit(".context exists but is not a directory")
        for path in sorted(context.rglob("*")):
            if path.is_symlink():
                rel = path.relative_to(target).as_posix()
                confined_local_path(target, rel)
            if path.is_file():
                rel = path.relative_to(target).as_posix()
                files[rel] = _read_text(path)

    manifest_text = files.get(".context/manifest.json")
    if manifest_text:
        try:
            manifest = json.loads(manifest_text)
        except Exception:
            manifest = None
        if isinstance(manifest, dict):
            candidates: list[str] = []
            for key in ("entrypoint", "protocol", "latest_handoff", "current_state"):
                value = manifest.get(key)
                if isinstance(value, str):
                    candidates.append(value)
            for section in ("project", "current"):
                value = manifest.get(section)
                if isinstance(value, dict):
                    candidates.extend(v for v in value.values() if isinstance(v, str))
            for section in ("rules", "decisions", "dialogues", "history"):
                value = manifest.get(section)
                if isinstance(value, list):
                    candidates.extend(v for v in value if isinstance(v, str))
            for rel in candidates:
                if rel in files:
                    continue
                try:
                    path = confined_local_path(target, rel)
                except CapsuleSafetyError as exc:
                    raise SystemExit(str(exc)) from exc
                if path.exists() and path.is_file():
                    files[rel] = _read_text(path)
    return files


def apply_local_changes(target: Path, changes: dict[str, str]) -> None:
    """Development/local helper. Canonical GitHub publication is single-commit, not this writer."""
    for rel, content in changes.items():
        path = confined_local_path(target, rel)
        if path.exists() and path.is_symlink():
            confined_local_path(target, rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".context-capsule.tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)


def infer_core_commit(explicit: str | None) -> str:
    if explicit:
        return validate_core_commit(explicit)
    try:
        sha = subprocess.run(
            ["git", "-C", str(CORE_ROOT), "rev-parse", "HEAD"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        return validate_core_commit(sha)
    except Exception as exc:
        raise SystemExit("--core-commit is required when Core is not running from a Git checkout") from exc


def actual_branch(target: Path) -> str | None:
    try:
        return subprocess.run(
            ["git", "-C", str(target), "branch", "--show-current"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip() or None
    except Exception:
        return None


def ensure_branch(target: Path, requested: str) -> None:
    actual = actual_branch(target)
    if actual and actual != requested:
        raise SystemExit(f"target checkout branch mismatch: requested {requested!r}, actual {actual!r}")


def cmd_install(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    ensure_branch(target, args.branch)
    files = load_snapshot(target)
    try:
        changes = clean_install_changes(
            files,
            TEMPLATES,
            args.repository,
            args.branch,
            infer_core_commit(args.core_commit),
        )
    except (CapsuleModelError, CapsuleSafetyError) as exc:
        print(f"Context Capsule install: FAIL\n  - {exc}")
        return 2
    apply_local_changes(target, changes)
    print(f"Context Capsule {VERSION} installed locally ({len(changes)} changed files).")
    print("Canonical GitHub installations must publish the same prepared snapshot as one commit.")
    return cmd_validate(argparse.Namespace(target=str(target)))


def cmd_adopt(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    ensure_branch(target, args.branch)
    files = load_snapshot(target)
    try:
        changes = adopt_known_legacy_changes(
            files,
            TEMPLATES,
            args.repository,
            args.branch,
            infer_core_commit(args.core_commit),
        )
    except (CapsuleModelError, CapsuleSafetyError) as exc:
        print(f"Context Capsule legacy adoption: FAIL\n  - {exc}")
        return 2
    apply_local_changes(target, changes)
    print(f"Known legacy capsule adopted locally ({len(changes)} changed files).")
    return cmd_validate(argparse.Namespace(target=str(target)))


def cmd_repair(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    ensure_branch(target, args.branch)
    files = load_snapshot(target)
    try:
        changes = repair_changes(
            files,
            TEMPLATES,
            repository=args.repository,
            branch=args.branch,
            core_commit=infer_core_commit(args.core_commit),
        )
    except (CapsuleModelError, CapsuleSafetyError) as exc:
        print(f"Context Capsule repair: FAIL\n  - {exc}")
        return 2
    apply_local_changes(target, changes)
    print(f"Context Capsule repair applied locally ({len(changes)} changed files).")
    return cmd_validate(argparse.Namespace(target=str(target)))


def cmd_validate(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    try:
        files = load_snapshot(target)
        errors = validate_snapshot(files)
    except (CapsuleModelError, CapsuleSafetyError, SystemExit) as exc:
        print(f"Context Capsule validation: FAIL\n  - {exc}")
        return 1
    if errors:
        print("Context Capsule validation: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Context Capsule validation: VALID")
    return 0


def cmd_ready(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    try:
        files = load_snapshot(target)
        ready, reasons = readiness_snapshot(files)
    except (CapsuleModelError, CapsuleSafetyError, SystemExit) as exc:
        print(f"Context Capsule readiness: NOT READY\n  - {exc}")
        return 1
    if not ready:
        print("Context Capsule readiness: NOT READY")
        for reason in reasons:
            print(f"  - {reason}")
        return 1
    print("Context Capsule readiness: READY")
    return 0


def cmd_recover(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    try:
        pack = build_recovery_pack(load_snapshot(target), max_chars=args.max_chars)
    except (CapsuleModelError, CapsuleSafetyError, SystemExit) as exc:
        print(f"Context Capsule recovery: FAIL\n  - {exc}")
        return 1
    sys.stdout.write(pack)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="capsulectl", description="Context Capsule lifecycle helper")
    sub = parser.add_subparsers(dest="command", required=True)

    install = sub.add_parser("install", help="local clean-install helper; GitHub publication is canonical")
    install.add_argument("--target", required=True)
    install.add_argument("--repository", required=True)
    install.add_argument("--branch", default="main")
    install.add_argument("--core-commit")
    install.set_defaults(func=cmd_install)

    adopt = sub.add_parser("adopt", help="temporary known-legacy adoption helper")
    adopt.add_argument("--target", required=True)
    adopt.add_argument("--repository", required=True)
    adopt.add_argument("--branch", required=True)
    adopt.add_argument("--core-commit")
    adopt.set_defaults(func=cmd_adopt)

    repair = sub.add_parser("repair", help="repair a v1.3 capsule without discarding manifest extensions")
    repair.add_argument("--target", required=True)
    repair.add_argument("--repository", required=True)
    repair.add_argument("--branch", required=True)
    repair.add_argument("--core-commit")
    repair.set_defaults(func=cmd_repair)

    validate = sub.add_parser("validate", help="check structural validity")
    validate.add_argument("--target", required=True)
    validate.set_defaults(func=cmd_validate)

    ready = sub.add_parser("ready", help="check fresh-chat recovery readiness")
    ready.add_argument("--target", required=True)
    ready.set_defaults(func=cmd_ready)

    recover = sub.add_parser("recover", help="emit a deterministic fresh-chat recovery pack")
    recover.add_argument("--target", required=True)
    recover.add_argument("--max-chars", type=int, default=30000)
    recover.set_defaults(func=cmd_recover)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
