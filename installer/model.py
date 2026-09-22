from __future__ import annotations

import copy
import datetime as dt
import json
import re
from pathlib import Path
from typing import Iterable

from .safety import CapsuleSafetyError, normalize_repo_path, render_managed_block, validate_core_commit

VERSION = "2.0.0-dev"
SOURCE_REPOSITORY = "lvlaksim1/context-capsule"
MANIFEST_SCHEMA_VERSION = 4
MANAGER_IDENTITY_SCHEMA_VERSION = 1
MANAGER_IDENTITY_PATH = ".context/manager/identity.json"

SYSTEM_TEXT_PATHS = (
    ".context/ENTRYPOINT.md",
    ".context/protocol.md",
    ".context/manager/PROTOCOL.md",
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
    ".context/manager/mandate.md",
    ".context/manager/beliefs.md",
    ".context/manager/goals.md",
    ".context/manager/intentions.md",
    ".context/manager/plans.md",
    ".context/memory/index.md",
    ".context/memory/semantic.md",
    ".context/memory/procedural.md",
    ".context/memory/episodes/README.md",
)
BOOTSTRAP_FILES = ("AI_CONTEXT.md", "AGENTS.md")

PLACEHOLDER_PATTERNS = (
    "capture the ",
    "capture durable ",
    "not yet captured",
    "no handoff recorded yet",
    "perform initial context capture",
    "no project-specific rules have been captured",
    "record only ",
    "record the currently actionable",
    "describe the manager",
    "define what the manager",
    "record current verified beliefs",
    "record the active goals",
    "record active commitments",
    "record the current plan",
    "record reusable durable knowledge",
    "record learned procedures",
)
_MANAGER_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")


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
        return text.replace("{{AUTHORITATIVE_BRANCH}}", authoritative_branch).replace(
            "{{DISCOVERY_BRANCH}}", discovery_branch
        )

    changes: dict[str, str | None] = {
        "AI_CONTEXT.md": render_managed_block(
            files.get("AI_CONTEXT.md"), discovery_text("AI_CONTEXT.md").strip(), default_heading="# AI Context"
        ),
        "AGENTS.md": render_managed_block(
            files.get("AGENTS.md"), discovery_text("AGENTS.md").strip(), default_heading="# Agent Instructions"
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


def build_manager_identity(repository: str, *, existing: dict | None = None) -> dict:
    old = copy.deepcopy(existing or {})
    manager_id = old.get("manager_id") or "project-manager"
    result = old
    result.update(
        {
            "schema": "context-capsule-manager-identity",
            "schema_version": MANAGER_IDENTITY_SCHEMA_VERSION,
            "manager_id": manager_id,
            "role": old.get("role") or "Project Manager",
            "repository": repository,
            "continuity": "runtime-independent",
            "authority_model": "bounded-by-mandate",
            "state_model": "beliefs-goals-intentions-plans",
            "memory_model": "typed-with-provenance",
        }
    )
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

    manager_old = _copy_nested(old, "manager")
    manager_old.update(
        {
            "protocol": manager_old.get("protocol") or ".context/manager/PROTOCOL.md",
            "identity": manager_old.get("identity") or MANAGER_IDENTITY_PATH,
            "mandate": manager_old.get("mandate") or ".context/manager/mandate.md",
            "beliefs": manager_old.get("beliefs") or ".context/manager/beliefs.md",
            "goals": manager_old.get("goals") or ".context/manager/goals.md",
            "intentions": manager_old.get("intentions") or ".context/manager/intentions.md",
            "plans": manager_old.get("plans") or ".context/manager/plans.md",
        }
    )

    memory_old = _copy_nested(old, "memory")
    memory_old.update(
        {
            "index": memory_old.get("index") or ".context/memory/index.md",
            "semantic": memory_old.get("semantic") or ".context/memory/semantic.md",
            "procedural": memory_old.get("procedural") or ".context/memory/procedural.md",
            "episodes": _merge_unique(
                memory_old.get("episodes"), _markdown_files(files, ".context/memory/episodes")
            ),
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
            "checkpoint_is_capsule_state": False,
        }
    )

    sync_old = _copy_nested(old, "sync_policy")
    sync_old.update(
        {
            "semantic_only": True,
            "volatile_runtime_excluded": True,
            "atomic_git_publication": True,
            "provenance_required_for_manager_beliefs": True,
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
            "manager": manager_old,
            "memory": memory_old,
            "current": current_old,
            "current_state": current_old["state"],
            "rules": _merge_unique(old.get("rules"), _markdown_files(files, ".context/rules")),
            "decisions": _merge_unique(old.get("decisions"), _markdown_files(files, ".context/decisions")),
            "dialogues": _merge_unique(old.get("dialogues"), _markdown_files(files, ".context/dialogues")),
            "history": _merge_unique(old.get("history"), _markdown_files(files, ".context/history")),
            "runtime": runtime_old,
            "sync_policy": sync_old,
            "updated_at": dt.date.today().isoformat(),
            "context_version": VERSION,
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
    manager = manifest.get("manager")
    if isinstance(manager, dict):
        for key in ("protocol", "identity", "mandate", "beliefs", "goals", "intentions", "plans"):
            value = manager.get(key)
            if isinstance(value, str):
                refs.append((f"manager.{key}", value))
    memory = manifest.get("memory")
    if isinstance(memory, dict):
        for key in ("index", "semantic", "procedural"):
            value = memory.get(key)
            if isinstance(value, str):
                refs.append((f"memory.{key}", value))
        episodes = memory.get("episodes")
        if isinstance(episodes, list):
            for index, item in enumerate(episodes):
                if isinstance(item, str):
                    refs.append((f"memory.episodes[{index}]", item))
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


def _validate_manager_identity(files: dict[str, str], repository: str | None) -> list[str]:
    errors: list[str] = []
    try:
        identity = parse_json_text(files, MANAGER_IDENTITY_PATH)
    except CapsuleModelError as exc:
        return [str(exc)]
    if identity is None:
        return [f"missing {MANAGER_IDENTITY_PATH}"]
    if identity.get("schema") != "context-capsule-manager-identity":
        errors.append("manager identity: invalid schema")
    if identity.get("schema_version") != MANAGER_IDENTITY_SCHEMA_VERSION:
        errors.append(f"manager identity: schema_version must be {MANAGER_IDENTITY_SCHEMA_VERSION}")
    manager_id = identity.get("manager_id")
    if not isinstance(manager_id, str) or not _MANAGER_ID.fullmatch(manager_id):
        errors.append("manager identity: manager_id must be a stable 3-128 character identifier")
    if identity.get("continuity") != "runtime-independent":
        errors.append("manager identity: continuity must be runtime-independent")
    if repository and identity.get("repository") != repository:
        errors.append("manager identity repository does not match capsule repository")
    return errors


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
        if meta.get("version") != VERSION:
            errors.append(f"capsule.json: version must be {VERSION}; use explicit upgrade for older capsules")
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
        if not isinstance(manifest.get("manager"), dict):
            errors.append("manifest.json: manager section is required")
        if not isinstance(manifest.get("memory"), dict):
            errors.append("manifest.json: memory section is required")

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
        if not isinstance(sync, dict) or sync.get("provenance_required_for_manager_beliefs") is not True:
            errors.append("manifest.json: manager belief provenance must be required")
        runtime = manifest.get("runtime")
        if not isinstance(runtime, dict) or runtime.get("checkpoint_is_capsule_state") is not False:
            errors.append("manifest.json: runtime checkpoint must remain separate from capsule state")

    repository = meta.get("repository") if isinstance(meta, dict) else None
    errors.extend(_validate_manager_identity(files, repository))
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


def _has_belief_provenance(text: str | None) -> bool:
    if not _is_substantive(text):
        return False
    lower = text.lower()
    return "source:" in lower and "authority:" in lower


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
        "manager.mandate": manifest["manager"]["mandate"],
        "manager.goals": manifest["manager"]["goals"],
        "manager.intentions": manifest["manager"]["intentions"],
        "manager.plans": manifest["manager"]["plans"],
        "current.state": manifest["current"]["state"],
        "current.next": manifest["current"]["next"],
    }
    for label, path in required.items():
        if not _is_substantive(files.get(path)):
            missing.append(f"{label} is empty or still a template")

    beliefs_path = manifest["manager"]["beliefs"]
    if not _has_belief_provenance(files.get(beliefs_path)):
        missing.append("manager.beliefs must be substantive and include source: and authority: provenance")

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
    identity = parse_json_text(files, manifest["manager"]["identity"]) or {}
    manager_id = identity.get("manager_id", "project-manager")

    ordered: list[tuple[str, str]] = [
        ("MANAGER PROTOCOL", manifest["manager"]["protocol"]),
        ("MANAGER IDENTITY", manifest["manager"]["identity"]),
        ("MANAGER MANDATE", manifest["manager"]["mandate"]),
        ("PROJECT IDENTITY", manifest["project"]["identity"]),
        ("PROJECT GOALS", manifest["project"]["goals"]),
        ("PROJECT ARCHITECTURE", manifest["project"]["architecture"]),
        ("PROJECT CONSTRAINTS", manifest["project"]["constraints"]),
        ("MANAGER BELIEFS", manifest["manager"]["beliefs"]),
        ("MANAGER GOALS", manifest["manager"]["goals"]),
        ("MANAGER INTENTIONS", manifest["manager"]["intentions"]),
        ("MANAGER PLANS", manifest["manager"]["plans"]),
    ]
    for path in manifest.get("rules", []):
        ordered.append(("ACTIVE RULE", path))
    ordered.extend(
        [
            ("CURRENT STATE", manifest["current"]["state"]),
            ("CURRENT BLOCKERS", manifest["current"]["blockers"]),
            ("NEXT ACTIONS", manifest["current"]["next"]),
            ("SEMANTIC MEMORY", manifest["memory"]["semantic"]),
            ("PROCEDURAL MEMORY", manifest["memory"]["procedural"]),
            ("EMERGENCY HANDOFF (NON-AUTHORITATIVE)", manifest["latest_handoff"]),
        ]
    )
    for path in manifest["memory"].get("episodes", []):
        ordered.append(("EPISODIC MEMORY", path))
    for path in manifest.get("decisions", []):
        ordered.append(("DURABLE DECISION", path))

    chunks = [
        "# CONTEXT CAPSULE PROJECT MANAGER REINSTANTIATION PACK",
        "",
        f"Repository: {manifest.get('repository')}",
        f"Authoritative branch: {manifest.get('authoritative_branch')}",
        f"Manager ID: {manager_id}",
        "",
        "You are a new runtime instance of the existing Project Manager, not a new manager.",
        "Preserve manager identity, open intentions, and durable memory unless newer authoritative evidence invalidates them.",
        "Runtime conversation/checkpoint state is not manager identity and must not override durable capsule state.",
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
        chunks.append("## OMITTED DEEPER MEMORY\n\n" + "\n".join(f"- {p}" for p in omitted))
    return "\n".join(chunks).rstrip() + "\n"


def _seed_v2_structure(
    provisional: dict[str, str], template_root: Path, repository: str, *, overwrite_system: bool
) -> None:
    for rel in SYSTEM_TEXT_PATHS:
        if overwrite_system or rel not in provisional:
            provisional[rel] = _load_template(template_root, rel)
    for rel in PROJECT_SEED_PATHS:
        if rel not in provisional:
            provisional[rel] = _load_template(template_root, rel)
    existing_identity = None
    if MANAGER_IDENTITY_PATH in provisional:
        try:
            existing_identity = json.loads(provisional[MANAGER_IDENTITY_PATH])
        except Exception:
            existing_identity = None
    if MANAGER_IDENTITY_PATH not in provisional:
        provisional[MANAGER_IDENTITY_PATH] = canonical_json(build_manager_identity(repository))
    elif isinstance(existing_identity, dict):
        provisional[MANAGER_IDENTITY_PATH] = canonical_json(
            build_manager_identity(repository, existing=existing_identity)
        )


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
    provisional = dict(files)
    provisional.update(bootstrap_changes(files, template_root))
    _seed_v2_structure(provisional, template_root, repository, overwrite_system=True)

    if semantic_overrides:
        for raw_path, content in semantic_overrides.items():
            path = normalize_repo_path(raw_path)
            if not path.startswith(".context/"):
                raise CapsuleModelError(f"semantic override must be inside .context/: {path}")
            provisional[path] = content

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


def upgrade_changes(
    files: dict[str, str],
    template_root: Path,
    *,
    repository: str,
    branch: str,
    core_commit: str,
) -> dict[str, str]:
    existing_manifest = parse_json_text(files, ".context/manifest.json") or {}
    existing_meta = parse_json_text(files, ".context/capsule.json") or {}
    old_version = existing_meta.get("version")
    if not isinstance(old_version, str) or not old_version.startswith("1.3."):
        raise CapsuleModelError("v2 upgrade currently accepts only installed v1.3.x capsules")
    authoritative_branch = existing_manifest.get("authoritative_branch") or branch
    if authoritative_branch != branch:
        raise CapsuleModelError(
            f"upgrade must run against authoritative branch {authoritative_branch!r}, not {branch!r}"
        )
    validate_core_commit(core_commit)
    provisional = dict(files)
    provisional.update(bootstrap_changes(files, template_root))
    _seed_v2_structure(provisional, template_root, repository, overwrite_system=True)
    provisional[".context/capsule.json"] = canonical_json(
        build_capsule_metadata(repository, core_commit, existing=existing_meta)
    )
    provisional[".context/manifest.json"] = canonical_json(
        build_manifest(provisional, repository, branch, existing=existing_manifest)
    )
    errors = validate_snapshot(provisional)
    if errors:
        raise CapsuleModelError("planned v2 upgrade is invalid: " + "; ".join(errors))
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
    if existing_meta.get("version") != VERSION:
        raise CapsuleModelError(
            f"repair never performs a major-version upgrade; installed version is {existing_meta.get('version')!r}, use upgrade"
        )
    authoritative_branch = existing_manifest.get("authoritative_branch")
    if isinstance(authoritative_branch, str) and authoritative_branch and authoritative_branch != branch:
        raise CapsuleModelError(
            f"repair must run against authoritative branch {authoritative_branch!r}, not {branch!r}"
        )
    provisional = dict(files)
    provisional.update(bootstrap_changes(files, template_root))
    _seed_v2_structure(provisional, template_root, repository, overwrite_system=True)
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
