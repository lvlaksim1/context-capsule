# Manager plans

## Completed implementation stage

1. Implement schema v4, Manager Protocol, manager identity/mandate/BDI state, typed memory, and explicit v1.3→v2 upgrade.
2. Add continuity, provenance, checkpoint-boundary, repair-boundary, redirect-topology, working-view-precedence, split-authority, evidence-revision, active-state-preservation, concurrent-publication, and bounded-recovery regression coverage.
3. Make Context Capsule Core's own capsule v2-ready on the development branch.
4. Exercise fresh-runtime manager continuity, authority separation, live reconciliation, evidence revision, and untrusted-evidence handling in isolated runtime tests.
5. Establish automation-first verification and an isolated consumer testbed for the small remainder of behavioral smoke testing.

## Current plan

1. Convert every newly discovered deterministic invariant into a permanent Core regression test.
2. Use `evrasia-hd-testbed` only when a behavioral property cannot be verified by deterministic Core tests.
3. Correct discovered semantic defects without turning routine confirmation into state churn.
4. Preserve stable v1.3.1 and existing consumers unchanged.
5. Freeze v2 semantics only when accumulated automated and limited behavioral evidence is sufficient.
6. Do not release or migrate consumers until explicitly authorized.
