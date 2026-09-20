# Lifecycle

## Clean install

A clean install refuses an existing `.context/`. Existing root bootstrap files are preserved outside the Context Capsule managed block.

The installer records the exact Core commit SHA and prepares a complete snapshot before publication.

## Validate

`validate` answers only whether the capsule is structurally coherent, repository-confined, and internally resolvable.

## Ready

`ready` is stricter. It requires substantive identity, goals, architecture, constraints, current state, next action, handoff, and at least one active rule or durable decision.

## Recover

`recover` emits a deterministic bounded fresh-chat recovery pack from a READY capsule. Active state/handoff is prioritized ahead of deeper decision history.

## Repair

Repair preserves unknown manifest extensions and nonstandard indexed paths. It updates Core-managed structure without flattening project-owned semantic context.

## Legacy layouts

Legacy adoption is not a permanent lifecycle operation. The known v1-era repositories were migrated during v1.3 hardening; the temporary `adopt` command and repository-specific adapter code were then retired.

## Permanent redirect topology

For feature-branch projects, Context Capsule supports a permanent authoritative branch plus a discovery-only default branch. The discovery branch contains only redirect bootstrap, while the full READY capsule remains on the permanent authoritative branch. Feature branches are never promoted to context authority.
