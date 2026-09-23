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

Auditor closed CCPM-001 through CCPM-004 with High confidence. Those findings remain closed and were
not modified by the CCPM-R001 remediation.

The retest identified new Low-severity `CCPM-R001`: stale lifecycle-stage prose had remained in this
working view after the previous remediation Persist step. The Project Manager independently confirmed
the cause and implemented a focused correction.

Verified CCPM-R001 remediation:

- obsolete “first real audit is next” phase prose was removed;
- state/blockers/next/handoff were reconciled to one current lifecycle stage;
- working views remain explicitly non-authoritative;
- a deterministic regression now rejects a literal Git SHA used as an installed/current/canonical Core-provenance projection in working views while allowing historical SHA evidence;
- free-form lifecycle-stage prose is deliberately not checked by keyword heuristics because no universal structured lifecycle ontology currently exists;
- GitHub Actions run `35811115748` on the remediation implementation passed 43 permanent tests, compile, Core-bound VALID, authoritative READY, recovery smoke, isolated-consumer compatibility/safety smoke, and Service Agent smoke.

Current stage: Project Manager remediation and self-verification are complete. CCPM-R001 remains open
until a separate focused Auditor retest; this Project Manager does not self-close the finding.

## Optional orchestration interoperability

By explicit Owner direction, the proven generic Agent Control Plane safety model has been folded into v2 development without importing infrastructure-specific scheduler/gateway implementation.

The Project Manager and Service Agent Base now share these generic invariants: direct Owner/requester invocation remains first-class; external task transport cannot increase authority; the reinstantiated target validates issuer/authority provenance and mandate before acceptance; a supplied fence is revalidated before consequential writes and terminal completion; recovery checkpoints contain stable resume facts rather than hidden reasoning; successful completion is evidence-backed; terminal execution clears active ownership; agent-to-agent routing does not require Supervisor mediation by default.

GitHub Actions run `35863606445` on the provenance-bound implementation passed permanent tests, compile, self VALID, authoritative Project Manager READY, reinstantiation smoke, isolated-consumer compatibility smoke, and Service Agent CLI smoke.

Current stage: implementation/self-verification complete; independent Auditor verification of this self-referential Core change is the next gate. Stable `main`, v1.3.1 consumers, stable-v2 promotion, and migration remain unchanged.
