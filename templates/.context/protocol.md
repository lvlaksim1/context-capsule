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

Persist a durable update when one of these changes:
- accepted decision;
- requirement or durable rule;
- persistent user preference;
- architecture or interface contract;
- blocker/root cause;
- rejected/superseded approach;
- milestone/release;
- active plan/priority;
- important verified finding.

Do **not** copy every runtime event, heartbeat, queue transition, CI poll, or conversational turn into `.context/`.

If a project has a separate live-state authority such as `.agent/`, keep volatile execution state there. Promote only semantic consequences into Context Capsule.

## Working-set discipline

- `.context/project/` — stable identity, goals, architecture, constraints.
- `.context/current/state.md` — compact present semantic state.
- `.context/current/blockers.md` — only unresolved blockers/risks.
- `.context/current/next.md` — only currently actionable next work.
- `.context/handoffs/latest.md` — concise transfer to the next chat/agent.
- `.context/decisions/` — durable decisions and supersession chain.
- `.context/dialogues/` — compact evidence-rich investigation records.
- `.context/history/` — older useful context.

Resolved items must leave `current/`. Do not turn `current/state.md` or `handoffs/latest.md` into append-only journals.

## Evidence and contradictions

Evidence priority is defined by `ENTRYPOINT.md`. Repository/runtime facts are authoritative for implementation state; capsule records explain meaning, decisions, and continuity.

Never silently resolve a contradiction by rewriting history.

## Concurrency / CAS

Before writing context:
1. re-read the authoritative branch and current HEAD;
2. if the caller supplied an expected HEAD, abort on mismatch;
3. merge concurrent context changes rather than overwriting them;
4. use SHA/version-aware writes where available.

## End / handoff

Before a substantial work segment finishes:
- update current state, blockers, next;
- record new durable decisions/rules;
- update relevant dialogue evidence;
- refresh the manifest;
- update `handoffs/latest.md`.

## Privacy

Never persist secret values, credentials, cookies, private keys, or unnecessary sensitive personal data.
