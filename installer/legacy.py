"""Temporary legacy adapters.

These helpers preserve legacy project semantics while the three known old
installations are migrated. They are intentionally narrow and should be
removed after that transition is verified.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

CORE_ROOT = Path(__file__).resolve().parents[1]
if str(CORE_ROOT) not in sys.path:
    sys.path.insert(0, str(CORE_ROOT))

from runtime.contracts import safe_path


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if isinstance(value, str) and value))


def staged_exists(target: Path, planned: dict[str, bytes], rel: str) -> bool:
    if rel in planned:
        return True
    try:
        return safe_path(target, rel).exists()
    except ValueError:
        # Preserve the declaration; later strict validation should surface it.
        return False


def md_files(
    relative_dir: Path,
    target: Path,
    planned: dict[str, bytes] | None = None,
    include_readme: bool = False,
) -> list[str]:
    planned = planned or {}
    prefix = relative_dir.as_posix().rstrip("/") + "/"
    result: list[str] = []

    root = safe_path(target, relative_dir.as_posix())
    if root.exists():
        if not root.is_dir():
            raise ValueError(f"{relative_dir.as_posix()} must be a directory")
        for path in sorted(root.rglob("*.md")):
            rel = path.relative_to(target).as_posix()
            safe_path(target, rel)
            if not include_readme and path.name.lower() == "readme.md":
                continue
            result.append(rel)

    for rel in sorted(planned):
        if not rel.startswith(prefix) or not rel.endswith(".md"):
            continue
        if not include_readme and Path(rel).name.lower() == "readme.md":
            continue
        result.append(rel)

    return _dedupe(result)


def as_path(value: object) -> str:
    return value if isinstance(value, str) else ""


def first_declared(candidates: list[str], fallback: str) -> str:
    for candidate in candidates:
        if isinstance(candidate, str) and candidate:
            return candidate
    return fallback


def legacy_authoritative_map(legacy: dict) -> dict:
    value = legacy.get("authoritative")
    return value if isinstance(value, dict) else {}


def declared_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def existing_rule_paths(
    target: Path,
    legacy: dict,
    planned: dict[str, bytes] | None = None,
) -> list[str]:
    planned = planned or {}
    found = declared_list(legacy.get("rules"))

    authoritative = legacy_authoritative_map(legacy)
    for key in ("user_rules", "development_rules", "ai_rules", "project_rules"):
        value = authoritative.get(key)
        if isinstance(value, str) and value:
            found.append(value)

    found.extend(md_files(Path(".context/rules"), target, planned))
    return _dedupe(found)


def legacy_project_paths(legacy: dict) -> dict[str, str]:
    nested = legacy.get("project")
    if not isinstance(nested, dict):
        nested = {}
    authoritative = legacy_authoritative_map(legacy)
    return {
        "identity": first_declared(
            [
                as_path(nested.get("identity")),
                as_path(authoritative.get("identity")),
            ],
            ".context/project/identity.md",
        ),
        "goals": first_declared(
            [
                as_path(nested.get("goals")),
                as_path(authoritative.get("goals")),
            ],
            ".context/project/goals.md",
        ),
        "architecture": first_declared(
            [
                as_path(nested.get("architecture")),
                as_path(authoritative.get("architecture")),
            ],
            ".context/project/architecture.md",
        ),
        "constraints": first_declared(
            [
                as_path(nested.get("constraints")),
                as_path(authoritative.get("constraints")),
            ],
            ".context/project/constraints.md",
        ),
    }


def legacy_current_paths(legacy: dict) -> dict[str, str]:
    nested = legacy.get("current")
    if not isinstance(nested, dict):
        nested = {}
    authoritative = legacy_authoritative_map(legacy)
    return {
        "state": first_declared(
            [
                as_path(nested.get("state")),
                as_path(legacy.get("current_state")),
                as_path(authoritative.get("current_state")),
            ],
            ".context/current/state.md",
        ),
        "blockers": first_declared(
            [
                as_path(nested.get("blockers")),
                as_path(authoritative.get("blockers")),
            ],
            ".context/current/blockers.md",
        ),
        "next": first_declared(
            [
                as_path(nested.get("next")),
                as_path(authoritative.get("next")),
            ],
            ".context/current/next.md",
        ),
    }


def infer_runtime(target: Path, legacy: dict) -> dict:
    runtime = legacy.get("runtime")
    result = copy.deepcopy(runtime) if isinstance(runtime, dict) else {}

    paths = result.get("authoritative_paths")
    paths = declared_list(paths)

    files = legacy.get("authoritative_files")
    if isinstance(files, dict):
        live_runtime = files.get("live_runtime")
        if isinstance(live_runtime, str) and live_runtime:
            paths.append(live_runtime.rstrip("/") + "/")

    agent = safe_path(target, ".agent")
    if agent.exists():
        paths.append(".agent/")

    paths = _dedupe(paths)
    result["authoritative_paths"] = paths
    result["volatile"] = bool(paths)
    result["promote_semantic_changes_only"] = bool(paths)
    return result


def infer_branches(
    legacy: dict,
    branch: str,
    discovery_branch: str | None,
) -> tuple[str, str, str]:
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


def merge_manifest(
    target: Path,
    planned: dict[str, bytes],
    repository: str,
    branch: str,
    discovery_branch: str | None,
    legacy: dict | None,
) -> dict:
    """Enrich a legacy manifest without discarding unknown semantic fields."""
    original = copy.deepcopy(legacy) if isinstance(legacy, dict) else {}
    manifest = copy.deepcopy(original)

    authoritative_branch, discovered_branch, branch_mode = infer_branches(
        original,
        branch,
        discovery_branch,
    )

    project = copy.deepcopy(original.get("project")) if isinstance(original.get("project"), dict) else {}
    project.update(legacy_project_paths(original))

    current = copy.deepcopy(original.get("current")) if isinstance(original.get("current"), dict) else {}
    current.update(legacy_current_paths(original))

    latest_handoff = first_declared(
        [
            as_path(original.get("latest_handoff")),
            as_path(original.get("active_handoff")),
        ],
        ".context/handoffs/latest.md",
    )
    protocol = first_declared(
        [as_path(original.get("protocol"))],
        ".context/protocol.md",
    )

    rules = existing_rule_paths(target, original, planned)
    if not rules:
        rules = [".context/rules/project-rules.md"]

    decisions = _dedupe(
        declared_list(original.get("decisions"))
        + md_files(Path(".context/decisions"), target, planned)
    )
    dialogues = _dedupe(
        declared_list(original.get("dialogues"))
        + md_files(Path(".context/dialogues"), target, planned)
    )
    history = _dedupe(
        declared_list(original.get("history"))
        + md_files(Path(".context/history"), target, planned)
    )

    sync_policy = (
        copy.deepcopy(original.get("sync_policy"))
        if isinstance(original.get("sync_policy"), dict)
        else {}
    )
    sync_policy.update(
        {
            "semantic_only": True,
            "volatile_runtime_excluded": True,
            "cas_required_when_expected_head_supplied": True,
        }
    )

    manifest.update(
        {
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
            "rules": rules,
            "decisions": decisions,
            "dialogues": dialogues,
            "history": history,
            "runtime": infer_runtime(target, original),
            "sync_policy": sync_policy,
        }
    )
    return manifest
