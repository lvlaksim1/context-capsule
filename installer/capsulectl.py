#!/usr/bin/env python3
"""Context Capsule Core installer/validator.

Standard-library only. Operates on a checked-out target repository.
It never sends target repository context anywhere.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
from pathlib import Path

CORE_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = CORE_ROOT / "templates"
VERSION = (CORE_ROOT / "VERSION").read_text(encoding="utf-8").strip()
SOURCE = (CORE_ROOT / "SOURCE_REPOSITORY").read_text(encoding="utf-8").strip()

SYSTEM_FILES = {
    Path("AI_CONTEXT.md"): TEMPLATES / "AI_CONTEXT.md",
    Path(".context/ENTRYPOINT.md"): TEMPLATES / ".context/ENTRYPOINT.md",
}
PROJECT_SEED_FILES = {
    Path(".context/current/state.md"): TEMPLATES / ".context/current/state.md",
    Path(".context/rules/project-rules.md"): TEMPLATES / ".context/rules/project-rules.md",
    Path(".context/decisions/README.md"): TEMPLATES / ".context/decisions/README.md",
    Path(".context/handoffs/latest.md"): TEMPLATES / ".context/handoffs/latest.md",
    Path(".context/history/README.md"): TEMPLATES / ".context/history/README.md",
}


def repo_root(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.exists() or not path.is_dir():
        raise SystemExit(f"target does not exist or is not a directory: {path}")
    return path


def metadata_path(target: Path) -> Path:
    return target / ".context" / "capsule.json"


def read_metadata(target: Path) -> dict | None:
    path = metadata_path(target)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"invalid capsule metadata: {exc}")


def write_metadata(target: Path, repository: str, version: str = VERSION) -> None:
    payload = {
        "schema": "context-capsule",
        "version": version,
        "source": SOURCE,
        "installed_at": dt.date.today().isoformat(),
        "repository": repository,
        "update_policy": "manual",
    }
    path = metadata_path(target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def copy_if_missing(source: Path, destination: Path) -> bool:
    if destination.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    return True


def install(args: argparse.Namespace) -> int:
    target = repo_root(args.target)
    if read_metadata(target) is not None:
        print("Context Capsule is already installed; use validate/upgrade/repair.")
        return 2
    if (target / "AI_CONTEXT.md").exists() or (target / ".context").exists():
        print("Existing AI_CONTEXT.md or .context/ found without capsule metadata; refusing implicit adoption.")
        return 2
    if "/" not in args.repository or args.repository.startswith("/") or args.repository.endswith("/"):
        raise SystemExit("--repository must be in owner/name form")
    created = []
    for rel, source in {**SYSTEM_FILES, **PROJECT_SEED_FILES}.items():
        if copy_if_missing(source, target / rel):
            created.append(str(rel))
    write_metadata(target, args.repository)
    created.append(".context/capsule.json")
    print(f"Installed Context Capsule {VERSION} into {args.repository}")
    for item in created:
        print(f"  + {item}")
    return validate_target(target, quiet=False)


def validate_target(target: Path, quiet: bool = False) -> int:
    errors: list[str] = []
    meta = read_metadata(target)
    if meta is None:
        errors.append("missing .context/capsule.json")
    else:
        if meta.get("schema") != "context-capsule":
            errors.append("capsule.json: invalid schema")
        version = meta.get("version")
        if not isinstance(version, str) or version.count(".") != 2:
            errors.append("capsule.json: invalid version")
        if meta.get("update_policy") != "manual":
            errors.append("capsule.json: update_policy must be manual")
        repository = meta.get("repository")
        if not isinstance(repository, str) or repository.count("/") != 1:
            errors.append("capsule.json: repository must be owner/name")
    required = list(SYSTEM_FILES) + list(PROJECT_SEED_FILES)
    for rel in required:
        if not (target / rel).exists():
            errors.append(f"missing required file: {rel}")
    if errors:
        print("Context Capsule validation: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    if not quiet:
        print("Context Capsule validation: OK")
    return 0


def validate(args: argparse.Namespace) -> int:
    return validate_target(repo_root(args.target))


def repair(args: argparse.Namespace) -> int:
    target = repo_root(args.target)
    meta = read_metadata(target)
    if meta is None:
        print("No installed capsule metadata found; use install instead of repair.")
        return 2
    repaired = []
    # Repair only missing files. Never overwrite project-owned context.
    for rel, source in SYSTEM_FILES.items():
        if copy_if_missing(source, target / rel):
            repaired.append(str(rel))
    for rel, source in PROJECT_SEED_FILES.items():
        if copy_if_missing(source, target / rel):
            repaired.append(str(rel))
    for item in repaired:
        print(f"  + restored {item}")
    if not repaired:
        print("No missing capsule files found.")
    return validate_target(target)


def upgrade(args: argparse.Namespace) -> int:
    target = repo_root(args.target)
    meta = read_metadata(target)
    if meta is None:
        print("No installed capsule metadata found; use install.")
        return 2
    installed = meta.get("version")
    if installed == VERSION:
        print(f"Already on Context Capsule {VERSION}.")
        return validate_target(target)
    registry = json.loads((CORE_ROOT / "migrations" / "registry.json").read_text(encoding="utf-8"))
    migration = next((m for m in registry.get("migrations", []) if m.get("from") == installed and m.get("to") == VERSION), None)
    if migration is None:
        print(f"No declared migration from {installed} to {VERSION}; refusing implicit upgrade.")
        return 3
    print("Migration execution is not implemented for this registry entry.")
    return 4


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="capsulectl", description="Context Capsule installer and validator")
    sub = parser.add_subparsers(dest="command", required=True)

    p_install = sub.add_parser("install", help="install a capsule into a target repository")
    p_install.add_argument("--target", required=True)
    p_install.add_argument("--repository", required=True, help="target repository in owner/name form")
    p_install.set_defaults(func=install)

    for name, func, help_text in [
        ("validate", validate, "validate an installed capsule"),
        ("repair", repair, "restore missing capsule structure without overwriting project context"),
        ("upgrade", upgrade, "upgrade using an explicit migration"),
    ]:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--target", required=True)
        p.set_defaults(func=func)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
