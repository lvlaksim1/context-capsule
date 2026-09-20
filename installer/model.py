from __future__ import annotations

import copy
import datetime as dt
import json
from pathlib import Path
from typing import Iterable

from .safety import CapsuleSafetyError, normalize_repo_path, render_managed_block, validate_core_commit

VERSION = "1.3.0"
SOURCE_REPOSITORY = "lvlaksim1/context-capsule"
MANIFEST_SCHEMA_VERSION = 3

SYSTEM_TEXT_PATHS = (
    ".context/ENTRYPOINT.md",
    ".context/protocol.md",
)
PROJECT_SEED_PATHS = (
    ".context/project/identity.md",
    ".context/project/goals.md",
    ".context/project/architecture.md",
    ".context/project/constraints.md",
    ".context/current/state.md",
    ".context/current/blockers.md",
    ".context/current/next.md",
    ".context/rules/project-rules.md",
    ".context/decisions/README.md",
    ".context/handoffs/latest.md",
    ".context/dialogues/README.md",
    ".context/history/README.md",
)
BOOTSTRAP_FILES = ("AI_CONTEXT.md", "AGENTS.md")

PLACEHOLDER_PATTERNS = (
    "capture the ",
    "not yet captured",
    "no handoff recorded yet",
    "perform initial context capture",
    "no project-specific rules have been captured",
    "record only ",
    "record the currently actionable",
)


class CapsuleModelError(ValueError):
    pass


def canonical_json(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def parse_json_text(files: dict[str, str], path: str) -> dict | None:
    text = files.get(path)
    if text is None:
        return None
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CapsuleModelError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CapsuleModelError(f"JSON root must be an object: {path}")
    return value


def _load_template(template_root: Path, rel: str) -> str:
    path = template_root / rel
    if not path.exists():
        raise CapsuleModelError(f"missing Core template: {rel}")
    return path.read_text(encoding="utf-8")


def _bootstrap_body(kind: str, template_root: Path) -> str:
    path = template_root / kind
    if not path.exists():
        raise CapsuleModelError(f"missing Core bootstrap template: {kind}")
    return path.read_text(encoding="utf-8").strip()


def bootstrap_changes(files: dict[str, str], template_root: Path) -> dict[str, str]:
    return {
        "AI_CONTEXT.md": render_managed_block(
            files.get("AI_CONTEXT.md"),
            _bootstrap_body("AI_CONTEXT.md", template_root),
            default_heading="# AI Context",
        ),
        "AGENTS.md": render_managed_block(
            files.get("AGENTS.md"),
            _bootstrap_body("AGENTS.md", template_root),
            default_heading="# Agent Instructions",
        ),
    }



def discovery_redirect_changes(
    files: dict[str, str],
    template_root: Path,
    authoritative_branch: str,
    discovery_branch: str,
) -> dict[str, str | None]:
    if authoritative_branch == discovery_branch:
        raise CapsuleModelError("discovery redirect requires different authoritative and discovery branches")

    def discovery_text(name: str) -> str:
        text = _load_template(template_root, f"discovery/{name}")
        return (
            text.replace("{{AUTHORITATIVE_BRANCH}}", authoritative_branch)
            .replace("{{DISCOVERY_BRANCH}}", discovery_branch)
        )

    changes: dict[str, str | None] = {
        "AI_CONTEXT.md": render_managed_block(
            files.get("AI_CONTEXT.md"),
            discovery_text("AI_CONTEXT.md").strip(),
            default_heading="# AI Context",
        ),
        "AGENTS.md": render_managed_block(
            files.get("AGENTS.md"),
            discovery_text("AGENTS.md").strip(),
            default_heading="# Agent Instructions",
        ),
        ".context/ENTRYPOINT.md": discovery_text(".context/ENTRYPOINT.md"),
    }
    for path in files:
        if path.startswith(".context/") and path != ".context/ENTRYPOINT.md":
            changes[path] = None
    return changes


def build_capsule_metadata(
    repository: str,
    core_commit: str,
    *,
    existing: dict | None = None,
    adopted_from: str | None = None,
) -> dict:
    validate_core_commit(core_commit)
    old = copy.deepcopy(existing or {})
    result = old
    result.update(
        {
            "schema": "context-capsule",
            "version": VERSION,
            "source": SOURCE_REPOSITORY,
            "core_commit": core_commit,
            "installed_at": old.get("installed_at") or dt.date.today().isoformat(),
            "repository": repository,
            "update_policy": "manual",
        }
    )
    if adopted_from:
        result["adopted_from"] = adopted_from
    return result


def _merge_unique(existing: object, discovered: Iterable[str]) -> list[str]:
    result: list[str] = []
    if isinstance(existing, list):
        for item in existing:
            if isinstance(item, str) and item not in result:
                result.append(item)
    for item in discovered:
        if item not in result:
            result.append(item)
    return result


def _markdown_files(files: dict[str, str], prefix: str, *, omit_readme: bool = True) -> list[str]:
    prefix = prefix.rstrip("/") + "/"
    result = []
    for path in sorted(files):
        if not path.startswith(prefix) or not path.endswith(".md"):
            continue
        if omit_readme and path.lower().endswith("/readme.md"):
            continue
        result.append(path)
    return result


def _copy_nested(existing: dict, key: str) -> dict:
    value = existing.get(key)
    return copy.deepcopy(value) if isinstance(value, dict) else {}


def build_manifest(
    files: dict[str, str],
    repository: str,
    branch: str,
    *,
    existing: dict | None = None,
    redirect_topology: tuple[str, str] | None = None,
) -> dict:
    old = copy.deepcopy(existing or {})
    manifest = old

    if redirect_topology:
        authoritative_branch, discovery_branch = redirect_topology
        branch_mode = "redirect" if authoritative_branch != discovery_branch else "single"
    elif existing:
        authoritative_branch = old.get("authoritative_branch") or branch
        discovery_branch = old.get("discovery_branch") or authoritative_branch
        branch_mode = old.get("branch_mode") or (
            "redirect" if authoritative_branch != discovery_branch else "single"
        )
    else:
        authoritative_branch = branch
        discovery_branch = branch
        branch_mode = "single"

    project_old = _copy_nested(old, "project")
    project_old.update(
        {
            "identity": project_old.get("identity") or ".context/project/identity.md",
            "goals": project_old.get("goals") or ".context/project/goals.md",
            "architecture": project_old.get("architecture") or ".context/project/architecture.md",
            "constraints": project_old.get("constraints") or ".context/project/constraints.md",
        }
    )

    current_old = _copy_nested(old, "current")
    current_old.update(
        {
            "state": current_old.get("state") or old.get("current_state") or ".context/current/state.md",
            "blockers": current_old.get("blockers") or ".context/current/blockers.md",
            "next": current_old.get("next") or ".context/current/next.md",
        }
    )

    runtime_old = _copy_nested(old, "runtime")
    runtime_paths = runtime_old.get("authoritative_paths")
    if not isinstance(runtime_paths, list):
        runtime_paths = []
    runtime_old.update(
        {
            "authoritative_paths": runtime_paths,
            "volatile": bool(runtime_old.get("volatile", bool(runtime_paths))),
            "promote_semantic_changes_only": bool(
                runtime_old.get("promote_semantic_changes_only", bool(runtime_paths))
            ),
        }
    )

    sync_old = _copy_nested(old, "sync_policy")
    sync_old.update(
        {
            "semantic_only": True,
            "volatile_runtime_excluded": True,
            "atomic_git_publication": True,
        }
    )

    manifest.update(
        {
            "schema": "context-capsule-manifest",
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "repository": repository,
            "authoritative_branch": authoritative_branch,
            "discovery_branch": discovery_branch,
            "branch_mode": branch_mode,
            "entrypoint": old.get("entrypoint") or ".context/ENTRYPOINT.md",
            "capsule_metadata": ".context/capsule.json",
            "protocol": old.get("protocol") or ".context/protocol.md",
            "latest_handoff": old.get("latest_handoff")
            or old.get("active_handoff")
            or ".context/handoffs/latest.md",
            "project": project_old,
            "current": current_old,
            "current_state": current_old["state"],
            "rules": _merge_unique(old.get("rules"), _markdown_files(files, ".context/rules")),
            "decisions": _merge_unique(old.get("decisions"), _markdown_files(files, ".context/decisions")),
            "dialogues": _merge_unique(old.get("dialogues"), _markdown_files(files, ".context/dialogues")),
            "history": _merge_unique(old.get("history"), _markdown_files(files, ".context/history")),
            "runtime": runtime_old,
            "sync_policy": sync_old,
            "updated_at": dt.date.today().isoformat(),
        }
    )
    if not manifest["rules"] and ".context/rules/project-rules.md" in files:
        manifest["rules"] = [".context/rules/project-rules.md"]
    return manifest


def referenced_paths(manifest: dict) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for key in ("entrypoint", "capsule_metadata", "protocol", "latest_handoff"):
        value = manifest.get(key)
        if isinstance(value, str):
            refs.append((key, value))
    project = manifest.get("project")
    if isinstance(project, dict):
        for key in ("identity", "goals", "architecture", "constraints"):
            value = project.get(key)
            if isinstance(value, str):
                refs.append((f"project.{key}", value))
    current = manifest.get("current")
    if isinstance(current, dict):
        for key in ("state", "blockers", "next"):
            value = current.get(key)
            if isinstance(value, str):
                refs.append((f"current.{key}", value))
    for key in ("rules", "decisions", "dialogues", "history"):
        value = manifest.get(key)
        if isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, str):
                    refs.append((f"{key}[{index}]", item))
    return refs


def validate_snapshot(files: dict[str, str]) -> list[str]:
    errors: list[str] = []
    try:
        meta = parse_json_text(files, ".context/capsule.json")
    except CapsuleModelError as exc:
        errors.append(str(exc))
        meta = None
    try:
        manifest = parse_json_text(files, ".context/manifest.json")
    except CapsuleModelError as exc:
        errors.append(str(exc))
        manifest = None

    if meta is None:
        errors.append("missing .context/capsule.json")
    else:
        if meta.get("schema") != "context-capsule":
            errors.append("capsule.json: invalid schema")
        if meta.get("version") == VERSION:
            try:
                validate_core_commit(meta.get("core_commit", ""))
            except CapsuleSafetyError as exc:
                errors.append(f"capsule.json: {exc}")
        if not isinstance(meta.get("repository"), str) or meta["repository"].count("/") != 1:
            errors.append("capsule.json: repository must be owner/name")
        if meta.get("update_policy") != "manual":
            errors.append("capsule.json: update_policy must be manual")

    for path in SYSTEM_TEXT_PATHS:
        if path not in files:
            errors.append(f"missing system file: {path}")
    for path in BOOTSTRAP_FILES:
        if path not in files:
            errors.append(f"missing bootstrap file: {path}")

    if manifest is None:
        errors.append("missing .context/manifest.json")
    else:
        if manifest.get("schema") != "context-capsule-manifest":
            errors.append("manifest.json: invalid schema")
        if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
            errors.append(f"manifest.json: schema_version must be {MANIFEST_SCHEMA_VERSION}")
        if manifest.get("branch_mode") not in ("single", "redirect"):
            errors.append("manifest.json: branch_mode must be single or redirect")
        if not isinstance(manifest.get("authoritative_branch"), str) or not manifest.get("authoritative_branch"):
            errors.append("manifest.json: authoritative_branch is required")
        if not isinstance(manifest.get("discovery_branch"), str) or not manifest.get("discovery_branch"):
            errors.append("manifest.json: discovery_branch is required")
        if meta and manifest.get("repository") != meta.get("repository"):
            errors.append("manifest.json repository does not match capsule.json")

        for label, raw_path in referenced_paths(manifest):
            try:
                safe = normalize_repo_path(raw_path)
            except CapsuleSafetyError as exc:
                errors.append(f"manifest.json {label}: {exc}")
                continue
            if safe not in files:
                errors.append(f"manifest.json {label}: referenced path does not exist: {safe}")

        sync = manifest.get("sync_policy")
        if not isinstance(sync, dict) or sync.get("semantic_only") is not True:
            errors.append("manifest.json: sync_policy.semantic_only must be true")
        if not isinstance(sync, dict) or sync.get("atomic_git_publication") is not True:
            errors.append("manifest.json: sync_policy.atomic_git_publication must be true")

    return errors


def _semantic_text(text: str) -> str:
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("<!--"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def _is_substantive(text: str | None) -> bool:
    if text is None:
        return False
    body = _semantic_text(text)
    if len(body) < 32:
        return False
    lower = body.lower()
    return not any(pattern in lower for pattern in PLACEHOLDER_PATTERNS)


def readiness_snapshot(files: dict[str, str]) -> tuple[bool, list[str]]:
    validation = validate_snapshot(files)
    if validation:
        return False, [f"VALIDATION: {item}" for item in validation]

    manifest = parse_json_text(files, ".context/manifest.json") or {}
    missing: list[str] = []

    required = {
        "project.identity": manifest["project"]["identity"],
        "project.goals": manifest["project"]["goals"],
        "project.architecture": manifest["project"]["architecture"],
        "project.constraints": manifest["project"]["constraints"],
        "current.state": manifest["current"]["state"],
        "current.next": manifest["current"]["next"],
        "latest_handoff": manifest["latest_handoff"],
    }
    for label, path in required.items():
        if not _is_substantive(files.get(path)):
            missing.append(f"{label} is empty or still a template")

    rule_ready = any(_is_substantive(files.get(path)) for path in manifest.get("rules", []))
    decision_ready = any(_is_substantive(files.get(path)) for path in manifest.get("decisions", []))
    if not (rule_ready or decision_ready):
        missing.append("no substantive active rule or durable decision is available")

    return not missing, missing


def build_recovery_pack(files: dict[str, str], *, max_chars: int = 50000) -> str:
    ready, reasons = readiness_snapshot(files)
    if not ready:
        raise CapsuleModelError("capsule is not READY: " + "; ".join(reasons))
    manifest = parse_json_text(files, ".context/manifest.json") or {}

    ordered: list[tuple[str, str]] = [
        ("PROJECT IDENTITY", manifest["project"]["identity"]),
        ("PROJECT GOALS", manifest["project"]["goals"]),
        ("PROJECT ARCHITECTURE", manifest["project"]["architecture"]),
        ("PROJECT CONSTRAINTS", manifest["project"]["constraints"]),
    ]
    for path in manifest.get("rules", []):
        ordered.append(("ACTIVE RULE", path))
    ordered.extend(
        [
            ("LATEST HANDOFF", manifest["latest_handoff"]),
            ("CURRENT STATE", manifest["current"]["state"]),
            ("CURRENT BLOCKERS", manifest["current"]["blockers"]),
            ("NEXT ACTIONS", manifest["current"]["next"]),
        ]
    )
    for path in manifest.get("decisions", []):
        ordered.append(("DURABLE DECISION", path))

    chunks = [
        "# CONTEXT CAPSULE RECOVERY PACK",
        "",
        f"Repository: {manifest.get('repository')}",
        f"Authoritative branch: {manifest.get('authoritative_branch')}",
        "",
    ]
    used = sum(len(x) + 1 for x in chunks)
    omitted: list[str] = []
    for label, path in ordered:
        text = files.get(path)
        if text is None:
            continue
        chunk = f"## {label}: {path}\n\n{text.strip()}\n"
        if used + len(chunk) > max_chars:
            omitted.append(path)
            continue
        chunks.append(chunk)
        used += len(chunk)
    if omitted:
        chunks.append("## OMITTED DEEPER CONTEXT\n\n" + "\n".join(f"- {p}" for p in omitted))
    return "\n".join(chunks).rstrip() + "\n"


def clean_install_changes(
    files: dict[str, str],
    template_root: Path,
    repository: str,
    branch: str,
    core_commit: str,
    *,
    semantic_overrides: dict[str, str] | None = None,
    discovery_branch: str | None = None,
) -> dict[str, str]:
    if any(path == ".context" or path.startswith(".context/") for path in files):
        raise CapsuleModelError("clean install refused: existing .context content found")

    validate_core_commit(core_commit)
    changes: dict[str, str] = {}
    changes.update(bootstrap_changes(files, template_root))

    for rel in SYSTEM_TEXT_PATHS + PROJECT_SEED_PATHS:
        changes[rel] = _load_template(template_root, rel)

    if semantic_overrides:
        for raw_path, content in semantic_overrides.items():
            path = normalize_repo_path(raw_path)
            if not path.startswith(".context/"):
                raise CapsuleModelError(f"semantic override must be inside .context/: {path}")
            changes[path] = content

    provisional = dict(files)
    provisional.update(changes)
    meta = build_capsule_metadata(repository, core_commit)
    provisional[".context/capsule.json"] = canonical_json(meta)
    redirect_topology = None
    if discovery_branch and discovery_branch != branch:
        redirect_topology = (branch, discovery_branch)
    manifest = build_manifest(provisional, repository, branch, redirect_topology=redirect_topology)
    provisional[".context/manifest.json"] = canonical_json(manifest)

    errors = validate_snapshot(provisional)
    if errors:
        raise CapsuleModelError("planned clean install is invalid: " + "; ".join(errors))
    return {path: provisional[path] for path in provisional if files.get(path) != provisional[path]}


def repair_changes(
    files: dict[str, str],
    template_root: Path,
    *,
    repository: str,
    branch: str,
    core_commit: str,
) -> dict[str, str]:
    existing_manifest = parse_json_text(files, ".context/manifest.json") or {}
    existing_meta = parse_json_text(files, ".context/capsule.json") or {}

    authoritative_branch = existing_manifest.get("authoritative_branch")
    if (
        isinstance(authoritative_branch, str)
        and authoritative_branch
        and authoritative_branch != branch
    ):
        raise CapsuleModelError(
            f"repair must run against authoritative branch {authoritative_branch!r}, not {branch!r}"
        )
    changes = bootstrap_changes(files, template_root)
    provisional = dict(files)
    provisional.update(changes)

    for rel in SYSTEM_TEXT_PATHS + PROJECT_SEED_PATHS:
        if rel not in provisional:
            provisional[rel] = _load_template(template_root, rel)

    provisional[".context/capsule.json"] = canonical_json(
        build_capsule_metadata(repository, core_commit, existing=existing_meta)
    )
    provisional[".context/manifest.json"] = canonical_json(
        build_manifest(provisional, repository, branch, existing=existing_manifest)
    )
    errors = validate_snapshot(provisional)
    if errors:
        raise CapsuleModelError("planned repair is invalid: " + "; ".join(errors))
    return {path: provisional[path] for path in provisional if files.get(path) != provisional[path]}
