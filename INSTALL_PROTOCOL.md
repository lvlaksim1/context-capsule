# Installation and adoption protocol

## New repository

1. Select an explicit stable Core version.
2. Inspect the target for existing discovery/context files.
3. Install on the authoritative context branch.
4. Capture stable project identity/goals/architecture/constraints from repository evidence.
5. Capture compact current state/blockers/next.
6. Record rules, decisions, and handoff.
7. Validate/audit and reconcile against live repository/CI/runtime state.

## Existing legacy capsule

Use `adopt`; never reinstall over useful `.context/`.

Adoption preserves rich legacy paths, recognizes old authoritative maps, detects split context/discovery branches and `.agent/` runtime authority, and adds only missing standard structure.

## Concurrency

For mutating lifecycle operations, use `--expected-head` when a Git HEAD is known. A mismatch aborts rather than overwriting concurrent changes.

## Prohibited

- no reverse context sync into Core;
- no telemetry/central registry;
- no silent version upgrade;
- no flattening of richer legacy context;
- no copying routine runtime churn into durable `.context/`.
