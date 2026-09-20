# Architecture

Context Capsule stores the durable meaning of a project in the project repository itself.

## Permanent layers

- `project/`: identity, goals, architecture, constraints.
- `rules/` and `decisions/`: binding durable choices.
- `current/`: compact state, blockers, next work.
- `handoffs/latest.md`: transfer to the next chat/agent.
- `dialogues/` and `history/`: evidence and deeper history.

`capsule.json` identifies the installed Core version and exact immutable `core_commit`.
`manifest.json` maps project-owned context without discarding unknown safe extensions.

## Mutation boundary

The canonical target is a GitHub branch. Lifecycle changes are planned and validated as a complete snapshot and become visible through one non-forced branch ref update to a commit based on the expected parent.

## Branch model

New clean installations use a single primary branch for discovery and authority.

An already installed capsule may legitimately use `branch_mode: redirect` when discovery and authoritative context live on different branches. Repair must preserve that existing topology and must run against the authoritative branch; it must not silently collapse redirect into single-branch mode.
