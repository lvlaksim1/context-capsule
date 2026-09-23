# Current state

## Production / development topology

- stable production: Context Capsule v1.3.1 on `main`;
- v2 development and durable manager state: `v2-manager-runtime`;
- installed Core provenance is read only from canonical `.context/capsule.json.core_commit`; working views do not duplicate the mutable SHA;
- no existing consumer migration to v2 has been authorized.

## Project Manager responsibility

By explicit Owner direction, `context-capsule-project-manager` is the primary operational manager/developer for ordinary ongoing Context Capsule work.

A replacement chat/model/runtime must reinstate this same manager rather than starting as an external ad-hoc developer.

## External ecosystem roles

- Supervisor: `ecosystem-supervisor`, repository `lvlaksim1/supervisor`; coordinates ecosystem-level concerns and does not own Context Capsule.
- Auditor: `project-manager-auditor`, repository `lvlaksim1/project-manager-auditor`; independently audits within separate read-only engagements by default, and findings remain evidence rather than project authority.

## Audit / remediation stage

The first real independent audit `AUD-2026-09-23-CCPM-001` and remediation retest
`AUD-2026-09-23-CCPM-001-RETEST-001` have completed.

Auditor closed CCPM-001 through CCPM-004 with High confidence. Those findings are not reopened by the
current work.

The retest identified one new Low-severity finding, `CCPM-R001`: stale lifecycle-stage prose remained
in this working view after the previous remediation write-back.

CCPM-R001 has been independently confirmed by the Project Manager. Its remediation in the current
development snapshot:

- removes the obsolete statement that the first real Auditor engagement is still in the future;
- reconciles state/blockers/next/handoff to one current phase;
- adds deterministic regression coverage that forbids a literal Git SHA from being used as an installed/current/canonical Core-provenance projection in working views;
- keeps working views explicitly non-authoritative;
- records that free-form lifecycle-stage consistency is not generically machine-checkable without an explicit structured lifecycle model.

Hosted verification of this remediation is the current immediate step. After successful verification,
the only audit action required is a focused Auditor retest of CCPM-R001.
