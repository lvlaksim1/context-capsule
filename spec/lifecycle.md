# Lifecycle

## Install — permanent path

`install` requires a repository with no existing `.context/`. Existing `AGENTS.md` or `AI_CONTEXT.md` are not grounds for destructive refusal: their project text is preserved and a Core-managed block is added.

Install creates a complete v1.3 structural capsule, repository-local tools/schemas, semantic index and a **draft** continuation checkpoint. Project semantic templates remain explicitly `CAPSULE_TODO` until captured and reconciled.

## Checkpoint

`checkpoint` updates `.context/resume.json`.

A `--ready` checkpoint requires:

- project/current/rule/handoff documents to contain substantive project-specific content;
- no unresolved preserved-bootstrap review;
- evidence;
- no uncommitted non-capsule implementation files;
- a semantic fingerprint over the current working set.

After a ready checkpoint is committed, context-only descendant commits do not make it stale. A descendant that changes implementation outside Context Capsule requires reconciliation.

## Validate

`validate` is structural. It executes the bundled schema vocabulary, verifies canonical references, branch consistency, safe repository paths, managed-file integrity, semantic index structure and current Core version.

Validation deliberately does not claim semantic readiness.

## Audit

`audit` adds repository-local runtime inspection, semantic readiness, checkpoint/fingerprint freshness, indexed-memory coverage, compactness and Git freshness signals.

`audit --ready` returns nonzero when structural validation succeeds but continuation readiness is incomplete.

## Repair

`repair` applies only to a current-version installed capsule. It restores/refreshes managed structure and navigation without replacing project-owned semantic files.

It preserves unknown manifest extensions and nonstandard indexed paths. Repair does not convert a draft checkpoint to ready.

## Adopt — temporary

`adopt` exists for pre-Core legacy `.context/` installations. It preserves useful structure, custom fields and custom bootstrap text, then enriches the repository with v1.3 contracts.

This command is scheduled for removal only after the three known old repositories have been migrated and verified.

## Upgrade — temporary legacy chain

The transition chain currently supports:

`1.0.0 -> 1.1.0 -> 1.2.0 -> 1.3.0`.

The chain is explicit; no unknown version is silently upgraded. Historical project memory is preserved. Recognized historical Core bootstrap may be replaced; unknown bootstrap is preserved and flagged for review.

## Mutation transaction

Mutating commands build the complete target snapshot before any write. Preflight includes schema/reference/path/branch checks.

Apply then:

1. holds a repository-local cooperating-writer OS lock in Git metadata;
2. verifies snapshot, HEAD and branch have not changed;
3. records preimages/digests in a transaction journal;
4. replaces each affected file atomically in its own directory;
5. detects a changed operand before overwriting it;
6. marks the journal committed, then removes it;
7. rolls back preimages on a handled mid-operation failure;
8. recovers a leftover prepared journal on the next lifecycle mutation when no conflicting external edit is present.

This is transactional recovery for cooperating lifecycle operations, not global filesystem isolation from arbitrary processes.

## Dirty state and CAS

By default, uncommitted capsule/discovery files block lifecycle mutation. `--allow-dirty-context` is an explicit override; it does not disable snapshot/concurrent-edit detection.

`--expected-head` adds a caller-supplied Git commit precondition. It is one part of concurrency protection, not the whole transaction guarantee.
