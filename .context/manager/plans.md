# Manager plans

## Completed implementation and acceptance stage

1. Implement schema v4, Manager Protocol, manager identity/mandate/BDI state, typed memory, and explicit v1.3→v2 upgrade.
2. Add continuity, provenance, checkpoint-boundary, repair-boundary, redirect-topology, working-view-precedence, split-authority, and evidence-revision regression tests.
3. Make Context Capsule Core's own capsule v2-ready on the development branch.
4. PM-001 Cold reinstantiation — PASS.
5. PM-002 Authority separation — PASS.
6. PM-003 Evidence revision/freshness — PASS.
7. Define the durable behavioral acceptance suite in `spec/v2-acceptance.md`.

## Next stage

1. PM-004 — origin-bound memory authority and provenance-laundering resistance.
2. PM-005 — explicit belief supersession.
3. PM-006 — unresolved conflict preservation/escalation.
4. PM-007 — commitment completion/cancellation/invalidation across runtime replacement.
5. PM-008 — concurrent-runtime conflict detection.
6. PM-009 — bounded long-term recovery.
7. Freeze v2 semantics only after the required acceptance scenarios pass.
8. Do not release or migrate consumers until explicitly authorized.
