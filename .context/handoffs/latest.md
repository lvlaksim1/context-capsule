# Latest handoff

## v2 Project Manager split-authority model verified

Context Capsule v1.3.1 remains the stable production line on `main`. No consumer repository has been migrated to v2.

The v2 Project Manager development line lives on `v2-manager-runtime`. The first cold-reinstantiation acceptance test proved identity/mandate/commitment recovery and live reconciliation, and also exposed two design flaws:

1. stale `current/*` views could contradict newer BDI/live evidence;
2. one historical `authoritative_branch` field ambiguously represented both product authority and manager-state authority.

Both are now hardened.

Current authority coordinates:

- manager-state authority: `v2-manager-runtime`;
- product authority: `main`;
- `authoritative_branch` is only a compatibility alias of manager-state authority;
- discovery is a separate bootstrap coordinate.

Current development Core source: `d591ac34d19c290630ef5382c4ecac603659a89c`.

Verification on GitHub Actions run `35766480844`: permanent tests PASS, compile PASS, self VALID, Project Manager READY, reinstantiation smoke PASS.

Next acceptance test: reinstate the manager in a completely new runtime and confirm it reports the two authority branches distinctly and reconciles production facts against `main` while preserving manager state on `v2-manager-runtime`.

Do not publish stable v2 or migrate consumers without explicit owner approval.
