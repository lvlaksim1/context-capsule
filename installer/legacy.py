"""Temporary legacy shape readers; retire after the three existing installations are migrated."""
from pathlib import Path

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
        if candidate:
            return candidate
    return fallback


def legacy_authoritative_map(legacy: dict) -> dict:
    value = legacy.get("authoritative")
    return value if isinstance(value, dict) else {}


def existing_rule_paths(target: Path, legacy: dict) -> list[str]:
    rules = legacy.get("rules")
    if isinstance(rules, list):
        found = [r for r in rules if isinstance(r, str)] + md_files(Path(".context/rules"), target)
        if found:
            return list(dict.fromkeys(found))
    authoritative = legacy_authoritative_map(legacy)
    found = []
    for key in ("user_rules", "development_rules", "ai_rules", "project_rules"):
        value = authoritative.get(key)
        if isinstance(value, str):
            found.append(value)
    if found:
        return list(dict.fromkeys(found))
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
        **result,
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


