# DEC-0017 — Working-view consistency automation boundary

- Status: accepted for development
- Date: 2026-09-23
- Trigger: focused retest finding `CCPM-R001` from `AUD-2026-09-23-CCPM-001-RETEST-001`.

## Decision

1. `current/state.md`, `current/blockers.md`, `current/next.md`, and `handoffs/latest.md` remain non-authoritative derived working views. They must be reconciled from manager BDI state plus verified live evidence; they do not become a new authority layer.
2. The mechanically enforceable CCPM-003 rule receives permanent regression coverage: a working-view line that declares **installed/current/canonical Core provenance** must not contain a literal 40-character Git SHA. Mutable installed Core provenance is referenced through `.context/capsule.json.core_commit`.
3. Historical commit SHAs remain allowed as audit/remediation evidence when they are not presented as the mutable installed-Core provenance coordinate.
4. Free-form lifecycle-stage prose is not generically validated by keyword/regex heuristics. Context Capsule currently has no universal machine-readable lifecycle ontology across arbitrary projects. Introducing a textual detector would be brittle and could both miss semantic drift and reject valid project language.
5. Until an explicit lifecycle-state schema is designed, lifecycle-stage consistency remains a Reconcile/Persist responsibility: when a verified phase transition occurs, all affected working views must be reviewed and updated together.

## Consequences

- Reintroduction of the specific mutable-Core provenance projection class is caught deterministically by the permanent test suite.
- CCPM-R001's stale phase statement is corrected semantically in all affected working views.
- No new authority is assigned to working views.
- A future generalized lifecycle checker requires an explicit structured lifecycle model rather than prose matching.
