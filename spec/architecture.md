# Architecture

Context Capsule provides durable repository-local context for human/AI project work.

## Invariants

1. Complete project context stays in the target repository.
2. Core never stores, mirrors, indexes, or receives target-project context.
3. Installed capsules operate autonomously when Core is unavailable.
4. Installed versions are pinned in `.context/capsule.json`.
5. Upgrades are explicit and migration-driven.
6. Project-owned context is preserved during adopt/repair/upgrade.
7. `.context/manifest.json` is the navigation index for actual context paths.
8. Recovery is incomplete until stored context is reconciled with live repository/CI/runtime evidence.
9. Volatile runtime state is not copied into durable context unless it creates a semantic consequence.
10. Context writes use branch/HEAD-aware concurrency discipline where available.

## Stable project semantics

Standard v1.2 introduces:
- `.context/project/identity.md`
- `.context/project/goals.md`
- `.context/project/architecture.md`
- `.context/project/constraints.md`

These contain durable project meaning, not temporary tasks.

## Compact current working set

Current work is split into:
- `current/state.md`
- `current/blockers.md`
- `current/next.md`

Resolved and superseded material moves out of `current/` into decisions, dialogues, or history.

## Branch model

`authoritative_branch` identifies the branch containing the real capsule. `discovery_branch` identifies the branch a fresh agent is expected to encounter first. If they differ, `branch_mode` is `redirect`.

This models projects such as a default `main` branch containing only discovery shims while the full capsule lives on another authoritative context branch.

## Runtime authority

Projects may declare volatile live-state authorities such as `.agent/` in `manifest.runtime.authoritative_paths`.

The capsule stores project semantics; the runtime store remains authoritative for fast-changing execution state. Only durable semantic consequences are promoted into `.context/`.
