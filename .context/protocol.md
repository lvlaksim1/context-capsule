# Context Capsule protocol

## Purpose

Context Capsule v2 stores the durable state required to reinstate the same Project Manager across independent chats, models, or agent runtimes.

The runtime is replaceable. The manager identity, mandate, durable beliefs, goals, intentions, plans, and typed memory are repository-local and persistent.

## Durable layers

- `project/` — objective project identity, goals, architecture, and constraints.
- `manager/` — stable manager identity, mandate, beliefs, goals, intentions, plans, and the Core-managed Manager Protocol.
- `memory/` — typed semantic, episodic, and procedural memory.
- `rules/` and `decisions/` — binding rules and durable accepted/rejected choices.
- `current/` — compact verified project state, blockers, and next work.
- `handoffs/latest.md` — emergency/convenience summary only; it is not the identity or primary continuity mechanism.
- `dialogues/` and `history/` — deeper evidence and historical context.

## Runtime boundary

Conversation history, pending tool calls, chain-of-thought, transient execution state, leases, heartbeats, and runtime checkpoints are not Project Manager identity. A runtime may persist its own checkpoint separately, but Context Capsule does not require or impersonate that checkpoint.

## Belief provenance

Durable manager beliefs must retain provenance. Distinguish owner directives, verified repository/CI/runtime evidence, trusted external evidence, and manager inference. Never silently promote untrusted content or a specialist agent's output into authoritative belief.

When a belief changes, record the newer evidence and explicitly supersede or reject the old belief instead of silently rewriting history.

## VALID vs READY

`VALID` means the v2 capsule is structurally coherent, repository-confined, internally resolvable, and includes the manager model.

`READY` additionally means the Project Manager can be reinstantiated: mandate, beliefs with provenance, manager goals, intentions, plans, core project semantics, current state, and next work are substantive.

## Semantic self-maintenance

Persist durable decisions, requirements, rules, architecture changes, root causes, rejected approaches, milestones, beliefs, commitments, lessons, learned procedures, and priority changes.

Periodically consolidate memory after major milestones or when the working set becomes noisy. Consolidation must preserve provenance and important superseded history.

Do not copy routine runtime churn into `.context/`.

## Repository mutation

Canonical GitHub lifecycle changes are planned and validated as a complete snapshot and published from an expected parent with a non-forced ref update.

## Privacy

Never persist credentials, secret values, cookies, private keys, hidden chain-of-thought, or unnecessary sensitive personal information.
