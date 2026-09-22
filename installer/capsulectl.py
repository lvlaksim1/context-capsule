#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from installer.model import (
    CapsuleModelError,
    VERSION,
    build_recovery_pack,
    clean_install_changes,
    discovery_redirect_changes,
    readiness_snapshot,
    repair_changes,
    upgrade_changes,
    validate_snapshot,
)
from installer.safety import CapsuleSafetyError, confined_local_path, validate_core_commit
from installer.service_agent import (
    ServiceAgentModelError,
    build_service_recovery_pack,
    service_clean_install_changes,
    service_readiness_snapshot,
    service_repair_changes,
    validate_service_snapshot,
)

CORE_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = CORE_ROOT / "templates"
SERVICE_TEMPLATES = CORE_ROOT / "service-agent-templates"


def target_root(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.exists() or not path.is_dir():
        raise SystemExit(f"target does not exist or is not a directory: {path}")
    return path


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise SystemExit(f"Context Capsule expected UTF-8 text at {path}") from exc


def load_snapshot(target: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for rel in ("AI_CONTEXT.md", "AGENTS.md"):
        path = target / rel
        if path.exists():
            if path.is_symlink():
                confined_local_path(target, rel)
            if path.is_file():
                files[rel] = _read_text(path)

    context = target / ".context"
    if context.exists():
        if context.is_symlink():
            confined_local_path(target, ".context")
        if not context.is_dir():
            raise SystemExit(".context exists but is not a directory")
        for path in sorted(context.rglob("*")):
            if path.is_symlink():
                rel = path.relative_to(target).as_posix()
                confined_local_path(target, rel)
            if path.is_file():
                rel = path.relative_to(target).as_posix()
                files[rel] = _read_text(path)

    manifest_text = files.get(".context/manifest.json")
    if manifest_text:
        try:
            manifest = json.loads(manifest_text)
        except Exception:
            manifest = None
        if isinstance(manifest, dict):
            candidates: list[str] = []
            for key in ("entrypoint", "protocol", "latest_handoff", "current_state", "capsule_metadata"):
                value = manifest.get(key)
                if isinstance(value, str):
                    candidates.append(value)
            for section in ("project", "current", "manager"):
                value = manifest.get(section)
                if isinstance(value, dict):
                    candidates.extend(v for v in value.values() if isinstance(v, str))
            memory = manifest.get("memory")
            if isinstance(memory, dict):
                for key in ("index", "semantic", "procedural"):
                    value = memory.get(key)
                    if isinstance(value, str):
                        candidates.append(value)
                episodes = memory.get("episodes")
                if isinstance(episodes, list):
                    candidates.extend(v for v in episodes if isinstance(v, str))
            for section in ("rules", "decisions", "dialogues", "history"):
                value = manifest.get(section)
                if isinstance(value, list):
                    candidates.extend(v for v in value if isinstance(v, str))
            for rel in candidates:
                if rel in files:
                    continue
                try:
                    path = confined_local_path(target, rel)
                except CapsuleSafetyError as exc:
                    raise SystemExit(str(exc)) from exc
                if path.exists() and path.is_file():
                    files[rel] = _read_text(path)
    return files


def apply_local_changes(target: Path, changes: dict[str, str | None]) -> None:
    for rel, content in changes.items():
        path = confined_local_path(target, rel)
        if path.exists() and path.is_symlink():
            confined_local_path(target, rel)
        if content is None:
            if path.exists():
                path.unlink()
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".context-capsule.tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)


def infer_core_commit(explicit: str | None) -> str:
    if explicit:
        return validate_core_commit(explicit)
    try:
        sha = subprocess.run(
            ["git", "-C", str(CORE_ROOT), "rev-parse", "HEAD"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        return validate_core_commit(sha)
    except Exception as exc:
        raise SystemExit("--core-commit is required when Core is not running from a Git checkout") from exc


def actual_branch(target: Path) -> str | None:
    try:
        return subprocess.run(
            ["git", "-C", str(target), "branch", "--show-current"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip() or None
    except Exception:
        return None


def ensure_branch(target: Path, requested: str) -> None:
    actual = actual_branch(target)
    if actual and actual != requested:
        raise SystemExit(f"target checkout branch mismatch: requested {requested!r}, actual {actual!r}")


def _apply_planned(target: Path, label: str, planner) -> int:
    try:
        changes = planner()
    except (CapsuleModelError, CapsuleSafetyError) as exc:
        print(f"Context Capsule {label}: FAIL\n  - {exc}")
        return 2
    apply_local_changes(target, changes)
    print(f"Context Capsule {label} applied locally ({len(changes)} changed files).")
    return cmd_validate(argparse.Namespace(target=str(target)))


def cmd_install(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    ensure_branch(target, args.branch)
    files = load_snapshot(target)
    return _apply_planned(
        target,
        "install",
        lambda: clean_install_changes(
            files,
            TEMPLATES,
            args.repository,
            args.branch,
            infer_core_commit(args.core_commit),
            discovery_branch=args.discovery_branch,
            product_branch=args.product_branch,
        ),
    )


def cmd_upgrade(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    ensure_branch(target, args.branch)
    files = load_snapshot(target)
    return _apply_planned(
        target,
        "upgrade",
        lambda: upgrade_changes(
            files,
            TEMPLATES,
            repository=args.repository,
            branch=args.branch,
            core_commit=infer_core_commit(args.core_commit),
            product_branch=args.product_branch,
        ),
    )


def cmd_repair(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    ensure_branch(target, args.branch)
    files = load_snapshot(target)
    return _apply_planned(
        target,
        "repair",
        lambda: repair_changes(
            files,
            TEMPLATES,
            repository=args.repository,
            branch=args.branch,
            core_commit=infer_core_commit(args.core_commit),
        ),
    )


def cmd_discovery(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    ensure_branch(target, args.discovery_branch)
    files = load_snapshot(target)
    try:
        changes = discovery_redirect_changes(
            files,
            TEMPLATES,
            authoritative_branch=args.authoritative_branch,
            discovery_branch=args.discovery_branch,
        )
    except (CapsuleModelError, CapsuleSafetyError) as exc:
        print(f"Context Capsule discovery: FAIL\n  - {exc}")
        return 2
    apply_local_changes(target, changes)
    print(f"Context Capsule discovery redirect prepared: {args.discovery_branch} -> {args.authoritative_branch}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    try:
        files = load_snapshot(target)
        errors = validate_snapshot(files)
    except (CapsuleModelError, CapsuleSafetyError, SystemExit) as exc:
        print(f"Context Capsule validation: FAIL\n  - {exc}")
        return 1
    if errors:
        print("Context Capsule validation: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Context Capsule validation: VALID")
    return 0


def cmd_ready(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    try:
        files = load_snapshot(target)
        ready, reasons = readiness_snapshot(files)
    except (CapsuleModelError, CapsuleSafetyError, SystemExit) as exc:
        print(f"Context Capsule readiness: NOT READY\n  - {exc}")
        return 1
    if not ready:
        print("Context Capsule readiness: NOT READY")
        for reason in reasons:
            print(f"  - {reason}")
        return 1
    print("Context Capsule readiness: READY (PROJECT MANAGER REINSTANTIABLE)")
    return 0


def cmd_recover(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    try:
        pack = build_recovery_pack(load_snapshot(target), max_chars=args.max_chars)
    except (CapsuleModelError, CapsuleSafetyError, SystemExit) as exc:
        print(f"Context Capsule recovery: FAIL\n  - {exc}")
        return 1
    sys.stdout.write(pack)
    return 0


def _apply_service_planned(target: Path, label: str, planner) -> int:
    try:
        changes = planner()
    except (ServiceAgentModelError, CapsuleSafetyError) as exc:
        print(f"Context Capsule service-agent {label}: FAIL\n  - {exc}")
        return 2
    apply_local_changes(target, changes)
    print(f"Context Capsule service-agent {label} applied locally ({len(changes)} changed files).")
    return cmd_service_validate(argparse.Namespace(target=str(target)))


def cmd_service_install(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    ensure_branch(target, args.branch)
    files = load_snapshot(target)
    return _apply_service_planned(
        target,
        "install",
        lambda: service_clean_install_changes(
            files,
            SERVICE_TEMPLATES,
            repository=args.repository,
            branch=args.branch,
            core_commit=infer_core_commit(args.core_commit),
            agent_id=args.agent_id,
            role=args.role,
            specialization=args.specialization,
        ),
    )


def cmd_service_repair(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    ensure_branch(target, args.branch)
    files = load_snapshot(target)
    return _apply_service_planned(
        target,
        "repair",
        lambda: service_repair_changes(
            files,
            SERVICE_TEMPLATES,
            repository=args.repository,
            branch=args.branch,
            core_commit=infer_core_commit(args.core_commit),
        ),
    )


def cmd_service_validate(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    try:
        errors = validate_service_snapshot(load_snapshot(target))
    except (ServiceAgentModelError, CapsuleSafetyError, SystemExit) as exc:
        print(f"Context Capsule service-agent validation: FAIL\n  - {exc}")
        return 1
    if errors:
        print("Context Capsule service-agent validation: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Context Capsule service-agent validation: VALID")
    return 0


def cmd_service_ready(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    try:
        ready, reasons = service_readiness_snapshot(load_snapshot(target))
    except (ServiceAgentModelError, CapsuleSafetyError, SystemExit) as exc:
        print(f"Context Capsule service-agent readiness: NOT READY\n  - {exc}")
        return 1
    if not ready:
        print("Context Capsule service-agent readiness: NOT READY")
        for reason in reasons:
            print(f"  - {reason}")
        return 1
    print("Context Capsule service-agent readiness: READY (SERVICE AGENT REINSTANTIABLE)")
    return 0


def cmd_service_recover(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    try:
        pack = build_service_recovery_pack(load_snapshot(target), max_chars=args.max_chars)
    except (ServiceAgentModelError, CapsuleSafetyError, SystemExit) as exc:
        print(f"Context Capsule service-agent recovery: FAIL\n  - {exc}")
        return 1
    sys.stdout.write(pack)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="capsulectl", description="Context Capsule Project Manager lifecycle helper")
    sub = parser.add_subparsers(dest="command", required=True)

    install = sub.add_parser("install", help="clean-install a v2 Project Manager capsule")
    install.add_argument("--target", required=True)
    install.add_argument("--repository", required=True)
    install.add_argument("--branch", default="main")
    install.add_argument("--core-commit")
    install.add_argument("--discovery-branch")
    install.add_argument("--product-branch", help="product baseline branch; defaults to manager-state authority (or discovery branch in redirect mode)")
    install.set_defaults(func=cmd_install)

    upgrade = sub.add_parser("upgrade", help="explicitly upgrade an installed v1.3.x capsule to v2")
    upgrade.add_argument("--target", required=True)
    upgrade.add_argument("--repository", required=True)
    upgrade.add_argument("--branch", required=True)
    upgrade.add_argument("--core-commit")
    upgrade.add_argument("--product-branch", help="product baseline branch; inferred from existing topology when omitted")
    upgrade.set_defaults(func=cmd_upgrade)

    discovery = sub.add_parser("discovery", help="prepare a discovery-only branch redirect")
    discovery.add_argument("--target", required=True)
    discovery.add_argument("--authoritative-branch", required=True)
    discovery.add_argument("--discovery-branch", default="main")
    discovery.set_defaults(func=cmd_discovery)

    repair = sub.add_parser("repair", help="repair the installed v2 capsule without major-version upgrade")
    repair.add_argument("--target", required=True)
    repair.add_argument("--repository", required=True)
    repair.add_argument("--branch", required=True)
    repair.add_argument("--core-commit")
    repair.set_defaults(func=cmd_repair)

    validate = sub.add_parser("validate", help="check structural validity")
    validate.add_argument("--target", required=True)
    validate.set_defaults(func=cmd_validate)

    ready = sub.add_parser("ready", help="check Project Manager reinstantiation readiness")
    ready.add_argument("--target", required=True)
    ready.set_defaults(func=cmd_ready)

    recover = sub.add_parser("recover", help="emit a deterministic Project Manager reinstantiation pack")
    recover.add_argument("--target", required=True)
    recover.add_argument("--max-chars", type=int, default=50000)
    recover.set_defaults(func=cmd_recover)

    service_install = sub.add_parser("service-install", help="clean-install a persistent Service Agent profile")
    service_install.add_argument("--target", required=True)
    service_install.add_argument("--repository", required=True)
    service_install.add_argument("--branch", default="main")
    service_install.add_argument("--core-commit")
    service_install.add_argument("--agent-id", required=True)
    service_install.add_argument("--role", required=True)
    service_install.add_argument("--specialization", required=True)
    service_install.set_defaults(func=cmd_service_install)

    service_repair = sub.add_parser("service-repair", help="repair an installed Service Agent profile")
    service_repair.add_argument("--target", required=True)
    service_repair.add_argument("--repository", required=True)
    service_repair.add_argument("--branch", required=True)
    service_repair.add_argument("--core-commit")
    service_repair.set_defaults(func=cmd_service_repair)

    service_validate = sub.add_parser("service-validate", help="check Service Agent structural validity")
    service_validate.add_argument("--target", required=True)
    service_validate.set_defaults(func=cmd_service_validate)

    service_ready = sub.add_parser("service-ready", help="check Service Agent reinstantiation readiness")
    service_ready.add_argument("--target", required=True)
    service_ready.set_defaults(func=cmd_service_ready)

    service_recover = sub.add_parser("service-recover", help="emit a deterministic Service Agent reinstantiation pack")
    service_recover.add_argument("--target", required=True)
    service_recover.add_argument("--max-chars", type=int, default=50000)
    service_recover.set_defaults(func=cmd_service_recover)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
