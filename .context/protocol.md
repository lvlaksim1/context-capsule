# Context Capsule protocol

## Principle

The repository is the durable memory for the project. Individual chats are ephemeral.

## Start of substantial work

- bootstrap through `ENTRYPOINT.md`;
- verify the authoritative context branch;
- restore project semantics before reading deep history;
- reconcile with live code/CI/runtime evidence;
- do not infer missing historical facts.

## Semantic sync triggers

Persist a durable update when one of these changes: accepted decision; requirement or durable rule; persistent user preference; architecture/interface contract; blocker/root cause; rejected/superseded approach; milestone/release; active plan/priority; important verified finding.

Do **not** copy every runtime event, heartbeat, queue transition, CI poll, or conversational turn into `.context/`.

If a project has a separate live-state authority such as `.agent/`, keep volatile execution state there. Promote only semantic consequences into Context Capsule.

## Working-set discipline

`project/` stores stable semantics. `current/state.md`, `current/blockers.md`, and `current/next.md` are compact working-set views. `handoffs/latest.md` is a concise transfer. Resolved material moves to decisions/dialogues/history.

## Concurrency / CAS

Before writing context, re-read the authoritative branch and current HEAD. When an expected HEAD is supplied, abort on mismatch and merge concurrent changes instead of overwriting them.

## End / handoff

Update current state, blockers, next, durable decisions/rules, relevant dialogue evidence, manifest, and latest handoff.

## Privacy

Never persist secret values, credentials, cookies, private keys, or unnecessary sensitive personal data.
