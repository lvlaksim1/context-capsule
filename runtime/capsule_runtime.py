#!/usr/bin/env python3
"""Repository-local Context Capsule readiness and recovery tooling.

This file is copied into each installed repository together with contracts.py
and the bundled schemas. It performs read-only checks and never contacts Core.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    from contracts import load_json, managed_block, safe_path, schema_errors
except ModuleNotFoundError:
    from runtime.contracts import load_json, managed_block, safe_path, schema_errors

SYSTEM = (
    "AGENTS.md",
    "AI_CONTEXT.md",
    ".context/ENTRYPOINT.md",
    ".context/protocol.md",
)
CAPSULE_SCOPE_PREFIXES = (".context/",)
CAPSULE_SCOPE_FILES = {"AGENTS.md", "AI_CONTEXT.md"}


def git(root: Path, *args: str) -> str:
    process = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
    )
    return process.stdout.strip() if process.returncode == 0 else ""


def git_success(root: Path, *args: str) -> bool:
    return (
        subprocess.run(
            ["git", "-C", str(root), *args],
            text=True,
            capture_output=True,
        ).returncode
        == 0
    )


def read_bytes(root: Path, rel: str, fallback: Path | None = None) -> bytes:
    path = safe_path(root, rel)
    if not path.exists() and fallback is not None:
        path = safe_path(fallback, rel)
    if not path.is_file():
        raise ValueError(f"missing context file: {rel}")
    return path.read_bytes()


def read(root: Path, rel: str, fallback: Path | None = None) -> str:
    return read_bytes(root, rel, fallback).decode("utf-8")


def canonical_text_sha256(data: bytes) -> str:
    text = data.decode("utf-8")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def required_paths(manifest: dict) -> list[str]:
    return list(
        dict.fromkeys(
            [
                ".context/ENTRYPOINT.md",
                ".context/manifest.json",
                manifest["protocol"],
                *(
                    manifest["project"][key]
                    for key in ("identity", "goals", "architecture", "constraints")
                ),
                *manifest["rules"],
                *(
                    manifest["current"][key]
                    for key in ("state", "blockers", "next")
                ),
                manifest["latest_handoff"],
                manifest["memory_index"],
            ]
        )
    )


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


def fingerprint(
    root: Path,
    manifest: dict,
    fallback: Path | None = None,
) -> str:
    """Hash durable project semantics while ignoring purely technical refreshes."""
    hasher = hashlib.sha256()
    manifest_view = json.dumps(
        semantic_manifest_view(manifest),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    hasher.update(b"@manifest-semantic\0" + manifest_view + b"\0")

    index = json.loads(read(root, manifest["memory_index"], fallback))
    paths = [
        *(manifest["project"][key] for key in ("identity", "goals", "architecture", "constraints")),
        *manifest["rules"],
        *(manifest["current"][key] for key in ("state", "blockers", "next")),
        manifest["latest_handoff"],
        manifest["memory_index"],
        *manifest["decisions"],
        *manifest["dialogues"],
        *manifest["history"],
        *(item["path"] for item in index["records"]),
    ]

    for rel in sorted(set(paths)):
        hasher.update(
            rel.encode("utf-8")
            + b"\0"
            + read(root, rel, fallback).encode("utf-8")
            + b"\0"
        )
    return hasher.hexdigest()

def _schema(root: Path, name: str, directory: Path | None) -> dict:
    if directory:
        return load_json(directory / f"{name}.schema.json")
    return load_json(
        safe_path(
            root,
            f".context/tools/schemas/{name}.schema.json",
            exists=True,
        )
    )


def _substantive_markdown(text: str) -> bool:
    body = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    substantive = "\n".join(
        line
        for line in body.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )
    return bool(substantive.strip()) and "CAPSULE_TODO" not in text


def _context_only_paths(paths: list[str]) -> bool:
    if not paths:
        return True
    for rel in paths:
        rel = rel.strip()
        if not rel:
            continue
        if rel in CAPSULE_SCOPE_FILES:
            continue
        if rel.startswith(CAPSULE_SCOPE_PREFIXES):
            continue
        return False
    return True


def _head_freshness(root: Path, verified_head: str, current_head: str) -> str | None:
    if not verified_head or not re.fullmatch(r"[0-9a-f]{40}", verified_head):
        return "checkpoint has no verified Git commit"
    if not current_head:
        return "current Git HEAD is unavailable"
    if verified_head == current_head:
        return None
    if not git_success(
        root,
        "merge-base",
        "--is-ancestor",
        verified_head,
        current_head,
    ):
        return (
            f"checkpoint commit {verified_head} is not an ancestor of current HEAD "
            f"{current_head}; reconcile repository history"
        )

    changed = git(root, "diff", "--name-only", f"{verified_head}..{current_head}")
    paths = [line for line in changed.splitlines() if line.strip()]
    if _context_only_paths(paths):
        return None
    return (
        f"implementation changed after checkpoint {verified_head}; "
        "reconcile these commits before continuing"
    )


def inspect(
    root: Path,
    *,
    schemas: Path | None = None,
    fallback: Path | None = None,
    check_git: bool = True,
) -> dict:
    errors: list[str] = []
    readiness: list[str] = []
    warnings: list[str] = []
    documents: dict[str, dict] = {}

    for name, rel in (
        ("capsule", ".context/capsule.json"),
        ("manifest", ".context/manifest.json"),
    ):
        try:
            documents[name] = json.loads(read(root, rel, fallback))
            errors.extend(
                schema_errors(
                    documents[name],
                    _schema(root, name, schemas),
                    name,
                )
            )
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            errors.append(str(exc))

    if errors:
        return {
            "errors": list(dict.fromkeys(errors)),
            "readiness": readiness,
            "warnings": warnings,
        }

    meta = documents["capsule"]
    manifest = documents["manifest"]

    if meta["repository"] != manifest["repository"]:
        errors.append("repository identity differs between capsule and manifest")

    expected_mode = (
        "single"
        if manifest["authoritative_branch"] == manifest["discovery_branch"]
        else "redirect"
    )
    if manifest["branch_mode"] != expected_mode:
        errors.append("branch_mode disagrees with the declared branches")

    canonical = {
        "entrypoint": ".context/ENTRYPOINT.md",
        "capsule_metadata": ".context/capsule.json",
        "resume": ".context/resume.json",
        "memory_index": ".context/index.json",
    }
    for name, expected in canonical.items():
        if manifest[name] != expected:
            errors.append(f"unexpected canonical {name}: {manifest[name]}")

    paths = required_paths(manifest) + sum(
        (manifest[key] for key in ("decisions", "dialogues", "history")),
        [],
    )
    texts: dict[str, str] = {}
    for rel in paths:
        try:
            texts[rel] = read(root, rel, fallback)
        except (ValueError, OSError) as exc:
            errors.append(str(exc))

    for rel in SYSTEM:
        try:
            text = read(root, rel, fallback)
            block = managed_block(text)
            expected = meta["managed_files"].get(rel)
            if expected is None:
                errors.append(f"managed bootstrap is not registered: {rel}")
            elif (
                block is None
                or hashlib.sha256(block.encode("utf-8")).hexdigest() != expected
            ):
                errors.append(f"missing or changed managed bootstrap: {rel}")
        except (ValueError, OSError) as exc:
            errors.append(str(exc))

    for rel, expected in meta["managed_files"].items():
        if rel in SYSTEM:
            continue
        try:
            if not rel.startswith(".context/tools/"):
                raise ValueError(f"unsupported managed path: {rel}")
            actual = canonical_text_sha256(
                read_bytes(root, rel, fallback)
            )
            if actual != expected:
                errors.append(f"installed tool integrity mismatch: {rel}")
        except (ValueError, OSError) as exc:
            errors.append(str(exc))

    for rel in manifest["runtime"]["authoritative_paths"]:
        try:
            candidate = rel[:-1] if rel.endswith("/") else rel
            path = safe_path(root, candidate)
            if not path.exists():
                warnings.append(
                    f"runtime authority unavailable locally: {rel}; verify live source"
                )
        except ValueError as exc:
            errors.append(str(exc))

    for name, key in (("resume", "resume"), ("index", "memory_index")):
        try:
            documents[name] = json.loads(read(root, manifest[key], fallback))
            errors.extend(
                schema_errors(
                    documents[name],
                    _schema(root, name, schemas),
                    name,
                )
            )
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            errors.append(str(exc))

    if errors:
        return {
            "errors": list(dict.fromkeys(errors)),
            "readiness": readiness,
            "warnings": list(dict.fromkeys(warnings)),
        }

    index = documents["index"]
    checkpoint = documents["resume"]

    ids: set[str] = set()
    indexed_paths: set[str] = set()
    for record in index["records"]:
        if record["id"] in ids:
            errors.append(f"duplicate memory id: {record['id']}")
        ids.add(record["id"])
        if record["path"] in indexed_paths:
            errors.append(f"duplicate memory path: {record['path']}")
        indexed_paths.add(record["path"])
        try:
            read(root, record["path"], fallback)
        except (ValueError, OSError) as exc:
            errors.append(str(exc))

    declared_memory = set(
        manifest["decisions"] + manifest["dialogues"] + manifest["history"]
    )
    missing_index = sorted(declared_memory - indexed_paths)
    extra_index = sorted(indexed_paths - declared_memory)
    if missing_index:
        readiness.append(
            "durable records missing from semantic index: "
            + ", ".join(missing_index)
        )
    if extra_index:
        readiness.append(
            "semantic index references undeclared durable records: "
            + ", ".join(extra_index)
        )

    if not manifest["rules"]:
        readiness.append("no project rules indexed")

    for rel in required_paths(manifest):
        text = texts.get(rel, "")
        if rel.endswith(".md") and not _substantive_markdown(text):
            readiness.append(f"unfilled context: {rel}")

    if checkpoint["verified_branch"] != manifest["authoritative_branch"]:
        readiness.append(
            "checkpoint verified_branch differs from manifest authority"
        )
    if checkpoint["status"] != "ready":
        readiness.append(
            "checkpoint is draft; reconcile evidence and complete resume.json"
        )
    if checkpoint["bootstrap_review"]:
        readiness.append(
            "review preserved custom bootstrap: "
            + ", ".join(checkpoint["bootstrap_review"])
        )
    if not checkpoint["summary"].strip() or not checkpoint["next_action"].strip():
        readiness.append(
            "checkpoint must state the verified position and the next action"
        )
    if not checkpoint["evidence"]:
        readiness.append("checkpoint has no evidence")

    for item in checkpoint["evidence"]:
        if item["kind"] == "file":
            try:
                read(root, item["reference"], fallback)
            except (ValueError, OSError) as exc:
                readiness.append(str(exc))
        elif (
            check_git
            and item["kind"] == "commit"
            and not git_success(
                root,
                "rev-parse",
                "--verify",
                item["reference"] + "^{commit}",
            )
        ):
            readiness.append(
                "commit evidence is unavailable: " + item["reference"]
            )

    try:
        actual_digest = fingerprint(root, manifest, fallback)
        if checkpoint["working_set_sha256"] != actual_digest:
            readiness.append(
                "context changed since checkpoint; reconcile and refresh its fingerprint"
            )
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        errors.append(str(exc))

    if check_git:
        branch = git(root, "branch", "--show-current")
        if branch and branch != manifest["authoritative_branch"]:
            errors.append(
                f"wrong branch: {branch}; context authority is "
                f"{manifest['authoritative_branch']}"
            )
        elif not branch:
            warnings.append(
                "no named Git branch available; verify authority before writing"
            )

        head = git(root, "rev-parse", "HEAD")
        freshness = _head_freshness(root, checkpoint["verified_head"], head)
        if freshness:
            readiness.append(freshness)

        if git(root, "rev-parse", "--is-shallow-repository") == "true":
            warnings.append(
                "shallow history: checkpoint ancestry cannot be fully assessed"
            )

    for key in ("state", "blockers", "next"):
        rel = manifest["current"][key]
        if len(texts.get(rel, "").encode("utf-8")) > 12_000:
            warnings.append(
                f"oversized current document: {rel}; "
                "move resolved work into history"
            )

    return {
        "errors": list(dict.fromkeys(errors)),
        "readiness": list(dict.fromkeys(readiness)),
        "warnings": list(dict.fromkeys(warnings)),
    }


def recovery_pack(
    root: Path,
    task: str = "",
    max_bytes: int = 48_000,
    max_records: int = 3,
) -> str:
    result = inspect(root)
    if result["errors"] or result["readiness"]:
        raise ValueError(
            "context is not ready:\n"
            + "\n".join(result["errors"] + result["readiness"])
        )

    manifest = json.loads(read(root, ".context/manifest.json"))
    index = json.loads(read(root, manifest["memory_index"]))

    paths = [
        ".context/capsule.json",
        *required_paths(manifest),
        manifest["resume"],
    ]
    # The index routes optional history; do not spend recovery budget rendering it.
    paths = [path for path in paths if path != manifest["memory_index"]]
    paths = list(dict.fromkeys(paths))

    warnings = "\n".join(
        "LIVE CHECK: " + warning for warning in result["warnings"]
    )
    prefix = "# Repository recovery pack\n\n" + warnings + "\n"
    chunks = [prefix] + [
        f"\n--- {path} ---\n{read(root, path)}" for path in paths
    ]
    used = len("".join(chunks).encode("utf-8"))
    if used > max_bytes:
        raise ValueError(
            f"mandatory context needs {used} bytes, budget is {max_bytes}; "
            "compact it, never silently omit constraints"
        )

    terms = set(re.findall(r"\w+", task.casefold()))
    scored: list[tuple[int, str, dict]] = []
    for item in index["records"]:
        cues = " ".join(
            [item["title"], item["summary"], *item["tags"]]
        )
        cue_terms = set(re.findall(r"\w+", cues.casefold()))
        score = len(terms & cue_terms)
        bootstrap = "bootstrap" in {
            tag.casefold() for tag in item["tags"]
        }
        if item["status"] == "active" and (score or bootstrap):
            scored.append((-(score + (1 if bootstrap else 0)), item["id"], item))

    for _, _, item in sorted(scored)[:max_records]:
        if item["path"] in paths:
            continue
        chunk = (
            f"\n--- {item['path']} [{item['id']}] ---\n"
            f"{read(root, item['path'])}"
        )
        if used + len(chunk.encode("utf-8")) > max_bytes:
            raise ValueError(
                f"selected memory {item['id']} exceeds budget; "
                "narrow the task or increase budget explicitly"
            )
        chunks.append(chunk)
        used += len(chunk.encode("utf-8"))

    return "".join(chunks)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("check", "resume", "fingerprint"),
    )
    parser.add_argument(
        "--target",
        default=str(Path(__file__).resolve().parents[2]),
    )
    parser.add_argument("--ready", action="store_true")
    parser.add_argument("--task", default="")
    parser.add_argument("--max-bytes", type=int, default=48_000)
    parser.add_argument("--max-records", type=int, default=3)
    args = parser.parse_args()
    root = Path(args.target).resolve()

    try:
        if args.command == "fingerprint":
            print(
                fingerprint(
                    root,
                    json.loads(read(root, ".context/manifest.json")),
                )
            )
            return 0
        if args.command == "resume":
            print(
                recovery_pack(
                    root,
                    args.task,
                    args.max_bytes,
                    args.max_records,
                )
            )
            return 0

        result = inspect(root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return (
            1
            if result["errors"]
            else 2
            if args.ready and result["readiness"]
            else 0
        )
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"Context Capsule: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
