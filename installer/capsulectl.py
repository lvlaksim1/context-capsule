#!/usr/bin/env python3
"""Context Capsule Core lifecycle tool.

Standard-library only. Operates on a checked-out target repository.
It never sends target repository context anywhere.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
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
    Path(".context/project/identity.md"): TEMPLATES / ".context/project/identity.md",
    Path(".context/project/goals.md"): TEMPLATES / ".context/project/goals.md",
    Path(".context/project/architecture.md"): TEMPLATES / ".context/project/architecture.md",
    Path(".context/project/constraints.md"): TEMPLATES / ".context/project/constraints.md",
    Path(".context/current/state.md"): TEMPLATES / ".context/current/state.md",
    Path(".context/current/blockers.md"): TEMPLATES / ".context/current/blockers.md",
    Path(".context/current/next.md"): TEMPLATES / ".context/current/next.md",
    Path(".context/rules/project-rules.md"): TEMPLATES / ".context/rules/project-rules.md",
    Path(".context/decisions/README.md"): TEMPLATES / ".context/decisions/README.md",
    Path(".context/handoffs/latest.md"): TEMPLATES / ".context/handoffs/latest.md",
    Path(".context/dialogues/README.md"): TEMPLATES / ".context/dialogues/README.md",
    Path(".context/history/README.md"): TEMPLATES / ".context/history/README.md",
}

COMPACT_WARN_BYTES = {
    "current.state": 12_000,
    "current.blockers": 8_000,
    "current.next": 8_000,
    "latest_handoff": 12_000,
}


def repo_root(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.exists() or not path.is_dir():
        raise SystemExit(f"target does not exist or is not a directory: {path}")
    return path


def valid_repository(value: object) -> bool:
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


def git_head(target: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(target), "rev-parse", "HEAD"],
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return None


def ensure_expected_head(target: Path, expected_head: str | None) -> None:
    if not expected_head:
        return
    actual = git_head(target)
    if actual is None:
        raise SystemExit("--expected-head was supplied, but target is not a readable Git worktree")
    if actual != expected_head:
        raise SystemExit(f"CAS mismatch: expected HEAD {expected_head}, actual HEAD {actual}")


def write_metadata(target: Path, repository: str, version: str, adopted_from: str | None = None) -> None:
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


def as_path(value: object) -> str:
    return value if isinstance(value, str) else ""


def first_existing(target: Path, candidates: list[str], fallback: str) -> str:
    for candidate in candidates:
        if candidate and (target / candidate).exists():
            return candidate
    return fallback


def legacy_authoritative_map(legacy: dict) -> dict:
    value = legacy.get("authoritative")
    return value if isinstance(value, dict) else {}


def existing_rule_paths(target: Path, legacy: dict) -> list[str]:
    rules = legacy.get("rules")
    if isinstance(rules, list):
        found = [r for r in rules if isinstance(r, str) and (target / r).exists()]
        if found:
            return found
    authoritative = legacy_authoritative_map(legacy)
    found = []
    for key in ("user_rules", "development_rules", "ai_rules", "project_rules"):
        value = authoritative.get(key)
        if isinstance(value, str) and (target / value).exists():
            found.append(value)
    if found:
        return found
    return md_files(Path(".context/rules"), target)


def legacy_project_paths(target: Path, legacy: dict) -> dict[str, str]:
    nested = legacy.get("project")
    if not isinstance(nested, dict):
        nested = {}
    authoritative = legacy_authoritative_map(legacy)
    return {
        "identity": first_existing(
            target,
            [as_path(nested.get("identity")), as_path(authoritative.get("identity")), ".context/project/identity.md"],
            ".context/project/identity.md",
        ),
        "goals": first_existing(
            target,
            [as_path(nested.get("goals")), as_path(authoritative.get("goals")), ".context/project/goals.md"],
            ".context/project/goals.md",
        ),
        "architecture": first_existing(
            target,
            [as_path(nested.get("architecture")), as_path(authoritative.get("architecture")), ".context/project/architecture.md"],
            ".context/project/architecture.md",
        ),
        "constraints": first_existing(
            target,
            [as_path(nested.get("constraints")), as_path(authoritative.get("constraints")), ".context/project/constraints.md"],
            ".context/project/constraints.md",
        ),
    }


def legacy_current_paths(target: Path, legacy: dict) -> dict[str, str]:
    nested = legacy.get("current")
    if not isinstance(nested, dict):
        nested = {}
    authoritative = legacy_authoritative_map(legacy)
    return {
        "state": first_existing(
            target,
            [as_path(nested.get("state")), as_path(legacy.get("current_state")), as_path(authoritative.get("current_state")), ".context/current/state.md"],
            ".context/current/state.md",
        ),
        "blockers": first_existing(
            target,
            [as_path(nested.get("blockers")), as_path(authoritative.get("blockers")), ".context/current/blockers.md"],
            ".context/current/blockers.md",
        ),
        "next": first_existing(
            target,
            [as_path(nested.get("next")), as_path(authoritative.get("next")), ".context/current/next.md"],
            ".context/current/next.md",
        ),
    }


def infer_runtime(target: Path, legacy: dict) -> dict:
    runtime = legacy.get("runtime")
    if isinstance(runtime, dict):
        result = dict(runtime)
    else:
        result = {}
    paths = result.get("authoritative_paths")
    if not isinstance(paths, list):
        paths = []
    files = legacy.get("authoritative_files")
    if isinstance(files, dict):
        live_runtime = files.get("live_runtime")
        if isinstance(live_runtime, str):
            paths.append(live_runtime.rstrip("/") + "/")
    if (target / ".agent").exists():
        paths.append(".agent/")
    paths = sorted(dict.fromkeys(p for p in paths if isinstance(p, str) and p))
    return {
        "authoritative_paths": paths,
        "volatile": bool(paths),
        "promote_semantic_changes_only": bool(paths),
    }


def infer_branches(legacy: dict, branch: str, discovery_branch: str | None) -> tuple[str, str, str]:
    authoritative = (
        as_path(legacy.get("authoritative_branch"))
        or as_path(legacy.get("authoritative_context_branch"))
        or branch
    )
    discovery = (
        discovery_branch
        or as_path(legacy.get("discovery_branch"))
        or as_path(legacy.get("default_branch"))
        or authoritative
    )
    mode = "redirect" if discovery != authoritative else "single"
    return authoritative, discovery, mode


def build_manifest(
    target: Path,
    repository: str,
    branch: str,
    discovery_branch: str | None = None,
    legacy: dict | None = None,
) -> dict:
    legacy = dict(legacy or {})
    authoritative_branch, discovered_branch, branch_mode = infer_branches(legacy, branch, discovery_branch)
    project = legacy_project_paths(target, legacy)
    current = legacy_current_paths(target, legacy)
    latest_handoff = first_existing(
        target,
        [as_path(legacy.get("latest_handoff")), as_path(legacy.get("active_handoff")), ".context/handoffs/latest.md"],
        ".context/handoffs/latest.md",
    )
    protocol = first_existing(
        target,
        [as_path(legacy.get("protocol")), ".context/protocol.md"],
        ".context/protocol.md",
    )
    manifest = legacy
    manifest.update({
        "schema": "context-capsule-manifest",
        "schema_version": 2,
        "repository": repository,
        "authoritative_branch": authoritative_branch,
        "discovery_branch": discovered_branch,
        "branch_mode": branch_mode,
        "entrypoint": ".context/ENTRYPOINT.md",
        "capsule_metadata": ".context/capsule.json",
        "protocol": protocol,
        "latest_handoff": latest_handoff,
        "project": project,
        "current": current,
        "current_state": current["state"],
        "rules": existing_rule_paths(target, legacy) or [".context/rules/project-rules.md"],
        "decisions": md_files(Path(".context/decisions"), target),
        "dialogues": md_files(Path(".context/dialogues"), target),
        "history": md_files(Path(".context/history"), target),
        "runtime": infer_runtime(target, legacy),
        "sync_policy": {
            "semantic_only": True,
            "volatile_runtime_excluded": True,
            "cas_required_when_expected_head_supplied": True,
        },
        "updated_at": dt.date.today().isoformat(),
    })
    return manifest


def write_manifest(
    target: Path,
    repository: str,
    branch: str,
    discovery_branch: str | None = None,
    preserve_legacy: bool = True,
) -> None:
    legacy = read_manifest(target) if preserve_legacy else None
    write_json(
        manifest_path(target),
        build_manifest(target, repository, branch, discovery_branch, legacy),
    )


def seed_project_files(target: Path, for_adoption: bool) -> list[str]:
    created = []
    for rel, source in PROJECT_SEED_FILES.items():
        if rel == Path(".context/rules/project-rules.md") and for_adoption:
            existing_rules = md_files(Path(".context/rules"), target)
            if existing_rules:
                continue
        if copy_if_missing(source, target / rel):
            created.append(str(rel))
    return created


def install(args: argparse.Namespace) -> int:
    target = repo_root(args.target)
    ensure_expected_head(target, args.expected_head)
    if read_metadata(target) is not None:
        print("Context Capsule is already installed; use validate/upgrade/repair.")
        return 2
    if (target / "AI_CONTEXT.md").exists() or (target / ".context").exists():
        print("Existing AI_CONTEXT.md or .context/ found without capsule metadata; use adopt for a legacy capsule.")
        return 2
    if not valid_repository(args.repository):
        raise SystemExit("--repository must be in owner/name form")
    created = []
    for rel, source in SYSTEM_FILES.items():
        if copy_if_missing(source, target / rel):
            created.append(str(rel))
    created.extend(seed_project_files(target, for_adoption=False))
    write_metadata(target, args.repository, VERSION)
    write_manifest(target, args.repository, args.branch, args.discovery_branch, preserve_legacy=False)
    created.extend([".context/capsule.json", ".context/manifest.json"])
    print(f"Installed Context Capsule {VERSION} into {args.repository}")
    for item in created:
        print(f"  + {item}")
    return validate_target(target, quiet=False)


def adopt(args: argparse.Namespace) -> int:
    target = repo_root(args.target)
    ensure_expected_head(target, args.expected_head)
    if read_metadata(target) is not None:
        print("This repository already has capsule metadata; use validate/upgrade/repair.")
        return 2
    if not (target / ".context").exists():
        print("No legacy .context/ found; use install for a new capsule.")
        return 2
    if not valid_repository(args.repository):
        raise SystemExit("--repository must be in owner/name form")
    created = []
    for rel, source in SYSTEM_FILES.items():
        if copy_if_missing(source, target / rel):
            created.append(str(rel))
    created.extend(seed_project_files(target, for_adoption=True))
    write_metadata(target, args.repository, VERSION, adopted_from="legacy")
    write_manifest(target, args.repository, args.branch, args.discovery_branch, preserve_legacy=True)
    print(f"Adopted legacy capsule as Context Capsule {VERSION} in {args.repository}")
    for item in created:
        print(f"  + {item}")
    print("  + .context/capsule.json")
    print("  ~ .context/manifest.json (preserved and enriched when present)")
    return validate_target(target, quiet=False)


def validate_path(target: Path, value: object, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value:
        errors.append(f"manifest.json: missing {label}")
    elif not (target / value).exists():
        errors.append(f"manifest.json: referenced {label} does not exist: {value}")


def validate_references(target: Path, manifest: dict, errors: list[str]) -> None:
    for key in ("entrypoint", "capsule_metadata", "latest_handoff", "protocol"):
        validate_path(target, manifest.get(key), key, errors)
    project = manifest.get("project")
    if not isinstance(project, dict):
        errors.append("manifest.json: project must be an object")
    else:
        for key in ("identity", "goals", "architecture", "constraints"):
            validate_path(target, project.get(key), f"project.{key}", errors)
    current = manifest.get("current")
    if not isinstance(current, dict):
        errors.append("manifest.json: current must be an object")
    else:
        for key in ("state", "blockers", "next"):
            validate_path(target, current.get(key), f"current.{key}", errors)
    for key in ("rules", "decisions", "dialogues", "history"):
        value = manifest.get(key)
        if not isinstance(value, list):
            errors.append(f"manifest.json: {key} must be a list")
            continue
        for item in value:
            if not isinstance(item, str) or not (target / item).exists():
                errors.append(f"manifest.json: missing referenced {key} item: {item}")


def compactness_warnings(target: Path, manifest: dict) -> list[str]:
    warnings = []
    current = manifest.get("current") if isinstance(manifest.get("current"), dict) else {}
    candidates = {
        "current.state": current.get("state"),
        "current.blockers": current.get("blockers"),
        "current.next": current.get("next"),
        "latest_handoff": manifest.get("latest_handoff"),
    }
    for label, rel in candidates.items():
        if isinstance(rel, str):
            path = target / rel
            if path.exists():
                size = path.stat().st_size
                limit = COMPACT_WARN_BYTES[label]
                if size > limit:
                    warnings.append(
                        f"{label} is {size} bytes (> {limit}); review for resolved/history material that should be compacted"
                    )
    return warnings


def context_git_lag_warning(target: Path) -> str | None:
    if git_head(target) is None:
        return None
    try:
        context_commit = subprocess.run(
            ["git", "-C", str(target), "log", "-1", "--format=%H", "--", ".context", "AI_CONTEXT.md", "AGENTS.md"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        if not context_commit:
            return None
        count_text = subprocess.run(
            ["git", "-C", str(target), "rev-list", "--count", f"{context_commit}..HEAD"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        count = int(count_text or "0")
        if count >= 25:
            return (
                f"{count} commits exist after the last context/discovery update; "
                "review intervening changes for semantic decisions that should be promoted into .context"
            )
    except Exception:
        return None
    return None


def validate_target(target: Path, quiet: bool = False, audit_git: bool = False) -> int:
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
        if manifest.get("schema_version") != 2:
            errors.append("manifest.json: schema_version must be 2")
        branch = manifest.get("authoritative_branch")
        if not isinstance(branch, str) or not branch:
            errors.append("manifest.json: authoritative_branch is required")
        discovery = manifest.get("discovery_branch")
        if not isinstance(discovery, str) or not discovery:
            errors.append("manifest.json: discovery_branch is required")
        if manifest.get("branch_mode") not in ("single", "redirect"):
            errors.append("manifest.json: branch_mode must be single or redirect")
        validate_references(target, manifest, errors)
        if meta and manifest.get("repository") != meta.get("repository"):
            errors.append("manifest.json repository does not match capsule.json")
        if not manifest.get("rules"):
            warnings.append("manifest.json: no project rules are indexed yet")
        warnings.extend(compactness_warnings(target, manifest))
        runtime = manifest.get("runtime")
        if not isinstance(runtime, dict):
            errors.append("manifest.json: runtime must be an object")
        sync_policy = manifest.get("sync_policy")
        if not isinstance(sync_policy, dict) or sync_policy.get("semantic_only") is not True:
            errors.append("manifest.json: sync_policy.semantic_only must be true")
    if audit_git:
        lag = context_git_lag_warning(target)
        if lag:
            warnings.append(lag)
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
    return validate_target(repo_root(args.target), audit_git=False)


def audit(args: argparse.Namespace) -> int:
    return validate_target(repo_root(args.target), audit_git=True)


def repair(args: argparse.Namespace) -> int:
    target = repo_root(args.target)
    ensure_expected_head(target, args.expected_head)
    meta = read_metadata(target)
    if meta is None:
        print("No installed capsule metadata found; use install or adopt instead of repair.")
        return 2
    repaired = []
    for rel, source in SYSTEM_FILES.items():
        if copy_if_missing(source, target / rel):
            repaired.append(str(rel))
    repaired.extend(seed_project_files(target, for_adoption=True))
    manifest = read_manifest(target)
    branch = (manifest or {}).get("authoritative_branch") or args.branch
    discovery_branch = (manifest or {}).get("discovery_branch") or args.discovery_branch
    write_manifest(target, meta["repository"], branch, discovery_branch, preserve_legacy=True)
    for item in repaired:
        print(f"  + restored {item}")
    if not repaired:
        print("No missing files found; manifest index refreshed.")
    return validate_target(target)


def migrate_1_0_to_1_1(target: Path, meta: dict, branch: str, discovery_branch: str | None) -> None:
    for rel, source in SYSTEM_FILES.items():
        copy_if_missing(source, target / rel)
    seed_project_files(target, for_adoption=True)
    write_manifest(target, meta["repository"], branch, discovery_branch, preserve_legacy=True)
    write_metadata(target, meta["repository"], "1.1.0")


def migrate_1_1_to_1_2(target: Path, meta: dict, branch: str, discovery_branch: str | None) -> None:
    for rel, source in SYSTEM_FILES.items():
        copy_if_missing(source, target / rel)
    seed_project_files(target, for_adoption=True)
    write_manifest(target, meta["repository"], branch, discovery_branch, preserve_legacy=True)
    write_metadata(target, meta["repository"], "1.2.0")


def apply_migration(operation: str, target: Path, meta: dict, branch: str, discovery_branch: str | None) -> None:
    if operation == "builtin:1.0.0-to-1.1.0":
        migrate_1_0_to_1_1(target, meta, branch, discovery_branch)
        return
    if operation == "builtin:1.1.0-to-1.2.0":
        migrate_1_1_to_1_2(target, meta, branch, discovery_branch)
        return
    raise SystemExit(f"unsupported migration operation: {operation}")


def upgrade(args: argparse.Namespace) -> int:
    target = repo_root(args.target)
    ensure_expected_head(target, args.expected_head)
    meta = read_metadata(target)
    if meta is None:
        print("No installed capsule metadata found; use install or adopt.")
        return 2
    installed = meta.get("version")
    if installed == VERSION:
        print(f"Already on Context Capsule {VERSION}.")
        return validate_target(target)
    registry = json.loads((CORE_ROOT / "migrations" / "registry.json").read_text(encoding="utf-8"))
    migrations = registry.get("migrations", [])
    seen = set()
    current = installed
    while current != VERSION:
        if current in seen:
            print("Migration cycle detected; refusing upgrade.")
            return 4
        seen.add(current)
        migration = next((m for m in migrations if m.get("from") == current), None)
        if migration is None:
            print(f"No declared migration from {current} toward {VERSION}; refusing implicit upgrade.")
            return 3
        meta = read_metadata(target) or meta
        apply_migration(migration.get("operation", ""), target, meta, args.branch, args.discovery_branch)
        next_version = migration.get("to")
        print(f"  migrated {current} -> {next_version}")
        current = next_version
    print(f"Upgraded Context Capsule {installed} -> {VERSION}")
    return validate_target(target)


def add_common_target(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--target", required=True)


def add_mutating_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--branch", default="main", help="authoritative context branch (default: main)")
    parser.add_argument("--discovery-branch", default=None, help="branch containing discovery shims; defaults to authoritative/default branch")
    parser.add_argument("--expected-head", default=None, help="optional Git HEAD CAS guard; abort if target HEAD differs")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="capsulectl", description="Context Capsule lifecycle tool")
    sub = parser.add_subparsers(dest="command", required=True)
    p_install = sub.add_parser("install", help="install a new capsule into a clean target repository")
    add_common_target(p_install)
    add_mutating_options(p_install)
    p_install.add_argument("--repository", required=True, help="target repository in owner/name form")
    p_install.set_defaults(func=install)
    p_adopt = sub.add_parser("adopt", help="adopt an existing legacy .context/ without overwriting project memory")
    add_common_target(p_adopt)
    add_mutating_options(p_adopt)
    p_adopt.add_argument("--repository", required=True, help="target repository in owner/name form")
    p_adopt.set_defaults(func=adopt)
    p_validate = sub.add_parser("validate", help="validate an installed capsule and manifest references")
    add_common_target(p_validate)
    p_validate.set_defaults(func=validate)
    p_audit = sub.add_parser("audit", help="validate plus compactness and Git semantic-sync lag checks")
    add_common_target(p_audit)
    p_audit.set_defaults(func=audit)
    p_repair = sub.add_parser("repair", help="restore missing structure and refresh the manifest index")
    add_common_target(p_repair)
    add_mutating_options(p_repair)
    p_repair.set_defaults(func=repair)
    p_upgrade = sub.add_parser("upgrade", help="upgrade through explicit declared migrations")
    add_common_target(p_upgrade)
    add_mutating_options(p_upgrade)
    p_upgrade.set_defaults(func=upgrade)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
