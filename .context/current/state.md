# Current state

## FACT — stable production remains v1.3.1

Stable Context Capsule v1.3.1 remains on `main`. Existing v1.3.1 consumers are unchanged.

## FACT — Project Manager v2 baseline remains verified

Project Manager v2 retains its normative Contract, runtime-independent identity, BDI model, typed memory, evidence revision, bounded recovery, self-modification boundary, and isolated consumer compatibility smoke.

## FACT — Minimal Service Agent Base is implemented

Service Agent Base profile version: `1.0.0-dev`.

The base defines a persistent service role whose own repository is its home while external projects/repositories are bounded engagement targets rather than owned project state.

Implemented Service Agent surface:

- stable runtime-independent `agent_id`;
- explicit role and specialization;
- mandate, capabilities, limitations;
- principal/requester model;
- invocation and result contracts;
- professional beliefs/goals/intentions/plans;
- active engagement ledger;
- professional semantic/procedural/episodic memory;
- explicit target-context isolation;
- advisory-by-default output;
- explicit grant required for target-side action;
- transport does not upgrade authority;
- self-authority expansion forbidden;
- runtime checkpoint separated from persistent identity;
- Service Agent reinstantiation recovery.

Development CLI now supports:
`service-install`, `service-repair`, `service-validate`, `service-ready`, and `service-recover`.

Machine-readable schemas exist for Service Agent identity, manifest, invocation, and result.

## FACT — verification is green

Current development Core provenance: `67772ccd376a54e44236035ae6593fe2658e99fc`.

GitHub Actions run `35798348813` succeeded with:

- 36 permanent tests: PASS;
- compile: PASS;
- Context Capsule self VALID/READY/recovery smoke: PASS;
- isolated Project Manager consumer smoke: PASS;
- full Service Agent CLI lifecycle smoke: PASS.

One immediately preceding run failed only because the new `SERVICE_AGENT_BASE_VERSION` file contained a literal backslash-n version-surface typo; the lockstep test caught it and the corrected coherent state passed.

## FACT — next stage

Master Plan item 2 is complete enough to proceed to item 3: create the Supervisor in its own repository using the Service Agent Base.

No stable v2 release or consumer migration has been authorized.

## FACT — persistent Supervisor is established

`lvlaksim1/supervisor` now hosts the persistent `ecosystem-supervisor` Service Agent.

Final bootstrap state `ff914b4aef130411d4c6fac97d10a55fad96eec0` was independently executed against pinned Core `7aa1e697504e686b02a4d7f1539a157214d5e692` and passed service VALID, READY, deterministic RECOVER, stable agent identity, and mandatory Supervisor profile-state recovery.

The Supervisor repository's own GitHub Actions currently has a non-blocking pre-runner startup failure; independent Core execution proved the agent state itself is valid.

Master Plan item 3 is complete. The next stage is Owner + Supervisor creation of the independent Auditor.
