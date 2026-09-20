# Architecture

Context Capsule provides durable repository-local context for human/AI project work. Core defines contracts and tooling; every target repository owns its memory and remains usable without Core.

## Invariants

1. Complete target-project context stays in the target repository.
2. Core never stores, mirrors, indexes, receives or telemeters target-project context.
3. Installed capsules operate autonomously during normal project work.
4. Installed versions and managed-file integrity are pinned in `.context/capsule.json`.
5. Clean installation is the permanent installation path.
6. Legacy adoption/version migration is a temporary transition facility until the three known old installations are migrated.
7. Project-owned semantic content is never overwritten merely to conform to a generic template.
8. `.context/manifest.json` is the navigation contract for actual semantic paths and branch/runtime topology.
9. Structural validity and continuation readiness are separate concepts.
10. Recovery is incomplete until stored semantics are reconciled with live repository/CI/release/runtime evidence.
11. Volatile runtime state remains in its runtime authority; only durable semantic consequences are promoted.
12. Mutating lifecycle operations are planned before writing and use path confinement, concurrency checks, journaled atomic file replacement and rollback.
13. Unknown bootstrap/project instructions are preserved and require explicit review rather than silent replacement.

## Stable project semantics

`.context/project/` contains durable meaning:

- `identity.md`;
- `goals.md`;
- `architecture.md`;
- `constraints.md`.

A clean installation marks these templates `CAPSULE_TODO`; presence alone is not readiness.

## Compact current working set

`.context/current/` contains:

- `state.md`;
- `blockers.md`;
- `next.md`.

Resolved/superseded material moves to decisions/dialogues/history rather than accumulating here.

## Semantic history and selective recall

Durable historical evidence may live in project-specific files referenced by the manifest. `.context/index.json` adds compact routing metadata: stable id, type, status, title, summary, tags and path.

The index is not the source of truth for the record; the referenced record remains authoritative. A recovery pack loads mandatory working context and only a small task-relevant subset of indexed history.

## Continuation checkpoint

`.context/resume.json` records:

- `draft` or `ready`;
- concise verified position and next action;
- authoritative branch and verified Git commit;
- semantic working-set fingerprint;
- bootstrap-review obligations;
- evidence references.

The fingerprint deliberately excludes the checkpoint itself and purely technical manifest refresh fields, so committing a context-only checkpoint does not invalidate itself. A later implementation change makes the checkpoint stale until reconciled.

## Core-managed vs project-owned content

Core-managed discovery/runtime material is integrity-registered:

- managed blocks inside `AGENTS.md`, `AI_CONTEXT.md`, `.context/ENTRYPOINT.md`, `.context/protocol.md`;
- repository-local runtime and bundled schemas under `.context/tools/`.

Core owns only the marked managed block inside bootstrap Markdown. Text outside the block remains project-owned.

Project semantics under `project/`, `current/`, rules, decisions, dialogues, history and handoff remain project-owned.

## Branch model

`authoritative_branch` contains the real capsule. `discovery_branch` is where a fresh agent is expected to arrive. If they differ, `branch_mode=redirect`.

Lifecycle mutation never interprets `--branch` as a checkout command. It must run from the authoritative branch and fails on mismatch.

## Runtime authority

Projects may declare separate live-state authorities such as `.agent/`. They remain authoritative for fast-changing execution state. Context Capsule persists only semantic consequences that matter across sessions.
