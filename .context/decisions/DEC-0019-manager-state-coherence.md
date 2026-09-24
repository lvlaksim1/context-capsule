# DEC-0019 — Coherent manager-state generations

Date: 2026-09-24
Status: ACCEPTED
Authority: Owner-authorized remediation of Auditor finding IOSPM-001

## Decision

Context Capsule v2 protects semantically coupled Project Manager persistence with a sealed generation marker at `.context/manager/state-integrity.json`.

The marker binds the Git blob identities of manager beliefs, goals, intentions, plans, current state, blockers, next actions, and latest handoff.

For protected capsules:
- `READY` and `recover` fail closed if any coupled file differs from the sealed generation;
- interrupted multi-commit publication therefore cannot be consumed as a coherent reinstantiation snapshot;
- preferred publication is one atomic Git commit containing all coupled semantic changes and the new marker;
- when transport forces intermediate commits, the previous marker remains in place until the final coherent state is ready to seal;
- `repair` may bootstrap the first generation for legacy-unsealed v2 capsules;
- `repair` must not auto-seal an already-protected mismatching snapshot.

This marker is a coherence mechanism, not an authority signature. Existing provenance, mandate, Owner authority, delegation, and execution-fence rules remain unchanged.

## Finding status

IOSPM-001 is remediated in development but remains OPEN until independent Auditor retest.
