# Current state

## FACT — Stable v1.3 state

Context Capsule Core v1.3 is complete and stable on `main`.

Stable release line was independently verified before promotion and then verified again by GitHub-hosted CI after the repository became public.

Hosted CI result on stable `main`:

- runner assigned successfully;
- permanent tests: PASS;
- Python compile: PASS;
- self structural validation: VALID;
- self recovery readiness: READY;
- fresh-chat recovery smoke: PASS.

The earlier `runner_id=0`, `steps=[]` condition disappeared immediately after the repository visibility changed from private to public. This confirms the workflow/code itself was not the cause.

The temporary legacy migration layer remains retired, and all three known legacy repositories are already migrated to v1.3.

## FACT — Default semantic write-back

Core v1.3 now states explicitly that significant durable project changes are written back during normal work without waiting for an owner command to save/update context or for chat termination.

The same rule is also carried by the Core-managed `AGENTS.md` block, so `repair` propagates it to already-installed v1.3 capsules without overwriting project-owned instructions outside the managed block.

## FACT — Permanent authoritative context branch

Core now officially supports a permanent authoritative context branch with a discovery-only default branch for projects that use disposable feature branches. Feature branches no longer need to become Context Capsule authority.

The fresh-chat feature-branch failure mode is now closed: Core supports a permanent authoritative context branch and discovery-only default branch, and FGIS FSA IL has been migrated to that topology.

## FACT — Canonical v1.3.1 provenance

v1.3.1 resolves the v1.3.0 provenance ambiguity. One immutable release commit is the canonical Core source for all installed v1.3.1 capsules. Installed consumers must record that exact commit in `.context/capsule.json`; a version label alone is not sufficient provenance.

Canonical Core SHA: `2ef41a5ed57ae514cc5980065560d7e55d5e4b9a`. GitHub-hosted CI run 35710461141 completed successfully on this exact commit.
