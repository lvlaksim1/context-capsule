# Current state

## Production / development topology

- stable production: Context Capsule v1.3.1 on `main`;
- v2 development and durable manager state: `v2-manager-runtime`;
- canonical installed Core provenance is read only from `.context/capsule.json.core_commit`;
- no consumer migration or stable-v2 promotion is authorized.

## Verified Core baseline

Current bound Core snapshot:
`ec465bd31a02fdc2602fa4d4808ac8a99ccda480`

Binding:
`9ad957063e16298e3117dd4f99015fbda7f12e3c`

Core hosted CI:
`35947165325` SUCCESS.

Master Plan 8.8 is complete.

Verified responsibility/authority semantics:
- responsibility, authority, and execution ownership are separate;
- bounded delegation keeps caller responsibility and return semantics;
- explicit handoff does not transfer responsibility until target acceptance is durably proven;
- target acceptance must be independently re-read from target Agent authoritative home at an immutable commit and projected only under the exact current execution fence;
- Owner-derived delegable work carries a normalized immutable root grant;
- first-hop and nested delegation may only attenuate allowed effects/scope while preserving prohibitions, inherited constraints, and subdelegation policy;
- direct Owner invocation remains first-class;
- historical completed task artifacts remain readable.

Independent terminal evidence:
- `AUD-2026-09-24-DRA-EVIDENCE-RETEST-001`;
- DRA-001 CLOSED / High confidence;
- DRA-002 CLOSED / High confidence;
- new findings: none.

Agent Control Plane exact executable evidence:
- snapshot `5039c15fe7debd779132a06f17edf168bce2b2ea`;
- public verifier run `35948730227` SUCCESS.
