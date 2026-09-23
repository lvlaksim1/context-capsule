# Current state

## Production / development topology

- stable production: Context Capsule v1.3.1 on `main`;
- v2 development and durable manager state: `v2-manager-runtime`;
- canonical current Core provenance remains `7aa1e697504e686b02a4d7f1539a157214d5e692`;
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
