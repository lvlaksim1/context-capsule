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

The current development Core source is `585d29c2bf3fd371b9509fde48f0c62355540f72`, and this exact SHA is recorded by the development capsule.

Verification evidence for the current Core includes GitHub Actions run `35788332122` with conclusion `success`:

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

## FACT — fresh-runtime continuity exercised

Independent fresh-runtime recovery has successfully exercised manager identity continuity, authority separation, live reconciliation, and evidence-revision semantics without prior-chat state.

These observations support the current v2 model but do not authorize stable release or consumer migration.

## FACT — automation-first verification

Routine v2 acceptance is now automation-first. The permanent suite contains 22 tests and verifies identity continuity, authority separation, provenance requirements, evidence-revision invariants, active-state preservation across repair, stale-parent publication rejection, runtime-checkpoint exclusion, and bounded recovery behavior.

Bounded recovery now treats manager protocol, identity, mandate, project authority context, active BDI state, and active rules as mandatory. If the configured recovery budget cannot hold that state, recovery fails explicitly rather than silently dropping active manager responsibility. Secondary working views and deeper memory may be omitted and indexed.

GitHub Actions run `35788332122` passed the 22 permanent tests, compile, self validation, Project Manager readiness, and reinstantiation smoke.

Manual multi-chat acceptance is no longer the default verification method. An isolated consumer repository such as `lvlaksim1/evrasia-hd-testbed` is reserved for occasional black-box behavioral smoke checks that cannot be proven deterministically in Core.
