# Current state

## Production / development topology

- stable production: Context Capsule v1.3.1 on `main`;
- v2 development and durable manager state: `v2-manager-runtime`;
- canonical Core provenance: `.context/capsule.json.core_commit = 8fc2da36f0a77d0f2a16508a8f7ee97fe1baa754`;
- no consumer migration or stable-v2 promotion is authorized.

## Task-scoped interactive-first amendment

The Core now requires:

- live Owner-carried inter-agent work uses GitHub durable handoff plus immediate same-runtime reinstantiation;
- if that task/chain is scheduler-visible, a fresh task-scoped live-carrier ownership fence MUST be established or verified before interactive execution;
- direct Owner work with no scheduler-visible projection does not require control-plane state;
- Owner presence never globally disables, parks, or delays scheduler infrastructure;
- unrelated autonomous tasks remain schedulable;
- successful live scheduler-visible work must terminalize its projection before carrier expiry;
- only the affected nonterminal task may fall back after expiry when allowed.

## Verification

- Core implementation snapshot: `8fc2da36f0a77d0f2a16508a8f7ee97fe1baa754`;
- binding commit: `b1e5ef97235400f8f3f98aae109a687b2643be30`;
- CI: run `35928337273` SUCCESS on `7d3c21770e439e7957185fda263d1636ec77e653`;
- all CI stages passed.

PTC-003 implementation remediation is complete but the finding remains formally OPEN until independent focused retest.
