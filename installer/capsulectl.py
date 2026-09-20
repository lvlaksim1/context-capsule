#!/usr/bin/env python3
"""Context Capsule Core lifecycle and checkpoint tool.

All target-project context remains in the target repository. Mutating lifecycle
operations are planned completely, validated, then applied through the local
transaction layer.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

CORE_ROOT = Path(__file__).resolve().parents[1]
if str(CORE_ROOT) not in sys.path:
    sys.path.insert(0, str(CORE_ROOT))

from installer.legacy import md_files, merge_manifest
from installer.storage import apply as transaction_apply
from installer.storage import git, inventory, locked, recover
from runtime.contracts import managed_block, safe_path, schema_errors

TEMPLATES = CORE_ROOT / "templates"
SCHEMAS = CORE_ROOT / "schemas"
RUNTIME = CORE_ROOT / "runtime"
VERSION = (CORE_ROOT / "VERSION").read_text(encoding="utf-8").strip()
SOURCE = (CORE_ROOT / "SOURCE_REPOSITORY").read_text(encoding="utf-8").strip()
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")

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
TOOL_FILES = {
    ".context/tools/contracts.py": RUNTIME / "contracts.py",
    ".context/tools/capsule_runtime.py": RUNTIME / "capsule_runtime.py",
    ".context/tools/schemas/capsule.schema.json": SCHEMAS / "capsule.schema.json",
    ".context/tools/schemas/manifest.schema.json": SCHEMAS / "manifest.schema.json",
    ".context/tools/schemas/index.schema.json": SCHEMAS / "index.schema.json",
    ".context/tools/schemas/resume.schema.json": SCHEMAS / "resume.schema.json",
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


def utc_now() -> str:
    return (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def json_bytes(payload: dict) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    ).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_text_sha256(data: bytes) -> str:
    """Hash UTF-8 text independent of CRLF/LF checkout conversion."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CapsuleError("managed bootstrap is not UTF-8 text") from exc
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return sha256(normalized.encode("utf-8"))


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


def read_bytes(
    target: Path,
    snapshot: dict[str, bytes],
    rel: str,
) -> bytes:
    if rel in snapshot:
        return snapshot[rel]
    try:
        path = safe_path(target, rel, exists=True)
    except ValueError as exc:
        raise CapsuleError(str(exc)) from exc
    return path.read_bytes()


def read_text(
    target: Path,
    snapshot: dict[str, bytes],
    rel: str,
) -> str:
    try:
        return read_bytes(target, snapshot, rel).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CapsuleError(f"context file is not UTF-8 text: {rel}") from exc


def planned_exists(target: Path, snapshot: dict[str, bytes], rel: str) -> bool:
    if rel in snapshot:
        return True
    try:
        return safe_path(target, rel).is_file()
    except ValueError as exc:
        raise CapsuleError(str(exc)) from exc


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
            if md_files(Path(".context/rules"), target, snapshot):
                continue
        if copy_if_missing(snapshot, rel, source):
            created.append(rel)
    return created


def legacy_bootstrap_hashes() -> dict[str, list[str]]:
    path = CORE_ROOT / "migrations" / "legacy-bootstrap-hashes.json"
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CapsuleError(f"invalid legacy bootstrap hash registry: {exc}") from exc
    if not isinstance(value, dict):
        raise CapsuleError("invalid legacy bootstrap hash registry")
    return {
        key: [item for item in items if isinstance(item, str)]
        for key, items in value.items()
        if isinstance(key, str) and isinstance(items, list)
    }


def template_managed_block(source: Path) -> str:
    text = source.read_text(encoding="utf-8")
    try:
        block = managed_block(text)
    except ValueError as exc:
        raise CapsuleError(f"invalid managed template {source}: {exc}") from exc
    if block is None:
        raise CapsuleError(f"managed template has no Context Capsule block: {source}")
    return block


def merge_managed_bootstrap(
    snapshot: dict[str, bytes],
    rel: str,
    source: Path,
    hashes: dict[str, list[str]],
) -> bool:
    """Install/refresh the Core block while preserving unknown user text.

    Returns True when previously unknown bootstrap text was preserved and needs
    explicit semantic review before the checkpoint may be considered ready.
    """
    template_text = source.read_text(encoding="utf-8")
    new_block = template_managed_block(source)
    existing = snapshot.get(rel)
    if existing is None:
        snapshot[rel] = template_text.encode("utf-8")
        return False

    try:
        existing_text = existing.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CapsuleError(f"bootstrap file is not UTF-8 text: {rel}") from exc

    try:
        old_block = managed_block(existing_text)
    except ValueError as exc:
        raise CapsuleError(f"malformed managed bootstrap in {rel}: {exc}") from exc

    if old_block is not None:
        snapshot[rel] = existing_text.replace(
            old_block,
            new_block,
            1,
        ).encode("utf-8")
        return False

    if canonical_text_sha256(existing) in hashes.get(rel, []):
        snapshot[rel] = template_text.encode("utf-8")
        return False

    preserved = existing_text.rstrip()
    if preserved:
        preserved += "\n\n"
    snapshot[rel] = (preserved + new_block + "\n").encode("utf-8")
    return True


def install_core_managed_files(
    snapshot: dict[str, bytes],
) -> list[str]:
    hashes = legacy_bootstrap_hashes()
    review: list[str] = []
    for rel, source in SYSTEM_FILES.items():
        if merge_managed_bootstrap(snapshot, rel, source, hashes):
            review.append(rel)
    for rel, source in TOOL_FILES.items():
        snapshot[rel] = source.read_bytes()
    return review


def managed_hashes(snapshot: dict[str, bytes]) -> dict[str, str]:
    result: dict[str, str] = {}
    for rel in SYSTEM_FILES:
        try:
            text = snapshot[rel].decode("utf-8")
            block = managed_block(text)
        except (KeyError, UnicodeDecodeError, ValueError) as exc:
            raise CapsuleError(f"cannot register managed bootstrap {rel}: {exc}") from exc
        if block is None:
            raise CapsuleError(f"missing managed bootstrap block: {rel}")
        result[rel] = sha256(block.encode("utf-8"))
    for rel in TOOL_FILES:
        if rel not in snapshot:
            raise CapsuleError(f"missing managed tool during planning: {rel}")
        result[rel] = canonical_text_sha256(snapshot[rel])
    return result


def metadata_payload(
    previous: dict | None,
    repository: str,
    version: str,
    managed: dict[str, str],
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
        "managed_files": managed,
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


def _first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return fallback


def _summary(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- Status:") or stripped.startswith("- Date:"):
            continue
        if stripped.startswith("CAPSULE_TODO"):
            continue
        lines.append(stripped)
        if len(" ".join(lines)) >= 300:
            break
    return " ".join(lines)[:400]


def _record_status(text: str, record_type: str) -> str:
    match = re.search(
        r"(?im)^-?\s*Status:\s*(active|superseded|deprecated|closed|reference)\s*$",
        text,
    )
    if match:
        return match.group(1).lower()
    return "active" if record_type == "decision" else "reference"


def build_memory_index(
    target: Path,
    snapshot: dict[str, bytes],
    manifest: dict,
    existing: dict | None,
) -> dict:
    existing_records = []
    if isinstance(existing, dict) and isinstance(existing.get("records"), list):
        existing_records = [
            copy.deepcopy(item)
            for item in existing["records"]
            if isinstance(item, dict)
            and isinstance(item.get("path"), str)
            and item.get("path")
        ]

    by_path = {item["path"]: item for item in existing_records}
    records = list(existing_records)
    used_ids = {
        item.get("id")
        for item in records
        if isinstance(item.get("id"), str) and item.get("id")
    }

    declared: list[tuple[str, str]] = []
    for record_type, key in (
        ("decision", "decisions"),
        ("dialogue", "dialogues"),
        ("history", "history"),
    ):
        for rel in manifest[key]:
            declared.append((record_type, rel))

    for record_type, rel in declared:
        if rel in by_path:
            continue
        text = read_text(target, snapshot, rel)
        base = Path(rel).stem or record_type
        candidate = base
        if candidate in used_ids:
            candidate = f"{record_type}:{base}"
        suffix = 2
        while candidate in used_ids:
            candidate = f"{record_type}:{base}:{suffix}"
            suffix += 1
        used_ids.add(candidate)
        item = {
            "id": candidate,
            "type": record_type,
            "status": _record_status(text, record_type),
            "title": _first_heading(text, base),
            "summary": _summary(text),
            "tags": [],
            "path": rel,
            "updated_at": dt.date.today().isoformat(),
        }
        records.append(item)
        by_path[rel] = item

    proposed = {
        "schema": "context-capsule-index",
        "schema_version": 1,
        "records": records,
        "updated_at": dt.date.today().isoformat(),
    }
    if (
        isinstance(existing, dict)
        and existing.get("schema") == "context-capsule-index"
        and existing.get("schema_version") == 1
        and existing.get("records") == records
        and isinstance(existing.get("updated_at"), str)
    ):
        return copy.deepcopy(existing)
    return proposed


def semantic_manifest_view(manifest: dict) -> dict:
    keys = (
        "repository",
        "authoritative_branch",
        "discovery_branch",
        "branch_mode",
        "latest_handoff",
        "project",
        "current",
        "rules",
        "decisions",
        "dialogues",
        "history",
        "runtime",
        "sync_policy",
    )
    return {key: manifest.get(key) for key in keys}


def working_set_fingerprint(
    target: Path,
    snapshot: dict[str, bytes],
    manifest: dict,
) -> str:
    hasher = hashlib.sha256()
    manifest_view = json.dumps(
        semantic_manifest_view(manifest),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    hasher.update(b"@manifest-semantic\0" + manifest_view + b"\0")

    index = snapshot_json(snapshot, manifest["memory_index"])
    if index is None:
        raise CapsuleError("missing memory index while computing fingerprint")

    paths = [
        *(manifest["project"][key] for key in ("identity", "goals", "architecture", "constraints")),
        *manifest["rules"],
        *(manifest["current"][key] for key in ("state", "blockers", "next")),
        manifest["latest_handoff"],
        manifest["memory_index"],
        *manifest["decisions"],
        *manifest["dialogues"],
        *manifest["history"],
        *(item["path"] for item in index.get("records", []) if isinstance(item, dict) and isinstance(item.get("path"), str)),
    ]
    for rel in sorted(set(paths)):
        hasher.update(rel.encode("utf-8") + b"\0")
        hasher.update(read_bytes(target, snapshot, rel) + b"\0")
    return hasher.hexdigest()


def draft_resume(
    branch: str,
    head: str,
    fingerprint: str,
    bootstrap_review: list[str],
) -> dict:
    evidence = []
    if HEX40.fullmatch(head):
        evidence.append(
            {
                "kind": "commit",
                "reference": head,
                "note": "repository state at capsule installation/migration",
            }
        )
    return {
        "schema": "context-capsule-resume",
        "schema_version": 1,
        "status": "draft",
        "summary": "Context Capsule capture requires reconciliation before continuation.",
        "next_action": "Reconcile repository evidence, fill CAPSULE_TODO documents, then create a ready checkpoint.",
        "verified_branch": branch,
        "verified_head": head if HEX40.fullmatch(head) else "",
        "working_set_sha256": fingerprint,
        "bootstrap_review": list(dict.fromkeys(bootstrap_review)),
        "evidence": evidence,
        "updated_at": utc_now(),
    }


def plan_v13_state(
    target: Path,
    before: dict[str, bytes],
    *,
    repository: str,
    branch: str,
    head: str,
    discovery_branch: str | None,
    legacy_manifest: dict | None,
    previous_metadata: dict | None,
    adopted_from: str | None,
    for_adoption: bool,
) -> tuple[dict[str, bytes], list[str], list[str]]:
    after = dict(before)
    bootstrap_review = install_core_managed_files(after)
    created = seed_project_files(
        target,
        after,
        for_adoption=for_adoption,
    )

    manifest = build_manifest(
        target,
        after,
        repository,
        branch,
        discovery_branch,
        legacy_manifest,
    )
    after[".context/manifest.json"] = json_bytes(manifest)

    existing_index = snapshot_json(before, ".context/index.json")
    index = build_memory_index(
        target,
        after,
        manifest,
        existing_index,
    )
    after[".context/index.json"] = json_bytes(index)

    managed = managed_hashes(after)
    after[".context/capsule.json"] = json_bytes(
        metadata_payload(
            previous_metadata,
            repository,
            VERSION,
            managed,
            adopted_from=adopted_from,
        )
    )

    fingerprint = working_set_fingerprint(target, after, manifest)
    existing_resume = snapshot_json(before, ".context/resume.json")
    if existing_resume is None:
        resume = draft_resume(
            branch,
            head,
            fingerprint,
            bootstrap_review,
        )
    else:
        resume = copy.deepcopy(existing_resume)
        if bootstrap_review:
            prior = (
                resume.get("bootstrap_review")
                if isinstance(resume.get("bootstrap_review"), list)
                else []
            )
            resume["bootstrap_review"] = list(
                dict.fromkeys(
                    [item for item in prior if isinstance(item, str)]
                    + bootstrap_review
                )
            )
            resume["status"] = "draft"
            resume["updated_at"] = utc_now()
    after[".context/resume.json"] = json_bytes(resume)

    return after, created, bootstrap_review


def load_schema(name: str) -> dict:
    path = SCHEMAS / f"{name}.schema.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CapsuleError(f"invalid bundled schema {name}: {exc}") from exc
    if not isinstance(value, dict):
        raise CapsuleError(f"bundled schema {name} must be an object")
    return value


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
    for key in (
        "entrypoint",
        "capsule_metadata",
        "latest_handoff",
        "protocol",
        "resume",
        "memory_index",
    ):
        validate_path(target, snapshot, manifest.get(key), key, errors)

    project = manifest.get("project")
    if isinstance(project, dict):
        for key in ("identity", "goals", "architecture", "constraints"):
            validate_path(
                target,
                snapshot,
                project.get(key),
                f"project.{key}",
                errors,
            )

    current = manifest.get("current")
    if isinstance(current, dict):
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
            continue
        for item in value:
            validate_path(target, snapshot, item, f"{key} item", errors)


def validate_managed_files(
    target: Path,
    snapshot: dict[str, bytes],
    metadata: dict,
    errors: list[str],
) -> None:
    managed = metadata.get("managed_files")
    if not isinstance(managed, dict):
        return

    expected_paths = set(SYSTEM_FILES) | set(TOOL_FILES)
    missing_registration = sorted(expected_paths - set(managed))
    for rel in missing_registration:
        errors.append(f"capsule.json: managed file is not registered: {rel}")

    for rel, expected in managed.items():
        if rel not in expected_paths:
            errors.append(f"capsule.json: unsupported managed path: {rel}")
            continue
        if rel not in snapshot:
            errors.append(f"missing managed file: {rel}")
            continue
        if rel in SYSTEM_FILES:
            try:
                text = snapshot[rel].decode("utf-8")
                block = managed_block(text)
            except (UnicodeDecodeError, ValueError) as exc:
                errors.append(f"invalid managed bootstrap {rel}: {exc}")
                continue
            if block is None:
                errors.append(f"missing managed block: {rel}")
                continue
            actual = sha256(block.encode("utf-8"))
        else:
            actual = canonical_text_sha256(snapshot[rel])
        if actual != expected:
            errors.append(f"managed file integrity mismatch: {rel}")


def validate_memory_index(
    target: Path,
    snapshot: dict[str, bytes],
    manifest: dict,
    index: dict,
    errors: list[str],
    warnings: list[str],
) -> None:
    ids: set[str] = set()
    paths: set[str] = set()
    for item in index.get("records", []):
        if not isinstance(item, dict):
            continue
        record_id = item.get("id")
        rel = item.get("path")
        if isinstance(record_id, str):
            if record_id in ids:
                errors.append(f"index.json: duplicate id: {record_id}")
            ids.add(record_id)
        if isinstance(rel, str):
            if rel in paths:
                errors.append(f"index.json: duplicate path: {rel}")
            paths.add(rel)
            validate_path(target, snapshot, rel, "memory index record", errors)

    declared = set(
        manifest.get("decisions", [])
        + manifest.get("dialogues", [])
        + manifest.get("history", [])
    )
    missing = sorted(declared - paths)
    extra = sorted(paths - declared)
    if missing:
        warnings.append(
            "semantic index missing declared records: " + ", ".join(missing)
        )
    if extra:
        warnings.append(
            "semantic index contains undeclared records: " + ", ".join(extra)
        )


def validate_snapshot(
    target: Path,
    snapshot: dict[str, bytes],
    *,
    authoritative_checkout: str | None = None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    documents: dict[str, dict] = {}

    for name, rel in (
        ("capsule", ".context/capsule.json"),
        ("manifest", ".context/manifest.json"),
        ("index", ".context/index.json"),
        ("resume", ".context/resume.json"),
    ):
        try:
            document = snapshot_json(snapshot, rel)
        except CapsuleError as exc:
            errors.append(str(exc))
            continue
        if document is None:
            errors.append(f"missing {rel}")
            continue
        documents[name] = document
        try:
            errors.extend(
                schema_errors(
                    document,
                    load_schema(name),
                    name,
                )
            )
        except ValueError as exc:
            errors.append(f"schema execution failed for {name}: {exc}")

    if errors:
        return list(dict.fromkeys(errors)), warnings

    metadata = documents["capsule"]
    manifest = documents["manifest"]
    index = documents["index"]
    resume = documents["resume"]

    if metadata.get("version") != VERSION:
        errors.append(
            f"capsule.json: installed version {metadata.get('version')} "
            f"does not match Core {VERSION}; run upgrade"
        )
    if metadata.get("source") != SOURCE:
        errors.append("capsule.json: unexpected source")
    if manifest.get("repository") != metadata.get("repository"):
        errors.append("manifest.json repository does not match capsule.json")

    canonical = {
        "entrypoint": ".context/ENTRYPOINT.md",
        "capsule_metadata": ".context/capsule.json",
        "resume": ".context/resume.json",
        "memory_index": ".context/index.json",
    }
    for key, expected in canonical.items():
        if manifest.get(key) != expected:
            errors.append(
                f"manifest.json: {key} must be canonical path {expected}"
            )

    branch = manifest.get("authoritative_branch")
    discovery = manifest.get("discovery_branch")
    expected_mode = "single" if branch == discovery else "redirect"
    if manifest.get("branch_mode") != expected_mode:
        errors.append("manifest.json: branch_mode disagrees with declared branches")
    if authoritative_checkout and branch != authoritative_checkout:
        errors.append(
            f"manifest.json: authoritative_branch {branch!r} "
            f"does not match checked-out branch {authoritative_checkout!r}"
        )

    validate_references(target, snapshot, manifest, errors)
    validate_managed_files(target, snapshot, metadata, errors)
    validate_memory_index(
        target,
        snapshot,
        manifest,
        index,
        errors,
        warnings,
    )

    if resume.get("verified_branch") != branch:
        warnings.append(
            "resume.json verified_branch differs from current manifest authority"
        )

    runtime = manifest.get("runtime")
    if isinstance(runtime, dict):
        for rel in runtime.get("authoritative_paths", []):
            if not isinstance(rel, str) or not rel:
                continue
            candidate = rel[:-1] if rel.endswith("/") else rel
            try:
                safe_path(target, candidate)
            except ValueError as exc:
                errors.append(f"manifest.json: unsafe runtime path {rel}: {exc}")

    return list(dict.fromkeys(errors)), list(dict.fromkeys(warnings))


def _substantive_markdown(text: str) -> bool:
    if "CAPSULE_TODO" in text:
        return False
    body = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return any(
        line.strip() and not line.lstrip().startswith("#")
        for line in body.splitlines()
    )


def readiness_errors(
    target: Path,
    snapshot: dict[str, bytes],
    manifest: dict,
    resume: dict,
) -> list[str]:
    errors: list[str] = []
    required = [
        *(manifest["project"][key] for key in ("identity", "goals", "architecture", "constraints")),
        *manifest["rules"],
        *(manifest["current"][key] for key in ("state", "blockers", "next")),
        manifest["latest_handoff"],
    ]
    for rel in required:
        try:
            text = read_text(target, snapshot, rel)
        except CapsuleError as exc:
            errors.append(str(exc))
            continue
        if rel.endswith(".md") and not _substantive_markdown(text):
            errors.append(f"unfilled context: {rel}")

    if not resume.get("summary", "").strip():
        errors.append("resume checkpoint summary is empty")
    if not resume.get("next_action", "").strip():
        errors.append("resume checkpoint next_action is empty")
    if resume.get("bootstrap_review"):
        errors.append(
            "custom bootstrap still requires review: "
            + ", ".join(resume["bootstrap_review"])
        )
    if not resume.get("evidence"):
        errors.append("resume checkpoint has no evidence")
    return errors


def branch_exists(target: Path, branch: str) -> bool:
    return bool(
        branch
        and git(
            target,
            "rev-parse",
            "--verify",
            f"{branch}^{{commit}}",
            required=False,
        )
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


def non_capsule_dirty_paths(target: Path) -> list[str]:
    """Return dirty paths outside the capsule without parsing porcelain records.

    Using name-only Git commands avoids quoting/rename/path-prefix ambiguities
    across platforms. The checkpoint only needs to know whether implementation
    state outside the capsule is uncommitted.
    """
    result: list[str] = []
    commands = (
        ("diff", "--name-only"),
        ("diff", "--cached", "--name-only"),
        ("ls-files", "--others", "--exclude-standard"),
    )
    for command in commands:
        output = git(target, *command, required=False)
        for path in output.splitlines():
            path = path.strip()
            if not path:
                continue
            if path in ("AGENTS.md", "AI_CONTEXT.md") or path.startswith(".context/"):
                continue
            result.append(path)
    return list(dict.fromkeys(result))


def mutation_context(target: Path, args: argparse.Namespace):
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
                f"wrong checkout branch: {branch}; requested authority is "
                f"{requested_branch}"
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


def prepare_install(
    target: Path,
    before: dict[str, bytes],
    args: argparse.Namespace,
    branch: str,
    head: str,
) -> tuple[dict[str, bytes], list[str]]:
    if snapshot_json(before, ".context/capsule.json") is not None:
        raise CapsuleError(
            "Context Capsule is already installed; use validate/upgrade/repair."
        )
    context = safe_path(target, ".context")
    if context.exists():
        raise CapsuleError(
            "Existing .context/ found without capsule metadata; use adopt for "
            "the temporary legacy transition."
        )
    if not valid_repository(args.repository):
        raise CapsuleError("--repository must be in owner/name form")

    after, created, review = plan_v13_state(
        target,
        before,
        repository=args.repository,
        branch=branch,
        head=head,
        discovery_branch=args.discovery_branch,
        legacy_manifest=None,
        previous_metadata=None,
        adopted_from=None,
        for_adoption=False,
    )
    messages = [f"  + {item}" for item in created]
    messages.extend(
        f"  ! preserved custom bootstrap for review: {item}"
        for item in review
    )
    messages.extend(
        [
            "  + .context/capsule.json",
            "  + .context/manifest.json",
            "  + .context/index.json",
            "  + .context/resume.json (draft)",
            "  + repository-local runtime and schemas",
        ]
    )
    return after, messages


def prepare_adopt(
    target: Path,
    before: dict[str, bytes],
    args: argparse.Namespace,
    branch: str,
    head: str,
) -> tuple[dict[str, bytes], list[str]]:
    if snapshot_json(before, ".context/capsule.json") is not None:
        raise CapsuleError(
            "This repository already has capsule metadata; use validate/upgrade/repair."
        )
    context = safe_path(target, ".context")
    if not context.exists() or not context.is_dir():
        raise CapsuleError("No legacy .context/ found; use install for a clean repository.")
    if not valid_repository(args.repository):
        raise CapsuleError("--repository must be in owner/name form")

    legacy = snapshot_json(before, ".context/manifest.json") or {}
    after, created, review = plan_v13_state(
        target,
        before,
        repository=args.repository,
        branch=branch,
        head=head,
        discovery_branch=args.discovery_branch,
        legacy_manifest=legacy,
        previous_metadata=None,
        adopted_from="legacy",
        for_adoption=True,
    )
    messages = [f"  + {item}" for item in created]
    messages.extend(
        f"  ! preserved custom bootstrap for review: {item}"
        for item in review
    )
    messages.append("  ~ legacy manifest preserved and enriched to v3")
    messages.append("  + continuation checkpoint remains draft until reconciled")
    return after, messages


def prepare_repair(
    target: Path,
    before: dict[str, bytes],
    args: argparse.Namespace,
    branch: str,
    head: str,
) -> tuple[dict[str, bytes], list[str]]:
    metadata = snapshot_json(before, ".context/capsule.json")
    if metadata is None:
        raise CapsuleError(
            "No installed capsule metadata found; use install or adopt instead."
        )
    if metadata.get("version") != VERSION:
        raise CapsuleError(
            f"installed capsule is {metadata.get('version')}; run upgrade before repair"
        )
    if not valid_repository(metadata.get("repository")):
        raise CapsuleError("capsule.json repository is invalid")

    legacy = snapshot_json(before, ".context/manifest.json") or {}
    after, created, review = plan_v13_state(
        target,
        before,
        repository=metadata["repository"],
        branch=branch,
        head=head,
        discovery_branch=args.discovery_branch,
        legacy_manifest=legacy,
        previous_metadata=metadata,
        adopted_from=None,
        for_adoption=True,
    )
    messages = (
        [f"  + restored {item}" for item in created]
        if created
        else ["No missing project seed files found."]
    )
    messages.extend(
        f"  ! preserved custom bootstrap for review: {item}"
        for item in review
    )
    messages.append("  ~ managed runtime/bootstrap refreshed non-destructively")
    return after, messages


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
    head: str,
) -> tuple[dict[str, bytes], list[str]]:
    metadata = snapshot_json(before, ".context/capsule.json")
    if metadata is None:
        raise CapsuleError("No installed capsule metadata found; use install or adopt.")
    installed = metadata.get("version")
    if not isinstance(installed, str):
        raise CapsuleError("capsule.json version is invalid")
    if installed == VERSION:
        return dict(before), [f"Already on Context Capsule {VERSION}."]

    registry = migration_registry()
    migrations = registry["migrations"]
    current = installed
    seen: set[str] = set()
    messages: list[str] = []
    supported = {
        "builtin:1.0.0-to-1.1.0",
        "builtin:1.1.0-to-1.2.0",
        "builtin:1.2.0-to-1.3.0",
    }

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
        if operation not in supported or not isinstance(next_version, str):
            raise CapsuleError(
                f"unsupported migration operation: {operation}",
                4,
            )
        messages.append(f"  migrate {current} -> {next_version}")
        current = next_version

    legacy = snapshot_json(before, ".context/manifest.json") or {}
    after, created, review = plan_v13_state(
        target,
        before,
        repository=metadata["repository"],
        branch=branch,
        head=head,
        discovery_branch=args.discovery_branch,
        legacy_manifest=legacy,
        previous_metadata=metadata,
        adopted_from=None,
        for_adoption=True,
    )
    messages.extend(f"  + {item}" for item in created)
    messages.extend(
        f"  ! preserved custom bootstrap for review: {item}"
        for item in review
    )
    messages.append(
        f"Upgraded Context Capsule {installed} -> {VERSION} atomically; "
        "resume checkpoint is draft until reconciled."
    )
    return after, messages


def prepare_checkpoint(
    target: Path,
    before: dict[str, bytes],
    args: argparse.Namespace,
    branch: str,
    head: str,
) -> tuple[dict[str, bytes], list[str]]:
    metadata = snapshot_json(before, ".context/capsule.json")
    manifest = snapshot_json(before, ".context/manifest.json")
    index = snapshot_json(before, ".context/index.json")
    previous = snapshot_json(before, ".context/resume.json")
    if not all((metadata, manifest, index, previous)):
        raise CapsuleError("checkpoint requires a complete v1.3 capsule")
    if metadata["version"] != VERSION:
        raise CapsuleError("upgrade the capsule before creating a checkpoint")
    if manifest["authoritative_branch"] != branch:
        raise CapsuleError(
            f"wrong checkout branch: {branch}; context authority is "
            f"{manifest['authoritative_branch']}"
        )

    after = dict(before)
    resume = copy.deepcopy(previous)
    resume["status"] = "ready" if args.ready else "draft"
    resume["summary"] = args.summary
    resume["next_action"] = args.next_action
    resume["verified_branch"] = branch
    resume["verified_head"] = head

    evidence: list[dict] = []
    for rel in args.evidence_file:
        if not planned_exists(target, after, rel):
            raise CapsuleError(f"checkpoint evidence file does not exist: {rel}")
        evidence.append({"kind": "file", "reference": rel})
    for commit in args.evidence_commit:
        if not git(
            target,
            "rev-parse",
            "--verify",
            f"{commit}^{{commit}}",
            required=False,
        ):
            raise CapsuleError(f"checkpoint evidence commit does not exist: {commit}")
        evidence.append({"kind": "commit", "reference": commit})
    if not evidence:
        evidence.append(
            {
                "kind": "commit",
                "reference": head,
                "note": "implementation state reconciled for this checkpoint",
            }
        )
    resume["evidence"] = evidence

    prior_review = (
        resume.get("bootstrap_review")
        if isinstance(resume.get("bootstrap_review"), list)
        else []
    )
    resume["bootstrap_review"] = (
        []
        if args.clear_bootstrap_review
        else [item for item in prior_review if isinstance(item, str)]
    )
    resume["working_set_sha256"] = working_set_fingerprint(
        target,
        after,
        manifest,
    )
    resume["updated_at"] = utc_now()

    if args.ready:
        outside = non_capsule_dirty_paths(target)
        if outside:
            raise CapsuleError(
                "cannot mark checkpoint ready while non-context repository files "
                "are uncommitted: " + ", ".join(outside)
            )
        ready_errors = readiness_errors(target, after, manifest, resume)
        if ready_errors:
            raise CapsuleError(
                "checkpoint is not ready:\n  - " + "\n  - ".join(ready_errors)
            )

    after[".context/resume.json"] = json_bytes(resume)
    return after, [
        f"Continuation checkpoint set to {resume['status']}.",
        f"  verified HEAD: {head}",
        f"  working-set fingerprint: {resume['working_set_sha256']}",
    ]


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
                    f"{label} is {size} bytes (> {limit}); compact resolved/history material"
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
                "review them for semantic changes"
            )
    except Exception:
        return None
    return None


def validate_target(
    target: Path,
    *,
    quiet: bool = False,
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


def audit_target(target: Path, *, require_ready: bool = False) -> int:
    structural = validate_target(target, quiet=True)
    if structural:
        validate_target(target, quiet=False)
        return structural

    try:
        from runtime.capsule_runtime import inspect

        result = inspect(target, schemas=SCHEMAS)
    except Exception as exc:
        print("Context Capsule audit: FAIL")
        print(f"  - runtime inspection failed: {exc}")
        return 1

    manifest = snapshot_json(inventory(target), ".context/manifest.json")
    warnings = list(result["warnings"])
    if isinstance(manifest, dict):
        warnings.extend(compactness_warnings(target, manifest))
    lag = context_git_lag_warning(target)
    if lag:
        warnings.append(lag)

    if result["errors"]:
        print("Context Capsule audit: FAIL")
        for error in result["errors"]:
            print(f"  - {error}")
        return 1

    print("Context Capsule audit: OK")
    for item in result["readiness"]:
        print(f"  ? readiness: {item}")
    for warning in dict.fromkeys(warnings):
        print(f"  ! {warning}")
    if require_ready and result["readiness"]:
        return 2
    return 0


def run_mutation(
    args: argparse.Namespace,
    planner,
    success_header: str | None = None,
) -> int:
    target = repo_root(args.target)
    lock = None
    try:
        lock, gitdir, head, branch, before = mutation_context(target, args)
        after, messages = planner(target, before, args, branch, head)

        errors, warnings = validate_snapshot(
            target,
            after,
            authoritative_checkout=branch,
        )
        manifest = snapshot_json(after, ".context/manifest.json")
        if manifest:
            discovery = manifest.get("discovery_branch")
            if (
                isinstance(discovery, str)
                and discovery != branch
                and not branch_exists(target, discovery)
            ):
                errors.append(
                    f"manifest.json: discovery branch does not exist locally: "
                    f"{discovery}"
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


def checkpoint(args: argparse.Namespace) -> int:
    code = run_mutation(args, prepare_checkpoint)
    if code == 0 and args.ready:
        return audit_target(repo_root(args.target), require_ready=True)
    return code


def validate(args: argparse.Namespace) -> int:
    return validate_target(repo_root(args.target), quiet=False)


def audit(args: argparse.Namespace) -> int:
    return audit_target(repo_root(args.target), require_ready=args.ready)


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
            "allow pre-existing uncommitted AGENTS.md, AI_CONTEXT.md or .context "
            "changes; concurrent edits are still rejected"
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
    p_install.add_argument("--repository", required=True)
    p_install.set_defaults(func=install)

    p_adopt = sub.add_parser(
        "adopt",
        help="temporarily adopt an existing legacy .context without overwriting memory",
    )
    add_common_target(p_adopt)
    add_mutating_options(p_adopt)
    p_adopt.add_argument("--repository", required=True)
    p_adopt.set_defaults(func=adopt)

    p_validate = sub.add_parser("validate", help="strict structural validation")
    add_common_target(p_validate)
    p_validate.set_defaults(func=validate)

    p_audit = sub.add_parser(
        "audit",
        help="validation plus readiness, compactness and Git freshness checks",
    )
    add_common_target(p_audit)
    p_audit.add_argument(
        "--ready",
        action="store_true",
        help="return a non-zero status when continuation readiness is incomplete",
    )
    p_audit.set_defaults(func=audit)

    p_repair = sub.add_parser(
        "repair",
        help="repair current-version managed structure without overwriting project memory",
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

    p_checkpoint = sub.add_parser(
        "checkpoint",
        help="write an evidence-backed continuation checkpoint",
    )
    add_common_target(p_checkpoint)
    add_mutating_options(p_checkpoint)
    p_checkpoint.set_defaults(allow_dirty_context=True)
    p_checkpoint.add_argument("--summary", required=True)
    p_checkpoint.add_argument("--next-action", required=True)
    p_checkpoint.add_argument("--ready", action="store_true")
    p_checkpoint.add_argument(
        "--clear-bootstrap-review",
        action="store_true",
        help="confirm preserved pre-existing bootstrap instructions have been reviewed",
    )
    p_checkpoint.add_argument(
        "--evidence-file",
        action="append",
        default=[],
    )
    p_checkpoint.add_argument(
        "--evidence-commit",
        action="append",
        default=[],
    )
    p_checkpoint.set_defaults(func=checkpoint)

    return parser


def main() -> int:
    args = build_parser().parse_args()
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
