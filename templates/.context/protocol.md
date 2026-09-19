<!-- context-capsule:begin -->
# Context Capsule protocol

## Principle

The repository is the durable memory for the project; individual chats are ephemeral. Recovery is complete only after stored semantics are reconciled with live evidence.

## Semantic sync

Persist a durable update when an accepted decision, requirement, durable rule/preference, architecture/interface contract, blocker/root cause, rejected or superseded approach, milestone/release meaning, active priority, or important verified finding changes.

Do not routinely persist heartbeats, leases, queue transitions, polling ticks, transient CI states, repetitive worker commits or raw chat turns. When such events change project meaning, record the consequence once.

## Working-set discipline

- `project/`: stable identity, goals, architecture and constraints.
- `current/`: only present state, unresolved blockers and actionable next work.
- `handoffs/latest.md`: concise transfer, not an append-only journal.
- `decisions/`, `dialogues/`, `history/`: durable evidence and supersession history.
- `index.json`: compact routing metadata for selective recall.
- `resume.json`: evidence-backed continuation checkpoint.

Resolved material leaves `current/`. A ready checkpoint must not be used to bless unreconciled semantic edits.

## Mutation discipline

Lifecycle mutations use repository-path confinement, branch/HEAD checks, a cooperating-writer lock, snapshot comparison, journaled atomic file replacement and rollback. Uncommitted capsule/discovery edits are refused unless explicitly allowed; allowing them does not disable concurrent-edit detection.

## End of substantial work

Update stable/current semantics as needed, durable decisions/rules, handoff, memory index and the continuation checkpoint. The checkpoint should state the verified position, next concrete action and evidence.

## Privacy

Never persist credentials, cookies, private keys, secret values or unnecessary sensitive personal data.
<!-- context-capsule:end -->
