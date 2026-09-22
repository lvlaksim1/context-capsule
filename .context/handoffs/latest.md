# Latest handoff

## Stable v1.3 — complete

Context Capsule Core v1.3 is released on `main` and fully verified.

Verification now exists in two independent forms:

1. exact-commit independent reconstruction and execution;
2. successful GitHub-hosted CI on stable `main` after the repository became public.

Hosted CI passed:

- permanent tests;
- compile;
- self VALID;
- self READY;
- fresh-chat recovery smoke.

The previous `runner_id=0`, `steps=[]` problem was infrastructure availability for the private repository, not a Context Capsule code failure. It is now resolved.

The permanent product surface remains clean install, non-destructive repair, VALID, READY, bounded recover, managed bootstrap blocks, repository path/symlink confinement, manifest-extension preservation, installed redirect-topology preservation, exact Core provenance, and expected-parent atomic GitHub publication.

All three known legacy projects were migrated before the temporary adapter was removed.

## Status

No known product, migration, or CI blocker remains.

## Default semantic write-back

The universal v1.3 templates now explicitly require semantic write-back during normal work. Agents must not wait for an owner request to save/update context or for chat termination. This behavior is regression-tested.

The managed `AGENTS.md` block is the repair propagation surface for this rule in existing v1.3 installations; project-owned text outside the managed block remains untouched.

## Permanent authoritative context branch

Core now supports a permanent context-authority branch plus discovery-only default branch. This closes the stale-authority failure mode exposed when a feature branch is merged or closed after carrying the capsule.

FGIS FSA IL is the first migrated permanent-context consumer: `main` is discovery-only and `context` is the durable authority. Fresh feature branches no longer carry Context Capsule authority.

## Canonical v1.3.1 patch

v1.3.1 is the provenance-hardening patch. It gives the stable v1.3 product line one canonical immutable Core source and requires installed consumers to record that exact Core SHA. The three known consumers are to be refreshed to this same canonical commit without changing project-owned semantic context.
