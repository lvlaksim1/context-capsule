#!/usr/bin/env python3
"""Context Capsule Core lifecycle tool.

Standard-library only. Operates on a checked-out target repository.
Target context never leaves that repository.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

CORE_ROOT = Path(__file__).resolve().parents[1]
if str(CORE_ROOT) not in sys.path:
    sys.path.insert(0, str(CORE_ROOT))

from installer.legacy import md_files, merge_manifest
from installer.storage import apply as transaction_apply
from installer.storage import git, inventory, locked, recover
from runtime.contracts import safe_path

TEMPLATES = CORE_ROOT / "templates"
VERSION = (CORE_ROOT / "VERSION").read_text(encoding="utf-8").strip()
SOURCE = (CORE_ROOT / "SOURCE_REPOSITORY").read_text(encoding="utf-8").strip()
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")

SYSTEM_FILES = {
    "AI_CONTEXT.md": TEMPLATES / "AI_CONTEXT.md",
    "AGENTS.md": TEMPLATES / "AGENTS.md",
    ".context/ENTRYPOINT.md": TEMPLATES / ".context/ENTRYPOINT.md",
    ".context/protocol.md": TEMPLATES / ".context/protocol.md",
}
PROJECT_SEED_FILES = {
    ".context/project/identity.md": TEMPLATES / ".context/project/identity.md",
    ".context/project/goals.md": TEMPLATES / ".context/project/goals.md",
    ".context/project/architecture.md": TEMPLATES / ".context/project/architecture.md",
    ".context/project/constraints.md": TEMPLATES / ".context/project/constraints.md",
    ".context/current/state.md": TEMPLATES / ".context/current/state.md",
    ".context/current/blockers.md": TEMPLATES / ".context/current/blockers.md",
    ".context/current/next.md": TEMPLATES / ".context/current/next.md",
    ".context/rules/project-rules.md": TEMPLATES / ".context/rules/project-rules.md",
    ".context/decisions/README.md": TEMPLATES / ".context/decisions/README.md",
    ".context/handoffs/latest.md": TEMPLATES / ".context/handoffs/latest.md",
    ".context/dialogues/README.md": TEMPLATES / ".context/dialogues/README.md",
    ".context/history/README.md": TEMPLATES / ".context/history/README.md",
}

COMPACT_WARN_BYTES = {
    "current.state": 12_000,
    "current.blockers": 8_000,
    "current.next": 8_000,
    "latest_handoff": 12_000,
}


class CapsuleError(Exception):
    def __init__(self, message: str, code: int = 2):
        super().__init__(message)
        self.code = code


def repo_root(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.exists() or not path.is_dir():
        raise CapsuleError(f"target does not exist or is not a directory: {path}")
    return path


def valid_repository(value: object) -> bool:
    return (
        isinstance(value, str)
        and re.fullmatch(r"[^/\s]+/[^/\s]+", value) is not None
    )


def json_bytes(payload: dict) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    ).encode("utf-8")


def parse_json_bytes(data: bytes, label: str) -> dict:
    try:
        value = json.loads(data.decode("utf-8"))
    except Exception as exc:
        raise CapsuleError(f"invalid JSON in {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise CapsuleError(f"JSON root must be an object: {label}")
    return value


def snapshot_json(snapshot: dict[str, bytes], rel: str) -> dict | None:
    data = snapshot.get(rel)
    return parse_json_bytes(data, rel) if data is not None else None


def target_json(target: Path, rel: str) -> dict | None:
    path = safe_path(target, rel)
    if not path.exists():
        return None
    if not path.is_file():
        raise CapsuleError(f"expected file: {rel}")
    return parse_json_bytes(path.read_bytes(), rel)


def planned_exists(target: Path, snapshot: dict[str, bytes], rel: str) -> bool:
    if rel in snapshot:
        return True
    try:
        path = safe_path(target, rel)
    except ValueError as exc:
        raise CapsuleError(str(exc)) from exc
    return path.is_file()


def copy_if_missing(snapshot: dict[str, bytes], rel: str, source: Path) -> bool:
    if rel in snapshot:
        return False
    snapshot[rel] = source.read_bytes()
    return True


def seed_project_files(
    target: Path,
    snapshot: dict[str, bytes],
    *,
    for_adoption: bool,
) -> list[str]:
    created: list[str] = []
    for rel, source in PROJECT_SEED_FILES.items():
        if rel == ".context/rules/project-rules.md" and for_adoption:
            existing_rules = md_files(Path(".context/rules"), target, snapshot)
            if existing_rules:
                continue
        if copy_if_missing(snapshot, rel, source):
            created.append(rel)
    return created


def metadata_payload(
    previous: dict | None,
    repository: str,
    version: str,
    adopted_from: str | None = None,
) -> dict:
    previous = previous or {}
    payload = {
        "schema": "context-capsule",
        "version": version,
        "source": SOURCE,
        "installed_at": previous.get("installed_at")
        or dt.date.today().isoformat(),
        "repository": repository,
        "update_policy": "manual",
    }
    if adopted_from:
        payload["adopted_from"] = adopted_from
    elif isinstance(previous.get("adopted_from"), str):
        payload["adopted_from"] = previous["adopted_from"]
    return payload


def build_manifest(
    target: Path,
    snapshot: dict[str, bytes],
    repository: str,
    branch: str,
    discovery_branch: str | None,
    legacy: dict | None,
) -> dict:
    manifest = merge_manifest(
        target,
        snapshot,
        repository,
        branch,
        discovery_branch,
        legacy,
    )
    manifest["updated_at"] = dt.date.today().isoformat()
    return manifest


def branch_exists(target: Path, branch: str) -> bool:
    if not branch:
        return False
    checks = (
        f"refs/heads/{branch}",
        f"refs/remotes/origin/{branch}",
    )
    for ref in checks:
        if git(target, "show-ref", "--verify", "--quiet", ref, required=False) == "":
            # show-ref --quiet emits nothing for both success and failure, inspect via rev-parse.
            if git(target, "rev-parse", "--verify", f"{ref}^{{commit}}", required=False):
                return True
    return bool(
        git(target, "rev-parse", "--verify", f"{branch}^{{commit}}", required=False)
    )


def dirty_capsule_state(target: Path) -> str:
    return git(
        target,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--",
        ".context",
        "AGENTS.md",
        "AI_CONTEXT.md",
        required=False,
    )


def mutation_context(target: Path, args: argparse.Namespace):
    """Acquire mutation lock and return stable Git identity plus snapshot."""
    lock = locked(target)
    gitdir = lock.__enter__()
    try:
        recover(target, gitdir)

        head = git(target, "rev-parse", "HEAD")
        branch = git(target, "branch", "--show-current")
        if not branch:
            raise CapsuleError(
                "mutating lifecycle operations require a named Git branch"
            )

        requested_branch = getattr(args, "branch", None)
        if requested_branch and requested_branch != branch:
            raise CapsuleError(
                f"wrong checkout branch: {branch}; requested authority is {requested_branch}"
            )

        expected_head = getattr(args, "expected_head", None)
        if expected_head and expected_head != head:
            raise CapsuleError(
                f"CAS mismatch: expected HEAD {expected_head}, actual HEAD {head}"
            )

        if (
            not getattr(args, "allow_dirty_context", False)
            and dirty_capsule_state(target)
        ):
            raise CapsuleError(
                "capsule/discovery files have uncommitted changes; "
                "commit/stash them or use --allow-dirty-context explicitly"
            )

        before = inventory(target)
        return lock, gitdir, head, branch, before
    except BaseException:
        lock.__exit__(*sys.exc_info())
        raise


def validate_path(
    target: Path,
    snapshot: dict[str, bytes],
    value: object,
    label: str,
    errors: list[str],
) -> None:
    if not isinstance(value, str) or not value:
        errors.append(f"manifest.json: missing {label}")
        return
    try:
        if not planned_exists(target, snapshot, value):
            errors.append(
                f"manifest.json: referenced {label} does not exist: {value}"
            )
    except CapsuleError as exc:
        errors.append(f"manifest.json: unsafe {label}: {exc}")


def validate_references(
    target: Path,
    snapshot: dict[str, bytes],
    manifest: dict,
    errors: list[str],
) -> None:
    for key in ("entrypoint", "capsule_metadata", "latest_handoff", "protocol"):
        validate_path(target, snapshot, manifest.get(key), key, errors)

    project = manifest.get("project")
    if not isinstance(project, dict):
        errors.append("manifest.json: project must be an object")
    else:
        for key in ("identity", "goals", "architecture", "constraints"):
            validate_path(
                target,
                snapshot,
                project.get(key),
                f"project.{key}",
                errors,
            )

    current = manifest.get("current")
    if not isinstance(current, dict):
        errors.append("manifest.json: current must be an object")
    else:
        for key in ("state", "blockers", "next"):
            validate_path(
                target,
                snapshot,
                current.get(key),
                f"current.{key}",
                errors,
            )

    for key in ("rules", "decisions", "dialogues", "history"):
        value = manifest.get(key)
        if not isinstance(value, list):
            errors.append(f"manifest.json: {key} must be a list")
            continue
        for item in value:
            validate_path(target, snapshot, item, f"{key} item", errors)


def validate_snapshot(
    target: Path,
    snapshot: dict[str, bytes],
    *,
    authoritative_checkout: str | None = None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        meta = snapshot_json(snapshot, ".context/capsule.json")
    except CapsuleError as exc:
        errors.append(str(exc))
        meta = None

    if meta is None:
        errors.append("missing .context/capsule.json")
    else:
        if meta.get("schema") != "context-capsule":
            errors.append("capsule.json: invalid schema")
        version = meta.get("version")
        if not isinstance(version, str) or SEMVER.fullmatch(version) is None:
            errors.append("capsule.json: invalid version")
        if meta.get("source") != SOURCE:
            errors.append("capsule.json: unexpected source")
        if meta.get("update_policy") != "manual":
            errors.append("capsule.json: update_policy must be manual")
        if not valid_repository(meta.get("repository")):
            errors.append("capsule.json: repository must be owner/name")
        installed_at = meta.get("installed_at")
        try:
            if not isinstance(installed_at, str):
                raise ValueError
            dt.date.fromisoformat(installed_at)
        except ValueError:
            errors.append("capsule.json: installed_at must be an ISO date")

    for rel in SYSTEM_FILES:
        if rel not in snapshot:
            errors.append(f"missing system file: {rel}")

    try:
        manifest = snapshot_json(snapshot, ".context/manifest.json")
    except CapsuleError as exc:
        errors.append(str(exc))
        manifest = None

    if manifest is None:
        errors.append("missing .context/manifest.json")
        return errors, warnings

    if manifest.get("schema") != "context-capsule-manifest":
        errors.append("manifest.json: invalid schema")
    if manifest.get("schema_version") != 2:
        errors.append("manifest.json: schema_version must be 2")

    branch = manifest.get("authoritative_branch")
    discovery = manifest.get("discovery_branch")
    if not isinstance(branch, str) or not branch:
        errors.append("manifest.json: authoritative_branch is required")
    if not isinstance(discovery, str) or not discovery:
        errors.append("manifest.json: discovery_branch is required")

    expected_mode = (
        "single"
        if isinstance(branch, str)
        and isinstance(discovery, str)
        and branch == discovery
        else "redirect"
    )
    if manifest.get("branch_mode") not in ("single", "redirect"):
        errors.append("manifest.json: branch_mode must be single or redirect")
    elif (
        isinstance(branch, str)
        and isinstance(discovery, str)
        and manifest.get("branch_mode") != expected_mode
    ):
        errors.append("manifest.json: branch_mode disagrees with declared branches")

    if authoritative_checkout and branch != authoritative_checkout:
        errors.append(
            f"manifest.json: authoritative_branch {branch!r} "
            f"does not match checked-out branch {authoritative_checkout!r}"
        )

    validate_references(target, snapshot, manifest, errors)

    if meta and manifest.get("repository") != meta.get("repository"):
        errors.append("manifest.json repository does not match capsule.json")
    if not manifest.get("rules"):
        warnings.append("manifest.json: no project rules are indexed yet")

    runtime = manifest.get("runtime")
    if not isinstance(runtime, dict):
        errors.append("manifest.json: runtime must be an object")
    else:
        paths = runtime.get("authoritative_paths")
        if not isinstance(paths, list):
            errors.append("manifest.json: runtime.authoritative_paths must be a list")
        else:
            for rel in paths:
                if not isinstance(rel, str) or not rel:
                    errors.append(
                        "manifest.json: runtime.authoritative_paths contains invalid path"
                    )
                    continue
                candidate = rel[:-1] if rel.endswith("/") else rel
                try:
                    safe_path(target, candidate)
                except ValueError as exc:
                    errors.append(f"manifest.json: unsafe runtime path {rel}: {exc}")

    sync_policy = manifest.get("sync_policy")
    if not isinstance(sync_policy, dict):
        errors.append("manifest.json: sync_policy must be an object")
    else:
        if sync_policy.get("semantic_only") is not True:
            errors.append("manifest.json: sync_policy.semantic_only must be true")
        if sync_policy.get("volatile_runtime_excluded") is not True:
            errors.append(
                "manifest.json: sync_policy.volatile_runtime_excluded must be true"
            )
        if (
            sync_policy.get("cas_required_when_expected_head_supplied")
            is not True
        ):
            errors.append(
                "manifest.json: sync_policy.cas_required_when_expected_head_supplied "
                "must be true"
            )

    updated_at = manifest.get("updated_at")
    try:
        if not isinstance(updated_at, str):
            raise ValueError
        dt.date.fromisoformat(updated_at)
    except ValueError:
        errors.append("manifest.json: updated_at must be an ISO date")

    return errors, warnings


def compactness_warnings(target: Path, manifest: dict) -> list[str]:
    warnings: list[str] = []
    current = (
        manifest.get("current")
        if isinstance(manifest.get("current"), dict)
        else {}
    )
    candidates = {
        "current.state": current.get("state"),
        "current.blockers": current.get("blockers"),
        "current.next": current.get("next"),
        "latest_handoff": manifest.get("latest_handoff"),
    }
    for label, rel in candidates.items():
        if not isinstance(rel, str):
            continue
        try:
            path = safe_path(target, rel)
        except ValueError:
            continue
        if path.is_file():
            size = path.stat().st_size
            limit = COMPACT_WARN_BYTES[label]
            if size > limit:
                warnings.append(
                    f"{label} is {size} bytes (> {limit}); review for resolved/history "
                    "material that should be compacted"
                )
    return warnings


def context_git_lag_warning(target: Path) -> str | None:
    try:
        context_commit = git(
            target,
            "log",
            "-1",
            "--format=%H",
            "--",
            ".context",
            "AI_CONTEXT.md",
            "AGENTS.md",
            required=False,
        )
        if not context_commit:
            return None
        count_text = git(
            target,
            "rev-list",
            "--count",
            f"{context_commit}..HEAD",
            required=False,
        )
        count = int(count_text or "0")
        if count >= 25:
            return (
                f"{count} commits exist after the last context/discovery update; "
                "review intervening changes for semantic decisions that should be "
                "promoted into .context"
            )
    except Exception:
        return None
    return None


def validate_target(
    target: Path,
    *,
    quiet: bool = False,
    audit_git: bool = False,
) -> int:
    try:
        snapshot = inventory(target)
    except ValueError as exc:
        print("Context Capsule validation: FAIL")
        print(f"  - {exc}")
        return 1

    branch = git(target, "branch", "--show-current", required=False) or None
    errors, warnings = validate_snapshot(
        target,
        snapshot,
        authoritative_checkout=branch,
    )

    manifest = None
    try:
        manifest = snapshot_json(snapshot, ".context/manifest.json")
    except CapsuleError:
        pass

    if isinstance(manifest, dict):
        warnings.extend(compactness_warnings(target, manifest))

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
        for warning in dict.fromkeys(warnings):
            print(f"  ! {warning}")
    return 0


def prepare_install(
    target: Path,
    before: dict[str, bytes],
    args: argparse.Namespace,
    branch: str,
) -> tuple[dict[str, bytes], list[str]]:
    if snapshot_json(before, ".context/capsule.json") is not None:
        raise CapsuleError(
            "Context Capsule is already installed; use validate/upgrade/repair."
        )

    context_dir = safe_path(target, ".context")
    if context_dir.exists():
        raise CapsuleError(
            "Existing .context/ found without capsule metadata; use adopt for a "
            "legacy capsule."
        )

    if not valid_repository(args.repository):
        raise CapsuleError("--repository must be in owner/name form")

    after = dict(before)
    created: list[str] = []

    for rel, source in SYSTEM_FILES.items():
        if copy_if_missing(after, rel, source):
            created.append(rel)

    created.extend(seed_project_files(target, after, for_adoption=False))
    after[".context/capsule.json"] = json_bytes(
        metadata_payload(None, args.repository, VERSION)
    )
    after[".context/manifest.json"] = json_bytes(
        build_manifest(
            target,
            after,
            args.repository,
            branch,
            args.discovery_branch,
            None,
        )
    )
    created.extend([".context/capsule.json", ".context/manifest.json"])
    return after, [f"  + {item}" for item in created]


def prepare_adopt(
    target: Path,
    before: dict[str, bytes],
    args: argparse.Namespace,
    branch: str,
) -> tuple[dict[str, bytes], list[str]]:
    if snapshot_json(before, ".context/capsule.json") is not None:
        raise CapsuleError(
            "This repository already has capsule metadata; use validate/upgrade/repair."
        )

    context_dir = safe_path(target, ".context")
    if not context_dir.exists() or not context_dir.is_dir():
        raise CapsuleError("No legacy .context/ found; use install for a new capsule.")

    if not valid_repository(args.repository):
        raise CapsuleError("--repository must be in owner/name form")

    # Parse the legacy manifest before planning any mutation. Malformed JSON
    # therefore leaves the target unchanged.
    legacy = snapshot_json(before, ".context/manifest.json") or {}

    after = dict(before)
    created: list[str] = []
    for rel, source in SYSTEM_FILES.items():
        if copy_if_missing(after, rel, source):
            created.append(rel)

    created.extend(seed_project_files(target, after, for_adoption=True))
    after[".context/capsule.json"] = json_bytes(
        metadata_payload(None, args.repository, VERSION, adopted_from="legacy")
    )
    after[".context/manifest.json"] = json_bytes(
        build_manifest(
            target,
            after,
            args.repository,
            branch,
            args.discovery_branch,
            legacy,
        )
    )
    messages = [f"  + {item}" for item in created]
    messages.append("  + .context/capsule.json")
    messages.append("  ~ .context/manifest.json (preserved and enriched)")
    return after, messages


def prepare_repair(
    target: Path,
    before: dict[str, bytes],
    args: argparse.Namespace,
    branch: str,
) -> tuple[dict[str, bytes], list[str]]:
    meta = snapshot_json(before, ".context/capsule.json")
    if meta is None:
        raise CapsuleError(
            "No installed capsule metadata found; use install or adopt instead of repair."
        )
    if not valid_repository(meta.get("repository")):
        raise CapsuleError("capsule.json repository is invalid")

    legacy = snapshot_json(before, ".context/manifest.json") or {}
    after = dict(before)
    repaired: list[str] = []

    for rel, source in SYSTEM_FILES.items():
        if copy_if_missing(after, rel, source):
            repaired.append(rel)
    repaired.extend(seed_project_files(target, after, for_adoption=True))

    after[".context/manifest.json"] = json_bytes(
        build_manifest(
            target,
            after,
            meta["repository"],
            branch,
            args.discovery_branch,
            legacy,
        )
    )

    if repaired:
        return after, [f"  + restored {item}" for item in repaired]
    return after, ["No missing files found; manifest index refreshed."]


def migration_registry() -> dict:
    path = CORE_ROOT / "migrations" / "registry.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CapsuleError(f"invalid migration registry: {exc}", 4) from exc
    if not isinstance(value, dict) or not isinstance(value.get("migrations"), list):
        raise CapsuleError("invalid migration registry structure", 4)
    return value


def prepare_upgrade(
    target: Path,
    before: dict[str, bytes],
    args: argparse.Namespace,
    branch: str,
) -> tuple[dict[str, bytes], list[str]]:
    meta = snapshot_json(before, ".context/capsule.json")
    if meta is None:
        raise CapsuleError("No installed capsule metadata found; use install or adopt.")
    installed = meta.get("version")
    if not isinstance(installed, str):
        raise CapsuleError("capsule.json version is invalid")

    if installed == VERSION:
        return dict(before), [f"Already on Context Capsule {VERSION}."]

    registry = migration_registry()
    migrations = registry["migrations"]
    current = installed
    seen: set[str] = set()
    after = dict(before)
    messages: list[str] = []

    while current != VERSION:
        if current in seen:
            raise CapsuleError("Migration cycle detected; refusing upgrade.", 4)
        seen.add(current)

        migration = next(
            (
                item
                for item in migrations
                if isinstance(item, dict) and item.get("from") == current
            ),
            None,
        )
        if migration is None:
            raise CapsuleError(
                f"No declared migration from {current} toward {VERSION}; "
                "refusing implicit upgrade.",
                3,
            )
        operation = migration.get("operation")
        next_version = migration.get("to")
        if operation not in (
            "builtin:1.0.0-to-1.1.0",
            "builtin:1.1.0-to-1.2.0",
        ) or not isinstance(next_version, str):
            raise CapsuleError(
                f"unsupported migration operation: {operation}",
                4,
            )

        for rel, source in SYSTEM_FILES.items():
            copy_if_missing(after, rel, source)
        seed_project_files(target, after, for_adoption=True)

        current_meta = snapshot_json(after, ".context/capsule.json") or meta
        legacy = snapshot_json(after, ".context/manifest.json") or {}
        after[".context/manifest.json"] = json_bytes(
            build_manifest(
                target,
                after,
                current_meta["repository"],
                branch,
                args.discovery_branch,
                legacy,
            )
        )
        after[".context/capsule.json"] = json_bytes(
            metadata_payload(
                current_meta,
                current_meta["repository"],
                next_version,
            )
        )

        messages.append(f"  migrated {current} -> {next_version}")
        current = next_version

    messages.append(f"Upgraded Context Capsule {installed} -> {VERSION}")
    return after, messages


def run_mutation(
    args: argparse.Namespace,
    planner,
    success_header: str | None = None,
) -> int:
    target = repo_root(args.target)
    lock = None
    try:
        lock, gitdir, head, branch, before = mutation_context(target, args)
        after, messages = planner(target, before, args, branch)

        errors, warnings = validate_snapshot(
            target,
            after,
            authoritative_checkout=branch,
        )
        discovery = snapshot_json(after, ".context/manifest.json")
        if discovery:
            discovery_branch = discovery.get("discovery_branch")
            if (
                isinstance(discovery_branch, str)
                and discovery_branch != branch
                and not branch_exists(target, discovery_branch)
            ):
                errors.append(
                    f"manifest.json: discovery branch does not exist locally: "
                    f"{discovery_branch}"
                )

        if errors:
            raise CapsuleError(
                "planned mutation failed preflight:\n  - " + "\n  - ".join(errors)
            )

        transaction_apply(target, gitdir, before, after, head, branch)

        if success_header:
            print(success_header)
        for message in messages:
            print(message)
        for warning in warnings:
            print(f"  ! {warning}")

        return validate_target(target, quiet=False)
    finally:
        if lock is not None:
            lock.__exit__(None, None, None)


def install(args: argparse.Namespace) -> int:
    return run_mutation(
        args,
        prepare_install,
        f"Installed Context Capsule {VERSION} into {args.repository}",
    )


def adopt(args: argparse.Namespace) -> int:
    return run_mutation(
        args,
        prepare_adopt,
        f"Adopted legacy capsule as Context Capsule {VERSION} in {args.repository}",
    )


def repair(args: argparse.Namespace) -> int:
    return run_mutation(args, prepare_repair)


def upgrade(args: argparse.Namespace) -> int:
    return run_mutation(args, prepare_upgrade)


def validate(args: argparse.Namespace) -> int:
    return validate_target(repo_root(args.target), audit_git=False)


def audit(args: argparse.Namespace) -> int:
    return validate_target(repo_root(args.target), audit_git=True)


def add_common_target(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--target", required=True)


def add_mutating_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--branch",
        default=None,
        help="authoritative context branch; defaults to the checked-out branch",
    )
    parser.add_argument(
        "--discovery-branch",
        default=None,
        help="branch containing discovery shims; defaults to authority/legacy declaration",
    )
    parser.add_argument(
        "--expected-head",
        default=None,
        help="optional Git HEAD precondition",
    )
    parser.add_argument(
        "--allow-dirty-context",
        action="store_true",
        help=(
            "explicitly allow pre-existing uncommitted AGENTS.md, AI_CONTEXT.md or "
            ".context changes; concurrent edits are still rejected"
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="capsulectl",
        description="Context Capsule lifecycle tool",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_install = sub.add_parser(
        "install",
        help="install a new capsule into a repository without .context",
    )
    add_common_target(p_install)
    add_mutating_options(p_install)
    p_install.add_argument(
        "--repository",
        required=True,
        help="target repository in owner/name form",
    )
    p_install.set_defaults(func=install)

    p_adopt = sub.add_parser(
        "adopt",
        help="temporarily adopt an existing legacy .context without overwriting memory",
    )
    add_common_target(p_adopt)
    add_mutating_options(p_adopt)
    p_adopt.add_argument(
        "--repository",
        required=True,
        help="target repository in owner/name form",
    )
    p_adopt.set_defaults(func=adopt)

    p_validate = sub.add_parser(
        "validate",
        help="validate an installed capsule and references",
    )
    add_common_target(p_validate)
    p_validate.set_defaults(func=validate)

    p_audit = sub.add_parser(
        "audit",
        help="validate plus compactness and Git semantic-lag checks",
    )
    add_common_target(p_audit)
    p_audit.set_defaults(func=audit)

    p_repair = sub.add_parser(
        "repair",
        help="restore missing structure and refresh navigation non-destructively",
    )
    add_common_target(p_repair)
    add_mutating_options(p_repair)
    p_repair.set_defaults(func=repair)

    p_upgrade = sub.add_parser(
        "upgrade",
        help="temporarily upgrade an old capsule through declared migrations",
    )
    add_common_target(p_upgrade)
    add_mutating_options(p_upgrade)
    p_upgrade.set_defaults(func=upgrade)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except CapsuleError as exc:
        print(f"Context Capsule: {exc}", file=sys.stderr)
        return exc.code
    except ValueError as exc:
        print(f"Context Capsule: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
