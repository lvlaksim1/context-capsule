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

The implementation commit is `4de7da1d835aa74b80313b4089994037e5e2a808` and is the Core provenance recorded by this development capsule.

Verification completed on 2026-09-22:

- local permanent tests: 14/14 PASS;
- GitHub-hosted permanent tests: PASS;
- Python compile: PASS;
- self validation: VALID;
- self Project Manager readiness: READY;
- Project Manager reinstantiation smoke: PASS.

Final clean-head GitHub Actions run: `35751992546`, conclusion `success`.

The stable `main` branch and all installed v1.3.1 consumers remain untouched.
