# Current state

## Production / development topology

- stable production: Context Capsule v1.3.1 on `main`;
- v2 development and durable manager state: `v2-manager-runtime`;
- canonical Core provenance: `.context/capsule.json.core_commit = 8fc2da36f0a77d0f2a16508a8f7ee97fe1baa754`;
- no consumer migration or stable-v2 promotion is authorized.

## Task-scoped interactive-first amendment

The Core requires:

- live Owner-carried inter-agent work uses GitHub durable handoff plus immediate same-runtime reinstantiation;
- scheduler-visible interactive work MUST establish or verify a fresh task-scoped live-carrier ownership fence before execution;
- direct Owner work with no scheduler-visible projection does not require control-plane state;
- Owner presence never globally disables, parks, or delays scheduler infrastructure;
- unrelated autonomous tasks remain schedulable;
- successful live scheduler-visible work must terminalize its projection before carrier expiry.

## Verification and audit

- Core implementation: `8fc2da36f0a77d0f2a16508a8f7ee97fe1baa754`;
- binding: `b1e5ef97235400f8f3f98aae109a687b2643be30`;
- CI `35928337273`: SUCCESS;
- focused Auditor retest `AUD-2026-09-24-PER-TASK-CARRIER-001-RETEST-001`: PTC-003 CLOSED / High confidence.

No active Context Capsule finding remains from the task-carrier amendment.
