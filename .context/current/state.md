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

The current split-authority development Core source is `d591ac34d19c290630ef5382c4ecac603659a89c`, and this exact SHA is recorded by the development capsule.

Verification of the split-authority Core completed on 2026-09-22:

- GitHub-hosted permanent tests: PASS;
- Python compile: PASS;
- self validation: VALID;
- self Project Manager readiness: READY;
- Project Manager reinstantiation smoke: PASS.

Clean-head GitHub Actions run: `35766480844`, conclusion `success`.

The stable `main` branch and all installed v1.3.1 consumers remain untouched.

## FACT — authority roles separated

The first cold-reinstantiation acceptance test exposed an ambiguity: the v2 capsule was physically on `v2-manager-runtime` while its inherited `authoritative_branch` still said `main`. The runtime correctly noticed that production and manager-state concepts were being conflated.

v2 now separates the roles explicitly:

- `authority.manager_state_branch = v2-manager-runtime`;
- `authority.product_branch = main`;
- `authoritative_branch` is retained only as an alias of manager-state authority.

The same hardening line marks `current/*` and handoff as non-authoritative working views so stale summaries cannot override BDI state or newer verified evidence.

