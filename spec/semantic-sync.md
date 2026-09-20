# Semantic sync

Context Capsule is durable project meaning, not an append-only event log.

## Promote into durable context

Persist semantic consequences of:

- accepted decisions;
- requirements;
- durable rules/preferences;
- architecture/interface changes;
- blocker/root-cause findings;
- accepted/rejected/superseded approaches;
- milestone/release meaning;
- active priority changes;
- important verified findings.

## Keep out of durable context

Do not routinely copy:

- heartbeats;
- leases;
- queue transitions;
- polling ticks;
- transient CI states;
- repetitive worker status commits;
- raw chat turns.

If such an event changes the durable meaning of the project, record that consequence once.

## Stable vs current

`project/` contains stable meaning. `current/` and `handoffs/latest.md` are compact working-set views. Resolved material moves into decisions/dialogues/history.

## Semantic index

`index.json` is a routing layer, not a duplicate knowledge base. It should summarize durable records sufficiently for selective recall without replacing the original record.

Index entries preserve a stable id and path. Missing/extra index coverage is a readiness signal because a fresh chat may otherwise fail to discover relevant history.

## Fingerprint and checkpoint

A ready continuation checkpoint fingerprints the semantic working set. A semantic edit invalidates readiness until the checkpoint is reconciled. Purely technical checkpoint/manifest timestamp churn is excluded by design.

## Runtime separation

When another store such as `.agent/` is declared authoritative for volatile execution state, routine runtime events stay there. Context Capsule records only durable conclusions, policies, blockers or architectural consequences.
