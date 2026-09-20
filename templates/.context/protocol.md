<!-- context-capsule:begin -->
# Context Capsule protocol

## Principle

The repository is the durable memory for the project; chats are ephemeral. Context Capsule itself is operated only through GitHub.

## Semantic sync

Persist durable changes to decisions, requirements, rules/preferences, architecture/interface contracts, blocker/root-cause findings, accepted/rejected approaches, milestone/release meaning, active priorities and important verified findings.

Do not routinely persist heartbeats, leases, queue transitions, polling ticks, transient CI states, repetitive worker commits or raw chat turns. Record only durable consequences.

## Working set

- `project/`: stable identity, goals, architecture and constraints.
- `current/`: present state, unresolved blockers and actionable next work.
- `handoffs/latest.md`: concise transfer.
- `decisions/`, `dialogues/`, `history/`: durable evidence/history.
- `index.json`: navigation metadata for history, never an access barrier.
- `resume.json`: evidence-backed continuation checkpoint.

Resolved material leaves `current/`.

## GitHub-only operation

Target repositories contain context data and discovery instructions only. Installation, validation, migration, repair, indexing and readiness checks are executed by the central Context Capsule service inside GitHub. No local executable runtime, Python setup or desktop compatibility layer is part of the product.

Mutations must be based on a verified repository branch and HEAD. The GitHub service must refuse stale writes and publish a coherent repository change through normal Git/GitHub concurrency controls.

## End of substantial work

Update stable/current semantics as needed, durable decisions/rules, handoff, memory index and the continuation checkpoint.

## Privacy

Never persist credentials, cookies, private keys, secret values or unnecessary sensitive personal data.
<!-- context-capsule:end -->
