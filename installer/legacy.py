from __future__ import annotations

import copy
from pathlib import Path

from .model import (
    PROJECT_SEED_PATHS,
    VERSION,
    CapsuleModelError,
    bootstrap_changes,
    build_capsule_metadata,
    build_manifest,
    canonical_json,
    parse_json_text,
    validate_snapshot,
)
from .safety import normalize_repo_path, validate_core_commit

KNOWN_LEGACY_REPOSITORIES = {
    "lvlaksim1/fgis-fsa-il": "fgis-fsa-il",
    "lvlaksim1/telegram-receiver": "telegram-receiver",
    "lvlaksim1/ai-agent-lab": "ai-agent-lab",
}


def detect_known_profile(repository: str) -> str:
    try:
        return KNOWN_LEGACY_REPOSITORIES[repository]
    except KeyError as exc:
        raise CapsuleModelError(
            "legacy adoption is temporary and is allowed only for "
            "fgis-fsa-il, telegram-receiver, and ai-agent-lab"
        ) from exc


def _load_template(template_root: Path, rel: str) -> str:
    path = template_root / rel
    if not path.exists():
        raise CapsuleModelError(f"missing Core template: {rel}")
    return path.read_text(encoding="utf-8")


def _normalize_fgis(manifest: dict) -> dict:
    result = copy.deepcopy(manifest)
    authoritative = result.get("authoritative")
    if isinstance(authoritative, dict):
        project = copy.deepcopy(result.get("project")) if isinstance(result.get("project"), dict) else {}
        for target_key, old_key in (
            ("identity", "identity"),
            ("goals", "goals"),
            ("architecture", "architecture"),
            ("constraints", "constraints"),
        ):
            value = authoritative.get(old_key)
            if isinstance(value, str):
                project[target_key] = value
        result["project"] = project

        current = copy.deepcopy(result.get("current")) if isinstance(result.get("current"), dict) else {}
        for target_key, old_key in (
            ("state", "current_state"),
            ("blockers", "blockers"),
            ("next", "next"),
        ):
            value = authoritative.get(old_key)
            if isinstance(value, str):
                current[target_key] = value
        result["current"] = current

        rules = []
        if isinstance(result.get("rules"), list):
            rules.extend(x for x in result["rules"] if isinstance(x, str))
        for key in ("user_rules", "development_rules", "ai_rules", "project_rules"):
            value = authoritative.get(key)
            if isinstance(value, str) and value not in rules:
                rules.append(value)
        if rules:
            result["rules"] = rules

    if not result.get("latest_handoff") and isinstance(result.get("active_handoff"), str):
        result["latest_handoff"] = result["active_handoff"]
    return result


def _normalize_telegram(manifest: dict) -> dict:
    result = copy.deepcopy(manifest)
    if isinstance(result.get("current_state"), str):
        current = copy.deepcopy(result.get("current")) if isinstance(result.get("current"), dict) else {}
        current.setdefault("state", result["current_state"])
        result["current"] = current
    return result


def _normalize_ai_agent(manifest: dict) -> dict:
    result = copy.deepcopy(manifest)
    if "context_version" in result:
        result.setdefault("legacy_context_version", result["context_version"])
    if "installed_from" in result:
        result.setdefault("legacy_installed_from", result["installed_from"])
    result["context_version"] = VERSION
    result["installed_from"] = f"Context Capsule Core v{VERSION}"
    result["installation_status"] = "adopted-v1.3"
    if isinstance(result.get("current_state"), str):
        current = copy.deepcopy(result.get("current")) if isinstance(result.get("current"), dict) else {}
        current.setdefault("state", result["current_state"])
        result["current"] = current

    runtime = copy.deepcopy(result.get("runtime")) if isinstance(result.get("runtime"), dict) else {}
    paths = runtime.get("authoritative_paths")
    if not isinstance(paths, list):
        paths = []
    authoritative_files = result.get("authoritative_files")
    if isinstance(authoritative_files, dict):
        live = authoritative_files.get("live_runtime")
        if isinstance(live, str):
            live = live.rstrip("/") + "/"
            if live not in paths:
                paths.append(live)
    if ".agent/" not in paths:
        paths.append(".agent/")
    runtime["authoritative_paths"] = paths
    runtime["volatile"] = True
    runtime["promote_semantic_changes_only"] = True
    result["runtime"] = runtime
    return result


def normalize_known_legacy_manifest(repository: str, manifest: dict) -> tuple[dict, tuple[str, str] | None]:
    profile = detect_known_profile(repository)
    if profile == "fgis-fsa-il":
        normalized = _normalize_fgis(manifest)
        authoritative = normalized.get("authoritative_branch") or normalized.get("default_branch") or "main"
        discovery = normalized.get("default_branch") or authoritative
        return normalized, (authoritative, discovery)
    if profile == "telegram-receiver":
        normalized = _normalize_telegram(manifest)
        authoritative = normalized.get("authoritative_branch") or "main"
        return normalized, (authoritative, authoritative)
    if profile == "ai-agent-lab":
        normalized = _normalize_ai_agent(manifest)
        authoritative = normalized.get("authoritative_context_branch") or normalized.get("authoritative_branch")
        if not isinstance(authoritative, str) or not authoritative:
            authoritative = "work-webhook-test"
        discovery = normalized.get("default_branch") or normalized.get("discovery_branch") or "main"
        return normalized, (authoritative, discovery)
    raise AssertionError(profile)


def adopt_known_legacy_changes(
    files: dict[str, str],
    template_root: Path,
    repository: str,
    branch: str,
    core_commit: str,
    *,
    semantic_overrides: dict[str, str] | None = None,
) -> dict[str, str]:
    detect_known_profile(repository)
    validate_core_commit(core_commit)
    if ".context/capsule.json" in files:
        raise CapsuleModelError("legacy adoption refused: capsule metadata already exists")
    if not any(path.startswith(".context/") for path in files):
        raise CapsuleModelError("legacy adoption refused: no legacy .context content found")

    legacy_manifest = parse_json_text(files, ".context/manifest.json") or {}
    normalized, redirect = normalize_known_legacy_manifest(repository, legacy_manifest)
    authoritative = redirect[0] if redirect else branch
    if branch != authoritative:
        raise CapsuleModelError(
            f"legacy adoption must run against authoritative branch {authoritative!r}, not {branch!r}"
        )

    provisional = dict(files)
    changes = bootstrap_changes(files, template_root)
    provisional.update(changes)

    for rel, archive_name in (
        (".context/ENTRYPOINT.md", ".context/history/legacy-entrypoint-before-v1.3.md"),
        (".context/protocol.md", ".context/history/legacy-protocol-before-v1.3.md"),
    ):
        old = provisional.get(rel)
        new = _load_template(template_root, rel)
        if old is not None and old != new and archive_name not in provisional:
            provisional[archive_name] = old
        provisional[rel] = new

    rich_prefixes = {
        ".context/rules/project-rules.md": ".context/rules/",
        ".context/decisions/README.md": ".context/decisions/",
        ".context/dialogues/README.md": ".context/dialogues/",
        ".context/history/README.md": ".context/history/",
    }
    for rel in PROJECT_SEED_PATHS:
        if rel in provisional:
            continue
        prefix = rich_prefixes.get(rel)
        if prefix and any(path.startswith(prefix) for path in provisional):
            continue
        provisional[rel] = _load_template(template_root, rel)

    if semantic_overrides:
        for raw_path, content in semantic_overrides.items():
            path = normalize_repo_path(raw_path)
            if not path.startswith(".context/"):
                raise CapsuleModelError(f"semantic override must be inside .context/: {path}")
            provisional[path] = content

    meta = build_capsule_metadata(repository, core_commit, adopted_from=f"legacy:{detect_known_profile(repository)}")
    provisional[".context/capsule.json"] = canonical_json(meta)
    manifest = build_manifest(
        provisional,
        repository,
        branch,
        existing=normalized,
        legacy_redirect=redirect,
    )
    provisional[".context/manifest.json"] = canonical_json(manifest)

    errors = validate_snapshot(provisional)
    if errors:
        raise CapsuleModelError("planned legacy adoption is invalid: " + "; ".join(errors))
    return {path: provisional[path] for path in provisional if files.get(path) != provisional[path]}
