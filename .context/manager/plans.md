# Manager plans

## Completed implementation stage

1. Implement schema v4, Manager Protocol, manager identity/mandate/BDI state, typed memory, and explicit v1.3→v2 upgrade.
2. Add continuity, provenance, checkpoint-boundary, repair-boundary, redirect-topology, working-view-precedence, and split-authority regression tests.
3. Make Context Capsule Core's own capsule v2-ready on the development branch.
4. Run local and GitHub-hosted self VALID/READY/recover checks.
5. Use the first cold-reinstantiation acceptance test to identify and fix stale working-view semantics.
6. Separate manager-state authority from product authority after the same acceptance test exposed their ambiguity.
7. Verify the split-authority implementation with GitHub-hosted CI.

## Next stage

1. Repeat cold reinstantiation in a completely new runtime and verify the two authority coordinates are understood without interpretation tricks.
2. Exercise adversarial memory/provenance and explicit belief supersession.
3. Exercise commitment completion, cancellation, and invalidation across runtime replacement.
4. Exercise concurrent-runtime conflict detection and bounded long-term recovery.
5. Freeze v2 semantics only after those acceptance scenarios pass.
6. Do not release or migrate consumers until explicitly authorized.
