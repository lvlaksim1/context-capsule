# Latest handoff — v1.3 integration checkpoint, NOT a release

## Objective

Deliver a robust Context Capsule whose permanent path is clean installation into a repository without a capsule, while retaining temporary migration/adoption only until `fgis-fsa-il`, `telegram-receiver` and `ai-agent-lab` have been migrated. The primary outcome is reliable continuation in a fresh chat without prior conversation.

## Branch and safety

- Released baseline: `main` / Core v1.2.0 / `2965c17`.
- Active development: `work/seamless-context-v1.3`.
- Draft PR: #1. Do not merge until final verification succeeds.
- Real target repositories have not been migrated by this work.

## Integrated implementation

- `installer/storage.py`: cooperating-writer OS lock in Git metadata, target snapshot, path-scoped mutation, validated rollback journal, same-directory atomic replacement, interruption recovery and concurrent-edit detection.
- `installer/legacy.py`: temporary legacy adapters preserve unknown top-level/nested semantics and nonstandard indexed references instead of flattening them.
- `installer/capsulectl.py`: full plan/preflight/apply lifecycle; branch/HEAD and dirty-context checks; install/adopt/repair/upgrade plus evidence-backed checkpoint command.
- `runtime/contracts.py`: repository confinement, symlink/special-file rejection, bundled-schema executor, managed-block parsing.
- `runtime/capsule_runtime.py`: offline structural/readiness inspection, semantic fingerprint, Git freshness classification and bounded task-specific recovery pack.
- schema v3 adds `managed_files`, `memory_index` and `resume`.
- Managed bootstrap blocks preserve existing AGENTS/AI_CONTEXT/custom legacy bootstrap text and force explicit review when origin is unknown.
- Installed repositories receive their own runtime and schemas under `.context/tools/`.
- `CAPSULE_TODO` marks unfilled clean-install semantic documents; structural validity and continuation readiness are intentionally different states.
- Migration registry now includes temporary v1.2 -> v1.3; earlier 1.0 -> 1.1 -> 1.2 hops remain available for the transition.

## Tests added/changed

- Existing lifecycle tests are being adapted to real Git worktrees and v1.3.
- New hardening tests cover wrong branch, malformed adoption without partial writes, nested/custom manifest preservation, dirty-context refusal, symlink escape, path traversal, concurrent edit and mid-apply rollback.
- New runtime tests cover draft-vs-ready behavior, ready checkpoint continuity across context-only commits, detection of later implementation commits, preservation/review of existing AGENTS instructions and strict schema rejection.

## Current verification status

Code and central structure are integrated, but final test results are not yet established. Do not claim the v1.2 defects fixed until the full suite and cross-platform CI pass.

## Next exact step

Run the complete test matrix, inspect failures, repair implementation/tests, then exercise migrations against disposable copies of the three real legacy projects. After success, update docs/specs, compute a real central semantic fingerprint, mark the central checkpoint ready and only then prepare merge/release.

## Constraints

Never overwrite target project memory, never export target context to Core, never silently replace unknown bootstrap instructions, and do not remove temporary migration mechanisms before the three real migrations are complete.
