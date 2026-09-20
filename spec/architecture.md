# Architecture

## Service boundary

Context Capsule is a GitHub-only service.

The central Core repository contains executable implementation, schemas and tests. A target repository contains its own durable context plus discovery/bootstrap text, but no executable Context Capsule runtime.

## Invariants

1. Complete target-project context remains in the target repository.
2. Core never stores, mirrors or telemeters target-project context.
3. Nothing must be installed or executed on the user's computer.
4. Target repositories do not receive copied Python modules or schema bundles.
5. Clean installation is the permanent product path.
6. Legacy adoption/version migration is temporary until the three known old installations are migrated.
7. Project-owned semantic content and unknown bootstrap text are preserved.
8. `.context/manifest.json` maps actual semantic paths and branch/runtime topology.
9. Structural validity and continuation readiness are distinct.
10. Recovery must reconcile stored semantics with current GitHub repository/CI/release/runtime evidence.
11. Volatile project runtime such as `.agent/` remains separate; only durable semantic consequences enter the capsule.
12. GitHub branch/HEAD/CAS and coherent commit publication form the mutation/concurrency boundary.

## Target repository content

The installed capsule is data-oriented:

- stable project semantics in `project/`;
- compact current working set in `current/`;
- durable decisions/dialogues/history;
- semantic navigation in `index.json`;
- continuation checkpoint in `resume.json`;
- managed discovery/bootstrap text.

No `.context/tools/` runtime is installed.

## Semantic index

`index.json` is navigation metadata, not the source of truth and not an access barrier. Original referenced records remain authoritative.

## Continuation checkpoint

`resume.json` records draft/ready status, verified branch/commit, semantic fingerprint, evidence, next action and any unresolved bootstrap review.

## Managed bootstrap

Core owns only its explicitly marked managed block in shared discovery Markdown. Text outside the block remains project-owned.

## Branch topology

`authoritative_branch` identifies the real capsule. `discovery_branch` identifies the branch a fresh agent encounters first. When different, `branch_mode=redirect`.

## Project runtime authority

Projects may separately declare volatile runtime paths such as `.agent/`. These are project runtime authorities, not Context Capsule executables.
