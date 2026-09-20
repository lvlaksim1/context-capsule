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

