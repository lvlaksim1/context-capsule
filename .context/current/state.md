# Current state

## Production / development topology

- stable production: Context Capsule v1.3.1 on `main`;
- v2 development and durable manager state: `v2-manager-runtime`;
- canonical installed Core provenance is read only from `.context/capsule.json.core_commit`;
- no consumer migration or stable-v2 promotion is authorized.

## Verified pre-Catalog Core baseline

The persistent-agent taxonomy plus task-scoped interactive-first execution and crash-safe live delegation return are independently verified.

Current Core evidence:
- canonical Core snapshot: `da89a35b2c6aeb460ed6f3e7665cdb886a3bde89`;
- binding: `45177bb3f7adb9ca965c9be067a4440d45a6085e`;
- hosted CI: `35941006206` SUCCESS.

Verified taxonomy:
- `Agent ≠ Runtime ≠ Skill ≠ Workflow`;
- Tool and Task/Engagement are separate adjacent concepts;
- Runtime/Skill/Workflow/Tool/Registry presence cannot create identity, commitment ownership, or authority;
- conversation history is not authoritative proof of reinstantiation or current durable state;
- installed contracts are self-sufficient; the full taxonomy spec remains a Core source artifact, not a required consumer file.

Verified execution semantics remain unchanged:
- bounded delegation preserves caller commitment/responsibility/authority;
- terminal bounded child state durably carries a pending caller continuation;
- live caller return is acknowledged before caller effects;
- runtime loss leaves the pending continuation autonomously recoverable without child re-execution;
- explicit handoff is a distinct authorized responsibility transfer;
- nested bounded delegation unwinds one caller at a time;
- direct Owner invocation remains first-class and Supervisor is not a mandatory hop.

Independent taxonomy audit:
- `AUD-2026-09-24-AGENT-TAXONOMY-001` opened TAX-001 Low / High confidence;
- focused retest `AUD-2026-09-24-TAX-001-RETEST-001` closed TAX-001 / High confidence;
- new findings: none.

A concrete continuity descriptor / Fast Resume subsystem is not part of this completed taxonomy stage.
