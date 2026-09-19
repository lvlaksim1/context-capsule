# Semantic sync

Context Capsule is not an append-only event log.

## Promote into `.context/`

Promote:
- decisions;
- requirements;
- durable rules/preferences;
- architecture changes;
- blocker/root-cause findings;
- accepted/rejected approaches;
- milestone/release meaning;
- active priority changes;
- important verified findings.

## Keep out of `.context/`

Do not routinely copy:
- heartbeats;
- leases;
- queue transitions;
- polling ticks;
- transient CI states;
- repetitive worker status commits;
- raw chat turns.

If those events change the durable meaning of the project, record the consequence once as a semantic update.

## Compactness

`current/` and `handoffs/latest.md` are working-set views, not history stores. Resolved material moves to decisions/dialogues/history.
