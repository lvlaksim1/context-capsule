# Current state

## Production / development topology

- stable production: Context Capsule v1.3.1 on `main`;
- v2 development and durable manager state: `v2-manager-runtime`;
- installed Core provenance is read only from canonical `.context/capsule.json.core_commit`; working views do not duplicate the mutable SHA;
- no existing consumer migration to v2 has been authorized.

## Project Manager responsibility

By explicit Owner direction, `context-capsule-project-manager` is now the primary operational manager/developer for ordinary ongoing Context Capsule work.

A replacement chat/model/runtime must reinstate this same manager rather than starting as an external ad-hoc developer.

## External ecosystem roles

- Supervisor: `ecosystem-supervisor`, repository `lvlaksim1/supervisor`; coordinates ecosystem-level concerns and does not own Context Capsule.
- Auditor: `project-manager-auditor`, repository `lvlaksim1/project-manager-auditor`; independently validated and READY; audits are read-only toward the target by default and findings are evidence, not automatic authority.

## Master plan status

Items 1–4 are complete.

Item 5 — transfer ordinary Context Capsule development to its own Project Manager — is now recorded in durable project state.

The next operational stage requires three independent runtimes: Supervisor, Context Capsule Project Manager, and Auditor. The first real Auditor engagement will then inspect this PM without transferring project ownership away from it.

## Independent audit remediation

Independent audit `AUD-2026-09-23-CCPM-001` findings CCPM-001 through CCPM-004 were independently
reproduced and remediated in the development line.

Verified remediation behavior:

- authority-bearing VALID binds Core-managed governing files to the exact declared Core Git commit;
- normal READY/recover require the manager-state authority checkout; explicit non-authoritative mode is inspection-only;
- mutable Core SHA is no longer duplicated in working views;
- beliefs and semantic/procedural memory require provenance per substantive durable entry before READY;
- remediation implementation commit `eb45a8de7879962fda3eb2df756e43a4ad1aa0b2` passed GitHub Actions run `35807681729` with 42 permanent tests, compile, self VALID, authoritative READY, recovery smoke, isolated-consumer compatibility/safety smoke, and Service Agent smoke.

A separate Auditor retest remains required before treating the independent audit engagement as closed.
