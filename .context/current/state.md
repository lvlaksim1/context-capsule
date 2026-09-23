# Current state

## Production / development topology

- stable production: Context Capsule v1.3.1 on `main`;
- v2 development and durable manager state: `v2-manager-runtime`;
- installed Core provenance is read only from canonical `.context/capsule.json.core_commit`;
- current development Core binding for the interactive-first amendment: `d5002dd7566396ae1ee8552b07cf2468e708a184`;
- no existing consumer migration to v2 has been authorized.

## Audit continuity

- CCPM-001 through CCPM-004: CLOSED / High confidence.
- Historical CCPM-R001: CLOSED / High confidence.
- ACP-CC-001: CLOSED / High confidence by focused Auditor retest `ACP-TASK-CC-ACP-RETEST-001`.
- The new interactive-first Core interoperability amendment materially changes the external-orchestration mechanism and therefore requires fresh independent verification before closure.

## Interactive-first interoperability amendment

Owner directive now requires:

- while an Owner-facing live runtime actively carries an authorized work chain, GitHub stores durable task/handoff state but the next persistent agent is reinstantiated directly in that same runtime;
- Scheduled Tasks / wake brokers / execution workers are fallback autonomous carriers only;
- autonomous scheduler delivery during a live Owner session requires explicit Owner delegation;
- execution mode constrains routing but never grants authority.

Implemented on `v2-manager-runtime` across:
- Project Manager Contract / Protocol / ENTRYPOINT;
- Service Agent Contract / Protocol / ENTRYPOINT;
- Agent Control Plane interoperability specification;
- installer-generated manifest flags and validators;
- permanent regression tests.

Stable `main`, v1.3.1 consumers, stable-v2 promotion, and migration remain unchanged.
