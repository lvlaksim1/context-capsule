# Lifecycle

## Clean install

A clean install refuses an existing `.context/`. Existing root bootstrap files are preserved outside the Context Capsule managed block.

The installer records the exact Core commit SHA and prepares a complete snapshot before publication.

## Validate

`validate` answers only whether the capsule is structurally coherent, repository-confined, and internally resolvable.

## Ready

`ready` is stricter. It requires substantive identity, goals, architecture, constraints, current state, next action, handoff, and at least one active rule or durable decision.

## Recover

`recover` emits a deterministic bounded fresh-chat recovery pack from a READY capsule. Deep dialogue/history is not loaded by default.

## Repair

Repair preserves unknown manifest extensions and nonstandard indexed paths. It updates only Core-owned structure and managed bootstrap blocks.

## Legacy adopt

Legacy adoption is a temporary, repository-name-gated bridge for three known projects. It is not a permanent arbitrary migration framework.
