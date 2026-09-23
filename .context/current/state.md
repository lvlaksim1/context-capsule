# Current state

## Production / development topology

- stable production: Context Capsule v1.3.1 on `main`;
- v2 development and durable manager state: `v2-manager-runtime`;
- installed Core provenance is read only from canonical `.context/capsule.json.core_commit`;
- current development Core binding: `bef230aa1599fd7ef04beabc19c6e42f5c1ec5e7`;
- no existing consumer migration to v2 has been authorized.

## Audit continuity

- CCPM-001 through CCPM-004: CLOSED / High confidence.
- Historical CCPM-R001: CLOSED / High confidence.
- ACP-CC-001: CLOSED / High confidence.
- EW-001, EW-002, EW-003 were CLOSED / High confidence by the earlier focused scheduler retest, but a later Owner clarification replaced the global interactive-mode interpretation with task-scoped live carriers. The combined ACP/Core task-carrier model requires fresh narrow acceptance.

## Task-scoped interactive-first amendment

Owner directive now requires:

- the task/chain currently carried by a live Owner runtime uses GitHub durable handoff plus immediate same-runtime reinstantiation of the next persistent agent;
- a renewable live-carrier lease is attached to that task/chain so scheduler execution cannot race it;
- Owner presence never globally disables, parks, or delays Broker/Worker;
- unrelated tasks without a fresh live carrier remain autonomously schedulable;
- only the affected task may fall back after carrier expiry when fallback is declared;
- explicit Owner hold is per-task.

Implemented on `v2-manager-runtime` across Project Manager and Service Agent contracts/protocols/entrypoints, interoperability specs, manifest flags/validators, and regression tests.

Stable `main`, v1.3.1 consumers, stable-v2 promotion, and migration remain unchanged.
