# Manager plans

## Completed implementation stage

1. Implement schema v4, Manager Protocol, manager identity/mandate/BDI state, typed memory, and explicit v1.3→v2 upgrade.
2. Add continuity, provenance, checkpoint-boundary, repair-boundary, redirect-topology, working-view-precedence, split-authority, and evidence-revision regression tests.
3. Make Context Capsule Core's own capsule v2-ready on the development branch.
4. Exercise fresh-runtime manager continuity, authority separation, live reconciliation, and evidence-revision behavior.
5. Keep product authority and manager-state authority explicitly separated.

## Current plan

1. Continue v2 hardening from owner direction and verified evidence.
2. Correct discovered semantic defects without turning routine confirmation into state churn.
3. Preserve stable v1.3.1 and existing consumers unchanged.
4. Freeze v2 semantics only when accumulated evidence is sufficient.
5. Do not release or migrate consumers until explicitly authorized.
