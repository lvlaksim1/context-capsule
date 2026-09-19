#!/usr/bin/env python3
"""Repository-local, read-only recovery tools. No Core access or third-party packages."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from contracts import load_json, managed_block, safe_path, schema_errors

SYSTEM = ("AGENTS.md", "AI_CONTEXT.md", ".context/ENTRYPOINT.md", ".context/protocol.md")


def git(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    return p.stdout.strip() if p.returncode == 0 else ""


def read(root: Path, rel: str, fallback: Path | None = None) -> str:
    path = safe_path(root, rel)
    if not path.exists() and fallback is not None:
        path = safe_path(fallback, rel)
    if not path.is_file():
        raise ValueError(f"missing context file: {rel}")
    return path.read_text(encoding="utf-8")


def required_paths(manifest: dict) -> list[str]:
    return list(dict.fromkeys([
        ".context/ENTRYPOINT.md", ".context/manifest.json", manifest["protocol"],
        *(manifest["project"][k] for k in ("identity", "goals", "architecture", "constraints")),
        *manifest["rules"], *(manifest["current"][k] for k in ("state", "blockers", "next")),
        manifest["latest_handoff"], manifest["memory_index"],
    ]))


def fingerprint(root: Path, manifest: dict, fallback: Path | None = None) -> str:
    h = hashlib.sha256()
    # All indexed durable records are included: changing a decision invalidates the checkpoint.
    paths = required_paths(manifest) + sum((manifest[k] for k in ("decisions", "dialogues", "history")), [])
    index = json.loads(read(root, manifest["memory_index"], fallback))
    paths += [item["path"] for item in index["records"]]
    for rel in sorted(set(paths)):
        h.update(rel.encode() + b"\0" + read(root, rel, fallback).encode() + b"\0")
    return h.hexdigest()


def _schema(root: Path, name: str, directory: Path | None) -> dict:
    if directory:
        return load_json(directory / f"{name}.schema.json")
    return load_json(safe_path(root, f".context/tools/schemas/{name}.schema.json", exists=True))


def inspect(root: Path, *, schemas: Path | None = None, fallback: Path | None = None,
            check_git: bool = True) -> dict:
    errors, readiness, warnings = [], [], []
    documents = {}
    for name, rel in (("capsule", ".context/capsule.json"), ("manifest", ".context/manifest.json")):
        try:
            documents[name] = json.loads(read(root, rel, fallback))
            errors.extend(schema_errors(documents[name], _schema(root, name, schemas), name))
        except (ValueError, OSError) as exc:
            errors.append(str(exc))
    if errors:
        return {"errors": errors, "readiness": readiness, "warnings": warnings}
    meta, manifest = documents["capsule"], documents["manifest"]
    if meta["repository"] != manifest["repository"]:
        errors.append("repository identity differs between capsule and manifest")
    expected_mode = "single" if manifest["authoritative_branch"] == manifest["discovery_branch"] else "redirect"
    if manifest["branch_mode"] != expected_mode:
        errors.append("branch_mode disagrees with the declared branches")
    for name in ("entrypoint", "capsule_metadata"):
        if manifest[name] != {"entrypoint": ".context/ENTRYPOINT.md", "capsule_metadata": ".context/capsule.json"}[name]:
            errors.append(f"unexpected canonical {name}")
    paths = required_paths(manifest) + sum((manifest[k] for k in ("decisions", "dialogues", "history")), [])
    texts = {}
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
            if block is None or hashlib.sha256(block.encode()).hexdigest() != expected:
                errors.append(f"missing or changed managed bootstrap: {rel}")
        except (ValueError, OSError) as exc:
            errors.append(str(exc))
    for rel, expected in meta["managed_files"].items():
        if rel in SYSTEM:
            continue
        try:
            if not rel.startswith(".context/tools/"):
                raise ValueError(f"unsupported managed path: {rel}")
            if hashlib.sha256(read(root, rel, fallback).encode()).hexdigest() != expected:
                errors.append(f"installed tool integrity mismatch: {rel}")
        except (ValueError, OSError) as exc:
            errors.append(str(exc))
    for rel in manifest["runtime"]["authoritative_paths"]:
        try:
            p = safe_path(fallback or root, rel)
            if not p.exists():
                warnings.append(f"runtime authority unavailable locally: {rel}; verify live source")
        except ValueError as exc:
            errors.append(str(exc))
    for name, key in (("resume", "resume"), ("index", "memory_index")):
        try:
            documents[name] = json.loads(read(root, manifest[key], fallback))
            errors.extend(schema_errors(documents[name], _schema(root, name, schemas), name))
        except (ValueError, OSError) as exc:
            errors.append(str(exc))
    if errors:
        return {"errors": errors, "readiness": readiness, "warnings": warnings}
    index, checkpoint = documents["index"], documents["resume"]
    ids = set()
    for record in index["records"]:
        if record["id"] in ids:
            errors.append(f"duplicate memory id: {record['id']}")
        ids.add(record["id"])
        try:
            read(root, record["path"], fallback)
        except (ValueError, OSError) as exc:
            errors.append(str(exc))
    if not manifest["rules"]:
        readiness.append("no project rules indexed")
    for rel in required_paths(manifest):
        text = texts.get(rel, "")
        if rel.endswith(".md"):
            body = re.sub(r"<!--.*?-->", "", text, flags=re.S)
            substantive = "\n".join(line for line in body.splitlines() if line.strip() and not line.lstrip().startswith("#"))
            if not substantive.strip() or "CAPSULE_TODO" in text:
                readiness.append(f"unfilled context: {rel}")
    if checkpoint["status"] != "ready":
        readiness.append("checkpoint is draft; reconcile evidence and complete resume.json")
    if checkpoint["bootstrap_review"]:
        readiness.append("review preserved custom bootstrap: " + ", ".join(checkpoint["bootstrap_review"]))
    if not checkpoint["summary"].strip() or not checkpoint["next_action"].strip():
        readiness.append("checkpoint must state the verified position and the next action")
    if not re.fullmatch(r"[0-9a-f]{40}", checkpoint["verified_head"]):
        readiness.append("checkpoint has no verified Git commit")
    if not checkpoint["evidence"]:
        readiness.append("checkpoint has no evidence")
    for item in checkpoint["evidence"]:
        if item["kind"] == "file":
            try:
                read(root, item["reference"], fallback)
            except (ValueError, OSError) as exc:
                readiness.append(str(exc))
        if check_git and item["kind"] == "commit" and not git(root, "rev-parse", "--verify", item["reference"] + "^{commit}"):
            readiness.append("commit evidence is unavailable: " + item["reference"])
    try:
        actual_digest = fingerprint(root, manifest, fallback)
        if checkpoint["working_set_sha256"] != actual_digest:
            readiness.append("context changed since checkpoint; reconcile and refresh its fingerprint")
    except (ValueError, OSError, KeyError) as exc:
        errors.append(str(exc))
    if check_git:
        branch = git(root, "branch", "--show-current")
        if branch and branch != manifest["authoritative_branch"]:
            errors.append(f"wrong branch: {branch}; context authority is {manifest['authoritative_branch']}")
        elif not branch:
            warnings.append("no named Git branch available; verify authority before writing")
        head = git(root, "rev-parse", "HEAD")
        if head and head != checkpoint["verified_head"]:
            warnings.append(f"HEAD {head} differs from checkpoint; inspect intervening changes before continuing")
        if git(root, "rev-parse", "--is-shallow-repository") == "true":
            warnings.append("shallow history: freshness/ancestry cannot be fully assessed")
    for key in ("state", "blockers", "next"):
        rel = manifest["current"][key]
        if len(texts.get(rel, "").encode()) > 12000:
            warnings.append(f"oversized current document: {rel}; move resolved work into history")
    return {"errors": errors, "readiness": list(dict.fromkeys(readiness)), "warnings": warnings}


def recovery_pack(root: Path, task: str = "", max_bytes: int = 48000, max_records: int = 3) -> str:
    result = inspect(root)
    if result["errors"] or result["readiness"]:
        raise ValueError("context is not ready:\n" + "\n".join(result["errors"] + result["readiness"]))
    manifest = json.loads(read(root, ".context/manifest.json"))
    index = json.loads(read(root, manifest["memory_index"]))
    paths = [".context/capsule.json", *required_paths(manifest), manifest["resume"]]
    # Index itself is a routing input. Return selected records instead of the whole index.
    paths = [p for p in paths if p != manifest["memory_index"]]
    warnings = "\n".join("LIVE CHECK: " + w for w in result["warnings"])
    prefix = "# Repository recovery pack\n\n" + warnings + "\n"
    chunks = [prefix] + [f"\n--- {p} ---\n{read(root, p)}" for p in paths]
    used = len("".join(chunks).encode())
    if used > max_bytes:
        raise ValueError(f"mandatory context needs {used} bytes, budget is {max_bytes}; compact it, never silently omit constraints")
    terms = set(re.findall(r"\w+", task.casefold()))
    scored = []
    for item in index["records"]:
        cues = " ".join([item["title"], item["summary"], *item["tags"]])
        score = len(terms & set(re.findall(r"\w+", cues.casefold())))
        if item["status"] == "active" and score:
            scored.append((-score, item["id"], item))
    for _, _, item in sorted(scored)[:max_records]:
        if item["path"] in paths:
            continue
        chunk = f"\n--- {item['path']} [{item['id']}] ---\n{read(root, item['path'])}"
        if used + len(chunk.encode()) > max_bytes:
            raise ValueError(f"selected memory {item['id']} exceeds budget; narrow the task or increase budget explicitly")
        chunks.append(chunk)
        used += len(chunk.encode())
    return "".join(chunks)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "resume", "fingerprint"))
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--ready", action="store_true")
    parser.add_argument("--task", default="")
    parser.add_argument("--max-bytes", type=int, default=48000)
    args = parser.parse_args()
    root = Path(args.target).resolve()
    try:
        if args.command == "fingerprint":
            print(fingerprint(root, json.loads(read(root, ".context/manifest.json"))))
            return 0
        if args.command == "resume":
            print(recovery_pack(root, args.task, args.max_bytes))
            return 0
        result = inspect(root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result["errors"] else 2 if args.ready and result["readiness"] else 0
    except (ValueError, OSError, KeyError) as exc:
        print(f"Context Capsule: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
