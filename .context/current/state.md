# Current state

## Production / development topology

- stable production: Context Capsule v1.3.1 on `main`;
- v2 development and durable manager state: `v2-manager-runtime`;
- installed Core provenance is read only from canonical `.context/capsule.json.core_commit`; working views do not duplicate the mutable SHA;
- no existing consumer migration to v2 has been authorized.

## Project Manager responsibility

By explicit Owner direction, `context-capsule-project-manager` is the primary operational manager/developer for ordinary ongoing Context Capsule work.

## Audit continuity

- CCPM-001 through CCPM-004: CLOSED / High confidence.
- Historical CCPM-R001: CLOSED / High confidence by focused Auditor retest `AUD-2026-09-23-CCPM-R001-RETEST-001`; no further focused CCPM-R001 retest is required.
- The later item-19 interoperability audit `ACP-TASK-CC-ACP-AUDIT-001` independently verified the scoped interoperability invariants and opened a separate finding `ACP-CC-001` Low / High confidence for recurrence of stale external-gate prose in working views.

## ACP-CC-001 remediation

The Project Manager is implementing a systemic fix rather than another one-off prose edit:

- before a pending external audit/retest/approval gate is carried into a new substantial Persist, Reconcile must re-check the authoritative durable result for that exact gate;
- a terminal external result must be reflected across all affected working views in the same Persist operation;
- any new follow-on gate is represented separately;
- the rule is a provenance/reconciliation invariant, not a universal keyword-based lifecycle ontology.

Current gate: complete implementation + full CI, then a separate focused Auditor retest of `ACP-CC-001`.

Stable `main`, v1.3.1 consumers, stable-v2 promotion, and migration remain unchanged.
