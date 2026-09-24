# Current state

## Production / development topology

- stable production: Context Capsule v1.3.1 on `main`;
- v2 development and durable manager state: `v2-manager-runtime`;
- canonical installed Core provenance is read only from `.context/capsule.json.core_commit`;
- no consumer migration or stable-v2 promotion is authorized.

## Verified pre-scaling Core baseline

Task-scoped interactive-first execution and crash-safe live delegation return are independently verified.

Current Core evidence:
- canonical Core snapshot: `3a0573751dc309148b5d2fd48b8df48f05eaa779`;
- binding: `e88cbb52e1ea1dd239442dfa31daf3376206021c`;
- hosted CI: `35937735593` SUCCESS.

Verified semantics:
- bounded delegation preserves caller commitment/responsibility/authority;
- terminal bounded child state durably carries a pending caller continuation;
- live caller return is acknowledged before caller effects;
- runtime loss leaves the pending continuation autonomously recoverable without child re-execution;
- consumed continuation is not redelivered;
- explicit handoff is a distinct responsibility transfer with no implicit return;
- nested bounded delegation unwinds one caller at a time;
- direct Owner invocation remains first-class and Supervisor is not a mandatory hop.

Independent retest `AUD-2026-09-24-LRC-001-RETEST-001` closed LRC-001 / High confidence with no new findings.
