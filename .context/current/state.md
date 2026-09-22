# Current state

## FACT — v1.3.1 stable

Stable Context Capsule v1.3.1 remains released and unchanged as the production line.

## FACT — v2 Project Manager implementation verified

The first complete v2 Project Manager model is implemented on branch `v2-manager-runtime`.

Implemented product surface:

- manifest schema v4;
- universal Core-managed Manager Protocol;
- stable runtime-independent `manager_id`;
- project mandate and bounded authority;
- BDI-style active state: beliefs, goals, intentions/commitments, and plans;
- typed semantic, episodic, and procedural memory;
- provenance and authority requirements for active beliefs;
- explicit v1.3.x → v2 major upgrade; `repair` does not silently cross the major-version boundary;
- manager-aware `READY` and deterministic reinstantiation recovery;
- runtime checkpoints explicitly separated from durable manager state;
- `handoff` retained as an optional operational snapshot rather than the root of manager continuity.

The current development Core source is `6b8477d382bbf5cd8d13bd914b2374473560a43d`, and this exact SHA is recorded by the development capsule.

Verification evidence for the current Core includes GitHub Actions run `35774586971` with conclusion `success`:

- permanent tests: PASS;
- Python compile: PASS;
- self validation: VALID;
- self Project Manager readiness: READY;
- Project Manager reinstantiation smoke: PASS.

This run ID is an evidence pointer, not a "latest run" field. A later successful run that confirms the same semantic state does not make this working view stale.

The stable `main` branch and all installed v1.3.1 consumers remain untouched.

## FACT — authority roles separated

The first cold-reinstantiation acceptance test exposed an ambiguity: the v2 capsule was physically on `v2-manager-runtime` while its inherited `authoritative_branch` still said `main`. The runtime correctly noticed that production and manager-state concepts were being conflated.

v2 now separates the roles explicitly:

- `authority.manager_state_branch = v2-manager-runtime`;
- `authority.product_branch = main`;
- `authoritative_branch` is retained only as an alias of manager-state authority.

The same hardening line marks `current/*` and handoff as non-authoritative working views so stale summaries cannot override BDI state or newer verified evidence.



## FACT — evidence revision semantics hardened

The second cold-reinstantiation acceptance test distinguished a real supersession from mere freshness.

- The old mutable Core SHA embedded in an active commitment was genuinely stale and has been removed from the commitment.
- A later successful CI run that confirms the same verified state is confirming evidence, not semantic supersession.
- New evidence is classified as `confirm`, `supersede`, or `conflict`.
- Working views become stale only when their semantic projection is false or materially misleading.

This prevents the self-generated loop `write → CI → record newer CI → write → CI`.
