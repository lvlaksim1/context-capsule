#!/usr/bin/env python3
"""Context Capsule Core installer, validator, adopter, repairer, and upgrader.

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
    Path("AGENTS.md"): TEMPLATES / "AGENTS.md",
    Path(".context/ENTRYPOINT.md"): TEMPLATES / ".context/ENTRYPOINT.md",
    Path(".context/protocol.md"): TEMPLATES / ".context/protocol.md",
}
PROJECT_SEED_FILES = {
    Path(".context/current/state.md"): TEMPLATES / ".context/current/state.md",
    Path(".context/rules/project-rules.md"): TEMPLATES / ".context/rules/project-rules.md",
    Path(".context/decisions/README.md"): TEMPLATES / ".context/decisions/README.md",
    Path(".context/handoffs/latest.md"): TEMPLATES / ".context/handoffs/latest.md",
    Path(".context/dialogues/README.md"): TEMPLATES / ".context/dialogues/README.md",
    Path(".context/history/README.md"): TEMPLATES / ".context/history/README.md",
}


def repo_root(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.exists() or not path.is_dir():
        raise SystemExit(f"target does not exist or is not a directory: {path}")
    return path


def valid_repository(value: str) -> bool:
    return isinstance(value, str) and value.count("/") == 1 and not value.startswith("/") and not value.endswith("/")


def metadata_path(target: Path) -> Path:
    return target / ".context" / "capsule.json"


def manifest_path(target: Path) -> Path:
    return target / ".context" / "manifest.json"


def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}")
    if not isinstance(value, dict):
        raise SystemExit(f"JSON root must be an object: {path}")
    return value


def read_metadata(target: Path) -> dict | None:
    return read_json(metadata_path(target))


def read_manifest(target: Path) -> dict | None:
    return read_json(manifest_path(target))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_metadata(target: Path, repository: str, version: str = VERSION, adopted_from: str | None = None) -> None:
    previous = read_metadata(target) or {}
    payload = {
        "schema": "context-capsule",
        "version": version,
        "source": SOURCE,
        "installed_at": previous.get("installed_at") or dt.date.today().isoformat(),
        "repository": repository,
        "update_policy": "manual",
    }
    if adopted_from:
        payload["adopted_from"] = adopted_from
    elif previous.get("adopted_from"):
        payload["adopted_from"] = previous["adopted_from"]
    write_json(metadata_path(target), payload)


def copy_if_missing(source: Path, destination: Path) -> bool:
    if destination.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    return True


def md_files(relative_dir: Path, target: Path, include_readme: bool = False) -> list[str]:
    root = target / relative_dir
    if not root.exists():
        return []
    result = []
    for path in sorted(root.rglob("*.md")):
        if not include_readme and path.name.lower() == "readme.md":
            continue
        result.append(str(path.relative_to(target)).replace("\\", "/"))
    return result


def existing_rule_paths(target: Path, legacy: dict | None = None) -> list[str]:
    if legacy:
        rules = legacy.get("rules")
        if isinstance(rules, list):
            found = [r for r in rules if isinstance(r, str) and (target / r).exists()]
            if found:
                return found
    candidates = md_files(Path(".context/rules"), target)
    return [p for p in candidates if not p.endswith("/README.md")]


def first_existing(target: Path, candidates: list[str], fallback: str) -> str:
    for candidate in candidates:
        if candidate and (target / candidate).exists():
            return candidate
    return fallback


def build_manifest(target: Path, repository: str, branch: str, legacy: dict | None = None) -> dict:
    legacy = dict(legacy or {})
    legacy_rules = existing_rule_paths(target, legacy)
    rules = legacy_rules or [".context/rules/project-rules.md"]
    current_state = first_existing(
        target,
        [legacy.get("current_state", ""), ".context/current/state.md"],
        ".context/current/state.md",
    )
    latest_handoff = first_existing(
        target,
        [legacy.get("latest_handoff", ""), ".context/handoffs/latest.md"],
        ".context/handoffs/latest.md",
    )
    protocol = first_existing(
        target,
        [legacy.get("protocol", ""), ".context/protocol.md"],
        ".context/protocol.md",
    )
    manifest = legacy
    manifest.update({
        "schema": "context-capsule-manifest",
        "schema_version": 1,
        "repository": repository,
        "authoritative_branch": legacy.get("authoritative_branch") or branch,
        "entrypoint": ".context/ENTRYPOINT.md",
        "capsule_metadata": ".context/capsule.json",
        "latest_handoff": latest_handoff,
        "current_state": current_state,
        "protocol": protocol,
        "rules": rules,
        "decisions": md_files(Path(".context/decisions"), target),
        "dialogues": md_files(Path(".context/dialogues"), target),
        "history": md_files(Path(".context/history"), target),
        "updated_at": dt.date.today().isoformat(),
    })
    return manifest


def write_manifest(target: Path, repository: str, branch: str, preserve_legacy: bool = True) -> None:
    legacy = read_manifest(target) if preserve_legacy else None
    write_json(manifest_path(target), build_manifest(target, repository, branch, legacy))


def install(args: argparse.Namespace) -> int:
    target = repo_root(args.target)
    if read_metadata(target) is not None:
        print("Context Capsule is already installed; use validate/upgrade/repair.")
        return 2
    if (target / "AI_CONTEXT.md").exists() or (target / ".context").exists():
        print("Existing AI_CONTEXT.md or .context/ found without capsule metadata; use adopt for a legacy capsule.")
        return 2
    if not valid_repository(args.repository):
        raise SystemExit("--repository must be in owner/name form")
    created = []
    for rel, source in {**SYSTEM_FILES, **PROJECT_SEED_FILES}.items():
        if copy_if_missing(source, target / rel):
            created.append(str(rel))
    write_metadata(target, args.repository)
    write_manifest(target, args.repository, args.branch, preserve_legacy=False)
    created.extend([".context/capsule.json", ".context/manifest.json"])
    print(f"Installed Context Capsule {VERSION} into {args.repository}")
    for item in created:
        print(f"  + {item}")
    return validate_target(target, quiet=False)


def adopt(args: argparse.Namespace) -> int:
    target = repo_root(args.target)
    if read_metadata(target) is not None:
        print("This repository already has capsule metadata; use validate/upgrade/repair.")
        return 2
    if not (target / ".context").exists():
        print("No legacy .context/ found; use install for a new capsule.")
        return 2
    if not valid_repository(args.repository):
        raise SystemExit("--repository must be in owner/name form")
    legacy_manifest = read_manifest(target)
    created = []
    for rel, source in SYSTEM_FILES.items():
        if copy_if_missing(source, target / rel):
            created.append(str(rel))
    for rel, source in PROJECT_SEED_FILES.items():
        category = rel.parts[1] if len(rel.parts) > 2 else None
        if category and (target / ".context" / category).exists() and any((target / ".context" / category).iterdir()):
            continue
        if copy_if_missing(source, target / rel):
            created.append(str(rel))
    write_metadata(target, args.repository, adopted_from="legacy")
    write_manifest(target, args.repository, args.branch, preserve_legacy=True)
    print(f"Adopted legacy capsule as Context Capsule {VERSION} in {args.repository}")
    for item in created:
        print(f"  + {item}")
    print("  + .context/capsule.json")
    print("  ~ .context/manifest.json (preserved and enriched when present)")
    return validate_target(target, quiet=False)


def validate_references(target: Path, manifest: dict, errors: list[str]) -> None:
    scalar_paths = ["entrypoint", "capsule_metadata", "latest_handoff", "current_state", "protocol"]
    for key in scalar_paths:
        value = manifest.get(key)
        if not isinstance(value, str) or not value:
            errors.append(f"manifest.json: missing {key}")
        elif not (target / value).exists():
            errors.append(f"manifest.json: referenced {key} does not exist: {value}")
    for key in ["rules", "decisions", "dialogues", "history"]:
        value = manifest.get(key)
        if not isinstance(value, list):
            errors.append(f"manifest.json: {key} must be a list")
            continue
        for item in value:
            if not isinstance(item, str) or not (target / item).exists():
                errors.append(f"manifest.json: missing referenced {key} item: {item}")


def validate_target(target: Path, quiet: bool = False) -> int:
    errors: list[str] = []
    warnings: list[str] = []
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
        if not valid_repository(meta.get("repository")):
            errors.append("capsule.json: repository must be owner/name")
    for rel in SYSTEM_FILES:
        if not (target / rel).exists():
            errors.append(f"missing system file: {rel}")
    manifest = read_manifest(target)
    if manifest is None:
        errors.append("missing .context/manifest.json")
    else:
        if manifest.get("schema") != "context-capsule-manifest":
            errors.append("manifest.json: invalid schema")
        branch = manifest.get("authoritative_branch")
        if not isinstance(branch, str) or not branch:
            errors.append("manifest.json: authoritative_branch is required")
        validate_references(target, manifest, errors)
        if meta and manifest.get("repository") != meta.get("repository"):
            errors.append("manifest.json repository does not match capsule.json")
        if not manifest.get("rules"):
            warnings.append("manifest.json: no project rules are indexed yet")
    if errors:
        print("Context Capsule validation: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    if not quiet:
        print("Context Capsule validation: OK")
        for warning in warnings:
            print(f"  ! {warning}")
    return 0


def validate(args: argparse.Namespace) -> int:
    return validate_target(repo_root(args.target))


def repair(args: argparse.Namespace) -> int:
    target = repo_root(args.target)
    meta = read_metadata(target)
    if meta is None:
        print("No installed capsule metadata found; use install or adopt instead of repair.")
        return 2
    repaired = []
    for rel, source in SYSTEM_FILES.items():
        if copy_if_missing(source, target / rel):
            repaired.append(str(rel))
    manifest = read_manifest(target)
    if manifest is None:
        branch = args.branch
        write_manifest(target, meta["repository"], branch, preserve_legacy=False)
        repaired.append(".context/manifest.json")
    else:
        write_manifest(target, meta["repository"], manifest.get("authoritative_branch") or args.branch, preserve_legacy=True)
    for item in repaired:
        print(f"  + restored {item}")
    if not repaired:
        print("No missing system files found; manifest index refreshed.")
    return validate_target(target)


V1_0_SYSTEM_CONTENT = {
    Path("AI_CONTEXT.md"): """# AI Context

This repository uses Context Capsule.

Start recovery at:

`.context/ENTRYPOINT.md`

The complete project context is stored in this repository. Do not look for a central copy of project context in Context Capsule Core.
""",
    Path(".context/ENTRYPOINT.md"): """# Context Capsule entrypoint

Read in this order:

1. `.context/capsule.json`
2. `.context/rules/project-rules.md`
3. `.context/current/state.md`
4. `.context/decisions/`
5. `.context/handoffs/latest.md`
6. `.context/history/` only when deeper history is required

Then verify the recovered state against the repository at the current commit.

If repository facts are newer than the capsule, treat repository facts as authoritative and update the capsule before continuing substantial work.

Never send or synchronize project context back to Context Capsule Core.
""",
}


def replace_if_canonical_v1(target: Path, rel: Path, new_source: Path) -> bool:
    destination = target / rel
    old = V1_0_SYSTEM_CONTENT.get(rel)
    if old is None or not destination.exists():
        return False
    if destination.read_text(encoding="utf-8") != old:
        return False
    shutil.copyfile(new_source, destination)
    return True


def migrate_1_0_to_1_1(target: Path, meta: dict, branch: str) -> None:
    for rel, source in SYSTEM_FILES.items():
        if not replace_if_canonical_v1(target, rel, source):
            copy_if_missing(source, target / rel)
    for rel, source in PROJECT_SEED_FILES.items():
        copy_if_missing(source, target / rel)
    write_manifest(target, meta["repository"], branch, preserve_legacy=True)
    write_metadata(target, meta["repository"], version=VERSION)


def upgrade(args: argparse.Namespace) -> int:
    target = repo_root(args.target)
    meta = read_metadata(target)
    if meta is None:
        print("No installed capsule metadata found; use install or adopt.")
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
    operation = migration.get("operation")
    if operation == "builtin:1.0.0-to-1.1.0":
        migrate_1_0_to_1_1(target, meta, args.branch)
        print(f"Upgraded Context Capsule {installed} -> {VERSION}")
        return validate_target(target)
    print(f"Unsupported migration operation: {operation}")
    return 4


def add_common_target(parser: argparse.ArgumentParser, branch: bool = False) -> None:
    parser.add_argument("--target", required=True)
    if branch:
        parser.add_argument("--branch", default="main", help="authoritative branch (default: main)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="capsulectl", description="Context Capsule lifecycle tool")
    sub = parser.add_subparsers(dest="command", required=True)

    p_install = sub.add_parser("install", help="install a new capsule into a clean target repository")
    add_common_target(p_install, branch=True)
    p_install.add_argument("--repository", required=True, help="target repository in owner/name form")
    p_install.set_defaults(func=install)

    p_adopt = sub.add_parser("adopt", help="adopt an existing legacy .context/ without overwriting project memory")
    add_common_target(p_adopt, branch=True)
    p_adopt.add_argument("--repository", required=True, help="target repository in owner/name form")
    p_adopt.set_defaults(func=adopt)

    p_validate = sub.add_parser("validate", help="validate an installed capsule and manifest references")
    add_common_target(p_validate)
    p_validate.set_defaults(func=validate)

    p_repair = sub.add_parser("repair", help="restore missing system structure and refresh the manifest index")
    add_common_target(p_repair, branch=True)
    p_repair.set_defaults(func=repair)

    p_upgrade = sub.add_parser("upgrade", help="upgrade using an explicit declared migration")
    add_common_target(p_upgrade, branch=True)
    p_upgrade.set_defaults(func=upgrade)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
